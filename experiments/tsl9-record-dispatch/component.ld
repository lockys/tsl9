OUTPUT_ARCH(riscv)
SECTIONS {
  .record_dispatch : ALIGN(2) {
    KEEP(*(.text.tsl9_queue_external_12a08))
    KEEP(*(.text.tsl9_dispatch_status_12a14))
    KEEP(*(.text.tsl9_dispatch_ID_12a16))
    KEEP(*(.text.tsl9_dispatch_query_12a20))
    KEEP(*(.text.tsl9_dispatch_tag_12a28))
    KEEP(*(.text.tsl9_dispatch_copy_12a2e))
    KEEP(*(.text.tsl9_dispatch_peripheral_12a50))
    KEEP(*(.text.tsl9_dispatch_finish_12a5e))
    KEEP(*(.text.tsl9_dispatch_tagged_12a66))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.record_dispatch) == 102, "Original102B record dispatch")
  ASSERT(tsl9_queue_external_12a08 == 0, "Private dispatcher frame")
  ASSERT(tsl9_dispatch_status_12a14 == 12, "Then-live status")
  ASSERT(tsl9_dispatch_ID_12a16 == 14, "Identifier read")
  ASSERT(tsl9_dispatch_query_12a20 == 24, "Query provider")
  ASSERT(tsl9_dispatch_tag_12a28 == 32, "Tag selection")
  ASSERT(tsl9_dispatch_copy_12a2e == 38, "Fresh indirect copy")
  ASSERT(tsl9_dispatch_peripheral_12a50 == 72, "Peripheral provider")
  ASSERT(tsl9_dispatch_finish_12a5e == 86, "Frame return")
  ASSERT(tsl9_dispatch_tagged_12a66 == 94, "Post-RET tagged path")
}
