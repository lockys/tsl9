/* Genuine compiled regions and true aliases; diagnostic VMA zero only. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_record_consumer_entry_c776)
  *(.text.tsl9_record_consumer_block_c78a)
  *(.text.tsl9_record_consumer_entry_c798)
  *(.text.tsl9_record_consumer_entry_c7aa)
  *(.text.tsl9_record_consumer_block_c7b4)
  *(.text.tsl9_record_consumer_block_c7bc)
  *(.text.tsl9_record_consumer_block_c7ca)
  *(.text.tsl9_record_consumer_block_c7d4)
  *(.text.tsl9_record_consumer_block_c7da)
  *(.text.tsl9_record_consumer_block_c7e0)
  *(.text.tsl9_record_consumer_block_c7e6)
  *(.state_read_code)
  *(.text.tsl9_queue_external_12a08)
  *(.text.tsl9_dispatch_status_12a14)
  *(.text.tsl9_dispatch_ID_12a16)
  *(.text.tsl9_dispatch_query_12a20)
  *(.text.tsl9_dispatch_tag_12a28)
  *(.text.tsl9_dispatch_copy_12a2e)
  *(.text.tsl9_dispatch_peripheral_12a50)
  *(.text.tsl9_dispatch_finish_12a5e)
  *(.text.tsl9_dispatch_tagged_12a66)
  tsl9_event_consumer_provider_c776 = tsl9_record_consumer_entry_c776;
  tsl9_record_consumer_provider_82a8 = tsl9_feature_external_82a8;
  tsl9_record_consumer_provider_12a08 = tsl9_queue_external_12a08;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
