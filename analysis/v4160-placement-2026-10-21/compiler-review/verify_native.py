"""Reproduce the frozen IRQ register allocator blocker and separately inspect IR."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
from ir_checks import gate, require, ENTRY, HELPERS, transcript_controls

HERE = Path(__file__).resolve().parent
SOURCE_PINS = {"interrupt_registers.c": "d3000829bd171e12d7fd6fe9ba5532c76635dce730d64628b3044d06b3724321", "interrupt_registers.h": "da57cec48aa144786cd9a64c8d20aadd2bb02d9e91d43408eac6441f7ba3ae59", "irq_io.h": "2ced66889c82da11b595b9dab734c8af4fdd4bb365390a534ec3611f0d5398f7"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(mode):
    return ["--target=riscv32-unknown-elf", "-march=rv32imac_zicsr", "-mabi=ilp32", "-Oz", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-relax", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", *["-ffixed-x" + str(reg) for reg in range(1,32) if reg not in {10,14,15}], "-x", "c" if mode == "c" else "c++", "-std=c11" if mode == "c" else "-std=c++17"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path, required=True)
    p.add_argument("--clang", type=Path)
    p.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    a = p.parse_args()
    root = a.project_root.resolve()
    source_root = root / "experiments/tsl9-v4160-interrupt-registers/src"
    require({name: sha(source_root / name) for name in SOURCE_PINS} == SOURCE_PINS, "frozen three-source pins")
    clang = (a.clang or a.tool_dir / ("clang.exe" if os.name == "nt" else "clang")).resolve()
    clang_pin = sha(clang)
    results = []
    for mode in (("c", "cpp") if a.language == "both" else (a.language,)):
        folder = HERE / "build" / ("blocked-" + uuid.uuid4().hex + "-" + mode)
        folder.mkdir(parents=True)
        obj, ir = folder / "interrupt_registers.o", folder / "interrupt_registers.ll"
        commands = []
        def run(label, argv):
            proc = subprocess.run([str(value) for value in argv], capture_output=True, timeout=120)
            raw = proc.stdout + proc.stderr
            (folder / (label + ".log")).write_bytes(raw)
            commands.append(dict(label=label, argv=[str(value) for value in argv], exit=proc.returncode, log_sha256=hashlib.sha256(raw).hexdigest()))
            return proc.returncode, raw.decode("utf-8", errors="replace")
        native_flags = flags(mode)
        compiled_exit, error = run("compile", [clang, *native_flags, "-c", source_root / "interrupt_registers.c", "-o", obj])
        diagnostic = "Stack pointer required, but has been reserved."
        require(compiled_exit != 0 and error.count(diagnostic) == 5 and all(name in error for name in [ENTRY, *HELPERS]) and not obj.exists(), "exact five-function reserved-stack native blocker without object emission")
        ir_exit, _ = run("llvm-ir", [clang, *native_flags, "-S", "-emit-llvm", source_root / "interrupt_registers.c", "-o", ir])
        require(ir_exit == 0, "same-profile optimized IR is available")
        ir_result = gate(ir)
        report = dict(schema="TSL9-IRQ-register-frozen-profile-blocker-v1", mode=mode,
                      expected_native_blocker_reproduced=True, native_compilation_succeeded=False, native_verification_passed=False,
                      blocker=diagnostic, affected_functions=[ENTRY, *HELPERS], object_emitted=False, linked_ELF_emitted=False,
                      flags=native_flags, allowed_allocator_registers=[10,14,15], A1_reserved_except_explicit_commitment=True,
                      source_sha256=SOURCE_PINS, runner_sha256=sha(Path(__file__)), IR_checker_sha256=sha(HERE / "ir_checks.py"),
                      clang=dict(path=str(clang), sha256=clang_pin), commands=commands,
                      LLVM_IR_sha256=sha(ir), IR_only_checks=ir_result, IR_transcript_controls=transcript_controls(ir),
                      actual_native_function_sizes=None, actual_native_RD_preservation_proved=False,
                      original_ABI_proved=False, original_fixed_placement_proved=False, firmware_executed=False,
                      ISA_emulation=False, network=False, hardware=False, OTA_ready=False)
        require({name: sha(source_root / name) for name in SOURCE_PINS} == SOURCE_PINS and sha(clang) == clang_pin, "source and compiler pins unchanged")
        receipt = folder / "verification.json"
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(receipt), sha256=sha(receipt), expected_native_blocker_reproduced=True, native_verification_passed=False, IR_only_checks_passed=True))
    print(json.dumps(dict(expected_blocker_reproduced=True, native_verification_passed=False, results=results)))


if __name__ == "__main__":
    main()
