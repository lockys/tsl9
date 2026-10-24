OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_main_provider_12d92)
  *(.text.tsl9_main_initializers_block_12dae)
  *(.text.tsl9_main_initializers_block_12dc0)
  *(.text.tsl9_main_initializers_block_12dd0)
  *(.text.tsl9_main_initializers_block_12de2)
  *(.text.tsl9_main_initializers_block_12dee)
  *(.text.tsl9_main_initializers_block_12e0c)
  *(.text.tsl9_main_initializers_block_12e18)
  *(.text.tsl9_main_initializers_block_12e24)
  *(.text.tsl9_main_initializers_block_12e26)
  *(.text.tsl9_main_initializers_block_12e2a)
  *(.text.tsl9_main_initializers_block_12e38)
  *(.text.tsl9_main_initializers_block_12e4c)
  *(.text.tsl9_main_initializers_block_12e50)
  *(.text.tsl9_main_provider_131c2)
  *(.text.tsl9_main_initializers_block_131e2)
  *(.text.tsl9_main_initializers_block_131f6)
  *(.text.tsl9_main_initializers_block_13204)
  *(.text.tsl9_main_initializers_block_13208)
  *(.text.tsl9_main_initializers_block_13224)
  *(.text.tsl9_main_initializers_block_13234)
  *(.text.tsl9_main_initializers_block_13238)
  *(.text.tsl9_main_initializers_block_13254)
  *(.text.tsl9_main_initializers_block_13264)
  *(.text.tsl9_main_initializers_block_13268)
  *(.text.tsl9_main_initializers_block_13284)
  *(.text.tsl9_main_initializers_block_13294)
  *(.text.tsl9_main_initializers_block_13298)
  *(.text.tsl9_main_initializers_block_132b4)
  *(.text.tsl9_main_initializers_block_132c4)
  *(.text.tsl9_main_initializers_block_132c8)
  *(.text.tsl9_main_initializers_block_132e4)
  *(.text.tsl9_main_initializers_block_132f4)
  *(.text.tsl9_main_initializers_block_132fc)
  *(.text.tsl9_main_initializers_block_13302)
  *(.text.tsl9_main_initializers_block_13304)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 .incoming_constants 0 : SUBALIGN(4) { *(.incoming_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
