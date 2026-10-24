/* Actual compiled decoder andsetter; diagnostic VMA zero only. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_record_decode_entry_c6a8)
  *(.text.tsl9_record_decode_block_c6b4)
  *(.text.tsl9_record_decode_block_c6c0)
  *(.text.tsl9_record_decode_block_c6e4)
  *(.text.tsl9_record_decode_block_c6ec)
  *(.text.tsl9_record_decode_block_c6f8)
  *(.text.tsl9_record_decode_block_c70e)
  *(.text.tsl9_record_decode_block_c71c)
  *(.text.tsl9_record_decode_block_c720)
  *(.text.tsl9_record_decode_block_c724)
  *(.text.tsl9_record_decode_block_c736)
  *(.text.tsl9_record_decode_block_c73c)
  *(.text.tsl9_record_decode_block_c754)
  *(.text.tsl9_record_decode_block_c762)
  *(.text.tsl9_record_decode_block_c772)
  *(.text.tsl9_record_decode_block_c774)
  *(.text.tsl9_record_decode_entry_faf8)
  tsl9_record_consumer_provider_c6a8 = tsl9_record_decode_entry_c6a8;
  tsl9_record_consumer_provider_faf8 = tsl9_record_decode_entry_faf8;
  tsl9_record_decode_provider_12a08 = tsl9_queue_external_12a08;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
