/* Diagnostic composition only; original-PC placement is unproved. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_callback_table_entry_901a)
  *(.text.tsl9_callback_table_block_9026)
  *(.text.tsl9_callback_table_block_902e)
  *(.text.tsl9_callback_table_block_9044)
  *(.text.tsl9_callback_table_block_9050)
  *(.text.tsl9_callback_table_block_9058)
  *(.text.tsl9_callback_table_block_905a)
  *(.text.tsl9_callback_table_block_9066)
  *(.text.tsl9_callback_table_block_9070)
  *(.text.tsl9_callback_table_block_9076)
  *(.text.tsl9_callback_table_entry_907a)
  *(.text.tsl9_callback_table_block_9096)
  *(.text.tsl9_callback_table_block_90a4)
  *(.text.tsl9_callback_table_entry_90b0)
  *(.text.tsl9_callback_table_block_90c6)
  *(.text.tsl9_callback_table_block_90cc)
  *(.text.tsl9_callback_table_block_90d8)
  *(.text.tsl9_callback_table_block_90e0)
  *(.text.tsl9_callback_table_block_9110)
  *(.text.tsl9_callback_table_block_9118)
  tsl9_main_provider_90b0 = tsl9_callback_table_entry_90b0;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
