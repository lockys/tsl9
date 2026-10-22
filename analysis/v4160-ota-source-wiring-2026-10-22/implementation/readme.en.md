# Source-wired numeric-address witness producer

[繁體中文](readme.zh-TW.md)

The single formal verify_image.py CLI supports fresh generation and read-only replay. It freshly compiles a real same-TU strong C568 alias and non-executable FF456 data, weakens only the old entry in a carrier copy, then partial-links and places actual sections using the old layout plus extension. The sealed compact algorithm/full eight-register bridges are included directly; raw kernel hash remainsb486c6...63af.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin \
  --base-object BASE/source-integrated.o --base-receipt BASE/verification.json \
  --base-witness BASE/ADDRESS-WITNESS-ONLY.elf \
  --base-image BASE/NOT-FLASH-VALIDATED-tx-integrated.bin \
  --build-root experiments/tsl9-v4160-ota-source-wiring/build/NEW-C
```

One language per invocation, inferred from the retained base receipt; no --mode/--language/--firmware. CPP uses its own base artifacts. Exact input hashes and the original receipt artifact map identify the four baseline inputs; the historical numeric script is read from the receipt folder and checked. Use real prior UUID archives in D/P rather than assuming formal-v1 paths. Fresh output is create-only under model/build.

Both actual language builds produce77,824 bytes with SHA3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee. Real caller14094 JALef60d036 reaches1AC00 with RA14098. Original691 allocations/8261 relocations remain, with explicit entry binding/preemption and caller-target projection. New partial693 allocations/8281 RELA retain nine allocated providers and sole real ROM UND. Raw530 remains in its old section; no fake FUNC extent or ABS C alias is introduced.

**ROM_provider=false.** Strict final linking really fails only for missing ROM and produces no strict ELF. A separate witness copies the exact historical ROM=40000 numeric script, yielding ADDRESS-WITNESS-ONLY.elf and a NOT-FLASH-VALIDATED BIN. This supplies no ROM body or installed-ROM/full-ABI/free-Flash-NV/OTA admission. The original reset tail/numeric boundary stays unchanged.

Per language:11 exact chronological recipes and20 actual artifacts, source/tool/input before-after pins, MD four project files plus actual stdint.h, complete193-instruction raw/linked coverage,13 full-eight-register asm calls,20 native relocations, all ordinary/metadata symbol origins,17 LOAD byte/permission checks and original35160-byte NOBITS RAM. Every77824 exported byte has actual section/LOAD ownership. Only three inherited bytes change inside the original caller word; appendage is real C568 plus explicit nonexec FF456, never missing code or BIN fallback.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root . --receipt C/verification.json --receipt CPP/verification.json
```

Published paths use analysis/v4160-ota-source-wiring-2026-10-22. Default check is source/seal/metadata-only with actual flags false. Explicit receipts read actual inputs/artifacts/logs/tools without launching compilers/linkers. results.json records two formal and two first-prototype metadata receipts; prototype.py is historical, while formal replay uses verification.json. Objects/build archives are excluded. Existing historical layout CRLF bytes remain untouched; new sources/docs/JSON use LF.

Independent ABI actual review passes both modes plus nine actual ELF negatives each. Allocator evidence retains unknown slot70 ambient/pointer observations and grants no bridge narrowing or ABI waiver. Unchanged HOST/base compilation was not rerun. No RV32 execution/ISA emulation/network/hardware/Flash write/UID-VIN access occurred.
