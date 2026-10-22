OUTPUT_ARCH(riscv)
SECTIONS
{
    .register_read : ALIGN(2)
    {
        KEEP(*(.text.tsl9_register_read_entry_16994))
        KEEP(*(.text.tsl9_register_read_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.register_read) == 72, "Expected original 72-byte read provider")
    ASSERT(tsl9_register_read_body == tsl9_register_read_entry_16994 + 4, "Mandatory entry/body adjacency")
}
