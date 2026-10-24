OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_provider_9a42)
  *(.text.tsl9_irq_initializer_block_9a62)
  *(.text.tsl9_irq_initializer_block_9a6e)
  *(.text.tsl9_irq_initializer_block_9a78)
  *(.text.tsl9_irq_initializer_block_9a82)
  *(.text.tsl9_irq_initializer_block_9a8c)
  *(.text.tsl9_irq_initializer_block_9a96)
  *(.text.tsl9_irq_init_helper_19124)
  *(.text.tsl9_irq_initializer_block_19126)
  *(.text.tsl9_irq_initializer_block_19132)
  *(.text.tsl9_irq_init_helper_19142)
  *(.text.tsl9_irq_initializer_block_19144)
  *(.text.tsl9_irq_initializer_block_19150)
  *(.text.tsl9_irq_init_helper_19160)
  *(.text.tsl9_irq_initializer_block_19162)
  *(.text.tsl9_irq_initializer_block_1916e)
  *(.text.tsl9_irq_init_helper_1917e)
  *(.text.tsl9_irq_initializer_block_19180)
  *(.text.tsl9_irq_initializer_block_1918c)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
