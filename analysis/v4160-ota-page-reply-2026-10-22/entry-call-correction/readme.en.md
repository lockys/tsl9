# 9DF4 entry-call correction

[繁體中文](readme.zh-TW.md)

**Original bytes `69 3B` at `0x9DF4` encode RV32 `C.JAL`: rd=x1, target `0x9B8E`, RA=`0x9DF6`. This is a linking call.** Halfword `0x3B69` has quadrant1/funct3=1 and signed displacement−614. Relocation type45 (`R_RISCV_RVC_JUMP`) alone does not determine whether RA is written. The corresponding no-link `C.J` has funct3=5.

This supplement supersedes **only** `/recorded_RELA/external_incoming_role` in old `source-review/contracts.json`, and the README/Traditional-Chinese/English statements describing **9DF4** as the shared physical W/R tail edge. [correction.json](correction.json) lists exact old hashes, phrases and replacements. All prior sealed files remain unchanged. The no-link release tail through T1 at **9BF8** remains correct and is outside this correction.

The original firmware SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` and existing C/C++ boundary-probe `carrier.o`/`partial.o` were actually read. Both languages preserve `693b`, caller section offset426, type45 and the local target at section offset0. These are two-object boundary observations, not proof of whole-image linking or hardware/OTA compatibility.

`check.py` decodes instruction fields without CPU execution or emulation. Three raw controls reject a same-target no-link `C.J`, a changed target and an incorrect width. Three mutated actual ELF-byte controls per language reject a no-link word, changed relocation type and shifted local entry.

```sh
python -B check.py
python -B check.py --project-root ROOT --firmware ORIGINAL_FW --report NEW_RAW_REPORT.json
python -B check.py --project-root ROOT --firmware ORIGINAL_FW --folder ACTUAL_BOUNDARY_FOLDER --report NEW_BOUNDARY_REPORT.json
```

The default and argument-free `check.sh` modes verify source/metadata seal members only; they do not read firmware or build objects. Explicit `--firmware` rereads original firmware; `--folder` additionally rereads actual boundary objects. Report paths must be new. The pinned parser supports workspace `apk-analysis/` and published `analysis/` locations. No `.o`, `.elf` or generated build folder is sealed. No compilation, target execution, emulation, network or physical I/O occurs here.
