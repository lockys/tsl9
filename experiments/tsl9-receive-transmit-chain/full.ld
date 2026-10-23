OUTPUT_ARCH(riscv)
SECTIONS {
  .full : ALIGN(2) { KEEP(*(.text.*)) }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.full) == 1902, "Full genuine component including unresolved queue")
}
