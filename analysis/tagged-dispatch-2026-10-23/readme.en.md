# Tagged-transmit reconstruction

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/tagged_dispatch.c) · [Detailed flow and limits](../../experiments/tsl9-tagged-dispatch/readme.en.md)

Official range `0x16B7C–0x16C72` was reconstructed as private C/C++ architectural regions: 246 bytes, 86 instructions, tag checks, a 64-byte frame, record packing, busy handling and status return. Both languages passed actual compilation, 132 negative controls and read-only replay. Eleven control relocations, four external providers and ROM identity remain unresolved. The candidate has not joined the existing 1162-byte composition.

Curated `src/` now contains 61 C/H files, 35 native units, 70 C/C++ comparisons and 140 objects. This is static evidence; **reverse engineering remains incomplete and no flashable firmware was produced**.

[Summary](summary.json) separates facts, inference and gaps. [Publication provenance](publication-provenance.json) preserves two portable receipts byte-for-byte and one path-only derivative. Original receipts and failed-build records remain local; Git history was not rewritten. The existing 816 anonymized derivatives also passed residual-field checks.
