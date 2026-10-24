/* Diagnostic composition only;original placement/ROM/IRQ/OTA unproved. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_resident_providers_entry_1753a)
  *(.text.tsl9_resident_providers_block_17546)
  *(.text.tsl9_resident_providers_block_175b0)
  *(.text.tsl9_resident_providers_block_175b8)
  *(.text.tsl9_resident_providers_block_175ca)
  *(.text.tsl9_resident_providers_block_175d8)
  *(.text.tsl9_resident_providers_block_175e4)
  *(.text.tsl9_resident_providers_entry_175e8)
  *(.text.tsl9_resident_providers_block_17608)
  *(.text.tsl9_resident_providers_block_17616)
  *(.text.tsl9_resident_providers_block_17626)
  *(.text.tsl9_resident_providers_block_1765c)
  tsl9_event_consumer_provider_1753a = tsl9_resident_providers_entry_1753a;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
