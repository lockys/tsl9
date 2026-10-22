"""Compile native clock C/C++ and prove structural/primitive properties only."""
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
spec = importlib.util.spec_from_file_location("native_clock_elf", HERE / "elf32.py")
elf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_module)
ELF, require = elf_module.ELF, elf_module.require
QUERY = "tsl9_rebuild_clock_query_18834"
FIELDS = "tsl9_rebuild_clock_fields_1973c"
NAMES = (QUERY, FIELDS)
NDK = _paths["llvm_bin"]()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tool(explicit, directory, name):
    suffix = ".exe" if os.name == "nt" else ""
    found = explicit or (str(directory / (name + suffix)) if directory else shutil.which(name))
    require(found and Path(found).is_file(), "missing explicit/local LLVM tool: " + name)
    return Path(found).resolve()


def run(argv, folder, label):
    result = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120)
    output = result.stdout + result.stderr
    (folder / (label + ".log")).write_bytes(output)
    require(result.returncode == 0, label + " failed; inspect local log")
    return dict(argv=[str(x) for x in argv], exit=result.returncode, log_sha256=hashlib.sha256(output).hexdigest()), output.decode("utf-8", errors="replace")


def elf_gate(path, linked):
    obj = ELF(path)
    require(obj.kind == (2 if linked else 1) and obj.flags == 1, "RV32 ELF, RVC, soft-float ABI")
    attributes = obj.data(obj.byname[".riscv.attributes"])
    arch = re.search(rb"rv32[a-z0-9_]+", attributes)
    require(arch is not None, "actual RISC-V architecture attribute")
    arch = arch.group().decode()
    require(arch.startswith("rv32i") and all("_" + letter in arch for letter in ("m", "a", "c")) and not any("_" + letter in arch for letter in ("f", "d", "v")), "actual RV32IMAC integer-only ISA attributes")
    und = sorted({s["name"] for s in obj.symbols if s["name"] and s["index"] == 0})
    require(not und, "no undefined runtime helpers/libcalls/stubs")
    globals_ = [s for s in obj.symbols if s["name"] and s["info"] >> 4 in (1, 2) and s["index"] != 0]
    require({s["name"] for s in globals_} == set(NAMES), "exact new reconstruction symbols; no original-symbol aliases")
    functions = [s for s in obj.symbols if (s["info"] & 15) == 2 and s["index"] != 0 and s["size"]]
    require({s["name"] for s in functions} == set(NAMES) and len(functions) == 2, "exact two emitted native functions, all primitives inlined")
    require(not any(s["size"] and s["flags"] & 1 for s in obj.sections), "no writable data/BSS/private runtime state")
    result = {}
    for symbol in functions:
        code = obj.function_bytes(symbol)
        require(code, "nonempty actual function")
        result[symbol["name"]] = dict(bytes=len(code), code_sha256=hashlib.sha256(code).hexdigest(), original_bytes=174 if symbol["name"] == QUERY else 40)
    return dict(kind=obj.kind, architecture=arch, flags=obj.flags, functions=result, undefined_symbols=und,
                relocations=len(obj.relocations), sha256=sha(path), writable_allocations=0)


def ir_body(text, name):
    match = re.search(r"^define\b[^\n]*@" + name + r"\([^\n]*\).*?\n\}", text, re.M | re.S)
    require(match is not None, "native IR function: " + name)
    return match.group()


