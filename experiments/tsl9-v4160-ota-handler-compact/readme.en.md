# Compact OTA handler C/C++ experiment

[繁體中文](readme.zh-TW.md)

Two source changes reduce native code while preserving all eight read/write argument-register bridge operands and opaque memory clobbers: separate the escaping two-byte S response object, then share the original terminal small/packet/page reply labels.

| Actual C11/C++17 build | Bytes | Instructions | Frame | Direct JAL / RELA |
|---|---:|---:|---:|---:|
| Sealed baseline | 776 | 285 | 112 | 15 / 23 |
| Disable W-loop unrolling | 776 | 285 | 112 | 15 / 23 |
| Separate response object | 592 | 196 | 48 | 15 / 23 |
| Shared reply labels (selected) | 568 | 193 | 48 | 12 / 20 |

The baseline already has one static quarter JAL and a backedge, not four unrolled copies. The ineffective pragma is absent from the final source. Final code saves 208 bytes but still exceeds the original 530-byte region by 38 bytes.

The response address originally escaped from an aggregate also containing args/state. A separate volatile two-byte C object permits scalarization of the remaining state. This preserves the private C response model, not original physical SP/frame/pointer-alias equivalence. Conventional callee S/SP preservation remains conditional; mutable HOST named state does not prove it.

Shared terminal labels retain setters and defined masks: W=63, U/R=7, packet=15. Eight-register asm read/write operands, clobbers, volatile access order and W A3/A4/A5 projection remain intact. Matching direct-call counts alone do not establish complete call ABI.

```sh
python3 -B experiments/tsl9-v4160-ota-handler-compact/verify_host.py --project-root . --language both
sh experiments/tsl9-v4160-ota-handler-compact/verify.sh --project-root . --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
```

Both CLIs accept read-only `--replay PATH/verification.json`. Fresh output uses a UUID directory; explicit `--build-root NEW` must be new and inside this model/build. Published case paths use analysis/v4160-ota-handler-compact-2026-10-22. Shell wrappers honor PYTHON, default python3.

Unchanged HOST smoke tests pass 10 cases /8292 checks and three compiled negatives per language. Every executable launch uses the sealed machine guard; actual Windows HOST was tested. Thin Mach-O Python is supported; universal/fat Python is not. Portable interfaces do not claim live Linux/macOS results.

Native output is ET_REL/IR/complete disassembly with actual MD resource-header closure and nine true UND symbols. No link, stub, numeric provider, BIN, RV32 execution or hardware OTA occurred. Complete original ABI, placement, raw8/frame/RA/alias/async conditions remain unproved. A 48-byte frame does not establish frame equivalence. Prior U/S/W/R/E limitations and BOOT write alias remain unchanged.

Hypothesis metadata retains actual W measurements; old build archives are excluded and default archive_replay is false. The original BIN is not codegen input. This component is not integrated; the existing complete image stays unchanged.
