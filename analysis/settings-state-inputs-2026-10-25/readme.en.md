# Settings and state inputs

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/settings_state_inputs.c) · [Instruction contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct14 complete functions:1,112B/353 instructions and97 private regions. They cover byte/halfword comparisons,bit-field edits,change notifications,checksum calls,one-shot flags,scheduled callbacks and one ROM indirect tail.

B1B6 consumes a GP+198 pending flag,edits the record,calls ED00 then forwards to12A08. B220 preserves modulo3 cycling and its high flag bit. All three callback references in B254/B29A bind to real reconstructed code. Scheduling selects0/1/5/10 and multiplies by60000;the time unit is unknown. B242 loads a pointer from0x40048 and tail-jumps with GP+196,0,3;only the SDK default table matches,not installed ROM identity.

234 comparisons/468 objects pass;54,878 original-coordinate bytes match,71.46% coverage. Twelve imports resolve and eight new function dependencies remain explicit,leaving98 providers without stubs. Opaque data remains unprovided.

Confirmed:bytes,widths,compare/store and call order. Inferred:settings/state handling. Unknown:vehicle feature names,time units,private ABI,physical ROM/RAM,IRQ and OTA. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness. Readonly settings-diff and scheduling traces are proposed features,not implemented App or vehicle behavior.
