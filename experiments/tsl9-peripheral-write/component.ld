OUTPUT_ARCH(riscv)
ENTRY(tsl9_dispatch_external_18ca4)
SECTIONS {
  . = 0x18ca4;
  .peripheral_write : ALIGN(2) {
    KEEP(*(.text.tsl9_dispatch_external_18ca4))
    KEEP(*(.text.tsl9_peripheral_selected_18cc6))
    KEEP(*(.text.tsl9_peripheral_metadata_18cec))
    KEEP(*(.text.tsl9_peripheral_finish_18d5a))
    KEEP(*(.text.tsl9_peripheral_select0_18d5e))
    KEEP(*(.text.tsl9_peripheral_select1_18d62))
    KEEP(*(.text.tsl9_peripheral_alternate_18d66))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(tsl9_dispatch_external_18ca4 == 0x18ca4, "Original region 0")
  ASSERT(tsl9_peripheral_selected_18cc6 == 0x18cc6, "Original region 34")
  ASSERT(tsl9_peripheral_metadata_18cec == 0x18cec, "Original region 72")
  ASSERT(tsl9_peripheral_finish_18d5a == 0x18d5a, "Original region 182")
  ASSERT(tsl9_peripheral_select0_18d5e == 0x18d5e, "Original region 186")
  ASSERT(tsl9_peripheral_select1_18d62 == 0x18d62, "Original region 190")
  ASSERT(tsl9_peripheral_alternate_18d66 == 0x18d66, "Original region 194")
  ASSERT(SIZEOF(.peripheral_write) == 212, "Complete original212B including cold blocks")
}
