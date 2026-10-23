OUTPUT_ARCH(riscv)
ENTRY(tsl9_queue_external_9b36)
SECTIONS {
  .toggle 0x9B36 : ALIGN(2) { KEEP(*(.text.tsl9_queue_external_9b36)) }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.toggle) == 24, "Original24B leaf")
  ASSERT(tsl9_queue_external_9b36 == 0x9B36, "Original leaf address")
}
