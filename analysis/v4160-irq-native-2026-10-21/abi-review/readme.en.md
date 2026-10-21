# Independent native IRQ normal-boundary review

Both actual C and C++ component ELFs contain four helpers of 30 bytes and a 180-byte initializer. **All 120 helper bytes match the original runtime exactly** at `0x19124`, `0x19142`, `0x19160`, `0x1917E`. Each helper's relative conditional branch, both RETs, load/store offsets and register choices are identical. The original runtime SHA is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

The complete 300 executable bytes per mode are covered without gaps or overlaps by exactly five function symbols: 113 decoded instructions, no extra outlined function, UND, relocation or writable allocation. The actual profile is `-Oz`, RV32IMAC_Zicsr, ILP32, with machine outliner disabled and only A0/A1/A4/A5 allocatable. This review reuses emitted artifacts; it does not compile or execute target instructions.

| Boundary | Statically established contract |
|---|---|
| Helper enabled | A0=before OR mask; A1 exact incoming bits; A4=`0x40021000`; A5=fresh before |
| Helper disabled | A0=before AND NOT mask; A1=0; A4=fresh before; A5=`0x40021000` |
| Helper preservation | Actual destinations only A0/A4/A5; A1 and every other GPR, including A2/A3/SP/RA, untouched |
| Main normal return | A0=last fresh READ32(`0x4002100C`) AND `0xFFFFEFE2`; A1=0; A4=128; A5=`0xE000E000` |
| Main preservation | Actual destinations only A0/A1/A4/A5; no encoded write to A2/A3/SP/RA or other GPR; no calls or frame |

The main's fixed admitted native transcript has 20 ordered effects: CSR800 clear88, six fresh 32-bit read/modify/write pairs, six trailing stores (three byte and three word), CSR800 set88. `verification.json` lists each native site, raw instruction, address, width and expression. In the candidate mapping, the final A0 fresh load is `0x10E2`, NOT is `0x10E4`, AND is `0x10E8`, store is `0x10EA`. No later instruction writes A0. Final A4=128 at `0x1120`, A5 base at `0x1124`, A1=0 at `0x1128`, then RET at `0x112A`. These offsets are independently bound to raw bytes, not inferred from source intent alone.

The source callback obligation remains relevant: query A3 survives the original IRQ/fields/`0x9F4C` path until the first opaque callback at `0x131E0`; callback consumption is unknown. This new main's absence of A3 writes satisfies that local preservation obligation at a normal return. It does not establish a callback signature or callback behavior.

## Limits and rejection of placement

This is not pointwise equivalence to original IRQ execution. Main temporarily repurposes A1 as `0xE000E000` address scratch at native `0x10EE`; the original uses a stack frame, calls helpers and reloads saved values, while this main is a leaf. CSR timing, transient registers, stack traffic, instruction addresses, interrupt delivery and asynchronous memory changes have not been proved equivalent. Helper byte identity also does not prove hardware interrupt/board behavior or arbitrary relocation compatibility.

Original main occupies 144 bytes at `0x9A42..0x9AD2`; the native main is 180 bytes, **36 bytes too large**. Exact 30-byte helpers provide no spare bytes. This review does not link at original addresses, select a donor area, produce a BIN, or accept placement, boot ROM, OTA or flashability. Separate compiler-review may provide a numeric layout witness; an out-of-image diagnostic address is not a storage-suitability proof.

Eleven actual in-memory mutated transcripts are rejected: helper identity change, A2 write, SP write, wrong return register, nonzero final A1, wrong final A4/A5, wrong CSR set mask, wrong final fresh-load offset, late A0 overwrite and tail write width. These are **static transcript controls**, not compiled mutant source tests, ISA execution or a general equivalence proof. The checker admits this exact bounded main transcript and fails unfamiliar encodings rather than emulating them. It uses retained ELF parsing and destination decoding with pinned hashes.

`verification.json` retains every admitted function byte/row, symbol address, profile and all source/ELF/IR/log hashes. A fresh replay requires those pinned local inputs; the retained ledger can still be inspected separately. No parent/model/old sealed scope is edited. No network, hardware, target execution or new firmware BIN occurs.
