"""Compile and statically inspect new native C/C++; never execute RV32 code."""
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

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("irq_elf_audit", HERE / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
ELF = audit.ELF
require = audit.require
sha = audit.sha
ENTRY = "tsl9_rebuild_interrupt_init_9a42"
HELPERS = {"tsl9_rebuild_rcc_19124": 0x40021018, "tsl9_rebuild_rcc_19142": 0x4002101C,
           "tsl9_rebuild_rcc_19160": 0x4002100C, "tsl9_rebuild_rcc_1917e": 0x40021010}


def tool_path(override, directory, name):
    suffix = ".exe" if os.name == "nt" else ""
    found = override or (str(directory / (name + suffix)) if directory else shutil.which(name))
    require(found is not None and Path(found).is_file(), "missing native tool: " + name)
    return Path(found).resolve()


def command(argv, folder, label):
    result = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120)
    log = result.stdout + result.stderr
    (folder / (label + ".log")).write_bytes(log)
    require(result.returncode == 0, label + " failed; inspect " + str(folder / (label + ".log")))
    return dict(argv=[str(x) for x in argv], exit=result.returncode, log_sha256=hashlib.sha256(log).hexdigest()), log.decode("utf-8", errors="replace")


def ir_function(text, name):
    found = re.search(r"^define\b[^\n]*@" + re.escape(name) + r"\([^\n]*\).*?\n\}", text, re.M | re.S)
    require(found is not None, "IR function: " + name)
    return found.group(0)


def pointer_address(line):
    found = re.search(r"inttoptr \(i32 (-?\d+) to ptr\)", line)
    require(found is not None, "constant explicit volatile address: " + line)
    return int(found.group(1)) & 0xFFFFFFFF