def ir_gate(path):
    text = path.read_text(encoding="utf-8")
    require('target triple = "riscv32-unknown-unknown-elf"' in text or 'target triple = "riscv32-unknown-elf"' in text, "RV32 LLVM IR target")
    result = {}
    for name, gp_count in ((QUERY, 4), (FIELDS, 3)):
        body = ir_body(text, name)
        gp_lines = [line for line in body.splitlines() if "asm sideeffect" in line]
        require(len(gp_lines) == gp_count and all('"mv $0, gp"' in line and '"=r,~{memory}"()' in line for line in gp_lines), "exact live GP read primitive sites and memory clobbers")
        require(not any(" call " in line and "asm sideeffect" not in line for line in body.splitlines()), "no runtime helper calls in native IR")
        volatile = [line.strip() for line in body.splitlines() if "volatile" in line]
        definitions = dict(re.findall(r"^\s*(%[-\w.]+) = (.*)$", body, re.M))
        gp_values = [re.match(r"\s*(%[-\w.]+) =", line).group(1) for line in gp_lines]
        def dynamic_address(line):
            pointer = re.search(r", ptr (%[-\w.]+),", line)
            require(pointer is not None, "explicit dynamic GP-relative pointer")
            cast = re.fullmatch(r"inttoptr i32 (%[-\w.]+) to ptr", definitions[pointer.group(1)])
            require(cast is not None, "GP pointer cast from32bit address")
            return definitions[cast.group(1)]
        reads = [line for line in volatile if "load volatile" in line]
        writes = [line for line in volatile if "store volatile" in line]
        if name == QUERY:
            require(len(reads) == 9 and len(writes) == 2, "query static volatile access sites: nine reads/two stores")
            require(sum("load volatile i8" in line for line in reads) == 1 and all("load volatile i32" in line or "load volatile i8" in line for line in reads), "query one unsigned-byte table read and 32bit register/global reads")
            require(all("store volatile i32" in line for line in writes), "query exact32bit output stores")
            fixed_reads = [line for line in reads if "inttoptr (i32 " in line]
            require(len(fixed_reads) == 7 and sum("i32 1073876996 to ptr" in line for line in fixed_reads) == 6 and sum("i32 1073887232 to ptr" in line for line in fixed_reads) == 1, "query fixed volatile addresses only six RCC sites and one EXTEN site")
            require(dynamic_address(writes[0]) == "add i32 " + gp_values[0] + ", 108" and dynamic_address(writes[1]) == "add i32 " + gp_values[3] + ", 108", "query two output stores use distinct liveGPreads+108")
            global_read = [line for line in reads if "load volatile i32" in line and "inttoptr (i32 " not in line]
            require(len(global_read) == 1 and dynamic_address(global_read[0]) == "add i32 " + gp_values[2] + ", 108", "query fresh global load uses third liveGP+108")
            table_read = next(line for line in reads if "load volatile i8" in line)
            table_address = re.fullmatch(r"add i32 (%[-\w.]+), (%[-\w.]+)", dynamic_address(table_read))
            require(table_address is not None and definitions[table_address.group(1)] == "add i32 " + gp_values[1] + ", 64", "query tablebase uses second liveGP+64")
            index = re.fullmatch(r"and i32 (%[-\w.]+), 15", definitions[table_address.group(2)])
            require(index is not None and re.fullmatch(r"lshr i32 %[-\w.]+, 4", definitions[index.group(1)]), "query unsigned prescaler index masksfourbits")
            require(re.search(r"and i8 %[-\w.]+, 31", body) and re.search(r"lshr i32 %[-\w.]+, %[-\w.]+", body), "query unsigned shift with explicit lowfivebit mask")
        else:
            require(len(reads) == 1 and "load volatile i32" in reads[0], "fields one fresh32bit global read")
            require(len(writes) == 2 and "store volatile i8" in writes[0] and "store volatile i16" in writes[1], "fields byte before halfword store widths")
            require(dynamic_address(reads[0]) == "add i32 " + gp_values[0] + ", 108" and dynamic_address(writes[0]) == "add i32 " + gp_values[1] + ", 382" and dynamic_address(writes[1]) == "add i32 " + gp_values[2] + ", 380", "fields each load/store uses distinct liveGP and exact108/382/380offset")
            require(re.search(r"udiv i32 %[-\w.]+, 8000000", body) and not re.search(r"\bsdiv\b", body), "fields unsigned division by8000000")
            require(re.search(r"and i16 %[-\w.]+, 255", body) and re.search(r"mul i16 %[-\w.]+, 1000", body), "fields lowbyte truncation precedes multiply1000")
        result[name] = dict(GP_read_sites=len(gp_lines), volatile_read_sites=len(reads), volatile_write_sites=len(writes),
                            native_branch_semantics_proved=False, volatile_access_lines=volatile)
    return result


