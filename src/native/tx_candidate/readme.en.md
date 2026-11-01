# V4.1.60 candidate TX source component

[繁體中文](README.md)

This independent `src/` package holds the tested candidate TX entry, C body and return leaf. `../receive/transport_frame.c` remains the original TX implementation; do not link both as providers for the same location. The entry is equivalent file-scope inline assembly; include paths are local. This package does not modify the historical `src/source-manifest.json` or sealed receipts.

With the original LLVM NDK 18, run `python src/native/tx_candidate/verify.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. It freshly compiles all three pieces as C11 and C++17, validates **pre-pass** section bytes and relocation fields, and emits `NOT-FLASHABLE-unlinked-TX-*.bin`. These 280-byte files are unlinked fragments, with no relocations, frame-order postpass, remaining APP, BOOT or resident; **do not flash them; they are not the 4.1.60 candidate BIN**. No official or candidate firmware is read.

Rebuilding the full candidate from `src/` still requires the correct symbol mapping and postpass, six providers, unselected and excluded ranges, RAM/resident/IRQ contracts and final OTA evidence. Existing hardware OTA evidence cannot be applied to this unlinked fragment.
