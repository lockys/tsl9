OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_feature_state_records_provider_ebac)
  *(.text.tsl9_selector_storage_block_ebbe)
  *(.text.tsl9_selector_storage_block_ebc0)
  *(.text.tsl9_selector_storage_block_ebc6)
  *(.text.tsl9_selector_storage_block_ebce)
  *(.text.tsl9_selector_storage_block_ebd6)
  *(.text.tsl9_selector_storage_block_ebe4)
  *(.text.tsl9_selector_storage_block_ebec)
  *(.text.tsl9_selector_storage_block_ebee)
  *(.text.tsl9_selector_storage_block_ebf6)
  *(.text.tsl9_selector_storage_block_ec12)
  *(.text.tsl9_selector_storage_block_ec16)
  *(.text.tsl9_selector_storage_block_ec1a)
  *(.text.tsl9_selector_storage_block_ec22)
  *(.text.tsl9_selector_storage_block_ec24)
  *(.text.tsl9_selector_storage_block_ec28)
  *(.text.tsl9_selector_storage_block_ec34)
  *(.text.tsl9_selector_storage_block_ec40)
  *(.text.tsl9_selector_storage_block_ec4a)
  *(.text.tsl9_selector_storage_block_ec50)
  *(.text.tsl9_selector_storage_block_ec58)
  *(.text.tsl9_selector_storage_block_ec5c)
  *(.text.tsl9_selector_storage_block_ec68)
  *(.text.tsl9_selector_storage_block_ec78)
  *(.text.tsl9_selector_storage_block_ec82)
  *(.text.tsl9_selector_storage_block_ec90)
  *(.text.tsl9_selector_storage_block_ec94)
  *(.text.tsl9_selector_storage_block_eca2)
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
 .selector_tables 0 : SUBALIGN(1) {
  *(.rodata.tsl9_feature_state_records_static_data_1a4e4)
  *(.rodata.tsl9_feature_state_records_static_data_1a518)
  *(.rodata.tsl9_feature_state_records_static_data_1a528)
  *(.rodata.tsl9_feature_state_records_static_data_1a538)
 }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
