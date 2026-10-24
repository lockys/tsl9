/* Diagnostic composition; original placement andhardware compatibility unproved. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_record_queue_entry_1787c)
  *(.text.tsl9_record_queue_block_1789a)
  *(.text.tsl9_record_queue_block_178be)
  *(.text.tsl9_record_queue_block_178dc)
  *(.text.tsl9_record_queue_block_178de)
  *(.text.tsl9_record_queue_block_178ee)
  *(.text.tsl9_record_queue_entry_178f8)
  *(.text.tsl9_record_queue_block_1790a)
  *(.text.tsl9_record_queue_block_17942)
  *(.text.tsl9_record_queue_entry_17948)
  *(.text.tsl9_record_queue_block_1796c)
  *(.text.tsl9_record_queue_block_17972)
  *(.text.tsl9_record_queue_block_17982)
  *(.text.tsl9_record_queue_block_17988)
  tsl9_record_control_provider_1787c = tsl9_record_queue_entry_1787c;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
