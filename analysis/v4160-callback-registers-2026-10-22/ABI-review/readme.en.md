# Independent callback register-profile and fresh-GP review

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

Only `-ffixed-x26 -ffixed-x27` was added to the sealed profile. No flag search or unchanged HOST rerun was performed. The sealed658 baseline, fixed-only656 diagnosis and fresh-GP624 component remain distinct.

All240 actual instructions of the656 diagnosis and all223 of the624 component are decoded independently. The final variant reads current GP at six source-use points rather than16 entry/postcall snapshots: two task LBU accesses; GP+lane×4 followed by the connection LHU; two A1=GP+128 gate arguments; and post-gate GP+42 halfword access. The last is actually LH, not a claim of pointwise equality to original LHU. No encoded GP write or S10/S11 operand occurs.

The frame is48 bytes with exactly11 saves and11 fresh32-bit restores: RA44,S0 40,S1 36,S2 32,S3 28,S4 24,S5 20,S6 16,S7 12,S8 8,S9 4. There is no SP+0 or other syntactic SP-derived spill substitute. This does not exclude arbitrary physical aliases. All15 opaque JALRs write RA (14 A5,1 A6). IR retains eight argument read/write bindings and caller clobbers; it does not prove every original scratch residue.

All raw operands agree with independently normalized LLVM text. Actual object/ELF metadata has one allocated GLOBAL FUNC624, no UND provider, helper, extra allocation or padding. Five exact compile/IR/link/disassembly recipes and actual MD closure are checked. Verification-only `baselines.json` never generates code; normal checks need no historical object archive.

The explicit new scheduling stage swaps only existing C.SWSP words at+2/+4. Exactly4 file bytes change and every other object byte/metadata field remains equal. The normally linked ordered ELF also differs only at those4 bytes. This restores relative S0/RA save ordering only: the original preceding SLLI and the complete entry prefix are not restored. Known branch/call-return frontiers do not enter the changed words; unknown computed entries remain unproved.

Five actual raw-artifact countercases reject reserved S10 use, SP0 spill substitution, lost RA links, cached GP substitution and fabricated FUNC632. Four frame countercases reject wrong slots, interior symbols, REL storage and extra output changes. Both languages' actual outputs pass.

Metadata-only default (no firmware/build read):

```sh
python -B ABI-review/check.py --project-root ROOT
```

Actual raw compiler artifacts and read-only replay:

```sh
python -B ABI-review/review.py --project-root ROOT --folder PRE_MODE --receipt RAW.json
python -B ABI-review/review.py --project-root ROOT --replay RAW.json
```

Complete actual compiler→schedule→linked review and replay:

```sh
python -B ABI-review/review-ordered.py --project-root ROOT --pre PRE_MODE --folder ORDERED_MODE --receipt NEW.json
python -B ABI-review/review-ordered.py --project-root ROOT --replay NEW.json
```

Keep receipts outside producer MODE folders. `review.sh` defaults to metadata-only and otherwise forwards ordered-review arguments; `PYTHON` selects an interpreter. Only sources/metadata are sealed, without objects or BINs.

624≤632 proves numerical fit only. The final8 original bytes have no source provider, so whole632 storage coverage remains false. No padding, original-byte fallback, fake FUNC632 or full-image integration is admitted. Unknown resident physical S/GP/SP contracts, changed RA offsets, scratch residues, every fault/interrupt prefix and hardware/BOOT/OTA behavior remain unproved; all full-ABI/placement/hardware flags stay false.
