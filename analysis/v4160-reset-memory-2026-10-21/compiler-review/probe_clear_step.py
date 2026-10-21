"""One diagnostic clear-step barrier source variant, C and C++; no RV32 run."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("reset_native_probe", HERE / "verify_native.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def main():
    project = HERE.parents[2]
    src = project / "experiments/tsl9-v4160-reset-memory/src"
    text = (src / "reset_memory.c").read_text(encoding="utf-8-sig")
    initial = {p.name: v.sha(p) for p in src.iterdir() if p.is_file()}
    require = v.require
    require(text.count("#define RM_GP() tsl9_rm_test_gp()") == 1 and text.count("#define RM_GP() rm_live_gp()") == 1 and text.count("clear+=4u;") == 1, "one explicit step mutation and primitive branches")
    text = text.replace("#define RM_GP() tsl9_rm_test_gp()", "#define RM_GP() tsl9_rm_test_gp()\n#define RM_CLEAR_STEP(v) (v)")
    text = text.replace("#define RM_GP() rm_live_gp()", '''static inline uint32_t rm_clear_step(uint32_t value)
{
    register uint32_t next __asm__("a0")=value;
    __asm__ volatile("" : "+r"(next) : : "memory");
    return next;
}
#define RM_CLEAR_STEP(v) rm_clear_step(v)
#define RM_GP() rm_live_gp()''')
    text = text.replace("clear+=4u;", "clear=RM_CLEAR_STEP(clear+4u);")
    build = HERE / "build" / ("clear-step-probe-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    tools = {"clang": v.NDK / "clang.exe", "linker": v.NDK / "ld.lld.exe", "objdump": v.NDK / "llvm-objdump.exe"}
    results = []
    for mode in ("c", "cpp"):
        folder = build / mode
        folder.mkdir()
        source, obj, ir = folder / "reset_memory.c", folder / "reset_memory.o", folder / "reset_memory.ll"
        source.write_text(text, encoding="utf-8")
        (folder / "reset_memory.h").write_bytes((src / "reset_memory.h").read_bytes())
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17", *["-ffixed-x" + str(i) for i in range(1, 32) if i not in {5,10,11,12}]]
        commands = []
        for label, argv in [("compile", [tools["clang"], *flags, "-c", source, "-o", obj]), ("llvm-ir", [tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir])]:
            command, _ = v.run(argv, folder, label)
            commands.append(command)
        linked = folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        command, _ = v.run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + v.ENTRY, "-Ttext=0x1000", obj, "-o", linked], folder, "link")
        commands.append(command)
        command, disassembly = v.run([tools["objdump"], "--disassemble", linked], folder, "disassembly")
        commands.append(command)
        checked = v.machine_gate(disassembly, linked)
        report = dict(schema="TSL9-one-clear-step-barrier-probe-v1", passed=True, mode=mode,
                      source_sha256=v.sha(source), original_parent_source_sha256=initial,
                      object=v.elf_gate(obj), linked=v.elf_gate(linked, linked=True),
                      LLVM_IR=v.ir_gate(ir), LLVM_IR_sha256=v.sha(ir), machine=checked,
                      physical_GP_operand_reads=sum(bool(re.search(r"\bgp\b", row["operands"])) for row in checked["rows"]),
                      commands=commands, native_flags=flags, tool_sha256={name:v.sha(path) for name,path in tools.items()},
                      parent_sources_modified=False, firmware_executed=False, ISA_emulation=False, hardware=False, network=False)
        receipt = folder / "verification.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(receipt), sha256=v.sha(receipt), helper_bytes=checked["helper_bytes"], instructions=checked["instruction_rows"], physical_GP_reads=report["physical_GP_operand_reads"], IR_GP_sites=report["LLVM_IR"]["GP_observation_sites"], source_sha256=v.sha(source)))
    require(all(v.sha(src / name) == digest for name,digest in initial.items()), "parent sources unchanged")
    (build / "probe-results.json").write_text(json.dumps(dict(passed=True, results=results), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, results=results)))


if __name__ == "__main__":
    main()
