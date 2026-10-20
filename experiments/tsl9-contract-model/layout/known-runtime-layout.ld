/* Known V4.1.00 code/RO only. No identity values, ROM/data providers or unknown-gap fill.
 * ld -r ADDR assertions do not serialize final VMA/LMA: ET_REL sh_addr stays0. */
SECTIONS {
 .tsl9_code_00008000 0x8000 : {
  KEEP(*(.text.tsl9_image_entry))
 }
 .tsl9_ro_00008038 0x8038 : {
  KEEP(*(.tsl9_vectors))
 }
 .tsl9_code_00008180 0x8180 : {
  KEEP(*(.text.tsl9_entry_main_8180))
 }
 .tsl9_code_000081aa 0x81aa : {
  KEEP(*(.text.tsl9_rf_flag_81aa))
 }
 .tsl9_code_000081b0 0x81b0 : {
  KEEP(*(.text.tsl9_periph_clock_81b0))
 }
 .tsl9_code_00008202 0x8202 : {
  KEEP(*(.text.tsl9_runtime_unported_8202))
 }
 .tsl9_code_00008214 0x8214 : {
  KEEP(*(.text.tsl9_tx_gate_8214))
 }
 .tsl9_code_00008282 0x8282 : {
  KEEP(*(.text.tsl9_control_limit_8282))
 }
 .tsl9_code_00008294 0x8294 : {
  KEEP(*(.text.tsl9_dispatch_mode_8294))
 }
 .tsl9_code_0000829e 0x829e : {
  KEEP(*(.text.tsl9_runtime_unported_829e))
 }
 .tsl9_code_000082c8 0x82c8 : {
  KEEP(*(.text.tsl9_runtime_unported_82c8))
 }
 .tsl9_code_00008386 0x8386 : {
  KEEP(*(.text.tsl9_runtime_unported_8386))
 }
 .tsl9_code_0000843a 0x843a : {
  KEEP(*(.text.tsl9_rf_enabled_843a))
 }
 .tsl9_code_00008440 0x8440 : {
  KEEP(*(.text.tsl9_context_restore_irq))
 }
 .tsl9_code_00008490 0x8490 : {
  KEEP(*(.text.tsl9_ble_lle))
 }
 .tsl9_code_00008518 0x8518 : {
  KEEP(*(.text.tsl9_tx_memset_8518))
 }
 .tsl9_code_000085c0 0x85c0 : {
  KEEP(*(.text.tsl9_ble_param_85c0))
 }
 .tsl9_code_000085e2 0x85e2 : {
  KEEP(*(.text.tsl9_runtime_unported_85e2))
 }
 .tsl9_code_00008cfa 0x8cfa : {
  KEEP(*(.text.tsl9_ble_frame_8cfa))
 }
 .tsl9_code_00008e82 0x8e82 : {
  KEEP(*(.text.tsl9_runtime_unported_8e82))
 }
 .tsl9_code_00008fe6 0x8fe6 : {
  KEEP(*(.text.__tsl9_runtime_entry))
 }
 .tsl9_code_00008ff8 0x8ff8 : {
  KEEP(*(.text.tsl9_ble_scheduler_event_8ff8))
 }
 .tsl9_code_00009058 0x9058 : {
  KEEP(*(.text.tsl9_ble_scheduler_init_9058))
 }
 .tsl9_code_0000908e 0x908e : {
  KEEP(*(.text.tsl9_scheduler_cancel_908e))
 }
 .tsl9_code_00009102 0x9102 : {
  KEEP(*(.text.tsl9_sgpio_register_9102))
 }
 .tsl9_code_0000922e 0x922e : {
  KEEP(*(.text.tsl9_entry_init_922e))
 }
 .tsl9_code_0000926e 0x926e : {
  KEEP(*(.text.tsl9_init_check_transform_926e))
 }
 .tsl9_code_00009298 0x9298 : {
  KEEP(*(.text.tsl9_init_check_identifier_9298))
 }
 .tsl9_code_00009312 0x9312 : {
  KEEP(*(.text.tsl9_init_check_value_9312))
 }
 .tsl9_code_0000935c 0x935c : {
  KEEP(*(.text.tsl9_runtime_unported_935c))
 }
 .tsl9_code_00009388 0x9388 : {
  KEEP(*(.text.tsl9_timer_start_9388))
 }
 .tsl9_code_000093cc 0x93cc : {
  KEEP(*(.text.tsl9_periph_timer_stop_93cc))
 }
 .tsl9_code_000093ee 0x93ee : {
  KEEP(*(.text.tsl9_timer_prepare_93ee))
 }
 .tsl9_code_00009432 0x9432 : {
  KEEP(*(.text.tsl9_runtime_unported_9432))
 }
 .tsl9_code_000094e6 0x94e6 : {
  KEEP(*(.text.tsl9_event_reference_94e6))
 }
 .tsl9_code_000095ec 0x95ec : {
  KEEP(*(.text.tsl9_event_reference_95ec))
 }
 .tsl9_code_00009770 0x9770 : {
  KEEP(*(.text.tsl9_timer_mode_9770))
 }
 .tsl9_code_0000977c 0x977c : {
  KEEP(*(.text.tsl9_timer3_irq))
 }
 .tsl9_code_00009936 0x9936 : {
  KEEP(*(.text.tsl9_runtime_unported_9936))
 }
 .tsl9_code_00009a02 0x9a02 : {
  KEEP(*(.text.tsl9_sgpio_pin_init_9a02))
 }
 .tsl9_code_00009a20 0x9a20 : {
  KEEP(*(.text.tsl9_runtime_unported_9a20))
 }
 .tsl9_code_00009ab0 0x9ab0 : {
  KEEP(*(.text.tsl9_sgpio_expire_9ab0))
 }
 .tsl9_code_00009ace 0x9ace : {
  KEEP(*(.text.tsl9_sgpio_idle_9ace))
 }
 .tsl9_code_00009b14 0x9b14 : {
  KEEP(*(.text.tsl9_runtime_unported_9b14))
 }
 .tsl9_code_00009b2c 0x9b2c : {
  KEEP(*(.text.tsl9_runtime_unported_9b2c))
 }
 .tsl9_code_00009b6c 0x9b6c : {
  KEEP(*(.text.tsl9_storage_page_9b6c))
 }
 .tsl9_code_00009d76 0x9d76 : {
  KEEP(*(.text.tsl9_config_persist_9d76))
 }
 .tsl9_code_00009d9e 0x9d9e : {
  KEEP(*(.text.tsl9_config_read_9d9e))
 }
 .tsl9_code_00009e2c 0x9e2c : {
  KEEP(*(.text.tsl9_runtime_unported_9e2c))
 }
 .tsl9_code_00009e66 0x9e66 : {
  KEEP(*(.text.tsl9_runtime_unported_9e66))
 }
 .tsl9_code_00009edc 0x9edc : {
  KEEP(*(.text.tsl9_rf_flag_9edc))
 }
 .tsl9_code_0000a2a0 0xa2a0 : {
  KEEP(*(.text.tsl9_feature_init_a2a0))
 }
 .tsl9_code_0000a936 0xa936 : {
  KEEP(*(.text.tsl9_feature_init_a936))
 }
 .tsl9_code_0000aed6 0xaed6 : {
  KEEP(*(.text.tsl9_feature_init_aed6))
 }
 .tsl9_code_0000af18 0xaf18 : {
  KEEP(*(.text.tsl9_feature_init_af18))
 }
 .tsl9_code_0000b060 0xb060 : {
  KEEP(*(.text.tsl9_feature_init_b060))
 }
 .tsl9_code_0000b46a 0xb46a : {
  KEEP(*(.text.tsl9_feature_init_b46a))
 }
 .tsl9_code_0000c25a 0xc25a : {
  KEEP(*(.text.tsl9_feature_init_c25a))
 }
 .tsl9_code_0000c516 0xc516 : {
  KEEP(*(.text.tsl9_feature_init_c516))
 }
 .tsl9_code_0000c544 0xc544 : {
  KEEP(*(.text.tsl9_tx_apply_c544))
 }
 .tsl9_code_0000c612 0xc612 : {
  KEEP(*(.text.tsl9_runtime_unported_c612))
 }
 .tsl9_code_0000c634 0xc634 : {
  KEEP(*(.text.tsl9_tx_clear_c634))
 }
 .tsl9_code_0000cd08 0xcd08 : {
  KEEP(*(.text.tsl9_feature_init_cd08))
 }
 .tsl9_code_0000cf4c 0xcf4c : {
  KEEP(*(.text.tsl9_feature_init_cf4c))
 }
 .tsl9_code_0000cff4 0xcff4 : {
  KEEP(*(.text.tsl9_feature_init_cff4))
 }
 .tsl9_code_0000d0cc 0xd0cc : {
  KEEP(*(.text.tsl9_feature_init_d0cc))
 }
 .tsl9_code_0000d39c 0xd39c : {
  KEEP(*(.text.tsl9_feature_init_d39c))
 }
 .tsl9_code_0000d514 0xd514 : {
  KEEP(*(.text.tsl9_feature_init_d514))
 }
 .tsl9_code_0000d5e4 0xd5e4 : {
  KEEP(*(.text.tsl9_feature_init_d5e4))
 }
 .tsl9_code_0000df2e 0xdf2e : {
  KEEP(*(.text.tsl9_feature_init_df2e))
 }
 .tsl9_code_0000ef6a 0xef6a : {
  KEEP(*(.text.tsl9_feature_init_ef6a))
 }
 .tsl9_code_0000f6fe 0xf6fe : {
  KEEP(*(.text.tsl9_feature_init_f6fe))
 }
 .tsl9_code_0000f906 0xf906 : {
  KEEP(*(.text.tsl9_feature_init_f906))
 }
 .tsl9_code_0000f9c2 0xf9c2 : {
  KEEP(*(.text.tsl9_feature_init_f9c2))
 }
 .tsl9_code_0000fdfa 0xfdfa : {
  KEEP(*(.text.tsl9_feature_init_fdfa))
 }
 .tsl9_code_0000fee4 0xfee4 : {
  KEEP(*(.text.tsl9_feature_init_fee4))
 }
 .tsl9_code_0001000a 0x1000a : {
  KEEP(*(.text.tsl9_feature_init_1000a))
 }
 .tsl9_code_00010128 0x10128 : {
  KEEP(*(.text.tsl9_feature_init_10128))
 }
 .tsl9_code_0001049a 0x1049a : {
  KEEP(*(.text.tsl9_rf_cancel_1049a))
 }
 .tsl9_code_00010564 0x10564 : {
  KEEP(*(.text.tsl9_runtime_unported_10564))
 }
 .tsl9_code_00010586 0x10586 : {
  KEEP(*(.text.tsl9_mode_clear_10586))
 }
 .tsl9_code_000105c8 0x105c8 : {
  KEEP(*(.text.tsl9_runtime_unported_105c8))
 }
 .tsl9_code_0001063c 0x1063c : {
  KEEP(*(.text.tsl9_control_zero_1063c))
 }
 .tsl9_code_00010642 0x10642 : {
  KEEP(*(.text.tsl9_runtime_unported_10642))
 }
 .tsl9_code_00010692 0x10692 : {
  KEEP(*(.text.tsl9_runtime_unported_10692))
 }
 .tsl9_code_000106b8 0x106b8 : {
  KEEP(*(.text.tsl9_runtime_unported_106b8))
 }
 .tsl9_code_000107b2 0x107b2 : {
  KEEP(*(.text.tsl9_runtime_unported_107b2))
 }
 .tsl9_code_00010a9a 0x10a9a : {
  KEEP(*(.text.tsl9_feature_init_10a9a))
 }
 .tsl9_code_00010af6 0x10af6 : {
  KEEP(*(.text.tsl9_ble_helper_10af6))
 }
 .tsl9_code_00010bdc 0x10bdc : {
  KEEP(*(.text.tsl9_runtime_unported_10bdc))
 }
 .tsl9_code_00010c16 0x10c16 : {
  KEEP(*(.text.tsl9_service_events_slot_10c16))
 }
 .tsl9_code_00010c48 0x10c48 : {
  KEEP(*(.text.tsl9_service_events_scan_10c48))
 }
 .tsl9_code_00010cfe 0x10cfe : {
  KEEP(*(.text.tsl9_runtime_unported_10cfe))
 }
 .tsl9_code_00010d2e 0x10d2e : {
  KEEP(*(.text.tsl9_runtime_unported_10d2e))
 }
 .tsl9_code_000111d2 0x111d2 : {
  KEEP(*(.text.tsl9_service_events_dispatch_111d2))
 }
 .tsl9_code_000112be 0x112be : {
  KEEP(*(.text.tsl9_runtime_unported_112be))
 }
 .tsl9_code_00011844 0x11844 : {
  KEEP(*(.text.tsl9_runtime_unported_11844))
 }
 .tsl9_code_00012388 0x12388 : {
  KEEP(*(.text.tsl9_runtime_unported_12388))
 }
 .tsl9_code_00012780 0x12780 : {
  KEEP(*(.text.tsl9_can_filter_fill_12780))
 }
 .tsl9_code_00012820 0x12820 : {
  KEEP(*(.text.tsl9_mode_filters_clear_12820))
 }
 .tsl9_code_00012864 0x12864 : {
  KEEP(*(.text.tsl9_runtime_unported_12864))
 }
 .tsl9_code_000128ec 0x128ec : {
  KEEP(*(.text.tsl9_mode_channel_clear_128ec))
 }
 .tsl9_code_0001290a 0x1290a : {
  KEEP(*(.text.tsl9_runtime_unported_1290a))
 }
 .tsl9_code_0001291c 0x1291c : {
  KEEP(*(.text.tsl9_runtime_unported_1291c))
 }
 .tsl9_code_000129d8 0x129d8 : {
  KEEP(*(.text.tsl9_periph_can_enqueue_129d8))
 }
 .tsl9_code_00012a34 0x12a34 : {
  KEEP(*(.text.tsl9_can_rx0_irq))
 }
 .tsl9_code_00012a68 0x12a68 : {
  KEEP(*(.text.tsl9_entry_can_consume_12a68))
 }
 .tsl9_code_00012b9c 0x12b9c : {
  KEEP(*(.text.tsl9_runtime_unported_12b9c))
 }
 .tsl9_code_00012c5e 0x12c5e : {
  KEEP(*(.text.tsl9_settings_write_12c5e))
 }
 .tsl9_code_00012c90 0x12c90 : {
  KEEP(*(.text.tsl9_settings_default_12c90))
 }
 .tsl9_code_00012d06 0x12d06 : {
  KEEP(*(.text.tsl9_settings_write_12d06))
 }
 .tsl9_code_00012d38 0x12d38 : {
  KEEP(*(.text.tsl9_settings_default_12d38))
 }
 .tsl9_code_00012d68 0x12d68 : {
  KEEP(*(.text.tsl9_settings_write_12d68))
 }
 .tsl9_code_00012d9a 0x12d9a : {
  KEEP(*(.text.tsl9_settings_default_12d9a))
 }
 .tsl9_code_00012e72 0x12e72 : {
  KEEP(*(.text.tsl9_settings_write_12e72))
 }
 .tsl9_code_00012ea4 0x12ea4 : {
  KEEP(*(.text.tsl9_settings_default_12ea4))
 }
 .tsl9_code_00012ef6 0x12ef6 : {
  KEEP(*(.text.tsl9_settings_write_12ef6))
 }
 .tsl9_code_00012f28 0x12f28 : {
  KEEP(*(.text.tsl9_settings_default_12f28))
 }
 .tsl9_code_00012f58 0x12f58 : {
  KEEP(*(.text.tsl9_settings_write_12f58))
 }
 .tsl9_code_00012f8a 0x12f8a : {
  KEEP(*(.text.tsl9_settings_default_12f8a))
 }
 .tsl9_code_00012fdc 0x12fdc : {
  KEEP(*(.text.tsl9_runtime_unported_12fdc))
 }
 .tsl9_code_00013156 0x13156 : {
  KEEP(*(.text.tsl9_runtime_unported_13156))
 }
 .tsl9_code_000133fa 0x133fa : {
  KEEP(*(.text.tsl9_service_events_pending_133fa))
 }
 .tsl9_code_00013960 0x13960 : {
  KEEP(*(.text.tsl9_ble_queue_copy_13960))
 }
 .tsl9_code_00013af0 0x13af0 : {
  KEEP(*(.text.tsl9_service_events_enqueue_13af0))
 }
 .tsl9_code_00013cac 0x13cac : {
  KEEP(*(.text.tsl9_ble_queue_route_13cac))
 }
 .tsl9_code_00013cc8 0x13cc8 : {
  KEEP(*(.text.tsl9_runtime_unported_13cc8))
 }
 .tsl9_code_00014a54 0x14a54 : {
  KEEP(*(.text.tsl9_runtime_unported_14a54))
 }
 .tsl9_code_00014af8 0x14af8 : {
  KEEP(*(.text.tsl9_runtime_unported_14af8))
 }
 .tsl9_code_0001524e 0x1524e : {
  KEEP(*(.text.tsl9_runtime_unported_1524e))
 }
 .tsl9_code_00015378 0x15378 : {
  KEEP(*(.text.tsl9_runtime_unported_15378))
 }
 .tsl9_code_000165cc 0x165cc : {
  KEEP(*(.text.tsl9_spi_select_165cc))
 }
 .tsl9_code_0001660a 0x1660a : {
  KEEP(*(.text.tsl9_spi_byte_1660a))
 }
 .tsl9_code_00016652 0x16652 : {
  KEEP(*(.text.tsl9_spi_write_16652))
 }
 .tsl9_code_000166b2 0x166b2 : {
  KEEP(*(.text.tsl9_spi_modify_166b2))
 }
 .tsl9_code_00016708 0x16708 : {
  KEEP(*(.text.tsl9_spi_read_16708))
 }
 .tsl9_code_00016750 0x16750 : {
  KEEP(*(.text.tsl9_spi_wait_16750))
 }
 .tsl9_code_000167a4 0x167a4 : {
  KEEP(*(.text.tsl9_spi_write_reg_167a4))
 }
 .tsl9_code_000167f0 0x167f0 : {
  KEEP(*(.text.tsl9_spi_capture_167f0))
 }
 .tsl9_code_0001687e 0x1687e : {
  KEEP(*(.text.tsl9_runtime_unported_1687e))
 }
 .tsl9_code_000168f0 0x168f0 : {
  KEEP(*(.text.tsl9_spi_transmit_168f0))
 }
 .tsl9_code_00016a38 0x16a38 : {
  KEEP(*(.text.tsl9_spi_filters_16a38))
 }
 .tsl9_code_00016b20 0x16b20 : {
  KEEP(*(.text.tsl9_mode_channel_flags_16b20))
 }
 .tsl9_code_00016b48 0x16b48 : {
  KEEP(*(.text.tsl9_mode_channel_mask_16b48))
 }
 .tsl9_code_00016d22 0x16d22 : {
  KEEP(*(.text.tsl9_exti_5_9_irq))
 }
 .tsl9_code_00016d6e 0x16d6e : {
  KEEP(*(.text.tsl9_entry_exti_consume_16d6e))
 }
 .tsl9_code_00016dac 0x16dac : {
  KEEP(*(.text.tsl9_runtime_unported_16dac))
 }
 .tsl9_code_00016f4a 0x16f4a : {
  KEEP(*(.text.tsl9_rf_schedule_16f4a))
 }
 .tsl9_code_00017048 0x17048 : {
  KEEP(*(.text.tsl9_rf_control_17048))
 }
 .tsl9_code_00017176 0x17176 : {
  KEEP(*(.text.tsl9_runtime_unported_17176))
 }
 .tsl9_code_000171c2 0x171c2 : {
  KEEP(*(.text.tsl9_rf_complete_171c2))
 }
 .tsl9_code_00017216 0x17216 : {
  KEEP(*(.text.tsl9_rf_retry_17216))
 }
 .tsl9_code_0001724a 0x1724a : {
  KEEP(*(.text.tsl9_rf_task_1724a))
 }
 .tsl9_code_000172c2 0x172c2 : {
  KEEP(*(.text.tsl9_rf_status_172c2))
 }
 .tsl9_code_0001730e 0x1730e : {
  KEEP(*(.text.tsl9_runtime_unported_1730e))
 }
 .tsl9_code_000173bc 0x173bc : {
  KEEP(*(.text.tsl9_runtime_unported_173bc))
 }
 .tsl9_code_0001743a 0x1743a : {
  KEEP(*(.text.tsl9_rf_queue_complete_1743a))
 }
 .tsl9_code_00017474 0x17474 : {
  KEEP(*(.text.tsl9_rf_queue_handshake_17474))
 }
 .tsl9_code_000174cc 0x174cc : {
  KEEP(*(.text.tsl9_rf_queue_task_174cc))
 }
 .tsl9_code_00017650 0x17650 : {
  KEEP(*(.text.tsl9_runtime_unported_17650))
 }
 .tsl9_code_000176cc 0x176cc : {
  KEEP(*(.text.tsl9_rf_queue_empty_frame_176cc))
 }
 .tsl9_code_0001771c 0x1771c : {
  KEEP(*(.text.tsl9_rf_queue_frame_1771c))
 }
 .tsl9_code_0001775e 0x1775e : {
  KEEP(*(.text.tsl9_rf_queue_select_1775e))
 }
 .tsl9_code_00017966 0x17966 : {
  KEEP(*(.text.tsl9_rf_queue_start_17966))
 }
 .tsl9_code_00017998 0x17998 : {
  KEEP(*(.text.tsl9_rf_queue_enable_17998))
 }
 .tsl9_code_000179ca 0x179ca : {
  KEEP(*(.text.tsl9_runtime_unported_179ca))
 }
 .tsl9_code_00017a22 0x17a22 : {
  KEEP(*(.text.tsl9_runtime_unported_17a22))
 }
 .tsl9_code_00017d52 0x17d52 : {
  KEEP(*(.text.tsl9_ble_helper_17d52))
 }
 .tsl9_code_00017dfa 0x17dfa : {
  KEEP(*(.text.tsl9_runtime_unported_17dfa))
 }
 .tsl9_code_0001836c 0x1836c : {
  KEEP(*(.text.tsl9_feature_init_1836c))
 }
 .tsl9_code_0001838c 0x1838c : {
  KEEP(*(.text.tsl9_default_irq_1838c))
 }
 .tsl9_code_0001838e 0x1838e : {
  KEEP(*(.text.tsl9_default_irq_1838e))
 }
 .tsl9_code_00018390 0x18390 : {
  KEEP(*(.text.tsl9_default_irq_18390))
 }
 .tsl9_code_00018392 0x18392 : {
  KEEP(*(.text.tsl9_default_irq_18392))
 }
 .tsl9_code_00018394 0x18394 : {
  KEEP(*(.text.tsl9_default_irq_18394))
 }
 .tsl9_code_00018396 0x18396 : {
  KEEP(*(.text.tsl9_default_irq_18396))
 }
 .tsl9_code_00018398 0x18398 : {
  KEEP(*(.text.tsl9_default_irq_18398))
 }
 .tsl9_code_0001839a 0x1839a : {
  KEEP(*(.text.tsl9_default_irq_1839a))
 }
 .tsl9_code_0001839c 0x1839c : {
  KEEP(*(.text.tsl9_default_irq_1839c))
 }
 .tsl9_code_0001839e 0x1839e : {
  KEEP(*(.text.tsl9_default_irq_1839e))
 }
 .tsl9_code_000183a0 0x183a0 : {
  KEEP(*(.text.tsl9_default_irq_183a0))
 }
 .tsl9_code_000183a2 0x183a2 : {
  KEEP(*(.text.tsl9_default_irq_183a2))
 }
 .tsl9_code_000183a4 0x183a4 : {
  KEEP(*(.text.tsl9_default_irq_183a4))
 }
 .tsl9_code_000183a6 0x183a6 : {
  KEEP(*(.text.tsl9_default_irq_183a6))
 }
 .tsl9_code_000183a8 0x183a8 : {
  KEEP(*(.text.tsl9_default_irq_183a8))
 }
 .tsl9_code_000183aa 0x183aa : {
  KEEP(*(.text.tsl9_default_irq_183aa))
 }
 .tsl9_code_000183ac 0x183ac : {
  KEEP(*(.text.tsl9_default_irq_183ac))
 }
 .tsl9_code_000183ae 0x183ae : {
  KEEP(*(.text.tsl9_default_irq_183ae))
 }
 .tsl9_code_000183b0 0x183b0 : {
  KEEP(*(.text.tsl9_default_irq_183b0))
 }
 .tsl9_code_000183b2 0x183b2 : {
  KEEP(*(.text.tsl9_default_irq_183b2))
 }
 .tsl9_code_000183b4 0x183b4 : {
  KEEP(*(.text.tsl9_default_irq_183b4))
 }
 .tsl9_code_000183b6 0x183b6 : {
  KEEP(*(.text.tsl9_default_irq_183b6))
 }
 .tsl9_code_000183b8 0x183b8 : {
  KEEP(*(.text.tsl9_default_irq_183b8))
 }
 .tsl9_code_000183bc 0x183bc : {
  KEEP(*(.text.tsl9_default_irq_183bc))
 }
 .tsl9_code_000183be 0x183be : {
  KEEP(*(.text.tsl9_default_irq_183be))
 }
 .tsl9_code_000183c2 0x183c2 : {
  KEEP(*(.text.tsl9_default_irq_183c2))
 }
 .tsl9_code_000183c4 0x183c4 : {
  KEEP(*(.text.tsl9_default_irq_183c4))
 }
 .tsl9_code_000183c6 0x183c6 : {
  KEEP(*(.text.tsl9_default_irq_183c6))
 }
 .tsl9_code_000183c8 0x183c8 : {
  KEEP(*(.text.tsl9_default_irq_183c8))
 }
 .tsl9_code_000183ca 0x183ca : {
  KEEP(*(.text.tsl9_default_irq_183ca))
 }
 .tsl9_code_000183ce 0x183ce : {
  KEEP(*(.text.tsl9_default_irq_183ce))
 }
 .tsl9_code_000183d0 0x183d0 : {
  KEEP(*(.text.tsl9_default_irq_183d0))
 }
 .tsl9_code_000183d2 0x183d2 : {
  KEEP(*(.text.tsl9_default_irq_183d2))
 }
 .tsl9_code_000183d4 0x183d4 : {
  KEEP(*(.text.tsl9_default_irq_183d4))
 }
 .tsl9_code_000183d6 0x183d6 : {
  KEEP(*(.text.tsl9_default_irq_183d6))
 }
 .tsl9_code_000183d8 0x183d8 : {
  KEEP(*(.text.tsl9_default_irq_183d8))
 }
 .tsl9_code_000183da 0x183da : {
  KEEP(*(.text.tsl9_default_irq_183da))
 }
 .tsl9_code_000183dc 0x183dc : {
  KEEP(*(.text.tsl9_default_irq_183dc))
 }
 .tsl9_code_000183de 0x183de : {
  KEEP(*(.text.tsl9_default_irq_183de))
 }
 .tsl9_code_000183e0 0x183e0 : {
  KEEP(*(.text.tsl9_default_irq_183e0))
 }
 .tsl9_code_000183e2 0x183e2 : {
  KEEP(*(.text.tsl9_default_irq_183e2))
 }
 .tsl9_code_000183e6 0x183e6 : {
  KEEP(*(.text.tsl9_default_irq_183e6))
 }
 .tsl9_code_000183e8 0x183e8 : {
  KEEP(*(.text.tsl9_default_irq_183e8))
 }
 .tsl9_code_000183ea 0x183ea : {
  KEEP(*(.text.tsl9_default_irq_183ea))
 }
 .tsl9_code_000183ec 0x183ec : {
  KEEP(*(.text.tsl9_default_irq_183ec))
 }
 .tsl9_code_000183ee 0x183ee : {
  KEEP(*(.text.tsl9_default_irq_183ee))
 }
 .tsl9_code_000183f4 0x183f4 : {
  KEEP(*(.text.tsl9_default_irq_183f4))
 }
 .tsl9_code_000183f6 0x183f6 : {
  KEEP(*(.text.tsl9_default_irq_183f6))
 }
 .tsl9_code_000183f8 0x183f8 : {
  KEEP(*(.text.tsl9_default_irq_183f8))
 }
 .tsl9_code_000183fa 0x183fa : {
  KEEP(*(.text.tsl9_default_irq_183fa))
 }
 .tsl9_code_000183fc 0x183fc : {
  KEEP(*(.text.tsl9_default_irq_183fc))
 }
 .tsl9_code_000183fe 0x183fe : {
  KEEP(*(.text.tsl9_reset_entry))
  KEEP(*(.text.tsl9_reset_mret_18488))
  KEEP(*(.text.tsl9_default_irq_1848c))
  KEEP(*(.text.tsl9_default_irq_18490))
 }
 .tsl9_code_00018492 0x18492 : {
  KEEP(*(.text.tsl9_ble_bb))
 }
 .tsl9_code_0001849e 0x1849e : {
  KEEP(*(.text.sc_native_init))
 }
 .tsl9_code_00018588 0x18588 : {
  KEEP(*(.text.tsl9_entry_clock_update_18588))
 }
 .tsl9_code_00018636 0x18636 : {
  KEEP(*(.text.tsl9_hal_adc_reset_18636))
 }
 .tsl9_code_00018682 0x18682 : {
  KEEP(*(.text.tsl9_hal_adc_configure_18682))
 }
 .tsl9_code_000186da 0x186da : {
  KEEP(*(.text.tsl9_hal_adc_enable_186da))
 }
 .tsl9_code_000186ea 0x186ea : {
  KEEP(*(.text.tsl9_hal_adc_start_186ea))
 }
 .tsl9_code_00018702 0x18702 : {
  KEEP(*(.text.tsl9_hal_adc_channel_18702))
 }
 .tsl9_code_000187ba 0x187ba : {
  KEEP(*(.text.tsl9_hal_adc_data_187ba))
 }
 .tsl9_code_000187c2 0x187c2 : {
  KEEP(*(.text.tsl9_hal_adc_temperature_187c2))
 }
 .tsl9_code_000187e2 0x187e2 : {
  KEEP(*(.text.tsl9_hal_adc_flag_187e2))
 }
 .tsl9_code_000187ec 0x187ec : {
  KEEP(*(.text.tsl9_hal_adc_buffer_187ec))
 }
 .tsl9_code_00018804 0x18804 : {
  KEEP(*(.text.tsl9_init_can_registers_18804))
 }
 .tsl9_code_000188f6 0x188f6 : {
  KEEP(*(.text.tsl9_can_filter_regs_188f6))
 }
 .tsl9_code_000189f8 0x189f8 : {
  KEEP(*(.text.tsl9_can_mailbox_189f8))
 }
 .tsl9_code_00018acc 0x18acc : {
  KEEP(*(.text.tsl9_periph_can_capture_18acc))
 }
 .tsl9_code_00018b70 0x18b70 : {
  KEEP(*(.text.tsl9_init_exti_config_18b70))
 }
 .tsl9_code_00018bda 0x18bda : {
  KEEP(*(.text.tsl9_event_exti_clear_18bda))
 }
 .tsl9_code_00018be4 0x18be4 : {
  KEEP(*(.text.tsl9_storage_status_18be4))
 }
 .tsl9_code_00018bec 0x18bec : {
  KEEP(*(.text.tsl9_storage_unlock_18bec))
 }
 .tsl9_code_00018c0a 0x18c0a : {
  KEEP(*(.text.tsl9_storage_lock_18c0a))
 }
 .tsl9_code_00018c18 0x18c18 : {
  KEEP(*(.text.tsl9_storage_erase_18c18))
 }
 .tsl9_code_00018c46 0x18c46 : {
  KEEP(*(.text.tsl9_storage_program_18c46))
 }
 .tsl9_code_00018caa 0x18caa : {
  KEEP(*(.text.tsl9_runtime_unported_18caa))
 }
 .tsl9_code_00018cdc 0x18cdc : {
  KEEP(*(.text.tsl9_sgpio_config_18cdc))
 }
 .tsl9_code_00018d9e 0x18d9e : {
  KEEP(*(.text.tsl9_init_gpio_route_18d9e))
 }
 .tsl9_code_00018dca 0x18dca : {
  KEEP(*(.text.tsl9_rtc_startup_18dca))
 }
 .tsl9_code_00018de0 0x18de0 : {
  KEEP(*(.text.tsl9_hal_adc_clock_18de0))
 }
 .tsl9_code_00018df2 0x18df2 : {
  KEEP(*(.text.tsl9_rtc_startup_18df2))
 }
 .tsl9_code_00018e1a 0x18e1a : {
  KEEP(*(.text.tsl9_rtc_startup_18e1a))
 }
 .tsl9_code_00018e2e 0x18e2e : {
  KEEP(*(.text.tsl9_rtc_startup_18e2e))
 }
 .tsl9_code_00018e3a 0x18e3a : {
  KEEP(*(.text.tsl9_rtc_startup_18e3a))
 }
 .tsl9_code_00018e5a 0x18e5a : {
  KEEP(*(.text.tsl9_hal_ahb_gate_18e5a))
 }
 .tsl9_code_00018e78 0x18e78 : {
  KEEP(*(.text.tsl9_board_rcc_apb2_enable_18e78))
 }
 .tsl9_code_00018e96 0x18e96 : {
  KEEP(*(.text.tsl9_board_rcc_apb1_enable_18e96))
 }
 .tsl9_code_00018eb4 0x18eb4 : {
  KEEP(*(.text.tsl9_board_rcc_apb2_reset_18eb4))
 }
 .tsl9_code_00018ed2 0x18ed2 : {
  KEEP(*(.text.tsl9_board_rcc_apb1_reset_18ed2))
 }
 .tsl9_code_00018ef0 0x18ef0 : {
  KEEP(*(.text.tsl9_rtc_startup_18ef0))
 }
 .tsl9_code_00018f02 0x18f02 : {
  KEEP(*(.text.tsl9_rtc_startup_18f02))
 }
 .tsl9_code_00018f1a 0x18f1a : {
  KEEP(*(.text.tsl9_rtc_startup_18f1a))
 }
 .tsl9_code_00018f74 0x18f74 : {
  KEEP(*(.text.tsl9_rtc_startup_18f74))
 }
 .tsl9_code_00018f9c 0x18f9c : {
  KEEP(*(.text.tsl9_rtc_startup_18f9c))
 }
 .tsl9_code_00018fc6 0x18fc6 : {
  KEEP(*(.text.tsl9_event_rtc_wait_18fc6))
 }
 .tsl9_code_00018fd6 0x18fd6 : {
  KEEP(*(.text.tsl9_event_rtc_clear_core_18fd6))
 }
 .tsl9_code_00018fea 0x18fea : {
  KEEP(*(.text.tsl9_event_rtc_clear_18fea))
 }
 .tsl9_code_00018fee 0x18fee : {
  KEEP(*(.text.tsl9_rtc_startup_18fee))
 }
 .tsl9_code_00019418 0x19418 : {
  KEEP(*(.text.tsl9_init_spi_registers_19418))
 }
 .tsl9_code_00019472 0x19472 : {
  KEEP(*(.text.tsl9_init_spi_enable_19472))
 }
 .tsl9_code_00019490 0x19490 : {
  KEEP(*(.text.tsl9_runtime_unported_19490))
 }
 .tsl9_code_000194b8 0x194b8 : {
  KEEP(*(.text.tsl9_hal_delay_ticks_194b8))
 }
 .tsl9_code_000194ee 0x194ee : {
  KEEP(*(.text.tsl9_runtime_unported_194ee))
 }
 .tsl9_code_0001950c 0x1950c : {
  KEEP(*(.text.tsl9_rtc_startup_1950c))
 }
 .tsl9_code_00019512 0x19512 : {
  KEEP(*(.text.tsl9_runtime_unported_19512))
 }
 .tsl9_code_00019544 0x19544 : {
  KEEP(*(.text.tsl9_runtime_unported_19544))
 }
 .tsl9_code_000196b0 0x196b0 : {
  KEEP(*(.text.tsl9_runtime_unported_196b0))
 }
 .tsl9_code_00019736 0x19736 : {
  KEEP(*(.text.tsl9_runtime_unported_19736))
 }
 .tsl9_code_0001986a 0x1986a : {
  KEEP(*(.text.tsl9_runtime_unported_1986a))
 }
 .tsl9_code_000198aa 0x198aa : {
  KEEP(*(.text.tsl9_rtc_startup_198aa))
 }
 .tsl9_code_00019928 0x19928 : {
  KEEP(*(.text.tsl9_rtc_alarm_irq))
 }
 .tsl9_code_00019944 0x19944 : {
  KEEP(*(.text.tsl9_runtime_unported_19944))
 }
 .tsl9_ro_00019a84 0x19a84 : {
  KEEP(*(.rodata.tsl9_ble_advertising_19a84))
 }
 .tsl9_ro_0001a318 0x1a318 : {
  KEEP(*(.rodata.tsl9_mode_table_1a318))
 }
 .tsl9_ro_0001a33c 0x1a33c : {
  KEEP(*(.rodata.tsl9_dispatch_mode_table_1a33c))
 }
 .tsl9_ro_0001a358 0x1a358 : {
  KEEP(*(.rodata.tsl9_dispatch_bits_table_1a358))
 }
 .tsl9_ro_0001a378 0x1a378 : {
  KEEP(*(.rodata.tsl9_service_table_1a378))
 }
}
ASSERT(ADDR(.tsl9_code_00008000) == 0x8000, ".tsl9_code_00008000 plan");
ASSERT(SIZEOF(.tsl9_code_00008000) == 4, ".tsl9_code_00008000 size");
ASSERT(ADDR(.tsl9_ro_00008038) == 0x8038, ".tsl9_ro_00008038 plan");
ASSERT(SIZEOF(.tsl9_ro_00008038) == 328, ".tsl9_ro_00008038 size");
ASSERT(ADDR(.tsl9_code_00008180) == 0x8180, ".tsl9_code_00008180 plan");
ASSERT(SIZEOF(.tsl9_code_00008180) == 42, ".tsl9_code_00008180 size");
ASSERT(ADDR(.tsl9_code_000081aa) == 0x81aa, ".tsl9_code_000081aa plan");
ASSERT(SIZEOF(.tsl9_code_000081aa) == 6, ".tsl9_code_000081aa size");
ASSERT(ADDR(.tsl9_code_000081b0) == 0x81b0, ".tsl9_code_000081b0 plan");
ASSERT(SIZEOF(.tsl9_code_000081b0) == 26, ".tsl9_code_000081b0 size");
ASSERT(ADDR(.tsl9_code_00008202) == 0x8202, ".tsl9_code_00008202 plan");
ASSERT(SIZEOF(.tsl9_code_00008202) == 18, ".tsl9_code_00008202 size");
ASSERT(ADDR(.tsl9_code_00008214) == 0x8214, ".tsl9_code_00008214 plan");
ASSERT(SIZEOF(.tsl9_code_00008214) == 42, ".tsl9_code_00008214 size");
ASSERT(ADDR(.tsl9_code_00008282) == 0x8282, ".tsl9_code_00008282 plan");
ASSERT(SIZEOF(.tsl9_code_00008282) == 18, ".tsl9_code_00008282 size");
ASSERT(ADDR(.tsl9_code_00008294) == 0x8294, ".tsl9_code_00008294 plan");
ASSERT(SIZEOF(.tsl9_code_00008294) == 10, ".tsl9_code_00008294 size");
ASSERT(ADDR(.tsl9_code_0000829e) == 0x829e, ".tsl9_code_0000829e plan");
ASSERT(SIZEOF(.tsl9_code_0000829e) == 42, ".tsl9_code_0000829e size");
ASSERT(ADDR(.tsl9_code_000082c8) == 0x82c8, ".tsl9_code_000082c8 plan");
ASSERT(SIZEOF(.tsl9_code_000082c8) == 190, ".tsl9_code_000082c8 size");
ASSERT(ADDR(.tsl9_code_00008386) == 0x8386, ".tsl9_code_00008386 plan");
ASSERT(SIZEOF(.tsl9_code_00008386) == 180, ".tsl9_code_00008386 size");
ASSERT(ADDR(.tsl9_code_0000843a) == 0x843a, ".tsl9_code_0000843a plan");
ASSERT(SIZEOF(.tsl9_code_0000843a) == 6, ".tsl9_code_0000843a size");
ASSERT(ADDR(.tsl9_code_00008440) == 0x8440, ".tsl9_code_00008440 plan");
ASSERT(SIZEOF(.tsl9_code_00008440) == 78, ".tsl9_code_00008440 size");
ASSERT(ADDR(.tsl9_code_00008490) == 0x8490, ".tsl9_code_00008490 plan");
ASSERT(SIZEOF(.tsl9_code_00008490) == 134, ".tsl9_code_00008490 size");
ASSERT(ADDR(.tsl9_code_00008518) == 0x8518, ".tsl9_code_00008518 plan");
ASSERT(SIZEOF(.tsl9_code_00008518) == 168, ".tsl9_code_00008518 size");
ASSERT(ADDR(.tsl9_code_000085c0) == 0x85c0, ".tsl9_code_000085c0 plan");
ASSERT(SIZEOF(.tsl9_code_000085c0) == 34, ".tsl9_code_000085c0 size");
ASSERT(ADDR(.tsl9_code_000085e2) == 0x85e2, ".tsl9_code_000085e2 plan");
ASSERT(SIZEOF(.tsl9_code_000085e2) == 406, ".tsl9_code_000085e2 size");
ASSERT(ADDR(.tsl9_code_00008cfa) == 0x8cfa, ".tsl9_code_00008cfa plan");
ASSERT(SIZEOF(.tsl9_code_00008cfa) == 280, ".tsl9_code_00008cfa size");
ASSERT(ADDR(.tsl9_code_00008e82) == 0x8e82, ".tsl9_code_00008e82 plan");
ASSERT(SIZEOF(.tsl9_code_00008e82) == 356, ".tsl9_code_00008e82 size");
ASSERT(ADDR(.tsl9_code_00008fe6) == 0x8fe6, ".tsl9_code_00008fe6 plan");
ASSERT(SIZEOF(.tsl9_code_00008fe6) == 18, ".tsl9_code_00008fe6 size");
ASSERT(ADDR(.tsl9_code_00008ff8) == 0x8ff8, ".tsl9_code_00008ff8 plan");
ASSERT(SIZEOF(.tsl9_code_00008ff8) == 96, ".tsl9_code_00008ff8 size");
ASSERT(ADDR(.tsl9_code_00009058) == 0x9058, ".tsl9_code_00009058 plan");
ASSERT(SIZEOF(.tsl9_code_00009058) == 54, ".tsl9_code_00009058 size");
ASSERT(ADDR(.tsl9_code_0000908e) == 0x908e, ".tsl9_code_0000908e plan");
ASSERT(SIZEOF(.tsl9_code_0000908e) == 116, ".tsl9_code_0000908e size");
ASSERT(ADDR(.tsl9_code_00009102) == 0x9102, ".tsl9_code_00009102 plan");
ASSERT(SIZEOF(.tsl9_code_00009102) == 300, ".tsl9_code_00009102 size");
ASSERT(ADDR(.tsl9_code_0000922e) == 0x922e, ".tsl9_code_0000922e plan");
ASSERT(SIZEOF(.tsl9_code_0000922e) == 64, ".tsl9_code_0000922e size");
ASSERT(ADDR(.tsl9_code_0000926e) == 0x926e, ".tsl9_code_0000926e plan");
ASSERT(SIZEOF(.tsl9_code_0000926e) == 42, ".tsl9_code_0000926e size");
ASSERT(ADDR(.tsl9_code_00009298) == 0x9298, ".tsl9_code_00009298 plan");
ASSERT(SIZEOF(.tsl9_code_00009298) == 56, ".tsl9_code_00009298 size");
ASSERT(ADDR(.tsl9_code_00009312) == 0x9312, ".tsl9_code_00009312 plan");
ASSERT(SIZEOF(.tsl9_code_00009312) == 74, ".tsl9_code_00009312 size");
ASSERT(ADDR(.tsl9_code_0000935c) == 0x935c, ".tsl9_code_0000935c plan");
ASSERT(SIZEOF(.tsl9_code_0000935c) == 44, ".tsl9_code_0000935c size");
ASSERT(ADDR(.tsl9_code_00009388) == 0x9388, ".tsl9_code_00009388 plan");
ASSERT(SIZEOF(.tsl9_code_00009388) == 68, ".tsl9_code_00009388 size");
ASSERT(ADDR(.tsl9_code_000093cc) == 0x93cc, ".tsl9_code_000093cc plan");
ASSERT(SIZEOF(.tsl9_code_000093cc) == 34, ".tsl9_code_000093cc size");
ASSERT(ADDR(.tsl9_code_000093ee) == 0x93ee, ".tsl9_code_000093ee plan");
ASSERT(SIZEOF(.tsl9_code_000093ee) == 68, ".tsl9_code_000093ee size");
ASSERT(ADDR(.tsl9_code_00009432) == 0x9432, ".tsl9_code_00009432 plan");
ASSERT(SIZEOF(.tsl9_code_00009432) == 154, ".tsl9_code_00009432 size");
ASSERT(ADDR(.tsl9_code_000094e6) == 0x94e6, ".tsl9_code_000094e6 plan");
ASSERT(SIZEOF(.tsl9_code_000094e6) == 70, ".tsl9_code_000094e6 size");
ASSERT(ADDR(.tsl9_code_000095ec) == 0x95ec, ".tsl9_code_000095ec plan");
ASSERT(SIZEOF(.tsl9_code_000095ec) == 74, ".tsl9_code_000095ec size");
ASSERT(ADDR(.tsl9_code_00009770) == 0x9770, ".tsl9_code_00009770 plan");
ASSERT(SIZEOF(.tsl9_code_00009770) == 12, ".tsl9_code_00009770 size");
ASSERT(ADDR(.tsl9_code_0000977c) == 0x977c, ".tsl9_code_0000977c plan");
ASSERT(SIZEOF(.tsl9_code_0000977c) == 442, ".tsl9_code_0000977c size");
ASSERT(ADDR(.tsl9_code_00009936) == 0x9936, ".tsl9_code_00009936 plan");
ASSERT(SIZEOF(.tsl9_code_00009936) == 144, ".tsl9_code_00009936 size");
ASSERT(ADDR(.tsl9_code_00009a02) == 0x9a02, ".tsl9_code_00009a02 plan");
ASSERT(SIZEOF(.tsl9_code_00009a02) == 30, ".tsl9_code_00009a02 size");
ASSERT(ADDR(.tsl9_code_00009a20) == 0x9a20, ".tsl9_code_00009a20 plan");
ASSERT(SIZEOF(.tsl9_code_00009a20) == 144, ".tsl9_code_00009a20 size");
ASSERT(ADDR(.tsl9_code_00009ab0) == 0x9ab0, ".tsl9_code_00009ab0 plan");
ASSERT(SIZEOF(.tsl9_code_00009ab0) == 18, ".tsl9_code_00009ab0 size");
ASSERT(ADDR(.tsl9_code_00009ace) == 0x9ace, ".tsl9_code_00009ace plan");
ASSERT(SIZEOF(.tsl9_code_00009ace) == 18, ".tsl9_code_00009ace size");
ASSERT(ADDR(.tsl9_code_00009b14) == 0x9b14, ".tsl9_code_00009b14 plan");
ASSERT(SIZEOF(.tsl9_code_00009b14) == 24, ".tsl9_code_00009b14 size");
ASSERT(ADDR(.tsl9_code_00009b2c) == 0x9b2c, ".tsl9_code_00009b2c plan");
ASSERT(SIZEOF(.tsl9_code_00009b2c) == 64, ".tsl9_code_00009b2c size");
ASSERT(ADDR(.tsl9_code_00009b6c) == 0x9b6c, ".tsl9_code_00009b6c plan");
ASSERT(SIZEOF(.tsl9_code_00009b6c) == 64, ".tsl9_code_00009b6c size");
ASSERT(ADDR(.tsl9_code_00009d76) == 0x9d76, ".tsl9_code_00009d76 plan");
ASSERT(SIZEOF(.tsl9_code_00009d76) == 40, ".tsl9_code_00009d76 size");
ASSERT(ADDR(.tsl9_code_00009d9e) == 0x9d9e, ".tsl9_code_00009d9e plan");
ASSERT(SIZEOF(.tsl9_code_00009d9e) == 34, ".tsl9_code_00009d9e size");
ASSERT(ADDR(.tsl9_code_00009e2c) == 0x9e2c, ".tsl9_code_00009e2c plan");
ASSERT(SIZEOF(.tsl9_code_00009e2c) == 58, ".tsl9_code_00009e2c size");
ASSERT(ADDR(.tsl9_code_00009e66) == 0x9e66, ".tsl9_code_00009e66 plan");
ASSERT(SIZEOF(.tsl9_code_00009e66) == 40, ".tsl9_code_00009e66 size");
ASSERT(ADDR(.tsl9_code_00009edc) == 0x9edc, ".tsl9_code_00009edc plan");
ASSERT(SIZEOF(.tsl9_code_00009edc) == 6, ".tsl9_code_00009edc size");
ASSERT(ADDR(.tsl9_code_0000a2a0) == 0xa2a0, ".tsl9_code_0000a2a0 plan");
ASSERT(SIZEOF(.tsl9_code_0000a2a0) == 18, ".tsl9_code_0000a2a0 size");
ASSERT(ADDR(.tsl9_code_0000a936) == 0xa936, ".tsl9_code_0000a936 plan");
ASSERT(SIZEOF(.tsl9_code_0000a936) == 22, ".tsl9_code_0000a936 size");
ASSERT(ADDR(.tsl9_code_0000aed6) == 0xaed6, ".tsl9_code_0000aed6 plan");
ASSERT(SIZEOF(.tsl9_code_0000aed6) == 22, ".tsl9_code_0000aed6 size");
ASSERT(ADDR(.tsl9_code_0000af18) == 0xaf18, ".tsl9_code_0000af18 plan");
ASSERT(SIZEOF(.tsl9_code_0000af18) == 78, ".tsl9_code_0000af18 size");
ASSERT(ADDR(.tsl9_code_0000b060) == 0xb060, ".tsl9_code_0000b060 plan");
ASSERT(SIZEOF(.tsl9_code_0000b060) == 18, ".tsl9_code_0000b060 size");
ASSERT(ADDR(.tsl9_code_0000b46a) == 0xb46a, ".tsl9_code_0000b46a plan");
ASSERT(SIZEOF(.tsl9_code_0000b46a) == 22, ".tsl9_code_0000b46a size");
ASSERT(ADDR(.tsl9_code_0000c25a) == 0xc25a, ".tsl9_code_0000c25a plan");
ASSERT(SIZEOF(.tsl9_code_0000c25a) == 22, ".tsl9_code_0000c25a size");
ASSERT(ADDR(.tsl9_code_0000c516) == 0xc516, ".tsl9_code_0000c516 plan");
ASSERT(SIZEOF(.tsl9_code_0000c516) == 46, ".tsl9_code_0000c516 size");
ASSERT(ADDR(.tsl9_code_0000c544) == 0xc544, ".tsl9_code_0000c544 plan");
ASSERT(SIZEOF(.tsl9_code_0000c544) == 206, ".tsl9_code_0000c544 size");
ASSERT(ADDR(.tsl9_code_0000c612) == 0xc612, ".tsl9_code_0000c612 plan");
ASSERT(SIZEOF(.tsl9_code_0000c612) == 34, ".tsl9_code_0000c612 size");
ASSERT(ADDR(.tsl9_code_0000c634) == 0xc634, ".tsl9_code_0000c634 plan");
ASSERT(SIZEOF(.tsl9_code_0000c634) == 18, ".tsl9_code_0000c634 size");
ASSERT(ADDR(.tsl9_code_0000cd08) == 0xcd08, ".tsl9_code_0000cd08 plan");
ASSERT(SIZEOF(.tsl9_code_0000cd08) == 22, ".tsl9_code_0000cd08 size");
ASSERT(ADDR(.tsl9_code_0000cf4c) == 0xcf4c, ".tsl9_code_0000cf4c plan");
ASSERT(SIZEOF(.tsl9_code_0000cf4c) == 22, ".tsl9_code_0000cf4c size");
ASSERT(ADDR(.tsl9_code_0000cff4) == 0xcff4, ".tsl9_code_0000cff4 plan");
ASSERT(SIZEOF(.tsl9_code_0000cff4) == 18, ".tsl9_code_0000cff4 size");
ASSERT(ADDR(.tsl9_code_0000d0cc) == 0xd0cc, ".tsl9_code_0000d0cc plan");
ASSERT(SIZEOF(.tsl9_code_0000d0cc) == 22, ".tsl9_code_0000d0cc size");
ASSERT(ADDR(.tsl9_code_0000d39c) == 0xd39c, ".tsl9_code_0000d39c plan");
ASSERT(SIZEOF(.tsl9_code_0000d39c) == 22, ".tsl9_code_0000d39c size");
ASSERT(ADDR(.tsl9_code_0000d514) == 0xd514, ".tsl9_code_0000d514 plan");
ASSERT(SIZEOF(.tsl9_code_0000d514) == 18, ".tsl9_code_0000d514 size");
ASSERT(ADDR(.tsl9_code_0000d5e4) == 0xd5e4, ".tsl9_code_0000d5e4 plan");
ASSERT(SIZEOF(.tsl9_code_0000d5e4) == 18, ".tsl9_code_0000d5e4 size");
ASSERT(ADDR(.tsl9_code_0000df2e) == 0xdf2e, ".tsl9_code_0000df2e plan");
ASSERT(SIZEOF(.tsl9_code_0000df2e) == 22, ".tsl9_code_0000df2e size");
ASSERT(ADDR(.tsl9_code_0000ef6a) == 0xef6a, ".tsl9_code_0000ef6a plan");
ASSERT(SIZEOF(.tsl9_code_0000ef6a) == 22, ".tsl9_code_0000ef6a size");
ASSERT(ADDR(.tsl9_code_0000f6fe) == 0xf6fe, ".tsl9_code_0000f6fe plan");
ASSERT(SIZEOF(.tsl9_code_0000f6fe) == 22, ".tsl9_code_0000f6fe size");
ASSERT(ADDR(.tsl9_code_0000f906) == 0xf906, ".tsl9_code_0000f906 plan");
ASSERT(SIZEOF(.tsl9_code_0000f906) == 18, ".tsl9_code_0000f906 size");
ASSERT(ADDR(.tsl9_code_0000f9c2) == 0xf9c2, ".tsl9_code_0000f9c2 plan");
ASSERT(SIZEOF(.tsl9_code_0000f9c2) == 18, ".tsl9_code_0000f9c2 size");
ASSERT(ADDR(.tsl9_code_0000fdfa) == 0xfdfa, ".tsl9_code_0000fdfa plan");
ASSERT(SIZEOF(.tsl9_code_0000fdfa) == 18, ".tsl9_code_0000fdfa size");
ASSERT(ADDR(.tsl9_code_0000fee4) == 0xfee4, ".tsl9_code_0000fee4 plan");
ASSERT(SIZEOF(.tsl9_code_0000fee4) == 18, ".tsl9_code_0000fee4 size");
ASSERT(ADDR(.tsl9_code_0001000a) == 0x1000a, ".tsl9_code_0001000a plan");
ASSERT(SIZEOF(.tsl9_code_0001000a) == 22, ".tsl9_code_0001000a size");
ASSERT(ADDR(.tsl9_code_00010128) == 0x10128, ".tsl9_code_00010128 plan");
ASSERT(SIZEOF(.tsl9_code_00010128) == 18, ".tsl9_code_00010128 size");
ASSERT(ADDR(.tsl9_code_0001049a) == 0x1049a, ".tsl9_code_0001049a plan");
ASSERT(SIZEOF(.tsl9_code_0001049a) == 20, ".tsl9_code_0001049a size");
ASSERT(ADDR(.tsl9_code_00010564) == 0x10564, ".tsl9_code_00010564 plan");
ASSERT(SIZEOF(.tsl9_code_00010564) == 34, ".tsl9_code_00010564 size");
ASSERT(ADDR(.tsl9_code_00010586) == 0x10586, ".tsl9_code_00010586 plan");
ASSERT(SIZEOF(.tsl9_code_00010586) == 66, ".tsl9_code_00010586 size");
ASSERT(ADDR(.tsl9_code_000105c8) == 0x105c8, ".tsl9_code_000105c8 plan");
ASSERT(SIZEOF(.tsl9_code_000105c8) == 116, ".tsl9_code_000105c8 size");
ASSERT(ADDR(.tsl9_code_0001063c) == 0x1063c, ".tsl9_code_0001063c plan");
ASSERT(SIZEOF(.tsl9_code_0001063c) == 6, ".tsl9_code_0001063c size");
ASSERT(ADDR(.tsl9_code_00010642) == 0x10642, ".tsl9_code_00010642 plan");
ASSERT(SIZEOF(.tsl9_code_00010642) == 80, ".tsl9_code_00010642 size");
ASSERT(ADDR(.tsl9_code_00010692) == 0x10692, ".tsl9_code_00010692 plan");
ASSERT(SIZEOF(.tsl9_code_00010692) == 38, ".tsl9_code_00010692 size");
ASSERT(ADDR(.tsl9_code_000106b8) == 0x106b8, ".tsl9_code_000106b8 plan");
ASSERT(SIZEOF(.tsl9_code_000106b8) == 52, ".tsl9_code_000106b8 size");
ASSERT(ADDR(.tsl9_code_000107b2) == 0x107b2, ".tsl9_code_000107b2 plan");
ASSERT(SIZEOF(.tsl9_code_000107b2) == 14, ".tsl9_code_000107b2 size");
ASSERT(ADDR(.tsl9_code_00010a9a) == 0x10a9a, ".tsl9_code_00010a9a plan");
ASSERT(SIZEOF(.tsl9_code_00010a9a) == 22, ".tsl9_code_00010a9a size");
ASSERT(ADDR(.tsl9_code_00010af6) == 0x10af6, ".tsl9_code_00010af6 plan");
ASSERT(SIZEOF(.tsl9_code_00010af6) == 102, ".tsl9_code_00010af6 size");
ASSERT(ADDR(.tsl9_code_00010bdc) == 0x10bdc, ".tsl9_code_00010bdc plan");
ASSERT(SIZEOF(.tsl9_code_00010bdc) == 58, ".tsl9_code_00010bdc size");
ASSERT(ADDR(.tsl9_code_00010c16) == 0x10c16, ".tsl9_code_00010c16 plan");
ASSERT(SIZEOF(.tsl9_code_00010c16) == 50, ".tsl9_code_00010c16 size");
ASSERT(ADDR(.tsl9_code_00010c48) == 0x10c48, ".tsl9_code_00010c48 plan");
ASSERT(SIZEOF(.tsl9_code_00010c48) == 182, ".tsl9_code_00010c48 size");
ASSERT(ADDR(.tsl9_code_00010cfe) == 0x10cfe, ".tsl9_code_00010cfe plan");
ASSERT(SIZEOF(.tsl9_code_00010cfe) == 48, ".tsl9_code_00010cfe size");
ASSERT(ADDR(.tsl9_code_00010d2e) == 0x10d2e, ".tsl9_code_00010d2e plan");
ASSERT(SIZEOF(.tsl9_code_00010d2e) == 582, ".tsl9_code_00010d2e size");
ASSERT(ADDR(.tsl9_code_000111d2) == 0x111d2, ".tsl9_code_000111d2 plan");
ASSERT(SIZEOF(.tsl9_code_000111d2) == 236, ".tsl9_code_000111d2 size");
ASSERT(ADDR(.tsl9_code_000112be) == 0x112be, ".tsl9_code_000112be plan");
ASSERT(SIZEOF(.tsl9_code_000112be) == 160, ".tsl9_code_000112be size");
ASSERT(ADDR(.tsl9_code_00011844) == 0x11844, ".tsl9_code_00011844 plan");
ASSERT(SIZEOF(.tsl9_code_00011844) == 2884, ".tsl9_code_00011844 size");
ASSERT(ADDR(.tsl9_code_00012388) == 0x12388, ".tsl9_code_00012388 plan");
ASSERT(SIZEOF(.tsl9_code_00012388) == 328, ".tsl9_code_00012388 size");
ASSERT(ADDR(.tsl9_code_00012780) == 0x12780, ".tsl9_code_00012780 plan");
ASSERT(SIZEOF(.tsl9_code_00012780) == 160, ".tsl9_code_00012780 size");
ASSERT(ADDR(.tsl9_code_00012820) == 0x12820, ".tsl9_code_00012820 plan");
ASSERT(SIZEOF(.tsl9_code_00012820) == 68, ".tsl9_code_00012820 size");
ASSERT(ADDR(.tsl9_code_00012864) == 0x12864, ".tsl9_code_00012864 plan");
ASSERT(SIZEOF(.tsl9_code_00012864) == 86, ".tsl9_code_00012864 size");
ASSERT(ADDR(.tsl9_code_000128ec) == 0x128ec, ".tsl9_code_000128ec plan");
ASSERT(SIZEOF(.tsl9_code_000128ec) == 30, ".tsl9_code_000128ec size");
ASSERT(ADDR(.tsl9_code_0001290a) == 0x1290a, ".tsl9_code_0001290a plan");
ASSERT(SIZEOF(.tsl9_code_0001290a) == 18, ".tsl9_code_0001290a size");
ASSERT(ADDR(.tsl9_code_0001291c) == 0x1291c, ".tsl9_code_0001291c plan");
ASSERT(SIZEOF(.tsl9_code_0001291c) == 188, ".tsl9_code_0001291c size");
ASSERT(ADDR(.tsl9_code_000129d8) == 0x129d8, ".tsl9_code_000129d8 plan");
ASSERT(SIZEOF(.tsl9_code_000129d8) == 92, ".tsl9_code_000129d8 size");
ASSERT(ADDR(.tsl9_code_00012a34) == 0x12a34, ".tsl9_code_00012a34 plan");
ASSERT(SIZEOF(.tsl9_code_00012a34) == 52, ".tsl9_code_00012a34 size");
ASSERT(ADDR(.tsl9_code_00012a68) == 0x12a68, ".tsl9_code_00012a68 plan");
ASSERT(SIZEOF(.tsl9_code_00012a68) == 308, ".tsl9_code_00012a68 size");
ASSERT(ADDR(.tsl9_code_00012b9c) == 0x12b9c, ".tsl9_code_00012b9c plan");
ASSERT(SIZEOF(.tsl9_code_00012b9c) == 194, ".tsl9_code_00012b9c size");
ASSERT(ADDR(.tsl9_code_00012c5e) == 0x12c5e, ".tsl9_code_00012c5e plan");
ASSERT(SIZEOF(.tsl9_code_00012c5e) == 50, ".tsl9_code_00012c5e size");
ASSERT(ADDR(.tsl9_code_00012c90) == 0x12c90, ".tsl9_code_00012c90 plan");
ASSERT(SIZEOF(.tsl9_code_00012c90) == 118, ".tsl9_code_00012c90 size");
ASSERT(ADDR(.tsl9_code_00012d06) == 0x12d06, ".tsl9_code_00012d06 plan");
ASSERT(SIZEOF(.tsl9_code_00012d06) == 50, ".tsl9_code_00012d06 size");
ASSERT(ADDR(.tsl9_code_00012d38) == 0x12d38, ".tsl9_code_00012d38 plan");
ASSERT(SIZEOF(.tsl9_code_00012d38) == 48, ".tsl9_code_00012d38 size");
ASSERT(ADDR(.tsl9_code_00012d68) == 0x12d68, ".tsl9_code_00012d68 plan");
ASSERT(SIZEOF(.tsl9_code_00012d68) == 50, ".tsl9_code_00012d68 size");
ASSERT(ADDR(.tsl9_code_00012d9a) == 0x12d9a, ".tsl9_code_00012d9a plan");
ASSERT(SIZEOF(.tsl9_code_00012d9a) == 216, ".tsl9_code_00012d9a size");
ASSERT(ADDR(.tsl9_code_00012e72) == 0x12e72, ".tsl9_code_00012e72 plan");
ASSERT(SIZEOF(.tsl9_code_00012e72) == 50, ".tsl9_code_00012e72 size");
ASSERT(ADDR(.tsl9_code_00012ea4) == 0x12ea4, ".tsl9_code_00012ea4 plan");
ASSERT(SIZEOF(.tsl9_code_00012ea4) == 82, ".tsl9_code_00012ea4 size");
ASSERT(ADDR(.tsl9_code_00012ef6) == 0x12ef6, ".tsl9_code_00012ef6 plan");
ASSERT(SIZEOF(.tsl9_code_00012ef6) == 50, ".tsl9_code_00012ef6 size");
ASSERT(ADDR(.tsl9_code_00012f28) == 0x12f28, ".tsl9_code_00012f28 plan");
ASSERT(SIZEOF(.tsl9_code_00012f28) == 48, ".tsl9_code_00012f28 size");
ASSERT(ADDR(.tsl9_code_00012f58) == 0x12f58, ".tsl9_code_00012f58 plan");
ASSERT(SIZEOF(.tsl9_code_00012f58) == 50, ".tsl9_code_00012f58 size");
ASSERT(ADDR(.tsl9_code_00012f8a) == 0x12f8a, ".tsl9_code_00012f8a plan");
ASSERT(SIZEOF(.tsl9_code_00012f8a) == 82, ".tsl9_code_00012f8a size");
ASSERT(ADDR(.tsl9_code_00012fdc) == 0x12fdc, ".tsl9_code_00012fdc plan");
ASSERT(SIZEOF(.tsl9_code_00012fdc) == 328, ".tsl9_code_00012fdc size");
ASSERT(ADDR(.tsl9_code_00013156) == 0x13156, ".tsl9_code_00013156 plan");
ASSERT(SIZEOF(.tsl9_code_00013156) == 10, ".tsl9_code_00013156 size");
ASSERT(ADDR(.tsl9_code_000133fa) == 0x133fa, ".tsl9_code_000133fa plan");
ASSERT(SIZEOF(.tsl9_code_000133fa) == 122, ".tsl9_code_000133fa size");
ASSERT(ADDR(.tsl9_code_00013960) == 0x13960, ".tsl9_code_00013960 plan");
ASSERT(SIZEOF(.tsl9_code_00013960) == 90, ".tsl9_code_00013960 size");
ASSERT(ADDR(.tsl9_code_00013af0) == 0x13af0, ".tsl9_code_00013af0 plan");
ASSERT(SIZEOF(.tsl9_code_00013af0) == 108, ".tsl9_code_00013af0 size");
ASSERT(ADDR(.tsl9_code_00013cac) == 0x13cac, ".tsl9_code_00013cac plan");
ASSERT(SIZEOF(.tsl9_code_00013cac) == 28, ".tsl9_code_00013cac size");
ASSERT(ADDR(.tsl9_code_00013cc8) == 0x13cc8, ".tsl9_code_00013cc8 plan");
ASSERT(SIZEOF(.tsl9_code_00013cc8) == 130, ".tsl9_code_00013cc8 size");
ASSERT(ADDR(.tsl9_code_00014a54) == 0x14a54, ".tsl9_code_00014a54 plan");
ASSERT(SIZEOF(.tsl9_code_00014a54) == 62, ".tsl9_code_00014a54 size");
ASSERT(ADDR(.tsl9_code_00014af8) == 0x14af8, ".tsl9_code_00014af8 plan");
ASSERT(SIZEOF(.tsl9_code_00014af8) == 1878, ".tsl9_code_00014af8 size");
ASSERT(ADDR(.tsl9_code_0001524e) == 0x1524e, ".tsl9_code_0001524e plan");
ASSERT(SIZEOF(.tsl9_code_0001524e) == 132, ".tsl9_code_0001524e size");
ASSERT(ADDR(.tsl9_code_00015378) == 0x15378, ".tsl9_code_00015378 plan");
ASSERT(SIZEOF(.tsl9_code_00015378) == 3494, ".tsl9_code_00015378 size");
ASSERT(ADDR(.tsl9_code_000165cc) == 0x165cc, ".tsl9_code_000165cc plan");
ASSERT(SIZEOF(.tsl9_code_000165cc) == 62, ".tsl9_code_000165cc size");
ASSERT(ADDR(.tsl9_code_0001660a) == 0x1660a, ".tsl9_code_0001660a plan");
ASSERT(SIZEOF(.tsl9_code_0001660a) == 72, ".tsl9_code_0001660a size");
ASSERT(ADDR(.tsl9_code_00016652) == 0x16652, ".tsl9_code_00016652 plan");
ASSERT(SIZEOF(.tsl9_code_00016652) == 96, ".tsl9_code_00016652 size");
ASSERT(ADDR(.tsl9_code_000166b2) == 0x166b2, ".tsl9_code_000166b2 plan");
ASSERT(SIZEOF(.tsl9_code_000166b2) == 86, ".tsl9_code_000166b2 size");
ASSERT(ADDR(.tsl9_code_00016708) == 0x16708, ".tsl9_code_00016708 plan");
ASSERT(SIZEOF(.tsl9_code_00016708) == 72, ".tsl9_code_00016708 size");
ASSERT(ADDR(.tsl9_code_00016750) == 0x16750, ".tsl9_code_00016750 plan");
ASSERT(SIZEOF(.tsl9_code_00016750) == 84, ".tsl9_code_00016750 size");
ASSERT(ADDR(.tsl9_code_000167a4) == 0x167a4, ".tsl9_code_000167a4 plan");
ASSERT(SIZEOF(.tsl9_code_000167a4) == 76, ".tsl9_code_000167a4 size");
ASSERT(ADDR(.tsl9_code_000167f0) == 0x167f0, ".tsl9_code_000167f0 plan");
ASSERT(SIZEOF(.tsl9_code_000167f0) == 142, ".tsl9_code_000167f0 size");
ASSERT(ADDR(.tsl9_code_0001687e) == 0x1687e, ".tsl9_code_0001687e plan");
ASSERT(SIZEOF(.tsl9_code_0001687e) == 70, ".tsl9_code_0001687e size");
ASSERT(ADDR(.tsl9_code_000168f0) == 0x168f0, ".tsl9_code_000168f0 plan");
ASSERT(SIZEOF(.tsl9_code_000168f0) == 246, ".tsl9_code_000168f0 size");
ASSERT(ADDR(.tsl9_code_00016a38) == 0x16a38, ".tsl9_code_00016a38 plan");
ASSERT(SIZEOF(.tsl9_code_00016a38) == 232, ".tsl9_code_00016a38 size");
ASSERT(ADDR(.tsl9_code_00016b20) == 0x16b20, ".tsl9_code_00016b20 plan");
ASSERT(SIZEOF(.tsl9_code_00016b20) == 40, ".tsl9_code_00016b20 size");
ASSERT(ADDR(.tsl9_code_00016b48) == 0x16b48, ".tsl9_code_00016b48 plan");
ASSERT(SIZEOF(.tsl9_code_00016b48) == 48, ".tsl9_code_00016b48 size");
ASSERT(ADDR(.tsl9_code_00016d22) == 0x16d22, ".tsl9_code_00016d22 plan");
ASSERT(SIZEOF(.tsl9_code_00016d22) == 76, ".tsl9_code_00016d22 size");
ASSERT(ADDR(.tsl9_code_00016d6e) == 0x16d6e, ".tsl9_code_00016d6e plan");
ASSERT(SIZEOF(.tsl9_code_00016d6e) == 62, ".tsl9_code_00016d6e size");
ASSERT(ADDR(.tsl9_code_00016dac) == 0x16dac, ".tsl9_code_00016dac plan");
ASSERT(SIZEOF(.tsl9_code_00016dac) == 378, ".tsl9_code_00016dac size");
ASSERT(ADDR(.tsl9_code_00016f4a) == 0x16f4a, ".tsl9_code_00016f4a plan");
ASSERT(SIZEOF(.tsl9_code_00016f4a) == 218, ".tsl9_code_00016f4a size");
ASSERT(ADDR(.tsl9_code_00017048) == 0x17048, ".tsl9_code_00017048 plan");
ASSERT(SIZEOF(.tsl9_code_00017048) == 154, ".tsl9_code_00017048 size");
ASSERT(ADDR(.tsl9_code_00017176) == 0x17176, ".tsl9_code_00017176 plan");
ASSERT(SIZEOF(.tsl9_code_00017176) == 76, ".tsl9_code_00017176 size");
ASSERT(ADDR(.tsl9_code_000171c2) == 0x171c2, ".tsl9_code_000171c2 plan");
ASSERT(SIZEOF(.tsl9_code_000171c2) == 84, ".tsl9_code_000171c2 size");
ASSERT(ADDR(.tsl9_code_00017216) == 0x17216, ".tsl9_code_00017216 plan");
ASSERT(SIZEOF(.tsl9_code_00017216) == 52, ".tsl9_code_00017216 size");
ASSERT(ADDR(.tsl9_code_0001724a) == 0x1724a, ".tsl9_code_0001724a plan");
ASSERT(SIZEOF(.tsl9_code_0001724a) == 120, ".tsl9_code_0001724a size");
ASSERT(ADDR(.tsl9_code_000172c2) == 0x172c2, ".tsl9_code_000172c2 plan");
ASSERT(SIZEOF(.tsl9_code_000172c2) == 76, ".tsl9_code_000172c2 size");
ASSERT(ADDR(.tsl9_code_0001730e) == 0x1730e, ".tsl9_code_0001730e plan");
ASSERT(SIZEOF(.tsl9_code_0001730e) == 174, ".tsl9_code_0001730e size");
ASSERT(ADDR(.tsl9_code_000173bc) == 0x173bc, ".tsl9_code_000173bc plan");
ASSERT(SIZEOF(.tsl9_code_000173bc) == 126, ".tsl9_code_000173bc size");
ASSERT(ADDR(.tsl9_code_0001743a) == 0x1743a, ".tsl9_code_0001743a plan");
ASSERT(SIZEOF(.tsl9_code_0001743a) == 58, ".tsl9_code_0001743a size");
ASSERT(ADDR(.tsl9_code_00017474) == 0x17474, ".tsl9_code_00017474 plan");
ASSERT(SIZEOF(.tsl9_code_00017474) == 88, ".tsl9_code_00017474 size");
ASSERT(ADDR(.tsl9_code_000174cc) == 0x174cc, ".tsl9_code_000174cc plan");
ASSERT(SIZEOF(.tsl9_code_000174cc) == 388, ".tsl9_code_000174cc size");
ASSERT(ADDR(.tsl9_code_00017650) == 0x17650, ".tsl9_code_00017650 plan");
ASSERT(SIZEOF(.tsl9_code_00017650) == 124, ".tsl9_code_00017650 size");
ASSERT(ADDR(.tsl9_code_000176cc) == 0x176cc, ".tsl9_code_000176cc plan");
ASSERT(SIZEOF(.tsl9_code_000176cc) == 80, ".tsl9_code_000176cc size");
ASSERT(ADDR(.tsl9_code_0001771c) == 0x1771c, ".tsl9_code_0001771c plan");
ASSERT(SIZEOF(.tsl9_code_0001771c) == 66, ".tsl9_code_0001771c size");
ASSERT(ADDR(.tsl9_code_0001775e) == 0x1775e, ".tsl9_code_0001775e plan");
ASSERT(SIZEOF(.tsl9_code_0001775e) == 114, ".tsl9_code_0001775e size");
ASSERT(ADDR(.tsl9_code_00017966) == 0x17966, ".tsl9_code_00017966 plan");
ASSERT(SIZEOF(.tsl9_code_00017966) == 50, ".tsl9_code_00017966 size");
ASSERT(ADDR(.tsl9_code_00017998) == 0x17998, ".tsl9_code_00017998 plan");
ASSERT(SIZEOF(.tsl9_code_00017998) == 50, ".tsl9_code_00017998 size");
ASSERT(ADDR(.tsl9_code_000179ca) == 0x179ca, ".tsl9_code_000179ca plan");
ASSERT(SIZEOF(.tsl9_code_000179ca) == 88, ".tsl9_code_000179ca size");
ASSERT(ADDR(.tsl9_code_00017a22) == 0x17a22, ".tsl9_code_00017a22 plan");
ASSERT(SIZEOF(.tsl9_code_00017a22) == 98, ".tsl9_code_00017a22 size");
ASSERT(ADDR(.tsl9_code_00017d52) == 0x17d52, ".tsl9_code_00017d52 plan");
ASSERT(SIZEOF(.tsl9_code_00017d52) == 168, ".tsl9_code_00017d52 size");
ASSERT(ADDR(.tsl9_code_00017dfa) == 0x17dfa, ".tsl9_code_00017dfa plan");
ASSERT(SIZEOF(.tsl9_code_00017dfa) == 44, ".tsl9_code_00017dfa size");
ASSERT(ADDR(.tsl9_code_0001836c) == 0x1836c, ".tsl9_code_0001836c plan");
ASSERT(SIZEOF(.tsl9_code_0001836c) == 24, ".tsl9_code_0001836c size");
ASSERT(ADDR(.tsl9_code_0001838c) == 0x1838c, ".tsl9_code_0001838c plan");
ASSERT(SIZEOF(.tsl9_code_0001838c) == 2, ".tsl9_code_0001838c size");
ASSERT(ADDR(.tsl9_code_0001838e) == 0x1838e, ".tsl9_code_0001838e plan");
ASSERT(SIZEOF(.tsl9_code_0001838e) == 2, ".tsl9_code_0001838e size");
ASSERT(ADDR(.tsl9_code_00018390) == 0x18390, ".tsl9_code_00018390 plan");
ASSERT(SIZEOF(.tsl9_code_00018390) == 2, ".tsl9_code_00018390 size");
ASSERT(ADDR(.tsl9_code_00018392) == 0x18392, ".tsl9_code_00018392 plan");
ASSERT(SIZEOF(.tsl9_code_00018392) == 2, ".tsl9_code_00018392 size");
ASSERT(ADDR(.tsl9_code_00018394) == 0x18394, ".tsl9_code_00018394 plan");
ASSERT(SIZEOF(.tsl9_code_00018394) == 2, ".tsl9_code_00018394 size");
ASSERT(ADDR(.tsl9_code_00018396) == 0x18396, ".tsl9_code_00018396 plan");
ASSERT(SIZEOF(.tsl9_code_00018396) == 2, ".tsl9_code_00018396 size");
ASSERT(ADDR(.tsl9_code_00018398) == 0x18398, ".tsl9_code_00018398 plan");
ASSERT(SIZEOF(.tsl9_code_00018398) == 2, ".tsl9_code_00018398 size");
ASSERT(ADDR(.tsl9_code_0001839a) == 0x1839a, ".tsl9_code_0001839a plan");
ASSERT(SIZEOF(.tsl9_code_0001839a) == 2, ".tsl9_code_0001839a size");
ASSERT(ADDR(.tsl9_code_0001839c) == 0x1839c, ".tsl9_code_0001839c plan");
ASSERT(SIZEOF(.tsl9_code_0001839c) == 2, ".tsl9_code_0001839c size");
ASSERT(ADDR(.tsl9_code_0001839e) == 0x1839e, ".tsl9_code_0001839e plan");
ASSERT(SIZEOF(.tsl9_code_0001839e) == 2, ".tsl9_code_0001839e size");
ASSERT(ADDR(.tsl9_code_000183a0) == 0x183a0, ".tsl9_code_000183a0 plan");
ASSERT(SIZEOF(.tsl9_code_000183a0) == 2, ".tsl9_code_000183a0 size");
ASSERT(ADDR(.tsl9_code_000183a2) == 0x183a2, ".tsl9_code_000183a2 plan");
ASSERT(SIZEOF(.tsl9_code_000183a2) == 2, ".tsl9_code_000183a2 size");
ASSERT(ADDR(.tsl9_code_000183a4) == 0x183a4, ".tsl9_code_000183a4 plan");
ASSERT(SIZEOF(.tsl9_code_000183a4) == 2, ".tsl9_code_000183a4 size");
ASSERT(ADDR(.tsl9_code_000183a6) == 0x183a6, ".tsl9_code_000183a6 plan");
ASSERT(SIZEOF(.tsl9_code_000183a6) == 2, ".tsl9_code_000183a6 size");
ASSERT(ADDR(.tsl9_code_000183a8) == 0x183a8, ".tsl9_code_000183a8 plan");
ASSERT(SIZEOF(.tsl9_code_000183a8) == 2, ".tsl9_code_000183a8 size");
ASSERT(ADDR(.tsl9_code_000183aa) == 0x183aa, ".tsl9_code_000183aa plan");
ASSERT(SIZEOF(.tsl9_code_000183aa) == 2, ".tsl9_code_000183aa size");
ASSERT(ADDR(.tsl9_code_000183ac) == 0x183ac, ".tsl9_code_000183ac plan");
ASSERT(SIZEOF(.tsl9_code_000183ac) == 2, ".tsl9_code_000183ac size");
ASSERT(ADDR(.tsl9_code_000183ae) == 0x183ae, ".tsl9_code_000183ae plan");
ASSERT(SIZEOF(.tsl9_code_000183ae) == 2, ".tsl9_code_000183ae size");
ASSERT(ADDR(.tsl9_code_000183b0) == 0x183b0, ".tsl9_code_000183b0 plan");
ASSERT(SIZEOF(.tsl9_code_000183b0) == 2, ".tsl9_code_000183b0 size");
ASSERT(ADDR(.tsl9_code_000183b2) == 0x183b2, ".tsl9_code_000183b2 plan");
ASSERT(SIZEOF(.tsl9_code_000183b2) == 2, ".tsl9_code_000183b2 size");
ASSERT(ADDR(.tsl9_code_000183b4) == 0x183b4, ".tsl9_code_000183b4 plan");
ASSERT(SIZEOF(.tsl9_code_000183b4) == 2, ".tsl9_code_000183b4 size");
ASSERT(ADDR(.tsl9_code_000183b6) == 0x183b6, ".tsl9_code_000183b6 plan");
ASSERT(SIZEOF(.tsl9_code_000183b6) == 2, ".tsl9_code_000183b6 size");
ASSERT(ADDR(.tsl9_code_000183b8) == 0x183b8, ".tsl9_code_000183b8 plan");
ASSERT(SIZEOF(.tsl9_code_000183b8) == 2, ".tsl9_code_000183b8 size");
ASSERT(ADDR(.tsl9_code_000183bc) == 0x183bc, ".tsl9_code_000183bc plan");
ASSERT(SIZEOF(.tsl9_code_000183bc) == 2, ".tsl9_code_000183bc size");
ASSERT(ADDR(.tsl9_code_000183be) == 0x183be, ".tsl9_code_000183be plan");
ASSERT(SIZEOF(.tsl9_code_000183be) == 2, ".tsl9_code_000183be size");
ASSERT(ADDR(.tsl9_code_000183c2) == 0x183c2, ".tsl9_code_000183c2 plan");
ASSERT(SIZEOF(.tsl9_code_000183c2) == 2, ".tsl9_code_000183c2 size");
ASSERT(ADDR(.tsl9_code_000183c4) == 0x183c4, ".tsl9_code_000183c4 plan");
ASSERT(SIZEOF(.tsl9_code_000183c4) == 2, ".tsl9_code_000183c4 size");
ASSERT(ADDR(.tsl9_code_000183c6) == 0x183c6, ".tsl9_code_000183c6 plan");
ASSERT(SIZEOF(.tsl9_code_000183c6) == 2, ".tsl9_code_000183c6 size");
ASSERT(ADDR(.tsl9_code_000183c8) == 0x183c8, ".tsl9_code_000183c8 plan");
ASSERT(SIZEOF(.tsl9_code_000183c8) == 2, ".tsl9_code_000183c8 size");
ASSERT(ADDR(.tsl9_code_000183ca) == 0x183ca, ".tsl9_code_000183ca plan");
ASSERT(SIZEOF(.tsl9_code_000183ca) == 2, ".tsl9_code_000183ca size");
ASSERT(ADDR(.tsl9_code_000183ce) == 0x183ce, ".tsl9_code_000183ce plan");
ASSERT(SIZEOF(.tsl9_code_000183ce) == 2, ".tsl9_code_000183ce size");
ASSERT(ADDR(.tsl9_code_000183d0) == 0x183d0, ".tsl9_code_000183d0 plan");
ASSERT(SIZEOF(.tsl9_code_000183d0) == 2, ".tsl9_code_000183d0 size");
ASSERT(ADDR(.tsl9_code_000183d2) == 0x183d2, ".tsl9_code_000183d2 plan");
ASSERT(SIZEOF(.tsl9_code_000183d2) == 2, ".tsl9_code_000183d2 size");
ASSERT(ADDR(.tsl9_code_000183d4) == 0x183d4, ".tsl9_code_000183d4 plan");
ASSERT(SIZEOF(.tsl9_code_000183d4) == 2, ".tsl9_code_000183d4 size");
ASSERT(ADDR(.tsl9_code_000183d6) == 0x183d6, ".tsl9_code_000183d6 plan");
ASSERT(SIZEOF(.tsl9_code_000183d6) == 2, ".tsl9_code_000183d6 size");
ASSERT(ADDR(.tsl9_code_000183d8) == 0x183d8, ".tsl9_code_000183d8 plan");
ASSERT(SIZEOF(.tsl9_code_000183d8) == 2, ".tsl9_code_000183d8 size");
ASSERT(ADDR(.tsl9_code_000183da) == 0x183da, ".tsl9_code_000183da plan");
ASSERT(SIZEOF(.tsl9_code_000183da) == 2, ".tsl9_code_000183da size");
ASSERT(ADDR(.tsl9_code_000183dc) == 0x183dc, ".tsl9_code_000183dc plan");
ASSERT(SIZEOF(.tsl9_code_000183dc) == 2, ".tsl9_code_000183dc size");
ASSERT(ADDR(.tsl9_code_000183de) == 0x183de, ".tsl9_code_000183de plan");
ASSERT(SIZEOF(.tsl9_code_000183de) == 2, ".tsl9_code_000183de size");
ASSERT(ADDR(.tsl9_code_000183e0) == 0x183e0, ".tsl9_code_000183e0 plan");
ASSERT(SIZEOF(.tsl9_code_000183e0) == 2, ".tsl9_code_000183e0 size");
ASSERT(ADDR(.tsl9_code_000183e2) == 0x183e2, ".tsl9_code_000183e2 plan");
ASSERT(SIZEOF(.tsl9_code_000183e2) == 2, ".tsl9_code_000183e2 size");
ASSERT(ADDR(.tsl9_code_000183e6) == 0x183e6, ".tsl9_code_000183e6 plan");
ASSERT(SIZEOF(.tsl9_code_000183e6) == 2, ".tsl9_code_000183e6 size");
ASSERT(ADDR(.tsl9_code_000183e8) == 0x183e8, ".tsl9_code_000183e8 plan");
ASSERT(SIZEOF(.tsl9_code_000183e8) == 2, ".tsl9_code_000183e8 size");
ASSERT(ADDR(.tsl9_code_000183ea) == 0x183ea, ".tsl9_code_000183ea plan");
ASSERT(SIZEOF(.tsl9_code_000183ea) == 2, ".tsl9_code_000183ea size");
ASSERT(ADDR(.tsl9_code_000183ec) == 0x183ec, ".tsl9_code_000183ec plan");
ASSERT(SIZEOF(.tsl9_code_000183ec) == 2, ".tsl9_code_000183ec size");
ASSERT(ADDR(.tsl9_code_000183ee) == 0x183ee, ".tsl9_code_000183ee plan");
ASSERT(SIZEOF(.tsl9_code_000183ee) == 2, ".tsl9_code_000183ee size");
ASSERT(ADDR(.tsl9_code_000183f4) == 0x183f4, ".tsl9_code_000183f4 plan");
ASSERT(SIZEOF(.tsl9_code_000183f4) == 2, ".tsl9_code_000183f4 size");
ASSERT(ADDR(.tsl9_code_000183f6) == 0x183f6, ".tsl9_code_000183f6 plan");
ASSERT(SIZEOF(.tsl9_code_000183f6) == 2, ".tsl9_code_000183f6 size");
ASSERT(ADDR(.tsl9_code_000183f8) == 0x183f8, ".tsl9_code_000183f8 plan");
ASSERT(SIZEOF(.tsl9_code_000183f8) == 2, ".tsl9_code_000183f8 size");
ASSERT(ADDR(.tsl9_code_000183fa) == 0x183fa, ".tsl9_code_000183fa plan");
ASSERT(SIZEOF(.tsl9_code_000183fa) == 2, ".tsl9_code_000183fa size");
ASSERT(ADDR(.tsl9_code_000183fc) == 0x183fc, ".tsl9_code_000183fc plan");
ASSERT(SIZEOF(.tsl9_code_000183fc) == 2, ".tsl9_code_000183fc size");
ASSERT(ADDR(.tsl9_code_000183fe) == 0x183fe, ".tsl9_code_000183fe plan");
ASSERT(SIZEOF(.tsl9_code_000183fe) == 148, ".tsl9_code_000183fe size");
ASSERT(ADDR(.tsl9_code_00018492) == 0x18492, ".tsl9_code_00018492 plan");
ASSERT(SIZEOF(.tsl9_code_00018492) == 12, ".tsl9_code_00018492 size");
ASSERT(ADDR(.tsl9_code_0001849e) == 0x1849e, ".tsl9_code_0001849e plan");
ASSERT(SIZEOF(.tsl9_code_0001849e) == 234, ".tsl9_code_0001849e size");
ASSERT(ADDR(.tsl9_code_00018588) == 0x18588, ".tsl9_code_00018588 plan");
ASSERT(SIZEOF(.tsl9_code_00018588) == 174, ".tsl9_code_00018588 size");
ASSERT(ADDR(.tsl9_code_00018636) == 0x18636, ".tsl9_code_00018636 plan");
ASSERT(SIZEOF(.tsl9_code_00018636) == 76, ".tsl9_code_00018636 size");
ASSERT(ADDR(.tsl9_code_00018682) == 0x18682, ".tsl9_code_00018682 plan");
ASSERT(SIZEOF(.tsl9_code_00018682) == 88, ".tsl9_code_00018682 size");
ASSERT(ADDR(.tsl9_code_000186da) == 0x186da, ".tsl9_code_000186da plan");
ASSERT(SIZEOF(.tsl9_code_000186da) == 16, ".tsl9_code_000186da size");
ASSERT(ADDR(.tsl9_code_000186ea) == 0x186ea, ".tsl9_code_000186ea plan");
ASSERT(SIZEOF(.tsl9_code_000186ea) == 24, ".tsl9_code_000186ea size");
ASSERT(ADDR(.tsl9_code_00018702) == 0x18702, ".tsl9_code_00018702 plan");
ASSERT(SIZEOF(.tsl9_code_00018702) == 184, ".tsl9_code_00018702 size");
ASSERT(ADDR(.tsl9_code_000187ba) == 0x187ba, ".tsl9_code_000187ba plan");
ASSERT(SIZEOF(.tsl9_code_000187ba) == 8, ".tsl9_code_000187ba size");
ASSERT(ADDR(.tsl9_code_000187c2) == 0x187c2, ".tsl9_code_000187c2 plan");
ASSERT(SIZEOF(.tsl9_code_000187c2) == 32, ".tsl9_code_000187c2 size");
ASSERT(ADDR(.tsl9_code_000187e2) == 0x187e2, ".tsl9_code_000187e2 plan");
ASSERT(SIZEOF(.tsl9_code_000187e2) == 10, ".tsl9_code_000187e2 size");
ASSERT(ADDR(.tsl9_code_000187ec) == 0x187ec, ".tsl9_code_000187ec plan");
ASSERT(SIZEOF(.tsl9_code_000187ec) == 24, ".tsl9_code_000187ec size");
ASSERT(ADDR(.tsl9_code_00018804) == 0x18804, ".tsl9_code_00018804 plan");
ASSERT(SIZEOF(.tsl9_code_00018804) == 242, ".tsl9_code_00018804 size");
ASSERT(ADDR(.tsl9_code_000188f6) == 0x188f6, ".tsl9_code_000188f6 plan");
ASSERT(SIZEOF(.tsl9_code_000188f6) == 258, ".tsl9_code_000188f6 size");
ASSERT(ADDR(.tsl9_code_000189f8) == 0x189f8, ".tsl9_code_000189f8 plan");
ASSERT(SIZEOF(.tsl9_code_000189f8) == 212, ".tsl9_code_000189f8 size");
ASSERT(ADDR(.tsl9_code_00018acc) == 0x18acc, ".tsl9_code_00018acc plan");
ASSERT(SIZEOF(.tsl9_code_00018acc) == 164, ".tsl9_code_00018acc size");
ASSERT(ADDR(.tsl9_code_00018b70) == 0x18b70, ".tsl9_code_00018b70 plan");
ASSERT(SIZEOF(.tsl9_code_00018b70) == 106, ".tsl9_code_00018b70 size");
ASSERT(ADDR(.tsl9_code_00018bda) == 0x18bda, ".tsl9_code_00018bda plan");
ASSERT(SIZEOF(.tsl9_code_00018bda) == 10, ".tsl9_code_00018bda size");
ASSERT(ADDR(.tsl9_code_00018be4) == 0x18be4, ".tsl9_code_00018be4 plan");
ASSERT(SIZEOF(.tsl9_code_00018be4) == 8, ".tsl9_code_00018be4 size");
ASSERT(ADDR(.tsl9_code_00018bec) == 0x18bec, ".tsl9_code_00018bec plan");
ASSERT(SIZEOF(.tsl9_code_00018bec) == 30, ".tsl9_code_00018bec size");
ASSERT(ADDR(.tsl9_code_00018c0a) == 0x18c0a, ".tsl9_code_00018c0a plan");
ASSERT(SIZEOF(.tsl9_code_00018c0a) == 14, ".tsl9_code_00018c0a size");
ASSERT(ADDR(.tsl9_code_00018c18) == 0x18c18, ".tsl9_code_00018c18 plan");
ASSERT(SIZEOF(.tsl9_code_00018c18) == 46, ".tsl9_code_00018c18 size");
ASSERT(ADDR(.tsl9_code_00018c46) == 0x18c46, ".tsl9_code_00018c46 plan");
ASSERT(SIZEOF(.tsl9_code_00018c46) == 100, ".tsl9_code_00018c46 size");
ASSERT(ADDR(.tsl9_code_00018caa) == 0x18caa, ".tsl9_code_00018caa plan");
ASSERT(SIZEOF(.tsl9_code_00018caa) == 50, ".tsl9_code_00018caa size");
ASSERT(ADDR(.tsl9_code_00018cdc) == 0x18cdc, ".tsl9_code_00018cdc plan");
ASSERT(SIZEOF(.tsl9_code_00018cdc) == 194, ".tsl9_code_00018cdc size");
ASSERT(ADDR(.tsl9_code_00018d9e) == 0x18d9e, ".tsl9_code_00018d9e plan");
ASSERT(SIZEOF(.tsl9_code_00018d9e) == 44, ".tsl9_code_00018d9e size");
ASSERT(ADDR(.tsl9_code_00018dca) == 0x18dca, ".tsl9_code_00018dca plan");
ASSERT(SIZEOF(.tsl9_code_00018dca) == 22, ".tsl9_code_00018dca size");
ASSERT(ADDR(.tsl9_code_00018de0) == 0x18de0, ".tsl9_code_00018de0 plan");
ASSERT(SIZEOF(.tsl9_code_00018de0) == 18, ".tsl9_code_00018de0 size");
ASSERT(ADDR(.tsl9_code_00018df2) == 0x18df2, ".tsl9_code_00018df2 plan");
ASSERT(SIZEOF(.tsl9_code_00018df2) == 40, ".tsl9_code_00018df2 size");
ASSERT(ADDR(.tsl9_code_00018e1a) == 0x18e1a, ".tsl9_code_00018e1a plan");
ASSERT(SIZEOF(.tsl9_code_00018e1a) == 20, ".tsl9_code_00018e1a size");
ASSERT(ADDR(.tsl9_code_00018e2e) == 0x18e2e, ".tsl9_code_00018e2e plan");
ASSERT(SIZEOF(.tsl9_code_00018e2e) == 12, ".tsl9_code_00018e2e size");
ASSERT(ADDR(.tsl9_code_00018e3a) == 0x18e3a, ".tsl9_code_00018e3a plan");
ASSERT(SIZEOF(.tsl9_code_00018e3a) == 32, ".tsl9_code_00018e3a size");
ASSERT(ADDR(.tsl9_code_00018e5a) == 0x18e5a, ".tsl9_code_00018e5a plan");
ASSERT(SIZEOF(.tsl9_code_00018e5a) == 30, ".tsl9_code_00018e5a size");
ASSERT(ADDR(.tsl9_code_00018e78) == 0x18e78, ".tsl9_code_00018e78 plan");
ASSERT(SIZEOF(.tsl9_code_00018e78) == 30, ".tsl9_code_00018e78 size");
ASSERT(ADDR(.tsl9_code_00018e96) == 0x18e96, ".tsl9_code_00018e96 plan");
ASSERT(SIZEOF(.tsl9_code_00018e96) == 30, ".tsl9_code_00018e96 size");
ASSERT(ADDR(.tsl9_code_00018eb4) == 0x18eb4, ".tsl9_code_00018eb4 plan");
ASSERT(SIZEOF(.tsl9_code_00018eb4) == 30, ".tsl9_code_00018eb4 size");
ASSERT(ADDR(.tsl9_code_00018ed2) == 0x18ed2, ".tsl9_code_00018ed2 plan");
ASSERT(SIZEOF(.tsl9_code_00018ed2) == 30, ".tsl9_code_00018ed2 size");
ASSERT(ADDR(.tsl9_code_00018ef0) == 0x18ef0, ".tsl9_code_00018ef0 plan");
ASSERT(SIZEOF(.tsl9_code_00018ef0) == 18, ".tsl9_code_00018ef0 size");
ASSERT(ADDR(.tsl9_code_00018f02) == 0x18f02, ".tsl9_code_00018f02 plan");
ASSERT(SIZEOF(.tsl9_code_00018f02) == 24, ".tsl9_code_00018f02 size");
ASSERT(ADDR(.tsl9_code_00018f1a) == 0x18f1a, ".tsl9_code_00018f1a plan");
ASSERT(SIZEOF(.tsl9_code_00018f1a) == 90, ".tsl9_code_00018f1a size");
ASSERT(ADDR(.tsl9_code_00018f74) == 0x18f74, ".tsl9_code_00018f74 plan");
ASSERT(SIZEOF(.tsl9_code_00018f74) == 40, ".tsl9_code_00018f74 size");
ASSERT(ADDR(.tsl9_code_00018f9c) == 0x18f9c, ".tsl9_code_00018f9c plan");
ASSERT(SIZEOF(.tsl9_code_00018f9c) == 42, ".tsl9_code_00018f9c size");
ASSERT(ADDR(.tsl9_code_00018fc6) == 0x18fc6, ".tsl9_code_00018fc6 plan");
ASSERT(SIZEOF(.tsl9_code_00018fc6) == 16, ".tsl9_code_00018fc6 size");
ASSERT(ADDR(.tsl9_code_00018fd6) == 0x18fd6, ".tsl9_code_00018fd6 plan");
ASSERT(SIZEOF(.tsl9_code_00018fd6) == 20, ".tsl9_code_00018fd6 size");
ASSERT(ADDR(.tsl9_code_00018fea) == 0x18fea, ".tsl9_code_00018fea plan");
ASSERT(SIZEOF(.tsl9_code_00018fea) == 4, ".tsl9_code_00018fea size");
ASSERT(ADDR(.tsl9_code_00018fee) == 0x18fee, ".tsl9_code_00018fee plan");
ASSERT(SIZEOF(.tsl9_code_00018fee) == 1066, ".tsl9_code_00018fee size");
ASSERT(ADDR(.tsl9_code_00019418) == 0x19418, ".tsl9_code_00019418 plan");
ASSERT(SIZEOF(.tsl9_code_00019418) == 90, ".tsl9_code_00019418 size");
ASSERT(ADDR(.tsl9_code_00019472) == 0x19472, ".tsl9_code_00019472 plan");
ASSERT(SIZEOF(.tsl9_code_00019472) == 30, ".tsl9_code_00019472 size");
ASSERT(ADDR(.tsl9_code_00019490) == 0x19490, ".tsl9_code_00019490 plan");
ASSERT(SIZEOF(.tsl9_code_00019490) == 40, ".tsl9_code_00019490 size");
ASSERT(ADDR(.tsl9_code_000194b8) == 0x194b8, ".tsl9_code_000194b8 plan");
ASSERT(SIZEOF(.tsl9_code_000194b8) == 54, ".tsl9_code_000194b8 size");
ASSERT(ADDR(.tsl9_code_000194ee) == 0x194ee, ".tsl9_code_000194ee plan");
ASSERT(SIZEOF(.tsl9_code_000194ee) == 30, ".tsl9_code_000194ee size");
ASSERT(ADDR(.tsl9_code_0001950c) == 0x1950c, ".tsl9_code_0001950c plan");
ASSERT(SIZEOF(.tsl9_code_0001950c) == 6, ".tsl9_code_0001950c size");
ASSERT(ADDR(.tsl9_code_00019512) == 0x19512, ".tsl9_code_00019512 plan");
ASSERT(SIZEOF(.tsl9_code_00019512) == 50, ".tsl9_code_00019512 size");
ASSERT(ADDR(.tsl9_code_00019544) == 0x19544, ".tsl9_code_00019544 plan");
ASSERT(SIZEOF(.tsl9_code_00019544) == 364, ".tsl9_code_00019544 size");
ASSERT(ADDR(.tsl9_code_000196b0) == 0x196b0, ".tsl9_code_000196b0 plan");
ASSERT(SIZEOF(.tsl9_code_000196b0) == 134, ".tsl9_code_000196b0 size");
ASSERT(ADDR(.tsl9_code_00019736) == 0x19736, ".tsl9_code_00019736 plan");
ASSERT(SIZEOF(.tsl9_code_00019736) == 308, ".tsl9_code_00019736 size");
ASSERT(ADDR(.tsl9_code_0001986a) == 0x1986a, ".tsl9_code_0001986a plan");
ASSERT(SIZEOF(.tsl9_code_0001986a) == 64, ".tsl9_code_0001986a size");
ASSERT(ADDR(.tsl9_code_000198aa) == 0x198aa, ".tsl9_code_000198aa plan");
ASSERT(SIZEOF(.tsl9_code_000198aa) == 126, ".tsl9_code_000198aa size");
ASSERT(ADDR(.tsl9_code_00019928) == 0x19928, ".tsl9_code_00019928 plan");
ASSERT(SIZEOF(.tsl9_code_00019928) == 28, ".tsl9_code_00019928 size");
ASSERT(ADDR(.tsl9_code_00019944) == 0x19944, ".tsl9_code_00019944 plan");
ASSERT(SIZEOF(.tsl9_code_00019944) == 182, ".tsl9_code_00019944 size");
ASSERT(ADDR(.tsl9_ro_00019a84) == 0x19a84, ".tsl9_ro_00019a84 plan");
ASSERT(SIZEOF(.tsl9_ro_00019a84) == 13, ".tsl9_ro_00019a84 size");
ASSERT(ADDR(.tsl9_ro_0001a318) == 0x1a318, ".tsl9_ro_0001a318 plan");
ASSERT(SIZEOF(.tsl9_ro_0001a318) == 28, ".tsl9_ro_0001a318 size");
ASSERT(ADDR(.tsl9_ro_0001a33c) == 0x1a33c, ".tsl9_ro_0001a33c plan");
ASSERT(SIZEOF(.tsl9_ro_0001a33c) == 28, ".tsl9_ro_0001a33c size");
ASSERT(ADDR(.tsl9_ro_0001a358) == 0x1a358, ".tsl9_ro_0001a358 plan");
ASSERT(SIZEOF(.tsl9_ro_0001a358) == 32, ".tsl9_ro_0001a358 size");
ASSERT(ADDR(.tsl9_ro_0001a378) == 0x1a378, ".tsl9_ro_0001a378 plan");
ASSERT(SIZEOF(.tsl9_ro_0001a378) == 1012, ".tsl9_ro_0001a378 size");

