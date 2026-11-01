# Source-built selected span data

[繁體中文](README.md)

`python scripts/build-source-spans.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` rebuilds the C/C++ diagnostic layouts and concatenates selected bytes in original-address order into `NOT-FLASHABLE-selected-spans-*.bin`, with `NOT-FLASHABLE-spans.json` as the address index. It reads neither a candidate image nor the excluded ranges. Each language emits 73,672 bytes and checks the retained digest.

| Original half-open address range | Output half-open file offsets | Bytes |
| --- | --- | ---: |
| `[0x8000,0x14056)` | `[0,49238)` | 49,238 |
| `[0x14C8A,0x1A69C)` | `[49238,72296)` | 23,058 |
| `[0x1A6A0,0x1AC00)` | `[72296,73672)` | 1,376 |

The output is a **concatenation of three spans**, not a contiguous original-address image; the designated 3,128 excluded bytes are not filled. Selected sections include 121 opaque original bytes. The strict link retains seven dependencies; numerical witnesses, ROM/RAM, startup, execution and hardware compatibility remain unresolved. **Do not flash this data file.**

To compare each selected section with a candidate without reading excluded ranges, run `python scripts/verify-allowed-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>`.
