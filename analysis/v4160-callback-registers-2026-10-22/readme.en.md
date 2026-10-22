# Callback register and live-GP reconstruction

[繁體中文](README.md)

This milestone refines the native register bridge and save order of the readable C/C++ callback originally occupying 632 bytes at `0x8614..0x888C`. Fresh C11 and C++17 builds each link a **624-byte / 223-instruction** component. No RISC-V execution, hardware operation or complete BIN generation is performed.

## Confirmed progress

- Explicitly reserving x26/x27 (S10/S11) reduces the previous 658-byte diagnostic to 656 bytes. The original direct instructions do not use them; this does not prove opaque callee preservation.
- The 656-byte component contains sixteen GP snapshots occupying 32 bytes. A narrow bridge now reads the current physical GP at six actual uses, removing entry and fifteen post-call snapshots and producing 624 bytes. ROM preservation of GP is not assumed.
- Actual native artifacts have a 48-byte frame, eleven original register/slot pairs and fifteen indirect calls, with no S10/S11 use, direct SP0 spill or GP write.
- An explicit postpass swaps only two existing two-byte stack stores to restore relative S0/RA save order. All other ELF bytes, symbols and relocation metadata are unchanged.
- Independent source and ABI reviews read the actual C/C++ pre/post artifacts, compiler recipes, header dependencies and readonly replays. HOST accessors retain the same mutable GP field; **HOST behavior suites are not rerun in this milestone**.

See the [C/C++ model](../../experiments/tsl9-v4160-callback-registers/readme.en.md), [implementation](implementation/readme.en.md), [independent source review](source-review/readme.en.md), [independent ABI review](ABI-review/readme.en.md), [live GP](gp-plan/readme.en.md), [save order](entry-plan/readme.en.md) and [original tail](tail-plan/readme.en.md).

## Compatibility still unproved

624 fitting numerically inside 632 does not admit integration. The final eight original bytes contain three executable instructions, and ownership of that tail is unresolved. The original also has another instruction before its first save; the fifteen call-return offset sets differ. A final halfword load becomes LH: the following low16 store corresponds, but the physical intermediate GPR sign prefix differs. Full entry prefix, unknown scratch registers, ROM/return ABI, placement, BOOT/interrupts and physical OTA remain open.

The existing complete experimental TX image, with thirteen readable original function regions, remains unchanged at SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` and retains the old callback carrier. **This 624-byte component is not integrated into that BIN. No rebuilt BIN is verified as flashable.**

## Reproduce the evidence

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/check.py --project-root /absolute/re-tsl9
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native
python3 -B analysis/v4160-callback-registers-2026-10-22/ABI-review/review-ordered.py --project-root /absolute/re-tsl9 --pre /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native/pre/c --folder /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native/ordered/c --receipt /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-review.json
```

The metadata checker is not a fresh compilation. The native runner requires identity-checked LLVM tools and create-only outputs. Actual source review additionally requires the local official BIN and `--receipt .../ordered/c/verification.json`; use `cpp` for C++. See each subdirectory. Windows is the measured environment; this milestone supplies no Linux/macOS or physical-device result.

Offline OTA packet preflight and update wait-reason explanations remain feature proposals, not implemented hardware functions. Closing original execution contracts takes priority.
