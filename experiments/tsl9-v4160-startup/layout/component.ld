OUTPUT_ARCH(riscv)
ENTRY(tsl9v4160_reset)
SECTIONS {
  .text.reset 0x186AA : { KEEP(*(.text.tsl9v4160.reset)) }
  .rodata.initializer 0x1AB60 : { KEEP(*(.rodata.tsl9v4160.initializer)) }
  .bss.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) }
  /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
ASSERT(SIZEOF(.text.reset)==138, "reset range changed")
ASSERT(SIZEOF(.rodata.initializer)==128, "initializer range changed")
ASSERT(SIZEOF(.bss.ram)==35160, "RAM carrier changed")
