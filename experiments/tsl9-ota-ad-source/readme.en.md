# Source integration of the 0x1417A command path

[繁體中文](README.md)

`src/native/receive/ota_ad_1417a.inc` expresses the 50 bytes at `0x1417A..0x141AC` as C/C++ architectural instructions, preserving the original argument handling, calls and branches. It depends on the enclosing stack frame, registers and original address and is not independently callable.

Each C/C++ object contains eight relocations, including five external JALs. Fragment linking uses original-address witnesses; the complete conditional link checks that the call targets are backed by executable sections. The builder uses the compiled bytes after exact comparison, retaining the intervening unreconstructed range as an opaque carrier. In this region 432 bytes now come from compiled source and 2,696 bytes remain carriers.

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` rebuilds the candidate from an isolated 197-file source copy without the existing BIN. This does not establish complete functionality, installed ROM/ABI or flashing safety.
