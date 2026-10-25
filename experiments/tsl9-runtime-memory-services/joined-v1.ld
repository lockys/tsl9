OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_services_provider_a37c)
  *(.text.tsl9_main_services_provider_b0ba)
  *(.text.tsl9_main_services_provider_b5e0)
  *(.text.tsl9_main_services_provider_ceaa)
  *(.text.tsl9_main_services_provider_d196)
  *(.text.tsl9_main_services_provider_d4f4)
  *(.text.tsl9_main_services_provider_d75a)
  *(.text.tsl9_main_services_provider_e0a4)
  *(.text.tsl9_main_services_provider_f0b0)
  *(.text.tsl9_main_services_provider_fa50)
  *(.text.tsl9_main_services_provider_fb0c)
  *(.text.tsl9_main_services_provider_ff44)
  *(.text.tsl9_main_services_provider_10158)
  *(.text.tsl9_main_services_provider_10276)
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
 .runtime_service_threshold_window 0 : SUBALIGN(1) { *(.runtime_service_threshold_window) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
