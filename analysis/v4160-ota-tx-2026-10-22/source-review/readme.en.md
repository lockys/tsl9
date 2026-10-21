# Original8A56 transport construction: raw source contract

[繁體中文](readme.zh-TW.md)

This source-only review covers official ID2966 V4.1.60 `0x8A56..0x8B6E`: **280 bytes,96 instructions**. `raw.py` decodes individual RV32I/M/C instruction fields as data and compares every operand/order to96 explicit tuples. It has no CPU state, instruction interpreter, ESIL or execution interface. All40 targeted raw operand controls are rejected by the decoder/contract, independently of the whole-image digest. `contracts.json` gives the full ordered source contract with PCs; `source-proof.json` retains the measured result.

The original payload digest is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; this280-byte interval is `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`. File offsets are VA minus0x8000. Compact retained LLVM rows cross-check all instruction boundaries/raw bytes; their mnemonics are not input to the independent decoder. The retained source is a full-section disassembly, avoiding symbol-limited truncation at the next private label.

## Inputs, eligibility and opaque boundaries

The source uses full32-bit A0=context, A1=command, A2=numeric payload address and A3=unsigned length. `8A56/5A` rejects length>1039 **before** changing SP or memory: A0 stays entryA0 and A5 becomes1039. A0 is not a universal boolean/status return.

The admitted path saves S0/S1/S2/S3/RA in a32-byte frame and captures the input length/address/context/command. It reads unsigned16-bit values at liveGP+0x96 and later liveGP+0x9A, compares them with full32-bit context, and excludes0xFFFE. The first candidate uses the entry context; the second uses live S2, which an earlier opaque callee could have changed.

At `8A8E` and `8AB4`, the routine calls independently loaded32-bit slot targets at0x4013C, setting A1=liveGP+0x80. Only returnedA0==1 selects a buffer lane. These are **opaque compare-to-one gates**, not proven allocator, permission or BLE API identities. For the second gate, A2/A3 retain entry values if the first was not called, otherwise its residues. `8AB8` then forces A2=1 even if the second gate fails. First success instead sets A2=0 at8ACC.

All GP/S/SP dependencies remain live. There is no second post-gate length check. A callee preserving these registers may be a declared native-profile condition; this source review does not prove that resident behavior. Any unknown/nonreturning gate or memory operation has no fabricated suffix.

## Ordered memory layout and additive checksum

For selected lane0/1, define `B=u32(0x2000B18C+1062*lane)`, `P=u32(B+6)` and N=post-gate live S0 before its later+6/restore. The base is a static AUIPC/ADDI address-pair fact, backed by the RAM symbol relocation. The stride instructions are MUL, not REMU. The literal uses LUI/XORI to produce full32-bit0x00007F55; replacing XORI with ADDI could leave the same stored low16 bits but a different instruction/register contract.

| PC | Ordered effect |
| --- | --- |
|8AEC|WRITE16(P,0x7F55), little-endian bytes55 7F|
|8AF0|WRITE8(P+4,low8(N))|
|8AFA|WRITE8(P+3,low8(N>>8))|
|8B00|WRITE8(P+2,low8(live command))|
|8B56/62|For each byte: fresh unsigned READ8(source+counter), then WRITE8(P+5+counter,byte)|
|8B16|WRITE8(P+5+N,checksum)|
|8B32/36|WRITE16(B+2,low16(N+6)), then WRITE16(B+4,0)|

The checksum is addition modulo256 of command, length low/high components and each freshly read payload byte; magic is excluded. It is **not a polynomial CRC**. This describes local memory bytes, not captured wire traffic. B+0..1 are not initialized locally. The final zero is SH16 atB+4, not SW32; it does not overwrite magic atB+6.

The loop compares `low16(full32 counter)` with full32 N, while source/destination addresses use the full counter. It reads each source byte before its write, allowing forward overlap feedback; a whole-buffer snapshot or generic memcpy assumption would strengthen the source contract. If stable N<=65535 and accesses complete, it terminates after N bytes. The entry guard guarantees<=1039 only before opaque calls; N>65535 after a callee lacks an ordinary terminating guard value. A HOST budget may report an explicit bounded/unknown prefix, but cannot invent a native guard, clamp or successful return.

## Return, tail and register details

The failure block8ABE..8ACA freshly restores RA/S0/S1/S2/S3 and SP. A0 is entry context when no opaque gate ran, the first result if its fallback lane is ineligible, or the second result when it fails. Caller-saved residues also depend on the path; after gate2, A2=1 even on failure.

Success freshly restores RA/S1/S2/S3 **before** the final metadata writes. It sets A1=1, computes A2=currentGP+0x94+4*lane, freshly restores S0 at8B40, reads the32-bit tail target at0x40050, loads unsigned A0 from byte0 atA2, increments live SP and executes **JR T1 without linking** at8B50. It does not read a16-bit handle atGP+0x9A here. A3 is0x2000B18C, A4 is the checksum, A5 is0x40000; A6 is P+N−1 after a nonempty copy, otherwise an opaque residue. A7 is locally untouched, not proven preserved across callees. A future tail return/result belongs to the opaque target.

Frame data is reread rather than cached. Earlier payload/metadata writes or opaque calls could alias later saved words. The original restore/store interleaving must not be replaced by an ordinary C ABI preservation assumption. This routine has no direct allocator/copy/release calls; unknown callee internals could still perform such work.

## Symbols, references and replay

The original AX/PROGBITS owner is align2, FUNC280 `__tsl9v4160_call_8a56`. It has11 owned relocations: ten internal targets (including PCREL low) and one external RAM PCREL high. Nine recorded incoming references all target offset0, including the reconstructed page-reply JAL at9BE0. Independent raw decoding gives **eight linked calls and one no-link tail**; relocation names alone do not determine rd/link semantics. No external recorded interior reference appears here. Computed, encoded or resident references remain unknown.

Selected evidence includes actual original and current twelve-function carrier role/body readbacks. Default replay uses the pinned manifest, all relevant raw carrier directives and original bytes; it does not require those archived objects. Optional `--object` reparses a real carrier's relevant symbols/relocations/body and reports the actual count separately.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

Published layouts use `analysis/v4160-ota-tx-2026-10-22`; the shell wrapper accepts the same arguments (`PYTHON` override supported). Add repeatable `--object ORIGINAL.o`/`--object CURRENT.o` only when real archives exist. Default output explicitly reports zero actual carrier replays, while retaining the two historical selected readbacks. No generated object is a publication member. C/C++ behavior, native extent fit, physical fault/interrupt prefixes, resident ABI, hardware/BLE and OTA compatibility require separate evidence and are not admitted by this seal.
