"""Native reset-memory compile/static proof; never executes RV32 code."""
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
spec = importlib.util.spec_from_file_location("reset_memory_elf", HERE / "elf32.py")
parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_module)
ELF, require = parser_module.ELF, parser_module.require
ENTRY = "tsl9_rebuild_reset_memory_186ba"
CONTINUATION = "__tsl9_reset_resume_186f8"
NDK = _paths["llvm_bin"]()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tool(explicit, directory, name):
    suffix = ".exe" if os.name == "nt" else ""
    found = explicit or (str(directory / (name + suffix)) if directory else shutil.which(name))
    require(found and Path(found).is_file(), "missing local LLVM tool: " + name)
    return Path(found).resolve()


def run(argv, folder, label, expected_success=True):
    p = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120)
    raw = p.stdout + p.stderr
    (folder / (label + ".log")).write_bytes(raw)
    if expected_success:
        require(p.returncode == 0, label + " failed; inspect local log")
    return dict(argv=[str(x) for x in argv], exit=p.returncode, log_sha256=hashlib.sha256(raw).hexdigest()), raw.decode("utf-8", errors="replace")


def destination(raw):
    word = int.from_bytes(raw, "little")
    if len(raw) == 4:
        opcode = word & 127
        if opcode in (0x03, 0x13, 0x33, 0x37):
            rd = (word >> 7) & 31
            return rd or None
        if opcode in (0x23, 0x63):
            return None
        if opcode == 0x6F and ((word >> 7) & 31) == 0:
            return None
    elif len(raw) == 2:
        q, f = word & 3, word >> 13
        if q == 0 and f == 2:
            return 8 + ((word >> 2) & 7)
        if q == 0 and f == 6:
            return None
        if q == 1 and f in (0, 2, 3):
            return ((word >> 7) & 31) or None
        if q == 1 and f == 4:
            return 8 + ((word >> 7) & 7)
        if q == 1 and f in (5, 6, 7):
            return None
        if q == 2 and f == 0:
            return ((word >> 7) & 31) or None
        if q == 2 and f == 4 and (word >> 2) & 31:
            return ((word >> 7) & 31) or None
        if word == 0x8082:
            return None
    raise ValueError("unsupported destination encoding: " + raw.hex())


def elf_gate(path, fragment=False, linked=False):
    obj = ELF(path)
    require(obj.kind == (2 if linked else 1) and obj.flags == 1, "RV32 ELF, RVC, soft-float ABI")
    architecture = re.search(rb"rv32[a-z0-9_]+", obj.data(obj.byname[".riscv.attributes"]))
    require(architecture is not None and architecture.group().startswith(b"rv32i") and all(b"_" + x in architecture.group() for x in (b"m", b"a", b"c")) and not any(b"_" + x in architecture.group() for x in (b"f", b"d", b"v")), "RV32IMAC integer-only attributes")
    undefined = sorted({s["name"] for s in obj.symbols if s["name"] and s["index"] == 0})
    require(undefined == ([CONTINUATION] if fragment and not linked else []), "exact continuation obligation or no undefined symbols")
    globals_ = [s for s in obj.symbols if s["name"] and s["info"] >> 4 in (1, 2) and s["index"] != 0]
    require({s["name"] for s in globals_} == ({ENTRY, CONTINUATION} if fragment and linked else {ENTRY}), "exact reconstruction symbol and optional numeric continuation witness")
    functions = [s for s in obj.symbols if s["info"] & 15 == 2 and s["index"] != 0 and s["size"]]
    require(len(functions) == 1 and functions[0]["name"] == ENTRY, "one actual new native helper")
    require(not any(s["size"] and s["flags"] & 1 for s in obj.sections), "no writable allocations/runtime state")
    code = obj.function_bytes(functions[0])
    external = [r for r in obj.relocations if r["symbol"]["name"] == CONTINUATION]
    if fragment and not linked:
        require(len(external) == 1 and external[0]["type"] == 17 and external[0]["addend"] == 0, "actual expanded R_RISCV_JAL continuation relocation")
        offset = external[0]["offset"]
        instruction = int.from_bytes(code[offset:offset + 4], "little")
        require(offset + 4 <= len(code) and instruction & 0x7F == 0x6F and (instruction >> 7) & 31 == 0, "actual four-byte JAL x0, no continuation body supplied")
    return dict(kind=obj.kind, architecture=architecture.group().decode(), sha256=sha(path), helper_bytes=len(code),
                original_fragment_bytes=62, code_sha256=hashlib.sha256(code).hexdigest(), undefined_symbols=undefined,
                continuation_relocations=[dict(offset=r["offset"], type=r["type"], addend=r["addend"]) for r in external],
                writable_allocations=0, continuation_encoding="JAL_x0_4bytes" if fragment else None,
                compressed_continuation_proved=False)


