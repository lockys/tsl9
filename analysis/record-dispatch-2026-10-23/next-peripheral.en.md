# Next:18CA4 register transfer operation

[繁體中文](next-peripheral.md) · [72 original instructions](next-peripheral.json) · [Bounded contract](next-peripheral-contract.json)

The bounded `[18CA4,18D78)` span contains212B/72 instructions and three reachable cold blocks after its sole RET. All direct targets remain inside it. The next18D78 entry is already backed by separate source evidence and is excluded here. This span has not yet been reconstructed in C; a register layout does not establish physical hardware identity.

| Original range | Confirmed operation | Boundary |
| --- | --- | --- |
| 18CA4..18CC4 | Three fresh `[A0+8]` reads test bits26/27/28; select0/1/2 or return4 | Do not collapse to one snapshot; asynchronous hardware behavior unknown |
| 18CC6..18CEA | Selector×16; shifted ID and input bytes8/9 update selected+384 | Preserve standard/alternate paths, fresh RMW order and overwritten A0 |
| 18CF0..18D0A | Mask input byte10 with15 and write it back; separate register+388 reads/writes | Add no length≤8 guard; record is mutable |
| 18D0E..18D56 | Read bytes12,11,13,14,16,15,17,18; write+392/+396; final+384 OR1 | Preserve read order, alternate-only A6 writes and every RMW |

The12A50 caller supplies base40006400. A three-bank register transmission operation is a candidate interpretation. Peripheral identity, physical delivery and seat/DND attribution remain unproved. A possible offline diagnostic could show selector, original/masked length and all eight bytes read, while separating those facts from observed hardware transmission.
