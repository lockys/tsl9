# Record decoding and state controls

[繁體中文](README.md) · [Source](../../src/native/receive/record_state_controls.c) · [Contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct17 connected complete functions:1,322B/441 instructions,including four10-bit field decoding/packing,selector priority,conditional notifications,two input formats,scheduled callbacks and explicit ROM-table ports. Preserve original volatile order,register roles,indirect tails and private assembly interfaces.

Decoded fields cache at GP+244/246/248/250. The changed path updates all four,then packs GP+252/256 while preserving the second word upper24 bits. Selector priority:b4.bit6→71,b4.bit7→72,b5.bit0→73,b5.bit1→74;otherwise70. These are bit-level facts,not feature names or physical units.

224 comparisons/448 objects pass;50,396 original-coordinate bytes match,65.62% byte coverage. Twelve imports resolve and seven downstream providers are exposed;126 remain. Four callback addresses bind to real reconstructed code;all seven existing guarded tables are rechecked.

Confirmed:bytes,masks,static address arithmetic and call order. Inferred:record/state updates support notification chains. Unknown:seat or button attribution,units,ROM/RAM mapping,private ABI,IRQ and OTA. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness.
