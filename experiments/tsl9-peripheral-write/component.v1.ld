OUTPUT_ARCH(riscv)
ENTRY(tsl9_dispatch_external_18ca4)
SECTIONS {
  . = 0x18ca4;
  .peripheral_write : ALIGN(2) { KEEP(*(.text.tsl9_dispatch_external_18ca4)) }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.peripheral_write) == 212, "Complete original212B including cold blocks")
}
