# Fill provider and tagged-transmit chain

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/fill_provider.c) · [Fill details](../../experiments/tsl9-fill-provider/readme.en.md) · [Three-span link](../../experiments/tsl9-tagged-native-chain/readme.en.md)

Reconstructed168B/55 instructions at `0x8520`, preserving descending byte stores, bulk word stores, computed controls and RA/T0 residues without libc substitution. LLVM swapped two instructions in v1; v2 adds only an ordering constraint. Both sources and measurements remain.

Five genuine C sources were actually compiled and linked: **740 code bytes/260 instructions/58 strong FUNC across three original-PC spans exactly match the original BIN, with zero pending direct symbols or relocations**. The31 computed cases have16 unique destinations. The59,218-byte executable ELF LOAD includes unproved gaps;740 counts only proved code.

Curated source now contains63 C/H files,37 native units,74 C/C++ comparisons and148 objects. All previous72 results and433 artifact hashes remain unchanged. Per language,94 fill controls and264 chain controls passed, together with independent read-only replay.

The fresh resident target/contract at `[0x4004C]` remains unknown; zero UND does not close the runtime environment. **Whole image, physical hardware, IRQ and OTA compatibility remain unproved; no flashable BIN.** Existing1162-byte composition was untouched.

[Summary](summary.json) · [Independent review](independent-review.json) · [Publication provenance](publication-provenance.json). Four portable original receipts remain byte-exact; one public derivative only anonymizes paths. Raw receipts and unselected versions stay local; Git history was not rewritten.