def ir_gate(path):
    text = path.read_text(encoding="utf-8")
    require('target triple = "riscv32-unknown-unknown-elf"' in text or 'target triple = "riscv32-unknown-elf"' in text, "RV32 ELF IR")
    body = ir_function(text, ENTRY)
    effects = []
    lines = body.splitlines()
    for line in lines:
        if "asm sideeffect" in line:
            match = re.search(r'"(csrc|csrs) 0x800, \$0".*\(i32 136\)', line)
            require(match is not None and "~{memory}" in line, "actual CSR800 mask136 and compiler memory clobber")
            effects.append(dict(kind=match.group(1), csr=0x800, mask=136))
        elif "load volatile" in line:
            match = re.search(r"(%[-\w.]+) = load volatile i(\d+)", line)
            require(match is not None, "explicit volatile load width")
            effects.append(dict(kind="read", width=int(match.group(2)), address=pointer_address(line), result=match.group(1)))
        elif "store volatile" in line:
            match = re.search(r"store volatile i(\d+) ([^,]+),", line)
            require(match is not None, "explicit volatile store width")
            effects.append(dict(kind="write", width=int(match.group(1)), address=pointer_address(line), value=match.group(2)))
    expected = [dict(kind="csrc", csr=0x800, mask=136)]
    masks = [0x02020006, 0x101D, 0x02020006, 0x02020006, 0x101D, 0x101D]
    addresses = [0x4002101C, 0x40021018, 0x40021010, 0x40021010, 0x4002100C, 0x4002100C]
    for address in addresses:
        expected += [dict(kind="read", width=32, address=address), dict(kind="write", width=32, address=address)]
    for address, width, value in [(0xE000E42D, 8, 0), (0xE000E104, 32, 0x2000), (0xE000E424, 8, 0x20), (0xE000E104, 32, 0x10), (0xE000E427, 8, 0x30), (0xE000E104, 32, 0x80)]:
        expected.append(dict(kind="write", width=width, address=address, value=str(value)))
    expected.append(dict(kind="csrs", csr=0x800, mask=136))
    require(len(effects) == len(expected) == 20, "exact20 native IR effects")
    for actual, wanted in zip(effects, expected):
        require(all(actual.get(k) == v for k, v in wanted.items()), "native IR effect order/address/width/value")
    rmw_results = []
    for i, mask in enumerate(masks):
        read = effects[1 + 2 * i]
        write = effects[2 + 2 * i]
        operand = mask if i in (0, 1, 2, 4) else ((~mask) & 0xFFFFFFFF)
        operation = "or" if i in (0, 1, 2, 4) else "and"
        expression = re.search(r"^\s*" + re.escape(write["value"]) + r" = " + operation + r" i32 " + re.escape(read["result"]) + r", (-?\d+)\s*$", body, re.M)
        require(expression is not None and int(expression.group(1)) & 0xFFFFFFFF == operand, "native IR exact fresh-load RMW mask")
        rmw_results.append(write["value"])
    require(re.search(r"\bret i32 " + re.escape(rmw_results[-1]) + r"\s*$", body, re.M) is not None, "return final RMW, not invented success status")
    require(not re.search(r"\b(?:br|switch|invoke)\b", body), "specialized initializer straight-line and leaf")
    for line in lines:
        if re.search(r"\b(?:call|tail call)\b", line):
            require("asm sideeffect" in line, "no runtime helper calls in initializer")
    helpers = {}
    for name, address in HELPERS.items():
        helper = ir_function(text, name)
        volatile = [line for line in helper.splitlines() if "volatile" in line]
        require(len(volatile) == 2 and "load volatile i32" in volatile[0] and "store volatile i32" in volatile[1], "helper exactly one fresh 32bit RMW")
        require(all(pointer_address(line) == address for line in volatile), "helper exact register address")
        signature = re.search(r"@" + name + r"\(i32[^%]*(%[-\w.]+), i32[^%]*(%[-\w.]+)\)", helper)
        require(signature is not None, "actual helper two32bit argument interface")
        mask, enabled = signature.groups()
        read_result = re.search(r"(%[-\w.]+) = load volatile i32", volatile[0]).group(1)
        predicate = re.search(r"(%[-\w.]+) = icmp eq i32 " + re.escape(enabled) + r", 0", helper)
        require(predicate is not None, "helper tests full32bit flag for zero")
        or_value = re.search(r"(%[-\w.]+) = or i32 " + re.escape(read_result) + r", " + re.escape(mask), helper)
        complement = re.search(r"(%[-\w.]+) = xor i32 " + re.escape(mask) + r", -1", helper)
        require(or_value is not None and complement is not None, "helper OR mask and bitwise mask complement")
        and_value = re.search(r"(%[-\w.]+) = and i32 " + re.escape(read_result) + r", " + re.escape(complement.group(1)), helper)
        require(and_value is not None, "helper AND_NOT source fresh read")
        select = re.search(r"(%[-\w.]+) = select i1 " + re.escape(predicate.group(1)) + r", i32 " + re.escape(and_value.group(1)) + r", i32 " + re.escape(or_value.group(1)), helper)
        require(select is not None, "helper selects AND_NOT only for zero, OR for every nonzero flag")
        require("store volatile i32 " + select.group(1) + "," in volatile[1] and re.search(r"ret i32 " + re.escape(select.group(1)) + r"\s*$", helper, re.M), "helper stores and returns same computed32bit result")
        helpers[name] = dict(address=address, effects=2)
    return dict(effects=effects, rmw_masks=masks, final_return=rmw_results[-1], helpers=helpers)


