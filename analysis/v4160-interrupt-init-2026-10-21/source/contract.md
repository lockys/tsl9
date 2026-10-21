# ID 2966 interrupt initialization: source contract

This file describes static instructions, not observed hardware behavior. The original is the 76800-byte ID 2966 V4.1.60 decoded image, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, mapped at `0x8000`. Register numbers in the retained decoder use the RV32 integer register file; x0 is constant zero. Addresses below are unsigned 32-bit numeric addresses, never host pointers.

## Extents and control flow

| Entry | Exclusive end | Bytes | Instructions | Direct callees |
|---|---|---:|---:|---|
| 0x9A42 | 0x9AD2 | 144 | 46 | 0x19142, 0x19124, 0x1917E twice, 0x19160 twice |
| 0x19124 | 0x19142 | 30 | 12 | none |
| 0x19142 | 0x19160 | 30 | 12 | none |
| 0x19160 | 0x1917E | 30 | 12 | none |
| 0x1917E | 0x1919C | 30 | 12 | none |

There are 264 bytes / 94 instructions. Extents end after their final `jalr x0,ra,0`; the next instructions are separate routines. Entry 0x9A42 has no local conditional branch or loop. Each RCC helper has one `beq a1,x0,entry+14`, two explicit return instructions, and no stack frame, CSR instruction, or nested call. Its nonzero path falls through to entry+2; its zero path starts at entry+14. All return targets are the live RA with bit zero cleared. This is a static control-flow fact, not a proof that an actual device reaches any return.

## 0x9A42: ordered operations

1. 0x9A42 subtracts 16 from SP. Four stores use the current SP: S2 at +0 (0x9A44), RA at +12 (0x9A46), S0 at +8 (0x9A48), S1 at +4 (0x9A4A). Every address is evaluated when its own instruction is reached.
2. 0x9A4C assigns S2=136 (`0x88`). 0x9A50 is raw `0x80093073`: `csrrc x0,0x800,s2`. It requests CSR 0x800 := old CSR AND NOT live S2. It discards the old CSR value; it does not save it for later restoration.
3. 0x9A54 assigns S1=`0x02020000`. 0x9A58 assigns A0=live S1+6; 0x9A5C assigns A1=1. JAL at 0x9A5E writes RA=0x9A62 and calls 0x19142.
4. 0x9A62 assigns S0=`0x1000`. 0x9A64 assigns A0=live S0+29; 0x9A68 assigns A1=1. JAL at 0x9A6A writes RA=0x9A6E and calls 0x19124.
5. 0x9A6E assigns A0=live S1+6; 0x9A72 assigns A1=1. JAL at 0x9A74 writes RA=0x9A78 and calls 0x1917E.
6. 0x9A78 assigns A0=live S1+6; 0x9A7C assigns A1=0. JAL at 0x9A7E writes RA=0x9A82 and calls 0x1917E.
7. 0x9A82 assigns A0=live S0+29; 0x9A86 assigns A1=1. JAL at 0x9A88 writes RA=0x9A8C and calls 0x19160.
8. 0x9A8C assigns A1=0; 0x9A8E assigns A0=live S0+29. JAL at 0x9A92 writes RA=0x9A96 and calls 0x19160. The order A1 then A0 is intentional.
9. 0x9A96 assigns A5=`0xE000E000`. Six writes follow, with values assigned between them:

| PC | Width | Address expression | Value expression | Numeric address/value absent intervening mutation |
|---|---:|---|---|---|
| 0x9A9A | 8 | live A5+1069 | x0 | 0xE000E42D / 0 |
| 0x9AA0 | 32 | live A5+260 | live A4 | 0xE000E104 / 8192, after 0x9A9E A4=8192 |
| 0x9AA8 | 8 | live A5+1060 | low8(live A4) | 0xE000E424 / 32, after 0x9AA4 A4=32 |
| 0x9AAE | 32 | live A5+260 | live A4 | 0xE000E104 / 16, after 0x9AAC A4=16 |
| 0x9AB6 | 8 | live A5+1063 | low8(live A4) | 0xE000E427 / 48, after 0x9AB2 A4=48 |
| 0x9ABE | 32 | live A5+260 | live A4 | 0xE000E104 / 128, after 0x9ABA A4=128 |

