OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_input_state_decoders_provider_ab08)
  *(.text.tsl9_selector_transitions_block_ab12)
  *(.text.tsl9_selector_transitions_block_ab26)
  *(.text.tsl9_selector_transitions_block_ab2c)
  *(.text.tsl9_selector_transitions_block_ab36)
  *(.text.tsl9_selector_transitions_block_ab3c)
  *(.text.tsl9_selector_transitions_block_ab4c)
  *(.text.tsl9_selector_transitions_block_ab5a)
  *(.text.tsl9_selector_transitions_block_ab5c)
  *(.text.tsl9_input_state_decoders_provider_ab7c)
  *(.text.tsl9_selector_transitions_block_ab90)
  *(.text.tsl9_selector_transitions_block_ab96)
  *(.text.tsl9_selector_transitions_block_ab98)
  *(.text.tsl9_selector_transitions_block_aba0)
  *(.text.tsl9_selector_transitions_block_aba4)
  *(.text.tsl9_selector_transitions_block_aba8)
  *(.text.tsl9_selector_transitions_block_abac)
  *(.text.tsl9_selector_transitions_block_abb6)
  *(.text.tsl9_selector_transitions_block_abc0)
  *(.text.tsl9_input_state_decoders_provider_eca8)
  *(.text.tsl9_selector_transitions_block_ecb6)
  *(.text.tsl9_selector_transitions_block_ecba)
  *(.text.tsl9_selector_transitions_block_ecbc)
  *(.text.tsl9_selector_transitions_block_ecc8)
  *(.text.tsl9_selector_transitions_block_ecd4)
  *(.text.tsl9_selector_transitions_block_ecda)
  *(.text.tsl9_selector_transitions_block_ece2)
  *(.text.tsl9_selector_transitions_block_ecee)
  *(.text.tsl9_selector_transitions_block_ecf2)
  *(.text.tsl9_selector_transitions_block_ecf8)
  *(.text.tsl9_selector_transitions_block_ecfa)
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
 .notification_tables 0 : SUBALIGN(4) {
  *(.rodata.tsl9_selector_notifications_table_1a13c)
  *(.rodata.tsl9_selector_notifications_table_1a150)
  *(.rodata.tsl9_selector_notifications_table_1a1c8)
  *(.rodata.tsl9_selector_notifications_table_1a314)
  *(.rodata.tsl9_selector_notifications_table_1a33c)
 }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
