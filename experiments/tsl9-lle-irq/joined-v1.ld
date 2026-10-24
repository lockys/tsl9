/* Genuine unresolved composition; final original placement remains unproved. */
SECTIONS
{
  .boot_code 0 : SUBALIGN(1)
  {
    *(.boot_code)
    *(.text.tsl9_lle_irq_entry_8498)
    *(.text.tsl9_lle_irq_callback_84d4)
    *(.text.tsl9_lle_irq_finish_84de)
    tsl9_vector_entry_8498 = tsl9_lle_irq_entry_8498;
  }
  .initializer 0 : SUBALIGN(1) { *(.initializer) }
  .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
