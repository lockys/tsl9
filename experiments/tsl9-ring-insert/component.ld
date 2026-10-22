OUTPUT_ARCH(riscv)
ENTRY(tsl9_ring_insert_entry_12bc8)
SECTIONS
{
  .ring 0x12BC8 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_ring_insert_entry_12bc8))
    KEEP(*(.text.tsl9_ring_init_12bd0))
    KEEP(*(.text.tsl9_ring_scan_12be0))
    KEEP(*(.text.tsl9_ring_finish_12c12))
    KEEP(*(.text.tsl9_ring_advance_12c1c))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.ring) == 92, "Original ring92B")
  ASSERT(tsl9_ring_insert_entry_12bc8 == 0x12BC8, "Ring entry")
  ASSERT(tsl9_ring_init_12bd0 == 0x12BD0, "Ring initialization")
  ASSERT(tsl9_ring_scan_12be0 == 0x12BE0, "Ring scan")
  ASSERT(tsl9_ring_finish_12c12 == 0x12C12, "Ring fresh restore")
  ASSERT(tsl9_ring_advance_12c1c == 0x12C1C, "Ring cold tail")
}
