OUTPUT_ARCH(riscv)
ENTRY(__tsl9v4160_image_entry)
SECTIONS {
 .text.tsl9v4160.image_entry 0x8000 : { KEEP(*(.text.tsl9v4160.image_entry)) }
 ASSERT(SIZEOF(.text.tsl9v4160.image_entry)==4, "Storage size changed")
 .rodata.tsl9v4160.image_only_8004 0x8004 : { KEEP(*(.rodata.tsl9v4160.image_only_8004)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_8004)==52, "Storage size changed")
 .rodata.tsl9v4160.vector_capture 0x8038 : { KEEP(*(.rodata.tsl9v4160.vector_capture)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.vector_capture)==328, "Storage size changed")
 .text.tsl9v4160.core_flow_8180 0x8180 : { KEEP(*(.text.tsl9v4160.core_flow_8180)) }
 ASSERT(SIZEOF(.text.tsl9v4160.core_flow_8180)==42, "Storage size changed")
 .text.tsl9v4160.direct_expansion_81aa 0x81aa : { KEEP(*(.text.tsl9v4160.direct_expansion_81aa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_81aa)==6, "Storage size changed")
 .text.tsl9v4160.callee_81b0 0x81b0 : { KEEP(*(.text.tsl9v4160.callee_81b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_81b0)==26, "Storage size changed")
 .rodata.tsl9v4160.image_only_81ca 0x81ca : { KEEP(*(.rodata.tsl9v4160.image_only_81ca)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_81ca)==20, "Storage size changed")
 .text.tsl9v4160.code_continuation_81de 0x81de : { KEEP(*(.text.tsl9v4160.code_continuation_81de)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_81de)==16, "Storage size changed")
 .text.tsl9v4160.direct_successors_81ee 0x81ee : { KEEP(*(.text.tsl9v4160.direct_successors_81ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_81ee)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_81f8 0x81f8 : { KEEP(*(.text.tsl9v4160.direct_successors_81f8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_81f8)==10, "Storage size changed")
 .text.tsl9v4160.direct_closure_8202 0x8202 : { KEEP(*(.text.tsl9v4160.direct_closure_8202)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_8202)==10, "Storage size changed")
 .text.tsl9v4160.direct_expansion_820c 0x820c : { KEEP(*(.text.tsl9v4160.direct_expansion_820c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_820c)==18, "Storage size changed")
 .text.tsl9v4160.code_continuation_821e 0x821e : { KEEP(*(.text.tsl9v4160.code_continuation_821e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_821e)==42, "Storage size changed")
 .text.tsl9v4160.direct_successors_8248 0x8248 : { KEEP(*(.text.tsl9v4160.direct_successors_8248)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_8248)==68, "Storage size changed")
 .text.tsl9v4160.direct_successors_828c 0x828c : { KEEP(*(.text.tsl9v4160.direct_successors_828c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_828c)==18, "Storage size changed")
 .text.tsl9v4160.direct_expansion_829e 0x829e : { KEEP(*(.text.tsl9v4160.direct_expansion_829e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_829e)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_82a8 0x82a8 : { KEEP(*(.text.tsl9v4160.post_table_code_82a8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_82a8)==42, "Storage size changed")
 .text.tsl9v4160.direct_expansion_82d2 0x82d2 : { KEEP(*(.text.tsl9v4160.direct_expansion_82d2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_82d2)==188, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_838e 0x838e : { KEEP(*(.text.tsl9v4160.conditional_runtime_838e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_838e)==178, "Storage size changed")
 .text.tsl9v4160.code_continuation_8440 0x8440 : { KEEP(*(.text.tsl9v4160.code_continuation_8440)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_8440)==6, "Storage size changed")
 .rodata.tsl9v4160.image_only_8446 0x8446 : { KEEP(*(.rodata.tsl9v4160.image_only_8446)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_8446)==2, "Storage size changed")
 .text.tsl9v4160.handler_8448 0x8448 : { KEEP(*(.text.tsl9v4160.handler_8448)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_8448)==78, "Storage size changed")
 .rodata.tsl9v4160.image_only_8496 0x8496 : { KEEP(*(.rodata.tsl9v4160.image_only_8496)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_8496)==2, "Storage size changed")
 .text.tsl9v4160.handler_8498 0x8498 : { KEEP(*(.text.tsl9v4160.handler_8498)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_8498)==134, "Storage size changed")
 .rodata.tsl9v4160.image_only_851e 0x851e : { KEEP(*(.rodata.tsl9v4160.image_only_851e)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_851e)==2, "Storage size changed")
 .text.tsl9v4160.direct_expansion_8520 0x8520 : { KEEP(*(.text.tsl9v4160.direct_expansion_8520)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_8520)==168, "Storage size changed")
 .text.tsl9v4160.residual_callbacks_85c8 0x85c8 : { KEEP(*(.text.tsl9v4160.residual_callbacks_85c8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_callbacks_85c8)==76, "Storage size changed")
 .text.tsl9v4160.callback_8614 0x8614 : { KEEP(*(.text.tsl9v4160.callback_8614)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_8614)==632, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_888c 0x888c : { KEEP(*(.text.tsl9v4160.gatt_ingress_888c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_888c)==458, "Storage size changed")
 .text.tsl9v4160.code_continuation_8a56 0x8a56 : { KEEP(*(.text.tsl9v4160.code_continuation_8a56)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_8a56)==280, "Storage size changed")
 .text.tsl9v4160.direct_expansion_8b6e 0x8b6e : { KEEP(*(.text.tsl9v4160.direct_expansion_8b6e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_8b6e)==34, "Storage size changed")
 .text.tsl9v4160.residual_callbacks_8b90 0x8b90 : { KEEP(*(.text.tsl9v4160.residual_callbacks_8b90)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_callbacks_8b90)==242, "Storage size changed")
 .text.tsl9v4160.callback_8c82 0x8c82 : { KEEP(*(.text.tsl9v4160.callback_8c82)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_8c82)==406, "Storage size changed")
 .text.tsl9v4160.ota_handler_8e18 0x8e18 : { KEEP(*(.text.tsl9v4160.ota_handler_8e18)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_8e18)==82, "Storage size changed")
 .text.tsl9v4160.direct_frontier_8e6a 0x8e6a : { KEEP(*(.text.tsl9v4160.direct_frontier_8e6a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_8e6a)==30, "Storage size changed")
 .text.tsl9v4160.init_8e88 0x8e88 : { KEEP(*(.text.tsl9v4160.init_8e88)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_8e88)==384, "Storage size changed")
 .text.tsl9v4160.main 0x9008 : { KEEP(*(.text.tsl9v4160.main)) }
 ASSERT(SIZEOF(.text.tsl9v4160.main)==18, "Storage size changed")
 .text.tsl9v4160.conditional_dispatcher_901a 0x901a : { KEEP(*(.text.tsl9v4160.conditional_dispatcher_901a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_dispatcher_901a)==96, "Storage size changed")
 .text.tsl9v4160.direct_expansion_907a 0x907a : { KEEP(*(.text.tsl9v4160.direct_expansion_907a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_907a)==54, "Storage size changed")
 .text.tsl9v4160.direct_expansion_90b0 0x90b0 : { KEEP(*(.text.tsl9v4160.direct_expansion_90b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_90b0)==116, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9124 0x9124 : { KEEP(*(.text.tsl9v4160.direct_expansion_9124)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9124)==300, "Storage size changed")
 .text.tsl9v4160.core_flow_9250 0x9250 : { KEEP(*(.text.tsl9v4160.core_flow_9250)) }
 ASSERT(SIZEOF(.text.tsl9v4160.core_flow_9250)==64, "Storage size changed")
 .text.tsl9v4160.direct_closure_9290 0x9290 : { KEEP(*(.text.tsl9v4160.direct_closure_9290)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_9290)==42, "Storage size changed")
 .text.tsl9v4160.direct_closure_92ba 0x92ba : { KEEP(*(.text.tsl9v4160.direct_closure_92ba)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_92ba)==56, "Storage size changed")
 .text.tsl9v4160.ota_handler_92f2 0x92f2 : { KEEP(*(.text.tsl9v4160.ota_handler_92f2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_92f2)==66, "Storage size changed")
 .text.tsl9v4160.code_continuation_9334 0x9334 : { KEEP(*(.text.tsl9v4160.code_continuation_9334)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_9334)==74, "Storage size changed")
 .text.tsl9v4160.direct_expansion_937e 0x937e : { KEEP(*(.text.tsl9v4160.direct_expansion_937e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_937e)==44, "Storage size changed")
 .text.tsl9v4160.code_continuation_93aa 0x93aa : { KEEP(*(.text.tsl9v4160.code_continuation_93aa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_93aa)==68, "Storage size changed")
 .text.tsl9v4160.callee_93ee 0x93ee : { KEEP(*(.text.tsl9v4160.callee_93ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_93ee)==34, "Storage size changed")
 .text.tsl9v4160.code_continuation_9410 0x9410 : { KEEP(*(.text.tsl9v4160.code_continuation_9410)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_9410)==68, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9454 0x9454 : { KEEP(*(.text.tsl9v4160.direct_expansion_9454)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9454)==154, "Storage size changed")
 .text.tsl9v4160.direct_followup_94ee 0x94ee : { KEEP(*(.text.tsl9v4160.direct_followup_94ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_94ee)==26, "Storage size changed")
 .text.tsl9v4160.direct_followup_9508 0x9508 : { KEEP(*(.text.tsl9v4160.direct_followup_9508)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_9508)==70, "Storage size changed")
 .text.tsl9v4160.direct_followup_954e 0x954e : { KEEP(*(.text.tsl9v4160.direct_followup_954e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_954e)==110, "Storage size changed")
 .text.tsl9v4160.direct_followup_95bc 0x95bc : { KEEP(*(.text.tsl9v4160.direct_followup_95bc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_95bc)==82, "Storage size changed")
 .text.tsl9v4160.direct_frontier_960e 0x960e : { KEEP(*(.text.tsl9v4160.direct_frontier_960e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_960e)==74, "Storage size changed")
 .text.tsl9v4160.direct_frontier_9658 0x9658 : { KEEP(*(.text.tsl9v4160.direct_frontier_9658)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_9658)==74, "Storage size changed")
 .text.tsl9v4160.direct_followup_96a2 0x96a2 : { KEEP(*(.text.tsl9v4160.direct_followup_96a2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_96a2)==154, "Storage size changed")
 .text.tsl9v4160.direct_frontier_973c 0x973c : { KEEP(*(.text.tsl9v4160.direct_frontier_973c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_973c)==86, "Storage size changed")
 .text.tsl9v4160.code_continuation_9792 0x9792 : { KEEP(*(.text.tsl9v4160.code_continuation_9792)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_9792)==12, "Storage size changed")
 .text.tsl9v4160.handler_979e 0x979e : { KEEP(*(.text.tsl9v4160.handler_979e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_979e)==442, "Storage size changed")
 .text.tsl9v4160.init_9958 0x9958 : { KEEP(*(.text.tsl9v4160.init_9958)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_9958)==144, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_99e8 0x99e8 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_99e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_99e8)==60, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9a24 0x9a24 : { KEEP(*(.text.tsl9v4160.direct_expansion_9a24)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9a24)==30, "Storage size changed")
 .text.tsl9v4160.init_9a42 0x9a42 : { KEEP(*(.text.tsl9v4160.init_9a42)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_9a42)==144, "Storage size changed")
 .text.tsl9v4160.callback_9ad2 0x9ad2 : { KEEP(*(.text.tsl9v4160.callback_9ad2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_9ad2)==18, "Storage size changed")
 .text.tsl9v4160.residual_code_9ae4 0x9ae4 : { KEEP(*(.text.tsl9v4160.residual_code_9ae4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_code_9ae4)==12, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9af0 0x9af0 : { KEEP(*(.text.tsl9v4160.direct_expansion_9af0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9af0)==18, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_9b02 0x9b02 : { KEEP(*(.text.tsl9v4160.gatt_ingress_9b02)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_9b02)==52, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9b36 0x9b36 : { KEEP(*(.text.tsl9v4160.direct_expansion_9b36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9b36)==24, "Storage size changed")
 .text.tsl9v4160.init_9b4e 0x9b4e : { KEEP(*(.text.tsl9v4160.init_9b4e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_9b4e)==64, "Storage size changed")
 .text.tsl9v4160.ota_handler_9b8e 0x9b8e : { KEEP(*(.text.tsl9v4160.ota_handler_9b8e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_9b8e)==124, "Storage size changed")
 .text.tsl9v4160.code_continuation_9c0a 0x9c0a : { KEEP(*(.text.tsl9v4160.code_continuation_9c0a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_9c0a)==64, "Storage size changed")
 .text.tsl9v4160.ota_handler_9c4a 0x9c4a : { KEEP(*(.text.tsl9v4160.ota_handler_9c4a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_9c4a)==530, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9e5c 0x9e5c : { KEEP(*(.text.tsl9v4160.direct_expansion_9e5c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9e5c)==40, "Storage size changed")
 .text.tsl9v4160.direct_expansion_9e84 0x9e84 : { KEEP(*(.text.tsl9v4160.direct_expansion_9e84)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_9e84)==34, "Storage size changed")
 .text.tsl9v4160.ota_handler_9ea6 0x9ea6 : { KEEP(*(.text.tsl9v4160.ota_handler_9ea6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_9ea6)==74, "Storage size changed")
 .text.tsl9v4160.direct_followup_9ef0 0x9ef0 : { KEEP(*(.text.tsl9v4160.direct_followup_9ef0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_9ef0)==34, "Storage size changed")
 .text.tsl9v4160.init_9f12 0x9f12 : { KEEP(*(.text.tsl9v4160.init_9f12)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_9f12)==58, "Storage size changed")
 .text.tsl9v4160.init_9f4c 0x9f4c : { KEEP(*(.text.tsl9v4160.init_9f4c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_9f4c)==40, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_9f74 0x9f74 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_9f74)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_9f74)==6, "Storage size changed")
 .text.tsl9v4160.direct_successors_9f7a 0x9f7a : { KEEP(*(.text.tsl9v4160.direct_successors_9f7a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_9f7a)==56, "Storage size changed")
 .text.tsl9v4160.direct_successors_9fb2 0x9fb2 : { KEEP(*(.text.tsl9v4160.direct_successors_9fb2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_9fb2)==16, "Storage size changed")
 .text.tsl9v4160.code_continuation_9fc2 0x9fc2 : { KEEP(*(.text.tsl9v4160.code_continuation_9fc2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_9fc2)==6, "Storage size changed")
 .text.tsl9v4160.direct_successors_9fc8 0x9fc8 : { KEEP(*(.text.tsl9v4160.direct_successors_9fc8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_9fc8)==68, "Storage size changed")
 .text.tsl9v4160.direct_successors_a00c 0xa00c : { KEEP(*(.text.tsl9v4160.direct_successors_a00c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_a00c)==24, "Storage size changed")
 .text.tsl9v4160.direct_followup_a024 0xa024 : { KEEP(*(.text.tsl9v4160.direct_followup_a024)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a024)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_a02e 0xa02e : { KEEP(*(.text.tsl9v4160.direct_successors_a02e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_a02e)==28, "Storage size changed")
 .text.tsl9v4160.direct_successors_a04a 0xa04a : { KEEP(*(.text.tsl9v4160.direct_successors_a04a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_a04a)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_a054 0xa054 : { KEEP(*(.text.tsl9v4160.post_table_code_a054)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_a054)==432, "Storage size changed")
 .text.tsl9v4160.code_continuation_a204 0xa204 : { KEEP(*(.text.tsl9v4160.code_continuation_a204)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_a204)==230, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_a2ea 0xa2ea : { KEEP(*(.text.tsl9v4160.materialized_callbacks_a2ea)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_a2ea)==4, "Storage size changed")
 .text.tsl9v4160.direct_expansion_a2ee 0xa2ee : { KEEP(*(.text.tsl9v4160.direct_expansion_a2ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_a2ee)==142, "Storage size changed")
 .text.tsl9v4160.direct_expansion_a37c 0xa37c : { KEEP(*(.text.tsl9v4160.direct_expansion_a37c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_a37c)==18, "Storage size changed")
 .text.tsl9v4160.direct_followup_a38e 0xa38e : { KEEP(*(.text.tsl9v4160.direct_followup_a38e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a38e)==62, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_a3cc 0xa3cc : { KEEP(*(.text.tsl9v4160.materialized_callbacks_a3cc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_a3cc)==256, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_a4cc 0xa4cc : { KEEP(*(.text.tsl9v4160.materialized_callbacks_a4cc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_a4cc)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_a4d8 0xa4d8 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_a4d8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_a4d8)==22, "Storage size changed")
 .text.tsl9v4160.direct_successors_a4ee 0xa4ee : { KEEP(*(.text.tsl9v4160.direct_successors_a4ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_a4ee)==362, "Storage size changed")
 .text.tsl9v4160.direct_successors_a658 0xa658 : { KEEP(*(.text.tsl9v4160.direct_successors_a658)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_a658)==12, "Storage size changed")
 .text.tsl9v4160.direct_followup_a664 0xa664 : { KEEP(*(.text.tsl9v4160.direct_followup_a664)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a664)==70, "Storage size changed")
 .text.tsl9v4160.direct_followup_a6aa 0xa6aa : { KEEP(*(.text.tsl9v4160.direct_followup_a6aa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a6aa)==46, "Storage size changed")
 .text.tsl9v4160.post_table_code_a6d8 0xa6d8 : { KEEP(*(.text.tsl9v4160.post_table_code_a6d8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_a6d8)==656, "Storage size changed")
 .text.tsl9v4160.direct_closure_a968 0xa968 : { KEEP(*(.text.tsl9v4160.direct_closure_a968)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_a968)==14, "Storage size changed")
 .text.tsl9v4160.direct_frontier_a976 0xa976 : { KEEP(*(.text.tsl9v4160.direct_frontier_a976)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_a976)==70, "Storage size changed")
 .text.tsl9v4160.direct_frontier_a9bc 0xa9bc : { KEEP(*(.text.tsl9v4160.direct_frontier_a9bc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_a9bc)==34, "Storage size changed")
 .text.tsl9v4160.direct_followup_a9de 0xa9de : { KEEP(*(.text.tsl9v4160.direct_followup_a9de)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a9de)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_a9e8 0xa9e8 : { KEEP(*(.text.tsl9v4160.direct_followup_a9e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_a9e8)==48, "Storage size changed")
 .text.tsl9v4160.direct_expansion_aa18 0xaa18 : { KEEP(*(.text.tsl9v4160.direct_expansion_aa18)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_aa18)==22, "Storage size changed")
 .text.tsl9v4160.direct_followup_aa2e 0xaa2e : { KEEP(*(.text.tsl9v4160.direct_followup_aa2e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_aa2e)==50, "Storage size changed")
 .text.tsl9v4160.direct_followup_aa60 0xaa60 : { KEEP(*(.text.tsl9v4160.direct_followup_aa60)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_aa60)==64, "Storage size changed")
 .text.tsl9v4160.direct_followup_aaa0 0xaaa0 : { KEEP(*(.text.tsl9v4160.direct_followup_aaa0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_aaa0)==56, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_aad8 0xaad8 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_aad8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_aad8)==10, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_aae2 0xaae2 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_aae2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_aae2)==16, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_aaf2 0xaaf2 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_aaf2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_aaf2)==16, "Storage size changed")
 .text.tsl9v4160.direct_followup_ab02 0xab02 : { KEEP(*(.text.tsl9v4160.direct_followup_ab02)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ab02)==6, "Storage size changed")
 .text.tsl9v4160.direct_followup_ab08 0xab08 : { KEEP(*(.text.tsl9v4160.direct_followup_ab08)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ab08)==86, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_ab5e 0xab5e : { KEEP(*(.text.tsl9v4160.materialized_callbacks_ab5e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_ab5e)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_ab68 0xab68 : { KEEP(*(.text.tsl9v4160.direct_successors_ab68)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ab68)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_ab72 0xab72 : { KEEP(*(.text.tsl9v4160.direct_frontier_ab72)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_ab72)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_ab7c 0xab7c : { KEEP(*(.text.tsl9v4160.direct_successors_ab7c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ab7c)==72, "Storage size changed")
 .text.tsl9v4160.post_table_code_abc4 0xabc4 : { KEEP(*(.text.tsl9v4160.post_table_code_abc4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_abc4)==46, "Storage size changed")
 .text.tsl9v4160.code_continuation_abf2 0xabf2 : { KEEP(*(.text.tsl9v4160.code_continuation_abf2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_abf2)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_abfc 0xabfc : { KEEP(*(.text.tsl9v4160.direct_followup_abfc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_abfc)==14, "Storage size changed")
 .text.tsl9v4160.direct_successors_ac0a 0xac0a : { KEEP(*(.text.tsl9v4160.direct_successors_ac0a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ac0a)==110, "Storage size changed")
 .text.tsl9v4160.direct_followup_ac78 0xac78 : { KEEP(*(.text.tsl9v4160.direct_followup_ac78)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ac78)==208, "Storage size changed")
 .text.tsl9v4160.direct_successors_ad48 0xad48 : { KEEP(*(.text.tsl9v4160.direct_successors_ad48)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ad48)==112, "Storage size changed")
 .text.tsl9v4160.direct_followup_adb8 0xadb8 : { KEEP(*(.text.tsl9v4160.direct_followup_adb8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_adb8)==30, "Storage size changed")
 .text.tsl9v4160.post_table_code_add6 0xadd6 : { KEEP(*(.text.tsl9v4160.post_table_code_add6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_add6)==56, "Storage size changed")
 .text.tsl9v4160.direct_successors_ae0e 0xae0e : { KEEP(*(.text.tsl9v4160.direct_successors_ae0e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ae0e)==552, "Storage size changed")
 .text.tsl9v4160.post_table_code_b036 0xb036 : { KEEP(*(.text.tsl9v4160.post_table_code_b036)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b036)==38, "Storage size changed")
 .text.tsl9v4160.post_table_code_b05c 0xb05c : { KEEP(*(.text.tsl9v4160.post_table_code_b05c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b05c)==38, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b082 0xb082 : { KEEP(*(.text.tsl9v4160.direct_frontier_b082)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b082)==46, "Storage size changed")
 .text.tsl9v4160.direct_successors_b0b0 0xb0b0 : { KEEP(*(.text.tsl9v4160.direct_successors_b0b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b0b0)==10, "Storage size changed")
 .text.tsl9v4160.direct_expansion_b0ba 0xb0ba : { KEEP(*(.text.tsl9v4160.direct_expansion_b0ba)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_b0ba)==22, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_b0d0 0xb0d0 : { KEEP(*(.text.tsl9v4160.conditional_runtime_b0d0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_b0d0)==44, "Storage size changed")
 .text.tsl9v4160.direct_expansion_b0fc 0xb0fc : { KEEP(*(.text.tsl9v4160.direct_expansion_b0fc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_b0fc)==78, "Storage size changed")
 .text.tsl9v4160.post_table_code_b14a 0xb14a : { KEEP(*(.text.tsl9v4160.post_table_code_b14a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b14a)==44, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b176 0xb176 : { KEEP(*(.text.tsl9v4160.direct_frontier_b176)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b176)==58, "Storage size changed")
 .text.tsl9v4160.direct_closure_b1b0 0xb1b0 : { KEEP(*(.text.tsl9v4160.direct_closure_b1b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_b1b0)==6, "Storage size changed")
 .text.tsl9v4160.post_table_code_b1b6 0xb1b6 : { KEEP(*(.text.tsl9v4160.post_table_code_b1b6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b1b6)==106, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b220 0xb220 : { KEEP(*(.text.tsl9v4160.direct_frontier_b220)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b220)==34, "Storage size changed")
 .text.tsl9v4160.direct_expansion_b242 0xb242 : { KEEP(*(.text.tsl9v4160.direct_expansion_b242)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_b242)==18, "Storage size changed")
 .text.tsl9v4160.direct_successors_b254 0xb254 : { KEEP(*(.text.tsl9v4160.direct_successors_b254)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b254)==70, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_b29a 0xb29a : { KEEP(*(.text.tsl9v4160.materialized_callbacks_b29a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_b29a)==100, "Storage size changed")
 .text.tsl9v4160.post_table_code_b2fe 0xb2fe : { KEEP(*(.text.tsl9v4160.post_table_code_b2fe)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b2fe)==116, "Storage size changed")
 .text.tsl9v4160.post_table_code_b372 0xb372 : { KEEP(*(.text.tsl9v4160.post_table_code_b372)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b372)==30, "Storage size changed")
 .text.tsl9v4160.post_table_code_b390 0xb390 : { KEEP(*(.text.tsl9v4160.post_table_code_b390)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b390)==74, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b3da 0xb3da : { KEEP(*(.text.tsl9v4160.direct_frontier_b3da)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b3da)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b3e4 0xb3e4 : { KEEP(*(.text.tsl9v4160.direct_frontier_b3e4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b3e4)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b3ee 0xb3ee : { KEEP(*(.text.tsl9v4160.direct_frontier_b3ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b3ee)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b3f8 0xb3f8 : { KEEP(*(.text.tsl9v4160.direct_frontier_b3f8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b3f8)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_b402 0xb402 : { KEEP(*(.text.tsl9v4160.post_table_code_b402)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b402)==286, "Storage size changed")
 .text.tsl9v4160.direct_successors_b520 0xb520 : { KEEP(*(.text.tsl9v4160.direct_successors_b520)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b520)==82, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b572 0xb572 : { KEEP(*(.text.tsl9v4160.direct_frontier_b572)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b572)==18, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b584 0xb584 : { KEEP(*(.text.tsl9v4160.direct_frontier_b584)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b584)==16, "Storage size changed")
 .text.tsl9v4160.direct_frontier_b594 0xb594 : { KEEP(*(.text.tsl9v4160.direct_frontier_b594)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_b594)==32, "Storage size changed")
 .text.tsl9v4160.direct_closure_b5b4 0xb5b4 : { KEEP(*(.text.tsl9v4160.direct_closure_b5b4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_b5b4)==18, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_b5c6 0xb5c6 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_b5c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_b5c6)==26, "Storage size changed")
 .text.tsl9v4160.direct_expansion_b5e0 0xb5e0 : { KEEP(*(.text.tsl9v4160.direct_expansion_b5e0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_b5e0)==22, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_b5f6 0xb5f6 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_b5f6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_b5f6)==110, "Storage size changed")
 .text.tsl9v4160.direct_successors_b664 0xb664 : { KEEP(*(.text.tsl9v4160.direct_successors_b664)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b664)==22, "Storage size changed")
 .text.tsl9v4160.direct_successors_b67a 0xb67a : { KEEP(*(.text.tsl9v4160.direct_successors_b67a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b67a)==46, "Storage size changed")
 .text.tsl9v4160.direct_successors_b6a8 0xb6a8 : { KEEP(*(.text.tsl9v4160.direct_successors_b6a8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b6a8)==20, "Storage size changed")
 .text.tsl9v4160.direct_successors_b6bc 0xb6bc : { KEEP(*(.text.tsl9v4160.direct_successors_b6bc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_b6bc)==46, "Storage size changed")
 .text.tsl9v4160.direct_closure_b6ea 0xb6ea : { KEEP(*(.text.tsl9v4160.direct_closure_b6ea)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_b6ea)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_b6f4 0xb6f4 : { KEEP(*(.text.tsl9v4160.direct_followup_b6f4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_b6f4)==60, "Storage size changed")
 .text.tsl9v4160.post_table_code_b730 0xb730 : { KEEP(*(.text.tsl9v4160.post_table_code_b730)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_b730)==1456, "Storage size changed")
 .text.tsl9v4160.direct_successors_bce0 0xbce0 : { KEEP(*(.text.tsl9v4160.direct_successors_bce0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_bce0)==12, "Storage size changed")
 .text.tsl9v4160.direct_followup_bcec 0xbcec : { KEEP(*(.text.tsl9v4160.direct_followup_bcec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_bcec)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_bcf6 0xbcf6 : { KEEP(*(.text.tsl9v4160.direct_frontier_bcf6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_bcf6)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_bd00 0xbd00 : { KEEP(*(.text.tsl9v4160.direct_followup_bd00)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_bd00)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_bd0a 0xbd0a : { KEEP(*(.text.tsl9v4160.direct_frontier_bd0a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_bd0a)==48, "Storage size changed")
 .text.tsl9v4160.direct_frontier_bd3a 0xbd3a : { KEEP(*(.text.tsl9v4160.direct_frontier_bd3a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_bd3a)==12, "Storage size changed")
 .text.tsl9v4160.direct_followup_bd46 0xbd46 : { KEEP(*(.text.tsl9v4160.direct_followup_bd46)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_bd46)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_bd50 0xbd50 : { KEEP(*(.text.tsl9v4160.direct_frontier_bd50)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_bd50)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_bd5a 0xbd5a : { KEEP(*(.text.tsl9v4160.direct_followup_bd5a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_bd5a)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_bd64 0xbd64 : { KEEP(*(.text.tsl9v4160.direct_frontier_bd64)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_bd64)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_bd6e 0xbd6e : { KEEP(*(.text.tsl9v4160.direct_successors_bd6e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_bd6e)==26, "Storage size changed")
 .text.tsl9v4160.post_table_code_bd88 0xbd88 : { KEEP(*(.text.tsl9v4160.post_table_code_bd88)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_bd88)==1020, "Storage size changed")
 .text.tsl9v4160.post_table_code_c184 0xc184 : { KEEP(*(.text.tsl9v4160.post_table_code_c184)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c184)==16, "Storage size changed")
 .text.tsl9v4160.post_table_code_c194 0xc194 : { KEEP(*(.text.tsl9v4160.post_table_code_c194)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c194)==42, "Storage size changed")
 .text.tsl9v4160.post_table_code_c1be 0xc1be : { KEEP(*(.text.tsl9v4160.post_table_code_c1be)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c1be)==188, "Storage size changed")
 .text.tsl9v4160.post_table_code_c27a 0xc27a : { KEEP(*(.text.tsl9v4160.post_table_code_c27a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c27a)==44, "Storage size changed")
 .text.tsl9v4160.post_table_code_c2a6 0xc2a6 : { KEEP(*(.text.tsl9v4160.post_table_code_c2a6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c2a6)==16, "Storage size changed")
 .text.tsl9v4160.post_table_code_c2b6 0xc2b6 : { KEEP(*(.text.tsl9v4160.post_table_code_c2b6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c2b6)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_c2c0 0xc2c0 : { KEEP(*(.text.tsl9v4160.post_table_code_c2c0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c2c0)==72, "Storage size changed")
 .text.tsl9v4160.post_table_code_c308 0xc308 : { KEEP(*(.text.tsl9v4160.post_table_code_c308)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c308)==16, "Storage size changed")
 .text.tsl9v4160.post_table_code_c318 0xc318 : { KEEP(*(.text.tsl9v4160.post_table_code_c318)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c318)==66, "Storage size changed")
 .text.tsl9v4160.direct_closure_c35a 0xc35a : { KEEP(*(.text.tsl9v4160.direct_closure_c35a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_c35a)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_c364 0xc364 : { KEEP(*(.text.tsl9v4160.direct_followup_c364)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_c364)==72, "Storage size changed")
 .text.tsl9v4160.direct_frontier_c3ac 0xc3ac : { KEEP(*(.text.tsl9v4160.direct_frontier_c3ac)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_c3ac)==18, "Storage size changed")
 .text.tsl9v4160.direct_expansion_c3be 0xc3be : { KEEP(*(.text.tsl9v4160.direct_expansion_c3be)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_c3be)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_c3d4 0xc3d4 : { KEEP(*(.text.tsl9v4160.post_table_code_c3d4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c3d4)==142, "Storage size changed")
 .text.tsl9v4160.direct_frontier_c462 0xc462 : { KEEP(*(.text.tsl9v4160.direct_frontier_c462)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_c462)==16, "Storage size changed")
 .text.tsl9v4160.post_table_code_c472 0xc472 : { KEEP(*(.text.tsl9v4160.post_table_code_c472)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c472)==412, "Storage size changed")
 .text.tsl9v4160.post_table_code_c60e 0xc60e : { KEEP(*(.text.tsl9v4160.post_table_code_c60e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c60e)==108, "Storage size changed")
 .text.tsl9v4160.direct_expansion_c67a 0xc67a : { KEEP(*(.text.tsl9v4160.direct_expansion_c67a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_c67a)==46, "Storage size changed")
 .text.tsl9v4160.code_continuation_c6a8 0xc6a8 : { KEEP(*(.text.tsl9v4160.code_continuation_c6a8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_c6a8)==206, "Storage size changed")
 .text.tsl9v4160.direct_expansion_c776 0xc776 : { KEEP(*(.text.tsl9v4160.direct_expansion_c776)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_c776)==34, "Storage size changed")
 .text.tsl9v4160.direct_expansion_c798 0xc798 : { KEEP(*(.text.tsl9v4160.direct_expansion_c798)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_c798)==18, "Storage size changed")
 .text.tsl9v4160.direct_followup_c7aa 0xc7aa : { KEEP(*(.text.tsl9v4160.direct_followup_c7aa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_c7aa)==62, "Storage size changed")
 .text.tsl9v4160.direct_successors_c7e8 0xc7e8 : { KEEP(*(.text.tsl9v4160.direct_successors_c7e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_c7e8)==186, "Storage size changed")
 .text.tsl9v4160.post_table_code_c8a2 0xc8a2 : { KEEP(*(.text.tsl9v4160.post_table_code_c8a2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c8a2)==172, "Storage size changed")
 .text.tsl9v4160.post_table_code_c94e 0xc94e : { KEEP(*(.text.tsl9v4160.post_table_code_c94e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_c94e)==774, "Storage size changed")
 .text.tsl9v4160.direct_successors_cc54 0xcc54 : { KEEP(*(.text.tsl9v4160.direct_successors_cc54)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_cc54)==12, "Storage size changed")
 .text.tsl9v4160.direct_followup_cc60 0xcc60 : { KEEP(*(.text.tsl9v4160.direct_followup_cc60)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_cc60)==24, "Storage size changed")
 .text.tsl9v4160.direct_followup_cc78 0xcc78 : { KEEP(*(.text.tsl9v4160.direct_followup_cc78)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_cc78)==10, "Storage size changed")
 .text.tsl9v4160.direct_followup_cc82 0xcc82 : { KEEP(*(.text.tsl9v4160.direct_followup_cc82)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_cc82)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_cc8c 0xcc8c : { KEEP(*(.text.tsl9v4160.direct_frontier_cc8c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_cc8c)==54, "Storage size changed")
 .text.tsl9v4160.direct_followup_ccc2 0xccc2 : { KEEP(*(.text.tsl9v4160.direct_followup_ccc2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ccc2)==52, "Storage size changed")
 .text.tsl9v4160.direct_followup_ccf6 0xccf6 : { KEEP(*(.text.tsl9v4160.direct_followup_ccf6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ccf6)==78, "Storage size changed")
 .text.tsl9v4160.direct_closure_cd44 0xcd44 : { KEEP(*(.text.tsl9v4160.direct_closure_cd44)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_cd44)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_cd4e 0xcd4e : { KEEP(*(.text.tsl9v4160.post_table_code_cd4e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_cd4e)==10, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_cd58 0xcd58 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_cd58)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_cd58)==18, "Storage size changed")
 .text.tsl9v4160.direct_frontier_cd6a 0xcd6a : { KEEP(*(.text.tsl9v4160.direct_frontier_cd6a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_cd6a)==286, "Storage size changed")
 .text.tsl9v4160.direct_frontier_ce88 0xce88 : { KEEP(*(.text.tsl9v4160.direct_frontier_ce88)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_ce88)==34, "Storage size changed")
 .text.tsl9v4160.direct_expansion_ceaa 0xceaa : { KEEP(*(.text.tsl9v4160.direct_expansion_ceaa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_ceaa)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_cec0 0xcec0 : { KEEP(*(.text.tsl9v4160.post_table_code_cec0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_cec0)==28, "Storage size changed")
 .text.tsl9v4160.post_table_code_cedc 0xcedc : { KEEP(*(.text.tsl9v4160.post_table_code_cedc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_cedc)==186, "Storage size changed")
 .text.tsl9v4160.post_table_code_cf96 0xcf96 : { KEEP(*(.text.tsl9v4160.post_table_code_cf96)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_cf96)==178, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d048 0xd048 : { KEEP(*(.text.tsl9v4160.direct_frontier_d048)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d048)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_d052 0xd052 : { KEEP(*(.text.tsl9v4160.direct_successors_d052)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d052)==10, "Storage size changed")
 .text.tsl9v4160.direct_closure_d05c 0xd05c : { KEEP(*(.text.tsl9v4160.direct_closure_d05c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_d05c)==32, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d07c 0xd07c : { KEEP(*(.text.tsl9v4160.direct_frontier_d07c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d07c)==114, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d0ee 0xd0ee : { KEEP(*(.text.tsl9v4160.direct_expansion_d0ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d0ee)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_d104 0xd104 : { KEEP(*(.text.tsl9v4160.post_table_code_d104)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d104)==70, "Storage size changed")
 .text.tsl9v4160.post_table_code_d14a 0xd14a : { KEEP(*(.text.tsl9v4160.post_table_code_d14a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d14a)==70, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d190 0xd190 : { KEEP(*(.text.tsl9v4160.direct_frontier_d190)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d190)==6, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d196 0xd196 : { KEEP(*(.text.tsl9v4160.direct_expansion_d196)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d196)==18, "Storage size changed")
 .text.tsl9v4160.direct_closure_d1a8 0xd1a8 : { KEEP(*(.text.tsl9v4160.direct_closure_d1a8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_d1a8)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_d1b2 0xd1b2 : { KEEP(*(.text.tsl9v4160.post_table_code_d1b2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d1b2)==192, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d272 0xd272 : { KEEP(*(.text.tsl9v4160.direct_expansion_d272)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d272)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_d288 0xd288 : { KEEP(*(.text.tsl9v4160.post_table_code_d288)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d288)==102, "Storage size changed")
 .text.tsl9v4160.direct_successors_d2ee 0xd2ee : { KEEP(*(.text.tsl9v4160.direct_successors_d2ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d2ee)==38, "Storage size changed")
 .text.tsl9v4160.direct_closure_d314 0xd314 : { KEEP(*(.text.tsl9v4160.direct_closure_d314)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_d314)==14, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d322 0xd322 : { KEEP(*(.text.tsl9v4160.direct_frontier_d322)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d322)==16, "Storage size changed")
 .text.tsl9v4160.post_table_code_d332 0xd332 : { KEEP(*(.text.tsl9v4160.post_table_code_d332)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d332)==70, "Storage size changed")
 .text.tsl9v4160.post_table_code_d378 0xd378 : { KEEP(*(.text.tsl9v4160.post_table_code_d378)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d378)==78, "Storage size changed")
 .text.tsl9v4160.direct_successors_d3c6 0xd3c6 : { KEEP(*(.text.tsl9v4160.direct_successors_d3c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d3c6)==34, "Storage size changed")
 .text.tsl9v4160.direct_closure_d3e8 0xd3e8 : { KEEP(*(.text.tsl9v4160.direct_closure_d3e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_d3e8)==14, "Storage size changed")
 .text.tsl9v4160.post_table_code_d3f6 0xd3f6 : { KEEP(*(.text.tsl9v4160.post_table_code_d3f6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d3f6)==114, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d468 0xd468 : { KEEP(*(.text.tsl9v4160.direct_frontier_d468)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d468)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d472 0xd472 : { KEEP(*(.text.tsl9v4160.direct_frontier_d472)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d472)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_d47c 0xd47c : { KEEP(*(.text.tsl9v4160.post_table_code_d47c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d47c)==100, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d4e0 0xd4e0 : { KEEP(*(.text.tsl9v4160.direct_frontier_d4e0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d4e0)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d4ea 0xd4ea : { KEEP(*(.text.tsl9v4160.direct_frontier_d4ea)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d4ea)==10, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d4f4 0xd4f4 : { KEEP(*(.text.tsl9v4160.direct_expansion_d4f4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d4f4)==22, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_d50a 0xd50a : { KEEP(*(.text.tsl9v4160.materialized_callbacks_d50a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_d50a)==50, "Storage size changed")
 .text.tsl9v4160.direct_successors_d53c 0xd53c : { KEEP(*(.text.tsl9v4160.direct_successors_d53c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d53c)==60, "Storage size changed")
 .text.tsl9v4160.direct_successors_d578 0xd578 : { KEEP(*(.text.tsl9v4160.direct_successors_d578)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d578)==186, "Storage size changed")
 .text.tsl9v4160.post_table_code_d632 0xd632 : { KEEP(*(.text.tsl9v4160.post_table_code_d632)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d632)==24, "Storage size changed")
 .text.tsl9v4160.post_table_code_d64a 0xd64a : { KEEP(*(.text.tsl9v4160.post_table_code_d64a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d64a)==24, "Storage size changed")
 .text.tsl9v4160.direct_followup_d662 0xd662 : { KEEP(*(.text.tsl9v4160.direct_followup_d662)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_d662)==6, "Storage size changed")
 .text.tsl9v4160.direct_followup_d668 0xd668 : { KEEP(*(.text.tsl9v4160.direct_followup_d668)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_d668)==34, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d68a 0xd68a : { KEEP(*(.text.tsl9v4160.direct_expansion_d68a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d68a)==18, "Storage size changed")
 .text.tsl9v4160.post_table_code_d69c 0xd69c : { KEEP(*(.text.tsl9v4160.post_table_code_d69c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_d69c)==184, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d754 0xd754 : { KEEP(*(.text.tsl9v4160.direct_frontier_d754)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d754)==6, "Storage size changed")
 .text.tsl9v4160.direct_expansion_d75a 0xd75a : { KEEP(*(.text.tsl9v4160.direct_expansion_d75a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_d75a)==18, "Storage size changed")
 .text.tsl9v4160.direct_followup_d76c 0xd76c : { KEEP(*(.text.tsl9v4160.direct_followup_d76c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_d76c)==56, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_d7a4 0xd7a4 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_d7a4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_d7a4)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_d7b0 0xd7b0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_d7b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_d7b0)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_d7bc 0xd7bc : { KEEP(*(.text.tsl9v4160.materialized_callbacks_d7bc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_d7bc)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_d7c8 0xd7c8 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_d7c8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_d7c8)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_d7d4 0xd7d4 : { KEEP(*(.text.tsl9v4160.direct_frontier_d7d4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_d7d4)==60, "Storage size changed")
 .text.tsl9v4160.direct_followup_d810 0xd810 : { KEEP(*(.text.tsl9v4160.direct_followup_d810)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_d810)==88, "Storage size changed")
 .text.tsl9v4160.direct_successors_d868 0xd868 : { KEEP(*(.text.tsl9v4160.direct_successors_d868)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d868)==122, "Storage size changed")
 .text.tsl9v4160.direct_successors_d8e2 0xd8e2 : { KEEP(*(.text.tsl9v4160.direct_successors_d8e2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d8e2)==44, "Storage size changed")
 .text.tsl9v4160.direct_successors_d90e 0xd90e : { KEEP(*(.text.tsl9v4160.direct_successors_d90e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d90e)==72, "Storage size changed")
 .text.tsl9v4160.direct_successors_d956 0xd956 : { KEEP(*(.text.tsl9v4160.direct_successors_d956)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_d956)==224, "Storage size changed")
 .text.tsl9v4160.direct_followup_da36 0xda36 : { KEEP(*(.text.tsl9v4160.direct_followup_da36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_da36)==62, "Storage size changed")
 .text.tsl9v4160.post_table_code_da74 0xda74 : { KEEP(*(.text.tsl9v4160.post_table_code_da74)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_da74)==84, "Storage size changed")
 .text.tsl9v4160.post_table_code_dac8 0xdac8 : { KEEP(*(.text.tsl9v4160.post_table_code_dac8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_dac8)==260, "Storage size changed")
 .text.tsl9v4160.post_table_code_dbcc 0xdbcc : { KEEP(*(.text.tsl9v4160.post_table_code_dbcc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_dbcc)==52, "Storage size changed")
 .text.tsl9v4160.post_table_code_dc00 0xdc00 : { KEEP(*(.text.tsl9v4160.post_table_code_dc00)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_dc00)==34, "Storage size changed")
 .text.tsl9v4160.post_table_code_dc22 0xdc22 : { KEEP(*(.text.tsl9v4160.post_table_code_dc22)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_dc22)==20, "Storage size changed")
 .text.tsl9v4160.post_table_code_dc36 0xdc36 : { KEEP(*(.text.tsl9v4160.post_table_code_dc36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_dc36)==586, "Storage size changed")
 .text.tsl9v4160.post_table_code_de80 0xde80 : { KEEP(*(.text.tsl9v4160.post_table_code_de80)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_de80)==2, "Storage size changed")
 .text.tsl9v4160.direct_successors_de82 0xde82 : { KEEP(*(.text.tsl9v4160.direct_successors_de82)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_de82)==30, "Storage size changed")
 .text.tsl9v4160.direct_followup_dea0 0xdea0 : { KEEP(*(.text.tsl9v4160.direct_followup_dea0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_dea0)==66, "Storage size changed")
 .text.tsl9v4160.direct_frontier_dee2 0xdee2 : { KEEP(*(.text.tsl9v4160.direct_frontier_dee2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_dee2)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_deec 0xdeec : { KEEP(*(.text.tsl9v4160.direct_successors_deec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_deec)==6, "Storage size changed")
 .text.tsl9v4160.post_table_code_def2 0xdef2 : { KEEP(*(.text.tsl9v4160.post_table_code_def2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_def2)==326, "Storage size changed")
 .text.tsl9v4160.direct_frontier_e038 0xe038 : { KEEP(*(.text.tsl9v4160.direct_frontier_e038)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_e038)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_e042 0xe042 : { KEEP(*(.text.tsl9v4160.direct_frontier_e042)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_e042)==6, "Storage size changed")
 .text.tsl9v4160.direct_frontier_e048 0xe048 : { KEEP(*(.text.tsl9v4160.direct_frontier_e048)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_e048)==16, "Storage size changed")
 .text.tsl9v4160.direct_frontier_e058 0xe058 : { KEEP(*(.text.tsl9v4160.direct_frontier_e058)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_e058)==76, "Storage size changed")
 .text.tsl9v4160.direct_expansion_e0a4 0xe0a4 : { KEEP(*(.text.tsl9v4160.direct_expansion_e0a4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_e0a4)==22, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_e0ba 0xe0ba : { KEEP(*(.text.tsl9v4160.materialized_callbacks_e0ba)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_e0ba)==236, "Storage size changed")
 .text.tsl9v4160.direct_frontier_e1a6 0xe1a6 : { KEEP(*(.text.tsl9v4160.direct_frontier_e1a6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_e1a6)==102, "Storage size changed")
 .text.tsl9v4160.direct_successors_e20c 0xe20c : { KEEP(*(.text.tsl9v4160.direct_successors_e20c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_e20c)==20, "Storage size changed")
 .text.tsl9v4160.direct_successors_e220 0xe220 : { KEEP(*(.text.tsl9v4160.direct_successors_e220)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_e220)==38, "Storage size changed")
 .text.tsl9v4160.direct_successors_e246 0xe246 : { KEEP(*(.text.tsl9v4160.direct_successors_e246)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_e246)==2404, "Storage size changed")
 .text.tsl9v4160.direct_successors_ebaa 0xebaa : { KEEP(*(.text.tsl9v4160.direct_successors_ebaa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ebaa)==2, "Storage size changed")
 .text.tsl9v4160.direct_successors_ebac 0xebac : { KEEP(*(.text.tsl9v4160.direct_successors_ebac)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ebac)==252, "Storage size changed")
 .text.tsl9v4160.post_table_code_eca8 0xeca8 : { KEEP(*(.text.tsl9v4160.post_table_code_eca8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_eca8)==88, "Storage size changed")
 .text.tsl9v4160.direct_successors_ed00 0xed00 : { KEEP(*(.text.tsl9v4160.direct_successors_ed00)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ed00)==54, "Storage size changed")
 .text.tsl9v4160.direct_successors_ed36 0xed36 : { KEEP(*(.text.tsl9v4160.direct_successors_ed36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ed36)==112, "Storage size changed")
 .text.tsl9v4160.direct_successors_eda6 0xeda6 : { KEEP(*(.text.tsl9v4160.direct_successors_eda6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_eda6)==76, "Storage size changed")
 .text.tsl9v4160.direct_frontier_edf2 0xedf2 : { KEEP(*(.text.tsl9v4160.direct_frontier_edf2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_edf2)==62, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_ee30 0xee30 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_ee30)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_ee30)==106, "Storage size changed")
 .text.tsl9v4160.direct_followup_ee9a 0xee9a : { KEEP(*(.text.tsl9v4160.direct_followup_ee9a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_ee9a)==70, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_eee0 0xeee0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_eee0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_eee0)==140, "Storage size changed")
 .text.tsl9v4160.direct_successors_ef6c 0xef6c : { KEEP(*(.text.tsl9v4160.direct_successors_ef6c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_ef6c)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_ef76 0xef76 : { KEEP(*(.text.tsl9v4160.direct_frontier_ef76)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_ef76)==160, "Storage size changed")
 .text.tsl9v4160.direct_successors_f016 0xf016 : { KEEP(*(.text.tsl9v4160.direct_successors_f016)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_f016)==66, "Storage size changed")
 .text.tsl9v4160.direct_followup_f058 0xf058 : { KEEP(*(.text.tsl9v4160.direct_followup_f058)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_f058)==88, "Storage size changed")
 .text.tsl9v4160.direct_expansion_f0b0 0xf0b0 : { KEEP(*(.text.tsl9v4160.direct_expansion_f0b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_f0b0)==22, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f0c6 0xf0c6 : { KEEP(*(.text.tsl9v4160.direct_frontier_f0c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f0c6)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_f0d0 0xf0d0 : { KEEP(*(.text.tsl9v4160.post_table_code_f0d0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_f0d0)==122, "Storage size changed")
 .text.tsl9v4160.post_table_code_f14a 0xf14a : { KEEP(*(.text.tsl9v4160.post_table_code_f14a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_f14a)==120, "Storage size changed")
 .text.tsl9v4160.post_table_code_f1c2 0xf1c2 : { KEEP(*(.text.tsl9v4160.post_table_code_f1c2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_f1c2)==594, "Storage size changed")
 .text.tsl9v4160.direct_successors_f414 0xf414 : { KEEP(*(.text.tsl9v4160.direct_successors_f414)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_f414)==84, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_f468 0xf468 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_f468)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_f468)==22, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f47e 0xf47e : { KEEP(*(.text.tsl9v4160.direct_frontier_f47e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f47e)==82, "Storage size changed")
 .text.tsl9v4160.callback_bodies_f4d0 0xf4d0 : { KEEP(*(.text.tsl9v4160.callback_bodies_f4d0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_bodies_f4d0)==168, "Storage size changed")
 .text.tsl9v4160.callback_bodies_f578 0xf578 : { KEEP(*(.text.tsl9v4160.callback_bodies_f578)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_bodies_f578)==184, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f630 0xf630 : { KEEP(*(.text.tsl9v4160.direct_frontier_f630)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f630)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f63c 0xf63c : { KEEP(*(.text.tsl9v4160.direct_frontier_f63c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f63c)==32, "Storage size changed")
 .text.tsl9v4160.direct_successors_f65c 0xf65c : { KEEP(*(.text.tsl9v4160.direct_successors_f65c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_f65c)==10, "Storage size changed")
 .text.tsl9v4160.residual_code_f666 0xf666 : { KEEP(*(.text.tsl9v4160.residual_code_f666)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_code_f666)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f672 0xf672 : { KEEP(*(.text.tsl9v4160.direct_frontier_f672)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f672)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f67e 0xf67e : { KEEP(*(.text.tsl9v4160.direct_frontier_f67e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f67e)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f688 0xf688 : { KEEP(*(.text.tsl9v4160.direct_frontier_f688)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f688)==40, "Storage size changed")
 .text.tsl9v4160.direct_closure_f6b0 0xf6b0 : { KEEP(*(.text.tsl9v4160.direct_closure_f6b0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_f6b0)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f6ba 0xf6ba : { KEEP(*(.text.tsl9v4160.direct_frontier_f6ba)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f6ba)==40, "Storage size changed")
 .text.tsl9v4160.direct_closure_f6e2 0xf6e2 : { KEEP(*(.text.tsl9v4160.direct_closure_f6e2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_f6e2)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f6ec 0xf6ec : { KEEP(*(.text.tsl9v4160.direct_frontier_f6ec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f6ec)==40, "Storage size changed")
 .text.tsl9v4160.direct_closure_f714 0xf714 : { KEEP(*(.text.tsl9v4160.direct_closure_f714)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_f714)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f71e 0xf71e : { KEEP(*(.text.tsl9v4160.direct_frontier_f71e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f71e)==40, "Storage size changed")
 .text.tsl9v4160.direct_closure_f746 0xf746 : { KEEP(*(.text.tsl9v4160.direct_closure_f746)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_f746)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f750 0xf750 : { KEEP(*(.text.tsl9v4160.direct_frontier_f750)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f750)==60, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f78c 0xf78c : { KEEP(*(.text.tsl9v4160.direct_frontier_f78c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f78c)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f796 0xf796 : { KEEP(*(.text.tsl9v4160.direct_frontier_f796)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f796)==60, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f7d2 0xf7d2 : { KEEP(*(.text.tsl9v4160.direct_frontier_f7d2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f7d2)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f7dc 0xf7dc : { KEEP(*(.text.tsl9v4160.direct_frontier_f7dc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f7dc)==16, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f7ec 0xf7ec : { KEEP(*(.text.tsl9v4160.direct_frontier_f7ec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f7ec)==20, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f800 0xf800 : { KEEP(*(.text.tsl9v4160.direct_frontier_f800)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f800)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f80a 0xf80a : { KEEP(*(.text.tsl9v4160.direct_frontier_f80a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f80a)==14, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f818 0xf818 : { KEEP(*(.text.tsl9v4160.direct_frontier_f818)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f818)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f822 0xf822 : { KEEP(*(.text.tsl9v4160.direct_frontier_f822)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f822)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f82c 0xf82c : { KEEP(*(.text.tsl9v4160.direct_frontier_f82c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f82c)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_f838 0xf838 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_f838)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_f838)==18, "Storage size changed")
 .text.tsl9v4160.direct_expansion_f84a 0xf84a : { KEEP(*(.text.tsl9v4160.direct_expansion_f84a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_f84a)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_f860 0xf860 : { KEEP(*(.text.tsl9v4160.post_table_code_f860)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_f860)==284, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f97c 0xf97c : { KEEP(*(.text.tsl9v4160.direct_frontier_f97c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f97c)==22, "Storage size changed")
 .text.tsl9v4160.direct_closure_f992 0xf992 : { KEEP(*(.text.tsl9v4160.direct_closure_f992)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_f992)==6, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f998 0xf998 : { KEEP(*(.text.tsl9v4160.direct_frontier_f998)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f998)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_f9a4 0xf9a4 : { KEEP(*(.text.tsl9v4160.direct_frontier_f9a4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_f9a4)==72, "Storage size changed")
 .text.tsl9v4160.direct_successors_f9ec 0xf9ec : { KEEP(*(.text.tsl9v4160.direct_successors_f9ec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_f9ec)==56, "Storage size changed")
 .text.tsl9v4160.direct_frontier_fa24 0xfa24 : { KEEP(*(.text.tsl9v4160.direct_frontier_fa24)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_fa24)==6, "Storage size changed")
 .text.tsl9v4160.direct_closure_fa2a 0xfa2a : { KEEP(*(.text.tsl9v4160.direct_closure_fa2a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_fa2a)==6, "Storage size changed")
 .text.tsl9v4160.direct_frontier_fa30 0xfa30 : { KEEP(*(.text.tsl9v4160.direct_frontier_fa30)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_fa30)==6, "Storage size changed")
 .text.tsl9v4160.direct_closure_fa36 0xfa36 : { KEEP(*(.text.tsl9v4160.direct_closure_fa36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_fa36)==6, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fa3c 0xfa3c : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fa3c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fa3c)==14, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fa4a 0xfa4a : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fa4a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fa4a)==6, "Storage size changed")
 .text.tsl9v4160.direct_expansion_fa50 0xfa50 : { KEEP(*(.text.tsl9v4160.direct_expansion_fa50)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_fa50)==18, "Storage size changed")
 .text.tsl9v4160.post_table_code_fa62 0xfa62 : { KEEP(*(.text.tsl9v4160.post_table_code_fa62)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_fa62)==26, "Storage size changed")
 .text.tsl9v4160.post_table_code_fa7c 0xfa7c : { KEEP(*(.text.tsl9v4160.post_table_code_fa7c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_fa7c)==106, "Storage size changed")
 .text.tsl9v4160.direct_frontier_fae6 0xfae6 : { KEEP(*(.text.tsl9v4160.direct_frontier_fae6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_fae6)==12, "Storage size changed")
 .text.tsl9v4160.direct_frontier_faf2 0xfaf2 : { KEEP(*(.text.tsl9v4160.direct_frontier_faf2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_faf2)==6, "Storage size changed")
 .text.tsl9v4160.direct_followup_faf8 0xfaf8 : { KEEP(*(.text.tsl9v4160.direct_followup_faf8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_faf8)==6, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fafe 0xfafe : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fafe)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fafe)==14, "Storage size changed")
 .text.tsl9v4160.direct_expansion_fb0c 0xfb0c : { KEEP(*(.text.tsl9v4160.direct_expansion_fb0c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_fb0c)==18, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fb1e 0xfb1e : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fb1e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fb1e)==64, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fb5e 0xfb5e : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fb5e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fb5e)==68, "Storage size changed")
 .text.tsl9v4160.post_table_code_fba2 0xfba2 : { KEEP(*(.text.tsl9v4160.post_table_code_fba2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_fba2)==412, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_fd3e 0xfd3e : { KEEP(*(.text.tsl9v4160.materialized_callbacks_fd3e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_fd3e)==32, "Storage size changed")
 .text.tsl9v4160.direct_successors_fd5e 0xfd5e : { KEEP(*(.text.tsl9v4160.direct_successors_fd5e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_fd5e)==6, "Storage size changed")
 .text.tsl9v4160.direct_successors_fd64 0xfd64 : { KEEP(*(.text.tsl9v4160.direct_successors_fd64)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_fd64)==6, "Storage size changed")
 .text.tsl9v4160.post_table_code_fd6a 0xfd6a : { KEEP(*(.text.tsl9v4160.post_table_code_fd6a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_fd6a)==54, "Storage size changed")
 .text.tsl9v4160.direct_followup_fda0 0xfda0 : { KEEP(*(.text.tsl9v4160.direct_followup_fda0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_fda0)==6, "Storage size changed")
 .text.tsl9v4160.direct_followup_fda6 0xfda6 : { KEEP(*(.text.tsl9v4160.direct_followup_fda6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_fda6)==80, "Storage size changed")
 .text.tsl9v4160.direct_frontier_fdf6 0xfdf6 : { KEEP(*(.text.tsl9v4160.direct_frontier_fdf6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_fdf6)==18, "Storage size changed")
 .text.tsl9v4160.direct_followup_fe08 0xfe08 : { KEEP(*(.text.tsl9v4160.direct_followup_fe08)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_fe08)==20, "Storage size changed")
 .text.tsl9v4160.direct_followup_fe1c 0xfe1c : { KEEP(*(.text.tsl9v4160.direct_followup_fe1c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_fe1c)==78, "Storage size changed")
 .text.tsl9v4160.direct_successors_fe6a 0xfe6a : { KEEP(*(.text.tsl9v4160.direct_successors_fe6a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_fe6a)==218, "Storage size changed")
 .text.tsl9v4160.direct_expansion_ff44 0xff44 : { KEEP(*(.text.tsl9v4160.direct_expansion_ff44)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_ff44)==18, "Storage size changed")
 .text.tsl9v4160.post_table_code_ff56 0xff56 : { KEEP(*(.text.tsl9v4160.post_table_code_ff56)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_ff56)==78, "Storage size changed")
 .text.tsl9v4160.post_table_code_ffa4 0xffa4 : { KEEP(*(.text.tsl9v4160.post_table_code_ffa4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_ffa4)==126, "Storage size changed")
 .text.tsl9v4160.direct_frontier_10022 0x10022 : { KEEP(*(.text.tsl9v4160.direct_frontier_10022)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_10022)==16, "Storage size changed")
 .text.tsl9v4160.direct_expansion_10032 0x10032 : { KEEP(*(.text.tsl9v4160.direct_expansion_10032)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_10032)==18, "Storage size changed")
 .text.tsl9v4160.post_table_code_10044 0x10044 : { KEEP(*(.text.tsl9v4160.post_table_code_10044)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10044)==70, "Storage size changed")
 .text.tsl9v4160.direct_frontier_1008a 0x1008a : { KEEP(*(.text.tsl9v4160.direct_frontier_1008a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_1008a)==12, "Storage size changed")
 .text.tsl9v4160.post_table_code_10096 0x10096 : { KEEP(*(.text.tsl9v4160.post_table_code_10096)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10096)==50, "Storage size changed")
 .text.tsl9v4160.direct_frontier_100c8 0x100c8 : { KEEP(*(.text.tsl9v4160.direct_frontier_100c8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_100c8)==14, "Storage size changed")
 .text.tsl9v4160.post_table_code_100d6 0x100d6 : { KEEP(*(.text.tsl9v4160.post_table_code_100d6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_100d6)==32, "Storage size changed")
 .text.tsl9v4160.direct_frontier_100f6 0x100f6 : { KEEP(*(.text.tsl9v4160.direct_frontier_100f6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_100f6)==10, "Storage size changed")
 .text.tsl9v4160.post_table_code_10100 0x10100 : { KEEP(*(.text.tsl9v4160.post_table_code_10100)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10100)==48, "Storage size changed")
 .text.tsl9v4160.direct_frontier_10130 0x10130 : { KEEP(*(.text.tsl9v4160.direct_frontier_10130)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_10130)==40, "Storage size changed")
 .text.tsl9v4160.direct_expansion_10158 0x10158 : { KEEP(*(.text.tsl9v4160.direct_expansion_10158)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_10158)==22, "Storage size changed")
 .text.tsl9v4160.direct_frontier_1016e 0x1016e : { KEEP(*(.text.tsl9v4160.direct_frontier_1016e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_1016e)==112, "Storage size changed")
 .text.tsl9v4160.direct_followup_101de 0x101de : { KEEP(*(.text.tsl9v4160.direct_followup_101de)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_101de)==152, "Storage size changed")
 .text.tsl9v4160.direct_expansion_10276 0x10276 : { KEEP(*(.text.tsl9v4160.direct_expansion_10276)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_10276)==18, "Storage size changed")
 .text.tsl9v4160.post_table_code_10288 0x10288 : { KEEP(*(.text.tsl9v4160.post_table_code_10288)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10288)==378, "Storage size changed")
 .text.tsl9v4160.direct_successors_10402 0x10402 : { KEEP(*(.text.tsl9v4160.direct_successors_10402)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_10402)==6, "Storage size changed")
 .text.tsl9v4160.direct_frontier_10408 0x10408 : { KEEP(*(.text.tsl9v4160.direct_frontier_10408)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_10408)==6, "Storage size changed")
 .text.tsl9v4160.direct_successors_1040e 0x1040e : { KEEP(*(.text.tsl9v4160.direct_successors_1040e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_1040e)==50, "Storage size changed")
 .text.tsl9v4160.post_table_code_10440 0x10440 : { KEEP(*(.text.tsl9v4160.post_table_code_10440)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10440)==278, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_10556 0x10556 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_10556)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_10556)==24, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_1056e 0x1056e : { KEEP(*(.text.tsl9v4160.materialized_callbacks_1056e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_1056e)==46, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_1059c 0x1059c : { KEEP(*(.text.tsl9v4160.materialized_callbacks_1059c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_1059c)==40, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_105c4 0x105c4 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_105c4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_105c4)==12, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_105d0 0x105d0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_105d0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_105d0)==28, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_105ec 0x105ec : { KEEP(*(.text.tsl9v4160.materialized_callbacks_105ec)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_105ec)==48, "Storage size changed")
 .text.tsl9v4160.code_continuation_1061c 0x1061c : { KEEP(*(.text.tsl9v4160.code_continuation_1061c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_1061c)==20, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_10630 0x10630 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_10630)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_10630)==110, "Storage size changed")
 .text.tsl9v4160.post_table_code_1069e 0x1069e : { KEEP(*(.text.tsl9v4160.post_table_code_1069e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_1069e)==34, "Storage size changed")
 .text.tsl9v4160.direct_successors_106c0 0x106c0 : { KEEP(*(.text.tsl9v4160.direct_successors_106c0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_106c0)==32, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_106e0 0x106e0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_106e0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_106e0)==8, "Storage size changed")
 .text.tsl9v4160.post_table_code_106e8 0x106e8 : { KEEP(*(.text.tsl9v4160.post_table_code_106e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_106e8)==34, "Storage size changed")
 .text.tsl9v4160.code_continuation_1070a 0x1070a : { KEEP(*(.text.tsl9v4160.code_continuation_1070a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_1070a)==66, "Storage size changed")
 .text.tsl9v4160.code_continuation_1074c 0x1074c : { KEEP(*(.text.tsl9v4160.code_continuation_1074c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_1074c)==116, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_107c0 0x107c0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_107c0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_107c0)==6, "Storage size changed")
 .text.tsl9v4160.direct_successors_107c6 0x107c6 : { KEEP(*(.text.tsl9v4160.direct_successors_107c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_107c6)==80, "Storage size changed")
 .text.tsl9v4160.code_continuation_10816 0x10816 : { KEEP(*(.text.tsl9v4160.code_continuation_10816)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_10816)==38, "Storage size changed")
 .text.tsl9v4160.post_table_code_1083c 0x1083c : { KEEP(*(.text.tsl9v4160.post_table_code_1083c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_1083c)==52, "Storage size changed")
 .text.tsl9v4160.post_table_code_10870 0x10870 : { KEEP(*(.text.tsl9v4160.post_table_code_10870)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10870)==104, "Storage size changed")
 .text.tsl9v4160.post_table_code_108d8 0x108d8 : { KEEP(*(.text.tsl9v4160.post_table_code_108d8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_108d8)==94, "Storage size changed")
 .text.tsl9v4160.post_table_code_10936 0x10936 : { KEEP(*(.text.tsl9v4160.post_table_code_10936)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10936)==14, "Storage size changed")
 .text.tsl9v4160.post_table_code_10944 0x10944 : { KEEP(*(.text.tsl9v4160.post_table_code_10944)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10944)==128, "Storage size changed")
 .text.tsl9v4160.post_table_code_109c4 0x109c4 : { KEEP(*(.text.tsl9v4160.post_table_code_109c4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_109c4)==60, "Storage size changed")
 .text.tsl9v4160.post_table_code_10a00 0x10a00 : { KEEP(*(.text.tsl9v4160.post_table_code_10a00)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10a00)==22, "Storage size changed")
 .text.tsl9v4160.post_table_code_10a16 0x10a16 : { KEEP(*(.text.tsl9v4160.post_table_code_10a16)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10a16)==176, "Storage size changed")
 .text.tsl9v4160.post_table_code_10ac6 0x10ac6 : { KEEP(*(.text.tsl9v4160.post_table_code_10ac6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10ac6)==68, "Storage size changed")
 .text.tsl9v4160.post_table_code_10b0a 0x10b0a : { KEEP(*(.text.tsl9v4160.post_table_code_10b0a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10b0a)==86, "Storage size changed")
 .text.tsl9v4160.post_table_code_10b60 0x10b60 : { KEEP(*(.text.tsl9v4160.post_table_code_10b60)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_10b60)==190, "Storage size changed")
 .text.tsl9v4160.direct_expansion_10c1e 0x10c1e : { KEEP(*(.text.tsl9v4160.direct_expansion_10c1e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_10c1e)==22, "Storage size changed")
 .text.tsl9v4160.residual_entry_10c34 0x10c34 : { KEEP(*(.text.tsl9v4160.residual_entry_10c34)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_entry_10c34)==2, "Storage size changed")
 .text.tsl9v4160.residual_entry_10c36 0x10c36 : { KEEP(*(.text.tsl9v4160.residual_entry_10c36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_entry_10c36)==68, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_10c7a 0x10c7a : { KEEP(*(.text.tsl9v4160.conditional_runtime_10c7a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_10c7a)==102, "Storage size changed")
 .text.tsl9v4160.reachable_code_10ce0 0x10ce0 : { KEEP(*(.text.tsl9v4160.reachable_code_10ce0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.reachable_code_10ce0)==78, "Storage size changed")
 .text.tsl9v4160.residual_entry_10d2e 0x10d2e : { KEEP(*(.text.tsl9v4160.residual_entry_10d2e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_entry_10d2e)==2, "Storage size changed")
 .text.tsl9v4160.residual_entry_10d30 0x10d30 : { KEEP(*(.text.tsl9v4160.residual_entry_10d30)) }
 ASSERT(SIZEOF(.text.tsl9v4160.residual_entry_10d30)==48, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_10d60 0x10d60 : { KEEP(*(.text.tsl9v4160.conditional_runtime_10d60)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_10d60)==920, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_110f8 0x110f8 : { KEEP(*(.text.tsl9v4160.gatt_ingress_110f8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_110f8)==366, "Storage size changed")
 .text.tsl9v4160.reachable_code_11266 0x11266 : { KEEP(*(.text.tsl9v4160.reachable_code_11266)) }
 ASSERT(SIZEOF(.text.tsl9v4160.reachable_code_11266)==240, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_11356 0x11356 : { KEEP(*(.text.tsl9v4160.conditional_runtime_11356)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_11356)==396, "Storage size changed")
 .text.tsl9v4160.reachable_code_114e2 0x114e2 : { KEEP(*(.text.tsl9v4160.reachable_code_114e2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.reachable_code_114e2)==98, "Storage size changed")
 .text.tsl9v4160.reachable_code_11544 0x11544 : { KEEP(*(.text.tsl9v4160.reachable_code_11544)) }
 ASSERT(SIZEOF(.text.tsl9v4160.reachable_code_11544)==1156, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_119c8 0x119c8 : { KEEP(*(.text.tsl9v4160.conditional_runtime_119c8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_119c8)==2878, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12506 0x12506 : { KEEP(*(.text.tsl9v4160.direct_expansion_12506)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12506)==328, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_1264e 0x1264e : { KEEP(*(.text.tsl9v4160.gatt_ingress_1264e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_1264e)==688, "Storage size changed")
 .text.tsl9v4160.code_continuation_128fe 0x128fe : { KEEP(*(.text.tsl9v4160.code_continuation_128fe)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_128fe)==160, "Storage size changed")
 .text.tsl9v4160.post_table_code_1299e 0x1299e : { KEEP(*(.text.tsl9v4160.post_table_code_1299e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_1299e)==38, "Storage size changed")
 .text.tsl9v4160.code_continuation_129c4 0x129c4 : { KEEP(*(.text.tsl9v4160.code_continuation_129c4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_129c4)==68, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12a08 0x12a08 : { KEEP(*(.text.tsl9v4160.direct_expansion_12a08)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12a08)==102, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_12a6e 0x12a6e : { KEEP(*(.text.tsl9v4160.gatt_ingress_12a6e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_12a6e)==50, "Storage size changed")
 .text.tsl9v4160.code_continuation_12aa0 0x12aa0 : { KEEP(*(.text.tsl9v4160.code_continuation_12aa0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_12aa0)==30, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12abe 0x12abe : { KEEP(*(.text.tsl9v4160.direct_expansion_12abe)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12abe)==18, "Storage size changed")
 .text.tsl9v4160.direct_successors_12ad0 0x12ad0 : { KEEP(*(.text.tsl9v4160.direct_successors_12ad0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_12ad0)==84, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12b24 0x12b24 : { KEEP(*(.text.tsl9v4160.direct_expansion_12b24)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12b24)==52, "Storage size changed")
 .text.tsl9v4160.table_cases_12b58 0x12b58 : { KEEP(*(.text.tsl9v4160.table_cases_12b58)) }
 ASSERT(SIZEOF(.text.tsl9v4160.table_cases_12b58)==34, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12b7a 0x12b7a : { KEEP(*(.text.tsl9v4160.direct_expansion_12b7a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12b7a)==8, "Storage size changed")
 .text.tsl9v4160.table_cases_12b82 0x12b82 : { KEEP(*(.text.tsl9v4160.table_cases_12b82)) }
 ASSERT(SIZEOF(.text.tsl9v4160.table_cases_12b82)==70, "Storage size changed")
 .text.tsl9v4160.callee_12bc8 0x12bc8 : { KEEP(*(.text.tsl9v4160.callee_12bc8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_12bc8)==92, "Storage size changed")
 .text.tsl9v4160.handler_12c24 0x12c24 : { KEEP(*(.text.tsl9v4160.handler_12c24)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_12c24)==52, "Storage size changed")
 .text.tsl9v4160.init_12c58 0x12c58 : { KEEP(*(.text.tsl9v4160.init_12c58)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_12c58)==314, "Storage size changed")
 .text.tsl9v4160.init_12d92 0x12d92 : { KEEP(*(.text.tsl9v4160.init_12d92)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_12d92)==194, "Storage size changed")
 .text.tsl9v4160.code_continuation_12e54 0x12e54 : { KEEP(*(.text.tsl9v4160.code_continuation_12e54)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_12e54)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12e86 0x12e86 : { KEEP(*(.text.tsl9v4160.direct_expansion_12e86)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12e86)==96, "Storage size changed")
 .text.tsl9v4160.code_continuation_12ee6 0x12ee6 : { KEEP(*(.text.tsl9v4160.code_continuation_12ee6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_12ee6)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12f18 0x12f18 : { KEEP(*(.text.tsl9v4160.direct_expansion_12f18)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12f18)==48, "Storage size changed")
 .text.tsl9v4160.code_continuation_12f48 0x12f48 : { KEEP(*(.text.tsl9v4160.code_continuation_12f48)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_12f48)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_12f7a 0x12f7a : { KEEP(*(.text.tsl9v4160.direct_expansion_12f7a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_12f7a)==216, "Storage size changed")
 .text.tsl9v4160.code_continuation_13052 0x13052 : { KEEP(*(.text.tsl9v4160.code_continuation_13052)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_13052)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_13084 0x13084 : { KEEP(*(.text.tsl9v4160.direct_expansion_13084)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_13084)==82, "Storage size changed")
 .text.tsl9v4160.code_continuation_130d6 0x130d6 : { KEEP(*(.text.tsl9v4160.code_continuation_130d6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_130d6)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_13108 0x13108 : { KEEP(*(.text.tsl9v4160.direct_expansion_13108)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_13108)==48, "Storage size changed")
 .text.tsl9v4160.code_continuation_13138 0x13138 : { KEEP(*(.text.tsl9v4160.code_continuation_13138)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_13138)==50, "Storage size changed")
 .text.tsl9v4160.direct_expansion_1316a 0x1316a : { KEEP(*(.text.tsl9v4160.direct_expansion_1316a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_1316a)==88, "Storage size changed")
 .text.tsl9v4160.init_131c2 0x131c2 : { KEEP(*(.text.tsl9v4160.init_131c2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_131c2)==328, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_1330a 0x1330a : { KEEP(*(.text.tsl9v4160.gatt_ingress_1330a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_1330a)==50, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_1333c 0x1333c : { KEEP(*(.text.tsl9v4160.materialized_callbacks_1333c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_1333c)==10, "Storage size changed")
 .text.tsl9v4160.code_continuation_13346 0x13346 : { KEEP(*(.text.tsl9v4160.code_continuation_13346)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_13346)==672, "Storage size changed")
 .text.tsl9v4160.code_continuation_135e6 0x135e6 : { KEEP(*(.text.tsl9v4160.code_continuation_135e6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_135e6)==122, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_13660 0x13660 : { KEEP(*(.text.tsl9v4160.gatt_ingress_13660)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_13660)==352, "Storage size changed")
 .text.tsl9v4160.direct_followup_137c0 0x137c0 : { KEEP(*(.text.tsl9v4160.direct_followup_137c0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_137c0)==908, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_13b4c 0x13b4c : { KEEP(*(.text.tsl9v4160.conditional_runtime_13b4c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_13b4c)==90, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_13ba6 0x13ba6 : { KEEP(*(.text.tsl9v4160.gatt_ingress_13ba6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_13ba6)==44, "Storage size changed")
 .text.tsl9v4160.post_table_code_13bd2 0x13bd2 : { KEEP(*(.text.tsl9v4160.post_table_code_13bd2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_13bd2)==124, "Storage size changed")
 .text.tsl9v4160.direct_successors_13c4e 0x13c4e : { KEEP(*(.text.tsl9v4160.direct_successors_13c4e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_13c4e)==142, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_13cdc 0x13cdc : { KEEP(*(.text.tsl9v4160.conditional_runtime_13cdc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_13cdc)==108, "Storage size changed")
 .text.tsl9v4160.direct_expansion_13d48 0x13d48 : { KEEP(*(.text.tsl9v4160.direct_expansion_13d48)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_13d48)==140, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_13dd4 0x13dd4 : { KEEP(*(.text.tsl9v4160.gatt_ingress_13dd4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_13dd4)==196, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_13e98 0x13e98 : { KEEP(*(.text.tsl9v4160.conditional_runtime_13e98)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_13e98)==158, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_13f36 0x13f36 : { KEEP(*(.text.tsl9v4160.gatt_ingress_13f36)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_13f36)==48, "Storage size changed")
 .text.tsl9v4160.ota_handler_13f66 0x13f66 : { KEEP(*(.text.tsl9v4160.ota_handler_13f66)) }
 ASSERT(SIZEOF(.text.tsl9v4160.ota_handler_13f66)==24, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_13f7e 0x13f7e : { KEEP(*(.text.tsl9v4160.gatt_ingress_13f7e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_13f7e)==3340, "Storage size changed")
 .text.tsl9v4160.init_14c8a 0x14c8a : { KEEP(*(.text.tsl9v4160.init_14c8a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_14c8a)==62, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_14cc8 0x14cc8 : { KEEP(*(.text.tsl9v4160.gatt_ingress_14cc8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_14cc8)==102, "Storage size changed")
 .text.tsl9v4160.direct_expansion_14d2e 0x14d2e : { KEEP(*(.text.tsl9v4160.direct_expansion_14d2e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_14d2e)==36, "Storage size changed")
 .text.tsl9v4160.table_cases_14d52 0x14d52 : { KEEP(*(.text.tsl9v4160.table_cases_14d52)) }
 ASSERT(SIZEOF(.text.tsl9v4160.table_cases_14d52)==1864, "Storage size changed")
 .text.tsl9v4160.direct_expansion_1549a 0x1549a : { KEEP(*(.text.tsl9v4160.direct_expansion_1549a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_1549a)==12, "Storage size changed")
 .text.tsl9v4160.init_154a6 0x154a6 : { KEEP(*(.text.tsl9v4160.init_154a6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_154a6)==132, "Storage size changed")
 .text.tsl9v4160.direct_frontier_1552a 0x1552a : { KEEP(*(.text.tsl9v4160.direct_frontier_1552a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_1552a)==8, "Storage size changed")
 .text.tsl9v4160.direct_frontier_15532 0x15532 : { KEEP(*(.text.tsl9v4160.direct_frontier_15532)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_15532)==82, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_15584 0x15584 : { KEEP(*(.text.tsl9v4160.gatt_ingress_15584)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_15584)==76, "Storage size changed")
 .text.tsl9v4160.direct_followup_155d0 0x155d0 : { KEEP(*(.text.tsl9v4160.direct_followup_155d0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_155d0)==128, "Storage size changed")
 .text.tsl9v4160.direct_followup_15650 0x15650 : { KEEP(*(.text.tsl9v4160.direct_followup_15650)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_15650)==316, "Storage size changed")
 .text.tsl9v4160.direct_followup_1578c 0x1578c : { KEEP(*(.text.tsl9v4160.direct_followup_1578c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_1578c)==12, "Storage size changed")
 .text.tsl9v4160.direct_followup_15798 0x15798 : { KEEP(*(.text.tsl9v4160.direct_followup_15798)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_15798)==3092, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_163ac 0x163ac : { KEEP(*(.text.tsl9v4160.gatt_ingress_163ac)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_163ac)==1018, "Storage size changed")
 .text.tsl9v4160.direct_successors_167a6 0x167a6 : { KEEP(*(.text.tsl9v4160.direct_successors_167a6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_167a6)==178, "Storage size changed")
 .text.tsl9v4160.direct_closure_16858 0x16858 : { KEEP(*(.text.tsl9v4160.direct_closure_16858)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_16858)==62, "Storage size changed")
 .text.tsl9v4160.direct_closure_16896 0x16896 : { KEEP(*(.text.tsl9v4160.direct_closure_16896)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_16896)==72, "Storage size changed")
 .text.tsl9v4160.direct_closure_168de 0x168de : { KEEP(*(.text.tsl9v4160.direct_closure_168de)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_168de)==96, "Storage size changed")
 .text.tsl9v4160.direct_closure_1693e 0x1693e : { KEEP(*(.text.tsl9v4160.direct_closure_1693e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_1693e)==86, "Storage size changed")
 .text.tsl9v4160.code_continuation_16994 0x16994 : { KEEP(*(.text.tsl9v4160.code_continuation_16994)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16994)==72, "Storage size changed")
 .text.tsl9v4160.code_continuation_169dc 0x169dc : { KEEP(*(.text.tsl9v4160.code_continuation_169dc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_169dc)==84, "Storage size changed")
 .text.tsl9v4160.code_continuation_16a30 0x16a30 : { KEEP(*(.text.tsl9v4160.code_continuation_16a30)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16a30)==76, "Storage size changed")
 .text.tsl9v4160.code_continuation_16a7c 0x16a7c : { KEEP(*(.text.tsl9v4160.code_continuation_16a7c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16a7c)==142, "Storage size changed")
 .text.tsl9v4160.direct_expansion_16b0a 0x16b0a : { KEEP(*(.text.tsl9v4160.direct_expansion_16b0a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_16b0a)==70, "Storage size changed")
 .text.tsl9v4160.code_continuation_16b50 0x16b50 : { KEEP(*(.text.tsl9v4160.code_continuation_16b50)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16b50)==44, "Storage size changed")
 .text.tsl9v4160.code_continuation_16b7c 0x16b7c : { KEEP(*(.text.tsl9v4160.code_continuation_16b7c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16b7c)==246, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_16c72 0x16c72 : { KEEP(*(.text.tsl9v4160.gatt_ingress_16c72)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_16c72)==82, "Storage size changed")
 .text.tsl9v4160.code_continuation_16cc4 0x16cc4 : { KEEP(*(.text.tsl9v4160.code_continuation_16cc4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16cc4)==232, "Storage size changed")
 .text.tsl9v4160.direct_closure_16dac 0x16dac : { KEEP(*(.text.tsl9v4160.direct_closure_16dac)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_16dac)==40, "Storage size changed")
 .text.tsl9v4160.direct_expansion_16dd4 0x16dd4 : { KEEP(*(.text.tsl9v4160.direct_expansion_16dd4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_16dd4)==56, "Storage size changed")
 .text.tsl9v4160.code_continuation_16e0c 0x16e0c : { KEEP(*(.text.tsl9v4160.code_continuation_16e0c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_16e0c)==124, "Storage size changed")
 .text.tsl9v4160.direct_expansion_16e88 0x16e88 : { KEEP(*(.text.tsl9v4160.direct_expansion_16e88)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_16e88)==120, "Storage size changed")
 .text.tsl9v4160.callback_16f00 0x16f00 : { KEEP(*(.text.tsl9v4160.callback_16f00)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_16f00)==182, "Storage size changed")
 .text.tsl9v4160.handler_16fb6 0x16fb6 : { KEEP(*(.text.tsl9v4160.handler_16fb6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_16fb6)==76, "Storage size changed")
 .text.tsl9v4160.init_17002 0x17002 : { KEEP(*(.text.tsl9v4160.init_17002)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_17002)==62, "Storage size changed")
 .text.tsl9v4160.init_17040 0x17040 : { KEEP(*(.text.tsl9v4160.init_17040)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_17040)==378, "Storage size changed")
 .text.tsl9v4160.direct_closure_171ba 0x171ba : { KEEP(*(.text.tsl9v4160.direct_closure_171ba)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_171ba)==36, "Storage size changed")
 .text.tsl9v4160.direct_expansion_171de 0x171de : { KEEP(*(.text.tsl9v4160.direct_expansion_171de)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_171de)==216, "Storage size changed")
 .text.tsl9v4160.callback_172b6 0x172b6 : { KEEP(*(.text.tsl9v4160.callback_172b6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_172b6)==106, "Storage size changed")
 .text.tsl9v4160.direct_followup_17320 0x17320 : { KEEP(*(.text.tsl9v4160.direct_followup_17320)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_17320)==36, "Storage size changed")
 .text.tsl9v4160.direct_expansion_17344 0x17344 : { KEEP(*(.text.tsl9v4160.direct_expansion_17344)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_17344)==94, "Storage size changed")
 .text.tsl9v4160.init_173a2 0x173a2 : { KEEP(*(.text.tsl9v4160.init_173a2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_173a2)==76, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_173ee 0x173ee : { KEEP(*(.text.tsl9v4160.conditional_runtime_173ee)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_173ee)==332, "Storage size changed")
 .text.tsl9v4160.direct_expansion_1753a 0x1753a : { KEEP(*(.text.tsl9v4160.direct_expansion_1753a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_1753a)==174, "Storage size changed")
 .text.tsl9v4160.direct_expansion_175e8 0x175e8 : { KEEP(*(.text.tsl9v4160.direct_expansion_175e8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_175e8)==126, "Storage size changed")
 .text.tsl9v4160.code_continuation_17666 0x17666 : { KEEP(*(.text.tsl9v4160.code_continuation_17666)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_17666)==58, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_176a0 0x176a0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_176a0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_176a0)==88, "Storage size changed")
 .text.tsl9v4160.callback_176f8 0x176f8 : { KEEP(*(.text.tsl9v4160.callback_176f8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_176f8)==388, "Storage size changed")
 .text.tsl9v4160.direct_expansion_1787c 0x1787c : { KEEP(*(.text.tsl9v4160.direct_expansion_1787c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_1787c)==124, "Storage size changed")
 .text.tsl9v4160.callback_178f8 0x178f8 : { KEEP(*(.text.tsl9v4160.callback_178f8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callback_178f8)==80, "Storage size changed")
 .text.tsl9v4160.direct_followup_17948 0x17948 : { KEEP(*(.text.tsl9v4160.direct_followup_17948)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_17948)==66, "Storage size changed")
 .text.tsl9v4160.direct_expansion_1798a 0x1798a : { KEEP(*(.text.tsl9v4160.direct_expansion_1798a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_1798a)==114, "Storage size changed")
 .text.tsl9v4160.direct_successors_179fc 0x179fc : { KEEP(*(.text.tsl9v4160.direct_successors_179fc)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_179fc)==406, "Storage size changed")
 .text.tsl9v4160.direct_expansion_17b92 0x17b92 : { KEEP(*(.text.tsl9v4160.direct_expansion_17b92)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_17b92)==50, "Storage size changed")
 .text.tsl9v4160.direct_successors_17bc4 0x17bc4 : { KEEP(*(.text.tsl9v4160.direct_successors_17bc4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_17bc4)==50, "Storage size changed")
 .text.tsl9v4160.core_flow_17bf6 0x17bf6 : { KEEP(*(.text.tsl9v4160.core_flow_17bf6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.core_flow_17bf6)==88, "Storage size changed")
 .text.tsl9v4160.direct_successors_17c4e 0x17c4e : { KEEP(*(.text.tsl9v4160.direct_successors_17c4e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_17c4e)==100, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_17cb2 0x17cb2 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_17cb2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_17cb2)==66, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_17cf4 0x17cf4 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_17cf4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_17cf4)==652, "Storage size changed")
 .text.tsl9v4160.direct_frontier_17f80 0x17f80 : { KEEP(*(.text.tsl9v4160.direct_frontier_17f80)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_17f80)==174, "Storage size changed")
 .text.tsl9v4160.direct_followup_1802e 0x1802e : { KEEP(*(.text.tsl9v4160.direct_followup_1802e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_1802e)==44, "Storage size changed")
 .text.tsl9v4160.direct_frontier_1805a 0x1805a : { KEEP(*(.text.tsl9v4160.direct_frontier_1805a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_1805a)==150, "Storage size changed")
 .text.tsl9v4160.direct_followup_180f0 0x180f0 : { KEEP(*(.text.tsl9v4160.direct_followup_180f0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_180f0)==32, "Storage size changed")
 .text.tsl9v4160.direct_frontier_18110 0x18110 : { KEEP(*(.text.tsl9v4160.direct_frontier_18110)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_18110)==10, "Storage size changed")
 .text.tsl9v4160.direct_frontier_1811a 0x1811a : { KEEP(*(.text.tsl9v4160.direct_frontier_1811a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_1811a)==134, "Storage size changed")
 .text.tsl9v4160.materialized_callbacks_181a0 0x181a0 : { KEEP(*(.text.tsl9v4160.materialized_callbacks_181a0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.materialized_callbacks_181a0)==36, "Storage size changed")
 .text.tsl9v4160.direct_closure_181c4 0x181c4 : { KEEP(*(.text.tsl9v4160.direct_closure_181c4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_181c4)==10, "Storage size changed")
 .text.tsl9v4160.direct_successors_181ce 0x181ce : { KEEP(*(.text.tsl9v4160.direct_successors_181ce)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_181ce)==74, "Storage size changed")
 .text.tsl9v4160.direct_frontier_18218 0x18218 : { KEEP(*(.text.tsl9v4160.direct_frontier_18218)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_frontier_18218)==26, "Storage size changed")
 .text.tsl9v4160.direct_successors_18232 0x18232 : { KEEP(*(.text.tsl9v4160.direct_successors_18232)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_18232)==510, "Storage size changed")
 .text.tsl9v4160.direct_followup_18430 0x18430 : { KEEP(*(.text.tsl9v4160.direct_followup_18430)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_followup_18430)==122, "Storage size changed")
 .text.tsl9v4160.gatt_ingress_184aa 0x184aa : { KEEP(*(.text.tsl9v4160.gatt_ingress_184aa)) }
 ASSERT(SIZEOF(.text.tsl9v4160.gatt_ingress_184aa)==302, "Storage size changed")
 .text.tsl9v4160.post_table_code_185d8 0x185d8 : { KEEP(*(.text.tsl9v4160.post_table_code_185d8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.post_table_code_185d8)==44, "Storage size changed")
 .text.tsl9v4160.direct_expansion_18604 0x18604 : { KEEP(*(.text.tsl9v4160.direct_expansion_18604)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_18604)==44, "Storage size changed")
 .rodata.tsl9v4160.image_only_18630 0x18630 : { KEEP(*(.rodata.tsl9v4160.image_only_18630)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_18630)==8, "Storage size changed")
 .text.tsl9v4160.vector_loop_pool 0x18638 : { KEEP(*(.text.tsl9v4160.vector_loop_pool)) }
 ASSERT(SIZEOF(.text.tsl9v4160.vector_loop_pool)==114, "Storage size changed")
 .text.tsl9v4160.reset 0x186aa : { KEEP(*(.text.tsl9v4160.reset)) }
 ASSERT(SIZEOF(.text.tsl9v4160.reset)==138, "Storage size changed")
 .text.tsl9v4160.stub_18734 0x18734 : { KEEP(*(.text.tsl9v4160.stub_18734)) }
 ASSERT(SIZEOF(.text.tsl9v4160.stub_18734)==4, "Storage size changed")
 .text.tsl9v4160.stub_18738 0x18738 : { KEEP(*(.text.tsl9v4160.stub_18738)) }
 ASSERT(SIZEOF(.text.tsl9v4160.stub_18738)==4, "Storage size changed")
 .text.tsl9v4160.stub_1873c 0x1873c : { KEEP(*(.text.tsl9v4160.stub_1873c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.stub_1873c)==2, "Storage size changed")
 .text.tsl9v4160.stub_1873e 0x1873e : { KEEP(*(.text.tsl9v4160.stub_1873e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.stub_1873e)==12, "Storage size changed")
 .text.tsl9v4160.clock 0x1874a : { KEEP(*(.text.tsl9v4160.clock)) }
 ASSERT(SIZEOF(.text.tsl9v4160.clock)==234, "Storage size changed")
 .text.tsl9v4160.init_18834 0x18834 : { KEEP(*(.text.tsl9v4160.init_18834)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_18834)==174, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_188e2 0x188e2 : { KEEP(*(.text.tsl9v4160.conditional_runtime_188e2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_188e2)==462, "Storage size changed")
 .text.tsl9v4160.direct_expansion_18ab0 0x18ab0 : { KEEP(*(.text.tsl9v4160.direct_expansion_18ab0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_18ab0)==242, "Storage size changed")
 .text.tsl9v4160.direct_closure_18ba2 0x18ba2 : { KEEP(*(.text.tsl9v4160.direct_closure_18ba2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18ba2)==258, "Storage size changed")
 .text.tsl9v4160.code_continuation_18ca4 0x18ca4 : { KEEP(*(.text.tsl9v4160.code_continuation_18ca4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_18ca4)==212, "Storage size changed")
 .text.tsl9v4160.callee_18d78 0x18d78 : { KEEP(*(.text.tsl9v4160.callee_18d78)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_18d78)==164, "Storage size changed")
 .text.tsl9v4160.frontier_18e1c 0x18e1c : { KEEP(*(.text.tsl9v4160.frontier_18e1c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_18e1c)==106, "Storage size changed")
 .text.tsl9v4160.callee_18e86 0x18e86 : { KEEP(*(.text.tsl9v4160.callee_18e86)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_18e86)==10, "Storage size changed")
 .text.tsl9v4160.direct_closure_18e90 0x18e90 : { KEEP(*(.text.tsl9v4160.direct_closure_18e90)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18e90)==8, "Storage size changed")
 .text.tsl9v4160.direct_closure_18e98 0x18e98 : { KEEP(*(.text.tsl9v4160.direct_closure_18e98)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18e98)==30, "Storage size changed")
 .text.tsl9v4160.direct_closure_18eb6 0x18eb6 : { KEEP(*(.text.tsl9v4160.direct_closure_18eb6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18eb6)==14, "Storage size changed")
 .text.tsl9v4160.direct_closure_18ec4 0x18ec4 : { KEEP(*(.text.tsl9v4160.direct_closure_18ec4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18ec4)==46, "Storage size changed")
 .text.tsl9v4160.direct_closure_18ef2 0x18ef2 : { KEEP(*(.text.tsl9v4160.direct_closure_18ef2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_18ef2)==100, "Storage size changed")
 .text.tsl9v4160.direct_expansion_18f56 0x18f56 : { KEEP(*(.text.tsl9v4160.direct_expansion_18f56)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_18f56)==50, "Storage size changed")
 .text.tsl9v4160.code_continuation_18f88 0x18f88 : { KEEP(*(.text.tsl9v4160.code_continuation_18f88)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_18f88)==194, "Storage size changed")
 .text.tsl9v4160.frontier_1904a 0x1904a : { KEEP(*(.text.tsl9v4160.frontier_1904a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_1904a)==44, "Storage size changed")
 .text.tsl9v4160.code_continuation_19076 0x19076 : { KEEP(*(.text.tsl9v4160.code_continuation_19076)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_19076)==22, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_1908c 0x1908c : { KEEP(*(.text.tsl9v4160.conditional_runtime_1908c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_1908c)==18, "Storage size changed")
 .text.tsl9v4160.code_continuation_1909e 0x1909e : { KEEP(*(.text.tsl9v4160.code_continuation_1909e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_1909e)==40, "Storage size changed")
 .text.tsl9v4160.code_continuation_190c6 0x190c6 : { KEEP(*(.text.tsl9v4160.code_continuation_190c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_190c6)==20, "Storage size changed")
 .text.tsl9v4160.code_continuation_190da 0x190da : { KEEP(*(.text.tsl9v4160.code_continuation_190da)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_190da)==12, "Storage size changed")
 .text.tsl9v4160.code_continuation_190e6 0x190e6 : { KEEP(*(.text.tsl9v4160.code_continuation_190e6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_190e6)==32, "Storage size changed")
 .text.tsl9v4160.direct_expansion_19106 0x19106 : { KEEP(*(.text.tsl9v4160.direct_expansion_19106)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_19106)==30, "Storage size changed")
 .text.tsl9v4160.frontier_19124 0x19124 : { KEEP(*(.text.tsl9v4160.frontier_19124)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_19124)==30, "Storage size changed")
 .text.tsl9v4160.frontier_19142 0x19142 : { KEEP(*(.text.tsl9v4160.frontier_19142)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_19142)==30, "Storage size changed")
 .text.tsl9v4160.frontier_19160 0x19160 : { KEEP(*(.text.tsl9v4160.frontier_19160)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_19160)==30, "Storage size changed")
 .text.tsl9v4160.frontier_1917e 0x1917e : { KEEP(*(.text.tsl9v4160.frontier_1917e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_1917e)==30, "Storage size changed")
 .text.tsl9v4160.direct_closure_1919c 0x1919c : { KEEP(*(.text.tsl9v4160.direct_closure_1919c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_1919c)==18, "Storage size changed")
 .text.tsl9v4160.direct_closure_191ae 0x191ae : { KEEP(*(.text.tsl9v4160.direct_closure_191ae)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_191ae)==24, "Storage size changed")
 .text.tsl9v4160.direct_closure_191c6 0x191c6 : { KEEP(*(.text.tsl9v4160.direct_closure_191c6)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_191c6)==90, "Storage size changed")
 .text.tsl9v4160.code_continuation_19220 0x19220 : { KEEP(*(.text.tsl9v4160.code_continuation_19220)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_19220)==40, "Storage size changed")
 .text.tsl9v4160.code_continuation_19248 0x19248 : { KEEP(*(.text.tsl9v4160.code_continuation_19248)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_19248)==42, "Storage size changed")
 .text.tsl9v4160.callee_19272 0x19272 : { KEEP(*(.text.tsl9v4160.callee_19272)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_19272)==16, "Storage size changed")
 .text.tsl9v4160.callee_19282 0x19282 : { KEEP(*(.text.tsl9v4160.callee_19282)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_19282)==20, "Storage size changed")
 .text.tsl9v4160.callee_19296 0x19296 : { KEEP(*(.text.tsl9v4160.callee_19296)) }
 ASSERT(SIZEOF(.text.tsl9v4160.callee_19296)==4, "Storage size changed")
 .text.tsl9v4160.direct_closure_1929a 0x1929a : { KEEP(*(.text.tsl9v4160.direct_closure_1929a)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_closure_1929a)==1066, "Storage size changed")
 .text.tsl9v4160.frontier_196c4 0x196c4 : { KEEP(*(.text.tsl9v4160.frontier_196c4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_196c4)==90, "Storage size changed")
 .text.tsl9v4160.frontier_1971e 0x1971e : { KEEP(*(.text.tsl9v4160.frontier_1971e)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_1971e)==30, "Storage size changed")
 .text.tsl9v4160.init_1973c 0x1973c : { KEEP(*(.text.tsl9v4160.init_1973c)) }
 ASSERT(SIZEOF(.text.tsl9v4160.init_1973c)==40, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_19764 0x19764 : { KEEP(*(.text.tsl9v4160.conditional_runtime_19764)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_19764)==84, "Storage size changed")
 .text.tsl9v4160.code_continuation_197b8 0x197b8 : { KEEP(*(.text.tsl9v4160.code_continuation_197b8)) }
 ASSERT(SIZEOF(.text.tsl9v4160.code_continuation_197b8)==6, "Storage size changed")
 .text.tsl9v4160.conditional_runtime_197be 0x197be : { KEEP(*(.text.tsl9v4160.conditional_runtime_197be)) }
 ASSERT(SIZEOF(.text.tsl9v4160.conditional_runtime_197be)==548, "Storage size changed")
 .text.tsl9v4160.frontier_199e2 0x199e2 : { KEEP(*(.text.tsl9v4160.frontier_199e2)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_199e2)==308, "Storage size changed")
 .text.tsl9v4160.frontier_19b16 0x19b16 : { KEEP(*(.text.tsl9v4160.frontier_19b16)) }
 ASSERT(SIZEOF(.text.tsl9v4160.frontier_19b16)==64, "Storage size changed")
 .text.tsl9v4160.direct_expansion_19b56 0x19b56 : { KEEP(*(.text.tsl9v4160.direct_expansion_19b56)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_expansion_19b56)==126, "Storage size changed")
 .text.tsl9v4160.handler_19bd4 0x19bd4 : { KEEP(*(.text.tsl9v4160.handler_19bd4)) }
 ASSERT(SIZEOF(.text.tsl9v4160.handler_19bd4)==28, "Storage size changed")
 .text.tsl9v4160.direct_successors_19bf0 0x19bf0 : { KEEP(*(.text.tsl9v4160.direct_successors_19bf0)) }
 ASSERT(SIZEOF(.text.tsl9v4160.direct_successors_19bf0)==182, "Storage size changed")
 .rodata.tsl9v4160.image_only_19ca6 0x19ca6 : { KEEP(*(.rodata.tsl9v4160.image_only_19ca6)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_19ca6)==2, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19ca8 0x19ca8 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19ca8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19ca8)==96, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19d08 0x19d08 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19d08)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19d08)==94, "Storage size changed")
 .rodata.tsl9v4160.image_only_19d66 0x19d66 : { KEEP(*(.rodata.tsl9v4160.image_only_19d66)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_19d66)==2, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19d68 0x19d68 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19d68)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19d68)==106, "Storage size changed")
 .rodata.tsl9v4160.image_only_19dd2 0x19dd2 : { KEEP(*(.rodata.tsl9v4160.image_only_19dd2)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_19dd2)==2, "Storage size changed")
 .rodata.tsl9v4160.gatt_ingress_19dd4 0x19dd4 : { KEEP(*(.rodata.tsl9v4160.gatt_ingress_19dd4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.gatt_ingress_19dd4)==12, "Storage size changed")
 .rodata.tsl9v4160.retained_data_19de0 0x19de0 : { KEEP(*(.rodata.tsl9v4160.retained_data_19de0)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_19de0)==12, "Storage size changed")
 .rodata.tsl9v4160.finite_data_19dec 0x19dec : { KEEP(*(.rodata.tsl9v4160.finite_data_19dec)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_19dec)==13, "Storage size changed")
 .rodata.tsl9v4160.image_only_19df9 0x19df9 : { KEEP(*(.rodata.tsl9v4160.image_only_19df9)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.image_only_19df9)==3, "Storage size changed")
 .rodata.tsl9v4160.retained_data_19dfc 0x19dfc : { KEEP(*(.rodata.tsl9v4160.retained_data_19dfc)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_19dfc)==12, "Storage size changed")
 .rodata.tsl9v4160.relative_table_19e08 0x19e08 : { KEEP(*(.rodata.tsl9v4160.relative_table_19e08)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_19e08)==72, "Storage size changed")
 .rodata.tsl9v4160.relative_table_19e50 0x19e50 : { KEEP(*(.rodata.tsl9v4160.relative_table_19e50)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_19e50)==44, "Storage size changed")
 .rodata.tsl9v4160.relative_table_19e7c 0x19e7c : { KEEP(*(.rodata.tsl9v4160.relative_table_19e7c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_19e7c)==44, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19ea8 0x19ea8 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19ea8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19ea8)==16, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19eb8 0x19eb8 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19eb8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19eb8)==16, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_19ec8 0x19ec8 : { KEEP(*(.rodata.tsl9v4160.readonly_view_19ec8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_19ec8)==16, "Storage size changed")
 .rodata.tsl9v4160.observed_union_19ed8 0x19ed8 : { KEEP(*(.rodata.tsl9v4160.observed_union_19ed8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.observed_union_19ed8)==432, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a088 0x1a088 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a088)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a088)==84, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a0dc 0x1a0dc : { KEEP(*(.rodata.tsl9v4160.relative_table_1a0dc)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a0dc)==96, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a13c 0x1a13c : { KEEP(*(.rodata.tsl9v4160.relative_table_1a13c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a13c)==20, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a150 0x1a150 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a150)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a150)==120, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a1c8 0x1a1c8 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a1c8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a1c8)==332, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a314 0x1a314 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a314)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a314)==40, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a33c 0x1a33c : { KEEP(*(.rodata.tsl9v4160.relative_table_1a33c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a33c)==244, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a430 0x1a430 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a430)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a430)==34, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a452 0x1a452 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a452)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a452)==2, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a454 0x1a454 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a454)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a454)==34, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a476 0x1a476 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a476)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a476)==2, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a478 0x1a478 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a478)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a478)==106, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a4e2 0x1a4e2 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a4e2)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a4e2)==2, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1a4e4 0x1a4e4 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1a4e4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1a4e4)==16, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1a4f4 0x1a4f4 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1a4f4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1a4f4)==36, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1a518 0x1a518 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1a518)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1a518)==15, "Storage size changed")
 .rodata.tsl9v4160.observed_fragment_1a527 0x1a527 : { KEEP(*(.rodata.tsl9v4160.observed_fragment_1a527)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.observed_fragment_1a527)==1, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1a528 0x1a528 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1a528)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1a528)==15, "Storage size changed")
 .rodata.tsl9v4160.observed_fragment_1a537 0x1a537 : { KEEP(*(.rodata.tsl9v4160.observed_fragment_1a537)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.observed_fragment_1a537)==1, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1a538 0x1a538 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1a538)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1a538)==15, "Storage size changed")
 .rodata.tsl9v4160.observed_fragment_1a547 0x1a547 : { KEEP(*(.rodata.tsl9v4160.observed_fragment_1a547)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.observed_fragment_1a547)==191, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a606 0x1a606 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a606)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a606)==2, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a608 0x1a608 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a608)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a608)==9, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a611 0x1a611 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a611)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a611)==3, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a614 0x1a614 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a614)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a614)==7, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a61b 0x1a61b : { KEEP(*(.rodata.tsl9v4160.retained_data_1a61b)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a61b)==1, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a61c 0x1a61c : { KEEP(*(.rodata.tsl9v4160.finite_data_1a61c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a61c)==11, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a627 0x1a627 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a627)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a627)==1, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a628 0x1a628 : { KEEP(*(.rodata.tsl9v4160.finite_data_1a628)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a628)==3, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a62b 0x1a62b : { KEEP(*(.rodata.tsl9v4160.retained_data_1a62b)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a62b)==1, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a62c 0x1a62c : { KEEP(*(.rodata.tsl9v4160.finite_data_1a62c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a62c)==10, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a636 0x1a636 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a636)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a636)==50, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a668 0x1a668 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a668)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a668)==12, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a674 0x1a674 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a674)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a674)==12, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a680 0x1a680 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a680)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a680)==28, "Storage size changed")
 .rodata.tsl9v4160.finite_data_1a69c 0x1a69c : { KEEP(*(.rodata.tsl9v4160.finite_data_1a69c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.finite_data_1a69c)==5, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1a6a1 0x1a6a1 : { KEEP(*(.rodata.tsl9v4160.retained_data_1a6a1)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1a6a1)==3, "Storage size changed")
 .rodata.tsl9v4160.gatt_ingress_1a6a4 0x1a6a4 : { KEEP(*(.rodata.tsl9v4160.gatt_ingress_1a6a4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.gatt_ingress_1a6a4)==20, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a6b8 0x1a6b8 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a6b8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a6b8)==28, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a6d4 0x1a6d4 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a6d4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a6d4)==32, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1a6f4 0x1a6f4 : { KEEP(*(.rodata.tsl9v4160.relative_table_1a6f4)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1a6f4)==1012, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1aae8 0x1aae8 : { KEEP(*(.rodata.tsl9v4160.retained_data_1aae8)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1aae8)==28, "Storage size changed")
 .rodata.tsl9v4160.relative_table_1ab04 0x1ab04 : { KEEP(*(.rodata.tsl9v4160.relative_table_1ab04)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.relative_table_1ab04)==24, "Storage size changed")
 .rodata.tsl9v4160.version_literal_1ab1c 0x1ab1c : { KEEP(*(.rodata.tsl9v4160.version_literal_1ab1c)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.version_literal_1ab1c)==22, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1ab32 0x1ab32 : { KEEP(*(.rodata.tsl9v4160.retained_data_1ab32)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1ab32)==2, "Storage size changed")
 .rodata.tsl9v4160.readonly_1ab34_view 0x1ab34 : { KEEP(*(.rodata.tsl9v4160.readonly_1ab34_view)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_1ab34_view)==3, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1ab37 0x1ab37 : { KEEP(*(.rodata.tsl9v4160.retained_data_1ab37)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1ab37)==13, "Storage size changed")
 .rodata.tsl9v4160.reachable_observed_u16_1ab44 0x1ab44 : { KEEP(*(.rodata.tsl9v4160.reachable_observed_u16_1ab44)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.reachable_observed_u16_1ab44)==2, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1ab46 0x1ab46 : { KEEP(*(.rodata.tsl9v4160.retained_data_1ab46)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1ab46)==10, "Storage size changed")
 .rodata.tsl9v4160.readonly_view_1ab50 0x1ab50 : { KEEP(*(.rodata.tsl9v4160.readonly_view_1ab50)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.readonly_view_1ab50)==8, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1ab58 0x1ab58 : { KEEP(*(.rodata.tsl9v4160.retained_data_1ab58)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1ab58)==1, "Storage size changed")
 .rodata.tsl9v4160.data_fragment_1ab59 0x1ab59 : { KEEP(*(.rodata.tsl9v4160.data_fragment_1ab59)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.data_fragment_1ab59)==7, "Storage size changed")
 .rodata.tsl9v4160.initializer 0x1ab60 : { KEEP(*(.rodata.tsl9v4160.initializer)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.initializer)==128, "Storage size changed")
 .rodata.tsl9v4160.retained_data_1abe0 0x1abe0 : { KEEP(*(.rodata.tsl9v4160.retained_data_1abe0)) }
 ASSERT(SIZEOF(.rodata.tsl9v4160.retained_data_1abe0)==32, "Storage size changed")
 .bss.tsl9v4160.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) }
 ASSERT(SIZEOF(.bss.tsl9v4160.ram)==35160, "Storage size changed")
 /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
