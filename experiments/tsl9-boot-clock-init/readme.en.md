# BOOT/Runtime clock initialization in C/C++

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Ordinary readable C reconstructs the original clock initialization. Curated source: [src/native/clock/clock_init.c](../../src/native/clock/clock_init.c). The only ASM is an empty frame-storage port: no instruction carrier, ASM algorithm or fake provider.

## Measured result

- Both C11/C++17 objects and linked components contain **214B/88 instructions**, one genuine FUNC/AX allocation, with no UND/ABS/relocations.
- The original BOOT/Runtime234B/93-instruction bodies are byte-identical; see the [source audit](../../analysis/boot2580-clock-2026-10-22/readme.en.md). New C machine code is not original-byte equal.
- Artifacts check own writes to SP/A2–A5, the16B frame and SP+8/+12. IR retains22 loads/20 stores, all three polls, fresh count/ready/postloop samples and both same-value writes. Original43 memory sites become42 because the ready0/1 branches share one store; no path transaction is omitted.

## Usage

From the project root, supply existing LLVM, both original images and a new build directory:

```sh
python3 experiments/tsl9-boot-clock-init/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --boot-firmware "/absolute/ID-2580-V1.0.00-decoded.bin" --runtime-firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-init/build/new-run"
python3 experiments/tsl9-boot-clock-init/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-init/build/component-v1/c/verification.json"
```

Windows may use `py -3` or `python`. Actual tools were Windows Android NDK27.1.12297006/LLVM18. Source/tool/header hashes and actual compiler dependencies are checked; other platforms were not tested. Complete SSA/CFG hashing guards this fixed profile rather than proving independent ISA semantics.

## Limits

Original first MMIO read precedes SP decrement; candidate frame comes first. Exit A2–A5 residues, faults, IRQs, asynchronous effects and complete ABI remain unproved. The final two polls keep their original lack of software timeout; normal return is not a physical readiness guarantee.

VMA zero is an offline link layout. This component is not integrated into startup or an OTA BIN and proves neither installed resident identity, physical frequency nor flashability. No target/MMIO execution, HOST tests or hardware operation occurred.
