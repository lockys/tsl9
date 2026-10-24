OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_record_dispatch_provider_8e6a)
  *(.text.tsl9_output_dependencies_provider_9f7a)
  *(.text.tsl9_output_dependencies_block_9f88)
  *(.text.tsl9_output_dependencies_block_9f92)
  *(.text.tsl9_output_dependencies_block_9f9a)
  *(.text.tsl9_output_dependencies_block_9f9e)
  *(.text.tsl9_output_dependencies_block_9fa6)
  *(.text.tsl9_output_builder_provider_9fc8)
  *(.text.tsl9_output_dependencies_block_9fda)
  *(.text.tsl9_output_dependencies_block_9fe2)
  *(.text.tsl9_output_dependencies_block_9fe4)
  *(.text.tsl9_output_dependencies_block_9fea)
  *(.text.tsl9_output_dependencies_block_a004)
  *(.text.tsl9_output_dependencies_block_a00a)
  *(.text.tsl9_output_dependencies_provider_d7d4)
  *(.text.tsl9_output_dependencies_block_d7e6)
  *(.text.tsl9_output_dependencies_block_d7ec)
  *(.text.tsl9_output_dependencies_block_d802)
  *(.text.tsl9_output_dependencies_block_d808)
  *(.text.tsl9_output_builder_provider_d810)
  *(.text.tsl9_output_dependencies_block_d822)
  *(.text.tsl9_output_dependencies_block_d826)
  *(.text.tsl9_output_dependencies_block_d834)
  *(.text.tsl9_output_dependencies_block_d842)
  *(.text.tsl9_output_dependencies_block_d848)
  *(.text.tsl9_output_dependencies_block_d850)
  *(.text.tsl9_output_dependencies_block_d852)
  *(.text.tsl9_output_dependencies_block_d854)
  *(.text.tsl9_output_dependencies_block_d85e)
  *(.text.tsl9_output_dependencies_block_d862)
  *(.text.tsl9_output_dependencies_block_d866)
  *(.text.tsl9_record_dispatch_provider_f818)
  *(.text.tsl9_record_dispatch_provider_f822)
  *(.text.tsl9_output_dependencies_provider_f82c)
  *(.text.tsl9_output_dependencies_provider_f838)
  *(.text.tsl9_main_services_provider_f84a)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 .action_table 0 : SUBALIGN(4) { *(.action_table) }
 .phase_table 0 : SUBALIGN(4) { *(.phase_table) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
