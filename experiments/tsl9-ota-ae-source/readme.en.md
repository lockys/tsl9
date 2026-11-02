# Source integration of the 0x140DC command path

[繁體中文](README.md)

`src/native/receive/ota_ae_140dc.inc` expresses the 70 bytes at `0x140DC..0x14122` as C/C++ architectural instructions, preserving the original branches, argument handling and call order. It depends on the original stack frame, registers and address and is not independently callable.

Each C/C++ object contains 11 relocations, including six external JALs. Fragment linking uses original-address witnesses; the complete conditional link separately checks all six targets are backed by executable sections. The builder uses the compiled bytes after an exact original comparison; original JSON is retained as a reference. Including [another command path](../tsl9-ota-ad-source/readme.en.md), 254 bytes in this region now come from compiled source, while 2,874 bytes remain opaque carriers.

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` rebuilds the candidate from an isolated 195-file source copy without the existing BIN. This does not establish complete functionality, installed ROM/ABI or flashing safety.
