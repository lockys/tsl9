# Conditional TX RAM model

[繁體中文](README.md)

The [source](../../src/native/tx_candidate/conditional_storage.c) declares a 2,124-byte uninitialized object, placed at nominal `[0x2000B18C,0x2000B9D8)` in a diagnostic layout. The model is based on the address and length passed to ROM in the [existing main-flow analysis](../../analysis/main-runtime-family-2026-10-24/readme.en.md), together with the two 1,062-byte TX slots; ROM behavior and physical RAM ownership are unproved.

Run `python scripts/verify-conditional-tx-storage.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` to compile actual C/C++ `NOBITS` objects and link a conditional diagnostic layout. With the TX RAM symbol backed by that object, the strict link retains six APP dependencies; a comparison link using numerical witnesses preserves all 73,672 selected Flash bytes. The ELF has zero `PT_LOAD` and is not a BIN.

**This is a conditional link model.** Hardware RAM capacity, startup clearing, stack, IRQ, DMA, other globals, ROM use and nonoverlap are unverified. Do not flash it or claim the RAM issue is solved on hardware; the default build retains the original unresolved RAM reference.
