# Clock initialization: normal exit registers

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

This version preserves original normal-return A2–A5 with readable C and an empty fixed-register port. The current [src/native/clock/clock_init.c](../../src/native/clock/clock_init.c) uses the [entry-order correction](../tsl9-boot-clock-prefix/readme.en.md); this224B version and its evidence remain for comparison.

## Measured result

C11/C++17 objects and linked components contain **224B/91 instructions**, one FUNC/AX allocation, with no UND/ABS/relocations. The16B frame,22 volatile loads/20 stores, three polls and both same-value writes remain. No hardware sample or timeout was added.

Let W be the final fresh SP+12 word:

| Normal RET path | A2 | A3 | A4 | A5 |
| --- | --- | --- | --- | --- |
| W≠1 | 0x20000 | 0x40021000 | complete W | 1 |
| W=1 and subsequent polls finish normally | 0x20000 | 0x40021000 | 8 | 8 |

Skip W is not necessarily zero; that specialization needs a coherent private stack without interference. The [original/caller audit](../../analysis/boot2580-clock-exit-2026-10-22/readme.en.md) shows residues reach the resident boundary and are not proved dead. The verifier replays that evidence, then checks actual IR phis, four GPR outputs and raw/LLVM exit instructions.

## Offline verification

```sh
python3 experiments/tsl9-boot-clock-registers/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --boot-firmware "/absolute/ID-2580-V1.0.00-decoded.bin" --runtime-firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-registers/build/new-run"
python3 experiments/tsl9-boot-clock-registers/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-registers/build/component-v2/c/verification.json"
```

Actual tools were Windows Android NDK27.1.12297006/LLVM18; Windows may use py -3/python. Other platforms were not tested. Tools, source, headers and transitive original evidence are hash-bound. Component-v1 predates pin deduplication and is a historical snapshot; current replay usesv2.

This checks a conditional normal four-GPR projection. First MMIO/frame ordering, complete ABI, faults, IRQs, asynchronous behavior, ROM and physical compatibility remain unproved. VMA zero is not startup/OTA integration. No target or hardware executes.
