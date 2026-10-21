# TSL9 V4.1.60: queue preparation and handoff at 0x8A56

[繁體中文](readme.zh-TW.md)

This is a partial readable C11/C++17 reconstruction of a 280-byte, 96-instruction function. The actual new native function also measures 280 bytes and 96 instructions. Original ABI admission remains false. This milestone produces only `COMPONENT-ONLY-NOT-FIRMWARE.elf`, no BIN or replacement for the existing twelve-function image.

The shared algorithm implements the unsigned 1039 entry limit, fresh connection and ROM +0x13C gate reads, 1062-byte lane stride, forward live byte copying, low-eight-bit additive checksum, and no-link ROM +0x50 tail handoff. These observations establish queue preparation/handoff, not actual GATT transmission. Failure preserves input or opaque gate residues rather than inventing a common status.

HOST uses numeric addresses and synthetic providers. Returned memory callbacks may edit memory/frame contents but must preserve registers/known masks. Named opaque gate/tail callbacks may change registers, GP, SP and frame contents. Original frame creation and fresh restore timing are modeled explicitly; they do not prove that the native compiler implements those timings. The model is a named algorithm, not a CPU interpreter.

Post-gate live S0 is not clamped again. Addressing uses the full 32-bit counter; the loop compares its low 16 bits with live S0. A separate HOST-only budget stops with UNKNOWN and retains effects already committed, without introducing native timeouts or cleanup. Raw slot/link identities and bit-zero-cleared JALR targets are separate; tail return values remain opaque.

Actual Windows HOST checks pass 4 groups, 107 cases and 15,605 assertions per language, plus eight compiled single-change semantic controls. Every HOST launch is guarded by an immutable local executable-format/architecture check that rejects RISC-V. The guard supports PE, ELF and thin Mach-O; Linux/macOS execution was not tested, and universal/fat Python is unsupported.

```sh
sh experiments/tsl9-v4160-ota-tx/verify.sh --project-root . --language both
sh experiments/tsl9-v4160-ota-tx/verify_native.sh --tool-dir /path/to/llvm/bin --language both
python -B experiments/tsl9-v4160-ota-tx/verify_host.py --project-root . --replay /path/to/verification.json
```

Set `PYTHON` to select Python. Builds use create-only directories. Native replay accepts an explicit `--firmware`; replay rejects build-only language/output/tool options and never recompiles or executes artifacts.

Native uses pinned local LLVM, RV32IMAC/Zicsr ILP32, `-Oz`, disabled outliner and C++ exceptions. Actual `-MD` closure covers three native sources and Clang resource `include/stdint.h`; sources, tools and resource header are checked before/after. Strict linking without the SRAM symbol must fail. Numeric 0x2000B18C supplies an address witness only, without SRAM/ROM implementation or board proof.

Known native gaps include frame creation before the entry guard, different save order, success stack restores after descriptor writes and ROM-tail pointer read, and different control/instruction forms. Size fit does not discharge alias, fault, interrupt or opaque-callee frame/S/SP effects. Original ABI, pointwise GPR prefix, full-image integration, physical compatibility and OTA readiness remain false. Target code is never executed or emulated.

Detailed receipts and independent reviews are under `analysis/v4160-ota-tx-2026-10-22/implementation` (research workspace: `apk-analysis/tsl9-v4160-ota-tx-2026-10-22/implementation`). Generated objects, executables and logs stay in local excluded `build/` directories.
