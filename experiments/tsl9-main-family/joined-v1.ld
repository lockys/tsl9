/* Real original regions only; not final original-PC placement. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_main_family_entry_8180)
  *(.text.tsl9_main_family_block_8198)
  *(.text.tsl9_main_family_block_819e)
  *(.text.tsl9_main_family_block_81a2)
  *(.text.tsl9_main_family_block_81a6)
  *(.text.tsl9_main_family_entry_9008)
  *(.text.tsl9_main_family_block_900e)
  *(.text.tsl9_main_family_block_9012)
  *(.text.tsl9_main_family_entry_9250)
  *(.text.tsl9_main_family_block_9258)
  *(.text.tsl9_main_family_block_925c)
  *(.text.tsl9_main_family_block_9260)
  *(.text.tsl9_main_family_block_9264)
  *(.text.tsl9_main_family_block_9268)
  *(.text.tsl9_main_family_block_926a)
  *(.text.tsl9_main_family_block_926e)
  *(.text.tsl9_main_family_block_9270)
  *(.text.tsl9_main_family_block_9274)
  *(.text.tsl9_main_family_block_9278)
  *(.text.tsl9_main_family_block_927c)
  *(.text.tsl9_main_family_block_9280)
  *(.text.tsl9_main_family_block_9284)
  *(.text.tsl9_main_family_block_9288)
  *(.text.tsl9_init_writes_9f4c)
  tsl9_boot_main_9008 = tsl9_main_family_entry_9008;
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
