"""Native verifier v2: full ELF-bound disassembly coverage, no target execution."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("immutable_irq_native_v1", HERE / "verify_native.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
require = base.require
sha = base.sha
ELF = base.ELF
ENTRY = base.ENTRY
BASE_MACHINE_GATE = base.machine_gate
BASE_COMMAND = base.command


def disassembly_coverage(disassembly, elf_path):
    obj = ELF(elf_path)
    require(obj.kind == 2, "coverage binds actual linked component ELF")
    candidates = [s for entries in obj.symbols.values() for s in entries
                  if s["name"] == ENTRY and (s["info"] & 15) == 2 and s["index"] != 0]
    require(len(candidates) == 1, "one actual linked initializer symbol")
    symbol = candidates[0]
    section = obj.sections[symbol["index"]]
    offset = symbol["value"] - section["address"]
    code = obj.data(section)[offset:offset + symbol["size"]]
    require(len(code) == symbol["size"] and code, "actual complete linked initializer bytes")
    marker = re.search(r"^([0-9a-f]+) <" + ENTRY + r">:\s*$", disassembly, re.M)
    require(marker is not None and int(marker.group(1), 16) == symbol["value"], "disassembly symbol address equals actual ELF")
    # LLVM emits one unbroken instruction block. Reject, rather than ignore,
    # any nonempty noninstruction line inside that block, including labels.
    tail = disassembly[marker.end():].lstrip("\r\n")
    lines = []
    for line in tail.splitlines():
        if not line.strip():
            break
        lines.append(line)
    cursor = 0
    rows = []
    for line in lines:
        match = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
        require(match is not None, "reject unparsed initializer disassembly line")
        address = int(match.group(1), 16)
        raw = bytes.fromhex(match.group(2))
        require(address == symbol["value"] + cursor, "contiguous actual initializer disassembly addresses")
        require(len(raw) in (2, 4) and len(raw) == (4 if raw[0] & 3 == 3 else 2), "complete actual instruction framing")
        require(cursor + len(raw) <= len(code), "no disassembly bytes outside actual initializer extent")
        require(raw == code[cursor:cursor + len(raw)], "every disassembly instruction byte equals actual ELF")
        rows.append(dict(address=address, bytes=raw.hex(), mnemonic=match.group(3)))
        cursor += len(raw)
    require(cursor == len(code), "full initializer ELF extent covered without skipped or truncated bytes")
    require(rows and rows[-1]["mnemonic"] == "ret", "last covered instruction is RET")
    return dict(entry_address=symbol["value"], end_exclusive=symbol["value"] + len(code),
                ELF_initializer_bytes=len(code), disassembly_bytes=cursor, instruction_rows=len(rows),
                initializer_code_sha256=hashlib.sha256(code).hexdigest(),
                contiguous=True, all_raw_bytes_match=True, unparsed_lines=0, skipped_bytes=0)


def transcript_negatives(disassembly, elf_path):
    marker = re.search(r"^([0-9a-f]+) <" + ENTRY + r">:\s*$", disassembly, re.M)
    require(marker is not None, "actual transcript source symbol")
    head, tail = disassembly[:marker.end()], disassembly[marker.end():]
    lines = tail.splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if re.match(r"\s*[0-9a-f]+:", line)]
    require(len(indexes) >= 3, "actual native transcript instruction rows")
    variants = {}
    for name, removed in (("missing_first_row", indexes[0]), ("missing_interior_row", indexes[len(indexes) // 2]), ("truncated_last_row", indexes[-1])):
        variants[name] = head + "".join(line for i, line in enumerate(lines) if i != removed)
    changed = list(lines)
    changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}", r"\g<1>00", changed[indexes[1]], count=1)
    require(changed[indexes[1]] != lines[indexes[1]], "actual changed instruction byte negative")
    variants["changed_raw_instruction_byte"] = head + "".join(changed)
    inserted = list(lines)
    inserted.insert(indexes[1], "    UNPARSED-INSTRUCTION\n")
    variants["unparsed_interior_line"] = head + "".join(inserted)
    appended = list(lines)
    appended.insert(indexes[-1] + 1, "    UNPARSED-TRAILING-INSTRUCTION\n")
    variants["unparsed_trailing_line"] = head + "".join(appended)
    results = []
    for name, changed_text in variants.items():
        try:
            disassembly_coverage(changed_text, elf_path)
        except ValueError as error:
            results.append(dict(case=name, rejected=True, reason=str(error), transcript_sha256=hashlib.sha256(changed_text.encode()).hexdigest()))
        else:
            raise ValueError("incomplete or modified machine transcript admitted: " + name)
    return results


def machine_gate(disassembly, elf_path):
    coverage = disassembly_coverage(disassembly, elf_path)
    machine = BASE_MACHINE_GATE(disassembly)
    require(machine["instructions"] == coverage["instruction_rows"], "semantic proof covers every actual instruction row")
    machine["ELF_bound_coverage"] = coverage
    machine["transcript_negative_controls"] = transcript_negatives(disassembly, elf_path)
    return machine


def main():
    # Reuse the immutable v1 compilation, IR, ELF, and compiled mutation checks.
    # The disassembler's actual command argument selects the ELF, never text
    # scraped from tool output or a guessed filename from an external path.
    last_elf = []

    def command(argv, folder, label):
        if label == "component-disassembly":
            last_elf[:] = [Path(argv[-1]).resolve()]
        return BASE_COMMAND(argv, folder, label)

    def bound_machine(disassembly):
        require(len(last_elf) == 1, "actual disassembler command ELF selected")
        return machine_gate(disassembly, last_elf[0])

    base.command = command
    base.machine_gate = bound_machine
    script_paths = [HERE / "audit.py", HERE / "verify_native.py", Path(__file__)]
    script_hashes = {p.name: sha(p) for p in script_paths}
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        base.main()
    result = json.loads(captured.getvalue())
    for item in result["results"]:
        path = Path(item["receipt"])
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["schema"] = "TSL9-readable-interrupt-init-native-verification-v2"
        receipt["immutable_v1_script_sha256"] = receipt["source_script_sha256"]
        receipt["source_script_sha256"] = script_hashes[Path(__file__).name]
        receipt["script_inputs_sha256"] = script_hashes
        receipt["full_ELF_disassembly_coverage_proved"] = True
        require(all(sha(HERE / name) == digest for name, digest in script_hashes.items()), "all v2 verifier source bytes unchanged")
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        item["sha256"] = sha(path)
        item["disassembly_negative_controls"] = len(receipt["machine_static_proof"]["transcript_negative_controls"])
    result["version"] = 2
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, base.subprocess.SubprocessError) as error:
        print("Native static verification v2 failed: " + str(error), file=sys.stderr)
        sys.exit(1)
