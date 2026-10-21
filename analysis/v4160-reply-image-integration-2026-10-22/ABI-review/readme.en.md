# Twelve-function full image: independent ABI review

[繁體中文](readme.zh-TW.md) · [简体中文](readme.zh-CN.md)

This review adds the OTA page-reply function to the prior eleven-function integration. Twelve readable C/C++ functions occupy650 bytes. Remaining sections retain original-byte carriers; complete source recovery is not claimed. Final actual C/C++ results and selected artifact hashes are recorded in `summary.json` and `receipts/`.

`baseline.json` contains verification-only expectations independently derived from sealed prior actual objects:691 allocation owners,679 retained section hashes,8257 outside relocation roles, global/local/SECTION roles,53 relative bindings and21 physical incoming sites. Fresh actual checks do not require historical Windows build objects.

All650 linked function bytes must equal original firmware. Twelve actual JALs retain width, destination register, target and RA; eleven discharged private branches retain exact original words and targets. Reply TX at9BE0 targets retained8A56 with RA9BE4. Incoming9DF4 bytes693b encode C.JAL/RA9DF6, not a no-link transfer. The original public NOTYPE/size0 and local entry0 remain; the new compiler FUNC124 is a separate symbol.

Two explicit stages are checked:28 reordered reply bytes before merge, and14 IRQ/Flash-quarter save-order bytes after merge. Actual compiler words, receipts, hashes and unchanged surrounding metadata are bound. The pipeline is C/C++ compilation plus explicit ABI ordering, not compiler-only final save ordering.

Excluded `.llvm_addrsig` grows56→57 bytes. Its old56-byte prefix hash must remain exact; its sole appended symbol index must come from the actual reply object and resolve to FUNC124 there. The concatenated merged section has link0, so its bytes are not interpreted as global symbol indices. It must be absent from final ELF.

Every LOAD memory extent, permission and file/NOBITS distinction is checked. All690 file-backed owners must cover76800 bytes without gaps or overlap. The actual BIN must equal linked scatter and original SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Six independent controls mutate actual ELF/BIN bytes: incoming link, TX RA, original NOTYPE role, LOAD permissions, appended addrsig payload and an exported byte must reject.

```sh
python -B check.py --project-root ROOT
python -B review.py --project-root ROOT --firmware ORIGINAL_FW --folder ACTUAL_MODE_FOLDER --receipt NEW_REPORT.json
python -B review.py --project-root ROOT --firmware ORIGINAL_FW --replay NEW_REPORT.json
```

Default `check.py`/`check.sh` verify sealed source/metadata only, without firmware or build-artifact replay. The other commands and `review.sh` explicitly inspect actual artifacts; output reports must be new. Published seal members exclude `.o`, `.elf`, BIN and `build/`. The default README equals the full Traditional-Chinese version; languages use separate files.

The numeric ROM witness does not contain resident ROM implementation. Computed entries, actual chip/board, resident ROM, hardware, interrupt timing and safe Bluetooth flashing remain unverified. No target execution, CPU emulation, network, physical I/O or firmware BIN generation occurs in this independent review.
