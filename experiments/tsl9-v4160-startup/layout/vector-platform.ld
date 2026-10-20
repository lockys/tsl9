OUTPUT_ARCH(riscv)
ENTRY(__tsl9v4160_image_entry)
SECTIONS {
  .text.tsl9v4160.image_entry 0x8000 : { KEEP(*(.text.tsl9v4160.image_entry)) }
  ASSERT(SIZEOF(.text.tsl9v4160.image_entry)==4, "section size changed")
  .rodata.tsl9v4160.vector_capture 0x8038 : { KEEP(*(.rodata.tsl9v4160.vector_capture)) }
  ASSERT(SIZEOF(.rodata.tsl9v4160.vector_capture)==328, "section size changed")
  .text.tsl9v4160.handler_8448 0x8448 : { KEEP(*(.text.tsl9v4160.handler_8448)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_8448)==78, "section size changed")
  .text.tsl9v4160.handler_8498 0x8498 : { KEEP(*(.text.tsl9v4160.handler_8498)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_8498)==134, "section size changed")
  .text.tsl9v4160.handler_979e 0x979e : { KEEP(*(.text.tsl9v4160.handler_979e)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_979e)==442, "section size changed")
  .text.tsl9v4160.handler_12c24 0x12c24 : { KEEP(*(.text.tsl9v4160.handler_12c24)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_12c24)==52, "section size changed")
  .text.tsl9v4160.handler_16fb6 0x16fb6 : { KEEP(*(.text.tsl9v4160.handler_16fb6)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_16fb6)==76, "section size changed")
  .text.tsl9v4160.vector_loop_pool 0x18638 : { KEEP(*(.text.tsl9v4160.vector_loop_pool)) }
  ASSERT(SIZEOF(.text.tsl9v4160.vector_loop_pool)==114, "section size changed")
  .text.reset 0x186aa : { KEEP(*(.text.tsl9v4160.reset)) }
  ASSERT(SIZEOF(.text.reset)==138, "section size changed")
  .text.tsl9v4160.stub_18734 0x18734 : { KEEP(*(.text.tsl9v4160.stub_18734)) }
  ASSERT(SIZEOF(.text.tsl9v4160.stub_18734)==4, "section size changed")
  .text.tsl9v4160.stub_18738 0x18738 : { KEEP(*(.text.tsl9v4160.stub_18738)) }
  ASSERT(SIZEOF(.text.tsl9v4160.stub_18738)==4, "section size changed")
  .text.tsl9v4160.stub_1873c 0x1873c : { KEEP(*(.text.tsl9v4160.stub_1873c)) }
  ASSERT(SIZEOF(.text.tsl9v4160.stub_1873c)==2, "section size changed")
  .text.tsl9v4160.stub_1873e 0x1873e : { KEEP(*(.text.tsl9v4160.stub_1873e)) }
  ASSERT(SIZEOF(.text.tsl9v4160.stub_1873e)==12, "section size changed")
  .text.clock 0x1874a : { KEEP(*(.text.tsl9v4160.clock)) }
  ASSERT(SIZEOF(.text.clock)==234, "section size changed")
  .text.tsl9v4160.handler_19bd4 0x19bd4 : { KEEP(*(.text.tsl9v4160.handler_19bd4)) }
  ASSERT(SIZEOF(.text.tsl9v4160.handler_19bd4)==28, "section size changed")
  .rodata.initializer 0x1ab60 : { KEEP(*(.rodata.tsl9v4160.initializer)) }
  ASSERT(SIZEOF(.rodata.initializer)==128, "section size changed")
  .bss.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) }
  ASSERT(SIZEOF(.bss.ram)==35160, "section size changed")
  /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
ASSERT((__tsl9v4160_ram0_address & 0xfff)==0, "RAM0 address alignment")
