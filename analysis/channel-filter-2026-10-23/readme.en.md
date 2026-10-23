# Channel and CAN filter reconstruction

[繁體中文](README.md)

Five new C units are curated under `src/native/receive/`. Both C11 and C++17 reproduce all1242B/445 instructions in six original-PC code spans. Composition with the prior receive/dispatch graph yields3166B/1104 instructions.

This remains partial evidence.14D2E is unresolved;17 opaque resident transfers and two internal computed controls remain. The nominal ELF includes67098B of unproved gaps. Physical hardware, startup, installed ROM ABI, memory, interrupts and OTA are unproved. No flashable reconstructed BIN is claimed.

- [Source, reproduction and findings](../../experiments/tsl9-channel-route/readme.en.md)
- [Actual summary and scope](summary.json)
- [1912B dispatch frontier with at least71 external direct targets](../feature-dispatch-frontier-2026-10-23/readme.en.md)
- [Original/public receipt provenance](publication-provenance.json)
- [Independent review and v1 corrections](independent-review.json)

V2 passes5903 negative controls per language. Frozen v1 code and receipts remain. Independent review exposed missing-RELA and detached-SHDR/LOAD gate gaps; v2 adds rejection checks. Actual baseline machine artifacts are unchanged. Historical receipts are not rewritten.

A proposed feature is a strictly offline filter-request inspector comparing ID truncation and channel/backend differences. It is not implemented; configuration routines are not read-only hardware diagnostics.
