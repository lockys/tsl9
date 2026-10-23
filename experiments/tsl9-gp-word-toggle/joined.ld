OUTPUT_ARCH(riscv)
SECTIONS {
  .full_plus_leaf : ALIGN(2) {
    KEEP(*(.full))
    KEEP(*(.text.tsl9_queue_external_9b36))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.full_plus_leaf) == 1926, "Genuine1902 plus24 bytes")
  ASSERT(tsl9_queue_external_9b36 == 1902, "Genuine new provider after all original code")
}