def machine_gate(text, elf_path):
    obj = ELF(elf_path)
    require(obj.kind == 2, "machine coverage binds actual linked ELF")
    results = {}
    for name, gp_count in ((QUERY, 4), (FIELDS, 3)):
        symbols = [s for s in obj.symbols if s["name"] == name and (s["info"] & 15) == 2 and s["index"] != 0]
        require(len(symbols) == 1, "one actual function symbol")
        symbol = symbols[0]
        code = obj.function_bytes(symbol)
        marker = re.search(r"^([0-9a-f]+) <" + name + r">:\s*$", text, re.M)
        require(marker is not None and int(marker.group(1), 16) == symbol["value"], "machine symbol address equals actual ELF")
        tail = text[marker.end():].lstrip("\r\n")
        rows = []
        cursor = 0
        for line in tail.splitlines():
            if not line.strip():
                break
            match = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
            require(match is not None, "no unparsed interior/trailing machine instruction lines")
            address, raw = int(match.group(1), 16), bytes.fromhex(match.group(2))
            require(address == symbol["value"] + cursor, "contiguous native instruction addresses")
            require(len(raw) in (2, 4) and len(raw) == (4 if raw[0] & 3 == 3 else 2), "complete instruction framing")
            require(cursor + len(raw) <= len(code) and raw == code[cursor:cursor + len(raw)], "every disassembly byte equals actual bounded ELF bytes")
            mnemonic, operands = match.group(3), match.group(4)
            allowed = {"lui", "li", "addi", "andi", "add", "and", "or", "xor", "not", "mv", "mul", "mulhu", "divu", "slli", "srli", "srl", "lw", "lbu", "sw", "sb", "sh", "beq", "bne", "bltz", "bgez", "beqz", "bnez", "j", "ret"}
            require(mnemonic in allowed, "supported integer-only native instruction profile")
            require(mnemonic not in ("call", "jal", "jalr", "tail", "ecall", "ebreak") and not mnemonic.startswith("csr"), "no hidden calls/traps/CSR operations")
            if len(raw) == 4:
                word = int.from_bytes(raw, "little")
                if word & 127 in (0x03, 0x13, 0x17, 0x33, 0x37, 0x67, 0x6F, 0x73):
                    require((word >> 7) & 31 != 3, "actual native instruction never writes GP")
            elif raw[0] & 3 in (1, 2):
                half = int.from_bytes(raw, "little")
                require((half >> 7) & 31 != 3 or mnemonic in ("beqz", "bnez", "j", "ret"), "compressed native instruction never writes GP")
            if re.search(r"\bgp\b", operands):
                require(mnemonic == "mv" and re.fullmatch(r"[a-z][a-z0-9]*, gp", operands), "GP used only by explicit live-read primitive")
            rows.append(dict(address=address, bytes=raw.hex(), mnemonic=mnemonic, operands=operands))
            cursor += len(raw)
        require(cursor == len(code), "full native function extent covered, no skipped/truncated bytes")
        boundaries = {row["address"] for row in rows}
        edges = []
        for i, row in enumerate(rows):
            if row["mnemonic"] in ("beq", "bne", "bltz", "bgez", "beqz", "bnez", "j"):
                target = re.search(r"(?:^|, )0x([0-9a-f]+)(?: |$)", row["operands"])
                require(target is not None and int(target.group(1), 16) in boundaries, "native branch target is an instruction boundary in same function")
                edges.append(dict(source=row["address"], target=int(target.group(1), 16), conditional=row["mnemonic"] != "j"))
            if row["mnemonic"] not in ("j", "ret"):
                require(i + 1 < len(rows), "all native fallthroughs remain inside function extent")
        require(rows[-1]["mnemonic"] == "ret", "actual function ends in RET")
        reads_gp = [r for r in rows if r["mnemonic"] == "mv" and r["operands"].endswith(", gp")]
        require(len(reads_gp) == gp_count, "actual machine exact GP-read sites")
        memory_ops = [r["mnemonic"] for r in rows if r["mnemonic"] in ("lb", "lbu", "lh", "lhu", "lw", "lwu", "ld", "sb", "sh", "sw", "sd", "flw", "fsw", "fld", "fsd")]
        require(set(memory_ops) <= ({"lw", "lbu", "sw"} if name == QUERY else {"lw", "sb", "sh"}), "actual native load/store width allowlist")
        results[name] = dict(entry_address=symbol["value"], bytes=len(code), instruction_rows=len(rows),
                             covered_bytes=cursor, raw_bytes_match=True, contiguous=True, GP_reads=len(reads_gp), GP_writes=0,
                             memory_instruction_widths=memory_ops, native_branch_semantics_proved=False)
        results[name]["direct_CFG_edges"] = edges
    return results