def elf_gate(path, linked):
    obj = ELF(path)
    require(obj.kind == (2 if linked else 1), "expected component ELF kind")
    undefined = sorted({s["name"] for entries in obj.symbols.values() for s in entries if s["name"] and s["index"] == 0})
    require(not undefined, "no unresolved helpers, libcalls, or native stubs")
    symbols = [s for entries in obj.symbols.values() for s in entries if s["name"] and s["info"] >> 4 in (1, 2) and s["index"] != 0]
    require({s["name"] for s in symbols} == set(HELPERS) | {ENTRY}, "exact five new native symbols; no original-address aliases")
    require(all((s["info"] & 15) == 2 and 0 < s["index"] < len(obj.sections) for s in symbols), "all new symbols actual functions with section owners")
    require(not any(s["size"] and s["flags"] & 1 for s in obj.sections), "no writable data, BSS, or private state")
    entry = next(s for s in symbols if s["name"] == ENTRY)
    owner = obj.sections[entry["index"]]
    offset = entry["value"] - owner["address"] if linked else entry["value"]
    code = obj.data(owner)[offset:offset + entry["size"]]
    require(len(code) == entry["size"] and code, "bounded native initializer code")
    # Instruction framing only, not instruction execution or ISA simulation.
    cursor = 0
    csr = []
    while cursor < len(code):
        half = int.from_bytes(code[cursor:cursor + 2], "little")
        length = 4 if half & 3 == 3 else 2
        require(cursor + length <= len(code), "bounded native instruction framing")
        if length == 4:
            word = int.from_bytes(code[cursor:cursor + 4], "little")
            if word & 0x7F == 0x73:
                csr.append(dict(offset=cursor, csr=word >> 20, funct3=(word >> 12) & 7, rd=(word >> 7) & 31, rs1=(word >> 15) & 31))
        cursor += length
    require(len(csr) == 2 and [(c["csr"], c["funct3"], c["rd"]) for c in csr] == [(0x800, 3, 0), (0x800, 2, 0)], "actual emitted CSRRC/CSRRS800 discard oldvalue")
    return dict(kind=obj.kind, sha256=sha(path), initializer_bytes=entry["size"], initializer_code_sha256=hashlib.sha256(code).hexdigest(), original_extent_bytes=144,
                fits_original_extent=entry["size"] <= 144, CSR_instructions=csr,
                symbols=[dict(name=s["name"], bytes=s["size"]) for s in symbols], undefined_symbols=undefined,
                relocations=len(obj.relocations), writable_allocations=0)


