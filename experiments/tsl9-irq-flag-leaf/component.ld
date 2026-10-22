/* Nominal placement of one source-backed leaf; not a firmware memory map. */
ENTRY(tsl9_irq_flag_leaf_16fb6)
SECTIONS
{
    .irq 0x16fb6 : { KEEP(*(.text.tsl9_irq_flag_leaf_16fb6)) }
    ASSERT(tsl9_irq_flag_leaf_16fb6 == 0x16fb6, "leaf entry moved")
    ASSERT(SIZEOF(.irq) == 76, "original leaf extent changed")
    ASSERT(ADDR(.irq) + SIZEOF(.irq) == 0x17002, "leaf end moved")
}
