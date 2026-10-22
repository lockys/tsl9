# Candidate resident initialization after callback return

[繁體中文](README.md) · [English](readme.en.md)

This static review follows the sealed228-byte initializer's entry+CE call: V1.40 `43DD8→43BCA`, V1.31 `43D4C→43B3E`. Each candidate contributes **eight complete bounded bodies,1056 bytes /359 rows**, rather than another96-byte prefix. Original HEX, slot400A4 and startup copy mappings identify candidate source views, not installed firmware.

| Body | V1.40 exclusive range | V1.31 exclusive range | Bytes / rows |
|---|---|---|---:|
| Post-init |43BCA..43CDA|43B3E..43C4E|272 /87|
| Heap initialization |43190..43200|43104..43174|112 /36|
| Heap-list scan |4316C..43190|430E0..43104|36 /13|
| Fixed-word zero leaf |43326..43330|4329A..432A4|10 /3|
| Table initialization |440B6..44156|44022..440C2|160 /61|
| Allocator core RAM view |20000040..20000110|same numeric view|208 /72|
| Byte fill RAM view |2000039C..200003CA|same numeric view|46 /14|
| Free RAM view |20000110..200001E4|same numeric view|212 /73|

Every row is reachable in a CFG conditional on nested calls returning. All direct branches stay in their bodies, all direct calls reach the reviewed set, and every normal RET/backedge is retained. Heap, allocator/free and table loops are not guaranteed to terminate for unknown memory/list/callback behavior. Bounds follow actual CFG/RET evidence, not the next symbol.

`ledger.json` records all raw fields and each view-to-flash mapping. Newer startup source402F0 maps11904 bytes to20000040; historical402B0 maps11828 bytes. The historical count includes its last copied word. Explicit reference mode verifies complete pinned HEX with the existing strict checksum/segment parser; every requested range must exist without materialized holes. Actual slot400A4 values43D0A/43C7E link config bases2000323C/200031EC. Both prior initializer bodies are reread too,456 bytes total.

All718 byte partitions independently match bounded radare2 static output. A separate text parser checks all operands in646 standard rows. The72 conditional Xwchc QK rows use the pinned official TableGen source; radare2's FLD/FSD names are not treated as their semantics. No decoder extension is needed. No ESIL strings are retained or executed, and no CPU emulation, opcode generation, compiler, linker, HOST matrix, hardware or network operation is used.

For candidate config base C, post-init zeroes words C−4/C+68/C−12 and byte-fills20 bytes `[C−36,C−16)` and40 bytes `[C−80,C−40)`, then builds heap metadata. One fresh byte x at C+21 supplies `n=(3*((x>>2)+(x&3))+14)&255`, stored at state+2. Allocation gets A0=`6*n+576`, A1=1; its result is stored at C+64. Null returns straight to the epilogue. The outer initializer's normal zero return therefore does not prove allocation or feature success.

The successful allocation path rereads live S0+2 for its fill length; it must not reuse the earlier n across allocation/callback effects or aliases. Pool/table pointers are then established, the small zero leaf and table initializer are called, and code-address values43330/433B2/433B2 (historical432A4/43326/43326) are stored into dynamic table locations. Their function-pointer role is inferred from context. They are **store values, not flash write destinations**. Heap/table/config/stack disjointness still needs evidence.

The byte-fill leaf reads numeric4002420C, stores zero, contains a fence.i instruction row, performs byte stores for nonzero pointer/count, then writes back the saved value. Its normal nonzero path returns the end pointer in A0; standard C memset return ABI must not be assumed. Physical peripheral/interrupt effects are unproved.

Three precise computed-call frontiers remain:

| Frontier | V1.40 / V1.31 call PC | Source / arguments |
|---|---|---|
| Allocation failure notification candidate |RAM200000A0 /same|Fresh READ32(C+52); A0=1, A1=live A1 OR rounded16-size<<16; A2 is never written on any path reaching the call and retains ambient entry A2|
| First table callback |440EA /44056|Fresh READ32(C+56); A0 from C+8, A1=1, A2=live SP+12 writable output word|
| Loop table callback |44152 /440BE|Fresh READ32(live S0+60); equals C+60 only with prior callback/callee S0 preservation; A0/A1/A2 follow later fresh reads and indexing|

The allocator skips its callback when C+52 is zero. The table body can return early when C+8,+56 or+60 is zero; their actual values are not assumed. Its first callback can write SP+12 and has unknown register/memory effects. Subsequent live-S0/S1 addresses remain conditional. No callback is executed and no SDK field label substitutes for ABI evidence.

No reviewed body explicitly writes GP. Post-init saves/restores RA/S0/S1; the table body RA/S0/S1/S2; allocator RA/S0; heap-init RA. These source save/load relationships do not close unknown callback contracts. Normal SP/S/GP preservation needs valid frames/accesses, computed-callback return/register/stack contracts and no interference. Known post-callback frames extend64 bytes below post-init entry or80 below the slot400A4 initializer entry. This excludes the already-returned ADC callback and is not a bound on unknown callback stack usage.

Identified fixed stores do not directly write C+52, but heap metadata, allocation fill, dynamic tables, callback output and callbacks themselves remain potential writers through aliases. Preservation of the entry C+52..55 word is conditional on all such writes being disjoint, callbacks preserving it and no asynchronous interference. This proves neither zero entry value, full initialization/runtime lifetime, installed resident, full ABI, BOOT, OTA nor flashability.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --candidate-root /absolute/wch-resident-candidate-2026-10-21
```

Default mode reads metadata with zero actual-HEX/body flags. Explicit reference mode reads two complete HEX files, sixteen new bodies and two prior initializers, and rejects five actual single-operand controls per candidate: fill count20, state address, config52 displacement, config56 displacement, SP restoration. The checker writes no files and resolves both D/P project layouts, sharing the existing D references without copying or filling holes. The earlier Git Bash sandbox rejection is not retried.
