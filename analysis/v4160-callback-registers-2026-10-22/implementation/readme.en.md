# Callback native-register implementation evidence

[繁體中文](readme.zh-TW.md)

The formal producer is `verify_native.py`, also available through the model's `verify.py / verify.sh`. It freshly compiles the three sources with the frozen profile plus only x26/x27 reservations, explicitly invokes new `postpass/frame.py`, then uses the standard linker at a scratch address. **C11 and C++17 each produce 624 bytes / 223 instructions. Full ABI and original 632-byte placement remain unadmitted.**

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/pinned/llvm/bin --language both
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root . --replay /absolute/path/to/ordered/c/verification.json
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/check.py --project-root .
```

The development prefix is `apk-analysis/tsl9-`; published checkouts use `analysis/`. Both resolve. Windows can use `python -B`; POSIX wrappers accept `PYTHON`. Pinned tools are the actually tested Windows NDK LLVM binaries; other-platform compiler identities/runs are not claimed.

The default creates a UUID build. Optional `--build-root NEW` must be a nonexistent child of this model/build; overwrites fail. Outputs:

- `pre/{c,cpp}/probe.json`: five raw compiler/resource/IR/link/disassembly commands plus raw object/ELF.
- `ordered/{c,cpp}/frame-order.json`: only the two existing 2-byte C.SWSP words are exchanged; every other ELF byte is preserved.
- `ordered/{c,cpp}/verification.json`: formal source/resource/tool/IR/machine/order/artifact readback.
- stdout JSON: `passed` and two `results`, each with receipt/hash, native_bytes=624, instructions=223 and explicit false admission flags. The selected index maps mode to each receipt.

Eight tool stages comprise seven LLVM commands and one explicit Python ordering command; the outer Python generator launch has separate argv/exit/log/hash provenance. MD covers exactly three project files and one actually observed Clang resource `include/stdint.h`, not a broad header inventory.

`results.json` and `receipts/*.json` retain byte-identical selected formal metadata with original local absolute labels. Published source excludes object/ELF/IR/log archives. Default `check.py` checks sealed source, the exact transformation and selected metadata: **actual_native_artifacts_read=false**. `--receipt NEW_VERIFICATION` explicitly reads actual local outputs; `--require-local-builds` requires the original W archives and fails if unavailable. A fresh checkout should first create its own receipts through the producer.

`probe.py` (656B), first-GP diagnostics and build intermediates are historical exploration. `probe_gp.py` is also the fixed raw-generation substage; standalone success does not establish ordering or formal verification. `machine.py` is a producer field/coverage gate. Independent `ABI-review` raw/frame/ordered gates and `source-review` retain separate conclusions/seals.

The frozen source3 has identical HOST expansion; unchanged HOST suites were not rerun. Actual output has no x26/x27 operand, GP write, SP+0 spill, hidden helper or UND; it has six live GP operands, fifteen opaque calls, a48B frame and eleven save/restore pairs. The new pass repairs relative stack-save order only. Original SLLI-before-store prefix, opaque RAs/frontiers and complete physical GPR residues remain unproved. Eight original tail bytes lack ownership; no padding, BIN or whole-image update is provided. Board, resident preservation and physical BLE/OTA remain unverified.
