OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_callback_flow_external_181c4)
  *(.text.tsl9_callback_flow_external_8440)
  *(.text.tsl9_callback_flow_external_b1b0)
  *(.text.tsl9_callback_flow_external_c35a)
  *(.text.tsl9_callback_flow_external_cd44)
  *(.text.tsl9_callback_flow_external_f6b0)
  *(.text.tsl9_callback_flow_external_f6e2)
  *(.text.tsl9_callback_flow_external_f714)
  *(.text.tsl9_callback_flow_external_f746)
  *(.text.tsl9_callback_flow_external_fa2a)
  *(.text.tsl9_callback_flow_external_fa36)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
