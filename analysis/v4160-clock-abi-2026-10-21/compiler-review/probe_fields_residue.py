"""Finite actual compile probes for explicit final A4/A5 field residues."""
import importlib.util
import json
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gp_probe", HERE / "probe_compiler.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def main():
    text = base.SOURCE.read_text(encoding="utf-8-sig")
    prefix = text[:text.index("/* Source contract:")]
    prefix = prefix.replace('    uint32_t value;\n    __asm__ volatile("mv %0, gp" : "=r"(value) : : "memory");', '    register uint32_t value __asm__("gp");\n    __asm__ volatile("" : "=r"(value) : : "memory");')
    fields = text[text.index("void tsl9_rebuild_clock_fields_1973c"):]
    primitive = '\nstatic uint32_t exact_divu(uint32_t n, uint32_t d) { uint32_t q; __asm__("divu %0, %1, %2" : "=r"(q) : "r"(n), "r"(d)); return q; }\n'
    fields = fields.replace("frequency / UINT32_C(8000000)", "exact_divu(frequency, UINT32_C(8000000))")
    before = "    write16(current_gp() + 380u, (uint16_t)(quotient * 1000u));"
    after = '''    register uint32_t final_a4 __asm__("a4") = UINT32_C(1000);
    __asm__ volatile("" : "+r"(final_a4) : : "memory");
    register uint32_t final_a5 __asm__("a5") = quotient * final_a4;
    write16(current_gp() + 380u, (uint16_t)final_a5);
    __asm__ volatile("" : : "r"(final_a4), "r"(final_a5) : "memory");'''
    assert fields.count(before) == 1
    fields = fields.replace(before, after)
    source_text = prefix + primitive + fields
    build = HERE / "build" / ("residue-probe-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    results = []
    for opt in ("Os", "Oz"):
        for mode in ("c", "cpp"):
            folder = build / (opt + "-" + mode)
            folder.mkdir()
            source, obj = folder / "candidate_fields.c", folder / "candidate_fields.o"
            source.write_text(source_text, encoding="utf-8")
            (folder / "native_clock.h").write_bytes(base.HEADER.read_bytes())
            flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17", *base.profile_flags({14, 15})]
            code, error, cmd = base.run([base.TOOLS / "clang.exe", *flags, "-c", source, "-o", obj], folder, "compile")
            record = dict(mode=mode, optimization=opt, compile_exit=code, source_sha256=base.sha(source), command=cmd)
            if code:
                record["compile_error"] = error[-1800:]
            else:
                _, disasm, _ = base.run([base.TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
                record["object_sha256"] = base.sha(obj)
            results.append(record)
    (build / "probe-results.json").write_text(json.dumps(dict(schema="TSL9-final-fields-residue-probe-v1", results=results), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), results=[{k:v for k,v in item.items() if k not in ("command", "compile_error")} for item in results])))


if __name__ == "__main__":
    main()
