/* Unresolved ET_REL only: no physical memory or hardware-vector-count claim. */
SECTIONS
{
  .boot_code 0 : SUBALIGN(1) { *(.boot_code) }
  .initializer 0 : SUBALIGN(1) { *(.initializer) }
  .vectors 0 : SUBALIGN(1) { *(.rodata.tsl9_original_vectors) }
}
