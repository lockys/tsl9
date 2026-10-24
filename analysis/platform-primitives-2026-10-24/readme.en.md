# CRC, routing and peripheral primitives

[繁體中文](README.md)

The [source](../../src/native/startup/platform_primitives.c) reconstructs six whole original functions:356B/134 instructions,19 private code regions and7 direct controls. Both C11/C++17 objects match original bytes. All six pending providers are real code,with no new data,callbacks,external providers or substitute stubs.

| Original range | Confirmed static behavior |
| --- | --- |
| 9290–92BA | XORs A0 with A1<<8,then performs8 left-shift rounds,conditionally XORing0x1021 according to bit15,and truncates to16 bits each round. This is a CRC16 update step. Caller9334 uses seed0x5AA5 and three updates per input byte:data,running sum and the previous return's low8 bits. It is not an ordinary single-pass CRC over12 bytes. |
| 18604–18630 | Uses a16B frame,calls ROM slot40048 to clear56B at nominal2000C920,then stores3 at offset4. Neighboring self-loop handlers are excluded;this is not identified as clock initialization. |
| 18E1C–18E86 | Four descriptor words supply mask,mode-register offset,trigger offset and a full-u32 enable. Enabling clears mask banks0/4,sets the selected mode,clears edge banks8/12 and selects the trigger offset;16 selects both. Disabling only clears the selected mode mask. All alternatives after RET are retained. |
| 1904A–19076 | Uses address40010000+(A1&252)+8 and shift4*(A1&3). Clears a4-bit field,reads the register again,and ORs the unmasked A0 shifted into it. No new bounds checks are introduced. |
| 196C4–1971E | Preserves control mask0x3040 and ORs the first eight descriptor halfwords;clears bit11 of a secondary halfword;writes descriptor halfword9 at peripheral+16. The18B descriptor is confirmed. No status polling or error return is present. |
| 1971E–1973C | Sets control bit6 for any nonzero full-u32 A1,otherwise clears it. The disable alternative after the first RET and its backward jump to the common store are retained. |

The [contract](provider-contracts.json) and [instructions](evidence.json) retain exact PCs. Composition with the previous17040 caller writes route value2 into line6/7 fields,then uses mask192,mode offset0,trigger offset12 and enable1. The SPI-like descriptor's first eight halfwords OR to0x0314,its ninth is7,and the later call sets control bit6. These are nominal addresses and code behavior;no live registers were read.

SPI/EXTI/AFIO are candidate register-layout interpretations. Actual GPIO pads,external controller models/counts and physical hardware remain unproved. The code is consistent with the [earlier hardware-candidate report](../public-hardware-2026-10-20/README.md);official SDK sources were not re-read this round,and that report is not physical proof for this TSL9 unit.

The main component has23196B code+714B data,1426RELA,1955 nonzero FUNC regions and71 real aliases. C/C++ diagnostic ELFs match. All23910 selected bytes match original coordinates in91 adjacent-only spans. Entry0 and PT_LOAD0 mean this is **not flashable firmware**. Flow checks cover8046 instructions,1264 direct transfers,7460 ordinary next positions and533 call-return positions,without ordinary gaps. Runtime targets for428 register-indirect transfers,10 MRETs and the original EBREAK/vector-data boundary remain unproved.

There are118 C/H files,184 source comparisons and368 objects. The previous117 C/H files,180 comparisons and1081 artifact records are unchanged. Unresolved providers fall from96 to90:86 direct-control providers,three address-only callbacks and one opaque4B default-data provider at1A69C. See the [summary](summary.json) and [next entries](next-providers.json).

A possible feature is a **read-only startup configuration audit** of route fields,interrupt masks/edges and SPI-like controls. It is not implemented;physical mapping,ROM contracts and a suitable diagnostic interface must be established first. No interrupt filtering,timing or control behavior changes are introduced. No firmware,HOST model,ISA emulation or hardware is executed. Complete startup/ROM/RAM/IRQ/OTA compatibility remains unproved. Original build receipts stay local;new public contents receive a separate incremental privacy scan. Historical Git privacy issues remain.