def machine_gate(disassembly):
    """Straight-line static def-use annotations, not a target executor.

    Constants and fresh-load expression identities recover effective addresses
    in this compiled leaf only. No guest RAM, CSR state, PC stepping, branches,
    instruction dispatch, target input, or executable target is created.
    """
    marker = re.search(r"^([0-9a-f]+) <" + ENTRY + r">:\s*$", disassembly, re.M)
    require(marker is not None, "actual emitted initializer symbol")
    body = disassembly[marker.end():]
    next_symbol = re.search(r"^\s*[0-9a-f]+ <[^>]+>:", body, re.M)
    if next_symbol:
        body = body[:next_symbol.start()]
    rows = []
    for line in body.splitlines():
        match = re.match(r"^\s*([0-9a-f]+):\s*(?:(?:[0-9a-f]{2})\s+)+\t(\S+)\s*(.*)$", line)
        if match:
            rows.append((int(match.group(1), 16), match.group(2), match.group(3).strip()))
    require(rows and rows[-1][1] == "ret", "actual emitted leaf ends RET")
    definitions = {"zero": 0}
    effects = []
    loads = 0
    for address, mnemonic, operands in rows:
        parts = [part.strip() for part in operands.split(",")]
        if mnemonic == "li":
            definitions[parts[0]] = int(parts[1], 0) & 0xFFFFFFFF
        elif mnemonic == "lui":
            definitions[parts[0]] = (int(parts[1], 0) << 12) & 0xFFFFFFFF
        elif mnemonic == "addi":
            known = definitions.get(parts[1])
            require(isinstance(known, int), "constant immediate source definition")
            definitions[parts[0]] = (known + int(parts[2], 0)) & 0xFFFFFFFF
        elif mnemonic in ("or", "and"):
            left, right = definitions.get(parts[1]), definitions.get(parts[2])
            require(isinstance(left, tuple) and isinstance(right, int), "actual RMW data/mask def-use")
            definitions[parts[0]] = (mnemonic, left, right)
        elif mnemonic in ("lw", "sw", "sb"):
            memory = re.fullmatch(r"(-?(?:0x[0-9a-f]+|\d+))\(([a-z][a-z0-9]*)\)", parts[1])
            require(memory is not None, "actual constant-base memory operand")
            base = definitions.get(memory.group(2))
            require(isinstance(base, int), "actual statically known MMIO base")
            target = (base + int(memory.group(1), 0)) & 0xFFFFFFFF
            if mnemonic == "lw":
                result = ("fresh_read", loads, target)
                definitions[parts[0]] = result
                effects.append(dict(kind="read", width=32, address=target, identity=loads))
                loads += 1
            else:
                value = definitions.get(parts[0])
                require(value is not None, "actual store data definition")
                effects.append(dict(kind="write", width=32 if mnemonic == "sw" else 8, address=target, value=value))
        elif mnemonic in ("csrc", "csrs"):
            require(int(parts[0], 0) == 0x800 and definitions.get(parts[1]) == 136, "actual machine CSR800 uses literal mask0x88")
            effects.append(dict(kind=mnemonic, csr=0x800, mask=136))
        elif mnemonic == "ret":
            require(address == rows[-1][0], "single final RET")
        else:
            raise ValueError("unsupported actual native instruction in static proof: " + mnemonic)
    wanted = [dict(kind="csrc", csr=0x800, mask=136)]
    targets = [0x4002101C, 0x40021018, 0x40021010, 0x40021010, 0x4002100C, 0x4002100C]
    masks = [0x02020006, 0x101D, 0x02020006, 0x02020006, 0x101D, 0x101D]
    final = None
    for index, (target, mask) in enumerate(zip(targets, masks)):
        operation = "or" if index in (0, 1, 2, 4) else "and"
        operand = mask if operation == "or" else ((~mask) & 0xFFFFFFFF)
        final = (operation, ("fresh_read", index, target), operand)
        wanted += [dict(kind="read", width=32, address=target, identity=index), dict(kind="write", width=32, address=target, value=final)]
    for target, width, value in [(0xE000E42D, 8, 0), (0xE000E104, 32, 0x2000), (0xE000E424, 8, 0x20), (0xE000E104, 32, 0x10), (0xE000E427, 8, 0x30), (0xE000E104, 32, 0x80)]:
        wanted.append(dict(kind="write", width=width, address=target, value=value))
    wanted.append(dict(kind="csrs", csr=0x800, mask=136))
    require(effects == wanted and loads == 6, "actual machine20effect order, widths, addresses, RMW masks/freshness")
    require(definitions.get("a0") == final, "actual returned A0 is final fresh RMW")
    return dict(effects=effects, instructions=len(rows), original_register_residue_equivalent=False,
                leaf=True, stack_accesses=0, static_def_use_only=True, target_execution=False)


