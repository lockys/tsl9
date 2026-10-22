# Callback call frontier: the GP halfword is not a missing argument

[繁體中文](readme.zh-TW.md)

This supplement answers the new def/use/kill question. The fifteen target-source, explicit A0..A7 assignment and opaque-residue records remain authoritative in sealed `v4160-event-callback-2026-10-22/source-review/contracts.json`: `opaque_calls`, `additional_raw_argument_obligations` and `all_calls`. No duplicate argument table or prior evidence was modified. The checker resolves both working `apk-analysis/tsl9-` and delivered `analysis/` case layouts.

The checker reads the actual official ID2966 image, base `0x8000`, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. It redecodes each of the fifteen JALR widths, rd, rs1 and raw links and the narrow local control-flow window. The previous 217-instruction/26-control matrix is not rerun.

| Original PC | Raw operand obligation |
|---|---|
| `0x87C8..0x87CA` | Mask A0 with 1, branch nonzero to `0x87FC`; A3/A4/A6/A7 remain untouched. |
| `0x87FC` | Copy live GP into A5 for the next load. |
| `0x8800` | **LHU A5,[A5+0x2A]**. The destination is x15, not A4. |
| `0x8804..0x8806` | A2=0 and A1=live S1. |
| `0x8808` | SH A5,[live S1+0] consumes the datum's low 16 bits. |
| `0x880C` | **LW A5,[live S7+0xD4]** kills the datum and establishes the call target. |
| `0x8810..0x8812` | A0=live S5, then JALR RA,A5 with original link `0x8814`. |
| `0x8814` | A nonzero result branches to release at `0x87CC`. |

The GP+0x2A datum is dead at `0x8812`. Adding it to C `a[4]` would overwrite the source's live post-`0x87C6` A4 residue. **No missing C argument repair was found at this call.** Current C uses `v` for the SH, then loads a separate `target`; the native call port writes that target into A5.

Optional `--component` reads the already-reviewed actual 624-byte ELF without executing it. Actual C and C++ bytes agree: LH A0,[GP+0x2A] at `0x120A`, SH at `0x120E`, then A0 is overwritten with the connection role at `0x121A` before JALR at `0x1220`. With matching live GP, descriptor address and memory replies, the low16 SH data agree; the candidate's sign-extended temporary is also dead at the call. Intermediate GPR, fault, interrupt and asynchronous boundaries are not shown equivalent.

Two concrete bridge constraints remain:

- Original `0x880C` reads **live S7+0xD4**. Candidate `0x1212` rematerializes S8=0x40000 and `0x1216` uses that constant base. Prove preceding opaque calls preserve original S7, or provide a genuine physical-S7 port with separately verified register ownership and compiled operands. A carried C field or constant rematerialization does not establish arbitrary live-S7 behavior.
- Original RA is `0x8814`; candidate component RA is `0x1222`. Translating only component base `0x1000` to `0x8614` projects RA to `0x8836`. An actual admitted source/layout transformation must preserve the callee-visible link, or evidence must establish that the resident callee does not observe it. No image generation, tail filling or full ABI admission is claimed.

```sh
python3 -B check-review.py --project-root ROOT --firmware OFFICIAL_BIN
python3 -B check-review.py --project-root ROOT --firmware OFFICIAL_BIN \
  --component ACTUAL_ORDERED/COMPONENT-ONLY-NOT-FIRMWARE.elf
```

Default `actual_candidate_artifact_read=false` means actual original-source and immutable model-source identity checks only. Supplying an actual ELF changes it to `true`; no historical W build path is needed. The option accepts only the reviewed 624-byte identity, not an arbitrary unreviewed candidate. Three decodable operand controls change the LHU destination, SH source and target LW slot offset; the local semantic gate rejects them independently of a whole-file hash. No HOST rerun, new model compilation, RV32 execution/emulation, network or hardware operation occurs.
