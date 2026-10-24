/* Real callback bodies only;literal constructor pointers require original placement. */
SECTIONS {
 .boot_code 0 : SUBALIGN(1) {
  *(.boot_code)
  *(.text.tsl9_rf_callbacks_entry_17476)
  *(.text.tsl9_rf_callbacks_block_1748a)
  *(.text.tsl9_rf_callbacks_block_17492)
  *(.text.tsl9_rf_callbacks_block_17494)
  *(.text.tsl9_rf_callbacks_block_17498)
  *(.text.tsl9_rf_callbacks_block_1749c)
  *(.text.tsl9_rf_callbacks_block_174a6)
  *(.text.tsl9_rf_callbacks_block_174ac)
  *(.text.tsl9_rf_callbacks_block_174b6)
  *(.text.tsl9_rf_callbacks_block_174d4)
  *(.text.tsl9_rf_callbacks_block_174da)
  *(.text.tsl9_rf_callbacks_block_174e2)
  *(.text.tsl9_rf_callbacks_block_174e8)
  *(.text.tsl9_rf_callbacks_entry_174ee)
  *(.text.tsl9_rf_callbacks_block_174f4)
  *(.text.tsl9_rf_callbacks_block_174f8)
  *(.text.tsl9_rf_callbacks_block_17504)
  *(.text.tsl9_rf_callbacks_block_17508)
  *(.text.tsl9_rf_callbacks_block_1750a)
  *(.text.tsl9_rf_callbacks_block_17512)
  *(.text.tsl9_rf_callbacks_block_17522)
  *(.text.tsl9_rf_callbacks_block_17532)
  *(.text.tsl9_rf_callbacks_block_17538)
 }
 .initializer 0 : SUBALIGN(1) { *(.initializer) }
 .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
