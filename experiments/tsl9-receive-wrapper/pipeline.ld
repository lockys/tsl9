OUTPUT_ARCH(riscv)
SECTIONS
{
    .pipeline : ALIGN(2)
    {
        KEEP(*(.text.tsl9_flag_consumer_entry_17002))
        KEEP(*(.text.tsl9_flag_consumer_body))
        KEEP(*(.text.tsl9_receive_entry_16b0a))
        KEEP(*(.text.tsl9_receive_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.pipeline) == 132, "Expected consumer62 plus receiver70")
    ASSERT(tsl9_flag_consumer_body == tsl9_flag_consumer_entry_17002 + 8, "Consumer fall-through")
    ASSERT(tsl9_receive_entry_16b0a == tsl9_flag_consumer_entry_17002 + 62, "Actual receiver definition follows caller")
    ASSERT(tsl9_receive_body == tsl9_receive_entry_16b0a + 14, "Receiver fall-through")
}
