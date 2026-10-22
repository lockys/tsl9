OUTPUT_ARCH(riscv)
SECTIONS
{
    .pipeline : ALIGN(2)
    {
        KEEP(*(.text.tsl9_flag_consumer_entry_17002))
        KEEP(*(.text.tsl9_flag_consumer_body))
        KEEP(*(.text.tsl9_receive_entry_16b0a))
        KEEP(*(.text.tsl9_receive_body))
        KEEP(*(.text.tsl9_register_read_entry_16994))
        KEEP(*(.text.tsl9_register_read_body))
        KEEP(*(.text.tsl9_register_write_entry_16a30))
        KEEP(*(.text.tsl9_register_write_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.pipeline) == 280, "Expected consumer62 receiver70 read72 write76")
    ASSERT(tsl9_flag_consumer_body == tsl9_flag_consumer_entry_17002 + 8, "Consumer fall-through")
    ASSERT(tsl9_receive_entry_16b0a == tsl9_flag_consumer_entry_17002 + 62, "Receiver definition follows caller")
    ASSERT(tsl9_receive_body == tsl9_receive_entry_16b0a + 14, "Receiver fall-through")
    ASSERT(tsl9_register_read_entry_16994 == tsl9_flag_consumer_entry_17002 + 132, "Read definition")
    ASSERT(tsl9_register_read_body == tsl9_register_read_entry_16994 + 4, "Read fall-through")
    ASSERT(tsl9_register_write_entry_16a30 == tsl9_flag_consumer_entry_17002 + 204, "Write definition")
    ASSERT(tsl9_register_write_body == tsl9_register_write_entry_16a30 + 4, "Write fall-through")
}
