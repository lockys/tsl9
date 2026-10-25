# Memory / ROM requirement checks

[繁體中文](README.md)

[`requirements-v1.h`](requirements-v1.h) records numeric startup requirements for the exact **ID2966 V4.1.60** official image. [`layout-contract-v1.c`](layout-contract-v1.c) checks addresses, extents and pointer widths with C11/C++17 static assertions. It is not executable firmware or physical chip identification.

`verify-v1.py` pins two official BINs, the startup source map, saved SDK header, ELF reader and compiler. It decodes version differences from original instructions, then compiles two RV32 ET_REL objects with no allocated code/data. It performs only positive compile-time checks and never connects hardware or executes output files.

From the repository root, using the saved SDK header and pinned Windows LLVM 18 toolchain:

```sh
python3 experiments/tsl9-memory-rom-contract/verify-v1.py \
  --sdk-header "$TSL9_SDK_HEADER" \
  --llvm-bin "$LLVM_BIN" \
  --output "$TSL9_AUDIT_OUTPUT"
```

Set these variables to the local `wchble_rom.h`, LLVM `bin` and a new output directory. Windows may use `py -3` and its Shell's line continuation. The script downloads nothing. Other toolchains need a separately documented verification profile; do not bypass the pinned digests. The C/C++ assertions themselves do not depend on Windows APIs.

[Findings and limits](../../analysis/memory-rom-requirements-2026-10-25/README.md). Matching the SDK default pointer table does not identify installed ROM bodies or ABI. Numeric containment in a conditional 64 KiB RAM candidate does not prove RAM ownership, usable stack space or hardware compatibility.
