/* Genuine unresolved binding only; not final original-address placement. */
SECTIONS
{
  .boot_code 0 : SUBALIGN(1)
  {
    *(.boot_code)
    *(.text.tsl9_irq_flag_leaf_16fb6)
    tsl9_vector_entry_16fb6 = tsl9_irq_flag_leaf_16fb6;
  }
  .initializer 0 : SUBALIGN(1) { *(.initializer) }
  .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
