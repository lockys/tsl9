"""Finite local register-reservation compiler probes; never execute RV32."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import uuid

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLS = _paths["llvm_bin"]()
SOURCE = ROOT / "experiments/tsl9-v4160-native-clock/src/native_clock.c"
HEADER = SOURCE.with_suffix(".h")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv, folder, label):
    p = subprocess.run([str(a) for a in argv], cwd=folder, capture_output=True, timeout=120)
    (folder / (label + ".log")).write_bytes(p.stdout + p.stderr)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", errors="replace"), [str(a) for a in argv]


def profile_flags(allowed):
    # x0 is inherently zero; GP/TP/SP/RA are also reserved to forbid their
    # use as allocator temporaries. A read-only RET may still read reserved RA.
    return ["-ffixed-x" + str(r) for r in range(1, 32) if r not in allowed]


def main():
    src = SOURCE.read_text(encoding="utf-8-sig")
    source_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in (SOURCE, HEADER)}
    prefix = src[:src.index("/* Source contract:")]
    qstart = src.index("void tsl9_rebuild_clock_query_18834")
    dcomment = src.index("/* Source contract:", qstart)
    query = src[qstart:dcomment]
    fields = src[src.index("void tsl9_rebuild_clock_fields_1973c"):]
    divu = "\nstatic uint32_t exact_divu(uint32_t numerator, uint32_t denominator) {\n    uint32_t quotient;\n    __asm__(\"divu %0, %1, %2\" : \"=r\"(quotient) : \"r\"(numerator), \"r\"(denominator));\n    return quotient;\n}\n"
    fixed_fields = fields.replace("frequency / UINT32_C(8000000)", "exact_divu(frequency, UINT32_C(8000000))")
    assert fixed_fields != fields
    variants = {"query": prefix + query, "fields": prefix + fields, "fields-divu": prefix + divu + fixed_fields}
    cases = []
    for name in variants:
        allowed = {12, 13, 14, 15} if name == "query" else {14, 15}
        for opt in ("Os", "Oz"):
            cases.append((name, opt, "ordinary", []))
            cases.append((name, opt, "preserve-a0-a1", ["-ffixed-x10", "-ffixed-x11"]))
            cases.append((name, opt, "source-clobbers-only", profile_flags(allowed)))
    build = HERE / "build" / ("probe-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    results = []
    for name, opt, label, flags in cases:
        folder = build / (name + "-" + opt + "-" + label)
        folder.mkdir()
        source = folder / "native_clock.c"
        source.write_text(variants[name], encoding="utf-8")
        (folder / "native_clock.h").write_bytes(HEADER.read_bytes())
        obj = folder / "component.o"
        cc = [TOOLS / "clang.exe", "--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-x", "c", "-std=c11", *flags, "-c", source, "-o", obj]
        code, output, command = run(cc, folder, "compile")
        record = dict(variant=name, optimization=opt, profile=label, reservation_flags=flags, source_sha256=sha(source), compilation_exit=code, command=command)
        if code:
            record["compile_error"] = output[-1800:]
            results.append(record)
            continue
        code, text, command = run([TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
        record["disassembler_exit"] = code
        record["object_sha256"] = sha(obj)
        record["disassembly_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        rows = []
        for line in text.splitlines():
            m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
            if m:
                rows.append(dict(offset=int(m.group(1), 16), bytes=m.group(2).split(), mnemonic=m.group(3), operands=m.group(4)))
        writes = set()
        all_regs = set()
        for row in rows:
            op, args = row["mnemonic"], row["operands"]
            all_regs.update(re.findall(r"\b(?:zero|ra|sp|gp|tp|[ast][0-9]+)\b", args))
            if op not in ("ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"):
                match = re.match(r"([a-z][a-z0-9]*)(?:,|$)", args)
                if match:
                    writes.add(match.group(1))
        record.update(instruction_rows=len(rows), machine_bytes=sum(len(row["bytes"]) for row in rows), registers_written=sorted(writes), registers_mentioned=sorted(all_regs), SP_mentioned="sp" in all_regs, divu_count=sum(row["mnemonic"] == "divu" for row in rows))
        results.append(record)
    report = dict(schema="TSL9-clock-register-allocation-probe-v1", source_sha256=source_hashes,
                  tool_sha256={p.name: sha(p) for p in [TOOLS / "clang.exe", TOOLS / "llvm-objdump.exe"]},
                  profile_count=len(cases), results=results, RV32_executed=False, ISA_emulation=False, hardware=False, network=False)
    (build / "probe-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), cases=[{k:r[k] for k in ("variant", "optimization", "profile", "compilation_exit", "machine_bytes", "registers_written", "SP_mentioned", "divu_count") if k in r} for r in results])))


if __name__ == "__main__":
    main()
