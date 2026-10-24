# Main initialization and settings loading

[繁體中文](README.md) · [C/C++](../../src/native/startup/main_initializers.c) · [Original instructions](evidence.json) · [Summary](summary.json) · [Encoded-address evidence](storage-regions.json)

Two complete original functions add522B/155 instructions,36 private regions and23 control relocations. Post-first-RET branches are retained.12D92/131C2 now have genuine bodies;six fallback providers and18AB0 are exposed,so real missing providers71→76. No stubs are introduced.

12D92 retains its48B frame,two ROM0x40048 clear-shaped tuples(384B at2000C038,228B at2000C1B8,contiguous to2000C29C),GPIO-shaped setup and a32B stack descriptor. Original clock comparisons120000000/144000000/96000000 select halfwords10/12/8. It passes0x40006400 plus the descriptor to18AB0 and retains the original register-bit1 update.18AB0 is unimplemented; physical CAN/peripheral initialization is not claimed.

131C2 passes six load-shaped tuples through ROM0x4004C. The first checks four bytes at offsets12..15 for32..126; others check the final byte0x5A and call original fallbacks on mismatch. These are code operands,no actual device contents:

| Source operand | RAM destination operand | Length |
| --- | --- | --- |
|0x08077A00|0x2000C29C|112B|
|0x08077900|0x2000C494|256B|
|0x08077800|0x2000C30C|256B|
|0x08077700|0x2000C594|256B|
|0x08077600|0x2000C694|256B|
|0x08077500|0x2000C40C|133B|

The1269B loaded span2000C29C..2000C794 leaves a3B gap2000C491..2000C494,which is not filled. Sources lie outside this APP's nominal VMA8000..1AC00. Actual settings,physical aliases,MCU capacity and BOOT/APP mapping are not established by this file.

114 C/H files and87 code units pass176 comparisons/352 objects including independent pointer data. Previous113 sources and1033 artifact records are preserved. The component has20746B code+714B data;all21460B match the official ID2966 BIN at native original addresses,with76 real providers still missing.

Flow covers7188 instructions,1183 direct transfers(1107 measured/76 reference-only),6636 ordinary next positions without gaps,and448 potential call-return positions.373 register-indirect transfers,10MRET and1EBREAK remain short of a complete CFG or physical proof. Diagnostic ELF entry0/PT_LOAD0 is not flashable.

Next:18AB0 and the six fallbacks,with privacy review before exporting fixed defaults. A proposed offline startup/persistent-region inspector would display clear/load ranges,validation gates,holes and unknown physical mappings. It is not implemented and fills no unknown data or bypasses checks. No target/HOST-model/ISA execution,hardware or network actions occurred. Historical privacy findings keep commit/push held.
