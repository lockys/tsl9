OUTPUT_ARCH(riscv)
SECTIONS
{
  .filter : ALIGN(2)
  {
    KEEP(*(.text.tsl9_queue_external_82d2))
    KEEP(*(.text.tsl9_filter_scan_8308))
    KEEP(*(.text.tsl9_filter_pack_8328))
    KEEP(*(.text.tsl9_filter_emit_8358))
    KEEP(*(.text.tsl9_filter_test_836a))
    KEEP(*(.text.tsl9_filter_finish_836e))
    KEEP(*(.text.tsl9_filter_second_838a))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.filter) == 188, "Original 188B filter span")
  ASSERT(tsl9_queue_external_82d2 == 0, "Private frame entry")
  ASSERT(tsl9_filter_scan_8308 == 54, "Routing record scan")
  ASSERT(tsl9_filter_pack_8328 == 86, "Message packaging")
  ASSERT(tsl9_filter_emit_8358 == 134, "Fresh post-provider inputs")
  ASSERT(tsl9_filter_test_836a == 152, "Then-live selector")
  ASSERT(tsl9_filter_finish_836e == 156, "Frame return")
  ASSERT(tsl9_filter_second_838a == 184, "Post-RET cold path")
}
