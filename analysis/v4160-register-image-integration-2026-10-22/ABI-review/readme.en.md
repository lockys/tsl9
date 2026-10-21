# Original-register-order whole image: independent ABI review

Actual C11/C++17 compiler, explicit ABI scheduling and linked outputs pass independent static review. The **76,800-byte image has zero differences from the original**, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. [繁體中文](readme.zh-TW.md) · [简体中文](readme.zh-CN.md)

This is source integration evidence for11 readable C/C++ functions occupying526 bytes. The other680 sections retain carrier sources. Identical output does not mean the complete application has been explained or recovered as high-level C.

## Actual evidence

- Actual compiler-integrated.o, source-integrated.o, frame-scheduling.json, linked ELF and BIN are read. The frozen policy's pure plan reproduces only the14-byte permutation of existing compiler C.SWSP instructions; every other byte/section/symbol/RELA stays identical.
- All11 pre-object bodies match sealed compiler contracts. All11 linked original-entry functions equal original bytes, including IRQ/wrapper save order, five Flash leaves and all original program boundaries.
- Checks cover691 allocations,15 LOAD extents/permissions,680 outside storage sections,8,259 outside/8,270 total RELA,53 relative bindings,11 JAL/RA continuations,10 discharged private branch roles and20 actual incoming width/target/RA contracts.
- The690 file-backed owners cover the complete image without holes, extra allocations or padding. Actual BIN equals both ELF scatter and original firmware.
- Per language,57 actual command/log/output associations and all producer artifact pins are checked, including42 object compilations and8 typed IR recipes. The strict missing-ROM link still fails;40000 is a numeric witness only.
- Five focused controls per language reject an unscheduled final object, false compiler-only provenance, an actual JAL→tail change, one corrupted BIN byte and an export sourced from a nonlinked file. Prior complete frame/native mutation matrices are not repeated. Detailed source/.d closure has a separate source review.

Compiler and scheduling remain separately identified. The compiler alone did not emit the final save order. Original firmware is for verification; transformation consumes compiler objects and export consumes linked ELF. No target execution/emulation, hardware operation or flashing occurs.

## Default metadata-only verification

The seal contains source, documentation, receipts and metadata only, **excluding generated objects, ELFs, BINs, IR, dependencies and logs**. Default commands do not read, rebuild or replay actual build outputs and explicitly return `actual_build_replayed=false`:

```sh
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/check_seal.py --project-root .
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root .
```

Retained receipts document historical actual checks. Metadata success is not a fresh local compilation or actual-artifact replay.

## Optional actual-artifact review

Build a fresh C or C++ MODE_DIR with the source producer, then explicitly request:

```sh
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root . --firmware ORIGINAL_BIN --folder MODE_DIR --receipt models-build-independent.json
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root . --firmware ORIGINAL_BIN --replay models-build-independent.json
```

Store new receipts under an ignored model/build directory. `--report` aliases `--receipt`; `--folder` can override the same actual directory during `--replay`. Missing actual artifacts stop the replay instead of substituting metadata success. Windows can use `python -X utf8 -B`. The POSIX wrapper was statically inspected without WSL/Git Bash execution.

Byte identity is a static source/ABI integration conclusion. Physical MCU/board, ROM contents, update packaging/flashing compatibility, recovery, external device state and hardware/OTA success remain unverified. Absence of unknown computed incoming references is not independently proved. No network, device I/O or target ISA execution/emulation occurs.
