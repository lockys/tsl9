OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_registered_callbacks_provider_838e)
  *(.text.tsl9_callback_completion_block_83c6)
  *(.text.tsl9_callback_completion_block_83d6)
  *(.text.tsl9_callback_completion_block_83e0)
  *(.text.tsl9_callback_completion_block_83ea)
  *(.text.tsl9_callback_completion_block_83f2)
  *(.text.tsl9_callback_completion_block_83f4)
  *(.text.tsl9_callback_completion_block_840c)
  *(.text.tsl9_callback_completion_block_841e)
  *(.text.tsl9_callback_completion_block_8420)
  *(.text.tsl9_callback_completion_block_8424)
  *(.text.tsl9_callback_completion_block_843c)
  *(.text.tsl9_callback_completion_provider_a38e)
  *(.text.tsl9_callback_completion_block_a3a0)
  *(.text.tsl9_callback_completion_block_a3ac)
  *(.text.tsl9_callback_completion_block_a3b0)
  *(.text.tsl9_callback_completion_block_a3b2)
  *(.text.tsl9_callback_completion_block_a3b6)
  *(.text.tsl9_callback_completion_block_a3ba)
  *(.text.tsl9_callback_completion_block_a3bc)
  *(.text.tsl9_callback_completion_block_a3c8)
  *(.text.tsl9_callback_completion_block_a3ca)
  *(.text.tsl9_record_helpers_provider_a3cc)
  *(.text.tsl9_callback_completion_block_a3d6)
  *(.text.tsl9_callback_completion_block_a3e0)
  *(.text.tsl9_callback_completion_block_a3e4)
  *(.text.tsl9_callback_completion_block_a3e8)
  *(.text.tsl9_callback_completion_block_a3ec)
  *(.text.tsl9_callback_completion_block_a3ee)
  *(.text.tsl9_callback_completion_block_a3f0)
  *(.text.tsl9_callback_completion_block_a3fc)
  *(.text.tsl9_callback_completion_block_a3fe)
  *(.text.tsl9_callback_completion_block_a40a)
  *(.text.tsl9_callback_completion_block_a40e)
  *(.text.tsl9_callback_completion_block_a414)
  *(.text.tsl9_callback_completion_block_a430)
  *(.text.tsl9_callback_completion_block_a454)
  *(.text.tsl9_callback_completion_block_a46e)
  *(.text.tsl9_callback_completion_provider_ab5e)
  *(.text.tsl9_callback_completion_provider_10556)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 .action_table 0 : SUBALIGN(4) { *(.action_table) }
 .phase_table 0 : SUBALIGN(4) { *(.phase_table) }
 .resident_version 0 : SUBALIGN(4) { *(.resident_version) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
