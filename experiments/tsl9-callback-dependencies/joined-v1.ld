OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_registered_callbacks_provider_11356)
  *(.text.tsl9_callback_dependencies_block_11362)
  *(.text.tsl9_callback_dependencies_block_11384)
  *(.text.tsl9_callback_dependencies_block_11392)
  *(.text.tsl9_callback_dependencies_block_113ac)
  *(.text.tsl9_callback_dependencies_block_113b0)
  *(.text.tsl9_callback_dependencies_block_113ba)
  *(.text.tsl9_callback_dependencies_block_113be)
  *(.text.tsl9_callback_dependencies_block_113c2)
  *(.text.tsl9_callback_dependencies_block_113d6)
  *(.text.tsl9_callback_dependencies_block_113dc)
  *(.text.tsl9_callback_dependencies_block_113f0)
  *(.text.tsl9_callback_dependencies_block_11404)
  *(.text.tsl9_callback_dependencies_block_11406)
  *(.text.tsl9_callback_dependencies_block_11430)
  *(.text.tsl9_callback_dependencies_block_11436)
  *(.text.tsl9_callback_dependencies_block_1143e)
  *(.text.tsl9_callback_dependencies_block_11440)
  *(.text.tsl9_registered_callbacks_provider_13cdc)
  *(.text.tsl9_callback_dependencies_block_13cf6)
  *(.text.tsl9_callback_dependencies_block_13cf8)
  *(.text.tsl9_callback_dependencies_block_13d08)
  *(.text.tsl9_callback_dependencies_block_13d0c)
  *(.text.tsl9_callback_dependencies_block_13d12)
  *(.text.tsl9_callback_dependencies_block_13d14)
  *(.text.tsl9_callback_dependencies_block_13d24)
  *(.text.tsl9_callback_dependencies_block_13d26)
  *(.text.tsl9_callback_dependencies_block_13d3c)
  *(.text.tsl9_registered_callbacks_provider_16e88)
  *(.text.tsl9_callback_dependencies_block_16e96)
  *(.text.tsl9_callback_dependencies_block_16e9a)
  *(.text.tsl9_callback_dependencies_block_16ea4)
  *(.text.tsl9_callback_dependencies_block_16eb0)
  *(.text.tsl9_callback_dependencies_block_16ebe)
  *(.text.tsl9_callback_dependencies_block_16ecc)
  *(.text.tsl9_callback_dependencies_block_16ed4)
  *(.text.tsl9_callback_dependencies_block_16edc)
  *(.text.tsl9_callback_dependencies_block_16ee8)
  *(.text.tsl9_callback_dependencies_block_16ef4)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
