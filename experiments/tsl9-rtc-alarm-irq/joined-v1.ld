/* Diagnostic real-code composition only; not final original-address layout. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_rtc_alarm_entry_19bd4)
  *(.text.tsl9_rtc_exti_write_18e86)
  *(.text.tsl9_rtc_wait_19272)
  *(.text.tsl9_rtc_clear_19282)
  *(.text.tsl9_rtc_clear_alias_19296)
  tsl9_vector_entry_19bd4 = tsl9_rtc_alarm_entry_19bd4;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
