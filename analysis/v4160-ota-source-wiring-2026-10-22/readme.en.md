# Complete experimental image with the original OTA caller wired to real C/C++

[繁體中文](README.md)

The goal remains rebuilt firmware compatible with the original hardware and BLE OTA. This round wires the actual caller and produces a complete experimental BIN. **It is not validated as flashable and must not be used as a hardware test image.**

## Confirmed offline results

- A TU includes the existing readable OTA handler and defines a genuine compiler strong FUNC568 alias. No numeric address substitutes for a function, fabricated size or new opcode template is used.
- Only the original NOTYPE global entry is weakened in a copy of the retained provider object. All691 original allocations remain. Nine new-handler references bind real providers, while the original ROM entry remains truly undefined in the partial object.
- New C occupies `0x1AC00..0x1AE38`. The actual caller JAL at `0x14094`, raw `ef60d036`, reaches `0x1AC00`, returning to `0x14098`. The original raw530 handler remains unchanged; its original address does not become readable C through a symbol name.
- C11/C++17 produce the same77,824-byte BIN, SHA-256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`. Only three bytes in the caller instruction change in the inherited76,800 bytes. Appended568-byte executable C and456-byte explicitly non-executable FF page data do not substitute padding for missing code.
- The image still contains extensive original carriers. Wiring this handler does not recover the whole original source.

## Numerical ROM witness versus a real provider

Original ID2966 has JAL raw `6f70120d` at `0x18730`, `rd=0`, numerical target `0x40000`. Its reset section starts at `0x186AA`, with a type17/addend0 relocation at offset134 to the true ROM undefined symbol. The complete ELF reuses that historical numerical boundary as ABS/NOTYPE/size0. **This supports static address witnessing, without supplying ROM code or identifying the installed ROM.** Strict linking without that boundary must fail; missing definitions cannot be ignored or replaced by a stub. [Source fields](original-ROM-boundary.json)

## The narrowed ABI boundary

In two official candidates, slot `+0x70` points to RAM `0x20000236`. Actual reads cover each86-byte/35-instruction wrapper and110-byte/37-instruction core prefix, plus the original90-byte App caller. Ambient A2 survives into a fresh unknown callback loaded from RAM `0x20003270` inV1.40 or `0x20003220` inV1.31. This is neither whole-allocator analysis nor installed-ROM identification. **It does not prove that new reply SP+6/7 is interchangeable with original SP+12.** [Evidence, eight operand controls and stop boundary](allocator-review/readme.en.md)

## Reproducible contents

| Scope | Evidence |
|---|---|
| Readable handler and real same-TU alias | [Model](../../experiments/tsl9-v4160-ota-source-wiring/readme.en.md) |
| Actual compilation, partial/final links and BIN | [Implementation](implementation/readme.en.md) |
| Independent ELF/symbol/relocation/full-byte review | [ABI review](ABI-review/readme.en.md) |
| Candidate allocator A2 boundary | [Allocator review](allocator-review/readme.en.md) |
| Delivered experimental image | [BIN guide](../../artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/readme.en.md) |
| Remaining conditions | [Plan](plan.en.md) |

Only local static reads, compilation, linking and extraction occur. No RV32/CPU execution, emulation, BLE/UART/CAN, Flash access or vendor API is used. The unchanged HOST algorithm suites are not rerun merely for this wiring change. Metadata-only defaults are distinct from explicitly supplied actual artifact checks, which delivery receipts record separately.

## Still incomplete and a feature candidate

Physical chip/board, installed ROM/BOOT, Flash/NV ownership, RAM, IRQ and complete S/SP/RA/GP contracts, asynchronous observation, OTA format/acceptance/failure recovery remain unproved. A BOOT numerical page bound that includes the extra page does not establish ownership or compatibility.

A worthwhile proposed feature is an **offline pre-update inspection** displaying BIN identity/length/section differences and unresolved ROM/board/recovery conditions. This remains a proposal, not an implemented hardware function or permission to flash. Next work should resolve the fresh allocator callback or original caller preservation/reply-pointer contract, prioritizing actual safety gaps in the new C.
