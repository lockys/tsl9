# Runtime reset / clock handoff: offline diagnostic component

[繁體中文](README.md)

Current sources are in [src/native/startup](../../src/native/startup/) and [clock_init.c](../../src/native/clock/clock_init.c). Readable C loops and minimal architectural ports reconstruct ID2966 startup. **This is not complete, validated flashable firmware.**

- Reset138B/38 instructions: entry20B plus memory/CSR handoff118B. The first16 GP/SP bytes match the original.
- Three independent GP samples, unsigned guards, forward word copy, zero writes and incoming T0 on skipped copy are retained. No C frame, spills or extra helpers.
- Actual linking preserves the `18720→1874A` clock JAL and RA=`18724`, MEPC=`9008`, and the final no-link `18730→40000` transfer.
- All128 initializer bytes match the original. RAM35160B and stack16B are explicit NOBITS allocations. C11/C++17 machine code matches; IR hashes are pinned separately because C++ GP ports carry noundef.

## Verify

Requires existing LLVM18 tools; [configure local tool variables](../../docs/local-paths.en.md). Run from the repository root using a new output directory:

```sh
python3 experiments/tsl9-runtime-reset-clock/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --build-root "$PWD/experiments/tsl9-runtime-reset-clock/build/new-run"
python3 experiments/tsl9-runtime-reset-clock/verify.py --project-root . --replay "$PWD/experiments/tsl9-runtime-reset-clock/build/new-run/c/verification.json"
```

Windows can use python / py -3 and PowerShell's `$env:TSL9_LLVM_BIN`. Tested NDK27.1.12297006/LLVM18; other platforms are untested. Each language has12 raw-operand plus4 IR negative controls. No target, HOST model, ISA or hardware execution. Current local receipts use build/component-v12.

## Open limits

The240B clock exceeds the original234B by6B and occupies original code at `[18834,1883A)`. Direct insertion into the original APP is blocked. `--require-firmware-ready` rejects this result; the tool has no BIN output operation.

An ELF without UND symbols does not close runtime dependencies: vector8038, main9008 and resident40000 are absent. The first two GP sample PCs/A0 setup order, AUIPC intermediates, timing and complete IRQ/fault effects differ or remain unproved. RAM/ROM/hardware identity and full APP placement remain unproved. Normal register composition assumes stable GP, successful original-data memory accesses, no asynchronous interference and a normally returning clock.
