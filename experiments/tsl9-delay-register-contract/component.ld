/* Offline layout only: address zero is not a physical allocation. */
ENTRY(tsl9_delay_registers_19764)
SECTIONS
{
  . = 0;
  .text : { *(.text.tsl9_delay_registers_19764) }
}