/* R71 additional original callback; all earlier layout plans retained. */
SECTIONS { .tsl9_code_0000aeec 0xAEEC : { KEEP(*(.text.tsl9_runtime_unported_aeec)) } }
ASSERT(ADDR(.tsl9_code_0000aeec) == 0xAEEC, "AEEC original plan");
ASSERT(SIZEOF(.tsl9_code_0000aeec) == 44, "AEEC exact code size");

/* R72 bounded original callback; remaining original gaps stay unfilled. */
SECTIONS { .tsl9_code_000087c4 0x87C4 : { KEEP(*(.text.tsl9_runtime_unported_87c4)) } }
ASSERT(ADDR(.tsl9_code_000087c4) == 0x87C4, "87C4 original plan");
ASSERT(SIZEOF(.tsl9_code_000087c4) == 632, "87C4 exact code size");


/* R73 bounded direct-only code closure. Remaining address/data/ROM obligations stay external. */
SECTIONS { .tsl9_code_000081de 0x81DE : { KEEP(*(.text.tsl9_runtime_unported_81de)) } }
ASSERT(ADDR(.tsl9_code_000081de) == 0x81DE, "tsl9_runtime_unported_81de plan");
ASSERT(SIZEOF(.tsl9_code_000081de) == 16, "tsl9_runtime_unported_81de exact size");
SECTIONS { .tsl9_code_0000a128 0xA128 : { KEEP(*(.text.tsl9_runtime_unported_a128)) } }
ASSERT(ADDR(.tsl9_code_0000a128) == 0xA128, "tsl9_runtime_unported_a128 plan");
ASSERT(SIZEOF(.tsl9_code_0000a128) == 230, "tsl9_runtime_unported_a128 exact size");
SECTIONS { .tsl9_code_0000a212 0xA212 : { KEEP(*(.text.tsl9_runtime_unported_a212)) } }
ASSERT(ADDR(.tsl9_code_0000a212) == 0xA212, "tsl9_runtime_unported_a212 plan");
ASSERT(SIZEOF(.tsl9_code_0000a212) == 142, "tsl9_runtime_unported_a212 exact size");
SECTIONS { .tsl9_code_0000a886 0xA886 : { KEEP(*(.text.tsl9_runtime_unported_a886)) } }
ASSERT(ADDR(.tsl9_code_0000a886) == 0xA886, "tsl9_runtime_unported_a886 plan");
ASSERT(SIZEOF(.tsl9_code_0000a886) == 14, "tsl9_runtime_unported_a886 exact size");
SECTIONS { .tsl9_code_0000ab12 0xAB12 : { KEEP(*(.text.tsl9_runtime_unported_ab12)) } }
ASSERT(ADDR(.tsl9_code_0000ab12) == 0xAB12, "tsl9_runtime_unported_ab12 plan");
ASSERT(SIZEOF(.tsl9_code_0000ab12) == 10, "tsl9_runtime_unported_ab12 exact size");
SECTIONS { .tsl9_code_0000afc0 0xAFC0 : { KEEP(*(.text.tsl9_runtime_unported_afc0)) } }
ASSERT(ADDR(.tsl9_code_0000afc0) == 0xAFC0, "tsl9_runtime_unported_afc0 plan");
ASSERT(SIZEOF(.tsl9_code_0000afc0) == 6, "tsl9_runtime_unported_afc0 exact size");
SECTIONS { .tsl9_code_0000b3de 0xB3DE : { KEEP(*(.text.tsl9_runtime_unported_b3de)) } }
ASSERT(ADDR(.tsl9_code_0000b3de) == 0xB3DE, "tsl9_runtime_unported_b3de plan");
ASSERT(SIZEOF(.tsl9_code_0000b3de) == 18, "tsl9_runtime_unported_b3de exact size");
SECTIONS { .tsl9_code_0000b574 0xB574 : { KEEP(*(.text.tsl9_runtime_unported_b574)) } }
ASSERT(ADDR(.tsl9_code_0000b574) == 0xB574, "tsl9_runtime_unported_b574 plan");
ASSERT(SIZEOF(.tsl9_code_0000b574) == 10, "tsl9_runtime_unported_b574 exact size");
SECTIONS { .tsl9_code_0000c1f6 0xC1F6 : { KEEP(*(.text.tsl9_runtime_unported_c1f6)) } }
ASSERT(ADDR(.tsl9_code_0000c1f6) == 0xC1F6, "tsl9_runtime_unported_c1f6 plan");
ASSERT(SIZEOF(.tsl9_code_0000c1f6) == 10, "tsl9_runtime_unported_c1f6 exact size");
SECTIONS { .tsl9_code_0000cbae 0xCBAE : { KEEP(*(.text.tsl9_runtime_unported_cbae)) } }
ASSERT(ADDR(.tsl9_code_0000cbae) == 0xCBAE, "tsl9_runtime_unported_cbae plan");
ASSERT(SIZEOF(.tsl9_code_0000cbae) == 10, "tsl9_runtime_unported_cbae exact size");
SECTIONS { .tsl9_code_0000ceba 0xCEBA : { KEEP(*(.text.tsl9_runtime_unported_ceba)) } }
ASSERT(ADDR(.tsl9_code_0000ceba) == 0xCEBA, "tsl9_runtime_unported_ceba plan");
ASSERT(SIZEOF(.tsl9_code_0000ceba) == 32, "tsl9_runtime_unported_ceba exact size");
SECTIONS { .tsl9_code_0000d006 0xD006 : { KEEP(*(.text.tsl9_runtime_unported_d006)) } }
ASSERT(ADDR(.tsl9_code_0000d006) == 0xD006, "tsl9_runtime_unported_d006 plan");
ASSERT(SIZEOF(.tsl9_code_0000d006) == 10, "tsl9_runtime_unported_d006 exact size");
SECTIONS { .tsl9_code_0000d16e 0xD16E : { KEEP(*(.text.tsl9_runtime_unported_d16e)) } }
ASSERT(ADDR(.tsl9_code_0000d16e) == 0xD16E, "tsl9_runtime_unported_d16e plan");
ASSERT(SIZEOF(.tsl9_code_0000d16e) == 14, "tsl9_runtime_unported_d16e exact size");
SECTIONS { .tsl9_code_0000d24c 0xD24C : { KEEP(*(.text.tsl9_runtime_unported_d24c)) } }
ASSERT(ADDR(.tsl9_code_0000d24c) == 0xD24C, "tsl9_runtime_unported_d24c plan");
ASSERT(SIZEOF(.tsl9_code_0000d24c) == 14, "tsl9_runtime_unported_d24c exact size");
SECTIONS { .tsl9_code_0000f564 0xF564 : { KEEP(*(.text.tsl9_runtime_unported_f564)) } }
ASSERT(ADDR(.tsl9_code_0000f564) == 0xF564, "tsl9_runtime_unported_f564 plan");
ASSERT(SIZEOF(.tsl9_code_0000f564) == 10, "tsl9_runtime_unported_f564 exact size");
SECTIONS { .tsl9_code_0000f596 0xF596 : { KEEP(*(.text.tsl9_runtime_unported_f596)) } }
ASSERT(ADDR(.tsl9_code_0000f596) == 0xF596, "tsl9_runtime_unported_f596 plan");
ASSERT(SIZEOF(.tsl9_code_0000f596) == 10, "tsl9_runtime_unported_f596 exact size");
SECTIONS { .tsl9_code_0000f5c8 0xF5C8 : { KEEP(*(.text.tsl9_runtime_unported_f5c8)) } }
ASSERT(ADDR(.tsl9_code_0000f5c8) == 0xF5C8, "tsl9_runtime_unported_f5c8 plan");
ASSERT(SIZEOF(.tsl9_code_0000f5c8) == 10, "tsl9_runtime_unported_f5c8 exact size");
SECTIONS { .tsl9_code_0000f5fa 0xF5FA : { KEEP(*(.text.tsl9_runtime_unported_f5fa)) } }
ASSERT(ADDR(.tsl9_code_0000f5fa) == 0xF5FA, "tsl9_runtime_unported_f5fa plan");
ASSERT(SIZEOF(.tsl9_code_0000f5fa) == 10, "tsl9_runtime_unported_f5fa exact size");
SECTIONS { .tsl9_code_0000f848 0xF848 : { KEEP(*(.text.tsl9_runtime_unported_f848)) } }
ASSERT(ADDR(.tsl9_code_0000f848) == 0xF848, "tsl9_runtime_unported_f848 plan");
ASSERT(SIZEOF(.tsl9_code_0000f848) == 6, "tsl9_runtime_unported_f848 exact size");
SECTIONS { .tsl9_code_0000f8e0 0xF8E0 : { KEEP(*(.text.tsl9_runtime_unported_f8e0)) } }
ASSERT(ADDR(.tsl9_code_0000f8e0) == 0xF8E0, "tsl9_runtime_unported_f8e0 plan");
ASSERT(SIZEOF(.tsl9_code_0000f8e0) == 6, "tsl9_runtime_unported_f8e0 exact size");
SECTIONS { .tsl9_code_0000f8ec 0xF8EC : { KEEP(*(.text.tsl9_runtime_unported_f8ec)) } }
ASSERT(ADDR(.tsl9_code_0000f8ec) == 0xF8EC, "tsl9_runtime_unported_f8ec plan");
ASSERT(SIZEOF(.tsl9_code_0000f8ec) == 6, "tsl9_runtime_unported_f8ec exact size");
SECTIONS { .tsl9_code_00013160 0x13160 : { KEEP(*(.text.tsl9_runtime_unported_13160)) } }
ASSERT(ADDR(.tsl9_code_00013160) == 0x13160, "tsl9_runtime_unported_13160 plan");
ASSERT(SIZEOF(.tsl9_code_00013160) == 666, "tsl9_runtime_unported_13160 exact size");
SECTIONS { .tsl9_code_00013b5c 0x13B5C : { KEEP(*(.text.tsl9_runtime_unported_13b5c)) } }
ASSERT(ADDR(.tsl9_code_00013b5c) == 0x13B5C, "tsl9_runtime_unported_13b5c plan");
ASSERT(SIZEOF(.tsl9_code_00013b5c) == 140, "tsl9_runtime_unported_13b5c exact size");
SECTIONS { .tsl9_code_000168c4 0x168C4 : { KEEP(*(.text.tsl9_runtime_unported_168c4)) } }
ASSERT(ADDR(.tsl9_code_000168c4) == 0x168C4, "tsl9_runtime_unported_168c4 plan");
ASSERT(SIZEOF(.tsl9_code_000168c4) == 44, "tsl9_runtime_unported_168c4 exact size");
SECTIONS { .tsl9_code_00016b78 0x16B78 : { KEEP(*(.text.tsl9_runtime_unported_16b78)) } }
ASSERT(ADDR(.tsl9_code_00016b78) == 0x16B78, "tsl9_runtime_unported_16b78 plan");
ASSERT(SIZEOF(.tsl9_code_00016b78) == 124, "tsl9_runtime_unported_16b78 exact size");
SECTIONS { .tsl9_code_00016bf4 0x16BF4 : { KEEP(*(.text.tsl9_runtime_unported_16bf4)) } }
ASSERT(ADDR(.tsl9_code_00016bf4) == 0x16BF4, "tsl9_runtime_unported_16bf4 plan");
ASSERT(SIZEOF(.tsl9_code_00016bf4) == 120, "tsl9_runtime_unported_16bf4 exact size");
SECTIONS { .tsl9_code_00016c6c 0x16C6C : { KEEP(*(.text.tsl9_runtime_unported_16c6c)) } }
ASSERT(ADDR(.tsl9_code_00016c6c) == 0x16C6C, "tsl9_runtime_unported_16c6c plan");
ASSERT(SIZEOF(.tsl9_code_00016c6c) == 182, "tsl9_runtime_unported_16c6c exact size");
SECTIONS { .tsl9_code_00016f26 0x16F26 : { KEEP(*(.text.tsl9_runtime_unported_16f26)) } }
ASSERT(ADDR(.tsl9_code_00016f26) == 0x16F26, "tsl9_runtime_unported_16f26 plan");
ASSERT(SIZEOF(.tsl9_code_00016f26) == 36, "tsl9_runtime_unported_16f26 exact size");
SECTIONS { .tsl9_code_000170e2 0x170E2 : { KEEP(*(.text.tsl9_runtime_unported_170e2)) } }
ASSERT(ADDR(.tsl9_code_000170e2) == 0x170E2, "tsl9_runtime_unported_170e2 plan");
ASSERT(SIZEOF(.tsl9_code_000170e2) == 148, "tsl9_runtime_unported_170e2 exact size");
SECTIONS { .tsl9_code_00017f68 0x17F68 : { KEEP(*(.text.tsl9_runtime_unported_17f68)) } }
ASSERT(ADDR(.tsl9_code_00017f68) == 0x17F68, "tsl9_runtime_unported_17f68 plan");
ASSERT(SIZEOF(.tsl9_code_00017f68) == 10, "tsl9_runtime_unported_17f68 exact size");

