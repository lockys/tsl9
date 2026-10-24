OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_settings_writer_12e54)
  *(.text.tsl9_settings_defaults_block_12e70)
  *(.text.tsl9_settings_defaults_block_12e7e)
  *(.text.tsl9_main_init_external_12e86)
  *(.text.tsl9_settings_defaults_block_12ea4)
  *(.text.tsl9_settings_writer_12ee6)
  *(.text.tsl9_settings_defaults_block_12f02)
  *(.text.tsl9_settings_defaults_block_12f10)
  *(.text.tsl9_main_init_external_12f18)
  *(.text.tsl9_settings_defaults_block_12f36)
  *(.text.tsl9_settings_writer_12f48)
  *(.text.tsl9_settings_defaults_block_12f64)
  *(.text.tsl9_settings_defaults_block_12f72)
  *(.text.tsl9_main_init_external_12f7a)
  *(.text.tsl9_settings_defaults_block_12f98)
  *(.text.tsl9_settings_writer_13052)
  *(.text.tsl9_settings_defaults_block_1306e)
  *(.text.tsl9_settings_defaults_block_1307c)
  *(.text.tsl9_main_init_external_13084)
  *(.text.tsl9_settings_defaults_block_130a2)
  *(.text.tsl9_settings_writer_130d6)
  *(.text.tsl9_settings_defaults_block_130f2)
  *(.text.tsl9_settings_defaults_block_13100)
  *(.text.tsl9_main_init_external_13108)
  *(.text.tsl9_settings_defaults_block_13126)
  *(.text.tsl9_settings_writer_13138)
  *(.text.tsl9_settings_defaults_block_13154)
  *(.text.tsl9_settings_defaults_block_13162)
  *(.text.tsl9_main_init_external_1316a)
  *(.text.tsl9_settings_defaults_block_1318a)
  *(.text.tsl9_settings_defaults_block_131b6)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
