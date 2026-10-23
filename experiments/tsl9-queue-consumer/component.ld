OUTPUT_ARCH(riscv)
SECTIONS
{
  .queue : ALIGN(2)
  {
    KEEP(*(.text.tsl9_queue_entry_12c58))
    KEEP(*(.text.tsl9_queue_scan_12c86))
    KEEP(*(.text.tsl9_queue_release_12ca6))
    KEEP(*(.text.tsl9_queue_validate_12cb4))
    KEEP(*(.text.tsl9_queue_advance_12cee))
    KEEP(*(.text.tsl9_queue_finish_12cf8))
    KEEP(*(.text.tsl9_queue_zero_12d0e))
    KEEP(*(.text.tsl9_queue_emit_12d42))
    KEEP(*(.text.tsl9_queue_response_12d4c))
    KEEP(*(.text.tsl9_queue_other_12d78))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.queue) == 314, "Original 314B consumer span")
  ASSERT(tsl9_queue_entry_12c58 == 0, "Private frame entry")
  ASSERT(tsl9_queue_scan_12c86 == 46, "Slot scan")
  ASSERT(tsl9_queue_release_12ca6 == 78, "Then-live slot release")
  ASSERT(tsl9_queue_validate_12cb4 == 92, "Dispatch validation")
  ASSERT(tsl9_queue_advance_12cee == 150, "Then-live index advance")
  ASSERT(tsl9_queue_finish_12cf8 == 160, "Frame return")
  ASSERT(tsl9_queue_zero_12d0e == 182, "Cold zero path")
  ASSERT(tsl9_queue_emit_12d42 == 234, "Cold second emission")
  ASSERT(tsl9_queue_response_12d4c == 244, "Cold response path")
  ASSERT(tsl9_queue_other_12d78 == 288, "Other ID path")
}
