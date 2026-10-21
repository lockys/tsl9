"""One source lifetime variant, same -Oz/three-register profile; no execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
from elf32 import ELF, require
from probe_allocator_a1 import raw_facts, ENTRY

HERE = Path(__file__).resolve().parent
SOURCES = {"interrupt_registers.c": "d3000829bd171e12d7fd6fe9ba5532c76635dce730d64628b3044d06b3724321", "interrupt_registers.h": "da57cec48aa144786cd9a64c8d20aadd2bb02d9e91d43408eac6441f7ba3ae59", "irq_io.h": "2ced66889c82da11b595b9dab734c8af4fdd4bb365390a534ec3611f0d5398f7"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path, required=True)
    p.add_argument("--allow-a1", action="store_true", help="Only the final authorized 2x2 combination")
    a = p.parse_args()
    root = a.project_root.resolve()
    source = root / "experiments/tsl9-v4160-interrupt-registers/src"
    require({name: sha(source / name) for name in SOURCES} == SOURCES, "frozen parent inputs")
    folder = HERE / "build" / ("return-commit-" + uuid.uuid4().hex)
    folder.mkdir(parents=True)
    for name in SOURCES:
        (folder / name).write_bytes((source / name).read_bytes())
    c = (folder / "interrupt_registers.c").read_text(encoding="utf-8-sig")
    old = "    if(enabled)IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),before);\n    else IR_RCC_OUTPUTS(after,enabled,before,UINT32_C(0x40021000));\n    return after;"
    new = "    if(enabled)return IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),before);\n    else return IR_RCC_OUTPUTS(after,enabled,before,UINT32_C(0x40021000));"
    require(c.count(old) == 1, "one exact helper lifetime site")
    c = c.replace(old, new)
    old = "    IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));\n    return result;"
    new = "    return IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));"
    require(c.count(old) == 1, "one exact initializer return site")
    (folder / "interrupt_registers.c").write_text(c.replace(old, new), encoding="utf-8")
    header = (folder / "irq_io.h").read_text(encoding="utf-8-sig")
    start, end = header.index("#define IR_COMMIT"), header.index("#endif", header.index("#define IR_COMMIT"))
    replacement = '''IR_INLINE uint32_t ir_commit(uint32_t v0,uint32_t v1,uint32_t v4,uint32_t v5)
{
    register uint32_t ir_a0 __asm__("a0")=v0;
    register uint32_t ir_a1 __asm__("a1")=v1;
    register uint32_t ir_a4 __asm__("a4")=v4;
    register uint32_t ir_a5 __asm__("a5")=v5;
    __asm__ volatile("" : "+r"(ir_a0) : "r"(ir_a1),"r"(ir_a4),"r"(ir_a5) : "memory");
    return ir_a0;
}
#define IR_RCC_OUTPUTS(a0,a1,a4,a5) ir_commit(a0,a1,a4,a5)
#define IR_INIT_OUTPUTS(a0,a1,a4,a5) ir_commit(a0,a1,a4,a5)
'''
    (folder / "irq_io.h").write_text(header[:start] + replacement + header[end:], encoding="utf-8")
    suffix = ".exe" if __import__("os").name == "nt" else ""
    tools = {name: a.tool_dir / (exe + suffix) for name, exe in (("clang", "clang"), ("linker", "ld.lld"), ("objdump", "llvm-objdump"))}
    flags = ["--target=riscv32-unknown-elf", "-march=rv32imac_zicsr", "-mabi=ilp32", "-Oz", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", *["-ffixed-x" + str(x) for x in range(1,32) if x not in {10,14,15}]]
    if a.allow_a1:
        flags.remove("-ffixed-x11")
    results = []
    for mode in ("c", "cpp"):
        build = folder / mode
        build.mkdir()
        native_flags = [*flags, "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17"]
        commands = []
        def run(label, argv):
            proc = subprocess.run([str(value) for value in argv], capture_output=True, timeout=120)
            raw = proc.stdout + proc.stderr
            (build / (label + ".log")).write_bytes(raw)
            commands.append(dict(label=label, argv=[str(value) for value in argv], exit=proc.returncode, log_sha256=hashlib.sha256(raw).hexdigest()))
            return proc.returncode
        obj, ir, linked = build / "interrupt_registers.o", build / "interrupt_registers.ll", build / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        compiled = run("compile", [tools["clang"], *native_flags, "-c", folder / "interrupt_registers.c", "-o", obj]) == 0
        require(run("llvm-ir", [tools["clang"], *native_flags, "-S", "-emit-llvm", folder / "interrupt_registers.c", "-o", ir]) == 0, "diagnostic variant IR")
        facts = None
        if compiled:
            require(run("link", [tools["linker"], "--no-relax", "--no-undefined", "--entry=tsl9_rebuild_interrupt_registers_9a42", "-Ttext=0x1000", obj, "-o", linked]) == 0, "diagnostic link")
            require(run("disassembly", [tools["objdump"], "--disassemble", linked]) == 0, "diagnostic disassembly")
            elf = ELF(linked)
            facts = raw_facts(elf)
        report = dict(schema="TSL9-IRQ-return-commit-one-source-diagnostic-v1", mode=mode, native_compilation_succeeded=compiled, flags=native_flags,
                      parent_source_sha256=SOURCES, diagnostic_source_sha256={name: sha(folder / name) for name in SOURCES}, runner_sha256=sha(Path(__file__)),
                      tools={name: dict(path=str(path), sha256=sha(path)) for name,path in tools.items()}, commands=commands, LLVM_IR_sha256=sha(ir),
                      functions=facts, A1_allocation_allowed=a.allow_a1,
                      helper_A1_preservation_raw_RD_passed=compiled and all(v["A1_writes"] == 0 for name,v in facts.items() if name != ENTRY),
                      machine_semantics_proved=False, original_ABI_proved=False, target_execution=False, ISA_emulation=False, network=False, hardware=False)
        path = build / "verification.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(path), sha256=sha(path), native_compilation_succeeded=compiled,
                            helper_A1_preservation_raw_RD_passed=report["helper_A1_preservation_raw_RD_passed"],
                            functions={name:{k:v for k,v in f.items() if k != "rows"} for name,f in facts.items()} if facts else None))
    require({name: sha(source / name) for name in SOURCES} == SOURCES, "parent inputs unchanged")
    print(json.dumps(dict(results=results)))


if __name__ == "__main__":
    main()
