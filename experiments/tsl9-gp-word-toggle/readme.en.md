# 9B36 native C/C++ static verification

[繁體中文](README.md)

`src/toggle.v2.c` is the selected24B/7-instruction ordinary-C leaf. `toggle.v1.c` emitted26B and is retained as an unselected early-return trial. Empty assembly ports bind live GP/A4/A5; this is not an ordinary callable C ABI or a HOST program.

These commands require the retained local1902B parent objects, current curation receipt/objects and original BIN. Private build artifacts are not published through Git. Missing inputs fail closed without downloads or replacement evidence.

From the repository root, set `LLVM_BIN` to the installed pinned LLVM bin directory. See [the commands](README.md): choose a new output directory, build once, then run `verify-v3.py --write` separately for c/cpp. Removing `--write` reproduces the saved v3 receipt byte-for-byte without executing or recompiling the target. Tool/header identity mismatches fail closed.

`LEAF-ONLY-NOT-FIRMWARE.elf` contains only the24B nominal-address leaf. `UNRESOLVED-FULL-PLUS-LEAF.o` is a1926B diagnostic partial link with97 pending relocations and3 genuine undefined providers. Neither is firmware or an OTA image.

The spec's `native_ELF_sha256` identifies the original `toggle.v2.c` probe object. The formal curated object's STT_FILE is `gp_word_toggle.c`, so its whole-object identity is pinned separately by v3. Both code sections have SHA256 `3629ae9c699510146a50485e475c373cdf2ea385d086633b70f1cfc43a88fb79`.

Earlier checkers/receipts are immutable history. Version3 adds exact recipes, actual dependency/readback checks, UND metadata, a fixed complete IR-body identity, and saved-receipt comparison. Earlier1985 controls did not cover the six independently demonstrated escapes. No download, emulation, target execution, hardware access, or firmware BIN generation occurs.

[Analysis and remaining limits](../../analysis/gp-word-toggle-2026-10-23/readme.en.md)
