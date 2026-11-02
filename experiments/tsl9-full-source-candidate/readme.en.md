# V4.1.60 candidate image source build

[繁體中文](README.md)

Run `python scripts/build-v4160-source-candidate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` to compile C and C++ from `src/` and the project build tools and emit a 76,800-byte candidate for each mode. The builder checks the resulting SHA-256 against the existing TX-integrated candidate without reading that BIN during the build.

The 3,128 bytes in `src/native/tx_candidate/full-image-payload.json` retain the candidate's original bytes for comparison. During the build, 14 bytes at `0x14098..0x140A6` are compiled from [C/C++ architectural instructions](../../src/native/receive/ota_epilogue_14098.inc) and replace the carrier; the remaining 3,114 bytes still come from the opaque carrier. The fragment is the end of an existing stack frame, not an independently callable C function. Other sources may also carry original instructions or data. Reproducing the bytes does not prove complete source recovery, closure of strict-link dependencies, device boot, or functional equivalence. Numeric address witnesses remain part of the diagnostic layout.

**The candidate has not been validated as safe to flash.** Original device ROM/ABI, RAM, IRQ, OTA and functional behavior need independent evidence. This build does not operate hardware.