def negative_controls(text, header, flags, tools, folder):
    cases = [
        ("csr_mask", "clear_csr800(UINT32_C(0x88));", "clear_csr800(UINT32_C(0x80));"),
        ("PFIC_width", "write8(UINT32_C(0xe000e42d),0);", "write32(UINT32_C(0xe000e42d),0);"),
        ("lost_fresh_read", "const uint32_t before=read32(address);", "const uint32_t before=0; (void)address; (void)read32;"),
        ("invented_status", "return result;", "return result & UINT32_C(0);"),
    ]
    reports = []
    for name, before, after in cases:
        require(text.count(before) == 1, "one explicit source mutation site: " + name)
        case = folder / ("negative-" + name)
        case.mkdir(exist_ok=False)
        source = case / "interrupt_init.c"
        source.write_text(text.replace(before, after), encoding="utf-8")
        (case / "interrupt_init.h").write_bytes(header.read_bytes())
        obj, ir = case / "mutant.o", case / "mutant.ll"
        command([tools["clang"], *flags, "-c", source, "-o", obj], case, "compile")
        command([tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir], case, "llvm-ir")
        try:
            ir_gate(ir)
        except ValueError as error:
            reports.append(dict(case=name, source_sha256=sha(source), object_sha256=sha(obj), LLVM_IR_sha256=sha(ir), actual_compilation_succeeded=True, rejected=True, reason=str(error)))
        else:
            raise ValueError("compiled mutation was not rejected: " + name)
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--clang")
    parser.add_argument("--linker")
    parser.add_argument("--objdump")
    parser.add_argument("--tool-dir", type=Path)
    parser.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    args = parser.parse_args()
    root = args.project_root.resolve()
    model = root / "experiments/tsl9-v4160-interrupt-init"
    source, header = model / "src/interrupt_init.c", model / "src/interrupt_init.h"
    require(source.is_file() and header.is_file(), "explicit actual model inputs")
    default_dir = args.tool_dir
    if default_dir is None and os.name == "nt" and audit.TOOLBIN.is_dir():
        default_dir = audit.TOOLBIN
    tools = {"clang": tool_path(args.clang, default_dir, "clang"), "linker": tool_path(args.linker, default_dir, "ld.lld"), "objdump": tool_path(args.objdump, default_dir, "llvm-objdump")}
    tool_hashes = {name: sha(path) for name, path in tools.items()}
    source_hashes = {str(path.relative_to(root)).replace("\\", "/"): sha(path) for path in (source, header)}
    script_hashes = {path.name: sha(path) for path in (Path(__file__), HERE / "audit.py")}
    outputs = []
    for mode in (("c", "cpp") if args.language == "both" else (args.language,)):
        folder = HERE / "build" / ("native-" + uuid.uuid4().hex + "-" + mode)
        folder.mkdir(parents=True, exist_ok=False)
        obj, ir, elf = folder / "interrupt_init.o", folder / "interrupt_init.ll", folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac_zicsr", "-mabi=ilp32", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-ffunction-sections", "-fdata-sections", "-mno-relax", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17"]
        if mode == "cpp":
            flags += ["-fno-exceptions", "-fno-rtti"]
        commands = []
        cmd, _ = command([tools["clang"], *flags, "-c", source, "-o", obj], folder, "compile")
        commands.append(cmd)
        cmd, _ = command([tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir], folder, "llvm-ir")
        commands.append(cmd)
        ir_result = ir_gate(ir)
        object_result = elf_gate(obj, False)
        cmd, _ = command([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + ENTRY, "-Ttext=0x1000", obj, "-o", elf], folder, "component-link")
        commands.append(cmd)
        linked_result = elf_gate(elf, True)
        require(linked_result["initializer_code_sha256"] == object_result["initializer_code_sha256"], "component link preserved leaf machine bytes")
        cmd, disassembly = command([tools["objdump"], "--disassemble", elf], folder, "component-disassembly")
        commands.append(cmd)
        machine_result = machine_gate(disassembly)
        negatives = negative_controls(source.read_text(encoding="utf-8-sig"), header, flags, tools, folder)
        require(all(sha(root / path) == digest for path, digest in source_hashes.items()), "native source inputs unchanged while verifying")
        require(all(sha(tools[name]) == digest for name, digest in tool_hashes.items()), "tool executable pins unchanged")
        require(all(sha(HERE / name) == digest for name, digest in script_hashes.items()), "static verification script inputs unchanged")
        report = dict(schema="TSL9-readable-interrupt-init-native-verification-v1", passed=True, mode=mode,
                      source_sha256=source_hashes, tools={name: dict(path=str(path), sha256=tool_hashes[name]) for name, path in tools.items()},
                      flags=flags, commands=commands, object=object_result, linked_component=linked_result,
                      LLVM_IR=ir_result, LLVM_IR_sha256=sha(ir), machine_static_proof=machine_result,
                      compiled_negative_controls=negatives, source_script_sha256=sha(Path(__file__)), script_inputs_sha256=script_hashes,
                      component_link_address=0x1000, original_fixed_placement_proved=False,
                      original_C_ABI_proved=False, original_IRQ_ABI_proved=False, old691_gate_modified=False,
                      firmware_executed=False, emulation=False, hardware=False, network=False, OTA_ready=False)
        receipt = folder / "verification.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        outputs.append(dict(mode=mode, receipt=str(receipt), sha256=sha(receipt), initializer_bytes=object_result["initializer_bytes"], effects=len(ir_result["effects"])))
    print(json.dumps(dict(passed=True, results=outputs)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Native static verification failed: " + str(error), file=sys.stderr)
        sys.exit(1)
