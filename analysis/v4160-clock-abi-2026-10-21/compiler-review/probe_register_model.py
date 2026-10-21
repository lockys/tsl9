"""Bounded actual new register-contract model feasibility probes."""
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
    build = HERE / "build" / ("register-model-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    pinned = {p.name: base.sha(p) for p in sorted(model.iterdir()) if p.is_file()}
    results = []
    for unit, allowed_sets in (("clock_query", [{13, 14, 15}, {12, 13, 14, 15}]), ("clock_fields", [{14, 15}])):
        for allowed in allowed_sets:
            for opt in ("Os", "Oz"):
                folder = build / (unit + "-" + str(len(allowed)) + "regs-" + opt)
                folder.mkdir()
                obj = folder / "candidate.o"
                source = model / (unit + ".c")
                flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-" + opt, "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c", "-std=c11", *base.profile_flags(allowed)]
                code, output, cmd = base.run([base.TOOLS / "clang.exe", *flags, "-c", source, "-o", obj], folder, "compile")
                record = dict(unit=unit, allowed_allocator_registers=sorted(allowed), optimization=opt, compile_exit=code, command=cmd)
                if code:
                    record["compiler_error"] = output[-2200:]
                    results.append(record)
                    continue
                _, text, _ = base.run([base.TOOLS / "llvm-objdump.exe", "--disassemble", obj], folder, "disassembly")
                rows = []
                for line in text.splitlines():
                    m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*", line)
                    if m:
                        rows.append(dict(offset=int(m.group(1), 16), bytes=m.group(2).split(), mnemonic=m.group(3), operands=m.group(4)))
                writes = set()
                for row in rows:
                    if row["mnemonic"] not in ("ret", "j", "beq", "bne", "beqz", "bnez", "blt", "bge", "bltu", "bgeu", "bltz", "bgez", "sb", "sh", "sw"):
                        first = re.match(r"([a-z][a-z0-9]*)(?:,|$)", row["operands"])
                        if first:
                            writes.add(first.group(1))
                record.update(object_sha256=base.sha(obj), instruction_rows=len(rows), machine_bytes=sum(len(row["bytes"]) for row in rows),
                              registers_written=sorted(writes), SP_mentioned=any(re.search(r"\bsp\b", row["operands"]) for row in rows),
                              divu_count=sum(row["mnemonic"] == "divu" for row in rows))
                results.append(record)
    assert all(base.sha(model / name) == digest for name, digest in pinned.items())
    report = dict(schema="TSL9-original-register-contract-compiler-probe-v1", source_sha256=pinned,
                  clang_sha256=base.sha(base.TOOLS / "clang.exe"), results=results,
                  RV32_executed=False, ISA_emulation=False, network=False, hardware=False)
    (build / "probe-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(report=str(build / "probe-results.json"), results=[{k:v for k,v in item.items() if k not in ("command", "compiler_error")} for item in results])))


if __name__ == "__main__":
    main()
