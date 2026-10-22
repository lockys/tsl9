/* Static component only. These addresses do not allocate physical Flash. */
ENTRY(tsl9_nv_write_frame_contract_197be)
SECTIONS
{
  . = 0;
  .text : { *(.text.*) }
}
