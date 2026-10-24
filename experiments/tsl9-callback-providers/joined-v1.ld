OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2)
 {
  *(.boot_code)
  *(.text.tsl9_callback_provider_entry_b0d0)
  *(.text.tsl9_callback_provider_block_b0d8)
  *(.text.tsl9_callback_provider_block_b0e2)
  *(.text.tsl9_callback_provider_block_b0ea)
  *(.text.tsl9_callback_provider_block_b0f0)
  *(.text.tsl9_callback_provider_block_b0f6)
  *(.text.tsl9_callback_provider_block_b0fa)
  *(.text.tsl9_callback_provider_entry_b0fc)
  *(.text.tsl9_callback_provider_block_b116)
  *(.text.tsl9_callback_provider_block_b132)
  *(.text.tsl9_callback_provider_entry_d272)
  *(.text.tsl9_callback_provider_entry_10630)
  *(.text.tsl9_callback_provider_block_10698)
  *(.text.tsl9_callback_provider_entry_12b24)
  *(.text.tsl9_callback_provider_block_12b30)
  *(.text.tsl9_callback_provider_block_12b34)
  *(.text.tsl9_callback_provider_block_12b3a)
  *(.text.tsl9_callback_provider_block_12b40)
  *(.text.tsl9_callback_provider_block_12b46)
  *(.text.tsl9_callback_provider_block_12b58)
  *(.text.tsl9_callback_provider_block_12b6a)
  *(.text.tsl9_callback_provider_block_12b7a)
  *(.text.tsl9_callback_provider_block_12b82)
  *(.text.tsl9_callback_provider_block_12b86)
  *(.text.tsl9_callback_provider_block_12b8c)
  *(.text.tsl9_callback_provider_block_12b92)
  *(.text.tsl9_callback_provider_block_12b94)
  *(.text.tsl9_callback_provider_block_12b98)
  *(.text.tsl9_callback_provider_block_12ba0)
  *(.text.tsl9_callback_provider_block_12ba6)
  *(.text.tsl9_callback_provider_block_12ba8)
  *(.text.tsl9_callback_provider_block_12bae)
  *(.text.tsl9_callback_provider_block_12bb2)
  *(.text.tsl9_callback_provider_block_12bc2)
  *(.text.tsl9_callback_provider_entry_13d48)
  *(.text.tsl9_callback_provider_block_13d50)
  *(.text.tsl9_callback_provider_block_13d68)
  *(.text.tsl9_callback_provider_block_13d72)
  *(.text.tsl9_callback_provider_block_13d7e)
  *(.text.tsl9_callback_provider_block_13d88)
  *(.text.tsl9_callback_provider_block_13d8a)
  *(.text.tsl9_callback_provider_block_13d90)
  *(.text.tsl9_callback_provider_block_13da2)
  *(.text.tsl9_callback_provider_block_13da6)
  *(.text.tsl9_callback_provider_block_13db8)
  *(.text.tsl9_callback_provider_block_13dc6)
  *(.text.tsl9_callback_provider_block_13dce)
 }
 .initializer 0 : { *(.initializer) }
 .vectors 0 : { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) {
  *(.rodata.tsl9_callback_provider_relative_table_1a680)
  *(.rodata.tsl9_callback_provider_templates_1a4f4)
 }
 tsl9_callback_external_d272 = tsl9_callback_provider_entry_d272;
 tsl9_callback_external_b0fc = tsl9_callback_provider_entry_b0fc;
 tsl9_callback_external_12b24 = tsl9_callback_provider_entry_12b24;
 tsl9_callback_external_13d48 = tsl9_callback_provider_entry_13d48;
 tsl9_callback_external_10630 = tsl9_callback_provider_entry_10630;
 tsl9_callback_provider_external_128fe = tsl9_channel_external_128fe;
 tsl9_callback_provider_external_12a08 = tsl9_queue_external_12a08;
 tsl9_callback_provider_external_12abe = tsl9_queue_external_12abe;
 tsl9_callback_provider_external_81b0 = tsl9_channel_external_81b0;
 tsl9_callback_provider_external_9124 = tsl9_callback_external_9124;
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
