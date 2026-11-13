# V4.1.60 record-helper reference targets

Offline, self-contained Python 3 standard-library verifier. From the repository root:

```sh
python -I -S -B experiments/v4160-record-helper-reference-targets/test_verify.py
python -I -S -B -O experiments/v4160-record-helper-reference-targets/test_verify.py
python -I -S -B experiments/v4160-record-helper-reference-targets/verify.py
python -I -S -B -O experiments/v4160-record-helper-reference-targets/verify.py
```

Default inputs are `experiments/tsl9-record-helpers/spec-v1.json` and `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`; `--spec PATH` and `--bin PATH` choose other copies, which must have the same exact pins. No input is written, fetched or reconstructed. A failure exits nonzero and does not emit success JSON. No `assert` is used in the verifier; optimization does not disable checks. The tests exercise the decoders and ledger with synthetic inputs without the whole-file pins, and also verify the real pinned files and tampering. The standard unittest runner uses a custom result class that fails when no tests are selected (including `-k nonexistent`); this is tested in both normal and `-O` modes.

## What is checked

- Raw SHA-256 pins: spec `f658349a73f7b246cbb037fc32185afbd12773cf2fa1f924eafbf6687a081d44`; BIN `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, exactly 76800 bytes at base `0x8000`. Duplicate JSON keys fail.
- Each of 68 uniquely named, non-overlapping, bounded, aligned regions has the actual BIN slice hash in the spec. The verifier assumes each contiguous region group's **first** start is an instruction boundary, then walks the entire group by 2/4-byte instruction length through every adjacent region. It rejects an instruction crossing any region boundary, truncation and lengths greater than 32 bits, including in unreferenced bytes. This length walk does not establish opcode validity or reachability for unreferenced instructions. Each reference has strict integer types (not booleans), owner, offset, PC, width, bounds, and a boundary established by that walk. References may not duplicate or overlap. All 51 controls and 11 pairs are processed separately from raw BIN bytes.
- Type/size `(16,4)` is a standard B-type branch (6), `(17,4)` JAL (26), `(44,2)` C.BEQZ/C.BNEZ (14), `(45,2)` C.J (5). Encodings, widths, legal branch funct3 and JAL link register are checked. The JALs are reported individually and summarized as **16 rd=x1 (ra, linking calls)** and **10 rd=x0 (non-linking jumps, not calls)**; this labeling does not infer runtime behavior. Compressed C.JAL is not accepted as C.J.
- All 11 pairs are consecutive 32-bit AUIPC/ADDI; opcode, ADDI funct3 and the nonzero same AUIPC rd / ADDI rs1 / ADDI rd are checked. Signed U and I immediates are added to the AUIPC PC. Other forms fail rather than being guessed. RV32 target arithmetic is range-checked without wrapping.
- Decoded targets must equal each entry's `target_PC`. Internal targets must name the exact region start. Every other target must be a spec `undefined` name, outside the defined regions; all undefined names must be referenced, unique, and disjoint from the region names. One name must resolve consistently, and distinct target names may not collide at one address. The exact 18-name set is thereby derived from the pinned spec, not from suffixes or a hard-coded address table.
- Success JSON contains each reference's owner, PC, raw bytes, decoded target, target name and kind, and each external target's address, count and reference PCs. Output is delayed until **all** checks pass. The output addresses are numeric JSON integers.

The synthetic tests include positive and negative extrema and exhaustive short branch/jump displacements, JAL displacement bits, register aliases, invalid opcode/width/branch funct/link destination, bad AUIPC/ADDI register chains and PC movement, overflow and boundaries, duplicate/missing references, extra undefined names, target collisions and image/spec tampering. A cross-region negative case makes the second half of a 32-bit instruction look like a C.J at the next region's start; mixed 2/4-byte adjacent regions and independent groups across a gap are positive cases. Unreferenced truncated and greater-than-32-bit instructions also fail. Counts for the synthetic ledger can be supplied to detect missing individual entries even if the same external name has another reference. In production the pinned spec and fixed 68/51/11/18 inventories provide this protection.

## Observed static direct external targets

These are derived from the listed references, not assigned from names. Counts combine controls and address-forming pairs.

| Spec name | Address | References |
| --- | ---: | ---: |
| tsl9_callback_external_9124 | 0x9124 | 6 |
| tsl9_callback_provider_entry_13d48 | 0x13d48 | 3 |
| tsl9_callback_table_entry_90b0 | 0x90b0 | 3 |
| tsl9_feature_external_82a8 | 0x82a8 | 2 |
| tsl9_feature_external_f1c2 | 0xf1c2 | 3 |
| tsl9_output_builder_provider_d810 | 0xd810 | 1 |
| tsl9_record_dispatch_provider_1811a | 0x1811a | 1 |
| tsl9_record_helpers_provider_1a430 | 0x1a430 | 1 |
| tsl9_record_helpers_provider_1a454 | 0x1a454 | 1 |
| tsl9_record_helpers_provider_1a478 | 0x1a478 | 1 |
| tsl9_record_helpers_provider_a3cc | 0xa3cc | 1 |
| tsl9_record_helpers_provider_bd46 | 0xbd46 | 1 |
| tsl9_record_helpers_provider_bd50 | 0xbd50 | 1 |
| tsl9_record_helpers_provider_edf2 | 0xedf2 | 3 |
| tsl9_record_helpers_provider_ee30 | 0xee30 | 1 |
| tsl9_record_helpers_provider_ee9a | 0xee9a | 2 |
| tsl9_record_helpers_provider_eee0 | 0xeee0 | 1 |
| tsl9_rom_driver_external_9792 | 0x9792 | 3 |

## Trust boundary and limitations

The first instruction boundary of each of the eight groups is an explicit, **independently unproven assumption**: `0xa6aa`, `0xb0b0`, `0xb572`, `0xb594`, `0xde82`, `0xef76`, `0xf47e`, `0x18218`. Neither a spec hash nor a slice hash establishes instruction boundaries. No group start is claimed to be derived from bytes in a preceding gap. Success JSON reports the assumed group starts and exclusive ends under `assumed_boundary_groups`; all further boundaries within a group follow from the length walk, conditional on its first start being correct.

Only the references enumerated by the pinned spec are decoded. The list is not proof of a complete CFG or of all AUIPC pairs, and unlisted indirect calls remain unknown. Forming an address does not establish callback/data contents, invocation or reachability. This does not establish provider body or ABI, loader mapping, source purity, runtime behavior, or whole-BIN reconstruction. The whole-file pin checks identity only, not the origin or correctness of that file. The `b0b0` region is hash-checked as a region; its separate destination is not one of the 18 and is not manually promoted to an external target. No compiler, linker, target execution/emulation, hardware or network is used.
