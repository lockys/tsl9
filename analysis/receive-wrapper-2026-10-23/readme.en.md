# Receive entry16B0A reconstruction

[繁體中文](README.md) · [C/C++ and verification](../../experiments/tsl9-receive-wrapper/readme.en.md) · [Downstream contracts](downstream-contracts.json)

**Confirmed:** the70B/26-instruction receiver has adjacent14B entry/56B body; all54B outside four call/tail windows equal the official code. It retains the16B frame, A0 bit0 test before S0 storage, then-live S0/S1 after calls, fresh saved-slot reads and original tail order.

Explicit S0/S1 architectural ports prevent LLVM from adding a callee-save frame. The mask0x02 test/branch is an assembly port, not claimed as pure C. Other conditions, arguments and call flow are reconstructed in C.

An actual132B ET_REL section contains the62B consumer and70B receiver. Two caller relocations reference a genuine receiver FUNC definition; four downstream relocations reference three UND providers. All relocations remain. This proves linkage structure, **not resolved executable code or flashable firmware**.

**New finding:** `16A7C→12BC8→[4004C]` reaches an unknown resident provider and known code also uses A6/A7/T1/T3. Compiler clobber lists do not establish its complete ABI. SPI timeout returns0, indistinguishable from a valid zero byte; separate diagnostic counters could help but are unimplemented pending RAM/IRQ proof.

Formal receipts use portable paths with originals retained locally. The public curation receipt is a path-anonymized derivative bound to the raw original SHA. Physical chip identity, complete resident/IRQ/main and OTA compatibility remain unproved. No RV32/MMIO execution or hardware operation occurred.
