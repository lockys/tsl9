# SPI write-path milestone

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/spi_write_providers.c) · [Detailed evidence and limits](../../experiments/tsl9-spi-write-providers/readme.en.md)

Reconstructed the block-write request at `0x168DE` and bit-modify request at `0x1693E`. Actual C/C++ compilation and original-PC linking with the existing SPI leaf produced **254 bytes/93 instructions exactly equal to the original BIN, with zero unresolved symbols or pending relocations**. v3 receipts also check entry, AX permissions, allocation mapping, LLVM fields and actual consumed inputs; 97 nominal negative controls passed per language.

Curated `src/` contains 62 C/H files, 36 native units, 72 comparisons and 144 objects. All previous 70 results and 421 artifact hashes remain unchanged. This is local static evidence: **no flashable BIN, completed reverse engineering, physical hardware or OTA compatibility is claimed**.

[Summary](summary.json) separates facts, inference and gaps. [Hardware correspondence](hardware-correspondence.json) establishes cached WCH address-map correspondence without confirming silicon or external controller count. Explicit SPI timeout diagnostics are a research opportunity; no behavior was changed.

[Publication provenance](publication-provenance.json) covers four portable original receipts and one path-only derivative. Raw originals, previous checkers and failed records stay local; Git history was not rewritten. Existing 1162-byte composition and 246-byte tagged candidate remain unchanged. The next provider is the genuine call target `0x8520`.
