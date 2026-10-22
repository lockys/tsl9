/* Offline component only: VMA zero is not a physical allocation. */
ENTRY(tsl9_nv_read_registers_1979a)
SECTIONS
{
  . = 0;
  .text : { *(.text.tsl9_nv_read_registers_1979a) }
}
