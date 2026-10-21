# Static input check for the OTA transmit function

[繁體中文](README.md)

This directory checks the 280 bytes at `0x8A56..0x8B6E` in official ID2966 V4.1.60. The recorded image mapping starts at `0x8000`, so the firmware file range is `0xA56..0xB6E`. `inspect.py` compares the actual official BIN, the previous complete-image ELF and the partial-link object. It does not execute firmware instructions.

`inspection.json` records input hashes, the original owner, symbols and RELA. `tx-llvm-disassembly.txt` is static disassembly of the complete owner section by a hash-pinned LLVM tool. Selecting the section avoids stopping at the next local symbol, which occurs when selecting only the entry symbol.

The measured object has 9 external direct references, 10 internal references and 11 owner RELA entries. This scope cannot exclude unknown indirect callers. Symbol names are reconstruction anchors, not recovered vendor names.

`rea-session.json` records the actual connection: REA 6.4.0 responded with no native target open. Native providers were unconfigured, and the firmware-region provider was unavailable on this host. The disassembly therefore comes from independent LLVM tooling, not a claimed REA function analysis. No additional engine was installed.

See the adjacent `source-review`, `implementation` and `ABI-review` for semantic and C/C++ checks. This static record does not prove ROM service implementations, physical SRAM, chip identity, Bluetooth transmission or flash compatibility.
