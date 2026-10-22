# Real OTA-handler source-entry wiring experiment

[繁體中文](readme.zh-TW.md)

A new TU includes the sealed compact algorithm and defines a genuine strong compiler FUNC568 alias for the original public entry. Standard llvm-objcopy weakens only the old NOTYPE entry in a separate carrier copy, allowing the original caller's symbolic relocation to bind to the strong C definition.

Actual C11/C++17 produce the same77,824-byte **NOT-FLASH-VALIDATED numeric-address witness**, SHA `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`. The real JAL at0x14094 targets0x1AC00, retaining RA0x14098. Only three bytes within that caller word differ in the inherited76,800-byte prefix. Original raw530 remains at0x9C4A; the proved known ingress is rerouted, not every unknown computed entry.

The appended1,024 bytes are actual compiled C568 plus explicitly non-executable FF456 page data, ending at0x1B000. Fill is packaging, never missing-code padding. Every exported byte belongs to real ELF sections and LOAD coverage; no old-BIN fallback supplies output bytes. Kernel identity/full eight-register bridge/frame48 do not prove complete original ABI.

**ROM_provider=false.** The no-ABS partial ET_REL retains sole real ROM UND. Strict final linking genuinely fails without a ROM body. The separately labelled numeric witness reuses only the historical ROM=0x40000 address boundary, corroborated by the original reset tail; it does not supply an installed ROM/provider or grant flash/OTA readiness.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin \
  --base-object BASE/source-integrated.o --base-receipt BASE/verification.json \
  --base-witness BASE/ADDRESS-WITNESS-ONLY.elf \
  --base-image BASE/NOT-FLASH-VALIDATED-tx-integrated.bin
```

One language per invocation, inferred from the retained base receipt. Fresh output uses a create-only UUID under model/build; explicit --build-root must be new. Existing baseline artifacts are pinned to their receipts; no base/HOST recompilation occurs. Baseline images validate output only and never generate code.

```sh
sh experiments/tsl9-v4160-ota-source-wiring/verify.sh --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root .
```

Published case paths use analysis/v4160-ota-source-wiring-2026-10-22. Python/shell interfaces are portable; actual tools are pinned Windows NDK binaries, not tested Linux/macOS native runs. Replay reads actual inputs/sources/artifacts without launching tools. Default check is source/seal/metadata-only with actual flags false. Opaque objects/build archives are excluded from publication.

Installed ROM/BOOT, free Flash/NV ownership at0x1AC00, full pointer/frame/S/GP/RA/async ABI and OTA acceptance remain unproved. Most original carrier storage remains. This is real source-entry-wiring progress, not complete readable firmware or hardware validation.
