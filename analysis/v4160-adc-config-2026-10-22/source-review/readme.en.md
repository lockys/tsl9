# Original ADC configuration and bounded callback closure

[繁體中文](README.md) · [English](readme.en.md)

This read-only source review covers 386 new bytes / 148 rows of original ID2966 V4.1.60, rereads the previous 364-byte callback and 106-byte 188E2/19160 dependency, and optionally checks existing source ELF subsets. No firmware, CPU/ISA/ESIL, HOST or hardware/MMIO execution, compiler, linker, BIN generation or network operation is used.

`ledger.json` retains complete raw bytes and operands. The sealed decoder is extended only for encountered standard32 ORI/SLL/AND/SLTU operand fields. Three pinned official `riscv-opcodes` excerpts in the parent case provide their encoding fields; existing MUL decoding is reused. Excerpt hashes are not whole-file hashes or immutable commits. An independent parser checks all 148 rows against retained bounded radare2 disassembly text. ESIL strings are neither retained nor used; no opcode encoder is introduced.

| Entry | Exclusive bound | Bytes / rows | CFG boundary |
|---|---|---:|---|
| 1892E | 18986 | 88 / 37 | Straight line to RET18984 |
| 18986 | 18996 | 16 / 7 | Two branches join store1898E, RET18990 |
| 18996 | 189AE | 24 / 10 | Two branches join store189A0, RET189A2 |
| 189AE | 18A66 | 184 / 64 | Channel branches then three sequence paths; RET189FC/18A44/18A64 |
| 18A66 | 18A6E | 8 / 4 | READ32, two shifts, RET18A6C |
| 18A6E | 18A8E | 32 / 12 | Two branches join store18A80, RET18A82 |
| 18A8E | 18A98 | 10 / 4 | READ32, AND, nonzero conversion, RET18A96 |
| 18A98 | 18AB0 | 24 / 10 | Two branches join store18AA2, RET18AA4 |

Every retained row is reachable from its entry. All branch destinations are internal, all indirect jumps are normal RA returns, there are no linked calls or cycles. Backward joins are not loops. Bounds follow actual CFG/RET evidence, not the next symbol or an original FUNC-size assumption. Optional ELF checks cover these eight source subsets only; no whole-ELF provenance or installed identity follows.

The exact 14-effect order in 1892E, with B=entry A0 and C=entry A1, is:

1. READ32(B+4), READ32(C+24), READ32(C+0), READ32(C+28), READ32(C+4), WRITE32(B+4).
2. READ32(B+8), READ32(C+12), READ32(C+16), READ32(C+8), WRITE32(B+8).
3. READ32(B+44), READ8(C+20), WRITE32(B+44).

Every read is fresh at its source position. The uint32 write values are `(old4 & E0F0FEFF) | C24 | C0 | C28 | (C4 << 8)`, `(old8 & FFF1F7FD) | C12 | C16 | (C8 << 1)`, and `(old44 & FF0FFFFF) | (((U8(C20)-1) & FF) << 20)`. Config words have no additional field masks, so their high bits must not be discarded. Byte20 is decremented, masked to FF, then shifted20; zero becomes FF before shifting. This is not merely a four-bit count. Aliased B/C may let earlier writes change subsequent fresh config reads; preserve the actual ordering.

The actual caller at19896 supplies A0=40012400 and A1=current callback SP+32. Under the previous restricted32-byte zero-fill premises, config words0/4/8/16 are zero, word12=E0000, byte20=1, words24/28 remain zero. This follows actual stores and the earlier bounded zero path, not an inferred C structure/offsetof. Its three writes reduce to `old4 & E0F0FEFF`, `(old8 & FFF1F7FD) | E0000`, and `old44 & FF0FFFFF`.

Other helper effects are:18986 sets/clears bit0 at B+8;18996 sets/clears00500000 at B+8;18A98 sets/clears04000000 at B+4;18A6E uses fixed40012408 and sets/clears00800000;18A8E returns `(READ32(B)&A1)!=0`;18A66 performs a **32-bit** fresh read at B+76 then extracts low16. The actual189AE caller resets channel16/sequence1/sample7, selecting a B+12 read/modify/write with shift18, followed by a B+52 low-five-bit update to16. All alternative raw branches remain available with their CFGs; arbitrary invalid argument hardware behavior is not established.

All13 direct callback calls now have bounded source contracts: the previous restricted8520 path, two RCC leaves,188E2/19160 and these eight leaves. These leaves never write RA/SP/S0–S11/GP/TP. A valid aligned nonwrapping144-byte stack interval (128-byte outer frame plus16-byte deepest nested frame), normal accesses, no adverse stack/code/MMIO/config-word52 aliases, and no asynchronous register/stack/code/config modifications allow the **normal return path** to restore entry SP/RA/S/GP/TP. Poll198C6..198D6 has no encoded timeout; finite return additionally requires some status read to observe mask2 nonzero.

This is not complete register or MMIO restoration. A6 is freshly written at189BE from4001240C before its channel edit, with no later overwrite. RCC4002100C mask200 is cleared by both reset-like calls and is never snapshotted/restored; only RCC+4/+18 are snapshotted/restored. Original A7 is neither read nor written anywhere in the callback or its bounded dependencies, so normal exit retains entry A7.

For possible additional A2/A6/A7 clobbers in a new native1892E candidate, the source gives a narrow caller result. Between1989A and198B2, including18986/18A98/18A6E, none is read.198B2 overwrites A2 with1 before use189DA. The actual channel16 path overwrites A6 at189BE before reading it at189CC. Early A2/A6 clobbers are therefore overwritten for this caller when asynchronous register observers are excluded. A7 is never subsequently overwritten; a new clobber escapes to the original callback exit. This is source evidence, not a PSABI assumption, complete ABI proof or promotion of a102-byte candidate.

The original A3/A4/A5 scratch exits have bounded later overwrites too. A5 is freshly loaded at18986 before use1898A. A4 is not read by18986; actual A1=1 selects LUI18A9C before use18AA0. A3 is not read by18986/18A98; actual A0=1 selects LUI18A7A before use18A7E, and caller198B0 later resets A3=7. A0/A1 are reset at1989C/1989A. Thus output-value differences in A0 through A6 at the1892E return are overwritten before use for this particular normal caller path with no asynchronous register observers. This does not permit different internal accesses or write values in the callee.

The T bank remains an escaping constraint. T0/T2/T3/T4/T5/T6 are neither read nor written anywhere in the complete bounded source and retain entry values at normal exit. T1 is written15 only at8520 and read for the early comparison8524, then never read or overwritten; its normal exit is15. Fixing A7 in a future native candidate is insufficient if allocation introduces a new T0 or other T clobber. All escaping registers still need explicit checks.

Config word52 can only be conditionally preserved across this one callback: its complete word must be disjoint from the144-byte stack interval and fixed MMIO write set, with no interference. This does not establish its entry value, initialization/runtime lifetime, or installed resident. Existing official WCH register declarations can corroborate ADC/temperature semantic candidates, not the physical chip. BOOT, BLE OTA, flashability and physical effects remain unproved.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --image-elf /absolute/ADDRESS-WITNESS-ONLY.elf
```

Default mode reads metadata only; actual FW/ELF flags remain false. Explicit FW mode requires76800 bytes and SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, rereads source rows and rejects six actual single-operand byte controls: mask, config-byte offset, byte decrement, shift20, channel branch target, and nonzero comparison source. ELF-without-FW and wrong-FW modes are rejected. The old94-case matrix is not rerun. These are static source results, not physical execution evidence.
