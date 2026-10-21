"""Bounded empty-asm GP observation variants; no target execution."""
import importlib.util
import json
from pathlib import Path
import re
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("clock_probe_base", HERE / "probe_compiler.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def main():
    source = base.SOURCE.read_text(encoding="utf-8-sig")
    prefix = source[:source.index("/* Source contract:")]
    gp_body = '    uint32_t value;\n    __asm__ volatile("mv %0, gp" : "=r"(value) : : "memory");'
    gp_empty = '    register uint32_t value __asm__("gp");\n    __asm__ volatile("" : "=r"(value) : : "memory");'
    assert prefix.count(gp_body) == 1
    prefix = prefix.replace(gp_body, gp_empty)
    qstart = source.index("void tsl9_rebuild_clock_query_18834")
    query = source[qstart:source.index("/* Source contract:", qstart)]
    fields = source[source.index("void tsl9_rebuild_clock_fields_1973c"):]
    divu = '\nstatic uint32_t exact_divu(uint32_t n, uint32_t d) { uint32_t q; __asm__("divu %0, %1, %2" : "=r"(q) : "r"(n), "r"(d)); return q; }\n'
    variants = {"query": prefix + query, "fields": prefix + fields,
                "fields-divu": prefix + divu + fields.replace("frequency / UINT32_C(8000000)", "exact_divu(frequency, UINT32_C(8000000))")}
    build = HERE / "build" / ("gp-probe-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    results = []
    for name, variant_source in variants.items():
        allowed = {12, 13, 14, 15} if name == "query" else {14, 15}
        for opt in ("Os", "Oz"):
            folder = build / (name + "-" + opt)
            folder.mkdir()
            src, obj = folder / "candidate.c", folder / "candidate.o"
            src.write_text(variant_source, encoding="utf-8")
            (folder / "native_clock.h").write_bytes(base.HEADER.read_bytes())
            flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-x", "c", "-std=c11", *base.profile_flags(allowed)]
            code, output, cmd = base.run([base.TOOLS / "clang.exe", *flags, "-c", src, "-o", obj], folder, "compile")
            item = dict(variant=name, optimization=opt, compilation_exit=code, source_sha256=base.sha(src), compile_command=cmd)
            if code:
                item["compile_error"] = output[-1800:]
                results.append(item)
                continue
            code, disassembly, cmd = base.run([base.TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
            rows = []
            for line in disassembly.splitlines():
                m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
                if m:
                    rows.append(dict(offset=int(m.group(1), 16), bytes=m.group(2).split(), mnemonic=m.group(3), operands=m.group(4)))
            writes = set()
            for row in rows:
                if row["mnemonic"] not in ("ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"):
                    first = re.match(r"([a-z][a-z0-9]*)(?:,|$)", row["operands"])
                    if first:
                        writes.add(first.group(1))
            item.update(object_sha256=base.sha(obj), machine_bytes=sum(len(row["bytes"]) for row in rows),
                        instruction_rows=len(rows), registers_written=sorted(writes),
                        SP_mentioned=any(re.search(r"\bsp\b", row["operands"]) for row in rows),
                        divu_count=sum(row["mnemonic"] == "divu" for row in rows))
            results.append(item)
    report = dict(schema="TSL9-fixed-GP-empty-asm-probe-v1", source_sha256=base.sha(base.SOURCE),
                  clang_sha256=base.sha(base.TOOLS / "clang.exe"), results=results,
                  RV32_executed=False, ISA_emulation=False, hardware=False, network=False)
    (build / "probe-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), results=[{k:v for k,v in item.items() if k not in ("compile_command", "compile_error")} for item in results])))


if __name__ == "__main__":
    main()
