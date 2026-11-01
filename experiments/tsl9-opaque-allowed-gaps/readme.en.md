# Opaque bytes in permitted ranges

[繁體中文](README.md)

The [source](../../src/native/receive/opaque_allowed_gaps.c) preserves 121 previously unselected candidate-image bytes in 31 read-only sections, all within permitted read ranges. These are opaque bytes, not a reconstruction of functionality, original types, reachability or executability; their values alone do not establish their purpose.

`python scripts/verify-allowed-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` freshly compiles and compares the selected 73,672 bytes for C/C++. Each read is bounded and excludes `[0x14056,0x14C8A)` and `[0x1A69C,0x1A6A0)`; these total 3,128 bytes and remain outside the build.

Matching selected bytes does not reconstruct the original source or complete firmware. Strict linking, ROM/RAM, startup and physical behavior remain unresolved; outputs are zero-`PT_LOAD` diagnostic ELFs, not flashable BINs.
