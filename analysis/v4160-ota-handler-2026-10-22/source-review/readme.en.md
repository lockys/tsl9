# Original-source contract for the OTA command body

[繁體中文](readme.zh-TW.md)

This is official ID2966/V4.1.60 `0x9C4A..0x9E5C`: 530 bytes, 169 original instructions, SHA256 `693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5`. Firmware base is `0x8000`, complete image SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Independent raw operand decoding is checked field by field against actual static LLVM disassembly. Nothing executes or simulates RV32.

`contracts.json` records the original obligations; `instructions.json` retains all 169 rows. Prior HOST-model conventional ABI assumptions, copied memory views and provider replies are not original hardware evidence. `source-reconciliation.json` records independent inspection and identities of the final four frozen C/H files. This is neither HOST execution nor native compilation proof, nor a claim to have recovered the complete original high-level source.

Entry uses A0=context, A1=full32 command, A2=payload, A3=full32 length. A6/A7 have no explicit body writes. The48-byte frame saves S0,S2,RA,S1,S3,S4,S5 at offsets40,32,44,36,28,24,20 in that order. The common epilogue freshly reads RA/S0..S5 using current liveSP, adds48, then JR RA. Unknown callee changes to SP/frame prevent unconditional entry-SP or initial-RA restoration claims.

| Command | Source obligation |
|---|---|
| W | Check fresh active at liveGP+0xA9, full length1026, BE16 page and unsigned address bound in order. Destination is0x08001000+page*1024; original BE16 pages0..27 pass. Misaligned source is copied downward through an unknown resident operation before programming. |
| W program/readback |9CFC increments liveS0 by256 BEFORE9D00. Returned liveS0/liveS5 control the loop; four calls require the relevant state to survive callees. LW Flash9D10 precedes fresh LW live source9D16, comparing32 bits at step4. Mismatch repliesFF; match requests page reply. |
| U | Clear active before92F2(payload+1,(length-1)&255). Raw zero proceeds; reread mode through liveS0 after UID. Only mode1 schedules callbacks, while another mode can still receive byte1. No strict full-length15 comparison exists in this body. |
| S | Store saved mode and byte1=1 at liveSP+12/13 BEFORE UID. Reread liveS0 mode after UID. Successful active store takes low8 of **post-UID liveS1**, not an unconditional literal1 under arbitrary callee effects. Reply uses current liveSP+12, not an automatically copied array. |
| R | Active, strict full length16 and UID14 raw zero precede fresh BE16 page reads. No W page0..27 guard. |
| E | Active, strict full length15, mode0 and UID14 raw zero. Clear active before scheduling8E18/200, then99E8/400, then empty E reply. |

There are12 direct call sites, one indirect call and one final JR. All direct calls write RA, including halfword `693b` at9DF4: **RV32 C.JAL rd1→9B8E, RA9DF6**, not a tail. The only indirect call is9CEC through A5 loaded from a freshly materialized0x40000+0x4C. Per-site explicit arguments/links are listed in JSON; all remaining A0..A7 are actual live/opaque residues, without a complete intermediate raw-GPR claim.

Inspection found a concrete bridge gap and the producer fixed it before freezing: W replies originally projected only A0..A2, omitting A3=the last source word from9D16, A4=1024 from9D08, and A5=the failing offset or1024 after complete match. Final C supplies these values and mask63 at both W reply boundaries. Only this selected subset improved; for example R's shifted high-byte A5 residue remains unprojected. Full raw8 equivalence is not established. Native response[2] does not establish original liveSP+12/13 addresses/aliases. HOST return-address state is saved-data bookkeeping, without executing or fully reproducing the original JR or changed return target.

The51 owned RELAs bind31 internal control edges,12 external direct calls and four HI/LO pairs. The sole recorded outside direct incoming is14094 JAL rd1→9C4A/link14098. Unrecorded/computed entries are not excluded. `owner-addresses.json` is validation data from the actual LLVM carrier, never a provider or numeric-alias generator.

```sh
python3 -B check-source.py --project-root ROOT --firmware OFFICIAL_BIN
python3 -B check-source.py --project-root ROOT --firmware OFFICIAL_BIN \
  --original-object ACTUAL_SOURCE_INTEGRATED_OBJECT
```

Default mode actually reads the official BIN, redecodes169 rows and rejects eight single-field operand controls relevant to the new consumer. Only an explicitly supplied object is claimed reread; default mode needs no historical W build. The old large OTA HOST matrix is not rerun. Overlapping copy, ROM identity, GP/S/SP preservation, actual delivery, physical hardware, installed BOOT and flash readiness remain unproved. This Runtime body writes the BOOT region; it does not prove a new Runtime can update itself. Word readback comparison is not whole-image CRC/signature validation.
