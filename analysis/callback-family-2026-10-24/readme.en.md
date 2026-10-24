# Callback-table and cancellation path

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/callback_table.c) covers original `901A–9124`: **266B, 102 instructions, 20 architectural regions**. Actual C11/C++17 objects match all 244 non-control bytes and eight typed branches after data-only original-VA encoding. [Standalone evidence](evidence/standalone-trial.json)

## Static observations

- `9070` is a shared loop back to `9026`, not an independent function. Frame entries are `901A`, `907A` and `90B0`.
- AUIPC expressions at `9034/908C/90B2` encode the same original address `2000BE08`; stride is12B and the scan bound15.
- `901A` selects a slot from event bits, loads callback/payload, and clears words +4/+8 before the A3 indirect call when the flag byte iszero. Original frames, shared restores and then-live S1 arithmetic are retained.
- `907A` passes zero/180B arguments through slot40048, passes original901A toslot40080, and stores lowA0 toGP+166.
- `90B0` finds the first matching callback, optionally passes its nonzero payload through slot40068, clears +4/+8, and tails through slot4005C withGP166 and a16-bit event mask. The no-match path returnsA0=1.

## Inference and limits

The layout corresponds to default WCH SDK memset/task-registration/message-deallocation/stop-task table macros. A15-slot callback/event table with initialization and cancellation is therefore inferred. Table slots are not function entries; actual installed pointers, ROM identity and callee ABI remain unknown. [SDK correspondence](rom-profile-correspondence.json)

The real17C38 reference now binds90B0's22B entry, with all266B linked. The genuine diagnostic component contains **2616B code +456B data,244 nonzero FUNC regions,9 entry aliases,225 RELA and17 direct UND**. All2350B parent code,456B parent data and62 nonzero vector bindings remain intact. [Native evidence](evidence/native-c.json) / [Pending providers](pending-providers.json)

The selected sources now contain87 C/H files:120 code-source comparisons/240 objects plus2 independent pointer-data comparisons/4 objects, totaling **122/244**. Source-projection and original-byte checks do not establish whole-firmware behavior. VMA-zero ET_REL is not original placement or a BIN; AUIPC placement, startup/IRQ, hardware/memory/ROM and BLE OTA compatibility remain unproved.

The next direct target is1798A with a1787C call. [Retained bounded decode](next-1798a-frontier.json) records and excludes a final truncated4B row with only2 available bytes. A later frame is not claimed as part of that function. A future read-only callback-queue diagnostic could expose occupancy, pending masks and cancellation state; it is not implemented and requires memory ownership, stable-snapshot and installed-ABI evidence.

No target/HOST-model execution, ISA emulation, hardware access, BIN generation, commit or push occurred. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
