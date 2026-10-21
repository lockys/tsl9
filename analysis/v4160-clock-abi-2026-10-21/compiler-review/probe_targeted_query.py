"""Two explicitly scoped query register-pressure experiments; no target run."""
import importlib.util
import json
from pathlib import Path
import re
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("clock_probe", HERE / "probe_compiler.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def main():
    model = base.ROOT / "experiments/tsl9-v4160-clock-registers/src"
    query = (model / "clock_query.c").read_text(encoding="utf-8-sig")
    header = (model / "clock_io.h").read_text(encoding="utf-8-sig")
    addition = '''static inline uint32_t ca_external_mask(void) {
    register uint32_t mask __asm__("a2")=UINT32_C(0xc00000);
    __asm__ volatile("" : "+r"(mask) : : "memory");
    return mask;
}
static inline uint32_t ca_residue_a3(uint32_t value) {
    register uint32_t residue __asm__("a3")=value;
    __asm__ volatile("" : "+r"(residue) : : "memory");
    return residue;
}
'''
    at = header.index("#define CA_SET_A2(v) do")
    header = header[:at] + addition + header[at:]
    assert query.count("CA_SET_A2(UINT32_C(0xc00000));") == 1
    query = query.replace("CA_SET_A2(UINT32_C(0xc00000));", "const uint32_t external_mask=ca_external_mask();")
    query = query.replace("(external_sample&UINT32_C(0xc00000))==UINT32_C(0xc00000)", "(external_sample&external_mask)==external_mask")
    anchored = query.replace("    CA_WRITE32(CA_GP()+108u,frequency);", "    residue_a3=ca_residue_a3(residue_a3);\n    CA_WRITE32(CA_GP()+108u,frequency);")
    assert anchored != query
    variants = {"opaque_external_mask": query, "opaque_mask_and_A3_anchor": anchored}
    build = HERE / "build" / ("targeted-query-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    results = []
    for name, text in variants.items():
        for opt in ("Os", "Oz"):
            folder = build / (name + "-" + opt)
            folder.mkdir()
            source, obj = folder / "clock_query.c", folder / "query.o"
            source.write_text(text, encoding="utf-8")
            (folder / "clock_io.h").write_text(header, encoding="utf-8")
            (folder / "clock_registers.h").write_bytes((model / "clock_registers.h").read_bytes())
            flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c", "-std=c11", *base.profile_flags({13, 14, 15})]
            code, error, command = base.run([base.TOOLS / "clang.exe", *flags, "-c", source, "-o", obj], folder, "compile")
            item = dict(variant=name, optimization=opt, compilation_exit=code, source_sha256=base.sha(source), header_sha256=base.sha(folder / "clock_io.h"), command=command)
            if code:
                item["compile_error"] = error[-2000:]
            else:
                _, assembly, _ = base.run([base.TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
                rows = []
                for line in assembly.splitlines():
                    m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
                    if m:
                        rows.append(dict(offset=int(m.group(1), 16), raw=m.group(2).split(), mnemonic=m.group(3), operands=m.group(4)))
                writes = set()
                for row in rows:
                    if row["mnemonic"] not in ("ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"):
                        m = re.match(r"([a-z][a-z0-9]*)(?:,|$)", row["operands"])
                        if m:
                            writes.add(m.group(1))
                item.update(object_sha256=base.sha(obj), machine_bytes=sum(len(row["raw"]) for row in rows), instruction_rows=len(rows), registers_written=sorted(writes), SP_mentioned=any(re.search(r"\bsp\b", row["operands"]) for row in rows))
            results.append(item)
    report = dict(schema="TSL9-two-targeted-query-pressure-probes-v1", source_model_sha256={p.name:base.sha(p) for p in sorted(model.iterdir()) if p.is_file()},
                  results=results, RV32_executed=False, ISA_emulation=False, hardware=False, network=False)
    (build / "probe-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), results=[{k:v for k,v in item.items() if k not in ("command", "compile_error")} for item in results])))


if __name__ == "__main__":
    main()
