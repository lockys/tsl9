# Source integration of the 0x14056 entry

[繁體中文](README.md)

`src/native/receive/ota_entry_14056.inc` expresses the 56 bytes at `0x14056..0x1408E`: the stack frame, saved registers and initial command-dispatch branches. It must be placed at its original address and continued by the enclosing code; it is not an independently callable C function.

Each C/C++ object has five RISC-V branch relocations. The builder checks their types, sites and targets, links at `0x14056`, compares the result byte for byte to the original and then uses the compiled result in the candidate. Together with the earlier epilogue, 70 bytes come from compiled source; 3,058 bytes remain opaque carriers. The complete original bytes remain in JSON for comparison.

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` verifies that an isolated 190-file source copy without the existing BIN can rebuild both candidates; `scripts/verify-payload-active-gates.py` rechecks the conditional link and prior control flow. Matching bytes do not establish full functionality, installed ROM/ABI or hardware safety.
