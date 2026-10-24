/* Diagnostic composition only; no final original-PC placement claim. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_record_control_entry_1798a)
  *(.text.tsl9_record_control_block_17992)
  *(.text.tsl9_record_control_block_17998)
  *(.text.tsl9_record_control_block_179b2)
  *(.text.tsl9_record_control_block_179c0)
  *(.text.tsl9_record_control_block_179ca)
  *(.text.tsl9_record_control_block_179ce)
  *(.text.tsl9_record_control_block_179d8)
  *(.text.tsl9_record_control_block_179de)
  *(.text.tsl9_record_control_block_179e4)
  *(.text.tsl9_record_control_block_179f8)
  *(.text.tsl9_record_control_block_179fa)
  tsl9_main_provider_1798a = tsl9_record_control_entry_1798a;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
