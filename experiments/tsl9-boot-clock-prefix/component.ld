/* Standalone static component only. Zero is not a hardware placement. */
ENTRY(tsl9_clock_prefix_entry)
SECTIONS
{
    . = 0;
    .text : {
        *(.text.tsl9_clock_prefix_entry)
        *(.text.tsl9_clock_prefix_body)
        *(.text.tsl9_clock_prefix_return)
    }
}
