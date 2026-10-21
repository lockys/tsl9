# Partial TX reconstruction at 0x8A56: evidence and limits

[繁體中文](readme.zh-TW.md)

The shared C11/C++17 algorithm under `experiments/tsl9-v4160-ota-tx/src` compiles to an actual RV32 component of 280 bytes and 96 instructions. Size fit is true; original ABI, full-image integration and physical compatibility are false. The existing twelve-function image is unchanged. There is no new BIN, target execution/emulation, hardware access or network activity.

`results.json` selects four actual HOST/native receipts. `receipts/` retains byte-identical metadata only. Full objects, IR, ELF, dependency files, test executables and logs remain in excluded local `build/`. Default checking verifies sealed sources/metadata only and does not claim to read missing build archives.

```sh
python -B analysis/v4160-ota-tx-2026-10-22/implementation/check.py --project-root .
sh experiments/tsl9-v4160-ota-tx/verify.sh --project-root . --language both
sh experiments/tsl9-v4160-ota-tx/verify_native.sh --tool-dir /path/to/llvm/bin --language both
python -B analysis/v4160-ota-tx-2026-10-22/implementation/check.py --project-root . --receipt /path/to/fresh/verification.json
```

The research workspace uses `apk-analysis/tsl9-` instead of published `analysis/`. `--require-local-builds` explicitly replays the four historical local archives; `--receipt` accepts a fresh archive on another checkout. Native `--firmware` forwards a pinned validation input through replay; an alternate-location identical copy was tested. Replay rejects build-only output, language and tool-dir options.

Each language passes 4 HOST groups, 107 cases and 15,605 checks plus eight actual compiled semantic controls. The independent oracle passes 4 groups, 31 cases and 78,283 checks plus fourteen compiled controls. Coverage includes live GP/S/SP and fresh frame reads, second-gate A2/A3 residues, forward overlap feedback, narrow writes, unknown/HALT/TRANSFER prefixes, the HOST-only budget and opaque tail return. Every HOST launch requires the immutable executable guard. An actual RV32 object was refused before subprocess invocation, with zero target launches.

The native chain has six real tool commands: resource-dir query, compilation, LLVM IR, static disassembly, strict unresolved-SRAM rejection, and numeric-SRAM-witness linking. Replay checks exact recipes/order, profile/source arguments, statuses, logs, artifacts and actual `-MD` closure: three project inputs plus the actual Clang resource `include/stdint.h`. No ROM implementation is supplied. The ABS value `__tsl9v4160_data_2000b18c=0x2000B18C` witnesses an address, not SRAM storage or board compatibility.

Static subset checks cover one AX allocation, no hidden helpers/writable data, complete disassembly byte coverage, 96 decoded rows, internal CFG boundaries, two linking gate calls, no-link JR T1, paired HI20/LO12_I and actual numeric target, fifteen lexical volatile sites/widths, honest A2/A3 read-write outputs and a real musttail. Lexical IR order is not full branch-path equivalence. Five disassembly/IR controls, seven independent actual native operand mutations and two linked-ELF mutations are rejected.

Original ABI admission is deliberately false: compiler saves the frame before the guard, uses another save order, and restores success RA/S1/S2/S3/S0 too late relative to descriptor writes and ROM-tail pointer reads. Branch, sentinel, commutative and GP-tail forms also differ. Existing word-permutation scheduling policies cannot fix this inventory. The HOST original-frame contract does not prove native frame/fault/alias/interrupt behavior.

Immutable `source-review` covers the original 96 instruction fields and forty operand controls. Its sealed tuple/list public-wrapper issue is corrected separately in `source-review-v2`; old members remain unchanged. `code-review` supplies the independent HOST oracle. `ABI-review` supplies independent native subset, numeric link and explicit gaps. All evidence remains offline, synthetic or static.
