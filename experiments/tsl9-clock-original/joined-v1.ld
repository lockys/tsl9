OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_provider_18834)
  *(.text.tsl9_clock_original_block_18842)
  *(.text.tsl9_clock_original_block_18848)
  *(.text.tsl9_clock_original_block_18850)
  *(.text.tsl9_clock_original_block_18878)
  *(.text.tsl9_clock_original_block_18882)
  *(.text.tsl9_clock_original_block_18896)
  *(.text.tsl9_clock_original_block_18898)
  *(.text.tsl9_clock_original_block_1889a)
  *(.text.tsl9_clock_original_block_188a6)
  *(.text.tsl9_clock_original_block_188b0)
  *(.text.tsl9_clock_original_block_188c0)
  *(.text.tsl9_clock_original_block_188c8)
  *(.text.tsl9_clock_original_block_188ce)
  *(.text.tsl9_clock_original_block_188d8)
  *(.text.tsl9_main_provider_1973c)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
