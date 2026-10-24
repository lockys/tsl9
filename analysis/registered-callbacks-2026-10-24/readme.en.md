# Registered callbacks: static C/C++ reconstruction

[繁體中文](README.md)

Three complete functions at `11442..114E2`, `119C8..12506` and `16F00..16FB6` add 3,220 bytes / 1,032 instructions to [src](../../src/native/receive/registered_callbacks.c). C11 and C++17 object checks pass. Neighbouring helpers and the IRQ starting at 16FB6 are excluded.

- **Confirmed:** 11442 selects flags in order 2,1,16,8,4; 16F00 selects 2,4,1 and increments two byte counters modulo256 before comparing with2. See address-level [contracts](provider-contracts.json) and original [instructions](evidence.json).
- **Inference:** 119C8 has a message-like receive/dispatch/release path through ROM slots4006C/4012C/40068. Vendor API names, flag meanings and time units remain unproved. The saved A1 mask is not assumed to be uint16.
- **Unresolved:** seventeen static pool addresses have no supplied payload. Address9508 is unclassified. Three old callback imports resolve, while28 further dependencies are exposed;115 genuine undefined providers remain. [Inventory](next-providers.json).

The complete source proof covers119 C/H files,186 comparisons and372 objects; all previous118 C/H files and1093 artifact records are preserved. The standalone object has613 sections: new [reader v4](../../experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py) changes only the section ceiling from512 to1024; an independent parser agrees on both language objects. The old reader and curation checker remain unchanged.

The integrated component has26,416B code +714B data,1,726 relocations and115 genuine imports. All27,130 selected bytes match the original at nominal addresses in a **non-loadable diagnostic ELF**. Static flow checks cover9,078 instructions,1,528 direct transfers and594 call-return positions with no ordinary continuation gaps.465 indirect transfers and10 MRET targets remain unproved; the original EBREAK/vector boundary is retained. [Machine summary](summary.json).

No firmware, host model or ISA was executed; no hardware, BLE/CAN/Flash or vendor network was accessed. No BIN is produced. Physical MCU, installed ROM, memory ownership, full startup/IRQ and OTA compatibility remain unproved; this is not a flashable firmware claim.
