# Source integration of the 0x14098 epilogue

[繁體中文](README.md)

`src/native/receive/ota_epilogue_14098.inc` expresses `0x14098..0x140A6` as a C/C++ naked function with explicit RISC-V instructions: restore RA/S0–S3, release the 192-byte stack frame and return. It depends on the enclosing function's frame and **must not be called independently**.

Both the full candidate builder and conditional link compile these 14 bytes in C and C++, check the actual ELF section and symbol and compare the result byte for byte against the original carrier, then use the compiled result in the image. The original JSON comparison bytes remain; see the entry integration below for current progress on the remaining range. The full BIN matches the previous candidate digest, which does not establish device boot or compatibility.

Run `python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` to rebuild both BINs from an isolated copy of 190 source and build files. The copy has no existing candidate BIN but does contain the original-byte carrier described above. The subsequent [entry source integration](../tsl9-ota-entry-source/readme.en.md) compiles a further 66 bytes from source.
