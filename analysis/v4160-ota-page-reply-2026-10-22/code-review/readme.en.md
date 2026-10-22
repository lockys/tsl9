# Independent C/C++ review: OTA page reply

[繁體中文](readme.zh-TW.md)

The frozen readable function is `experiments/tsl9-v4160-ota-page-reply/src/page_reply.c`, with its named synthetic HOST adapter. This bundle is separate from the immutable original124B/50-instruction source proof (`../source-review/seal.json`, SHA256 `2fe1ed8e78cbb6e054a0368c330b5d1d15f9c75bc0510769340371464b3d32f3`). It tests the C/C++ algorithm against a finite effect oracle derived from those raw-source contracts; it does not execute or interpret RV32 instructions.

## Actual independent results

C11 and C++17 each passed **3 groups, 90 cases, 6,699 assertions**, plus **10 separately compiled semantic negatives per language**. `expected-effects.c` contains an independent fixed21-effect ordering table and source-derived address, width, argument and terminal-result checks. It does not import the producer's expected outputs or canonical test fixture. Coverage comprises:

- Thirteen complete cases: ten full32-bit indexes (including65536, wrap-related and high-bit values), zero allocation with edited saved RA and opaque caller residues, combined named-callee changes to S1/S2/S0/S3/S4/SP and three synthetic frames, and an unknown TX A1 forwarded as unknown into the tail.
- Fourteen unavailable-state cases: unknown allocator result, S1 or SP; unknown data at nine distinct reads; and rejected returned-memory callbacks that mutate registers or their known mask.
- Sixty-three stopped prefixes: UNKNOWN/HALT/TRANSFER at each of21 ordered effects, checking exact prefix length and absence of a fabricated suffix.

Every positive/negative executable was inspected before and after launch by the immutable native-host guard `76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189`. This Windows run used actual PE machine0x8664 outputs. There were eleven guarded launches per language; no RV32 executable was launched. C11 used MSVC `/TC /std:c11`; C++17 used `/TP /std:c++17`, with `/W4 /WX`. The first independent fixture compile exposed a signed/unsigned assertion warning; its failed log is retained locally. The fixture assertion was corrected before the selected successful pair; no product source was changed.

The ten actual compiled controls change exactly one bounded source fragment each: narrowed source index, reversed header stores, cached copy slot base, wrong copy size, cached release slot base, stale free buffer, cached restore SP, normalized tail result, overwritten TX A1 and an unmasked odd release target. Each compiles successfully, runs only after host-machine inspection and fails an independent semantic assertion. Their count is separate from the producer's six controls and the raw proof's18 operand controls.

Selected independent receipts reside under the local `code-review/build/independent-9307d2c1418f4fef9faf85eab1441c10/{c,cpp}` archive. Their SHA256 values are `4da39eda271a8975a55af77b1f8a8386c9fa722d62a455466194cf22a4c58107` and `d66e2e6a042e98e739908a96d6a39c59ea0ab346e5818f4f1dc95f3ec617fe0c`. Both were independently reparsed without executing again. `selected-receipts.json` retains concise source/tool/result identities, not generated binaries or full archive contents.

The final producer HOST CLI is `92e3d7bf90b7255a8efee6a90c4126df802c15225586e006170aa006d779e332`. Its separate C/C++ canonical pair each passed3/87/3634 plus six compiled negatives, and both actual archives were read-only replayed here. Those results are attributed to the producer; they do not replace this independent90-case oracle.

## What the result means

The tests distinguish full32-bit index in the copy formula from low16-bit header output; low-byte store precedes high-byte store. Live S2 is reread after opaque calls for later slots. Frame reads use the live SP and can observe newly supplied saved words, including a changed/odd caller link. Raw slot/link values are distinguished from JALR's bit0-cleared targets. Free receives live S0 selected before its restore; TX A1/A2/A3 residues survive into the opaque tail. The tail provider supplies its own result; no unique common success/status value is invented.

The HOST contract permits synthetic memory/frame edits in READ/WRITE callbacks, but a returning memory callback must not mutate registers/known bits. Such mutation produces UNKNOWN with an explicit diagnostic. Arbitrary exposed register/SP/known-mask changes are permitted only at named opaque call boundaries. Providers must supply their documented result through `op_event`; direct A0 edits are not an alternative return channel. Call effects are opaque: copy data, allocator internals and TX/release implementation are not reconstructed or validated by this oracle.

`OP_RETURNED` describes the synthetic provider/model reaching its declared terminal edge. It does not prove that a physical tail returns to the original caller. A raw/restored link is reported separately; release may transfer or never return. UNKNOWN/HALT/TRANSFER prefixes establish bounded effect behavior only, not physical instruction-boundary GPR residues. Native SP/frame and callee-save preservation, ABI order passes, source placement, ROM identity, hardware and BLE update acceptance remain separate proof obligations. No native-machine execution, device access, network request or new firmware image occurred in this review.

## Portable checks and fresh tests

From the workspace root (published layouts use `analysis/v4160-ota-page-reply-2026-10-22` instead of `apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22`):

```sh
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/code-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/code-review/run-effects.py --project-root . --language both
```

Both have shell wrappers accepting the same arguments; set `PYTHON` if needed. Fresh tests require a native host C/C++ compiler supported by `scripts/portable_verify.py` and the pinned host guard. macOS guard support requires a thin matching Python executable; fat/universal inputs are rejected rather than guessed.

Default checking revalidates sealed review bytes, current five source files/oracle/guard/helper/final producer CLI, and original raw50/18controls. It is **source and selected metadata only** and emits `actual_archived_artifacts_replayed:false`; publication excludes build archives. To inspect a real independent archive, append `--receipt PATH/verification.json` (repeatable). This read-only mode checks actual artifacts, native-host executable headers, exact compile recipes/flags/output roles, logs/exits and one-change mutant source files. It neither launches a binary nor claims unavailable local archive replay. A fresh run produces new receipts in a create-only local `build/` directory.
