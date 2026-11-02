# Conditional link with source-carried original sections

[繁體中文](README.md)

Run `python scripts/verify-conditional-full-payload-link.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`.
The test compiles the source-carried `0x14056..0x14C8A` code bytes and `0x1A69C..0x1A6A0` data into real sections, and links them with three conditional data aliases and the TX RAM model. Strict linking leaves `tsl9_boot_resident_40000`; providing its numeric address only as a diagnostic witness produces a complete 76,800-byte image in each language matching the existing candidate SHA-256.

This proves the link and byte layout only under the stated conditions. The entry, forwarding, epilogue and continuation total 134 bytes compiled from source architectural instructions; the remaining 2,994 bytes use opaque carriers. Global index invariants for the aliases, RAM ownership and installed ROM/ABI remain unproved. The diagnostic ELF has no PT_LOAD, and the resulting BIN is not validated as safe to flash; no firmware or hardware is executed. Potential authentication material is not disclosed here.
