# Original config field 44 → 197F0: source CFG and dependencies

[繁體中文](readme.zh-TW.md)

The source-derived body under normal call/return continuations is **364 bytes / 130 instructions**, rather than the old 112-byte prefix. It contains 13 direct JAL sites, 12 distinct App callees, and one poll loop with no encoded timeout in this body. Nested effects, normal completion, post-callback config+52, and SP/S/GP preservation remain unproved. The raw App field44 value 197F0 is confirmed; tsCB / temperature remains an inferred header label.

Official ID2966 SHA256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, analysis base8000.

| Bounded source | Bytes / instructions | SHA256 |
|---|---|---|
|197F0..1995C|364 / 130|ee7d9a35ebc31a363cc5f6efca0ce21d341099694f34aa90185be94995d826a4|
|8520..854A, restricted path|42 / 17|98688760c7a23d3f8b23f4b6cdbb0dd285fd8562ff5ba950b5fd46fee5a7ae2d|
|19124..19142, complete leaf|30 / 12|ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864|
|1908C..1909E, complete leaf|18 / 8|8a1f8aa217067a65d4a6cfa6420d03b423019f47471c699a98afc65062a01b0a|

Total: 454 bytes / 167 operand rows, plus the original 42-byte App setter. The existing IRQ source audit supplies the unchanged 19124 identity; its old control matrix is not rerun. Instruction partitioning, all calls, the sole backedge, RET1995A and next prologue1995C corroborate the range under normal callee continuations.

In the actual prior ELF, 197F0 is at offset50 within the 548-byte AX/PROGBITS owner `.text.tsl9v4160.conditional_runtime_197be`. Both entry/address symbols are GLOBAL NOTYPE, size0. **There is no original FUNC364 metadata claim.** Optional ELF validation covers these roles and the code slice, not whole-build provenance. The first observed ELF SHA256 was 6ab2e06720dc9f9ea4fa531836605fed6d3b8832a7dfa008d76bd9bd0a54f7b2; the CLI requires no particular path.

## Main contract

SP decreases by128, followed by 13 word saves: RA124, S1116, S0120, S2112 through S1176. The first call receives A0=currentSP+32, A1=0, A2=32. Main then snapshots 32-bit values from literal40021000+18/+4 and S1=40012400+4/8/2C/30/34/0C/10/14/18/1C/20/24/28/38. Some occupy S registers; others occupy currentSP+4/8/12/16/20/24.

S0 is set to40012000 before later calls. Subsequent writes use **live S0**+404/408/42C/430/434/40C/410/414/418/41C/420/424/428/438. Two further writes freshly rematerialize40021000 and access+18/+4. These values/bases cross unreviewed callees: fixed physical destinations, saved values, and restoration of real MMIO state are conditional. Private stack writes include SW32/36/40/44/48, SB52, the conversion-result SW28, and saved words.

The A0 returned by18A66 is stored at liveSP+28, freshly read intoA4 at1991E and copied toA0 at19948. Its units or physical meaning are not proved. RA is freshly loaded at19920; S restores interleave with MMIO writes, with S0 restoring late at1994E. SP+=128 and RET follow. This source shape does not prove preservation after arbitrary callee/frame changes. Main has no explicit GP/TP/A6/A7 writes; nested effects remain unknown.

Exact callsite → target pairs: 19814→8520; 1986E→19124; 19874→1908C; 1987A→188E2; 19896→1892E; 1989E→18986; 198A6→18A98; 198AC→18A6E; 198B8→189AE; 198C0→18996; 198CA→18A8E; 198DC→18A66; 198E6→188E2. Their selected source assignments are listed in the Traditional Chinese document; these are not complete physical signatures or SDK prototypes.

198C4 copiesS1 intoA5. Each poll passesA5 asA0 withA1=2. After18A8E returns, 198CE/198D2 freshly setA5=40012400; 198D6 branches back to198C6 ifA0==0. No counter or timeout is encoded here. Main's only JALR is RET. The direct targets are App addresses, rather than identified resident providers.

## Three small dependencies only

The carrier's8520 FUNC is168 bytes, but **only its42-byte restricted path is proved**. Given 16-byte entry-SP alignment, a valid nonwrapping32-byte destination at liveSP+32, A1=0/A2=32, normal accesses and no adverse alias or asynchronous change, the size/alignment/value branches stay on this path. Four SW offsets0/4/8/12 with stride16 run twice, coverSP+32..63, then RET8548. No nested call or SP/S/GP write occurs on this path. A0 retains the destination, A2=0, A3/A4=end, A5=0, T1=15. This is closed-form guard/stride reasoning, not CPU-state execution. Other paths, including a computed JR, remain unproved.

The complete30-byte19124 leaf performs fresh32-bit RMW at40021018: OR entryA0 for nonzeroA1, otherwise AND ~entryA0; this caller setsA1=1. The complete18-byte1908C leaf performs RMW at40021004 using `old & FFFF3FFF | entryA0`. Neither has nested calls or S/SP/GP/RA writes. The next unreviewed dependency is1987A→188E2. No wider peripheral chain or post-callback zero value is claimed.

## Replay and limits

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware ID2966.bin
python3 -B check.py --project-root ROOT --firmware ID2966.bin --image-elf EXISTING_SOURCE_ELF
```

Default metadata mode has both actual-read flags false. Explicit firmware rereads454 bytes /167 rows plus the App's42 bytes, and rejects four actual single-field byte controls: initial count32, fourth fill-word offset, poll backedge, and frame pop128. Optional ELF validation is only an enclosing role/slice check. Both `apk-analysis/tsl9-*` and delivered `analysis/*` layouts work. Existing IRQ source evidence is required; archived builds are unnecessary for firmware-only verification.

No opcode generation, native provider, compiler/HOST sample, RV32/CPU/ISA/ESIL execution or emulation, hardware, network, or UID transmission occurs. Installed identity, full ABI, all transitive effects, post-callback config contents, and OTA compatibility remain unknown.
