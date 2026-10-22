/* Nominal Runtime clock extent only; NOT an application/flash memory map. */
ENTRY(tsl9_clock_prefix_entry)
SECTIONS
{
    .clock 0x1874a : {
        KEEP(*(.text.tsl9_clock_prefix_entry))
        KEEP(*(.text.tsl9_clock_prefix_body))
    }
    ASSERT(tsl9_clock_prefix_entry == 0x1874a, "clock entry changed")
    ASSERT(tsl9_clock_prefix_body == 0x18756, "fall-through adjacency lost")
    ASSERT(SIZEOF(.clock) == 232, "reviewed extent changed")
    ASSERT(ADDR(.clock) + SIZEOF(.clock) <= 0x18834, "next-function overlap")
}
