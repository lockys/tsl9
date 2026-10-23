# GP guard / word-XOR leaf

[繁體中文](README.md)

Readable C reconstructs the original `0x9B36–0x9B4E` leaf: **24 bytes / 7 instructions**, identical byte-for-byte when compiled as C11 and C++17. The selected source is [`src/native/receive/gp_word_toggle.c`](../../src/native/receive/gp_word_toggle.c). This is a local architectural contract, not flashable firmware.

- `9B36 LBU` reads an unsigned byte at then-live GP+168. `9B3A BNEZ` skips to `9B4C`, preserving entry A4 and retaining the guard byte in A5.
- The zero path sets A5=`0x40011000`; `9B40 LW`, `9B44 XORI 2`, and `9B48 SW` perform a 32-bit read/XOR/write at `0x4001080C`.
- Only A4/A5 are written. `9B4C RET` uses RA with bit0 cleared. There is no frame, call, CSR access, interrupt masking, atomicity, or fault recovery guarantee.
- Original JAL at `0x12D1C` calls this leaf and sets RA=`0x12D20`. The caller's A0=0 is ignored by the leaf.

The physical peripheral and purpose remain unknown. No LED/buzzer identity or installed memory validity is inferred.

The actual partial link is **1926B / 669 instructions / 108 strong FUNC / 97 pending RELA / 3 UND**. A genuine compiled C definition replaces the 9B36 undefined symbol without an ABS substitute. Remaining direct providers: `9454`, `12ABE`, `14D2E`. All97 original typed destinations and nonrelocation bits are checked; diagnostic ET_REL control displacements remain pending. The previous 1588B nominal-address graph is unchanged; the separate leaf is not counted as an enlarged closed graph.

Version3 passes1991 static negative controls per language. Independent review exposed six UND/IR escapes in earlier gates; all12 language-specific retests reject them. The complete IR-body hash checks a fixed compiler product, not arbitrary SSA correctness. Earlier checkers, receipts, and the failed26B early-return trial remain available.

Curation now has65 C/H files and39 native units. All78 origin/curated comparisons and156 objects pass; the earlier76 result facts and old artifact identities are unchanged. Integration binds13 current source units and their actual dependency/object records directly. It does not claim replay of an older global-manifest receipt against changed source inventory.

[Provenance](publication-provenance.json) identifies four exact portable original receipts and one path-only derivative of the curation receipt. Raw originals are retained in a local private ZIP. BIN/APK bytes are unchanged.

The chip, installed ROM, full startup/memory ownership/interrupts and Bluetooth OTA compatibility remain unproved. No firmware BIN is generated and no target/hardware is executed. A possible future addition is a diagnostic distinction between guard-skip and actual-write states using existing authorized observations; no physical observation source exists yet and this feature is not implemented.

[Reproduction](../../experiments/tsl9-gp-word-toggle/README.md) · [Independent review](independent-review.json) · [Summary](summary.json)
