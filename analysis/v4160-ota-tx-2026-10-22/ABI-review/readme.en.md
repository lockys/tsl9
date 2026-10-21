# Independent TX 0x8A56 ABI and static component review

[繁體中文](readme.zh-TW.md)

The readable C/C++ component is 280 bytes and 96 instructions. It fits the original extent, but **original ABI equivalence, original-location replacement and whole-image integration remain unproved**. This milestone keeps the existing twelve-function full image unchanged.

`summary.json` identifies the selected final inputs and receipts. `selected-c.json` and `selected-cpp.json` record actual object, LLVM IR and linked-component inspection. Default validation reads only sealed source/metadata and dependency hashes; archived build files are not implicit inputs. No compiled object, ELF or BIN is sealed here.

## Original evidence

The pinned ID2966 V4.1.60 body is `0x8A56..0x8B6E`, 280 bytes, base `0x8000`. `original-source.json` records original evidence. Nine recorded external incoming branches enter at offset zero: eight create RA; `0x13EAC` is JAL rd0. `0x135A8` is JAL rd1 with RA `0x135AC`. Encoded instructions determine link behavior, not relocation type or symbol name.

The original unsigned length limit 1039 precedes frame allocation. Two fresh ROM `+0x13C` pointer calls are opaque. Their actual signatures, register-preservation rules and physical effects are unknown. Gate two forwards gate one's A2/A3 residues. The selected lane uses stride 1062, header/byte copying/checksum and descriptor stores. A fresh ROM `+0x50` pointer ends in JR T1 without a new RA. No alloc/copy/free call is visible here.

The initial bound does not constrain S0 after an opaque call. The loop compares the low sixteen counter bits against live S0 while address arithmetic uses the full counter. Arbitrary ROM behavior, faults, nonreturn, GP/SP changes and interrupts have no physical proof.

## Remaining native gaps

- The compiler allocates/saves the frame before the length guard; the original oversized path returns without frame accesses.
- Gate two is at `+0x62`, versus original `+0x5E`, changing its continuation and internal positions.
- Success restores RA/S1/S2/S3/S0 after descriptor stores and task-byte loading, rather than the original interleaved order. Fault, saved-frame alias and interrupt prefixes are not equivalent.
- Even after normalizing branch targets and PCREL immediates, instruction inventories differ: BEQ/BNE structure, MUL/ADD operands and GP address formation. An existing-word scheduling pass alone cannot close these gaps.

The current candidate removes extra A2/A3 writes before gate two, an extra failure A1 copy and cached A7 loop length; live S0 is observed. These improvements do not establish original ABI admission.

## Commands

Metadata-only validation, without firmware or build reads:

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/check.py --project-root .
```

Actual fresh artifacts, explicit local firmware and a new receipt path:

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/native/c --receipt /absolute/new-review.json
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --replay /absolute/new-review.json
```

`review.sh` runs metadata validation without arguments, otherwise forwards arguments to `review.py`. `PYTHON` selects Python. Actual mode reports `actual_build_artifact_replay:true` and `original_ABI_admitted:false`.

Each language's actual 96 instructions are decoded across all bytes. Seven actual operand mutations and two linked-ELF byte mutations are rejected. The only object relocations are the RAM alias PCREL HI/LO pair. The linked pair resolves to numeric `0x2000B18C`; all other bytes equal the fresh compiler object. This numeric provider proves neither installed RAM nor ROM/board identity. No target execution, ISA emulation, new BIN generation or physical flashing occurs.
