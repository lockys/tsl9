# State controls and record transfer

[繁體中文](README.md) · [English](readme.en.md)

Ten whole functions add 1,266B / 452 instructions. Seven previous imports are now genuine code; no new external provider was introduced. This is a static reconstruction milestone; **no firmware BIN was generated or hardware accessed**.

| Evidence | Result |
| --- | --- |
| Native C11 / C++17 | Same standalone object, 89 code regions, 59 RELA, 12 imports all provided by the parent |
| Curated sources | 126 C/H files; 198 function comparisons plus 2 independent data comparisons = 200 comparisons / 400 objects |
| Integrated component | 34,956B code + 1,750B data; 12,238 instructions; 2,954 FUNC, 71 zero-size aliases, 2,316 RELA; 161 true imports |
| Original coordinates | All 36,706 selected bytes match the official BIN; 2,967 owners in 101 adjacent-only spans |
| Static transfer positions | 2,076 direct transfers; 738 call-return positions; zero ordinary continuation gaps |
| Saved SDK candidate layout | Two independent 48B readonly metadata objects; zero FUNC, relocation or import; not linked into firmware |

Confirmed instruction behavior:

- `960E` stores the allocation result before the null test, builds seven halfwords and submits the record. The argument 3 is not proved to be byte capacity.
- `AC0A` keeps full-width inputs, reloads bit8 after the command call and conditionally schedules `AB02`; that callback issues command13 without a new gate check.
- `D2EE/D332` retain low-byte store followed by whole-halfword reload, transition commands102/103 and both calls to `13D48`.
- `10C7A` constructs a two-byte payload and descriptor; allocation, copy, submission and conditional free retain the original register tuples.
- `10D60/10E82/10EB2` preserve cleanup order, pointer reloads, three43-byte records, 12-byte nodes, bytewise progress and all post-return alternatives.
- `167A6` scans 127 pairs and two35-entry tables. All matches and table pointer reloads remain present.

Candidate inference: the saved WCH header maps the default slots to `GATT_bm_alloc`, `GATT_WriteCharValue`, `GATT_bm_free` and TMOS functions. Its `tmos_memcmp` returns TRUE for equal bytes. Native `attWriteReq_t` size12/alignment4/offsets0,2,4,8,9 agree with the observed stack writes. These are **candidate header/profile correspondences**; installed ROM identity and the private caller ABI remain unproved. The write slot is not `GATT_Notification`.

Unknown: physical MCU/board components, ROM contents, RAM ownership/capacity, asynchronous ABI/IRQ behavior, time units and product labels, startup/Flash/OTA compatibility. The diagnostic ELF has entry0 and no PT_LOAD. The opaque default and seventeen pool data targets remain unprovided. The full authentication body remains private/unresolved. No host model, ISA emulator or target was executed.

[Raw instruction evidence](evidence.json) · [Semantic contracts](provider-contracts.json) · [Measured summary](summary.json) · [Remaining providers](next-providers.json) · [Feature candidates](feature-candidates.json)

[Selected source](../../src/native/receive/state_controls.c) · [Native recipe](../../experiments/tsl9-state-controls/spec-v1.json) · [Source proof](../../experiments/tsl9-state-controls/verify-source-v1.py) · [Integration recipe](../../experiments/tsl9-state-controls/integration-v1.json) · [Layout recipe](../../experiments/tsl9-original-layout/spec-v29.json) · [Static flow verifier](../../experiments/tsl9-original-layout/verify-flow-v32.py) · [SDK data-only layout proof](../../experiments/tsl9-state-controls/sdk-write-layout-v1.json)

From the repository root, using the existing pinned local toolchain and retained artifacts:

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v32.py --replay experiments/tsl9-original-layout/build/state-controls-flow-v1
python3 -B experiments/tsl9-state-controls/verify-sdk-write-layout-v1.py --tool-dir "$LLVM_BIN" --sdk-header "$SDK_HEADER" --replay experiments/tsl9-state-controls/build/sdk-write-v1
```

`LLVM_BIN` and `SDK_HEADER` are user-provided local paths. Build receipts and the saved SDK header stay local; the public recipes pin their identities. These commands validate static artifacts and never flash hardware.
