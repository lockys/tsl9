OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_ota_reply_external_9ea6)
  *(.text.tsl9_ota_finalizers_block_9eb2)
  *(.text.tsl9_ota_finalizers_block_9eb4)
  *(.text.tsl9_ota_finalizers_block_9ec0)
  *(.text.tsl9_ota_finalizers_block_9ece)
  *(.text.tsl9_ota_finalizers_block_9ed0)
  *(.text.tsl9_ota_finalizers_block_9ed2)
  *(.text.tsl9_ota_finalizers_block_9edc)
  *(.text.tsl9_ota_reply_external_16e0c)
  *(.text.tsl9_ota_finalizers_block_16e20)
  *(.text.tsl9_ota_finalizers_block_16e2a)
  *(.text.tsl9_ota_finalizers_block_16e30)
  *(.text.tsl9_ota_finalizers_block_16e3a)
  *(.text.tsl9_ota_finalizers_block_16e42)
  *(.text.tsl9_ota_finalizers_block_16e50)
  *(.text.tsl9_ota_finalizers_block_16e58)
  *(.text.tsl9_ota_finalizers_block_16e5c)
  *(.text.tsl9_ota_finalizers_block_16e64)
  *(.text.tsl9_ota_finalizers_block_16e66)
  *(.text.tsl9_ota_finalizers_block_16e74)
  *(.text.tsl9_ota_finalizers_block_16e7c)
  *(.text.tsl9_ota_finalizers_block_16e84)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
