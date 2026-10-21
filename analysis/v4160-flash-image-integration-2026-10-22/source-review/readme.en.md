# Independent review of the IRQ and Flash integrated image

[繁體中文](readme.zh-TW.md)

This review reads the final C11 and C++17 objects, linked ELFs, BINs and compilation records. Eleven readable C functions, 526 bytes total, replace their original allocations; the other 680 allocations retain the original instruction/data carrier. This is a partial source reconstruction in a hybrid image. Hardware boot and OTA acceptance remain unproved.

Both actual 76,800-byte images have SHA-256 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`: 70 changed bytes from original ID2966, 62 from the previous IRQ-only image. No original/rebuilt RISC-V instructions, emulator, device or network operation was executed.

## Evidence and scope

`source-constraints.json`, SHA-256 `b1d2908c00fd7577beaf5cf9eee0a462cbe611767d310c7314ef945691da8ccf`, was independently derived from actual local original/prior objects and sealed IRQ/Flash component ELFs. It preserves source-backed roles and hashes for portable admission of new artifacts when the old build archives are absent. Portable mode explicitly does not claim to reread those archives.

The independent gate verifies all 691 original allocation metadata and linked addresses, the partial-object contents of all 680 retained allocations, all eleven native bodies, real section-owned FUNC aliases/providers, all 53 section-relative bindings, and all twenty external references to selected function entries. It preserves all 8259 outside relocation records, including signed addends and multiplicity; the actual new owned relocations are eleven JALs, for 8270 total.

The original 8280-relocation object contains 21 selected-owner records: six IRQ JALs, four IRQ branches, five Flash JALs and six Flash branches. The prior IRQ object has 8276 total and seventeen selected-owner records because the four IRQ branches were already resolved inside its native components. The new object has `8259 + 11 = 8270`. Exact six Flash branch roles are discharged; unknown names are not removed by wildcard or assumed to be free space.

An independent quoted-assembly interval filter reproduces the four source filters. Each of the 34 actual raw carrier objects lacks all selected allocations, preventing raw fallback. Compilation provenance independently checks 42 object TUs, 56 distinct compile/IR/link/export recipes, 42 actual dependency rules, 72 existing project files and twelve generated inputs. Every rule binds its own object target, primary source and injected adapter. `-MMD` excludes compiler system/resource headers; this is a project-input closure, not a complete compiler-header inventory.

Both final language archives passed actual reads of 194 pinned artifacts/logs/dependency files each, plus the producer's read-only static replay of 23 ELF/RELA/image and three dependency controls. All 691 linked sections and fifteen PT_LOAD segments agree on data, memory extents and per-byte permissions. The RAM allocation remains NOBITS at `0x20004000`, 35160 bytes. Actual linked section bytes, LOAD bytes, BIN bytes and an independent overlay of sealed native components match exactly.

Partial-object relocation-bearing data are not expected to equal final BIN bytes. Retained partial-object storage hashes, linked native bytes, and the final ELF/LOAD/BIN layers are checked separately. The full nonmetadata symbol-role multiset also matches its independently derived reference.

## Independent controls

`independent-controls.json` records fifteen actual ELF/RELA/BIN file mutations and two actual dependency-text mutations, all rejected by the independent gate. They cover an omitted allocation, original raw fallback replacing the native program, an outside RELA addend, a duplicate relocation preserving count, ABS/NOTYPE aliases, an entry reference redirected into an interior, a relative-binding displacement, shortening the 100-byte program owner to 94 bytes, LOAD address/memory/permission errors, a BIN byte outside selected owners, and truncation. These are static file controls, not target execution tests.

The actual control files remain only in local `build/independent-controls`; the small sealed result is an archival receipt. Default admission does not claim to regenerate it. `control-artifacts.py` can recreate this bounded suite in a fresh directory.

## Commands

Metadata/source admission needs no old build archive:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/ID-2966-V4.1.60-decoded.bin
```

For actual new artifacts and compilation provenance:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original.bin --receipt /path/to/new-build/c/verification.json
```

Alternatively provide `--new-object source-integrated.o --new-elf ADDRESS-WITNESS-ONLY.elf --new-bin NOT-FLASH-VALIDATED-irq-and-flash.bin`. That mode does not claim compilation provenance. Add `--producer-replay` only when a complete actual archive and its recorded tools are present; it performs additional read-only static checks. `check-review.sh` uses `PYTHON` or `python3`; Windows may invoke Python directly.

Optional `inspect-image.py` rereads original archives using `--original-object`, `--prior-object`, `--IRQ-elf`, and `--Flash-elf`. This was performed locally. Portable admission still emits `original_baseline_archives_replayed: false`.

## Open boundaries

The strict final link fails on the missing `__tsl9v4160_rom_entry`. The numeric witness script assigns `0x40000` without supplying ROM bytes or implementation. ROM contracts, complete firmware behavior, physical nonreturn register prefixes, pointwise/asynchronous equivalence, installed BOOT identity, hardware compatibility and OTA acceptance remain false/unknown. No newly proposed feature is claimed implemented.

`review.json` and the two `selected-*-verification.json` files bind the final inputs and actual producer receipts. `final-C-review.json` and `final-CPP-review.json` retain independent readback results. Historical receipt paths describe the original workspace, not the availability of old artifacts on another machine. Supply an actual fresh receipt or three fresh artifacts there.
