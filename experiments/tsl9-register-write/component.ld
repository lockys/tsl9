OUTPUT_ARCH(riscv)
SECTIONS
{
    .writer : ALIGN(2)
    {
        KEEP(*(.text.tsl9_register_write_entry_16a30))
        KEEP(*(.text.tsl9_register_write_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.writer) == 76, "Expected original 76-byte register writer")
    ASSERT(tsl9_register_write_body == tsl9_register_write_entry_16a30 + 4, "Mandatory entry/body adjacency")
}
