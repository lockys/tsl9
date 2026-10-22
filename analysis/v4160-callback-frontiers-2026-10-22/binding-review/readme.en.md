# App bindings for resident callback frontiers

[繁體中文](README.md) · [English](readme.en.md)

This static review retains nine complete original ranges, **682 bytes /248 rows**: App199E2..19B16 (308/106), read1979A..197B8 (30/13), write197BE..197F0 (50/20), timer19764..1979A (54/22), four Flash leaves (190/73), and MAC-source18F56..18F88 (50/14). Bounds are exclusive and follow actual CFG/RET evidence. The separate six-byte197B8 tail is excluded.

All raw operands are retained in ledger.json and independently compared with248 bounded radare2 rows. The sealed decoder is reused without new formats. No CPU/ISA/ESIL/MMIO/native execution, opcode generation, compiler/linker, HOST suites, network or hardware operations occur.

The actual App stores1979A at record+56 (19A76/19A7A, store19A7E atSP72),197BE at+60 (19A80/19A84, store19A88 atSP76), with record baseSP16. Record+8 is08078000−1024=**08077C00**, stored at19A52/SP24. This numeric NV address proves no physical ownership. Record+52 has no explicit overlapping store after the requested64-byte zero fill. It is zero only when the exact fill/copy profile, required SP/S0/S1 preservation and nonalias/interference premises hold.

After zeroing,18F56 writes only the six bytes at callerSP8..13; the App loop writes onlySP40..45. No physical UID value is read by this review. The original version guard must pass normally; no bypass or assumption that both public candidates pass it is introduced.

1979A freshly reads slot4004C **before allocating its16-byte frame or saving RA**. It saves RA atSP12, moves entryA2 toA4, constructs A2=`u32(entryA1<<2)`, A1=entryA0, A0=A4, then JALRs the loaded target. It restores RA, sets A0=0, pops16 and returns. Reordering frame writes or using other scratch does not prove identical fault prefixes. No original C prototype is inferred.

Under the exact candidate4004C→copied20000332 profile, the complete58-byte/18-row forward-byte-copy leaf does not write SP/RA/S/GP/TP/T/A7 or A0/A1/A2. Normal accesses to4002420C, FENCE.I, coherent copied code and return remain premises. Hence the read wrapper conditionally preserves S0 and returns A0=0, A1=entry source, A2=the shifted word count.

The first resident read uses source08077C00, word count1 and destination=tableSP+12: four bytes only. Output occupies parentSP12..15, wrapper RA parentSP−4..−1, and the caller's first saved S2 word begins atparentSP16. Valid nonzero nonwrapping frames without aliases keep these disjoint.

For this **nonzero four-byte** copy, a native pre-call A3 change is overwritten:20000346 defines A5=0, branch348 reaches354, ADD354 defines A3 before LBU358 reads it, and ADD35C constructs destination+index. A3 exits asdestination+3. Null or zero-count early paths never write A3, preserving its entry value; word count40000000 also shifts tozero. The actual caller projection is therefore conditional and **generic native full ABI remains false**.

post-read-liveness.json performs finite source CFG read/write analysis through sealed allocator/fill/free, with fixed conditional block256/tag78/count3 and valid nonwrapping heap/frame/config premises. It preserves allocator zero/nonzero return-path correlation and executes no instructions. Both candidates agree:

| Boundary | Original read-exit values that may remain live |
|---|---|
| Early table return |A1/A2/A3/A6/A7 andT0–T6|
| Next+60 callback |A7 andT0–T6|
| Allocation failure callback if+52 can be nonzero |A2/A6/A7 andT0–T6|

No own read-before-write observes these original A/T values before those boundaries, but early returns can expose them and unknown callbacks can inspect them. Lack of reads is not permission to clobber. Conditional zero+52 removes only the failure-callback frontier. The four-byte copy's A3 overwrite is a separate fact. No PSABI assumption closes T/A7, normal caller replacement or full ABI.

197BE saves a32-byte frame, RA/S0 and entryA2 as source; entryA1 is unused. It calls18E98 unlock,18EC4 erase,18EF2 fixed256-byte/64-word program,18EB6 lock and19764 withA0=1. The timer reads a scaling byte atGP+382 and accessesE000F000-family registers with an unbounded poll; Flash busy polls are also unbounded. Valid normal terminating paths restoreS0/RA/SP and returnzero without checking success. GP validity, timing units, interrupt exclusion, hardware results and OTA routing remain unknown.

The first+56 S0 preservation can now be closed under the exact-copy premises. A later allocator call through nonzero+52 still needs that callback's preservation contract. Only preserving intermediate calls allow fresh READ32(liveS0+60) to mean record+60 and resolve197BE.

The App's initially zero record+12 receives candidate default256; halfword0803 atrecord+14 supplies byte14=3. With stable fresh config, preserved index/callback state and valid nonaliased allocation, write arguments are count64 words, a fresh allocated source buffer and destinations08077C00/08077D00/08077E00, ending numerically at08077F00. This is conditional source arithmetic, not measured Flash extent, ownership or flashing authorization.

The existing `experiments/tsl9-v4160-contract-model/src/flash_contract.c:fc_write_registers` is a pinned HOST provider/semantic model of197BE and its timer sequence. It is not rerun or reimplemented here. Existing Flash-leaf native work and the new read-native review belong to other scopes; the HOST model is not a native callback ABI proof.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --candidate-root /absolute/wch-resident-candidate-2026-10-21
```

Default mode reads metadata with zero actual-source counts. Explicit FW mode requires76800 bytes/SHA0ee64183…fb667, rereads682 bytes/248 rows and rejects seven actual single-operand controls. Optional candidate mode rereads two HEX files, slot40048/4C and eight bounded ranges (984 bytes/370 rows) without filling holes. The checker is read-only; Python/sh wrappers are portable. Previously denied shell execution is not retried.
