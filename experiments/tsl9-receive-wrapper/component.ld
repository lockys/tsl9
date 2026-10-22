OUTPUT_ARCH(riscv)
SECTIONS
{
    .receiver : ALIGN(2)
    {
        KEEP(*(.text.tsl9_receive_entry_16b0a))
        KEEP(*(.text.tsl9_receive_body))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.receiver) == 70, "Expected original 70-byte receive wrapper")
    ASSERT(tsl9_receive_body == tsl9_receive_entry_16b0a + 14, "Mandatory entry/body adjacency")
}
