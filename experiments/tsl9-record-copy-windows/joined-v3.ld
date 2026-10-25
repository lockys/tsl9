SECTIONS {
 .boot_code 0 : SUBALIGN(2) { *(.boot_code) }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 .action_table 0 : SUBALIGN(4) { *(.action_table) }
 .phase_table 0 : SUBALIGN(4) { *(.phase_table) }
 .resident_version 0 : SUBALIGN(4) { *(.resident_version) }
 .selector_tables 0 : SUBALIGN(1) { *(.selector_tables) }
 .notification_tables 0 : SUBALIGN(4) { *(.notification_tables) }
 .runtime_service_threshold_window 0 : SUBALIGN(1) { *(.runtime_service_threshold_window) }
 .record_field_window_19ea8 0 : SUBALIGN(1) { *(.record_field_window_19ea8) }
 .record_field_window_19eb8 0 : SUBALIGN(1) { *(.record_field_window_19eb8) }
 .record_field_window_19ec8 0 : SUBALIGN(1) { *(.record_field_window_19ec8) }
 .record_field_window_1a0d8 0 : SUBALIGN(1) { *(.record_field_window_1a0d8) }
 .record_dispatch_data_19e08 0 : SUBALIGN(4) { *(.record_dispatch_data_19e08) }
 .record_dispatch_data_19e50 0 : SUBALIGN(4) { *(.record_dispatch_data_19e50) }
 .record_dispatch_data_19e7c 0 : SUBALIGN(4) { *(.record_dispatch_data_19e7c) }
 .record_dispatch_data_1a0dc 0 : SUBALIGN(4) { *(.record_dispatch_data_1a0dc) }
 .record_dispatch_data_1ab50 0 : SUBALIGN(1) { *(.record_dispatch_data_1ab50) }
 .record_copy_data_19d08 0 : SUBALIGN(4) { *(.rodata.tsl9_record_field_helpers_static_data_19d08) }
 .record_copy_data_19d68 0 : SUBALIGN(4) { *(.rodata.tsl9_record_field_helpers_static_data_19d68) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
