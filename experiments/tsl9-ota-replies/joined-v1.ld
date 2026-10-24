OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_ota_external_8e18)
  *(.text.tsl9_ota_replies_block_8e24)
  *(.text.tsl9_ota_replies_block_8e32)
  *(.text.tsl9_ota_replies_block_8e3e)
  *(.text.tsl9_ota_replies_block_8e4a)
  *(.text.tsl9_ota_replies_block_8e4c)
  *(.text.tsl9_ota_replies_block_8e52)
  *(.text.tsl9_ota_replies_block_8e5e)
  *(.text.tsl9_ota_replies_block_8e68)
  *(.text.tsl9_ota_external_99e8)
  *(.text.tsl9_ota_replies_block_99f6)
  *(.text.tsl9_ota_replies_block_9a00)
  *(.text.tsl9_ota_replies_block_9a06)
  *(.text.tsl9_ota_replies_block_9a0c)
  *(.text.tsl9_ota_replies_block_9a22)
  *(.text.tsl9_ota_external_9b8e)
  *(.text.tsl9_ota_replies_block_9bb0)
  *(.text.tsl9_ota_replies_block_9bb2)
  *(.text.tsl9_ota_replies_block_9bd6)
  *(.text.tsl9_ota_replies_block_9be4)
  *(.text.tsl9_ota_replies_block_9bfa)
  *(.text.tsl9_ota_external_9ee0)
  *(.text.tsl9_ota_replies_block_9ee8)
  *(.text.tsl9_ota_external_13e98)
  *(.text.tsl9_ota_replies_block_13ea2)
  *(.text.tsl9_ota_replies_block_13ea4)
  *(.text.tsl9_ota_replies_block_13eb0)
  *(.text.tsl9_ota_external_13f66)
  *(.text.tsl9_ota_replies_block_13f78)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
