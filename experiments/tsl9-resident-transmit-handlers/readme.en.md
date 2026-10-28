# Transmit callers, buffer handoff and guarded recycling

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_transmit_handlers.c)

Three whole candidate SDK bodies add **3,576 CODE bytes / 1,173 instructions**. C11/C++17 preserve original instructions, control relocations and whole CFGs. No new DATA, fake providers or target execution.

|Original range (exclusive end)|Static evidence|
|---|---|
|5774E..5784A, 252B / 78 instructions|Drain separate queue heads280 and288, guard buffer release, refresh the head, restore the tag high byte and advance next; also release frame buffer, optional slots and controller record|
|59042..595B8, 1,398B / 442 instructions|Three real far calls toRAM20000AC6 preserve the incoming record inA0; state1 selects queue buffer, other states select record frame buffer|
|595B8..59D3E, 1,926B / 653 instructions|Preserve numeric status/helper/head/prepared/marker gates, release, counters and head update; normal exit restores the frame and tails to567BE, without an invented return|

Real calls **59212, 59284, 59594 → 20000AC6** establish the original static binding. Header writes590BA/590C4 or591A2/591AA use record offsets12 and21. At590D4 the selected buffer pointer is written atword112 of the context loaded throughglobal2000353C. This explains the first-whole no-copy path. **Physical MMIO/DMA/radio meaning of this handoff remains unproved.**

The head+280 update at5983C is dominated by: status byte2000351A bit0 clear, helper560B2 returning0, nonnull head, nonzero prepared state and a clear marker low bit. The path writes `uint16(tag | 0xff00)` at59822, then passes the **current node.buffer** to20000110 at59828. It freshly reads head.next after release, increments the halfword atrecord+68 and conditionally decrements the word atrecord+420. These numeric/dataflow facts do **not prove a physical ACK or CRC success**. Split marker81→01 retains bit0; whole marker0 is eligible only under the other gates.

Drain5774E does not explicitly clear either tail. Optional slots39/38/40/41 are released only when not255. Custom release semantics and current-buffer lifetime remain unproved; do not substitute an assumed standard free.

Of54 normal imports,12 resolve to actual prior bodies and **42 remain genuine UND**. Two own indirect sites599F6/59BEC also remain open. Identical C/C++ partial links contain **48,720 CODE+412 DATA bytes / 16,883 instructions**,3,595 positive FUNCs and2,913 relocations. Parent bytes/globals/relocation roles remain, with no duplicate original CODE. Readonly/RAM/MMIO/callback and physical event binding remain incomplete.

Formal APP provenance stays **162 files / 73,478 of76,800B (95.67% static byte coverage)**, not functional completion. This candidate is not curated into formal src, linked into APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or proved physical ROM/RAM/IRQ/Flash/OTA compatibility.** No target, HOST model, ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM, read-only replay:

```sh
python3 experiments/tsl9-resident-transmit-handlers/verify-v1.py --tool-dir "$LLVM_BIN"
```
