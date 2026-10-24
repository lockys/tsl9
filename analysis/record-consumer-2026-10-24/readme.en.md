# Record consumers and genuine provider linkage

[繁體中文](README.md)

Added [record_consumer.c](../../src/native/receive/record_consumer.c): original C776–C7E8,114B/42 instructions/11 architectural regions. In both C11 and C++17,94 noncontrol bytes and7 typed references reproduce every original byte after static original-VA encoding.

| Checked scope | Evidence and limits |
| --- | --- |
| C776/C798/C7AA | Separate16B copy frame, frameless clear tail and conditional32B completion frame; GP+220 scratch remains distinct from literal object2000C290 |
| 82A8–82D2 | Reuses42B/16 instructions/4 genuine compiled regions from existing state access; all fall-through regions retained |
| 12A08–12A6E | Reuses the entire102B/35 instructions/9-region dispatcher with four explicit downstream dependencies |
| Main component | 4424B code+456B data,371 nonzero FUNC regions,18 real entry aliases,299 RELA and22 UND; identical C/C++ component hashes |

The previous4166B code and456B data are unchanged. Genuine code binds the old C776 dependency. Expanding this call chain exposes C6A8,FAF8 and four dispatcher children; UND increases from17 to22. No executable stub or ABS provider substitutes for missing code. All62 selected nonzero vector bindings remain.

C7AA writes status before deciding whether to establish a frame; fresh post-call pointer/byte/stack-record reads remain. Its mask is4; evidence does not establish seat or do-not-disturb semantics.

Use the replay commands in the [experiment](../../experiments/tsl9-record-consumer/readme.en.md). [Summary](summary.json), [pending providers](pending-providers.json), [next disassembly](next-providers.json), [publication provenance](publication-provenance.json).

Next: reconstruct the206B C6A8 record parser/dispatcher and6B FAF8 status setter. An offline seven-byte record preview and passive dispatch counters are possible feature candidates, not implemented features.

**This unresolved VMA-zero ET_REL is not a flashable BIN.** Physical MCU, installed ROM/ABI, original placement, full memory/IRQ and BLE OTA compatibility remain unproved. No target, HOST model or ISA execution, hardware access, commit or push occurred. Historical personal information remains unresolved.
