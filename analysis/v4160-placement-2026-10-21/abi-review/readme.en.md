# Placement and normal-boundary ABI findings

The old native IRQ initializer (118 bytes) and four helpers (22 bytes each) are **not ABI-compatible replacements**. Their previously verified memory/CSR effect sequence does not establish original register behavior. The static audit decodes actual linked ELF bytes independently for C and C++; it does not execute RV32 instructions.

| Function | Original ordinary return | Old native ordinary return |
|---|---|---|
| IRQ `0x9A42` | A2/A3 preserved; A1=0; A4=128; A5=`0xE000E000` | A2=`0xE000E000`; A3=128; A1=136; A4=`0x101D`; A5 unchanged |
| Helpers, enabled | A4=`0x40021000`, A5=fresh pre-write word; A1 exact incoming bits; A2/A3 preserved | A2=`0x40021000`, A3=fresh pre-write word; A4/A5 unchanged |
| Helpers, disabled | A4=fresh pre-write word, A5=`0x40021000`; A1 exact incoming bits; A2/A3 preserved | Same native residues as enabled path |

Both versions produce A0 from the final fresh RMW; that agreement cannot erase the other differences. Native main destinations are x10..x14, helpers x10/x12/x13. Original helper destinations are x10/x14/x15. Original main uses and reloads its 16-byte stack frame, while native leaf does not. Normal-boundary reasoning assumes unchanged saved stack words; asynchronous observation and external writes to that frame remain outside equivalence claims.

The retained caller proof shows A3 from clock query survives original IRQ, fields and `0x9F4C`, then reaches the first opaque callback at `0x131E0` before overwrite. The callback's use of A3 is unknown; no proof permits discarding it. This is a concrete preservation obligation, not an assertion that the callback accepts a fourth C argument.

The original IRQ extent is `0x9A42..0x9AD2` = **144 bytes**, not 176. The nominal shrink to 118 is 26 bytes, not 58. The ABI mismatch above makes even that 26-byte saving unavailable as proved replacement slack. The four original helpers each own 30 bytes; their nominal 8-byte differences are equally unproved slack.

## Layout and control transport

The eight bounded extents total 540 bytes: reset memory 62, query 174, fields 40, IRQ 144, four helpers 30 each. They are separated. The largest is 174; the current 196-byte register-aware query has no contiguous fit. Fields 38 fitting 40 is only a size fact. Whole-image fidelity uses the actual 126450-byte `original-image-layout.ld`: 691 explicit bindings and 691 exact size assertions. The small ROM assignment script is only a numeric address witness. Reset memory is an interior 62-byte slice of the 138-byte reset section; its prefix and CSR/clock suffix must remain explicitly owned.

For callable entries, an explicit four-byte **JAL x0** thunk preserves the caller's existing RA and all GPRs; `jal ra` would overwrite that RA. All 56 directed pairs among the eight extent starts round-trip as valid JAL x0 encodings. This establishes transport range only, not permission to overwrite an entry or destination. C.J has a narrower range and cannot replace every such transfer. A helper's first two-byte branch is followed by a four-byte instruction: a four-byte thunk covers only part of that next instruction, so whole-instruction prefix coverage (six bytes), padding and interior incoming references need explicit handling.

Reset entry `0x186BA` is a fallthrough, not a function call. Routing it to the 78-byte RET leaf would introduce a wrong continuation. The existing 80-byte fragment instead has a final four-byte JAL x0 relocation to `0x186F8`. That path must preserve incoming RA, original CSR ordering, `0x18720 -> 0x1874A` call/link `0x18724`, MEPC=`0x9008`, and the terminal jump to ROM `0x40000`. The fragment's numeric continuation witness is not an integrated implementation; ROM behavior remains unresolved.

The query's emitted main body ends with RET at offset 166, and a 28-byte cold tail starts at offset 168. Splitting it would require deliberate branch/relocation repair: existing branch into the tail and two short jumps back cannot be copied blindly. This review does not establish a valid split, a donor region, or an integrated link layout. Keep original entry addresses and explicit section bounds; do not weaken exact assertions or assume padding/ABI-dead registers.

Source-review separately owns incoming-reference evidence. Direct/relocation scans cannot prove absence of computed indirect entries. This report makes no full ABI, asynchronous IRQ, board, boot ROM, OTA or flashability claim and creates no firmware BIN. A new register-aware IRQ component must be independently tested, decoded and remeasured before any placement budget is accepted.

Evidence: `verification.json` binds original runtime SHA `0ee64183...`, source IRQ/caller proofs, full layout, actual old C/C++ ELF/IR/disassembly and receipts. `audit.py` checks 264 original bytes against retained rows, destination sets for ten emitted functions, eight source extents, 691 assertions and 56 transport encodings. No hardware or target execution is involved.
