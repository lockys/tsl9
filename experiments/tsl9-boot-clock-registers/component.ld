/* Static standalone component. VMA zero is not a physical allocation. */
ENTRY(tsl9_boot_clock_registers_2c78)
SECTIONS
{
    . = 0;
    .text : { *(.text.tsl9_boot_clock_registers_2c78) }
}
