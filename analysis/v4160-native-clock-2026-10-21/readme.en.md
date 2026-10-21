# Native clock evidence

The readable implementation is under `experiments/tsl9-v4160-native-clock/`.
This scope reuses the sealed ID2966 V4.1.60 raw source proof at
`analysis/v4160-system-clock-query-2026-10-21/source/` (in the investigation
workspace: `apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/`).
The original two functions total 214 bytes / 69 instructions; the existing
50 raw negative controls remain unchanged.

- [Source contract](source-review/readme.en.md): source-specific effects and ABI limits.
- [Independent C/C++ review](code-review/readme.en.md): actual compiled tests and countercases.
- [Native structural review](native-review/readme.en.md): fresh RV32 compile/link and complete disassembly coverage.

Source/host proof and native structural proof are separate. Only our host
tests run. Original and rebuilt RV32 code are never executed or emulated.
Ordinary-C register, stack and interrupt ABI, full-image integration and OTA
compatibility remain unproved. No hardware or vendor-network request is used.
The existing original-layout offline image is unchanged; no new BIN is made.

Historical local build archives may be present in the delivered project but
are excluded from Git publication. Fresh host and native verifiers generate
their own ignored output directories. A published seal that binds a local
archive identifies evidence; it does not imply that excluded files are
available in a new clone.
