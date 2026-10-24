OUTPUT_ARCH(riscv)
SECTIONS
{
 .boot_code 0 : SUBALIGN(2) { *(.boot_code)
  *(.text.tsl9_callback_gate_entry_9a24)
  *(.text.tsl9_callback_gate_block_9a3c)
  *(.text.tsl9_callback_gate_entry_9ad2)
  *(.text.tsl9_callback_flow_external_9af0)
  *(.text.tsl9_callback_gate_block_9af6)
  *(.text.tsl9_callback_gate_block_9b00)
  *(.text.tsl9_main_provider_9b4e)
  *(.text.tsl9_callback_gate_block_9b64)
  *(.text.tsl9_callback_gate_block_9b7a)
  *(.text.tsl9_callback_gate_block_9b88)
  *(.text.tsl9_callback_flow_external_b5b4)
  *(.text.tsl9_callback_flow_external_d314)
  *(.text.tsl9_callback_flow_external_d3e8)
  *(.text.tsl9_callback_gate_entry_18f88)
  *(.text.tsl9_callback_gate_block_18f94)
  *(.text.tsl9_callback_gate_block_18f9a)
  *(.text.tsl9_callback_gate_block_18fa4)
  *(.text.tsl9_callback_gate_block_18fb6)
  *(.text.tsl9_callback_gate_block_18fc2)
  *(.text.tsl9_callback_gate_block_18fde)
  *(.text.tsl9_callback_gate_block_18fe0)
  *(.text.tsl9_callback_gate_block_18fe6)
  *(.text.tsl9_callback_gate_block_18fe8)
  *(.text.tsl9_callback_gate_block_18ff0)
  *(.text.tsl9_callback_gate_block_19002)
  *(.text.tsl9_callback_gate_block_1900e)
  *(.text.tsl9_callback_gate_block_1902a)
  *(.text.tsl9_callback_gate_block_1902e)
  *(.text.tsl9_callback_gate_block_19034)
  *(.text.tsl9_callback_gate_block_19036)
  *(.text.tsl9_callback_gate_block_19038)
  *(.text.tsl9_callback_gate_block_1903c)
  *(.text.tsl9_callback_gate_block_19040)
  *(.text.tsl9_callback_gate_block_19044)
 }
 .initializer 0 : SUBALIGN(4) { *(.initializer) }
 .vectors 0 : SUBALIGN(4) { *(.vectors) }
 .feature_tables 0 : SUBALIGN(4) { *(.feature_tables) }
 .callback_constants 0 : SUBALIGN(4) { *(.callback_constants) }
 .callback_flow_constants 0 : SUBALIGN(4) { *(.callback_flow_constants) }
 /DISCARD/ : { *(.comment) *(.riscv.attributes) *(.llvm_addrsig) }
}
