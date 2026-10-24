OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_record_helpers_provider_bd46)
  *(.text.tsl9_record_helpers_provider_bd50)
  *(.text.tsl9_record_dispatch_provider_bd64)
  *(.text.tsl9_record_helpers_provider_edf2)
  *(.text.tsl9_record_continuations_block_ee00)
  *(.text.tsl9_record_continuations_block_ee2a)
  *(.text.tsl9_record_helpers_provider_ee30)
  *(.text.tsl9_record_continuations_block_ee3c)
  *(.text.tsl9_record_continuations_block_ee58)
  *(.text.tsl9_record_continuations_block_ee64)
  *(.text.tsl9_record_continuations_block_ee68)
  *(.text.tsl9_record_continuations_block_ee7e)
  *(.text.tsl9_record_continuations_block_ee98)
  *(.text.tsl9_record_helpers_provider_ee9a)
  *(.text.tsl9_record_continuations_block_eea2)
  *(.text.tsl9_record_continuations_block_eeae)
  *(.text.tsl9_record_continuations_block_eec6)
  *(.text.tsl9_record_continuations_block_eed6)
  *(.text.tsl9_record_continuations_block_eed8)
  *(.text.tsl9_record_helpers_provider_eee0)
  *(.text.tsl9_record_continuations_block_eee8)
  *(.text.tsl9_record_continuations_block_eef4)
  *(.text.tsl9_record_continuations_block_ef00)
  *(.text.tsl9_record_continuations_block_ef04)
  *(.text.tsl9_record_continuations_block_ef16)
  *(.text.tsl9_record_continuations_block_ef2e)
  *(.text.tsl9_record_continuations_block_ef3c)
  *(.text.tsl9_record_continuations_block_ef40)
  *(.text.tsl9_record_continuations_block_ef42)
  *(.text.tsl9_record_continuations_block_ef56)
  *(.text.tsl9_record_continuations_block_ef5c)
  *(.text.tsl9_record_continuations_block_ef60)
  *(.text.tsl9_record_continuations_provider_ef6c)
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
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