def transcript_controls(text, elf):
    reports = []
    for name in NAMES:
        marker = re.search(r"^([0-9a-f]+) <" + name + r">:\s*$", text, re.M)
        require(marker is not None, "actual transcript symbol")
        head, tail = text[:marker.end()], text[marker.end():]
        lines = tail.splitlines(keepends=True)
        indexes = []
        for index, line in enumerate(lines):
            if indexes and not line.strip():
                break
            if re.match(r"\s*[0-9a-f]+:", line):
                indexes.append(index)
        require(len(indexes) >= 3, "actual complete transcript rows")
        variants = {}
        for label, index in (("missing_first", indexes[0]), ("missing_middle", indexes[len(indexes) // 2]), ("truncated_last", indexes[-1])):
            variants[label] = head + "".join(line for i, line in enumerate(lines) if i != index)
        changed = list(lines)
        changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}", r"\g<1>00", changed[indexes[1]], count=1)
        require(changed[indexes[1]] != lines[indexes[1]], "changed actual raw byte")
        variants["changed_raw_byte"] = head + "".join(changed)
        for label, index in (("unparsed_middle", indexes[1]), ("unparsed_trailing", indexes[-1] + 1)):
            changed = list(lines)
            changed.insert(index, "    UNPARSED-INSTRUCTION\n")
            variants[label] = head + "".join(changed)
        for label, changed in variants.items():
            try:
                machine_gate(changed, elf)
            except ValueError as error:
                reports.append(dict(function=name, case=label, rejected=True, reason=str(error), transcript_sha256=hashlib.sha256(changed.encode()).hexdigest()))
            else:
                raise ValueError("incomplete/modified native transcript admitted: " + label)
    return reports


def source_controls(source, header, flags, tools, folder):
    cases = [
        ("fixed_GP", '__asm__ volatile("mv %0, gp" : "=r"(value) : : "memory");', 'value = UINT32_C(0x20004000);'),
        ("wrong_global_offset", "write32(current_gp() + 108u, frequency);", "write32(current_gp() + 112u, frequency);"),
        ("wrong_table_width", "const uint8_t shift = read8(current_gp() + 64u + index);", "const uint8_t shift = (uint8_t)read32(current_gp() + 64u + index); (void)read8;"),
        ("lost_quotient_truncation", "(frequency / UINT32_C(8000000)) & 255u", "(frequency / UINT32_C(8000000))"),
        ("signed_division", "frequency / UINT32_C(8000000)", "(uint32_t)((int32_t)frequency / INT32_C(8000000))"),
    ]
    text = source.read_text(encoding="utf-8-sig")
    reports = []
    for name, before, after in cases:
        require(text.count(before) == 1, "single intentional native source mutation site")
        case = folder / ("negative-" + name)
        case.mkdir(exist_ok=False)
        changed = case / "native_clock.c"
        changed.write_text(text.replace(before, after), encoding="utf-8")
        (case / "native_clock.h").write_bytes(header.read_bytes())
        obj, ir = case / "mutant.o", case / "mutant.ll"
        run([tools["clang"], *flags, "-c", changed, "-o", obj], case, "compile")
        run([tools["clang"], *flags, "-S", "-emit-llvm", changed, "-o", ir], case, "llvm-ir")
        try:
            ir_gate(ir)
        except ValueError as error:
            reports.append(dict(case=name, actual_compilation_succeeded=True, rejected=True, reason=str(error), source_sha256=sha(changed), object_sha256=sha(obj), LLVM_IR_sha256=sha(ir)))
        else:
            raise ValueError("native source mutant admitted: " + name)
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
    model = root / "experiments/tsl9-v4160-native-clock"
    source, header = model / "src/native_clock.c", model / "src/native_clock.h"
    require(source.is_file() and header.is_file(), "actual native C/H source inputs")
    directory = args.tool_dir or (NDK if os.name == "nt" and NDK.is_dir() else None)
    tools = {"clang": tool(args.clang, directory, "clang"), "linker": tool(args.linker, directory, "ld.lld"), "objdump": tool(args.objdump, directory, "llvm-objdump")}
    pins = {name: sha(path) for name, path in tools.items()}
    inputs = {p.relative_to(root).as_posix(): sha(p) for p in (source, header)}
    scripts = {p.name: sha(p) for p in (Path(__file__), HERE / "elf32.py")}
    results = []
    for mode in (("c", "cpp") if args.language == "both" else (args.language,)):
        folder = HERE / "build" / ("native-" + uuid.uuid4().hex + "-" + mode)
        folder.mkdir(parents=True, exist_ok=False)
        obj, ir, elf = folder / "native_clock.o", folder / "native_clock.ll", folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-ffunction-sections", "-fdata-sections", "-mno-relax", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17"]
        if mode == "cpp":
            flags += ["-fno-exceptions", "-fno-rtti"]
        commands = []
        for label, argv in [("compile", [tools["clang"], *flags, "-c", source, "-o", obj]), ("llvm-ir", [tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir])]:
            record, _ = run(argv, folder, label)
            commands.append(record)
        ir_result = ir_gate(ir)
        object_result = elf_gate(obj, False)
        record, _ = run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + QUERY, "-Ttext=0x1000", obj, "-o", elf], folder, "component-link")
        commands.append(record)
        linked_result = elf_gate(elf, True)
        require(linked_result["functions"] == object_result["functions"], "actual link preserves every native function byte")
        record, disassembly = run([tools["objdump"], "--disassemble", elf], folder, "component-disassembly")
        commands.append(record)
        machine_result = machine_gate(disassembly, elf)
        transcripts = transcript_controls(disassembly, elf)
        negatives = source_controls(source, header, flags, tools, folder)
        require(all(sha(root / name) == digest for name, digest in inputs.items()), "C/H inputs unchanged")
        require(all(sha(HERE / name) == digest for name, digest in scripts.items()), "verifier inputs unchanged")
        require(all(sha(tools[name]) == digest for name, digest in pins.items()), "LLVM executable pins unchanged")
        report = dict(schema="TSL9-readable-native-clock-structural-verification-v1", passed=True, mode=mode,
                      source_sha256=inputs, script_inputs_sha256=scripts, tools={name: dict(path=str(path), sha256=pins[name]) for name, path in tools.items()},
                      commands=commands, flags=flags, object=object_result, linked_component=linked_result,
                      LLVM_IR=ir_result, LLVM_IR_sha256=sha(ir), machine_static_coverage=machine_result,
                      actual_compiled_source_controls=negatives, actual_transcript_controls=transcripts,
                      native_branch_semantics_proved=False, original_fixed_placement_proved=False, original_C_ABI_proved=False,
                      original_IRQ_ABI_proved=False, firmware_executed=False, ISA_emulation=False, network=False, hardware=False, OTA_ready=False)
        receipt = folder / "verification.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(receipt), sha256=sha(receipt), functions=object_result["functions"]))
    print(json.dumps(dict(passed=True, results=results)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print("Native clock static verification failed: " + str(error), file=sys.stderr)
        sys.exit(1)
