/* Genuine unresolved composition; no final original-address or trap-ABI claim. */
SECTIONS
{
  .boot_code 0 : SUBALIGN(1)
  {
    *(.boot_code)
    *(.text.tsl9_ecall_restore_entry_8448)
    *(.text.tsl9_ecall_restore_finish_8456)
    tsl9_vector_entry_8448 = tsl9_ecall_restore_entry_8448;
  }
  .initializer 0 : SUBALIGN(1) { *(.initializer) }
  .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