/* R74 exact direct-only66body closure; no unknown gap fill. */
SECTIONS { .tsl9_code_000081f8 0x81F8 : { KEEP(*(.text.tsl9_runtime_unported_81f8)) } }
ASSERT(ADDR(.tsl9_code_000081f8) == 0x81F8, "tsl9_runtime_unported_81f8 plan");
ASSERT(SIZEOF(.tsl9_code_000081f8) == 10, "tsl9_runtime_unported_81f8 exact size");
SECTIONS { .tsl9_code_00009e8e 0x9E8E : { KEEP(*(.text.tsl9_runtime_unported_9e8e)) } }
ASSERT(ADDR(.tsl9_code_00009e8e) == 0x9E8E, "tsl9_runtime_unported_9e8e plan");
ASSERT(SIZEOF(.tsl9_code_00009e8e) == 6, "tsl9_runtime_unported_9e8e exact size");
SECTIONS { .tsl9_code_0000a894 0xA894 : { KEEP(*(.text.tsl9_runtime_unported_a894)) } }
ASSERT(ADDR(.tsl9_code_0000a894) == 0xA894, "tsl9_runtime_unported_a894 plan");
ASSERT(SIZEOF(.tsl9_code_0000a894) == 70, "tsl9_runtime_unported_a894 exact size");
SECTIONS { .tsl9_code_0000a8da 0xA8DA : { KEEP(*(.text.tsl9_runtime_unported_a8da)) } }
ASSERT(ADDR(.tsl9_code_0000a8da) == 0xA8DA, "tsl9_runtime_unported_a8da plan");
ASSERT(SIZEOF(.tsl9_code_0000a8da) == 34, "tsl9_runtime_unported_a8da exact size");
SECTIONS { .tsl9_code_0000aafe 0xAAFE : { KEEP(*(.text.tsl9_runtime_unported_aafe)) } }
ASSERT(ADDR(.tsl9_code_0000aafe) == 0xAAFE, "tsl9_runtime_unported_aafe plan");
ASSERT(SIZEOF(.tsl9_code_0000aafe) == 10, "tsl9_runtime_unported_aafe exact size");
SECTIONS { .tsl9_code_0000ab08 0xAB08 : { KEEP(*(.text.tsl9_runtime_unported_ab08)) } }
ASSERT(ADDR(.tsl9_code_0000ab08) == 0xAB08, "tsl9_runtime_unported_ab08 plan");
ASSERT(SIZEOF(.tsl9_code_0000ab08) == 10, "tsl9_runtime_unported_ab08 exact size");
SECTIONS { .tsl9_code_0000aea4 0xAEA4 : { KEEP(*(.text.tsl9_runtime_unported_aea4)) } }
ASSERT(ADDR(.tsl9_code_0000aea4) == 0xAEA4, "tsl9_runtime_unported_aea4 plan");
ASSERT(SIZEOF(.tsl9_code_0000aea4) == 50, "tsl9_runtime_unported_aea4 exact size");
SECTIONS { .tsl9_code_0000b228 0xB228 : { KEEP(*(.text.tsl9_runtime_unported_b228)) } }
ASSERT(ADDR(.tsl9_code_0000b228) == 0xB228, "tsl9_runtime_unported_b228 plan");
ASSERT(SIZEOF(.tsl9_code_0000b228) == 10, "tsl9_runtime_unported_b228 exact size");
SECTIONS { .tsl9_code_0000b232 0xB232 : { KEEP(*(.text.tsl9_runtime_unported_b232)) } }
ASSERT(ADDR(.tsl9_code_0000b232) == 0xB232, "tsl9_runtime_unported_b232 plan");
ASSERT(SIZEOF(.tsl9_code_0000b232) == 10, "tsl9_runtime_unported_b232 exact size");
SECTIONS { .tsl9_code_0000b23c 0xB23C : { KEEP(*(.text.tsl9_runtime_unported_b23c)) } }
ASSERT(ADDR(.tsl9_code_0000b23c) == 0xB23C, "tsl9_runtime_unported_b23c plan");
ASSERT(SIZEOF(.tsl9_code_0000b23c) == 10, "tsl9_runtime_unported_b23c exact size");
SECTIONS { .tsl9_code_0000b246 0xB246 : { KEEP(*(.text.tsl9_runtime_unported_b246)) } }
ASSERT(ADDR(.tsl9_code_0000b246) == 0xB246, "tsl9_runtime_unported_b246 plan");
ASSERT(SIZEOF(.tsl9_code_0000b246) == 10, "tsl9_runtime_unported_b246 exact size");
SECTIONS { .tsl9_code_0000c2fe 0xC2FE : { KEEP(*(.text.tsl9_runtime_unported_c2fe)) } }
ASSERT(ADDR(.tsl9_code_0000c2fe) == 0xC2FE, "tsl9_runtime_unported_c2fe plan");
ASSERT(SIZEOF(.tsl9_code_0000c2fe) == 16, "tsl9_runtime_unported_c2fe exact size");
SECTIONS { .tsl9_code_0000cea6 0xCEA6 : { KEEP(*(.text.tsl9_runtime_unported_cea6)) } }
ASSERT(ADDR(.tsl9_code_0000cea6) == 0xCEA6, "tsl9_runtime_unported_cea6 plan");
ASSERT(SIZEOF(.tsl9_code_0000cea6) == 10, "tsl9_runtime_unported_cea6 exact size");
SECTIONS { .tsl9_code_0000ceb0 0xCEB0 : { KEEP(*(.text.tsl9_runtime_unported_ceb0)) } }
ASSERT(ADDR(.tsl9_code_0000ceb0) == 0xCEB0, "tsl9_runtime_unported_ceb0 plan");
ASSERT(SIZEOF(.tsl9_code_0000ceb0) == 10, "tsl9_runtime_unported_ceb0 exact size");
SECTIONS { .tsl9_code_0000cfee 0xCFEE : { KEEP(*(.text.tsl9_runtime_unported_cfee)) } }
ASSERT(ADDR(.tsl9_code_0000cfee) == 0xCFEE, "tsl9_runtime_unported_cfee plan");
ASSERT(SIZEOF(.tsl9_code_0000cfee) == 6, "tsl9_runtime_unported_cfee exact size");
SECTIONS { .tsl9_code_0000d17c 0xD17C : { KEEP(*(.text.tsl9_runtime_unported_d17c)) } }
ASSERT(ADDR(.tsl9_code_0000d17c) == 0xD17C, "tsl9_runtime_unported_d17c plan");
ASSERT(SIZEOF(.tsl9_code_0000d17c) == 26, "tsl9_runtime_unported_d17c exact size");
SECTIONS { .tsl9_code_0000d2a6 0xD2A6 : { KEEP(*(.text.tsl9_runtime_unported_d2a6)) } }
ASSERT(ADDR(.tsl9_code_0000d2a6) == 0xD2A6, "tsl9_runtime_unported_d2a6 plan");
ASSERT(SIZEOF(.tsl9_code_0000d2a6) == 10, "tsl9_runtime_unported_d2a6 exact size");
SECTIONS { .tsl9_code_0000d31a 0xD31A : { KEEP(*(.text.tsl9_runtime_unported_d31a)) } }
ASSERT(ADDR(.tsl9_code_0000d31a) == 0xD31A, "tsl9_runtime_unported_d31a plan");
ASSERT(SIZEOF(.tsl9_code_0000d31a) == 10, "tsl9_runtime_unported_d31a exact size");
SECTIONS { .tsl9_code_0000d388 0xD388 : { KEEP(*(.text.tsl9_runtime_unported_d388)) } }
ASSERT(ADDR(.tsl9_code_0000d388) == 0xD388, "tsl9_runtime_unported_d388 plan");
ASSERT(SIZEOF(.tsl9_code_0000d388) == 10, "tsl9_runtime_unported_d388 exact size");
SECTIONS { .tsl9_code_0000d392 0xD392 : { KEEP(*(.text.tsl9_runtime_unported_d392)) } }
ASSERT(ADDR(.tsl9_code_0000d392) == 0xD392, "tsl9_runtime_unported_d392 plan");
ASSERT(SIZEOF(.tsl9_code_0000d392) == 10, "tsl9_runtime_unported_d392 exact size");
SECTIONS { .tsl9_code_0000d5de 0xD5DE : { KEEP(*(.text.tsl9_runtime_unported_d5de)) } }
ASSERT(ADDR(.tsl9_code_0000d5de) == 0xD5DE, "tsl9_runtime_unported_d5de plan");
ASSERT(SIZEOF(.tsl9_code_0000d5de) == 6, "tsl9_runtime_unported_d5de exact size");
SECTIONS { .tsl9_code_0000dd0c 0xDD0C : { KEEP(*(.text.tsl9_runtime_unported_dd0c)) } }
ASSERT(ADDR(.tsl9_code_0000dd0c) == 0xDD0C, "tsl9_runtime_unported_dd0c plan");
ASSERT(SIZEOF(.tsl9_code_0000dd0c) == 30, "tsl9_runtime_unported_dd0c exact size");
SECTIONS { .tsl9_code_0000dd6c 0xDD6C : { KEEP(*(.text.tsl9_runtime_unported_dd6c)) } }
ASSERT(ADDR(.tsl9_code_0000dd6c) == 0xDD6C, "tsl9_runtime_unported_dd6c plan");
ASSERT(SIZEOF(.tsl9_code_0000dd6c) == 10, "tsl9_runtime_unported_dd6c exact size");
SECTIONS { .tsl9_code_0000dec2 0xDEC2 : { KEEP(*(.text.tsl9_runtime_unported_dec2)) } }
ASSERT(ADDR(.tsl9_code_0000dec2) == 0xDEC2, "tsl9_runtime_unported_dec2 plan");
ASSERT(SIZEOF(.tsl9_code_0000dec2) == 10, "tsl9_runtime_unported_dec2 exact size");
SECTIONS { .tsl9_code_0000dee2 0xDEE2 : { KEEP(*(.text.tsl9_runtime_unported_dee2)) } }
ASSERT(ADDR(.tsl9_code_0000dee2) == 0xDEE2, "tsl9_runtime_unported_dee2 plan");
ASSERT(SIZEOF(.tsl9_code_0000dee2) == 76, "tsl9_runtime_unported_dee2 exact size");
SECTIONS { .tsl9_code_0000ebbc 0xEBBC : { KEEP(*(.text.tsl9_runtime_unported_ebbc)) } }
ASSERT(ADDR(.tsl9_code_0000ebbc) == 0xEBBC, "tsl9_runtime_unported_ebbc plan");
ASSERT(SIZEOF(.tsl9_code_0000ebbc) == 52, "tsl9_runtime_unported_ebbc exact size");
SECTIONS { .tsl9_code_0000f076 0xF076 : { KEEP(*(.text.tsl9_runtime_unported_f076)) } }
ASSERT(ADDR(.tsl9_code_0000f076) == 0xF076, "tsl9_runtime_unported_f076 plan");
ASSERT(SIZEOF(.tsl9_code_0000f076) == 594, "tsl9_runtime_unported_f076 exact size");
SECTIONS { .tsl9_code_0000f332 0xF332 : { KEEP(*(.text.tsl9_runtime_unported_f332)) } }
ASSERT(ADDR(.tsl9_code_0000f332) == 0xF332, "tsl9_runtime_unported_f332 plan");
ASSERT(SIZEOF(.tsl9_code_0000f332) == 82, "tsl9_runtime_unported_f332 exact size");
SECTIONS { .tsl9_code_0000f4e4 0xF4E4 : { KEEP(*(.text.tsl9_runtime_unported_f4e4)) } }
ASSERT(ADDR(.tsl9_code_0000f4e4) == 0xF4E4, "tsl9_runtime_unported_f4e4 plan");
ASSERT(SIZEOF(.tsl9_code_0000f4e4) == 12, "tsl9_runtime_unported_f4e4 exact size");
SECTIONS { .tsl9_code_0000f4f0 0xF4F0 : { KEEP(*(.text.tsl9_runtime_unported_f4f0)) } }
ASSERT(ADDR(.tsl9_code_0000f4f0) == 0xF4F0, "tsl9_runtime_unported_f4f0 plan");
ASSERT(SIZEOF(.tsl9_code_0000f4f0) == 32, "tsl9_runtime_unported_f4f0 exact size");
SECTIONS { .tsl9_code_0000f510 0xF510 : { KEEP(*(.text.tsl9_runtime_unported_f510)) } }
ASSERT(ADDR(.tsl9_code_0000f510) == 0xF510, "tsl9_runtime_unported_f510 plan");
ASSERT(SIZEOF(.tsl9_code_0000f510) == 10, "tsl9_runtime_unported_f510 exact size");
SECTIONS { .tsl9_code_0000f526 0xF526 : { KEEP(*(.text.tsl9_runtime_unported_f526)) } }
ASSERT(ADDR(.tsl9_code_0000f526) == 0xF526, "tsl9_runtime_unported_f526 plan");
ASSERT(SIZEOF(.tsl9_code_0000f526) == 12, "tsl9_runtime_unported_f526 exact size");
SECTIONS { .tsl9_code_0000f532 0xF532 : { KEEP(*(.text.tsl9_runtime_unported_f532)) } }
ASSERT(ADDR(.tsl9_code_0000f532) == 0xF532, "tsl9_runtime_unported_f532 plan");
ASSERT(SIZEOF(.tsl9_code_0000f532) == 10, "tsl9_runtime_unported_f532 exact size");
SECTIONS { .tsl9_code_0000f53c 0xF53C : { KEEP(*(.text.tsl9_runtime_unported_f53c)) } }
ASSERT(ADDR(.tsl9_code_0000f53c) == 0xF53C, "tsl9_runtime_unported_f53c plan");
ASSERT(SIZEOF(.tsl9_code_0000f53c) == 40, "tsl9_runtime_unported_f53c exact size");
SECTIONS { .tsl9_code_0000f56e 0xF56E : { KEEP(*(.text.tsl9_runtime_unported_f56e)) } }
ASSERT(ADDR(.tsl9_code_0000f56e) == 0xF56E, "tsl9_runtime_unported_f56e plan");
ASSERT(SIZEOF(.tsl9_code_0000f56e) == 40, "tsl9_runtime_unported_f56e exact size");
SECTIONS { .tsl9_code_0000f5a0 0xF5A0 : { KEEP(*(.text.tsl9_runtime_unported_f5a0)) } }
ASSERT(ADDR(.tsl9_code_0000f5a0) == 0xF5A0, "tsl9_runtime_unported_f5a0 plan");
ASSERT(SIZEOF(.tsl9_code_0000f5a0) == 40, "tsl9_runtime_unported_f5a0 exact size");
SECTIONS { .tsl9_code_0000f5d2 0xF5D2 : { KEEP(*(.text.tsl9_runtime_unported_f5d2)) } }
ASSERT(ADDR(.tsl9_code_0000f5d2) == 0xF5D2, "tsl9_runtime_unported_f5d2 plan");
ASSERT(SIZEOF(.tsl9_code_0000f5d2) == 40, "tsl9_runtime_unported_f5d2 exact size");
SECTIONS { .tsl9_code_0000f604 0xF604 : { KEEP(*(.text.tsl9_runtime_unported_f604)) } }
ASSERT(ADDR(.tsl9_code_0000f604) == 0xF604, "tsl9_runtime_unported_f604 plan");
ASSERT(SIZEOF(.tsl9_code_0000f604) == 60, "tsl9_runtime_unported_f604 exact size");
SECTIONS { .tsl9_code_0000f640 0xF640 : { KEEP(*(.text.tsl9_runtime_unported_f640)) } }
ASSERT(ADDR(.tsl9_code_0000f640) == 0xF640, "tsl9_runtime_unported_f640 plan");
ASSERT(SIZEOF(.tsl9_code_0000f640) == 10, "tsl9_runtime_unported_f640 exact size");
SECTIONS { .tsl9_code_0000f64a 0xF64A : { KEEP(*(.text.tsl9_runtime_unported_f64a)) } }
ASSERT(ADDR(.tsl9_code_0000f64a) == 0xF64A, "tsl9_runtime_unported_f64a plan");
ASSERT(SIZEOF(.tsl9_code_0000f64a) == 60, "tsl9_runtime_unported_f64a exact size");
SECTIONS { .tsl9_code_0000f686 0xF686 : { KEEP(*(.text.tsl9_runtime_unported_f686)) } }
ASSERT(ADDR(.tsl9_code_0000f686) == 0xF686, "tsl9_runtime_unported_f686 plan");
ASSERT(SIZEOF(.tsl9_code_0000f686) == 10, "tsl9_runtime_unported_f686 exact size");
SECTIONS { .tsl9_code_0000f690 0xF690 : { KEEP(*(.text.tsl9_runtime_unported_f690)) } }
ASSERT(ADDR(.tsl9_code_0000f690) == 0xF690, "tsl9_runtime_unported_f690 plan");
ASSERT(SIZEOF(.tsl9_code_0000f690) == 16, "tsl9_runtime_unported_f690 exact size");
SECTIONS { .tsl9_code_0000f6a0 0xF6A0 : { KEEP(*(.text.tsl9_runtime_unported_f6a0)) } }
ASSERT(ADDR(.tsl9_code_0000f6a0) == 0xF6A0, "tsl9_runtime_unported_f6a0 plan");
ASSERT(SIZEOF(.tsl9_code_0000f6a0) == 20, "tsl9_runtime_unported_f6a0 exact size");
SECTIONS { .tsl9_code_0000f6b4 0xF6B4 : { KEEP(*(.text.tsl9_runtime_unported_f6b4)) } }
ASSERT(ADDR(.tsl9_code_0000f6b4) == 0xF6B4, "tsl9_runtime_unported_f6b4 plan");
ASSERT(SIZEOF(.tsl9_code_0000f6b4) == 10, "tsl9_runtime_unported_f6b4 exact size");
SECTIONS { .tsl9_code_0000f6be 0xF6BE : { KEEP(*(.text.tsl9_runtime_unported_f6be)) } }
ASSERT(ADDR(.tsl9_code_0000f6be) == 0xF6BE, "tsl9_runtime_unported_f6be plan");
ASSERT(SIZEOF(.tsl9_code_0000f6be) == 14, "tsl9_runtime_unported_f6be exact size");
SECTIONS { .tsl9_code_0000f6cc 0xF6CC : { KEEP(*(.text.tsl9_runtime_unported_f6cc)) } }
ASSERT(ADDR(.tsl9_code_0000f6cc) == 0xF6CC, "tsl9_runtime_unported_f6cc plan");
ASSERT(SIZEOF(.tsl9_code_0000f6cc) == 10, "tsl9_runtime_unported_f6cc exact size");
SECTIONS { .tsl9_code_0000f6d6 0xF6D6 : { KEEP(*(.text.tsl9_runtime_unported_f6d6)) } }
ASSERT(ADDR(.tsl9_code_0000f6d6) == 0xF6D6, "tsl9_runtime_unported_f6d6 plan");
ASSERT(SIZEOF(.tsl9_code_0000f6d6) == 10, "tsl9_runtime_unported_f6d6 exact size");
SECTIONS { .tsl9_code_0000f714 0xF714 : { KEEP(*(.text.tsl9_runtime_unported_f714)) } }
ASSERT(ADDR(.tsl9_code_0000f714) == 0xF714, "tsl9_runtime_unported_f714 plan");
ASSERT(SIZEOF(.tsl9_code_0000f714) == 286, "tsl9_runtime_unported_f714 exact size");
SECTIONS { .tsl9_code_0000f832 0xF832 : { KEEP(*(.text.tsl9_runtime_unported_f832)) } }
ASSERT(ADDR(.tsl9_code_0000f832) == 0xF832, "tsl9_runtime_unported_f832 plan");
ASSERT(SIZEOF(.tsl9_code_0000f832) == 22, "tsl9_runtime_unported_f832 exact size");
SECTIONS { .tsl9_code_0000f84e 0xF84E : { KEEP(*(.text.tsl9_runtime_unported_f84e)) } }
ASSERT(ADDR(.tsl9_code_0000f84e) == 0xF84E, "tsl9_runtime_unported_f84e plan");
ASSERT(SIZEOF(.tsl9_code_0000f84e) == 12, "tsl9_runtime_unported_f84e exact size");
SECTIONS { .tsl9_code_0000f85a 0xF85A : { KEEP(*(.text.tsl9_runtime_unported_f85a)) } }
ASSERT(ADDR(.tsl9_code_0000f85a) == 0xF85A, "tsl9_runtime_unported_f85a plan");
ASSERT(SIZEOF(.tsl9_code_0000f85a) == 72, "tsl9_runtime_unported_f85a exact size");
SECTIONS { .tsl9_code_0000f8da 0xF8DA : { KEEP(*(.text.tsl9_runtime_unported_f8da)) } }
ASSERT(ADDR(.tsl9_code_0000f8da) == 0xF8DA, "tsl9_runtime_unported_f8da plan");
ASSERT(SIZEOF(.tsl9_code_0000f8da) == 6, "tsl9_runtime_unported_f8da exact size");
SECTIONS { .tsl9_code_0000f8e6 0xF8E6 : { KEEP(*(.text.tsl9_runtime_unported_f8e6)) } }
ASSERT(ADDR(.tsl9_code_0000f8e6) == 0xF8E6, "tsl9_runtime_unported_f8e6 plan");
ASSERT(SIZEOF(.tsl9_code_0000f8e6) == 6, "tsl9_runtime_unported_f8e6 exact size");
SECTIONS { .tsl9_code_0000f918 0xF918 : { KEEP(*(.text.tsl9_runtime_unported_f918)) } }
ASSERT(ADDR(.tsl9_code_0000f918) == 0xF918, "tsl9_runtime_unported_f918 plan");
ASSERT(SIZEOF(.tsl9_code_0000f918) == 26, "tsl9_runtime_unported_f918 exact size");
SECTIONS { .tsl9_code_0000f932 0xF932 : { KEEP(*(.text.tsl9_runtime_unported_f932)) } }
ASSERT(ADDR(.tsl9_code_0000f932) == 0xF932, "tsl9_runtime_unported_f932 plan");
ASSERT(SIZEOF(.tsl9_code_0000f932) == 106, "tsl9_runtime_unported_f932 exact size");
SECTIONS { .tsl9_code_0000f99c 0xF99C : { KEEP(*(.text.tsl9_runtime_unported_f99c)) } }
ASSERT(ADDR(.tsl9_code_0000f99c) == 0xF99C, "tsl9_runtime_unported_f99c plan");
ASSERT(SIZEOF(.tsl9_code_0000f99c) == 12, "tsl9_runtime_unported_f99c exact size");
SECTIONS { .tsl9_code_0000f9a8 0xF9A8 : { KEEP(*(.text.tsl9_runtime_unported_f9a8)) } }
ASSERT(ADDR(.tsl9_code_0000f9a8) == 0xF9A8, "tsl9_runtime_unported_f9a8 plan");
ASSERT(SIZEOF(.tsl9_code_0000f9a8) == 6, "tsl9_runtime_unported_f9a8 exact size");
SECTIONS { .tsl9_code_0000fc22 0xFC22 : { KEEP(*(.text.tsl9_runtime_unported_fc22)) } }
ASSERT(ADDR(.tsl9_code_0000fc22) == 0xFC22, "tsl9_runtime_unported_fc22 plan");
ASSERT(SIZEOF(.tsl9_code_0000fc22) == 54, "tsl9_runtime_unported_fc22 exact size");
SECTIONS { .tsl9_code_0000ff3c 0xFF3C : { KEEP(*(.text.tsl9_runtime_unported_ff3c)) } }
ASSERT(ADDR(.tsl9_code_0000ff3c) == 0xFF3C, "tsl9_runtime_unported_ff3c plan");
ASSERT(SIZEOF(.tsl9_code_0000ff3c) == 12, "tsl9_runtime_unported_ff3c exact size");
SECTIONS { .tsl9_code_0000ff7a 0xFF7A : { KEEP(*(.text.tsl9_runtime_unported_ff7a)) } }
ASSERT(ADDR(.tsl9_code_0000ff7a) == 0xFF7A, "tsl9_runtime_unported_ff7a plan");
ASSERT(SIZEOF(.tsl9_code_0000ff7a) == 14, "tsl9_runtime_unported_ff7a exact size");
SECTIONS { .tsl9_code_0000ffa8 0xFFA8 : { KEEP(*(.text.tsl9_runtime_unported_ffa8)) } }
ASSERT(ADDR(.tsl9_code_0000ffa8) == 0xFFA8, "tsl9_runtime_unported_ffa8 plan");
ASSERT(SIZEOF(.tsl9_code_0000ffa8) == 10, "tsl9_runtime_unported_ffa8 exact size");
SECTIONS { .tsl9_code_0000ffe2 0xFFE2 : { KEEP(*(.text.tsl9_runtime_unported_ffe2)) } }
ASSERT(ADDR(.tsl9_code_0000ffe2) == 0xFFE2, "tsl9_runtime_unported_ffe2 plan");
ASSERT(SIZEOF(.tsl9_code_0000ffe2) == 40, "tsl9_runtime_unported_ffe2 exact size");
SECTIONS { .tsl9_code_00010280 0x10280 : { KEEP(*(.text.tsl9_runtime_unported_10280)) } }
ASSERT(ADDR(.tsl9_code_00010280) == 0x10280, "tsl9_runtime_unported_10280 plan");
ASSERT(SIZEOF(.tsl9_code_00010280) == 6, "tsl9_runtime_unported_10280 exact size");
SECTIONS { .tsl9_code_00010286 0x10286 : { KEEP(*(.text.tsl9_runtime_unported_10286)) } }
ASSERT(ADDR(.tsl9_code_00010286) == 0x10286, "tsl9_runtime_unported_10286 plan");
ASSERT(SIZEOF(.tsl9_code_00010286) == 6, "tsl9_runtime_unported_10286 exact size");
SECTIONS { .tsl9_code_000135d4 0x135D4 : { KEEP(*(.text.tsl9_runtime_unported_135d4)) } }
ASSERT(ADDR(.tsl9_code_000135d4) == 0x135D4, "tsl9_runtime_unported_135d4 plan");
ASSERT(SIZEOF(.tsl9_code_000135d4) == 908, "tsl9_runtime_unported_135d4 exact size");
SECTIONS { .tsl9_code_00013a62 0x13A62 : { KEEP(*(.text.tsl9_runtime_unported_13a62)) } }
ASSERT(ADDR(.tsl9_code_00013a62) == 0x13A62, "tsl9_runtime_unported_13a62 plan");
ASSERT(SIZEOF(.tsl9_code_00013a62) == 142, "tsl9_runtime_unported_13a62 exact size");

