OUTPUT_ARCH(riscv)
ENTRY(tsl9_init_writes_9f4c)
SECTIONS
{
    .text 0x9f4c : ALIGN(2) { KEEP(*(.text.tsl9_init_writes_9f4c)) }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.text) == 40, "Expected complete 40-byte source leaf")
}
