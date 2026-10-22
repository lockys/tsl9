# Callback native call frontiers

[繁體中文](README.md)

This independent review reads the unchanged 624-byte C/C++ callback components. Fifteen sites are identified by the actual pointer-load source, distinguishing argument definitions, predecessor call families and an independent LLVM SSA check. Address ranking is never a pairing rule. All 223 native instruction fields also agree with the LLVM disassembly; the original source ledger contains 217 instructions over 632 bytes.

`selected.json` records the measured C/C++ results and pins, rather than shipping compiled archives. A successful metadata check does not mean an actual native archive was opened. No source change, compilation, HOST rerun, target execution, ISA emulation or new BIN is performed by this bundle.

## Findings

- Original `8800 LHU A5` and native `120A LH A0` have only a low-16-bit `SH` use before explicit register replacement. Their sign-extension difference is dead at the matched `descriptor_send` calls (`8812` / component `1220`). This closes that particular call-boundary discrepancy, with no interrupt/fault-prefix equivalence claim.
- At that call, physical A3/A4 retain the matched earlier gate's opaque outputs in both streams. The LLVM SSA operands independently forward the same two gate outputs. No missing A4 assignment was found at this frontier.
- Physical S-register roles differ. For example, original S2 is `40000` at receive, whereas the native component retains entry S2; original pending-gate S7 is nominally `40000`, whereas native S7 is an unsigned halfword queue value. Native S4 there is a scratch mask. These are observations and conditional obligations for unknown resident code that observes implicit inputs, not automatic functional failures under a separately established resident ABI.
- Matching slot identities assumes conventional callee-saved preservation only for the nominal signature. Every call's A0..A7, S registers, GP and SP definitions are separately retained under an `opaque-all` policy. Actual target loads using live S registers remain explicitly different from compiler constant-base loads.
- Matched return offsets differ. A different literal RA alone does not establish incompatibility; no installed-ROM RA contract is proved here. Candidate resident-body analysis belongs to its own evidence scope.

Three focused counterexamples reject a changed actual D4 pointer-load operand, an actual A3 replacement before descriptor-send, and an SSA A4 substitution. A positive reversal of stored row order preserves all fifteen site identities. These are static checks, not instruction execution or firmware fuzzing.

## Run

Metadata only, with no generated archives required:

```sh
python3 -B native-review/check.py --project-root ROOT
```

Actual read-only component review (write the new receipt outside the old component folder):

```sh
python3 -B native-review/review.py --project-root ROOT --folder ROOT/experiments/tsl9-v4160-callback-registers/build/RUN/ordered/c --receipt ROOT/analysis/v4160-callback-call-frontiers-2026-10-22/build/native-c.json
python3 -B native-review/review.py --project-root ROOT --replay RECEIPT.json
```

The IR defaults to sibling `RUN/pre/c/callback.ll`; `--ir-folder PRE_MODE` selects it explicitly. Add `--firmware FW` to also read and verify the pinned official original bytes; use the same mode during replay. Without that option, the pinned original instruction ledger is checked and `original_firmware_read` remains false. `review.sh` and `verify.sh` accept the same arguments; `PYTHON` selects a local Python executable. Paths above are examples relative to the case directory; use the actual script location in your checkout. Both original `apk-analysis/tsl9-...` and published `analysis/...` evidence layouts are supported.

Actual success emits `actual_native_artifacts_read=true` and `actual_call_frontiers_checked=true`. Metadata-only success emits both false. The checker reads actual ELF/object/disassembly/IR bytes directly, independently of the producer's `passed` field. Replaying a receipt requires the same archived artifacts and firmware-read mode.

Full prefix equivalence, complete 632-byte ownership (including the remaining eight executable bytes), original ABI admission, image placement, installed ROM, interrupts, hardware and OTA compatibility remain unproved. The existing component is not promoted to an integrated firmware by this review.
