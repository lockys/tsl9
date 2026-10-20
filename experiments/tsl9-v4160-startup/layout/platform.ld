OUTPUT_ARCH(riscv)
ENTRY(tsl9v4160_reset)
SECTIONS {
  .text.reset 0x186AA : { KEEP(*(.text.tsl9v4160.reset)) }
  .text.clock 0x1874A : { KEEP(*(.text.tsl9v4160.clock)) }
  .rodata.initializer 0x1AB60 : { KEEP(*(.rodata.tsl9v4160.initializer)) }
  .bss.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) }
  /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
ASSERT(SIZEOF(.text.reset)==138, "reset changed")
ASSERT(SIZEOF(.text.clock)==234, "clock changed")
ASSERT(SIZEOF(.rodata.initializer)==128, "initializer changed")
ASSERT(SIZEOF(.bss.ram)==35160, "RAM carrier changed")
