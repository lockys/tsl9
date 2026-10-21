"""Last two-profile query experiment: reuse original A3 compare constants."""
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
    prior = HERE / "build/targeted-query-36ec62f99dc441dba5ec2be0b96007c4/opaque_mask_and_A3_anchor-Os"
    assert base.sha(prior / "clock_query.c") == "59e883ab3099f518bbebbec67709c933e3d49bf9d597198eceecc49443af6ca4"
    assert base.sha(prior / "clock_io.h") == "7eb1d7c23eb2c0a53135037d39f8125d5b5f9ce3e352a21141c7d50a9c1039a6"
    source = '''#include "clock_registers.h"
#include "clock_io.h"
void tsl9_rebuild_clock_query_registers_18834(void) {
    const uint32_t rcc=UINT32_C(0x40021004);
    const uint32_t selector=CA_READ32(rcc)&12u;
    uint32_t frequency,residue_a3;
    residue_a3=ca_residue_a3(4u);
    if(selector==residue_a3) {
        frequency=UINT32_C(32000000);
    } else {
        residue_a3=ca_residue_a3(8u);
        if(selector==residue_a3) {
            const uint32_t multiplier_sample=CA_READ32(rcc);
            const uint32_t source_sample=CA_READ32(rcc);
            uint32_t multiplier=((multiplier_sample>>18)&15u)+2u;
            uint32_t base;
            residue_a3=ca_residue_a3(17u);
            if(multiplier==residue_a3)multiplier=18u;
            if((source_sample&UINT32_C(0x10000))==0u) {
                const uint32_t control=CA_READ32(UINT32_C(0x40023800));
                base=(control&16u)!=0u?UINT32_C(8000000):UINT32_C(4000000);
            } else {
                const uint32_t external_sample=CA_READ32(rcc);
                const uint32_t external_mask=ca_external_mask();
                residue_a3=UINT32_C(0x40021000);
                if((external_sample&external_mask)==external_mask) {
                    base=UINT32_C(16000000);
                } else {
                    const uint32_t fallback_sample=CA_READ32(rcc);
                    residue_a3=fallback_sample<<14;
                    base=(residue_a3&UINT32_C(0x80000000))!=0u
                         ?UINT32_C(4000000):UINT32_C(8000000);
                }
            }
            frequency=multiplier*base;
        } else {
            frequency=UINT32_C(8000000);
        }
    }
    CA_WRITE32(CA_GP()+108u,frequency);
    {
        const uint32_t prescaler_sample=CA_READ32(rcc);
        const uint8_t shift=CA_READ8(CA_GP()+64u+((prescaler_sample>>4)&15u));
        const uint32_t live_frequency=CA_READ32(CA_GP()+108u);
        const uint32_t result=live_frequency>>(shift&31u);
        CA_WRITE32(CA_GP()+108u,result);
        CA_QUERY_OUTPUTS(residue_a3,(uint32_t)shift,result);
    }
}
'''
    build = HERE / "build" / ("reuse-a3-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    results = []
    for opt in ("Os", "Oz"):
        folder = build / opt
        folder.mkdir()
        src, obj = folder / "clock_query.c", folder / "query.o"
        src.write_text(source, encoding="utf-8")
        for name in ("clock_io.h", "clock_registers.h"):
            (folder / name).write_bytes((prior / name).read_bytes())
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c", "-std=c11", *base.profile_flags({13, 14, 15})]
        code, output, cmd = base.run([base.TOOLS / "clang.exe", *flags, "-c", src, "-o", obj], folder, "compile")
        record = dict(optimization=opt, compile_exit=code, command=cmd, source_sha256=base.sha(src), header_sha256=base.sha(folder / "clock_io.h"))
        if code:
            record["compile_error"] = output[-1800:]
        else:
            _, text, _ = base.run([base.TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
            rows = []
            for line in text.splitlines():
                m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
                if m:
                    rows.append(dict(raw=m.group(2).split(), mnemonic=m.group(3), operands=m.group(4)))
            writes = set()
            for row in rows:
                if row["mnemonic"] not in ("ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"):
                    first = re.match(r"([a-z][a-z0-9]*)(?:,|$)", row["operands"])
                    if first:
                        writes.add(first.group(1))
            record.update(object_sha256=base.sha(obj), machine_bytes=sum(len(row["raw"]) for row in rows), instruction_rows=len(rows), registers_written=sorted(writes), SP_mentioned=any(re.search(r"\bsp\b", row["operands"]) for row in rows))
        results.append(record)
    (build / "probe-results.json").write_text(json.dumps(dict(schema="TSL9-original-A3-compare-reuse-probe-v1", results=results, RV32_executed=False, ISA_emulation=False, hardware=False, network=False), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), results=[{k:v for k,v in row.items() if k not in ("command", "compile_error")} for row in results])))


if __name__ == "__main__":
    main()
