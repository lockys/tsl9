# Original NV write and timer source contracts

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

This bounded review covers six closed source CFGs in original ID2966 V4.1.60 firmware for checking a separate C/C++ implementation. No original instruction, CPU/ISA/ESIL, native/HOST code, MMIO or hardware was executed. No BIN or network activity was produced. This is not a whole-firmware or flashable-compatibility proof.

Original SHA-256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, 76800 bytes, VA base `0x8000`, file offset `VA-0x8000`, without filling holes.

|Source|Half-open range|Bytes|Rows|
|---|---|---:|---:|
|Write wrapper|197BE..197F0|50|20|
|Timer|19764..1979A|54|22|
|Unlock|18E98..18EB6|30|10|
|Lock|18EB6..18EC4|14|6|
|Erase|18EC4..18EF2|46|19|
|Program|18EF2..18F56|100|38|
|Total||294|115|

`ledger.json` retains every original byte, PC and decoded field. `r2-static.json` independently corroborates these original ranges with static r2 operands; ESIL was neither retained nor executed. Call continuations are conditional on normal return. All five direct dependencies are leaves. RETs, backedges and explicit GPR writes come from actual CFGs rather than blindly using the next symbol as a function boundary.

## Write wrapper

Entry A0 is destination D; entry A2 is source S. Entry A1 is never read before being overwritten, so it is not a variable length. 197BE reserves the complete 32-byte frame. 197C0/197C2/197C4 store RA/S0/entry A2 as words at F+28/F+24/F+12, where F=u32(entrySP-32). The remaining frame bytes have no explicit wrapper stores. S0 holds D.

The five linked calls are ordered:

1. 197C8→18E98 unlock, A0=D.
2. 197CE→18EC4 erase, A0=D; the leaf aligns to `D & 0xFFFFFF00`.
3. 197D8→18EF2 program, A0=D, A1=fresh 197D2 R32(F+12), A2=that same read. The leaf sets A2=256 before using it.
4. 197DC→18EB6 lock, A0=aligned D, A1=source, A2=256, without resetting those registers.
5. 197E2→19764 timer, A0=1, A1=source, A2=256.

197E6/197E8 restore RA/S0 from fresh frame reads. 197EA sets A0=0; 197EC releases the complete frame. Returning zero does not establish hardware success: no success status is checked.

Under normal completing accesses and polls, with no adverse frame/source/destination/MMIO alias or intervening modification, final A1=S, A2=fresh GP+382 byte, A3=0, A4=last fresh timer CTRL with bit0 cleared, A5=E000F000, A6=last source word. SP/RA/S0 restore their entry values. Other S/GP/TP/T/A7 have no explicit writes in these bodies. Without the alias premises, restoration only restores the fresh saved-location values, not necessarily entry values.

## Timer's 12 minimum accesses

`effects.json` supplies ordered PCs, widths, formulas and normal leaf register outputs. Every R8/R32 is fresh; every W32 writes a complete word.

1. 19768: R32(E000F004).
2. 1976E: W32(E000F004, prior read & FFFFFFFE).
3. 19770: zero-extended R8(u32(GP+382)).
4. 19778: W32(E000F010, u32(byte × full entry A0)).
5. 1977A: W32(E000F014, 0), not the high product word.
6. 1977C: fresh R32(E000F000).
7. 19782: W32(E000F000, that read | 10).
8. 19784: another fresh R32(E000F000), without reusing the previous value.
9. 1978A: W32(E000F000, that read | 21).
10. 1978C: repeated fresh R32(E000F004); 19790 branches back while bit0 is zero, exiting when bit0 is observed set.
11. 19792: another fresh R32(E000F000).
12. 19796: W32(E000F000, that read & FFFFFFFE).

Addresses and masks above are hexadecimal. Access count is `11 + poll reads`, at least 12 on normal return. Multiplication uses the full 32-bit A0 and keeps the low 32 bits. A0 is neither byte-truncated nor converted to boolean. Timer does not write A0/A1; its normal outputs are A2=low product word, A3=0, A4=last CTRL & FFFFFFFE, A5=E000F000. It has no frame, calls or other GPR writes.

This exit condition differs from Flash polls that wait for bits to clear. There is no timeout or termination proof. Timer does not initialize GP+382, and the source establishes no milliseconds or physical time unit. MMIO may change between fresh reads; stability is not assumed.

## Four Flash leaves

Unlock writes 45670123 then CDEF89AB to 40022004, then the same ordered values to 40022024. Lock freshly reads 40022010, ORs 8000, and writes it back.

Erase freshly reads CTRL and ORs 20000, writes the aligned destination at base+20, then freshly reads CTRL and ORs 40. It polls base+12 until bit0 clears, then freshly reads CTRL and ANDs FFFDFFFF. Program freshly reads CTRL and ORs 10000; it waits for base+12 bit0 then bit1 to clear. For offsets 0,4,...,252 it interleaves a fresh source word read, destination word write, and bit1-clear polling. It finally freshly reads CTRL and ORs 200000, waits for bit0 to clear, then freshly reads CTRL and ANDs FFFEFFFF. Program does not prebuffer the source. A0 remains the aligned base, A1 remains the source, and A2 ends at 256.

These numeric contracts come from actual operands, not SDK prototypes or assumed board identity. `effects.json` lists all four leaves' complete output GPRs and access ordering. None of their busy polls has a timeout or checked success result.

## Replay and limits

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware /absolute/ID-2966-V4.1.60-decoded.bin
./check.sh --project-root ROOT --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

On Windows, invoke check.py with the installed Python. Default mode only checks sealed metadata and reports zero actual original bytes/rows read. Explicit `--firmware` rechecks the file SHA, 294 bytes/115 rows and seven raw operand controls: saved-frame offset, direct call target, GP byte offset, MUL source, zero high-word store source, poll direction, and fixed program length. Controls flip an actual original bit and require only the intended decoded field to change. They generate no new opcode and execute no modified content.

`mode-controls.json` records mode and wrong-source checks. `dependency-availability.json` records successful existing dependency closure checks in W/D/P before sealing. The checker is read-only; post-seal replay preserves member hashes. check.sh was not retried through the previously denied Git Bash environment; the Python entry point was verified.

The immutable `callback-frontiers-2026-10-22/binding-review` seal is `a1d0dc4d3e8767e8dbd959235133779650f1da649c2d3f8ddbb38662addea9a7`; its pinned decoder, encoding references and prerequisite evidence are reused without modification. `seal.json` pins all new members. Installed hardware identity, Flash ownership, write success, whole OTA, fault equivalence and a new native full ABI remain unproved by this static source review.
