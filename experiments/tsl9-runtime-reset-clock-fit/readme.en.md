# Reset and 232-byte clock: offline composition

[繁體中文](README.md)

This experiment compiles the current `src/native/startup/` and `src/native/clock/clock_init.c` as C11/C++17, then links diagnostic ELFs. It neither executes the target nor generates a firmware BIN.

- Reset138B/38 instructions + clock232B/93 instructions =370B/131 instructions. The original call `0x18720 -> 0x1874A` retains RA=`0x18724`.
- The genuine12B clock entry falls through to its220B C body. There are no added jumps, aliases, ABS providers or unresolved relocations. The fixed linker placement and verifier are mandatory; the body is not an ordinary standalone C ABI entry.
- Each language checks6 actual ELFs, complete IR/source/tool/MD-include evidence,16 reset negative controls and18 clock negative controls.
- The initializer is128B; RAM35160B and stack16B are real NOBITS allocations, without proving physical ownership.

## Run

From the repository root, set `PROJECT_ROOT` to that directory and `LLVM_BIN` to the existing tool directory:

```sh
python3 experiments/tsl9-runtime-reset-clock-fit/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-runtime-reset-clock-fit/build/my-run
python3 experiments/tsl9-runtime-reset-clock-fit/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-runtime-reset-clock-fit/build/my-run/c/verification.json
```

On Windows use `py -3` and PowerShell variables `$env:PROJECT_ROOT`/`$env:LLVM_BIN`. Only the recorded local NDK LLVM hashes are accepted; no dependencies are downloaded. The build directory must be new. Explicit `--clock-source origin` selects the experimental source; the default checks the curated source for byte equality.

Actual local receipts are `build/curated-v1/{c,cpp}/verification.json`. New receipt source fields are relative; existing local original receipts are preserved. Public evidence and the curated-source comparison summary are in the [analysis directory](../../analysis/runtime-reset-clock-fit-2026-10-23/summary.json). The older runtime-reset-clock reader/receipts remain frozen; their clock pin does not apply to this checkout.

## Unresolved

New RET at`0x18830` replaces an original cold SW. The original cold J at`0x18832..0x18834` is not free space. Avoiding the next function does not prove indirect/BOOT/resident/IRQ entry compatibility. Vector`0x8038`, main`0x9008`, resident`0x40000`, full APP, asynchronous/fault behavior and physical chip/ROM/OTA compatibility remain unresolved.

`firmware_ready=false`; replay with `--require-firmware-ready` must refuse. No flashable BIN, RV32/MMIO execution or emulation, hardware action or network operation is performed.
