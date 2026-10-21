"""One bounded -Oz reset-memory profile; compile/static checks only, no RV32 execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
DEPENDENCY = Path("apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review")
PINS = {"verify_native.py": "6d5d0e43a1a909e8dbaa6a63027c0db7fc14b295c934b979b3d3169bdd38d456", "elf32.py": "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"}
SOURCE_PINS = {"reset_memory.c": "123bef3ebb0cfef1e39e942052302bc0d8cea66c7e4a6ab62d6752b9adf2d4f6", "reset_memory.h": "04d81c8f927fa00a217eea3dc54b6e8c47a709bd8ddcc9bc87dae6da8d725d32"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path, required=True)
    p.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    p.add_argument("--fragment", action="store_true")
    args = p.parse_args()
    root = args.project_root.resolve()
    dependency = root / DEPENDENCY
    for name, pin in PINS.items():
        if sha(dependency / name) != pin:
            raise ValueError("immutable static verifier dependency changed: " + name)
    spec = importlib.util.spec_from_file_location("pinned_reset_native", dependency / "verify_native.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    model = root / "experiments/tsl9-v4160-reset-memory/src"
    source, header = model / "reset_memory.c", model / "reset_memory.h"
    v.require({name: sha(model / name) for name in SOURCE_PINS} == SOURCE_PINS, "frozen reset source pins")
    tools = {key: v.tool(None, args.tool_dir, name) for key, name in (("clang", "clang"), ("linker", "ld.lld"), ("objdump", "llvm-objdump"))}
    tool_pins = {key: sha(path) for key, path in tools.items()}
    results = []
    for mode in (("c", "cpp") if args.language == "both" else (args.language,)):
        folder = HERE / "build" / ("oz-" + uuid.uuid4().hex + ("-fragment-" if args.fragment else "-leaf-") + mode)
        folder.mkdir(parents=True)
        flags = ["--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-Oz", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17", *["-ffixed-x" + str(i) for i in range(1, 32) if i not in {5, 10, 11, 12}]]
        if args.fragment:
            flags.append("-DTSL9_RESET_MEMORY_FRAGMENT=1")
        obj, ir = folder / "reset_memory.o", folder / "reset_memory.ll"
        commands = []
        for label, argv in (("compile", [tools["clang"], *flags, "-c", source, "-o", obj]), ("llvm-ir", [tools["clang"], *flags, "-S", "-emit-llvm", source, "-o", ir])):
            record, _ = v.run(argv, folder, label)
            commands.append(record)
        object_result, ir_result = v.elf_gate(obj, args.fragment), v.ir_gate(ir)
        strict = None
        if args.fragment:
            strict, error = v.run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + v.ENTRY, "-Ttext=0x1000", obj, "-o", folder / "STRICT-MISSING-CONTINUATION.elf"], folder, "strict-link", False)
            v.require(strict["exit"] != 0 and "undefined symbol: " + v.CONTINUATION in error, "strict missing-continuation rejection")
            commands.append(strict)
        linked = folder / ("ADDRESS-WITNESS-ONLY.elf" if args.fragment else "COMPONENT-ONLY-NOT-FIRMWARE.elf")
        numeric = ["--defsym=" + v.CONTINUATION + "=0x186f8"] if args.fragment else []
        record, _ = v.run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + v.ENTRY, "-Ttext=0x1000", *numeric, obj, "-o", linked], folder, "link")
        commands.append(record)
        record, disassembly = v.run([tools["objdump"], "--disassemble", linked], folder, "disassembly")
        commands.append(record)
        machine = v.machine_gate(disassembly, linked, args.fragment)
        report = dict(schema="TSL9-reset-memory-bounded-Oz-static-probe-v1", passed=True, mode=mode, fragment=args.fragment,
                      flags=flags, source_sha256=SOURCE_PINS, runner_sha256=sha(Path(__file__)), immutable_dependencies=PINS,
                      tools={key: dict(path=str(path), sha256=tool_pins[key]) for key, path in tools.items()}, commands=commands,
                      object=object_result, LLVM_IR=ir_result, LLVM_IR_sha256=sha(ir), linked_component=v.elf_gate(linked, args.fragment, True), machine=machine,
                      transcript_controls=v.transcript_controls(disassembly, linked, args.fragment),
                      actual_compiled_controls=v.compiled_controls(source, header, flags, folder, tools, args.fragment),
                      original_slot_check=dict(passed=machine["helper_bytes"] <= 62, original_start=0x186ba, original_end_exclusive=0x186f8, candidate_end_exclusive=0x186ba + machine["helper_bytes"]),
                      strict_missing_continuation_rejected=strict is not None, continuation_body_supplied=False,
                      original_fallthrough_ABI_proved=False, original_fixed_placement_proved=False, full_native_loop_semantics_proved=False,
                      firmware_executed=False, ISA_emulation=False, network=False, hardware=False, OTA_ready=False)
        v.require({name: sha(model / name) for name in SOURCE_PINS} == SOURCE_PINS, "source unchanged after bounded profile")
        v.require({key: sha(path) for key, path in tools.items()} == tool_pins, "tool pins unchanged")
        receipt = folder / "verification.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, fragment=args.fragment, receipt=str(receipt), sha256=sha(receipt), helper_bytes=machine["helper_bytes"], instructions=machine["instruction_rows"], physical_GP_operand_reads=machine["physical_GP_operand_reads"], IR_GP_observation_sites=ir_result["GP_observation_sites"], loop_SCCs=len(machine["loop_components"])))
    print(json.dumps(dict(passed=True, results=results)))


if __name__ == "__main__":
    main()