def ir_gate(path):
    text = path.read_text(encoding="utf-8")
    marker = re.search(r"^define\b[^\n]*@" + ENTRY + r"\([^\n]*\).*?\n\}", text, re.M | re.S)
    require(marker is not None, "actual reset helper LLVM IR")
    body = marker.group()
    gp = [line for line in body.splitlines() if "asm sideeffect" in line and "={x3}" in line]
    require(len(gp) == 3 and all("~{memory}" in line for line in gp), "three separate fixed-GP empty-asm observations with memory clobbers")
    require(not any(re.search(r"\b(?:call|invoke)\b", line) and "asm sideeffect" not in line for line in body.splitlines()), "no memcpy/memset/libcall/hidden helper")
    memory = [line.strip() for line in body.splitlines() if "volatile" in line]
    require(len(memory) == 3 and sum("load volatile i32" in line for line in memory) == 1 and sum("store volatile i32" in line for line in memory) == 2, "one copy READ32 site, one copy WRITE32 site, one zero WRITE32 site")
    require(not any("slt" in line or "sgt" in line or "sle" in line or "sge" in line for line in body.splitlines() if "icmp" in line), "no signed loop bound comparisons")
    require(any("store volatile i32 0," in line for line in memory), "explicit zero word store")
    return dict(GP_observation_sites=3, volatile_memory_sites=memory, native_loop_semantics_executed=False)


