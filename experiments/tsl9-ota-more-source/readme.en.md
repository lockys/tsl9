# Dispatch continuation at 0x140A6

[繁體中文](README.md)

`src/native/receive/ota_more_140a6.inc` expresses the 54 bytes at `0x140A6..0x140DC` as C/C++ architectural instructions, retaining the command comparisons, state reads and original branches. It depends on the enclosing stack frame, registers and original address and is not independently callable.

Each C/C++ object contains five standard branch relocations and one compressed jump relocation. The builder checks their sites and targets, links at `0x140A6`, compares the result byte for byte to the original and puts the compiled result into the candidate. The entry, epilogue and this range total 134 bytes compiled from source; 2,994 bytes remain opaque. The original JSON is retained for comparison.

Run `python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` for isolated source rebuilding. `scripts/verify-payload-active-gates.py` rechecks the conditional link and prior paths. This does not prove complete functionality, installed ABI or flashing safety.
