OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_init_external_18ab0)
  *(.text.tsl9_peripheral_initializer_block_18ac2)
  *(.text.tsl9_peripheral_initializer_block_18ac8)
  *(.text.tsl9_peripheral_initializer_block_18acc)
  *(.text.tsl9_peripheral_initializer_block_18ad4)
  *(.text.tsl9_peripheral_initializer_block_18adc)
  *(.text.tsl9_peripheral_initializer_block_18ae2)
  *(.text.tsl9_peripheral_initializer_block_18aec)
  *(.text.tsl9_peripheral_initializer_block_18af2)
  *(.text.tsl9_peripheral_initializer_block_18afc)
  *(.text.tsl9_peripheral_initializer_block_18b02)
  *(.text.tsl9_peripheral_initializer_block_18b0c)
  *(.text.tsl9_peripheral_initializer_block_18b12)
  *(.text.tsl9_peripheral_initializer_block_18b1c)
  *(.text.tsl9_peripheral_initializer_block_18b22)
  *(.text.tsl9_peripheral_initializer_block_18b2c)
  *(.text.tsl9_peripheral_initializer_block_18b32)
  *(.text.tsl9_peripheral_initializer_block_18b64)
  *(.text.tsl9_peripheral_initializer_block_18b6a)
  *(.text.tsl9_peripheral_initializer_block_18b6e)
  *(.text.tsl9_peripheral_initializer_block_18b76)
  *(.text.tsl9_peripheral_initializer_block_18b78)
  *(.text.tsl9_peripheral_initializer_block_18b80)
  *(.text.tsl9_peripheral_initializer_block_18b88)
  *(.text.tsl9_peripheral_initializer_block_18b90)
  *(.text.tsl9_peripheral_initializer_block_18b96)
  *(.text.tsl9_peripheral_initializer_block_18b9c)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