def machine_gate(text, path, fragment=False):
    obj = ELF(path)
    symbols = [s for s in obj.symbols if s["name"] == ENTRY and s["index"] != 0 and s["info"] & 15 == 2]
    require(len(symbols) == 1, "one helper symbol")
    symbol = symbols[0]
    code = obj.function_bytes(symbol)
    marker = re.search(r"^([0-9a-f]+) <" + ENTRY + r">:\s*$", text, re.M)
    require(marker is not None and int(marker.group(1), 16) == symbol["value"], "actual ELF function address")
    allowed = {"li", "lui", "addi", "add", "mv", "lw", "sw", "beq", "bne", "beqz", "bnez", "bltu", "bgeu", "bleu", "bgtu", "j", "ret"}
    branches = {"beq", "bne", "beqz", "bnez", "bltu", "bgeu", "bleu", "bgtu", "j"}
    nonwrites = branches | {"sw", "ret"}
    rows, cursor = [], 0
    for line in text[marker.end():].lstrip("\r\n").splitlines():
        if not line.strip():
            break
        m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
        require(m is not None, "no ignored/unparsed/interior instruction lines")
        address, raw = int(m.group(1), 16), bytes.fromhex(m.group(2))
        require(address == symbol["value"] + cursor and cursor + len(raw) <= len(code) and raw == code[cursor:cursor + len(raw)], "complete contiguous actual instruction bytes")
        require(len(raw) in (2, 4) and len(raw) == (4 if raw[0] & 3 == 3 else 2), "whole instruction framing")
        op, operands = m.group(3), m.group(4)
        require(op in allowed and not re.search(r"\b(?:sp|tp)\b", operands), "supported no-stack/no-call integer instruction profile")
        rd = destination(raw)
        displayed = None if op in nonwrites else operands.split(",")[0]
        number = {"t0": 5, "a0": 10, "a1": 11, "a2": 12}.get(displayed) if displayed else None
        require((displayed is None or number is not None) and rd == number, "raw destination equals displayed original-clobber register subset")
        rows.append(dict(address=address, bytes=raw.hex(), mnemonic=op, operands=operands, encoded_rd=rd))
        cursor += len(raw)
    require(cursor == len(code), "complete ELF helper extent covered")
    boundaries = {row["address"] for row in rows}
    graph = {point: [] for point in boundaries}
    external, edges = [], []
    for index, row in enumerate(rows):
        if row["mnemonic"] in branches:
            target = re.search(r"(?:^|, )0x([0-9a-f]+)(?: |$)", row["operands"])
            require(target is not None, "direct native branch target")
            target = int(target.group(1), 16)
            if target in boundaries:
                graph[row["address"]].append(target)
            else:
                require(fragment and row["mnemonic"] == "j" and target == 0x186F8 and len(bytes.fromhex(row["bytes"])) == 4, "only actual four-byte continuation jump may leave diagnostic fragment")
                external.append(dict(source=row["address"], target=target, instruction_bytes=4))
            edges.append(dict(source=row["address"], target=target, conditional=row["mnemonic"] != "j"))
        if row["mnemonic"] not in ("j", "ret"):
            require(index + 1 < len(rows), "no implicit fallthrough outside new helper")
            graph[row["address"]].append(rows[index + 1]["address"])
    reached, pending = set(), [rows[0]["address"]]
    while pending:
        node = pending.pop()
        if node not in reached:
            reached.add(node)
            pending.extend(graph[node])
    require(reached == boundaries, "all native helper instructions structurally reachable")
    require((len(external) == 1 and not any(r["mnemonic"] == "ret" for r in rows)) if fragment else (not external and any(r["mnemonic"] == "ret" for r in rows)), "explicit fragment transfer versus new leaf return")
    # Structural SCCs describe loop regions; they do not execute iterations or
    # claim termination for altered GP / memory environments.
    index_counter, stack, on_stack, indices, low, components = [0], [], set(), {}, {}, []
    def visit(node):
        indices[node] = low[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for child in graph[node]:
            if child not in indices:
                visit(child)
                low[node] = min(low[node], low[child])
            elif child in on_stack:
                low[node] = min(low[node], indices[child])
        if low[node] == indices[node]:
            component = []
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.append(item)
                if item == node:
                    break
            if len(component) > 1 or node in graph[node]:
                components.append(sorted(component))
    for node in sorted(graph):
        if node not in indices:
            visit(node)
    require(len(components) == 2, "actual copy and zero loop SCCs")
    return dict(helper_bytes=len(code), instruction_rows=len(rows), rows=rows, direct_CFG_edges=edges,
                loop_components=sorted(components), external_continuation_edges=external,
                every_raw_destination_checked=True, GP_writes=0, SP_accesses=0, hidden_calls=0,
                physical_GP_operand_reads=sum(bool(re.search(r"\bgp\b", row["operands"])) for row in rows),
                loop_termination_proved=False, machine_loop_semantics_executed=False)


def transcript_controls(text, path, fragment):
    marker = re.search(r"^([0-9a-f]+) <" + ENTRY + r">:\s*$", text, re.M)
    require(marker is not None, "actual transcript helper")
    head, tail = text[:marker.end()], text[marker.end():]
    lines = tail.splitlines(keepends=True)
    indexes = []
    for index, line in enumerate(lines):
        if indexes and not line.strip():
            break
        if re.match(r"\s*[0-9a-f]+:", line):
            indexes.append(index)
    require(len(indexes) > 3, "actual helper instruction block")
    variants = {}
    for name, index in (("missing_first", indexes[0]), ("missing_middle", indexes[len(indexes) // 2]), ("truncated_last", indexes[-1])):
        variants[name] = head + "".join(line for i, line in enumerate(lines) if i != index)
    changed = list(lines)
    changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}", r"\g<1>00", changed[indexes[1]], count=1)
    require(changed[indexes[1]] != lines[indexes[1]], "changed actual raw byte")
    variants["changed_raw_byte"] = head + "".join(changed)
    for name, index in (("unparsed_middle", indexes[1]), ("unparsed_trailing", indexes[-1] + 1)):
        changed = list(lines)
        changed.insert(index, "    UNPARSED-INSTRUCTION\n")
        variants[name] = head + "".join(changed)
    reports = []
    for name, changed in variants.items():
        try:
            machine_gate(changed, path, fragment)
        except ValueError as error:
            reports.append(dict(case=name, rejected=True, reason=str(error), transcript_sha256=hashlib.sha256(changed.encode()).hexdigest()))
        else:
            raise ValueError("modified native transcript admitted: " + name)
    return reports


def compiled_controls(source, header, flags, folder, tools, fragment):
    text = source.read_text(encoding="utf-8-sig")
    cases = [("A3_write", '    RM_OUTPUTS(clear,zero_end,copy_end);', '    RM_OUTPUTS(clear,zero_end,copy_end);\n    __asm__ volatile("li a3, 1");'),
             ("SP_write", '    RM_OUTPUTS(clear,zero_end,copy_end);', '    RM_OUTPUTS(clear,zero_end,copy_end);\n    __asm__ volatile("addi sp, sp, -16");'),
             ("wrong_write_width", '#define RM_WRITE32(a,v) (*(volatile uint32_t *)(uintptr_t)(a)=(v))', '#define RM_WRITE32(a,v) (*(volatile uint16_t *)(uintptr_t)(a)=(v))')]
    reports = []
    for name, before, after in cases:
        require(text.count(before) == 1, "one explicit native source control site")
        case = folder / ("negative-" + name)
        case.mkdir()
        src, obj, ir = case / "reset_memory.c", case / "reset_memory.o", case / "reset_memory.ll"
        src.write_text(text.replace(before, after), encoding="utf-8")
        (case / "reset_memory.h").write_bytes(header.read_bytes())
        run([tools["clang"], *flags, "-c", src, "-o", obj], case, "compile")
        run([tools["clang"], *flags, "-S", "-emit-llvm", src, "-o", ir], case, "llvm-ir")
        linked = case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
        absolute = ["--defsym=" + CONTINUATION + "=0x186f8"] if fragment else []
        run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + ENTRY, "-Ttext=0x1000", *absolute, obj, "-o", linked], case, "link")
        _, assembly = run([tools["objdump"], "--disassemble", linked], case, "disassembly")
        try:
            ir_gate(ir)
            machine_gate(assembly, linked, fragment)
        except ValueError as error:
            reports.append(dict(case=name, actual_compilation_and_link_succeeded=True, rejected=True, reason=str(error),
                                source_sha256=sha(src), object_sha256=sha(obj), LLVM_IR_sha256=sha(ir), linked_sha256=sha(linked)))
        else:
            raise ValueError("compiled native control admitted: " + name)
    return reports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path)
    p.add_argument("--clang")
    p.add_argument("--linker")
    p.add_argument("--objdump")
    p.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    p.add_argument("--fragment", action="store_true")
    a = p.parse_args()
    root = a.project_root.resolve()
    model = root / "experiments/tsl9-v4160-reset-memory/src"
    source, header = model / "reset_memory.c", model / "reset_memory.h"
    directory = a.tool_dir or (NDK if os.name == "nt" and NDK.is_dir() else None)
    tools = {"clang": tool(a.clang, directory, "clang"), "linker": tool(a.linker, directory, "ld.lld"), "objdump": tool(a.objdump, directory, "llvm-objdump")}
    inputs, pins = {f.name: sha(f) for f in (source, header)}, {name: sha(path) for name, path in tools.items()}
    outputs = []
    for mode in (("c", "cpp") if a.language == "both" else (a.language,)):
        folder = HERE / "build" / ("native-" + uuid.uuid4().hex + "-" + ("fragment-" if a.fragment else "leaf-") + mode)
        folder.mkdir(parents=True, exist_ok=False)
        obj, ir = folder / "reset_memory.o", folder / "reset_memory.ll"
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17", *["-ffixed-x" + str(i) for i in range(1, 32) if i not in {5, 10, 11, 12}]]
        if a.fragment:
            flags += ["-DTSL9_RESET_MEMORY_FRAGMENT=1"]
        commands = []
        for label, argv in [("compile", [tools["clang"], *flags, "-c", source, "-o", obj]), ("llvm-ir", [tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir])]:
            record, _ = run(argv, folder, label)
            commands.append(record)
        object_result, ir_result = elf_gate(obj, a.fragment), ir_gate(ir)
        strict_result = None
        if a.fragment:
            record, error = run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + ENTRY, "-Ttext=0x1000", obj, "-o", folder / "STRICT-MISSING-CONTINUATION.elf"], folder, "strict-link", False)
            require(record["exit"] != 0 and "undefined symbol: " + CONTINUATION in error, "strict fragment link rejects absent continuation implementation")
            strict_result = record
            commands.append(record)
        linked = folder / ("ADDRESS-WITNESS-ONLY.elf" if a.fragment else "COMPONENT-ONLY-NOT-FIRMWARE.elf")
        link_flags = ["--defsym=" + CONTINUATION + "=0x186f8"] if a.fragment else []
        record, _ = run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + ENTRY, "-Ttext=0x1000", *link_flags, obj, "-o", linked], folder, "link")
        commands.append(record)
        linked_result = elf_gate(linked, a.fragment, True)
        record, text = run([tools["objdump"], "--disassemble", linked], folder, "disassembly")
        commands.append(record)
        machine = machine_gate(text, linked, a.fragment)
        transcripts = transcript_controls(text, linked, a.fragment)
        negatives = compiled_controls(source, header, flags, folder, tools, a.fragment)
        require(all(sha(model / name) == digest for name, digest in inputs.items()), "actual reset C/H unchanged")
        require(all(sha(tools[name]) == digest for name, digest in pins.items()), "LLVM executable pins unchanged")
        report = dict(schema="TSL9-reset-memory-native-structural-proof-v1", passed=True, mode=mode, fragment=a.fragment,
                      source_sha256=inputs, source_script_sha256=sha(Path(__file__)), ELF_parser_sha256=sha(HERE / "elf32.py"),
                      tools={name: dict(path=str(path), sha256=pins[name]) for name, path in tools.items()}, flags=flags, commands=commands,
                      object=object_result, LLVM_IR=ir_result, LLVM_IR_sha256=sha(ir), linked_component=linked_result, machine=machine,
                      transcript_controls=transcripts, actual_compiled_controls=negatives,
                      original_slot_check=dict(passed=machine["helper_bytes"] <= 62, original_start=0x186BA, original_end_exclusive=0x186F8,
                                               candidate_end_exclusive=0x186BA + machine["helper_bytes"],
                                               continuation_overlaps_candidate_if_original_placement=machine["helper_bytes"] > 62),
                      strict_missing_continuation_rejected=strict_result is not None,
                      continuation_body_supplied=False, numeric_witness_is_implementation=False,
                      original_fallthrough_ABI_proved=False, original_fixed_placement_proved=False,
                      full_native_loop_semantics_proved=False, firmware_executed=False, ISA_emulation=False,
                      network=False, hardware=False, OTA_ready=False)
        path = folder / "verification.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        outputs.append(dict(mode=mode, fragment=a.fragment, receipt=str(path), sha256=sha(path), helper_bytes=machine["helper_bytes"], instructions=machine["instruction_rows"], loop_SCCs=len(machine["loop_components"])))
    print(json.dumps(dict(passed=True, results=outputs)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print("Reset memory native verification failed: " + str(error), file=sys.stderr)
        sys.exit(1)
