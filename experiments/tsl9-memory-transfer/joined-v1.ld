OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_callback_flow_external_19bf0)
  *(.text.tsl9_memory_transfer_block_19bfc)
  *(.text.tsl9_memory_transfer_block_19c02)
  *(.text.tsl9_memory_transfer_block_19c08)
  *(.text.tsl9_memory_transfer_block_19c18)
  *(.text.tsl9_memory_transfer_block_19c1a)
  *(.text.tsl9_memory_transfer_block_19c20)
  *(.text.tsl9_memory_transfer_block_19c22)
  *(.text.tsl9_memory_transfer_block_19c34)
  *(.text.tsl9_memory_transfer_block_19c3c)
  *(.text.tsl9_memory_transfer_block_19c40)
  *(.text.tsl9_memory_transfer_block_19c92)
  *(.text.tsl9_memory_transfer_block_19c9c)
  *(.text.tsl9_memory_transfer_block_19ca0)
  *(.text.tsl9_memory_transfer_block_19ca4)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
