OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_services_provider_9290)
  *(.text.tsl9_platform_primitives_block_929c)
  *(.text.tsl9_platform_primitives_block_92a4)
  *(.text.tsl9_platform_primitives_block_92a6)
  *(.text.tsl9_platform_primitives_block_92b2)
  *(.text.tsl9_platform_primitives_block_92b4)
  *(.text.tsl9_main_services_provider_18604)
  *(.text.tsl9_platform_primitives_block_18622)
  *(.text.tsl9_main_services_provider_18e1c)
  *(.text.tsl9_platform_primitives_block_18e34)
  *(.text.tsl9_platform_primitives_block_18e66)
  *(.text.tsl9_platform_primitives_block_18e74)
  *(.text.tsl9_platform_primitives_block_18e7e)
  *(.text.tsl9_main_services_provider_1904a)
  *(.text.tsl9_main_services_provider_196c4)
  *(.text.tsl9_main_services_provider_1971e)
  *(.text.tsl9_platform_primitives_block_19724)
  *(.text.tsl9_platform_primitives_block_19728)
  *(.text.tsl9_platform_primitives_block_1972e)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
