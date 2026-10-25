OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_selector_notifications_provider_b664)
  *(.text.tsl9_selector_notifications_provider_b6a8)
  *(.text.tsl9_record_dispatch_provider_cc60)
  *(.text.tsl9_selector_notifications_provider_ccc2)
  *(.text.tsl9_notification_support_block_cccc)
  *(.text.tsl9_notification_support_block_ccd6)
  *(.text.tsl9_notification_support_block_cce2)
  *(.text.tsl9_notification_support_block_ccec)
  *(.text.tsl9_notification_support_block_ccf4)
  *(.text.tsl9_selector_notifications_provider_ccf6)
  *(.text.tsl9_notification_support_block_ccfe)
  *(.text.tsl9_notification_support_block_cd00)
  *(.text.tsl9_notification_support_block_cd14)
  *(.text.tsl9_notification_support_block_cd24)
  *(.text.tsl9_notification_support_block_cd38)
  *(.text.tsl9_notification_support_block_cd3e)
  *(.text.tsl9_record_dispatch_provider_fe08)
  *(.text.tsl9_notification_support_block_fe10)
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
