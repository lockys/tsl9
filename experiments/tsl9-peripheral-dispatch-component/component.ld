OUTPUT_ARCH(riscv)
SECTIONS {
  .peripheral_dispatch_component : ALIGN(2) {
    KEEP(*(.record_dispatch_component))
    KEEP(*(.text.tsl9_dispatch_external_18ca4))
    KEEP(*(.text.tsl9_peripheral_selected_18cc6))
    KEEP(*(.text.tsl9_peripheral_metadata_18cec))
    KEEP(*(.text.tsl9_peripheral_finish_18d5a))
    KEEP(*(.text.tsl9_peripheral_select0_18d5e))
    KEEP(*(.text.tsl9_peripheral_select1_18d62))
    KEEP(*(.text.tsl9_peripheral_alternate_18d66))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(tsl9_queue_entry_12c58 == 0, "Complete prior950B dispatch retained")
  ASSERT(tsl9_dispatch_external_18ca4 == 950, "Genuine provider region0")
  ASSERT(tsl9_peripheral_selected_18cc6 == 984, "Genuine provider region1")
  ASSERT(tsl9_peripheral_metadata_18cec == 1022, "Genuine provider region2")
  ASSERT(tsl9_peripheral_finish_18d5a == 1132, "Genuine provider region3")
  ASSERT(tsl9_peripheral_select0_18d5e == 1136, "Genuine provider region4")
  ASSERT(tsl9_peripheral_select1_18d62 == 1140, "Genuine provider region5")
  ASSERT(tsl9_peripheral_alternate_18d66 == 1144, "Genuine provider region6")
  ASSERT(SIZEOF(.peripheral_dispatch_component) == 1162, "All950 plus212 genuine bytes")
}
