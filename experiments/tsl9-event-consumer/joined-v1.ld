/* Diagnostic composition only; original placement/ROM/IRQ/OTA unproved. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_event_consumer_entry_17666)
  *(.text.tsl9_event_consumer_block_1767e)
  *(.text.tsl9_event_consumer_block_17680)
  *(.text.tsl9_event_consumer_block_17686)
  *(.text.tsl9_event_consumer_block_17692)
  *(.text.tsl9_event_consumer_block_17698)
  *(.text.tsl9_event_consumer_entry_176a0)
  *(.text.tsl9_event_consumer_block_176c8)
  *(.text.tsl9_event_consumer_block_176ca)
  *(.text.tsl9_event_consumer_block_176de)
  *(.text.tsl9_event_consumer_block_176f2)
  *(.text.tsl9_event_consumer_entry_176f8)
  *(.text.tsl9_event_consumer_block_1770c)
  *(.text.tsl9_event_consumer_block_1771e)
  *(.text.tsl9_event_consumer_block_17744)
  *(.text.tsl9_event_consumer_block_17746)
  *(.text.tsl9_event_consumer_block_17764)
  *(.text.tsl9_event_consumer_block_17768)
  *(.text.tsl9_event_consumer_block_17776)
  *(.text.tsl9_event_consumer_block_17780)
  *(.text.tsl9_event_consumer_block_177a2)
  *(.text.tsl9_event_consumer_block_177a8)
  *(.text.tsl9_event_consumer_block_177b2)
  *(.text.tsl9_event_consumer_block_177c4)
  *(.text.tsl9_event_consumer_block_177cc)
  *(.text.tsl9_event_consumer_block_177dc)
  *(.text.tsl9_event_consumer_block_177e2)
  *(.text.tsl9_event_consumer_block_177e8)
  *(.text.tsl9_event_consumer_block_177ee)
  *(.text.tsl9_event_consumer_block_177f8)
  *(.text.tsl9_event_consumer_block_17806)
  *(.text.tsl9_event_consumer_block_17816)
  *(.text.tsl9_event_consumer_block_17826)
  *(.text.tsl9_event_consumer_block_17830)
  *(.text.tsl9_event_consumer_block_17832)
  tsl9_record_queue_provider_17666 = tsl9_event_consumer_entry_17666;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
