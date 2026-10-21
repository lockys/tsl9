# TX register ABI: required behavior versus acceptable compiler differences

[繁體中文](readme.zh-TW.md) | [简体中文](readme.zh-CN.md)

This review distinguishes ABI/functional obligations from byte-layout differences using original `0x8A56..0x8B6E` and actual C/C++ objects. Compatibility does not require every byte to match. Unknown ROM behavior and memory aliasing still prevent hardware admission or whole-image replacement.

Measured progress now includes a narrow entry, real typed returning leaf and C body totaling 280 bytes, followed by an explicit source-owned frame scheduling layer. A bounded original/candidate loop CFG correspondence is also checked. These are separate static results, not hardware/OTA validation.

## Potentially acceptable changes

ADD/MUL operand reversal is the same unsigned32 operation when width, destination and incoming values correspond. BEQ/BNE operand reversal preserves the symmetric predicate but needs separate target/role proof. A similarly shaped sentinel comparison is not automatically the gate-result comparison.

Local branch inversion/layout changes need actual CFG, continuation and known-role proofs. A genuine PCREL HI/LO anchor may move if it resolves the same RAM symbol into A3 and preserves use ordering and known references. Original `+0x80` is not intrinsically mandatory.

Five independent saved-register stores can commute at a normally completed first-call boundary when all accesses complete, source registers remain unchanged and no fault/interrupt-prefix equivalence is claimed. This does not justify moving fresh frame reads across potentially aliasing descriptor writes. The shape candidates in `predicates.py` explicitly do not prove incoming values or logical role correspondence at different PCs.

## Required observations

The original unsigned `A3>1039` path has no frame/memory effects, retains entry A0/RA/SP and leaves A5=1039. Gate RAs are `0x8A90` and `0x8AB6`. Unknown ROM does not establish that RA, T1 or other residues are ignored.

Gate two forwards the first opaque gate's A2/A3 residues; it sets A2=1 even if its acceptance check fails. Failure A0 is path dependent, with no proven common status.

Success fresh-reads RA/S1/S2/S3 before descriptor writes and S0 before the ROM tail-target load. Source-worker interval/byte algebra gives a concrete alias counterexample: live SP `0x2000B170`, lane0 B `0x2000B18C`, hence saved RA at SP+28 equals B. With saved RA `0x12340003` and N=1, a later `SH16(B+2,7)` makes a delayed RA load read `0x00070003`; the original earlier load retains its prior value. This is not CPU execution or proof of actual stack placement.

Payload copying must retain live S0/S1, low16 counter comparison, full32 address arithmetic and byte-wise read-before-write feedback. The tail must retain its task LBU, fresh ROM `+0x50` target, arguments/residues and no-link JR T1.

## Ordinary C feasibility

A minimal C example does emit a guard before its frame. Removing the full TX guard's memory clobber and enabling shrink-wrap did not change its placement. Thus the clobber is not a sufficient root cause, and ordinary-C impossibility has not been established.

The actual source-only split diagnostic emits an 18-byte entry plus a 272-byte valid body. Its oversized RET avoids the frame. The valid path uses compiler-owned AUIPC/JR T1 without a new RA, but totals 290 bytes, adds a T1 write before gate one and retains late restores. This establishes a feasible entry-prefix technique, not complete admission.

Two cold-success hints in the canonical C/C++ candidate emit 278 bytes and 95 instructions, restoring both gate RAs to `0x8A90`/`0x8AB6`. This is measured progress from ordinary C topology. The frame still precedes its guard and success restores remain late. If placed at the original entry, two trailing bytes still lack replacement-source ownership. Numerical fit does not establish replacement admission.

The first narrow-entry assembler probe expanded an external BLTU into BGEU/JAL, totaling 284 bytes; it was not accepted. A standard `bltu a5,a3,0` plus one `R_RISCV_BRANCH` relocation to the real typed RET then emitted entry8/body270/leaf2. Entry `0x8A56` falls through to C at `0x8A5E`; the oversized branch reaches the compiled RET at `0x8B6C`. The actual entry FUNC remains 8 bytes; 280 is the aggregate allocation, not a fabricated compiler FUNC size. No extra T1 entry transfer occurs.

## Explicit narrow frame scheduling

The new pass handles only two windows of the fresh compiled valid body: five C.SWSP words in `[2,12)` and success tail `[208,270)`. Saves become S0/S1/S2/S3/RA. Only five existing C.LWSP words move in the tail: RA/S1/S2/S3 before descriptor SH, S0 after both SH and before the ROM pointer load, with SP increment remaining after task LBU. Other word order, total length and all ELF metadata stay exact. Original firmware is not a word-generation input.

`tail.py` independently reads pre/post objects and checks both windows, all outside bytes, word inventories and fresh-read frontiers. `controls.py` rejects fourteen actual ELF mutations per language, including storage aliases, symbols/relocations/branches/call returns inside windows, wrong registers/slots/widths and double application. Three actual CLI alias rejections are also checked. This is compiler output plus an explicit ABI scheduling layer, not a claim that the compiler emitted the final ordering.

## Bounded loop correspondence

`loop.py` reads the original96 and actual ordered linked ELF. Original BLTU true reaches out-of-line payload; candidate BGEU false falls through to payload. Both compare the same low16 counter against live S0. Eight payload instructions correspond field by field, allowing only ADD A6 operand reversal; both backedges reach the corresponding counter header. Checksum finish and zero-iteration A6 behavior also correspond. Nine actual linked instruction-byte mutations are rejected per language.

This correspondence assumes matching A1/A4/A5/S0/S1 at logical boundaries and corresponding byte responses. No loop or ISA state is executed. Async interference, differing code bytes read as payload, unknown computed interior entries and arbitrary ROM behavior are outside the claim. The nine full-image incoming entries and private roles still require separate integration checks.

Unadopted diagnostics do not replace sealed components or the full image. No full-function assembly, borrowed original bytes, padding, old-scheduler expansion or opcode encoder is used.

## Explicit static commands

The default validates sealed source/metadata and dependency source hashes without reading firmware or builds:

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/check.py --project-root .
```

For fresh actual artifacts, `review.py` combines entry, both frame windows, loop CFG and fourteen existing guard controls. Providers come from the actual producer receipt's `pre_folder`, or explicit `--providers`. New receipts are create-only; replay is read-only:

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/formal/ordered/c --receipt /absolute/new-review.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --replay /absolute/new-review.json
```

Default stdout reports `actual_build_artifact_replay:false`, versus true in actual mode. Both retain `original_full_ABI_admitted:false` and `whole_image_integrated:false`. `review.sh` defaults to metadata-only, forwarding any supplied arguments to actual mode. `PYTHON` selects Python.

Individual source/diagnostic checks remain explicit:

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/predicates.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/prior-native/c --receipt /absolute/new-predicates.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/split.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/split/c --receipt /absolute/new-split.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/candidate.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/candidate/c --receipt /absolute/new-candidate.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/loop.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --elf /absolute/ordered/COMPONENT-ONLY-NOT-FIRMWARE.elf --receipt /absolute/new-loop.json
```

Receipts are create-only. Four predicate controls reject expanded decoded-operand relations; four split controls mutate actual compiled entry bytes to check condition, RET link, address GPR and tail link. `candidate.py` reuses seven sealed actual-operand controls and additionally checks both original gate RAs. None executes/emulates RISC-V. Recorded incoming/interior-reference evidence does not establish absence of arbitrary computed references.