10. 0x9AC2 is raw `0x80092073`: `csrrs x0,0x800,s2`. It requests old CSR OR live S2, discarding the old value. With unmodified S2 this sets 0x88; it is not restoration of the CSR value preceding step 2. Existing other CSR bits remain dependent on intervening effects.
11. 0x9AC6 loads RA from current SP+12; 0x9AC8 loads S0 from current SP+8; 0x9ACA loads S1 from current SP+4; 0x9ACC loads S2 from current SP+0. 0x9ACE adds 16 to live SP. 0x9AD0 returns through live RA with bit zero cleared. The routine does not assign a dedicated status result to A0.

## RCC helpers

| Entry | Offset | Normally addressed register |
|---|---:|---|
| 0x19124 | 24 | 0x40021018 |
| 0x19142 | 28 | 0x4002101C |
| 0x19160 | 12 | 0x4002100C |
| 0x1917E | 16 | 0x40021010 |

For each helper, A1 is tested for zero; a negative A1 is nonzero. On the nonzero path, A4 is assigned 0x40021000, then A5 receives a fresh READ32 at live A4+offset, then A0 := live A0 OR live A5, then WRITE32 at live A4+offset with live A0, then return. On the zero path, A5 is assigned 0x40021000, then A4 receives a fresh READ32 at live A5+offset, then A0 := NOT live A0, then A0 := live A0 AND live A4, then WRITE32 at live A5+offset with live A0, then return. All arithmetic and complements are modulo 32 bits. Both paths leave their computed masked register value in A0; they do not assign a Boolean return status.

Read/modify/write is not proved atomic. Each invocation reads again, including the set-then-clear pairs. Preserve other bits from that invocation's own sampled word; do not reuse a prior invocation's sample. The static source has no nested callees or instructions modifying S0/S1/S2/SP/RA/GP in these helpers, but this is not a proof about physical asynchronous interrupts or external actors. If a synthetic backend is explicitly allowed to mutate registers at an effect boundary, the next address and operands must use those live registers. A read response writes its destination after the provider returns; no hidden reset to a cached entry state is justified.

## Evidence and limits

`retained-instructions.json` contains original little-endian bytes, an independently bit-decoded normalized instruction tuple for every row, and separate radare2 mnemonic listings. The raw decoder does not parse radare2 text and does not execute an instruction. radare2 6.2.4 SHA-256 is `cf307a66636960527e1511d00d2be6484b3b45929bf49f3d0923b24b13e17e58`; all 94 reported instruction addresses, sizes and byte strings agree. `initialization_native.c` was used only as a locator, never as source proof.

The numeric maps and CSR 0x800 are consistent with a WCH-related candidate, but these instructions do not identify a unique chip, PCB, peripheral implementation, clock behavior, interrupt ABI, boot ROM, or installed resident firmware. The labels RCC and PFIC are contextual names; only the explicit numeric accesses and dataflow above are established here. No original/rebuilt RV32 code, emulator, physical I/O, firmware update, or external request was used. OTA compatibility and flash readiness remain unproved.

An ordinary C reconstruction may preserve the ordered peripheral effects while relying on a normal C compiler ABI. Such a component is not the instruction-level register/stack implementation above and does not establish drop-in compatibility. A host MMIO/CSR test double that changes external memory or CSR state does not demonstrate machine-register mutation, interrupt entry/exit, or device behavior. If all six helpers return normally and no external machine-register mutation intervenes, A0 at the final return is the fourth helper's last clear-operation result: its own fresh sample at 0x4002100C AND the 32-bit complement of 0x101D. The entry function performs no later A0 assignment. A C return preserving that value is a dataflow reconstruction, not a recovered source-level signature.
