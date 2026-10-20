#ifndef TSL9_MEMORY_WITNESSES_R57_H
#define TSL9_MEMORY_WITNESSES_R57_H
/* Generated frozen R56 source/ELF observations; offsets assume GP remains0x20004000.
 * This is host-test data, not memory allocation, firmware payload or ABI proof. */
typedef struct {
 rml_witness witness;uint32_t original_pc;
 rml_range runtime_point,runtime_window,boot_point,boot_window;
 unsigned gp_wrapped,pointer_provider_required;
} r57_gp_fixture;
static const r57_gp_fixture r57_gp_fixtures[]={
 /* src/target_ble_platform.c:77; tsl9_runtime_unported_8e82; original0x8eb4 */
 {{UINT32_C(0x200040a5),0u,INT32_C(165),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8eb4),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_platform.c:79; tsl9_runtime_unported_8e82; original0x8eb8 */
 {{UINT32_C(0x2000409c),0u,INT32_C(156),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8eb8),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_platform.c:209; tsl9_runtime_unported_8e82; original0x8f84 */
 {{UINT32_C(0x20004088),0u,INT32_C(136),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8f84),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_platform.c:228; tsl9_runtime_unported_8e82; original0x8fa0 */
 {{UINT32_C(0x20004000),0u,INT32_C(0),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8fa0),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_platform.c:238; tsl9_runtime_unported_8e82; original0x8fae */
 {{UINT32_C(0x20004098),0u,INT32_C(152),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8fae),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_platform.c:325; tsl9_ble_scheduler_init_9058; original0x9086 */
 {{UINT32_C(0x200040ae),1u,INT32_C(174),1u,RML_WITNESS_WRITE},UINT32_C(0x9086),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_ble_service_events.c:94; tsl9_service_events_scan_10c48; original0x10c5a */
 {{UINT32_C(0x20004058),0u,INT32_C(88),1u,RML_WITNESS_ADDRESS},UINT32_C(0x10c5a),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_service_events.c:137; tsl9_service_events_scan_10c48; original0x10c90 */
 {{UINT32_C(0x2000405c),0u,INT32_C(92),1u,RML_WITNESS_ADDRESS},UINT32_C(0x10c90),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_service_events.c:273; tsl9_service_events_dispatch_111d2; original0x11200 */
 {{UINT32_C(0x20004058),0u,INT32_C(88),1u,RML_WITNESS_ADDRESS},UINT32_C(0x11200),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_service_events.c:835; tsl9_runtime_unported_196b0; original0x1970c */
 {{UINT32_C(0x20004184),1u,INT32_C(388),1u,RML_WITNESS_READ},UINT32_C(0x1970c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_ble_service_events.c:858; tsl9_runtime_unported_196b0; original0x1972c */
 {{UINT32_C(0x20004184),1u,INT32_C(388),1u,RML_WITNESS_READ},UINT32_C(0x1972c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_ble_services.c:237; tsl9_runtime_unported_1986a; original0x19884 */
 {{UINT32_C(0x20004184),0u,INT32_C(388),1u,RML_WITNESS_ADDRESS},UINT32_C(0x19884),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_ble_services.c:653; tsl9_rtc_startup_18fee; original0x18ff0 */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x18ff0),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_board_init.c:125; tsl9_runtime_unported_19490; original0x19490 */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x19490),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_board_init.c:137; tsl9_runtime_unported_19490; original0x194a6 */
 {{UINT32_C(0x2000417e),1u,INT32_C(382),1u,RML_WITNESS_WRITE},UINT32_C(0x194a6),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_board_init.c:143; tsl9_runtime_unported_19490; original0x194b2 */
 {{UINT32_C(0x2000417c),2u,INT32_C(380),1u,RML_WITNESS_WRITE},UINT32_C(0x194b2),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_bridge_frame.c:138; tsl9_ble_frame_8cfa; original0x8d0e */
 {{UINT32_C(0x2000409e),2u,INT32_C(158),1u,RML_WITNESS_READ},UINT32_C(0x8d0e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_bridge_frame.c:153; tsl9_ble_frame_8cfa; original0x8d2e */
 {{UINT32_C(0x20004088),0u,INT32_C(136),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8d2e),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bridge_frame.c:160; tsl9_ble_frame_8cfa; original0x8d3a */
 {{UINT32_C(0x200040a2),2u,INT32_C(162),1u,RML_WITNESS_READ},UINT32_C(0x8d3a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_bridge_frame.c:169; tsl9_ble_frame_8cfa; original0x8d52 */
 {{UINT32_C(0x20004088),0u,INT32_C(136),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8d52),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bridge_frame.c:243; tsl9_ble_frame_8cfa; original0x8dde */
 {{UINT32_C(0x2000409c),0u,INT32_C(156),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8dde),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bus_init.c:89; tsl9_runtime_unported_12b9c; original0x12c04 */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x12c04),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bus_init.c:153; tsl9_runtime_unported_16dac; original0x16dc0 */
 {{UINT32_C(0x20004168),0u,INT32_C(360),1u,RML_WITNESS_ADDRESS},UINT32_C(0x16dc0),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bus_init.c:161; tsl9_runtime_unported_16dac; original0x16dd2 */
 {{UINT32_C(0x2000416b),0u,INT32_C(363),1u,RML_WITNESS_ADDRESS},UINT32_C(0x16dd2),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_bus_init.c:185; tsl9_runtime_unported_16dac; original0x16e1e */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x16e1e),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_filters.c:152; tsl9_spi_select_165cc; original0x165e0 */
 {{UINT32_C(0x2000416b),1u,INT32_C(363),1u,RML_WITNESS_READ},UINT32_C(0x165e0),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_can_transmit.c:42; tsl9_runtime_unported_8202; original0x8208 */
 {{UINT32_C(0x200040c0),0u,INT32_C(192),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8208),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:61; tsl9_tx_gate_8214; original0x8214 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x8214),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:74; tsl9_tx_gate_8214; original0x822c */
 {{UINT32_C(0x200040c0),0u,INT32_C(192),1u,RML_WITNESS_ADDRESS},UINT32_C(0x822c),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:188; tsl9_tx_apply_c544; original0xc544 */
 {{UINT32_C(0x200040dc),0u,INT32_C(220),1u,RML_WITNESS_ADDRESS},UINT32_C(0xc544),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:321; tsl9_runtime_unported_c612; original0xc620 */
 {{UINT32_C(0x200040dc),0u,INT32_C(220),1u,RML_WITNESS_ADDRESS},UINT32_C(0xc620),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:349; tsl9_tx_clear_c634; original0xc640 */
 {{UINT32_C(0x200040dc),0u,INT32_C(220),1u,RML_WITNESS_ADDRESS},UINT32_C(0xc640),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_can_transmit.c:930; tsl9_spi_transmit_168f0; original0x16900 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x16900),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_config_storage.c:36; tsl9_runtime_unported_9e2c; original0x9e2e */
 {{UINT32_C(0x200040b1),1u,INT32_C(177),1u,RML_WITNESS_WRITE},UINT32_C(0x9e2e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1260; tsl9_runtime_unported_14af8; original0x150d6 */
 {{UINT32_C(0x2000415c),1u,INT32_C(348),1u,RML_WITNESS_WRITE},UINT32_C(0x150d6),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1268; tsl9_runtime_unported_14af8; original0x150e2 */
 {{UINT32_C(0x20004163),1u,INT32_C(355),1u,RML_WITNESS_WRITE},UINT32_C(0x150e2),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1281; tsl9_runtime_unported_14af8; original0x150f4 */
 {{UINT32_C(0x20004161),1u,INT32_C(353),1u,RML_WITNESS_WRITE},UINT32_C(0x150f4),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1311; tsl9_runtime_unported_14af8; original0x15116 */
 {{UINT32_C(0x20004164),1u,INT32_C(356),1u,RML_WITNESS_WRITE},UINT32_C(0x15116),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1321; tsl9_runtime_unported_14af8; original0x15120 */
 {{UINT32_C(0x20004162),1u,INT32_C(354),1u,RML_WITNESS_READ},UINT32_C(0x15120),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1330; tsl9_runtime_unported_14af8; original0x1512a */
 {{UINT32_C(0x2000415c),1u,INT32_C(348),1u,RML_WITNESS_READ},UINT32_C(0x1512a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1336; tsl9_runtime_unported_14af8; original0x15132 */
 {{UINT32_C(0x20004160),1u,INT32_C(352),1u,RML_WITNESS_READ},UINT32_C(0x15132),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1345; tsl9_runtime_unported_14af8; original0x1513c */
 {{UINT32_C(0x20004162),1u,INT32_C(354),1u,RML_WITNESS_READ},UINT32_C(0x1513c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1354; tsl9_runtime_unported_14af8; original0x15146 */
 {{UINT32_C(0x2000415c),1u,INT32_C(348),1u,RML_WITNESS_READ},UINT32_C(0x15146),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1360; tsl9_runtime_unported_14af8; original0x1514e */
 {{UINT32_C(0x20004160),1u,INT32_C(352),1u,RML_WITNESS_READ},UINT32_C(0x1514e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_dispatch.c:1374; tsl9_runtime_unported_14af8; original0x1515c */
 {{UINT32_C(0x20004164),1u,INT32_C(356),1u,RML_WITNESS_WRITE},UINT32_C(0x1515c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_events.c:69; tsl9_exti_5_9_irq; original0x16d3a */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_READ},UINT32_C(0x16d3a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_events.c:71; tsl9_exti_5_9_irq; original0x16d42 */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_WRITE},UINT32_C(0x16d42),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_events.c:79; tsl9_exti_5_9_irq; original0x16d5e */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_READ},UINT32_C(0x16d5e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_events.c:81; tsl9_exti_5_9_irq; original0x16d66 */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_WRITE},UINT32_C(0x16d66),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_events.c:94; tsl9_rtc_alarm_irq; original0x1992e */
 {{UINT32_C(0x20004188),4u,INT32_C(392),1u,RML_WITNESS_WRITE},UINT32_C(0x1992e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_feature_init.c:72; tsl9_feature_init_a2a0; original0xa2ac */
 {{UINT32_C(0x200040b4),0u,INT32_C(180),1u,RML_WITNESS_ADDRESS},UINT32_C(0xa2ac),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:138; tsl9_feature_init_af18; original0xaf24 */
 {{UINT32_C(0x200040c0),0u,INT32_C(192),1u,RML_WITNESS_ADDRESS},UINT32_C(0xaf24),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:188; tsl9_feature_init_b060; original0xb06c */
 {{UINT32_C(0x200040c4),0u,INT32_C(196),1u,RML_WITNESS_ADDRESS},UINT32_C(0xb06c),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:269; tsl9_feature_init_c516; original0xc53c */
 {{UINT32_C(0x200040d0),0u,INT32_C(208),1u,RML_WITNESS_ADDRESS},UINT32_C(0xc53c),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:334; tsl9_feature_init_cff4; original0xd000 */
 {{UINT32_C(0x200040e8),0u,INT32_C(232),1u,RML_WITNESS_ADDRESS},UINT32_C(0xd000),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:398; tsl9_feature_init_d514; original0xd520 */
 {{UINT32_C(0x200040f0),0u,INT32_C(240),1u,RML_WITNESS_ADDRESS},UINT32_C(0xd520),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:418; tsl9_feature_init_d5e4; original0xd5f0 */
 {{UINT32_C(0x200040fc),0u,INT32_C(252),1u,RML_WITNESS_ADDRESS},UINT32_C(0xd5f0),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:504; tsl9_feature_init_f906; original0xf912 */
 {{UINT32_C(0x20004114),0u,INT32_C(276),1u,RML_WITNESS_ADDRESS},UINT32_C(0xf912),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:524; tsl9_feature_init_f9c2; original0xf9ce */
 {{UINT32_C(0x2000411c),0u,INT32_C(284),1u,RML_WITNESS_ADDRESS},UINT32_C(0xf9ce),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:544; tsl9_feature_init_fdfa; original0xfe06 */
 {{UINT32_C(0x20004120),0u,INT32_C(288),1u,RML_WITNESS_ADDRESS},UINT32_C(0xfe06),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:564; tsl9_feature_init_fee4; original0xfef0 */
 {{UINT32_C(0x2000412c),0u,INT32_C(300),1u,RML_WITNESS_ADDRESS},UINT32_C(0xfef0),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:606; tsl9_feature_init_10128; original0x10134 */
 {{UINT32_C(0x20004130),0u,INT32_C(304),1u,RML_WITNESS_ADDRESS},UINT32_C(0x10134),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_feature_init.c:650; tsl9_runtime_unported_1524e; original0x1525c */
 {{UINT32_C(0x20004160),0u,INT32_C(352),1u,RML_WITNESS_ADDRESS},UINT32_C(0x1525c),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_irq.c:59; tsl9_ble_lle_irq; original0x84cc */
 {{UINT32_C(0x20004180),0u,INT32_C(384),1u,RML_WITNESS_ADDRESS},UINT32_C(0x84cc),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_mode_setup.c:461; tsl9_runtime_unported_1291c; original0x129be */
 {{UINT32_C(0x20004078),0u,INT32_C(120),1u,RML_WITNESS_ADDRESS},UINT32_C(0x129be),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_mode_setup.c:477; tsl9_runtime_unported_1291c; original0x129d2 */
 {{UINT32_C(0x20004080),0u,INT32_C(128),1u,RML_WITNESS_ADDRESS},UINT32_C(0x129d2),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_peripherals.c:242; tsl9_timer3_irq; original0x9820 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x9820),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_queue.c:79; tsl9_scheduler_cancel_908e; original0x90d0 */
 {{UINT32_C(0x200040ae),1u,INT32_C(174),1u,RML_WITNESS_READ},UINT32_C(0x90d0),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:125; tsl9_rf_queue_complete_1743a; original0x1744c */
 {{UINT32_C(0x2000406c),1u,INT32_C(108),1u,RML_WITNESS_READ},UINT32_C(0x1744c),RML_RANGE_DATA,RML_RANGE_DATA,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:130; tsl9_rf_queue_complete_1743a; original0x17454 */
 {{UINT32_C(0x2000417a),1u,INT32_C(378),1u,RML_WITNESS_READ},UINT32_C(0x17454),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:141; tsl9_rf_queue_complete_1743a; original0x17468 */
 {{UINT32_C(0x2000417a),1u,INT32_C(378),1u,RML_WITNESS_WRITE},UINT32_C(0x17468),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:185; tsl9_rf_queue_handshake_17474; original0x1749e */
 {{UINT32_C(0x20004179),1u,INT32_C(377),1u,RML_WITNESS_READ},UINT32_C(0x1749e),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:190; tsl9_rf_queue_handshake_17474; original0x174a8 */
 {{UINT32_C(0x20004179),1u,INT32_C(377),1u,RML_WITNESS_WRITE},UINT32_C(0x174a8),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:304; tsl9_rf_queue_task_174cc; original0x17554 */
 {{UINT32_C(0x20004178),1u,INT32_C(376),1u,RML_WITNESS_READ},UINT32_C(0x17554),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:309; tsl9_rf_queue_task_174cc; original0x1755e */
 {{UINT32_C(0x20004068),0u,INT32_C(104),1u,RML_WITNESS_ADDRESS},UINT32_C(0x1755e),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_queue.c:319; tsl9_rf_queue_task_174cc; original0x17576 */
 {{UINT32_C(0x20004178),1u,INT32_C(376),1u,RML_WITNESS_READ},UINT32_C(0x17576),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:328; tsl9_rf_queue_task_174cc; original0x17586 */
 {{UINT32_C(0x20004178),1u,INT32_C(376),1u,RML_WITNESS_WRITE},UINT32_C(0x17586),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:366; tsl9_rf_queue_task_174cc; original0x175cc */
 {{UINT32_C(0x20004171),1u,INT32_C(369),1u,RML_WITNESS_READ},UINT32_C(0x175cc),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:368; tsl9_rf_queue_task_174cc; original0x175d4 */
 {{UINT32_C(0x20004171),1u,INT32_C(369),1u,RML_WITNESS_WRITE},UINT32_C(0x175d4),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:401; tsl9_rf_queue_task_174cc; original0x17606 */
 {{UINT32_C(0x20004172),1u,INT32_C(370),1u,RML_WITNESS_READ},UINT32_C(0x17606),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:427; tsl9_rf_queue_task_174cc; original0x1763c */
 {{UINT32_C(0x20004172),1u,INT32_C(370),1u,RML_WITNESS_WRITE},UINT32_C(0x1763c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:639; tsl9_rf_queue_select_1775e; original0x17772 */
 {{UINT32_C(0x20004064),0u,INT32_C(100),1u,RML_WITNESS_ADDRESS},UINT32_C(0x17772),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_queue.c:661; tsl9_rf_queue_select_1775e; original0x1779a */
 {{UINT32_C(0x2000416f),1u,INT32_C(367),1u,RML_WITNESS_WRITE},UINT32_C(0x1779a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:670; tsl9_rf_queue_select_1775e; original0x177a8 */
 {{UINT32_C(0x20004170),1u,INT32_C(368),1u,RML_WITNESS_WRITE},UINT32_C(0x177a8),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:683; tsl9_rf_queue_select_1775e; original0x177b8 */
 {{UINT32_C(0x20004178),1u,INT32_C(376),1u,RML_WITNESS_WRITE},UINT32_C(0x177b8),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:690; tsl9_rf_queue_select_1775e; original0x177c6 */
 {{UINT32_C(0x2000406c),1u,INT32_C(108),1u,RML_WITNESS_READ},UINT32_C(0x177c6),RML_RANGE_DATA,RML_RANGE_DATA,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:707; tsl9_rf_queue_start_17966; original0x17966 */
 {{UINT32_C(0x2000417a),1u,INT32_C(378),1u,RML_WITNESS_READ},UINT32_C(0x17966),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:723; tsl9_rf_queue_start_17966; original0x17980 */
 {{UINT32_C(0x20004179),1u,INT32_C(377),1u,RML_WITNESS_WRITE},UINT32_C(0x17980),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:728; tsl9_rf_queue_start_17966; original0x1798a */
 {{UINT32_C(0x2000417a),1u,INT32_C(378),1u,RML_WITNESS_READ},UINT32_C(0x1798a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:734; tsl9_rf_queue_start_17966; original0x17992 */
 {{UINT32_C(0x2000417a),1u,INT32_C(378),1u,RML_WITNESS_READ},UINT32_C(0x17992),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_queue.c:796; tsl9_runtime_unported_179ca; original0x179da */
 {{UINT32_C(0x20004178),0u,INT32_C(376),1u,RML_WITNESS_ADDRESS},UINT32_C(0x179da),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_queue.c:818; tsl9_runtime_unported_179ca; original0x17a00 */
 {{UINT32_C(0x2000406c),1u,INT32_C(108),1u,RML_WITNESS_WRITE},UINT32_C(0x17a00),RML_RANGE_DATA,RML_RANGE_DATA,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_runtime.c:248; tsl9_runtime_unported_1730e; original0x1731a */
 {{UINT32_C(0x2000416e),1u,INT32_C(366),1u,RML_WITNESS_READ},UINT32_C(0x1731a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_runtime.c:256; tsl9_runtime_unported_1730e; original0x17326 */
 {{UINT32_C(0x2000416e),1u,INT32_C(366),1u,RML_WITNESS_WRITE},UINT32_C(0x17326),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:42; tsl9_rf_flag_81aa; original0x81aa */
 {{UINT32_C(0x200040af),1u,INT32_C(175),1u,RML_WITNESS_READ},UINT32_C(0x81aa),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:56; tsl9_rf_enabled_843a; original0x843a */
 {{UINT32_C(0x2000416c),1u,INT32_C(364),1u,RML_WITNESS_READ},UINT32_C(0x843a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:70; tsl9_timer_start_9388; original0x9388 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x9388),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_timer.c:295; tsl9_runtime_unported_9936; original0x996a */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x996a),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_timer.c:342; tsl9_rf_flag_9edc; original0x9edc */
 {{UINT32_C(0x200040b4),1u,INT32_C(180),1u,RML_WITNESS_READ},UINT32_C(0x9edc),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:386; tsl9_rf_schedule_16f4a; original0x16f58 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x16f58),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_timer.c:437; tsl9_rf_schedule_16f4a; original0x16fac */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_READ},UINT32_C(0x16fac),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:450; tsl9_rf_schedule_16f4a; original0x16fc8 */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_READ},UINT32_C(0x16fc8),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:522; tsl9_rf_control_17048; original0x17056 */
 {{UINT32_C(0x2000416c),1u,INT32_C(364),1u,RML_WITNESS_WRITE},UINT32_C(0x17056),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:533; tsl9_rf_control_17048; original0x17068 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x17068),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_timer.c:554; tsl9_rf_control_17048; original0x17090 */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_READ},UINT32_C(0x17090),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:577; tsl9_rf_control_17048; original0x170b2 */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_READ},UINT32_C(0x170b2),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:583; tsl9_rf_control_17048; original0x170bc */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_READ},UINT32_C(0x170bc),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:623; tsl9_runtime_unported_17176; original0x17186 */
 {{UINT32_C(0x2000416c),0u,INT32_C(364),1u,RML_WITNESS_ADDRESS},UINT32_C(0x17186),RML_RANGE_BSS,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_rf_timer.c:634; tsl9_runtime_unported_17176; original0x1719a */
 {{UINT32_C(0x2000416d),1u,INT32_C(365),1u,RML_WITNESS_WRITE},UINT32_C(0x1719a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_rf_timer.c:635; tsl9_runtime_unported_17176; original0x1719e */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x1719e),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_runtime_entry.c:161; tsl9_entry_clock_update_18588; original0x185a4 */
 {{UINT32_C(0x20004070),4u,INT32_C(112),1u,RML_WITNESS_WRITE},UINT32_C(0x185a4),RML_RANGE_DATA,RML_RANGE_DATA,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:164; tsl9_entry_clock_update_18588; original0x185ae */
 {{UINT32_C(0x20004040),0u,INT32_C(64),1u,RML_WITNESS_ADDRESS},UINT32_C(0x185ae),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_runtime_entry.c:169; tsl9_entry_clock_update_18588; original0x185bc */
 {{UINT32_C(0x20004070),0u,INT32_C(112),1u,RML_WITNESS_ADDRESS},UINT32_C(0x185bc),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_BSS,RML_RANGE_EMPTY,0u,0u},
 /* src/target_runtime_entry.c:172; tsl9_entry_clock_update_18588; original0x185c6 */
 {{UINT32_C(0x20004070),4u,INT32_C(112),1u,RML_WITNESS_WRITE},UINT32_C(0x185c6),RML_RANGE_DATA,RML_RANGE_DATA,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:228; tsl9_entry_exti_consume_16d6e; original0x16d70 */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_READ},UINT32_C(0x16d70),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:234; tsl9_entry_exti_consume_16d6e; original0x16d80 */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_WRITE},UINT32_C(0x16d80),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:238; tsl9_entry_exti_consume_16d6e; original0x16d88 */
 {{UINT32_C(0x20004169),1u,INT32_C(361),1u,RML_WITNESS_WRITE},UINT32_C(0x16d88),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:240; tsl9_entry_exti_consume_16d6e; original0x16d8c */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_READ},UINT32_C(0x16d8c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:245; tsl9_entry_exti_consume_16d6e; original0x16d9a */
 {{UINT32_C(0x20004168),1u,INT32_C(360),1u,RML_WITNESS_WRITE},UINT32_C(0x16d9a),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:249; tsl9_entry_exti_consume_16d6e; original0x16da2 */
 {{UINT32_C(0x2000416a),1u,INT32_C(362),1u,RML_WITNESS_WRITE},UINT32_C(0x16da2),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_runtime_entry.c:283; tsl9_entry_can_consume_12a68; original0x12a92 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x12a92),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_scheduler_gpio.c:29; tsl9_runtime_unported_9b2c; original0x9b2c */
 {{UINT32_C(0x200040b0),1u,INT32_C(176),1u,RML_WITNESS_WRITE},UINT32_C(0x9b2c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:31; tsl9_runtime_unported_9b2c; original0x9b30 */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x9b30),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
 /* src/target_scheduler_gpio.c:87; tsl9_runtime_unported_9b14; original0x9b14 */
 {{UINT32_C(0x200040b0),1u,INT32_C(176),1u,RML_WITNESS_READ},UINT32_C(0x9b14),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:180; tsl9_sgpio_register_9102; original0x9156 */
 {{UINT32_C(0x200040ae),1u,INT32_C(174),1u,RML_WITNESS_READ},UINT32_C(0x9156),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:239; tsl9_sgpio_register_9102; original0x919c */
 {{UINT32_C(0x200040ae),1u,INT32_C(174),1u,RML_WITNESS_READ},UINT32_C(0x919c),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:316; tsl9_sgpio_register_9102; original0x9204 */
 {{UINT32_C(0x200040ae),1u,INT32_C(174),1u,RML_WITNESS_READ},UINT32_C(0x9204),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:540; tsl9_sgpio_idle_9ace; original0x9ace */
 {{UINT32_C(0x200040b0),1u,INT32_C(176),1u,RML_WITNESS_READ},UINT32_C(0x9ace),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_scheduler_gpio.c:565; tsl9_sgpio_expire_9ab0; original0x9ab2 */
 {{UINT32_C(0x200040b0),1u,INT32_C(176),1u,RML_WITNESS_WRITE},UINT32_C(0x9ab2),RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,RML_RANGE_BSS,0u,0u},
 /* src/target_settings_load.c:618; tsl9_settings_default_12f8a; original0x12fba */
 {{UINT32_C(0x20004054),0u,INT32_C(84),1u,RML_WITNESS_ADDRESS},UINT32_C(0x12fba),RML_RANGE_DATA,RML_RANGE_EMPTY,RML_RANGE_DATA,RML_RANGE_EMPTY,0u,0u},
};
#define R57_GP_FIXTURE_COUNT (sizeof(r57_gp_fixtures)/sizeof(r57_gp_fixtures[0]))
#endif
