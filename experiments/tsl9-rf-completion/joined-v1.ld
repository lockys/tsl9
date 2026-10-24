/* Genuine completion/retry entries;not final original-PC placement. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_rf_completion_entry_173ee)
  *(.text.tsl9_rf_completion_block_17408)
  *(.text.tsl9_rf_completion_block_17428)
  *(.text.tsl9_rf_completion_block_1743a)
  *(.text.tsl9_rf_completion_entry_17442)
  *(.text.tsl9_rf_completion_block_1745a)
  *(.text.tsl9_rf_completion_block_17460)
  tsl9_rf_callbacks_provider_173ee = tsl9_rf_completion_entry_173ee;
  tsl9_rf_callbacks_provider_17442 = tsl9_rf_completion_entry_17442;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