/* R75 bounded dependency closure and guarded switch offsets. */
SECTIONS { .tsl9_code_000081ee 0x81EE : { KEEP(*(.text.tsl9_runtime_unported_81ee)) } }
ASSERT(ADDR(.tsl9_code_000081ee) == 0x81EE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000081ee) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000823e 0x823E : { KEEP(*(.text.tsl9_runtime_unported_823e)) } }
ASSERT(ADDR(.tsl9_code_0000823e) == 0x823E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000823e) == 68, "R75 exact size");
SECTIONS { .tsl9_code_00008e64 0x8E64 : { KEEP(*(.text.tsl9_runtime_unported_8e64)) } }
ASSERT(ADDR(.tsl9_code_00008e64) == 0x8E64, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00008e64) == 30, "R75 exact size");
SECTIONS { .tsl9_code_000094cc 0x94CC : { KEEP(*(.text.tsl9_runtime_unported_94cc)) } }
ASSERT(ADDR(.tsl9_code_000094cc) == 0x94CC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000094cc) == 26, "R75 exact size");
SECTIONS { .tsl9_code_0000952c 0x952C : { KEEP(*(.text.tsl9_runtime_unported_952c)) } }
ASSERT(ADDR(.tsl9_code_0000952c) == 0x952C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000952c) == 110, "R75 exact size");
SECTIONS { .tsl9_code_0000959a 0x959A : { KEEP(*(.text.tsl9_runtime_unported_959a)) } }
ASSERT(ADDR(.tsl9_code_0000959a) == 0x959A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000959a) == 82, "R75 exact size");
SECTIONS { .tsl9_code_00009636 0x9636 : { KEEP(*(.text.tsl9_runtime_unported_9636)) } }
ASSERT(ADDR(.tsl9_code_00009636) == 0x9636, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009636) == 74, "R75 exact size");
SECTIONS { .tsl9_code_00009680 0x9680 : { KEEP(*(.text.tsl9_runtime_unported_9680)) } }
ASSERT(ADDR(.tsl9_code_00009680) == 0x9680, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009680) == 154, "R75 exact size");
SECTIONS { .tsl9_code_0000971a 0x971A : { KEEP(*(.text.tsl9_runtime_unported_971a)) } }
ASSERT(ADDR(.tsl9_code_0000971a) == 0x971A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000971a) == 86, "R75 exact size");
SECTIONS { .tsl9_code_000099c6 0x99C6 : { KEEP(*(.text.tsl9_service_reference_99c6)) } }
ASSERT(ADDR(.tsl9_code_000099c6) == 0x99C6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000099c6) == 60, "R75 exact size");
SECTIONS { .tsl9_code_00009ac2 0x9AC2 : { KEEP(*(.text.tsl9_runtime_unported_9ac2)) } }
ASSERT(ADDR(.tsl9_code_00009ac2) == 0x9AC2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009ac2) == 12, "R75 exact size");
SECTIONS { .tsl9_code_00009e0a 0x9E0A : { KEEP(*(.text.tsl9_runtime_unported_9e0a)) } }
ASSERT(ADDR(.tsl9_code_00009e0a) == 0x9E0A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009e0a) == 34, "R75 exact size");
SECTIONS { .tsl9_code_00009e94 0x9E94 : { KEEP(*(.text.tsl9_runtime_unported_9e94)) } }
ASSERT(ADDR(.tsl9_code_00009e94) == 0x9E94, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009e94) == 56, "R75 exact size");
SECTIONS { .tsl9_code_00009ecc 0x9ECC : { KEEP(*(.text.tsl9_runtime_unported_9ecc)) } }
ASSERT(ADDR(.tsl9_code_00009ecc) == 0x9ECC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009ecc) == 16, "R75 exact size");
SECTIONS { .tsl9_code_00009ee2 0x9EE2 : { KEEP(*(.text.tsl9_runtime_unported_9ee2)) } }
ASSERT(ADDR(.tsl9_code_00009ee2) == 0x9EE2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009ee2) == 68, "R75 exact size");
SECTIONS { .tsl9_code_00009f26 0x9F26 : { KEEP(*(.text.tsl9_runtime_unported_9f26)) } }
ASSERT(ADDR(.tsl9_code_00009f26) == 0x9F26, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009f26) == 24, "R75 exact size");
SECTIONS { .tsl9_code_00009f3e 0x9F3E : { KEEP(*(.text.tsl9_runtime_unported_9f3e)) } }
ASSERT(ADDR(.tsl9_code_00009f3e) == 0x9F3E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009f3e) == 10, "R75 exact size");
SECTIONS { .tsl9_code_00009f48 0x9F48 : { KEEP(*(.text.tsl9_runtime_unported_9f48)) } }
ASSERT(ADDR(.tsl9_code_00009f48) == 0x9F48, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009f48) == 28, "R75 exact size");
SECTIONS { .tsl9_code_00009f64 0x9F64 : { KEEP(*(.text.tsl9_runtime_unported_9f64)) } }
ASSERT(ADDR(.tsl9_code_00009f64) == 0x9F64, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009f64) == 10, "R75 exact size");
SECTIONS { .tsl9_code_00009f6e 0x9F6E : { KEEP(*(.text.tsl9_runtime_unported_9f6e)) } }
ASSERT(ADDR(.tsl9_code_00009f6e) == 0x9F6E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00009f6e) == 442, "R75 exact size");
SECTIONS { .tsl9_code_0000a2b2 0xA2B2 : { KEEP(*(.text.tsl9_runtime_unported_a2b2)) } }
ASSERT(ADDR(.tsl9_code_0000a2b2) == 0xA2B2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a2b2) == 64, "R75 exact size");
SECTIONS { .tsl9_code_0000a416 0xA416 : { KEEP(*(.text.tsl9_runtime_unported_a416)) } }
ASSERT(ADDR(.tsl9_code_0000a416) == 0xA416, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a416) == 360, "R75 exact size");
SECTIONS { .tsl9_code_0000a57e 0xA57E : { KEEP(*(.text.tsl9_runtime_unported_a57e)) } }
ASSERT(ADDR(.tsl9_code_0000a57e) == 0xA57E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a57e) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000a58a 0xA58A : { KEEP(*(.text.tsl9_runtime_unported_a58a)) } }
ASSERT(ADDR(.tsl9_code_0000a58a) == 0xA58A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a58a) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000a5d0 0xA5D0 : { KEEP(*(.text.tsl9_runtime_unported_a5d0)) } }
ASSERT(ADDR(.tsl9_code_0000a5d0) == 0xA5D0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a5d0) == 46, "R75 exact size");
SECTIONS { .tsl9_code_0000a5fe 0xA5FE : { KEEP(*(.text.tsl9_runtime_unported_a5fe)) } }
ASSERT(ADDR(.tsl9_code_0000a5fe) == 0xA5FE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a5fe) == 648, "R75 exact size");
SECTIONS { .tsl9_code_0000a8fc 0xA8FC : { KEEP(*(.text.tsl9_runtime_unported_a8fc)) } }
ASSERT(ADDR(.tsl9_code_0000a8fc) == 0xA8FC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a8fc) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000a906 0xA906 : { KEEP(*(.text.tsl9_runtime_unported_a906)) } }
ASSERT(ADDR(.tsl9_code_0000a906) == 0xA906, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a906) == 48, "R75 exact size");
SECTIONS { .tsl9_code_0000a94c 0xA94C : { KEEP(*(.text.tsl9_runtime_unported_a94c)) } }
ASSERT(ADDR(.tsl9_code_0000a94c) == 0xA94C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a94c) == 48, "R75 exact size");
SECTIONS { .tsl9_code_0000a97c 0xA97C : { KEEP(*(.text.tsl9_runtime_unported_a97c)) } }
ASSERT(ADDR(.tsl9_code_0000a97c) == 0xA97C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a97c) == 64, "R75 exact size");
SECTIONS { .tsl9_code_0000a9bc 0xA9BC : { KEEP(*(.text.tsl9_runtime_unported_a9bc)) } }
ASSERT(ADDR(.tsl9_code_0000a9bc) == 0xA9BC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a9bc) == 56, "R75 exact size");
SECTIONS { .tsl9_code_0000aa1e 0xAA1E : { KEEP(*(.text.tsl9_runtime_unported_aa1e)) } }
ASSERT(ADDR(.tsl9_code_0000aa1e) == 0xAA1E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aa1e) == 72, "R75 exact size");
SECTIONS { .tsl9_code_0000aa66 0xAA66 : { KEEP(*(.text.tsl9_runtime_unported_aa66)) } }
ASSERT(ADDR(.tsl9_code_0000aa66) == 0xAA66, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aa66) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000aa6c 0xAA6C : { KEEP(*(.text.tsl9_runtime_unported_aa6c)) } }
ASSERT(ADDR(.tsl9_code_0000aa6c) == 0xAA6C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aa6c) == 86, "R75 exact size");
SECTIONS { .tsl9_code_0000aac2 0xAAC2 : { KEEP(*(.text.tsl9_runtime_unported_aac2)) } }
ASSERT(ADDR(.tsl9_code_0000aac2) == 0xAAC2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aac2) == 50, "R75 exact size");
SECTIONS { .tsl9_code_0000ab1c 0xAB1C : { KEEP(*(.text.tsl9_runtime_unported_ab1c)) } }
ASSERT(ADDR(.tsl9_code_0000ab1c) == 0xAB1C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ab1c) == 14, "R75 exact size");
SECTIONS { .tsl9_code_0000ab2a 0xAB2A : { KEEP(*(.text.tsl9_runtime_unported_ab2a)) } }
ASSERT(ADDR(.tsl9_code_0000ab2a) == 0xAB2A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ab2a) == 116, "R75 exact size");
SECTIONS { .tsl9_code_0000ab9e 0xAB9E : { KEEP(*(.text.tsl9_runtime_unported_ab9e)) } }
ASSERT(ADDR(.tsl9_code_0000ab9e) == 0xAB9E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ab9e) == 212, "R75 exact size");
SECTIONS { .tsl9_code_0000ac72 0xAC72 : { KEEP(*(.text.tsl9_runtime_unported_ac72)) } }
ASSERT(ADDR(.tsl9_code_0000ac72) == 0xAC72, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ac72) == 112, "R75 exact size");
SECTIONS { .tsl9_code_0000ace2 0xACE2 : { KEEP(*(.text.tsl9_runtime_unported_ace2)) } }
ASSERT(ADDR(.tsl9_code_0000ace2) == 0xACE2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ace2) == 52, "R75 exact size");
SECTIONS { .tsl9_code_0000ad16 0xAD16 : { KEEP(*(.text.tsl9_runtime_unported_ad16)) } }
ASSERT(ADDR(.tsl9_code_0000ad16) == 0xAD16, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ad16) == 92, "R75 exact size");
SECTIONS { .tsl9_code_0000ad72 0xAD72 : { KEEP(*(.text.tsl9_runtime_unported_ad72)) } }
ASSERT(ADDR(.tsl9_code_0000ad72) == 0xAD72, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ad72) == 306, "R75 exact size");
SECTIONS { .tsl9_code_0000af66 0xAF66 : { KEEP(*(.text.tsl9_runtime_unported_af66)) } }
ASSERT(ADDR(.tsl9_code_0000af66) == 0xAF66, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000af66) == 32, "R75 exact size");
SECTIONS { .tsl9_code_0000af86 0xAF86 : { KEEP(*(.text.tsl9_runtime_unported_af86)) } }
ASSERT(ADDR(.tsl9_code_0000af86) == 0xAF86, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000af86) == 58, "R75 exact size");
SECTIONS { .tsl9_code_0000afc6 0xAFC6 : { KEEP(*(.text.tsl9_runtime_unported_afc6)) } }
ASSERT(ADDR(.tsl9_code_0000afc6) == 0xAFC6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000afc6) == 120, "R75 exact size");
SECTIONS { .tsl9_code_0000b03e 0xB03E : { KEEP(*(.text.tsl9_runtime_unported_b03e)) } }
ASSERT(ADDR(.tsl9_code_0000b03e) == 0xB03E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b03e) == 34, "R75 exact size");
SECTIONS { .tsl9_code_0000b0ba 0xB0BA : { KEEP(*(.text.tsl9_runtime_unported_b0ba)) } }
ASSERT(ADDR(.tsl9_code_0000b0ba) == 0xB0BA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b0ba) == 58, "R75 exact size");
SECTIONS { .tsl9_code_0000b0f4 0xB0F4 : { KEEP(*(.text.tsl9_runtime_unported_b0f4)) } }
ASSERT(ADDR(.tsl9_code_0000b0f4) == 0xB0F4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b0f4) == 116, "R75 exact size");
SECTIONS { .tsl9_code_0000b168 0xB168 : { KEEP(*(.text.tsl9_runtime_unported_b168)) } }
ASSERT(ADDR(.tsl9_code_0000b168) == 0xB168, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b168) == 30, "R75 exact size");
SECTIONS { .tsl9_code_0000b186 0xB186 : { KEEP(*(.text.tsl9_runtime_unported_b186)) } }
ASSERT(ADDR(.tsl9_code_0000b186) == 0xB186, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b186) == 162, "R75 exact size");
SECTIONS { .tsl9_code_0000b250 0xB250 : { KEEP(*(.text.tsl9_runtime_unported_b250)) } }
ASSERT(ADDR(.tsl9_code_0000b250) == 0xB250, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b250) == 332, "R75 exact size");
SECTIONS { .tsl9_code_0000b39c 0xB39C : { KEEP(*(.text.tsl9_runtime_unported_b39c)) } }
ASSERT(ADDR(.tsl9_code_0000b39c) == 0xB39C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b39c) == 18, "R75 exact size");
SECTIONS { .tsl9_code_0000b3ae 0xB3AE : { KEEP(*(.text.tsl9_runtime_unported_b3ae)) } }
ASSERT(ADDR(.tsl9_code_0000b3ae) == 0xB3AE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b3ae) == 16, "R75 exact size");
SECTIONS { .tsl9_code_0000b3be 0xB3BE : { KEEP(*(.text.tsl9_runtime_unported_b3be)) } }
ASSERT(ADDR(.tsl9_code_0000b3be) == 0xB3BE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b3be) == 32, "R75 exact size");
SECTIONS { .tsl9_code_0000b3f0 0xB3F0 : { KEEP(*(.text.tsl9_runtime_unported_b3f0)) } }
ASSERT(ADDR(.tsl9_code_0000b3f0) == 0xB3F0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b3f0) == 96, "R75 exact size");
SECTIONS { .tsl9_code_0000b4ee 0xB4EE : { KEEP(*(.text.tsl9_runtime_unported_b4ee)) } }
ASSERT(ADDR(.tsl9_code_0000b4ee) == 0xB4EE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b4ee) == 22, "R75 exact size");
SECTIONS { .tsl9_code_0000b504 0xB504 : { KEEP(*(.text.tsl9_runtime_unported_b504)) } }
ASSERT(ADDR(.tsl9_code_0000b504) == 0xB504, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b504) == 46, "R75 exact size");
SECTIONS { .tsl9_code_0000b532 0xB532 : { KEEP(*(.text.tsl9_runtime_unported_b532)) } }
ASSERT(ADDR(.tsl9_code_0000b532) == 0xB532, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b532) == 20, "R75 exact size");
SECTIONS { .tsl9_code_0000b546 0xB546 : { KEEP(*(.text.tsl9_runtime_unported_b546)) } }
ASSERT(ADDR(.tsl9_code_0000b546) == 0xB546, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b546) == 46, "R75 exact size");
SECTIONS { .tsl9_code_0000b57e 0xB57E : { KEEP(*(.text.tsl9_runtime_unported_b57e)) } }
ASSERT(ADDR(.tsl9_code_0000b57e) == 0xB57E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b57e) == 60, "R75 exact size");
SECTIONS { .tsl9_code_0000b5ba 0xB5BA : { KEEP(*(.text.tsl9_runtime_unported_b5ba)) } }
ASSERT(ADDR(.tsl9_code_0000b5ba) == 0xB5BA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b5ba) == 1464, "R75 exact size");
SECTIONS { .tsl9_code_0000bb72 0xBB72 : { KEEP(*(.text.tsl9_runtime_unported_bb72)) } }
ASSERT(ADDR(.tsl9_code_0000bb72) == 0xBB72, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bb72) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000bb7e 0xBB7E : { KEEP(*(.text.tsl9_runtime_unported_bb7e)) } }
ASSERT(ADDR(.tsl9_code_0000bb7e) == 0xBB7E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bb7e) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bb88 0xBB88 : { KEEP(*(.text.tsl9_runtime_unported_bb88)) } }
ASSERT(ADDR(.tsl9_code_0000bb88) == 0xBB88, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bb88) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bb92 0xBB92 : { KEEP(*(.text.tsl9_runtime_unported_bb92)) } }
ASSERT(ADDR(.tsl9_code_0000bb92) == 0xBB92, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bb92) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bb9c 0xBB9C : { KEEP(*(.text.tsl9_runtime_unported_bb9c)) } }
ASSERT(ADDR(.tsl9_code_0000bb9c) == 0xBB9C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bb9c) == 48, "R75 exact size");
SECTIONS { .tsl9_code_0000bbcc 0xBBCC : { KEEP(*(.text.tsl9_runtime_unported_bbcc)) } }
ASSERT(ADDR(.tsl9_code_0000bbcc) == 0xBBCC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bbcc) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000bbd8 0xBBD8 : { KEEP(*(.text.tsl9_runtime_unported_bbd8)) } }
ASSERT(ADDR(.tsl9_code_0000bbd8) == 0xBBD8, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bbd8) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bbe2 0xBBE2 : { KEEP(*(.text.tsl9_runtime_unported_bbe2)) } }
ASSERT(ADDR(.tsl9_code_0000bbe2) == 0xBBE2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bbe2) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bbec 0xBBEC : { KEEP(*(.text.tsl9_runtime_unported_bbec)) } }
ASSERT(ADDR(.tsl9_code_0000bbec) == 0xBBEC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bbec) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bbf6 0xBBF6 : { KEEP(*(.text.tsl9_runtime_unported_bbf6)) } }
ASSERT(ADDR(.tsl9_code_0000bbf6) == 0xBBF6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bbf6) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000bc00 0xBC00 : { KEEP(*(.text.tsl9_runtime_unported_bc00)) } }
ASSERT(ADDR(.tsl9_code_0000bc00) == 0xBC00, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bc00) == 26, "R75 exact size");
SECTIONS { .tsl9_code_0000bc1a 0xBC1A : { KEEP(*(.text.tsl9_runtime_unported_bc1a)) } }
ASSERT(ADDR(.tsl9_code_0000bc1a) == 0xBC1A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000bc1a) == 1500, "R75 exact size");
SECTIONS { .tsl9_code_0000c200 0xC200 : { KEEP(*(.text.tsl9_runtime_unported_c200)) } }
ASSERT(ADDR(.tsl9_code_0000c200) == 0xC200, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c200) == 72, "R75 exact size");
SECTIONS { .tsl9_code_0000c248 0xC248 : { KEEP(*(.text.tsl9_runtime_unported_c248)) } }
ASSERT(ADDR(.tsl9_code_0000c248) == 0xC248, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c248) == 18, "R75 exact size");
SECTIONS { .tsl9_code_0000c270 0xC270 : { KEEP(*(.text.tsl9_runtime_unported_c270)) } }
ASSERT(ADDR(.tsl9_code_0000c270) == 0xC270, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c270) == 142, "R75 exact size");
SECTIONS { .tsl9_code_0000c30e 0xC30E : { KEEP(*(.text.tsl9_runtime_unported_c30e)) } }
ASSERT(ADDR(.tsl9_code_0000c30e) == 0xC30E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c30e) == 412, "R75 exact size");
SECTIONS { .tsl9_code_0000c4aa 0xC4AA : { KEEP(*(.text.tsl9_runtime_unported_c4aa)) } }
ASSERT(ADDR(.tsl9_code_0000c4aa) == 0xC4AA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c4aa) == 108, "R75 exact size");
SECTIONS { .tsl9_code_0000c646 0xC646 : { KEEP(*(.text.tsl9_runtime_unported_c646)) } }
ASSERT(ADDR(.tsl9_code_0000c646) == 0xC646, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c646) == 62, "R75 exact size");
SECTIONS { .tsl9_code_0000c684 0xC684 : { KEEP(*(.text.tsl9_runtime_unported_c684)) } }
ASSERT(ADDR(.tsl9_code_0000c684) == 0xC684, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c684) == 186, "R75 exact size");
SECTIONS { .tsl9_code_0000c73e 0xC73E : { KEEP(*(.text.tsl9_runtime_unported_c73e)) } }
ASSERT(ADDR(.tsl9_code_0000c73e) == 0xC73E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c73e) == 130, "R75 exact size");
SECTIONS { .tsl9_code_0000c7c0 0xC7C0 : { KEEP(*(.text.tsl9_runtime_unported_c7c0)) } }
ASSERT(ADDR(.tsl9_code_0000c7c0) == 0xC7C0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000c7c0) == 768, "R75 exact size");
SECTIONS { .tsl9_code_0000cac0 0xCAC0 : { KEEP(*(.text.tsl9_runtime_unported_cac0)) } }
ASSERT(ADDR(.tsl9_code_0000cac0) == 0xCAC0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cac0) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000cacc 0xCACC : { KEEP(*(.text.tsl9_runtime_unported_cacc)) } }
ASSERT(ADDR(.tsl9_code_0000cacc) == 0xCACC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cacc) == 22, "R75 exact size");
SECTIONS { .tsl9_code_0000cae2 0xCAE2 : { KEEP(*(.text.tsl9_runtime_unported_cae2)) } }
ASSERT(ADDR(.tsl9_code_0000cae2) == 0xCAE2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cae2) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000caec 0xCAEC : { KEEP(*(.text.tsl9_runtime_unported_caec)) } }
ASSERT(ADDR(.tsl9_code_0000caec) == 0xCAEC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000caec) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000caf6 0xCAF6 : { KEEP(*(.text.tsl9_runtime_unported_caf6)) } }
ASSERT(ADDR(.tsl9_code_0000caf6) == 0xCAF6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000caf6) == 54, "R75 exact size");
SECTIONS { .tsl9_code_0000cb2c 0xCB2C : { KEEP(*(.text.tsl9_runtime_unported_cb2c)) } }
ASSERT(ADDR(.tsl9_code_0000cb2c) == 0xCB2C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cb2c) == 52, "R75 exact size");
SECTIONS { .tsl9_code_0000cb60 0xCB60 : { KEEP(*(.text.tsl9_runtime_unported_cb60)) } }
ASSERT(ADDR(.tsl9_code_0000cb60) == 0xCB60, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cb60) == 78, "R75 exact size");
SECTIONS { .tsl9_code_0000cbca 0xCBCA : { KEEP(*(.text.tsl9_runtime_unported_cbca)) } }
ASSERT(ADDR(.tsl9_code_0000cbca) == 0xCBCA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cbca) == 284, "R75 exact size");
SECTIONS { .tsl9_code_0000cce6 0xCCE6 : { KEEP(*(.text.tsl9_runtime_unported_cce6)) } }
ASSERT(ADDR(.tsl9_code_0000cce6) == 0xCCE6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cce6) == 34, "R75 exact size");
SECTIONS { .tsl9_code_0000cd1e 0xCD1E : { KEEP(*(.text.tsl9_runtime_unported_cd1e)) } }
ASSERT(ADDR(.tsl9_code_0000cd1e) == 0xCD1E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cd1e) == 28, "R75 exact size");
SECTIONS { .tsl9_code_0000cd3a 0xCD3A : { KEEP(*(.text.tsl9_runtime_unported_cd3a)) } }
ASSERT(ADDR(.tsl9_code_0000cd3a) == 0xCD3A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cd3a) == 186, "R75 exact size");
SECTIONS { .tsl9_code_0000cdf4 0xCDF4 : { KEEP(*(.text.tsl9_runtime_unported_cdf4)) } }
ASSERT(ADDR(.tsl9_code_0000cdf4) == 0xCDF4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cdf4) == 178, "R75 exact size");
SECTIONS { .tsl9_code_0000ceda 0xCEDA : { KEEP(*(.text.tsl9_runtime_unported_ceda)) } }
ASSERT(ADDR(.tsl9_code_0000ceda) == 0xCEDA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ceda) == 114, "R75 exact size");
SECTIONS { .tsl9_code_0000cf62 0xCF62 : { KEEP(*(.text.tsl9_runtime_unported_cf62)) } }
ASSERT(ADDR(.tsl9_code_0000cf62) == 0xCF62, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cf62) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000cfa8 0xCFA8 : { KEEP(*(.text.tsl9_runtime_unported_cfa8)) } }
ASSERT(ADDR(.tsl9_code_0000cfa8) == 0xCFA8, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cfa8) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000d010 0xD010 : { KEEP(*(.text.tsl9_runtime_unported_d010)) } }
ASSERT(ADDR(.tsl9_code_0000d010) == 0xD010, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d010) == 188, "R75 exact size");
SECTIONS { .tsl9_code_0000d0e2 0xD0E2 : { KEEP(*(.text.tsl9_runtime_unported_d0e2)) } }
ASSERT(ADDR(.tsl9_code_0000d0e2) == 0xD0E2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d0e2) == 102, "R75 exact size");
SECTIONS { .tsl9_code_0000d148 0xD148 : { KEEP(*(.text.tsl9_runtime_unported_d148)) } }
ASSERT(ADDR(.tsl9_code_0000d148) == 0xD148, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d148) == 38, "R75 exact size");
SECTIONS { .tsl9_code_0000d196 0xD196 : { KEEP(*(.text.tsl9_runtime_unported_d196)) } }
ASSERT(ADDR(.tsl9_code_0000d196) == 0xD196, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d196) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000d1dc 0xD1DC : { KEEP(*(.text.tsl9_runtime_unported_d1dc)) } }
ASSERT(ADDR(.tsl9_code_0000d1dc) == 0xD1DC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d1dc) == 78, "R75 exact size");
SECTIONS { .tsl9_code_0000d22a 0xD22A : { KEEP(*(.text.tsl9_runtime_unported_d22a)) } }
ASSERT(ADDR(.tsl9_code_0000d22a) == 0xD22A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d22a) == 34, "R75 exact size");
SECTIONS { .tsl9_code_0000d25a 0xD25A : { KEEP(*(.text.tsl9_runtime_unported_d25a)) } }
ASSERT(ADDR(.tsl9_code_0000d25a) == 0xD25A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d25a) == 76, "R75 exact size");
SECTIONS { .tsl9_code_0000d2b0 0xD2B0 : { KEEP(*(.text.tsl9_runtime_unported_d2b0)) } }
ASSERT(ADDR(.tsl9_code_0000d2b0) == 0xD2B0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d2b0) == 106, "R75 exact size");
SECTIONS { .tsl9_code_0000d324 0xD324 : { KEEP(*(.text.tsl9_runtime_unported_d324)) } }
ASSERT(ADDR(.tsl9_code_0000d324) == 0xD324, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d324) == 100, "R75 exact size");
SECTIONS { .tsl9_code_0000d3e4 0xD3E4 : { KEEP(*(.text.tsl9_runtime_unported_d3e4)) } }
ASSERT(ADDR(.tsl9_code_0000d3e4) == 0xD3E4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d3e4) == 60, "R75 exact size");
SECTIONS { .tsl9_code_0000d420 0xD420 : { KEEP(*(.text.tsl9_runtime_unported_d420)) } }
ASSERT(ADDR(.tsl9_code_0000d420) == 0xD420, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d420) == 204, "R75 exact size");
SECTIONS { .tsl9_code_0000d4ec 0xD4EC : { KEEP(*(.text.tsl9_runtime_unported_d4ec)) } }
ASSERT(ADDR(.tsl9_code_0000d4ec) == 0xD4EC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d4ec) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000d4f2 0xD4F2 : { KEEP(*(.text.tsl9_runtime_unported_d4f2)) } }
ASSERT(ADDR(.tsl9_code_0000d4f2) == 0xD4F2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d4f2) == 34, "R75 exact size");
SECTIONS { .tsl9_code_0000d526 0xD526 : { KEEP(*(.text.tsl9_runtime_unported_d526)) } }
ASSERT(ADDR(.tsl9_code_0000d526) == 0xD526, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d526) == 184, "R75 exact size");
SECTIONS { .tsl9_code_0000d5f6 0xD5F6 : { KEEP(*(.text.tsl9_runtime_unported_d5f6)) } }
ASSERT(ADDR(.tsl9_code_0000d5f6) == 0xD5F6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d5f6) == 56, "R75 exact size");
SECTIONS { .tsl9_code_0000d65e 0xD65E : { KEEP(*(.text.tsl9_runtime_unported_d65e)) } }
ASSERT(ADDR(.tsl9_code_0000d65e) == 0xD65E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d65e) == 60, "R75 exact size");
SECTIONS { .tsl9_code_0000d69a 0xD69A : { KEEP(*(.text.tsl9_runtime_unported_d69a)) } }
ASSERT(ADDR(.tsl9_code_0000d69a) == 0xD69A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d69a) == 88, "R75 exact size");
SECTIONS { .tsl9_code_0000d6f2 0xD6F2 : { KEEP(*(.text.tsl9_runtime_unported_d6f2)) } }
ASSERT(ADDR(.tsl9_code_0000d6f2) == 0xD6F2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d6f2) == 122, "R75 exact size");
SECTIONS { .tsl9_code_0000d76c 0xD76C : { KEEP(*(.text.tsl9_runtime_unported_d76c)) } }
ASSERT(ADDR(.tsl9_code_0000d76c) == 0xD76C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d76c) == 44, "R75 exact size");
SECTIONS { .tsl9_code_0000d798 0xD798 : { KEEP(*(.text.tsl9_runtime_unported_d798)) } }
ASSERT(ADDR(.tsl9_code_0000d798) == 0xD798, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d798) == 72, "R75 exact size");
SECTIONS { .tsl9_code_0000d7e0 0xD7E0 : { KEEP(*(.text.tsl9_runtime_unported_d7e0)) } }
ASSERT(ADDR(.tsl9_code_0000d7e0) == 0xD7E0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d7e0) == 224, "R75 exact size");
SECTIONS { .tsl9_code_0000d8c0 0xD8C0 : { KEEP(*(.text.tsl9_runtime_unported_d8c0)) } }
ASSERT(ADDR(.tsl9_code_0000d8c0) == 0xD8C0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d8c0) == 62, "R75 exact size");
SECTIONS { .tsl9_code_0000d8fe 0xD8FE : { KEEP(*(.text.tsl9_runtime_unported_d8fe)) } }
ASSERT(ADDR(.tsl9_code_0000d8fe) == 0xD8FE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d8fe) == 84, "R75 exact size");
SECTIONS { .tsl9_code_0000d952 0xD952 : { KEEP(*(.text.tsl9_runtime_unported_d952)) } }
ASSERT(ADDR(.tsl9_code_0000d952) == 0xD952, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d952) == 260, "R75 exact size");
SECTIONS { .tsl9_code_0000da56 0xDA56 : { KEEP(*(.text.tsl9_runtime_unported_da56)) } }
ASSERT(ADDR(.tsl9_code_0000da56) == 0xDA56, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000da56) == 694, "R75 exact size");
SECTIONS { .tsl9_code_0000dd2a 0xDD2A : { KEEP(*(.text.tsl9_runtime_unported_dd2a)) } }
ASSERT(ADDR(.tsl9_code_0000dd2a) == 0xDD2A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000dd2a) == 66, "R75 exact size");
SECTIONS { .tsl9_code_0000dd76 0xDD76 : { KEEP(*(.text.tsl9_runtime_unported_dd76)) } }
ASSERT(ADDR(.tsl9_code_0000dd76) == 0xDD76, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000dd76) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000dd7c 0xDD7C : { KEEP(*(.text.tsl9_runtime_unported_dd7c)) } }
ASSERT(ADDR(.tsl9_code_0000dd7c) == 0xDD7C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000dd7c) == 326, "R75 exact size");
SECTIONS { .tsl9_code_0000decc 0xDECC : { KEEP(*(.text.tsl9_runtime_unported_decc)) } }
ASSERT(ADDR(.tsl9_code_0000decc) == 0xDECC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000decc) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000ded2 0xDED2 : { KEEP(*(.text.tsl9_runtime_unported_ded2)) } }
ASSERT(ADDR(.tsl9_code_0000ded2) == 0xDED2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ded2) == 16, "R75 exact size");
SECTIONS { .tsl9_code_0000e030 0xE030 : { KEEP(*(.text.tsl9_runtime_unported_e030)) } }
ASSERT(ADDR(.tsl9_code_0000e030) == 0xE030, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000e030) == 102, "R75 exact size");
SECTIONS { .tsl9_code_0000e096 0xE096 : { KEEP(*(.text.tsl9_runtime_unported_e096)) } }
ASSERT(ADDR(.tsl9_code_0000e096) == 0xE096, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000e096) == 20, "R75 exact size");
SECTIONS { .tsl9_code_0000e0aa 0xE0AA : { KEEP(*(.text.tsl9_runtime_unported_e0aa)) } }
ASSERT(ADDR(.tsl9_code_0000e0aa) == 0xE0AA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000e0aa) == 2444, "R75 exact size");
SECTIONS { .tsl9_code_0000ea36 0xEA36 : { KEEP(*(.text.tsl9_runtime_unported_ea36)) } }
ASSERT(ADDR(.tsl9_code_0000ea36) == 0xEA36, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ea36) == 252, "R75 exact size");
SECTIONS { .tsl9_code_0000eb32 0xEB32 : { KEEP(*(.text.tsl9_runtime_unported_eb32)) } }
ASSERT(ADDR(.tsl9_code_0000eb32) == 0xEB32, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000eb32) == 88, "R75 exact size");
SECTIONS { .tsl9_code_0000eb8a 0xEB8A : { KEEP(*(.text.tsl9_runtime_unported_eb8a)) } }
ASSERT(ADDR(.tsl9_code_0000eb8a) == 0xEB8A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000eb8a) == 50, "R75 exact size");
SECTIONS { .tsl9_code_0000ebf0 0xEBF0 : { KEEP(*(.text.tsl9_runtime_unported_ebf0)) } }
ASSERT(ADDR(.tsl9_code_0000ebf0) == 0xEBF0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ebf0) == 112, "R75 exact size");
SECTIONS { .tsl9_code_0000ec60 0xEC60 : { KEEP(*(.text.tsl9_runtime_unported_ec60)) } }
ASSERT(ADDR(.tsl9_code_0000ec60) == 0xEC60, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ec60) == 76, "R75 exact size");
SECTIONS { .tsl9_code_0000ecac 0xECAC : { KEEP(*(.text.tsl9_runtime_unported_ecac)) } }
ASSERT(ADDR(.tsl9_code_0000ecac) == 0xECAC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ecac) == 62, "R75 exact size");
SECTIONS { .tsl9_code_0000ed54 0xED54 : { KEEP(*(.text.tsl9_runtime_unported_ed54)) } }
ASSERT(ADDR(.tsl9_code_0000ed54) == 0xED54, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ed54) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000ee26 0xEE26 : { KEEP(*(.text.tsl9_runtime_unported_ee26)) } }
ASSERT(ADDR(.tsl9_code_0000ee26) == 0xEE26, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ee26) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000ee30 0xEE30 : { KEEP(*(.text.tsl9_runtime_unported_ee30)) } }
ASSERT(ADDR(.tsl9_code_0000ee30) == 0xEE30, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ee30) == 160, "R75 exact size");
SECTIONS { .tsl9_code_0000eed0 0xEED0 : { KEEP(*(.text.tsl9_runtime_unported_eed0)) } }
ASSERT(ADDR(.tsl9_code_0000eed0) == 0xEED0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000eed0) == 66, "R75 exact size");
SECTIONS { .tsl9_code_0000ef12 0xEF12 : { KEEP(*(.text.tsl9_runtime_unported_ef12)) } }
ASSERT(ADDR(.tsl9_code_0000ef12) == 0xEF12, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ef12) == 88, "R75 exact size");
SECTIONS { .tsl9_code_0000ef80 0xEF80 : { KEEP(*(.text.tsl9_runtime_unported_ef80)) } }
ASSERT(ADDR(.tsl9_code_0000ef80) == 0xEF80, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ef80) == 10, "R75 exact size");
SECTIONS { .tsl9_code_0000ef8a 0xEF8A : { KEEP(*(.text.tsl9_runtime_unported_ef8a)) } }
ASSERT(ADDR(.tsl9_code_0000ef8a) == 0xEF8A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ef8a) == 116, "R75 exact size");
SECTIONS { .tsl9_code_0000effe 0xEFFE : { KEEP(*(.text.tsl9_runtime_unported_effe)) } }
ASSERT(ADDR(.tsl9_code_0000effe) == 0xEFFE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000effe) == 120, "R75 exact size");
SECTIONS { .tsl9_code_0000f2c8 0xF2C8 : { KEEP(*(.text.tsl9_runtime_unported_f2c8)) } }
ASSERT(ADDR(.tsl9_code_0000f2c8) == 0xF2C8, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f2c8) == 84, "R75 exact size");
SECTIONS { .tsl9_code_0000f384 0xF384 : { KEEP(*(.text.tsl9_runtime_unported_f384)) } }
ASSERT(ADDR(.tsl9_code_0000f384) == 0xF384, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f384) == 168, "R75 exact size");
SECTIONS { .tsl9_code_0000f42c 0xF42C : { KEEP(*(.text.tsl9_runtime_unported_f42c)) } }
ASSERT(ADDR(.tsl9_code_0000f42c) == 0xF42C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f42c) == 184, "R75 exact size");
SECTIONS { .tsl9_code_0000f51a 0xF51A : { KEEP(*(.text.tsl9_runtime_unported_f51a)) } }
ASSERT(ADDR(.tsl9_code_0000f51a) == 0xF51A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f51a) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000f6e0 0xF6E0 : { KEEP(*(.text.tsl9_runtime_unported_f6e0)) } }
ASSERT(ADDR(.tsl9_code_0000f6e0) == 0xF6E0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f6e0) == 12, "R75 exact size");
SECTIONS { .tsl9_code_0000f8a2 0xF8A2 : { KEEP(*(.text.tsl9_runtime_unported_f8a2)) } }
ASSERT(ADDR(.tsl9_code_0000f8a2) == 0xF8A2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f8a2) == 56, "R75 exact size");
SECTIONS { .tsl9_code_0000f9ae 0xF9AE : { KEEP(*(.text.tsl9_runtime_unported_f9ae)) } }
ASSERT(ADDR(.tsl9_code_0000f9ae) == 0xF9AE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f9ae) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000fa58 0xFA58 : { KEEP(*(.text.tsl9_runtime_unported_fa58)) } }
ASSERT(ADDR(.tsl9_code_0000fa58) == 0xFA58, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fa58) == 414, "R75 exact size");
SECTIONS { .tsl9_code_0000fc16 0xFC16 : { KEEP(*(.text.tsl9_runtime_unported_fc16)) } }
ASSERT(ADDR(.tsl9_code_0000fc16) == 0xFC16, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fc16) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000fc1c 0xFC1C : { KEEP(*(.text.tsl9_runtime_unported_fc1c)) } }
ASSERT(ADDR(.tsl9_code_0000fc1c) == 0xFC1C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fc1c) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000fc58 0xFC58 : { KEEP(*(.text.tsl9_runtime_unported_fc58)) } }
ASSERT(ADDR(.tsl9_code_0000fc58) == 0xFC58, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fc58) == 6, "R75 exact size");
SECTIONS { .tsl9_code_0000fc5e 0xFC5E : { KEEP(*(.text.tsl9_runtime_unported_fc5e)) } }
ASSERT(ADDR(.tsl9_code_0000fc5e) == 0xFC5E, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fc5e) == 78, "R75 exact size");
SECTIONS { .tsl9_code_0000fcac 0xFCAC : { KEEP(*(.text.tsl9_runtime_unported_fcac)) } }
ASSERT(ADDR(.tsl9_code_0000fcac) == 0xFCAC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fcac) == 18, "R75 exact size");
SECTIONS { .tsl9_code_0000fcbe 0xFCBE : { KEEP(*(.text.tsl9_runtime_unported_fcbe)) } }
ASSERT(ADDR(.tsl9_code_0000fcbe) == 0xFCBE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fcbe) == 20, "R75 exact size");
SECTIONS { .tsl9_code_0000fcd2 0xFCD2 : { KEEP(*(.text.tsl9_runtime_unported_fcd2)) } }
ASSERT(ADDR(.tsl9_code_0000fcd2) == 0xFCD2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fcd2) == 78, "R75 exact size");
SECTIONS { .tsl9_code_0000fd20 0xFD20 : { KEEP(*(.text.tsl9_runtime_unported_fd20)) } }
ASSERT(ADDR(.tsl9_code_0000fd20) == 0xFD20, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fd20) == 218, "R75 exact size");
SECTIONS { .tsl9_code_0000fe0c 0xFE0C : { KEEP(*(.text.tsl9_runtime_unported_fe0c)) } }
ASSERT(ADDR(.tsl9_code_0000fe0c) == 0xFE0C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fe0c) == 76, "R75 exact size");
SECTIONS { .tsl9_code_0000fe58 0xFE58 : { KEEP(*(.text.tsl9_runtime_unported_fe58)) } }
ASSERT(ADDR(.tsl9_code_0000fe58) == 0xFE58, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fe58) == 124, "R75 exact size");
SECTIONS { .tsl9_code_0000fed4 0xFED4 : { KEEP(*(.text.tsl9_runtime_unported_fed4)) } }
ASSERT(ADDR(.tsl9_code_0000fed4) == 0xFED4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fed4) == 16, "R75 exact size");
SECTIONS { .tsl9_code_0000fef6 0xFEF6 : { KEEP(*(.text.tsl9_runtime_unported_fef6)) } }
ASSERT(ADDR(.tsl9_code_0000fef6) == 0xFEF6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fef6) == 70, "R75 exact size");
SECTIONS { .tsl9_code_0000ff48 0xFF48 : { KEEP(*(.text.tsl9_runtime_unported_ff48)) } }
ASSERT(ADDR(.tsl9_code_0000ff48) == 0xFF48, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ff48) == 50, "R75 exact size");
SECTIONS { .tsl9_code_0000ff88 0xFF88 : { KEEP(*(.text.tsl9_runtime_unported_ff88)) } }
ASSERT(ADDR(.tsl9_code_0000ff88) == 0xFF88, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ff88) == 32, "R75 exact size");
SECTIONS { .tsl9_code_0000ffb2 0xFFB2 : { KEEP(*(.text.tsl9_runtime_unported_ffb2)) } }
ASSERT(ADDR(.tsl9_code_0000ffb2) == 0xFFB2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ffb2) == 48, "R75 exact size");
SECTIONS { .tsl9_code_00010020 0x10020 : { KEEP(*(.text.tsl9_runtime_unported_10020)) } }
ASSERT(ADDR(.tsl9_code_00010020) == 0x10020, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010020) == 112, "R75 exact size");
SECTIONS { .tsl9_code_00010090 0x10090 : { KEEP(*(.text.tsl9_runtime_unported_10090)) } }
ASSERT(ADDR(.tsl9_code_00010090) == 0x10090, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010090) == 152, "R75 exact size");
SECTIONS { .tsl9_code_0001013a 0x1013A : { KEEP(*(.text.tsl9_runtime_unported_1013a)) } }
ASSERT(ADDR(.tsl9_code_0001013a) == 0x1013A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001013a) == 326, "R75 exact size");
SECTIONS { .tsl9_code_0001028c 0x1028C : { KEEP(*(.text.tsl9_runtime_unported_1028c)) } }
ASSERT(ADDR(.tsl9_code_0001028c) == 0x1028C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001028c) == 50, "R75 exact size");
SECTIONS { .tsl9_code_000102be 0x102BE : { KEEP(*(.text.tsl9_runtime_unported_102be)) } }
ASSERT(ADDR(.tsl9_code_000102be) == 0x102BE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000102be) == 278, "R75 exact size");
SECTIONS { .tsl9_code_0001041a 0x1041A : { KEEP(*(.text.tsl9_control_reference_1041a)) } }
ASSERT(ADDR(.tsl9_code_0001041a) == 0x1041A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001041a) == 40, "R75 exact size");
SECTIONS { .tsl9_code_000104ae 0x104AE : { KEEP(*(.text.tsl9_mode_reference_104ae)) } }
ASSERT(ADDR(.tsl9_code_000104ae) == 0x104AE, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000104ae) == 110, "R75 exact size");
SECTIONS { .tsl9_code_0001051c 0x1051C : { KEEP(*(.text.tsl9_dispatch_reference_1051c)) } }
ASSERT(ADDR(.tsl9_code_0001051c) == 0x1051C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001051c) == 32, "R75 exact size");
SECTIONS { .tsl9_code_0001053c 0x1053C : { KEEP(*(.text.tsl9_runtime_unported_1053c)) } }
ASSERT(ADDR(.tsl9_code_0001053c) == 0x1053C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001053c) == 32, "R75 exact size");
SECTIONS { .tsl9_code_000106ec 0x106EC : { KEEP(*(.text.tsl9_runtime_unported_106ec)) } }
ASSERT(ADDR(.tsl9_code_000106ec) == 0x106EC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000106ec) == 104, "R75 exact size");
SECTIONS { .tsl9_code_00010754 0x10754 : { KEEP(*(.text.tsl9_runtime_unported_10754)) } }
ASSERT(ADDR(.tsl9_code_00010754) == 0x10754, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010754) == 94, "R75 exact size");
SECTIONS { .tsl9_code_000107c0 0x107C0 : { KEEP(*(.text.tsl9_runtime_unported_107c0)) } }
ASSERT(ADDR(.tsl9_code_000107c0) == 0x107C0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000107c0) == 128, "R75 exact size");
SECTIONS { .tsl9_code_00010840 0x10840 : { KEEP(*(.text.tsl9_runtime_unported_10840)) } }
ASSERT(ADDR(.tsl9_code_00010840) == 0x10840, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010840) == 60, "R75 exact size");
SECTIONS { .tsl9_code_0001087c 0x1087C : { KEEP(*(.text.tsl9_runtime_unported_1087c)) } }
ASSERT(ADDR(.tsl9_code_0001087c) == 0x1087C, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001087c) == 22, "R75 exact size");
SECTIONS { .tsl9_code_00010892 0x10892 : { KEEP(*(.text.tsl9_runtime_unported_10892)) } }
ASSERT(ADDR(.tsl9_code_00010892) == 0x10892, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010892) == 176, "R75 exact size");
SECTIONS { .tsl9_code_00010942 0x10942 : { KEEP(*(.text.tsl9_runtime_unported_10942)) } }
ASSERT(ADDR(.tsl9_code_00010942) == 0x10942, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010942) == 68, "R75 exact size");
SECTIONS { .tsl9_code_00010986 0x10986 : { KEEP(*(.text.tsl9_runtime_unported_10986)) } }
ASSERT(ADDR(.tsl9_code_00010986) == 0x10986, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010986) == 86, "R75 exact size");
SECTIONS { .tsl9_code_000109dc 0x109DC : { KEEP(*(.text.tsl9_runtime_unported_109dc)) } }
ASSERT(ADDR(.tsl9_code_000109dc) == 0x109DC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000109dc) == 190, "R75 exact size");
SECTIONS { .tsl9_code_000139e6 0x139E6 : { KEEP(*(.text.tsl9_runtime_unported_139e6)) } }
ASSERT(ADDR(.tsl9_code_000139e6) == 0x139E6, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000139e6) == 124, "R75 exact size");
SECTIONS { .tsl9_code_000152d2 0x152D2 : { KEEP(*(.text.tsl9_service_reference_152d2)) } }
ASSERT(ADDR(.tsl9_code_000152d2) == 0x152D2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000152d2) == 8, "R75 exact size");
SECTIONS { .tsl9_code_000152da 0x152DA : { KEEP(*(.text.tsl9_runtime_unported_152da)) } }
ASSERT(ADDR(.tsl9_code_000152da) == 0x152DA, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000152da) == 82, "R75 exact size");
SECTIONS { .tsl9_code_0001651a 0x1651A : { KEEP(*(.text.tsl9_runtime_unported_1651a)) } }
ASSERT(ADDR(.tsl9_code_0001651a) == 0x1651A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001651a) == 178, "R75 exact size");
SECTIONS { .tsl9_code_00017024 0x17024 : { KEEP(*(.text.tsl9_runtime_unported_17024)) } }
ASSERT(ADDR(.tsl9_code_00017024) == 0x17024, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017024) == 36, "R75 exact size");
SECTIONS { .tsl9_code_000177d0 0x177D0 : { KEEP(*(.text.tsl9_runtime_unported_177d0)) } }
ASSERT(ADDR(.tsl9_code_000177d0) == 0x177D0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000177d0) == 406, "R75 exact size");
SECTIONS { .tsl9_code_00017e26 0x17E26 : { KEEP(*(.text.tsl9_runtime_unported_17e26)) } }
ASSERT(ADDR(.tsl9_code_00017e26) == 0x17E26, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017e26) == 150, "R75 exact size");
SECTIONS { .tsl9_code_00017ebc 0x17EBC : { KEEP(*(.text.tsl9_runtime_unported_17ebc)) } }
ASSERT(ADDR(.tsl9_code_00017ebc) == 0x17EBC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017ebc) == 32, "R75 exact size");
SECTIONS { .tsl9_code_00017edc 0x17EDC : { KEEP(*(.text.tsl9_runtime_unported_17edc)) } }
ASSERT(ADDR(.tsl9_code_00017edc) == 0x17EDC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017edc) == 140, "R75 exact size");
SECTIONS { .tsl9_code_00017f72 0x17F72 : { KEEP(*(.text.tsl9_runtime_unported_17f72)) } }
ASSERT(ADDR(.tsl9_code_00017f72) == 0x17F72, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017f72) == 40, "R75 exact size");
SECTIONS { .tsl9_code_00017f9a 0x17F9A : { KEEP(*(.text.tsl9_runtime_unported_17f9a)) } }
ASSERT(ADDR(.tsl9_code_00017f9a) == 0x17F9A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017f9a) == 26, "R75 exact size");
SECTIONS { .tsl9_code_00017fb4 0x17FB4 : { KEEP(*(.text.tsl9_runtime_unported_17fb4)) } }
ASSERT(ADDR(.tsl9_code_00017fb4) == 0x17FB4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017fb4) == 510, "R75 exact size");
SECTIONS { .tsl9_code_000181b2 0x181B2 : { KEEP(*(.text.tsl9_runtime_unported_181b2)) } }
ASSERT(ADDR(.tsl9_code_000181b2) == 0x181B2, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_000181b2) == 122, "R75 exact size");
SECTIONS { .tsl9_code_0001835a 0x1835A : { KEEP(*(.text.tsl9_runtime_unported_1835a)) } }
ASSERT(ADDR(.tsl9_code_0001835a) == 0x1835A, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001835a) == 18, "R75 exact size");
SECTIONS { .tsl9_ro_00019aa0 0x19AA0 : { KEEP(*(.rodata.__tsl9_jump_table_19aa0)) } }
ASSERT(ADDR(.tsl9_ro_00019aa0) == 0x19AA0, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019aa0) == 72, "R75 exact size");
SECTIONS { .tsl9_ro_00019ae8 0x19AE8 : { KEEP(*(.rodata.__tsl9_jump_table_19ae8)) } }
ASSERT(ADDR(.tsl9_ro_00019ae8) == 0x19AE8, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019ae8) == 44, "R75 exact size");
SECTIONS { .tsl9_ro_00019b14 0x19B14 : { KEEP(*(.rodata.__tsl9_jump_table_19b14)) } }
ASSERT(ADDR(.tsl9_ro_00019b14) == 0x19B14, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019b14) == 44, "R75 exact size");
SECTIONS { .tsl9_ro_00019d74 0x19D74 : { KEEP(*(.rodata.__tsl9_jump_table_19d74)) } }
ASSERT(ADDR(.tsl9_ro_00019d74) == 0x19D74, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019d74) == 96, "R75 exact size");
SECTIONS { .tsl9_ro_00019dd4 0x19DD4 : { KEEP(*(.rodata.__tsl9_jump_table_19dd4)) } }
ASSERT(ADDR(.tsl9_ro_00019dd4) == 0x19DD4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019dd4) == 20, "R75 exact size");
SECTIONS { .tsl9_ro_00019de8 0x19DE8 : { KEEP(*(.rodata.__tsl9_jump_table_19de8)) } }
ASSERT(ADDR(.tsl9_ro_00019de8) == 0x19DE8, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019de8) == 120, "R75 exact size");
SECTIONS { .tsl9_ro_00019e60 0x19E60 : { KEEP(*(.rodata.__tsl9_jump_table_19e60)) } }
ASSERT(ADDR(.tsl9_ro_00019e60) == 0x19E60, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019e60) == 332, "R75 exact size");
SECTIONS { .tsl9_ro_00019fac 0x19FAC : { KEEP(*(.rodata.__tsl9_jump_table_19fac)) } }
ASSERT(ADDR(.tsl9_ro_00019fac) == 0x19FAC, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019fac) == 40, "R75 exact size");
SECTIONS { .tsl9_ro_00019fd4 0x19FD4 : { KEEP(*(.rodata.__tsl9_jump_table_19fd4)) } }
ASSERT(ADDR(.tsl9_ro_00019fd4) == 0x19FD4, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019fd4) == 244, "R75 exact size");
SECTIONS { .tsl9_ro_0001a788 0x1A788 : { KEEP(*(.rodata.__tsl9_jump_table_1a788)) } }
ASSERT(ADDR(.tsl9_ro_0001a788) == 0x1A788, "R75 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a788) == 24, "R75 exact size");

/* R76 proven-consumer closure and finite admitted operand windows. */
SECTIONS { .tsl9_code_0000a20e 0xA20E : { KEEP(*(.text.tsl9_callback_a20e)) } }
ASSERT(ADDR(.tsl9_code_0000a20e) == 0xA20E, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a20e) == 4, "R76 exact size");
SECTIONS { .tsl9_code_0000a2f2 0xA2F2 : { KEEP(*(.text.tsl9_callback_a2f2)) } }
ASSERT(ADDR(.tsl9_code_0000a2f2) == 0xA2F2, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a2f2) == 172, "R76 exact size");
SECTIONS { .tsl9_code_0000a39e 0xA39E : { KEEP(*(.text.tsl9_runtime_unported_a39e)) } }
ASSERT(ADDR(.tsl9_code_0000a39e) == 0xA39E, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a39e) == 86, "R76 exact size");
SECTIONS { .tsl9_code_0000a3f4 0xA3F4 : { KEEP(*(.text.tsl9_callback_a3f4)) } }
ASSERT(ADDR(.tsl9_code_0000a3f4) == 0xA3F4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a3f4) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0000a400 0xA400 : { KEEP(*(.text.tsl9_callback_a400)) } }
ASSERT(ADDR(.tsl9_code_0000a400) == 0xA400, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a400) == 22, "R76 exact size");
SECTIONS { .tsl9_code_0000a9f4 0xA9F4 : { KEEP(*(.text.tsl9_callback_a9f4)) } }
ASSERT(ADDR(.tsl9_code_0000a9f4) == 0xA9F4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a9f4) == 10, "R76 exact size");
SECTIONS { .tsl9_code_0000a9fe 0xA9FE : { KEEP(*(.text.tsl9_callback_a9fe)) } }
ASSERT(ADDR(.tsl9_code_0000a9fe) == 0xA9FE, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000a9fe) == 16, "R76 exact size");
SECTIONS { .tsl9_code_0000aa0e 0xAA0E : { KEEP(*(.text.tsl9_callback_aa0e)) } }
ASSERT(ADDR(.tsl9_code_0000aa0e) == 0xAA0E, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aa0e) == 16, "R76 exact size");
SECTIONS { .tsl9_code_0000aaf4 0xAAF4 : { KEEP(*(.text.tsl9_runtime_unported_aaf4)) } }
ASSERT(ADDR(.tsl9_code_0000aaf4) == 0xAAF4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000aaf4) == 10, "R76 exact size");
SECTIONS { .tsl9_code_0000b072 0xB072 : { KEEP(*(.text.tsl9_callback_b072)) } }
ASSERT(ADDR(.tsl9_code_0000b072) == 0xB072, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b072) == 72, "R76 exact size");
SECTIONS { .tsl9_code_0000b450 0xB450 : { KEEP(*(.text.tsl9_runtime_unported_b450)) } }
ASSERT(ADDR(.tsl9_code_0000b450) == 0xB450, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b450) == 26, "R76 exact size");
SECTIONS { .tsl9_code_0000b480 0xB480 : { KEEP(*(.text.tsl9_callback_b480)) } }
ASSERT(ADDR(.tsl9_code_0000b480) == 0xB480, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000b480) == 110, "R76 exact size");
SECTIONS { .tsl9_code_0000cbb8 0xCBB8 : { KEEP(*(.text.tsl9_runtime_unported_cbb8)) } }
ASSERT(ADDR(.tsl9_code_0000cbb8) == 0xCBB8, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000cbb8) == 18, "R76 exact size");
SECTIONS { .tsl9_code_0000d3b2 0xD3B2 : { KEEP(*(.text.tsl9_callback_d3b2)) } }
ASSERT(ADDR(.tsl9_code_0000d3b2) == 0xD3B2, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d3b2) == 50, "R76 exact size");
SECTIONS { .tsl9_code_0000d62e 0xD62E : { KEEP(*(.text.tsl9_callback_d62e)) } }
ASSERT(ADDR(.tsl9_code_0000d62e) == 0xD62E, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d62e) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0000d63a 0xD63A : { KEEP(*(.text.tsl9_callback_d63a)) } }
ASSERT(ADDR(.tsl9_code_0000d63a) == 0xD63A, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d63a) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0000d646 0xD646 : { KEEP(*(.text.tsl9_callback_d646)) } }
ASSERT(ADDR(.tsl9_code_0000d646) == 0xD646, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d646) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0000d652 0xD652 : { KEEP(*(.text.tsl9_callback_d652)) } }
ASSERT(ADDR(.tsl9_code_0000d652) == 0xD652, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000d652) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0000df44 0xDF44 : { KEEP(*(.text.tsl9_callback_df44)) } }
ASSERT(ADDR(.tsl9_code_0000df44) == 0xDF44, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000df44) == 236, "R76 exact size");
SECTIONS { .tsl9_code_0000ecea 0xECEA : { KEEP(*(.text.tsl9_callback_ecea)) } }
ASSERT(ADDR(.tsl9_code_0000ecea) == 0xECEA, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ecea) == 106, "R76 exact size");
SECTIONS { .tsl9_code_0000ed9a 0xED9A : { KEEP(*(.text.tsl9_callback_ed9a)) } }
ASSERT(ADDR(.tsl9_code_0000ed9a) == 0xED9A, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000ed9a) == 140, "R76 exact size");
SECTIONS { .tsl9_code_0000f31c 0xF31C : { KEEP(*(.text.tsl9_callback_f31c)) } }
ASSERT(ADDR(.tsl9_code_0000f31c) == 0xF31C, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f31c) == 22, "R76 exact size");
SECTIONS { .tsl9_code_0000f6ec 0xF6EC : { KEEP(*(.text.tsl9_runtime_unported_f6ec)) } }
ASSERT(ADDR(.tsl9_code_0000f6ec) == 0xF6EC, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f6ec) == 18, "R76 exact size");
SECTIONS { .tsl9_code_0000f8f2 0xF8F2 : { KEEP(*(.text.tsl9_runtime_unported_f8f2)) } }
ASSERT(ADDR(.tsl9_code_0000f8f2) == 0xF8F2, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f8f2) == 14, "R76 exact size");
SECTIONS { .tsl9_code_0000f900 0xF900 : { KEEP(*(.text.tsl9_runtime_unported_f900)) } }
ASSERT(ADDR(.tsl9_code_0000f900) == 0xF900, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f900) == 6, "R76 exact size");
SECTIONS { .tsl9_code_0000f9b4 0xF9B4 : { KEEP(*(.text.tsl9_runtime_unported_f9b4)) } }
ASSERT(ADDR(.tsl9_code_0000f9b4) == 0xF9B4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f9b4) == 14, "R76 exact size");
SECTIONS { .tsl9_code_0000f9d4 0xF9D4 : { KEEP(*(.text.tsl9_callback_f9d4)) } }
ASSERT(ADDR(.tsl9_code_0000f9d4) == 0xF9D4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000f9d4) == 64, "R76 exact size");
SECTIONS { .tsl9_code_0000fa14 0xFA14 : { KEEP(*(.text.tsl9_callback_fa14)) } }
ASSERT(ADDR(.tsl9_code_0000fa14) == 0xFA14, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fa14) == 68, "R76 exact size");
SECTIONS { .tsl9_code_0000fbf6 0xFBF6 : { KEEP(*(.text.tsl9_callback_fbf6)) } }
ASSERT(ADDR(.tsl9_code_0000fbf6) == 0xFBF6, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0000fbf6) == 32, "R76 exact size");
SECTIONS { .tsl9_code_000103d4 0x103D4 : { KEEP(*(.text.tsl9_runtime_unported_103d4)) } }
ASSERT(ADDR(.tsl9_code_000103d4) == 0x103D4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_000103d4) == 24, "R76 exact size");
SECTIONS { .tsl9_code_000103ec 0x103EC : { KEEP(*(.text.tsl9_callback_103ec)) } }
ASSERT(ADDR(.tsl9_code_000103ec) == 0x103EC, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_000103ec) == 46, "R76 exact size");
SECTIONS { .tsl9_code_00010442 0x10442 : { KEEP(*(.text.tsl9_callback_10442)) } }
ASSERT(ADDR(.tsl9_code_00010442) == 0x10442, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_00010442) == 12, "R76 exact size");
SECTIONS { .tsl9_code_0001044e 0x1044E : { KEEP(*(.text.tsl9_callback_1044e)) } }
ASSERT(ADDR(.tsl9_code_0001044e) == 0x1044E, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001044e) == 28, "R76 exact size");
SECTIONS { .tsl9_code_0001046a 0x1046A : { KEEP(*(.text.tsl9_callback_1046a)) } }
ASSERT(ADDR(.tsl9_code_0001046a) == 0x1046A, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001046a) == 48, "R76 exact size");
SECTIONS { .tsl9_code_0001055c 0x1055C : { KEEP(*(.text.tsl9_callback_1055c)) } }
ASSERT(ADDR(.tsl9_code_0001055c) == 0x1055C, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_0001055c) == 8, "R76 exact size");
SECTIONS { .tsl9_code_00017a84 0x17A84 : { KEEP(*(.text.tsl9_runtime_unported_17a84)) } }
ASSERT(ADDR(.tsl9_code_00017a84) == 0x17A84, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017a84) == 66, "R76 exact size");
SECTIONS { .tsl9_code_00017ac6 0x17AC6 : { KEEP(*(.text.tsl9_callback_17ac6)) } }
ASSERT(ADDR(.tsl9_code_00017ac6) == 0x17AC6, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_code_00017ac6) == 652, "R76 exact size");
SECTIONS { .tsl9_ro_000199fc 0x199FC : { KEEP(*(.rodata.tsl9_ro_window_199fc)) } }
ASSERT(ADDR(.tsl9_ro_000199fc) == 0x199FC, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_000199fc) == 110, "R76 exact size");
SECTIONS { .tsl9_ro_00019b40 0x19B40 : { KEEP(*(.rodata.tsl9_ro_window_19b40)) } }
ASSERT(ADDR(.tsl9_ro_00019b40) == 0x19B40, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019b40) == 48, "R76 exact size");
SECTIONS { .tsl9_ro_00019d70 0x19D70 : { KEEP(*(.rodata.tsl9_ro_window_19d70)) } }
ASSERT(ADDR(.tsl9_ro_00019d70) == 0x19D70, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_00019d70) == 3, "R76 exact size");
SECTIONS { .tsl9_ro_0001a0c8 0x1A0C8 : { KEEP(*(.rodata.tsl9_ro_window_1a0c8)) } }
ASSERT(ADDR(.tsl9_ro_0001a0c8) == 0x1A0C8, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a0c8) == 34, "R76 exact size");
SECTIONS { .tsl9_ro_0001a0ec 0x1A0EC : { KEEP(*(.rodata.tsl9_ro_window_1a0ec)) } }
ASSERT(ADDR(.tsl9_ro_0001a0ec) == 0x1A0EC, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a0ec) == 34, "R76 exact size");
SECTIONS { .tsl9_ro_0001a110 0x1A110 : { KEEP(*(.rodata.tsl9_ro_window_1a110)) } }
ASSERT(ADDR(.tsl9_ro_0001a110) == 0x1A110, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a110) == 106, "R76 exact size");
SECTIONS { .tsl9_ro_0001a17c 0x1A17C : { KEEP(*(.rodata.tsl9_ro_window_1a17c)) } }
ASSERT(ADDR(.tsl9_ro_0001a17c) == 0x1A17C, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a17c) == 16, "R76 exact size");
SECTIONS { .tsl9_ro_0001a1b0 0x1A1B0 : { KEEP(*(.rodata.tsl9_ro_window_1a1b0)) } }
ASSERT(ADDR(.tsl9_ro_0001a1b0) == 0x1A1B0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a1b0) == 15, "R76 exact size");
SECTIONS { .tsl9_ro_0001a1c0 0x1A1C0 : { KEEP(*(.rodata.tsl9_ro_window_1a1c0)) } }
ASSERT(ADDR(.tsl9_ro_0001a1c0) == 0x1A1C0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a1c0) == 15, "R76 exact size");
SECTIONS { .tsl9_ro_0001a1d0 0x1A1D0 : { KEEP(*(.rodata.tsl9_ro_window_1a1d0)) } }
ASSERT(ADDR(.tsl9_ro_0001a1d0) == 0x1A1D0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a1d0) == 15, "R76 exact size");
SECTIONS { .tsl9_ro_0001a240 0x1A240 : { KEEP(*(.rodata.tsl9_ro_window_1a240)) } }
ASSERT(ADDR(.tsl9_ro_0001a240) == 0x1A240, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a240) == 4, "R76 exact size");
SECTIONS { .tsl9_ro_0001a248 0x1A248 : { KEEP(*(.rodata.tsl9_ro_window_1a248)) } }
ASSERT(ADDR(.tsl9_ro_0001a248) == 0x1A248, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a248) == 7, "R76 exact size");
SECTIONS { .tsl9_ro_0001a250 0x1A250 : { KEEP(*(.rodata.tsl9_ro_window_1a250)) } }
ASSERT(ADDR(.tsl9_ro_0001a250) == 0x1A250, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a250) == 19, "R76 exact size");
SECTIONS { .tsl9_ro_0001a264 0x1A264 : { KEEP(*(.rodata.tsl9_ro_window_1a264)) } }
ASSERT(ADDR(.tsl9_ro_0001a264) == 0x1A264, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a264) == 5, "R76 exact size");
SECTIONS { .tsl9_ro_0001a26c 0x1A26C : { KEEP(*(.rodata.tsl9_ro_window_1a26c)) } }
ASSERT(ADDR(.tsl9_ro_0001a26c) == 0x1A26C, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a26c) == 11, "R76 exact size");
SECTIONS { .tsl9_ro_0001a278 0x1A278 : { KEEP(*(.rodata.tsl9_ro_window_1a278)) } }
ASSERT(ADDR(.tsl9_ro_0001a278) == 0x1A278, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a278) == 5, "R76 exact size");
SECTIONS { .tsl9_ro_0001a280 0x1A280 : { KEEP(*(.rodata.tsl9_ro_window_1a280)) } }
ASSERT(ADDR(.tsl9_ro_0001a280) == 0x1A280, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a280) == 4, "R76 exact size");
SECTIONS { .tsl9_ro_0001a288 0x1A288 : { KEEP(*(.rodata.tsl9_ro_window_1a288)) } }
ASSERT(ADDR(.tsl9_ro_0001a288) == 0x1A288, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a288) == 13, "R76 exact size");
SECTIONS { .tsl9_ro_0001a298 0x1A298 : { KEEP(*(.rodata.tsl9_ro_window_1a298)) } }
ASSERT(ADDR(.tsl9_ro_0001a298) == 0x1A298, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a298) == 6, "R76 exact size");
SECTIONS { .tsl9_ro_0001a2a0 0x1A2A0 : { KEEP(*(.rodata.tsl9_ro_window_1a2a0)) } }
ASSERT(ADDR(.tsl9_ro_0001a2a0) == 0x1A2A0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a2a0) == 8, "R76 exact size");
SECTIONS { .tsl9_ro_0001a2ac 0x1A2AC : { KEEP(*(.rodata.tsl9_ro_window_1a2ac)) } }
ASSERT(ADDR(.tsl9_ro_0001a2ac) == 0x1A2AC, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a2ac) == 6, "R76 exact size");
SECTIONS { .tsl9_ro_0001a2b4 0x1A2B4 : { KEEP(*(.rodata.tsl9_ro_window_1a2b4)) } }
ASSERT(ADDR(.tsl9_ro_0001a2b4) == 0x1A2B4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a2b4) == 10, "R76 exact size");
SECTIONS { .tsl9_ro_0001a2c0 0x1A2C0 : { KEEP(*(.rodata.tsl9_ro_window_1a2c0)) } }
ASSERT(ADDR(.tsl9_ro_0001a2c0) == 0x1A2C0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a2c0) == 2, "R76 exact size");
SECTIONS { .tsl9_ro_0001a2c4 0x1A2C4 : { KEEP(*(.rodata.tsl9_ro_window_1a2c4)) } }
ASSERT(ADDR(.tsl9_ro_0001a2c4) == 0x1A2C4, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a2c4) == 9, "R76 exact size");
SECTIONS { .tsl9_ro_0001a334 0x1A334 : { KEEP(*(.rodata.tsl9_ro_window_1a334)) } }
ASSERT(ADDR(.tsl9_ro_0001a334) == 0x1A334, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a334) == 4, "R76 exact size");
SECTIONS { .tsl9_ro_0001a7a0 0x1A7A0 : { KEEP(*(.rodata.tsl9_ro_window_1a7a0)) } }
ASSERT(ADDR(.tsl9_ro_0001a7a0) == 0x1A7A0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a7a0) == 21, "R76 exact size");
SECTIONS { .tsl9_ro_0001a7d0 0x1A7D0 : { KEEP(*(.rodata.tsl9_ro_window_1a7d0)) } }
ASSERT(ADDR(.tsl9_ro_0001a7d0) == 0x1A7D0, "R76 planned origin");
ASSERT(SIZEOF(.tsl9_ro_0001a7d0) == 16, "R76 exact size");

/* R77 exact observed lookup union; no unknown gaps filled. */
SECTIONS { .tsl9_ro_00019b70 0x19B70 : { KEEP(*(.rodata.tsl9_ro_window_19b70)) } }
ASSERT(ADDR(.tsl9_ro_00019b70) == 0x19B70, "R77 origin");
ASSERT(SIZEOF(.tsl9_ro_00019b70) == 432, "R77 exact observed union");
