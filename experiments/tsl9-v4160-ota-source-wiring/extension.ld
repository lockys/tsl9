/* Used together with the byte-identical historical original-image-layout.ld. */
SECTIONS {
 .text.tsl9_ota_handler_native_9c4a 0x1AC00 : {
  KEEP(*(.text.tsl9_ota_handler_native_9c4a))
 }
 ASSERT(SIZEOF(.text.tsl9_ota_handler_native_9c4a)==568, "Measured C body extent changed")
 .rodata.tsl9v4160.source_wiring_page_tail 0x1AE38 : {
  KEEP(*(.rodata.tsl9v4160.source_wiring_page_tail))
 }
 ASSERT(SIZEOF(.rodata.tsl9v4160.source_wiring_page_tail)==456, "Non-executable page packaging extent changed")
}
