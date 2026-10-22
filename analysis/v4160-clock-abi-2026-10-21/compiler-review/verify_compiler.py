"""Native register-contract build and complete ELF/CFG structural audit."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

HERE = Path(__file__).resolve().parent
NDK = _paths["llvm_bin"]()
QUERY = "tsl9_rebuild_clock_query_registers_18834"
FIELDS = "tsl9_rebuild_clock_fields_registers_1973c"
PARSER_SHA = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def elf_parser(root):
    path = HERE / "elf32.py"
    require(path.is_file() and sha(path) == PARSER_SHA, "explicit local tiny ELF parser dependency")
    spec = importlib.util.spec_from_file_location("clock_register_elf", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ELF, path


def executable(value, directory, name):
    suffix = ".exe" if os.name == "nt" else ""
    found = value or (str(directory / (name + suffix)) if directory else shutil.which(name))
    require(found and Path(found).is_file(), "missing local LLVM executable: " + name)
    return Path(found).resolve()


def run(argv, folder, name):
    result = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120)
    output = result.stdout + result.stderr
    (folder / (name + ".log")).write_bytes(output)
    require(result.returncode == 0, name + " failed; see local log")
    return dict(argv=[str(x) for x in argv], exit=result.returncode, log_sha256=hashlib.sha256(output).hexdigest()), output.decode("utf-8", errors="replace")


def integer_destination(raw):
    """Inspect only destination encoding fields; never execute instructions.

    The bounded source-review decoder is extended for compiler C.SLLI/C.MV.
    The separately checked mnemonic allowlist excludes other ISA families.
    """
    word = int.from_bytes(raw, "little")
    if len(raw) == 4:
        opcode = word & 127
        if opcode in (0x03, 0x13, 0x33, 0x37):
            rd = (word >> 7) & 31
            return rd if rd else None
        if opcode in (0x23, 0x63):
            return None
    elif len(raw) == 2:
        quadrant, funct3 = word & 3, word >> 13
        if quadrant == 0 and funct3 == 2:
            return 8 + ((word >> 2) & 7)
        if quadrant == 1 and funct3 in (0, 2, 3):
            rd = (word >> 7) & 31
            return rd if rd else None
        if quadrant == 1 and funct3 == 4:
            return 8 + ((word >> 7) & 7)
        if quadrant == 1 and funct3 in (5, 6, 7):
            return None
        if quadrant == 2 and funct3 == 0:
            rd = (word >> 7) & 31
            return rd if rd else None
        if quadrant == 2 and funct3 == 4 and (word >> 2) & 31:
            rd = (word >> 7) & 31
            return rd if rd else None
        if word == 0x8082:
            return None
    raise ValueError("unrecognized native destination encoding: " + raw.hex())


def machine_gate(text, elf, parser):
    obj = parser(elf)
    require(obj.kind == 2 and obj.flags == 1, "actual RV32 RVC/soft-float linked ELF")
    attributes = obj.data(obj.byname[".riscv.attributes"])
    architecture = re.search(rb"rv32[a-z0-9_]+", attributes)
    require(architecture is not None and architecture.group().startswith(b"rv32i") and
            all(b"_" + letter in architecture.group() for letter in (b"m", b"a", b"c")) and
            not any(b"_" + letter in architecture.group() for letter in (b"f", b"d", b"v")),
            "actual RV32IMAC integer-only ISA attributes")
    require(not any(s["name"] and s["index"] == 0 for s in obj.symbols), "no native undefined symbol or stub")
    require(not any(s["size"] and s["flags"] & 1 for s in obj.sections), "no writable native data")
    symbols = [s for s in obj.symbols if s["name"] and s["info"] >> 4 in (1, 2) and s["index"] != 0]
    require({s["name"] for s in symbols} == {QUERY, FIELDS} and all(s["info"] & 15 == 2 for s in symbols), "exact actual new function symbols, no aliases")
    result = {}
    no_write = {"ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"}
    branches = no_write - {"ret", "sb", "sh", "sw"}
    allowed = no_write | {"li", "lui", "addi", "andi", "add", "and", "or", "xor", "not", "mv", "mul", "divu", "slli", "srli", "srl", "lw", "lbu"}
    for symbol in symbols:
        name = symbol["name"]
        code = obj.function_bytes(symbol)
        marker = re.search(r"^([0-9a-f]+) <" + name + r">:\s*$", text, re.M)
        require(marker is not None and int(marker.group(1), 16) == symbol["value"], "actual function disassembly symbol")
        rows, cursor = [], 0
        for line in text[marker.end():].lstrip("\r\n").splitlines():
            if not line.strip():
                break
            found = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
            require(found is not None, "reject unparsed instruction lines/labels")
            address, raw = int(found.group(1), 16), bytes.fromhex(found.group(2))
            require(address == symbol["value"] + cursor, "complete contiguous native instruction addresses")
            require(len(raw) in (2, 4) and len(raw) == (4 if raw[0] & 3 == 3 else 2), "native instruction framing")
            require(cursor + len(raw) <= len(code) and raw == code[cursor:cursor + len(raw)], "every raw disassembly byte equals actual ELF")
            op, operands = found.group(3), found.group(4)
            require(op in allowed and not re.search(r"\b(?:sp|ra|tp)\b", operands), "supported no-stack/no-hidden-call instruction profile")
            writes = None
            if op not in no_write:
                first = re.match(r"([a-z][a-z0-9]*)(?:,|$)", operands)
                require(first is not None, "explicit native destination register")
                writes = first.group(1)
                require(writes in ({"a2", "a3", "a4", "a5"} if name == QUERY else {"a4", "a5"}), "actual writes confined to original register subset")
            encoded_rd = integer_destination(raw)
            displayed_rd = {"a2": 12, "a3": 13, "a4": 14, "a5": 15}.get(writes) if writes else None
            require(encoded_rd == displayed_rd, "actual raw instruction destination matches parsed destination")
            require(encoded_rd is None or encoded_rd in ({12, 13, 14, 15} if name == QUERY else {14, 15}), "actual encoded destination confined to source allowlist")
            rows.append(dict(address=address, bytes=raw.hex(), mnemonic=op, operands=operands, writes=writes, encoded_rd=encoded_rd))
            cursor += len(raw)
        require(cursor == len(code), "full actual ELF function byte extent covered")
        boundaries = {row["address"] for row in rows}
        edges = []
        graph = {row["address"]: [] for row in rows}
        for index, row in enumerate(rows):
            if row["mnemonic"] in branches:
                target = re.search(r"(?:^|, )0x([0-9a-f]+)(?: |$)", row["operands"])
                require(target is not None and int(target.group(1), 16) in boundaries, "direct branch targets an actual internal instruction")
                target = int(target.group(1), 16)
                graph[row["address"]].append(target)
                edges.append(dict(source=row["address"], target=target, conditional=row["mnemonic"] != "j"))
            if row["mnemonic"] not in ("j", "ret"):
                require(index + 1 < len(rows), "native fallthrough never escapes function extent")
                graph[row["address"]].append(rows[index + 1]["address"])
        reached, pending = set(), [rows[0]["address"]]
        while pending:
            point = pending.pop()
            if point not in reached:
                reached.add(point)
                pending.extend(graph[point])
        require(reached == boundaries and any(row["mnemonic"] == "ret" for row in rows), "entire structural CFG reachable, bounded internal returns")
        visiting, complete = set(), set()
        def acyclic(point):
            require(point not in visiting, "no hidden cycle in static native CFG")
            if point in complete:
                return
            visiting.add(point)
            for child in graph[point]:
                acyclic(child)
            visiting.remove(point)
            complete.add(point)
        acyclic(rows[0]["address"])
        field_pattern = None
        if name == FIELDS:
            field_pattern = [("lw", "a4, 0x6c(gp)"), ("lui", "a5, 0x7a1"), ("addi", "a5, a5, 0x200"),
                             ("divu", "a4, a4, a5"), ("andi", "a5, a4, 0xff"), ("sb", "a4, 0x17e(gp)"),
                             ("li", "a4, 0x3e8"), ("mul", "a5, a4, a5"), ("sh", "a5, 0x17c(gp)"), ("ret", "")]
            require([(row["mnemonic"], row["operands"]) for row in rows] == field_pattern, "exact field straight-line unsigned DIVU/lowbyte/store/finalA4A5 dataflow")
        result[name] = dict(bytes=len(code), original_bytes=174 if name == QUERY else 40,
                            architecture=architecture.group().decode(),
                            code_sha256=hashlib.sha256(code).hexdigest(), instruction_rows=len(rows),
                            written_registers=sorted({row["writes"] for row in rows if row["writes"]}),
                            direct_CFG_edges=edges, all_instruction_bytes_compared=True,
                            no_SP_access=True, GP_writes=0, no_hidden_calls=True,
                            every_raw_destination_checked=True,
                            DIVU_instructions=sum(row["mnemonic"] == "divu" for row in rows),
                            direct_CFG_acyclic=True, field_normal_return_pattern_proved=field_pattern is not None,
                            rows=rows, branch_semantics_executed=False)
    return result


def transcript_controls(text, elf, parser):
    reports = []
    for name in (QUERY, FIELDS):
        marker = re.search(r"^([0-9a-f]+) <" + name + r">:\s*$", text, re.M)
        require(marker is not None, "actual transcript function source")
        head, tail = text[:marker.end()], text[marker.end():]
        lines = tail.splitlines(keepends=True)
        indexes = []
        for i, line in enumerate(lines):
            if indexes and not line.strip():
                break
            if re.match(r"\s*[0-9a-f]+:", line):
                indexes.append(i)
        require(len(indexes) >= 3, "actual full transcript block")
        variants = {}
        for label, index in (("missing_first", indexes[0]), ("missing_middle", indexes[len(indexes) // 2]), ("truncated_last", indexes[-1])):
            variants[label] = head + "".join(line for j, line in enumerate(lines) if j != index)
        changed = list(lines)
        changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}", r"\g<1>00", changed[indexes[1]], count=1)
        require(changed[indexes[1]] != lines[indexes[1]], "actual instruction raw byte mutation")
        variants["changed_raw_byte"] = head + "".join(changed)
        changed = list(lines)
        changed[indexes[0]] = re.sub(r"\t(lui|lw)\s+[a-z][a-z0-9]*,", r"\t\1\ta3,", changed[indexes[0]], count=1)
        require(changed[indexes[0]] != lines[indexes[0]], "actual display-only destination mutation")
        variants["display_destination_mismatch"] = head + "".join(changed)
        for label, index in (("unparsed_middle", indexes[1]), ("unparsed_trailing", indexes[-1] + 1)):
            changed = list(lines)
            changed.insert(index, "    UNPARSED-INSTRUCTION\n")
            variants[label] = head + "".join(changed)
        for label, changed in variants.items():
            try:
                machine_gate(changed, elf, parser)
            except ValueError as error:
                reports.append(dict(function=name, case=label, rejected=True, reason=str(error), transcript_sha256=hashlib.sha256(changed.encode()).hexdigest()))
            else:
                raise ValueError("modified machine transcript admitted: " + label)
    return reports


def compile_unit(tools, source_root, folder, unit, mode):
    allowed_registers = {13, 14, 15} if unit == "clock_query" else {14, 15}
    obj = folder / (unit + ".o")
    flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17", *["-ffixed-x" + str(reg) for reg in range(1, 32) if reg not in allowed_registers]]
    record, _ = run([tools["clang"], *flags, "-c", source_root / (unit + ".c"), "-o", obj], folder, "compile-" + unit)
    return record, obj


def compiled_controls(source_root, folder, tools, mode, parser):
    reports = []
    cases = [("A0_write", "clock_query.c", '__asm__ volatile("li a0, 1");'),
             ("SP_write", "clock_query.c", '__asm__ volatile("addi sp, sp, -16");'),
             ("wrong_final_A4", "clock_fields.c", '__asm__ volatile("li a4, 999");')]
    for name, file, statement in cases:
        case = folder / ("negative-" + name)
        case.mkdir()
        for path in source_root.iterdir():
            if path.is_file():
                data = path.read_bytes()
                if path.name == file:
                    text = data.decode("utf-8-sig")
                    require(text.rstrip().endswith("}"), "explicit function-ending mutation site")
                    before, _ = text.rsplit("}", 1)
                    data = (before + "    " + statement + "\n}\n").encode()
                (case / path.name).write_bytes(data)
        objects = []
        for unit in ("clock_query", "clock_fields"):
            _, obj = compile_unit(tools, case, case, unit, mode)
            objects.append(obj)
        elf = case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
        run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + QUERY, "-Ttext=0x1000", *objects, "-o", elf], case, "link")
        _, text = run([tools["objdump"], "--disassemble", elf], case, "disassembly")
        try:
            machine_gate(text, elf, parser)
        except ValueError as error:
            reports.append(dict(case=name, actual_compilation_and_link_succeeded=True, rejected=True, reason=str(error),
                                changed_source=file, source_sha256=sha(case / file), linked_component_sha256=sha(elf),
                                object_sha256={p.name: sha(p) for p in objects}, disassembly_sha256=hashlib.sha256(text.encode()).hexdigest()))
        else:
            raise ValueError("compiled register/stack mutation admitted: " + name)
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--tool-dir", type=Path)
    parser.add_argument("--clang")
    parser.add_argument("--linker")
    parser.add_argument("--objdump")
    parser.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    args = parser.parse_args()
    root = args.project_root.resolve()
    ELF, dependency = elf_parser(root)
    source_root = root / "experiments/tsl9-v4160-clock-registers/src"
    inputs = {p.name: sha(p) for p in sorted(source_root.iterdir()) if p.is_file()}
    directory = args.tool_dir or (NDK if os.name == "nt" and NDK.is_dir() else None)
    tools = {"clang": executable(args.clang, directory, "clang"), "linker": executable(args.linker, directory, "ld.lld"), "objdump": executable(args.objdump, directory, "llvm-objdump")}
    pins = {name: sha(path) for name, path in tools.items()}
    results = []
    for mode in (("c", "cpp") if args.language == "both" else (args.language,)):
        folder = HERE / "build" / ("verified-" + uuid.uuid4().hex + "-" + mode)
        folder.mkdir(parents=True, exist_ok=False)
        commands, objects = [], []
        for unit in ("clock_query", "clock_fields"):
            record, obj = compile_unit(tools, source_root, folder, unit, mode)
            commands.append(record)
            objects.append(obj)
        linked = folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        record, _ = run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + QUERY, "-Ttext=0x1000", *objects, "-o", linked], folder, "link")
        commands.append(record)
        record, disassembly = run([tools["objdump"], "--disassemble", linked], folder, "disassembly")
        commands.append(record)
        checked = machine_gate(disassembly, linked, ELF)
        transcripts = transcript_controls(disassembly, linked, ELF)
        negatives = compiled_controls(source_root, folder, tools, mode, ELF)
        require(all(sha(source_root / name) == digest for name, digest in inputs.items()), "actual native C/H inputs unchanged")
        require(all(sha(tools[name]) == digest for name, digest in pins.items()), "LLVM executable pins unchanged")
        receipt = dict(schema="TSL9-clock-register-compiler-structural-proof-v1", passed=True, mode=mode,
                       source_sha256=inputs, source_script_sha256=sha(Path(__file__)),
                       ELF_parser_dependency=dict(path=dependency.name, sha256=PARSER_SHA),
                       tools={name: dict(path=str(path), sha256=pins[name]) for name, path in tools.items()}, commands=commands,
                       objects={p.name: sha(p) for p in objects}, linked_component_sha256=sha(linked), functions=checked,
                       transcript_controls=transcripts, actual_compiled_controls=negatives,
                       full_original_ABI_proved=False, pointwise_register_semantics_proved=False,
                       original_fixed_placement_proved=False, original_IRQ_ABI_proved=False,
                       firmware_executed=False, ISA_emulation=False, network=False, hardware=False, OTA_ready=False)
        path = folder / "verification.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(path), sha256=sha(path), functions={name: {k: v for k, v in details.items() if k not in ("rows", "direct_CFG_edges")} for name, details in checked.items()}))
    print(json.dumps(dict(passed=True, results=results)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print("Compiler structural verification failed: " + str(error), file=sys.stderr)
        sys.exit(1)
