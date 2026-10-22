OUTPUT_ARCH(riscv)
SECTIONS
{
    .consumer : ALIGN(2)
    {
        KEEP(*(.text.tsl9_flag_consumer_entry_17002))
        KEEP(*(.text.tsl9_flag_consumer_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.consumer) == 62, "Expected complete 62-byte caller")
    ASSERT(tsl9_flag_consumer_body == tsl9_flag_consumer_entry_17002 + 8, "Mandatory entry/body adjacency")
}
