OUTPUT_ARCH(riscv)
ENTRY(tsl9_irq_provider_18d78)
SECTIONS
{
  .provider 0x18D78 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_irq_provider_18d78))
    KEEP(*(.text.tsl9_irq_provider_standard_18d8a))
    KEEP(*(.text.tsl9_irq_provider_common_18d92))
    KEEP(*(.text.tsl9_irq_provider_bank0_18dfe))
    KEEP(*(.text.tsl9_irq_provider_extended_18e08))
    KEEP(*(.text.tsl9_irq_provider_bank1_18e12))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.provider) == 164, "Original provider span")
  ASSERT(tsl9_irq_provider_standard_18d8a == 0x18D8A, "Standard path")
  ASSERT(tsl9_irq_provider_common_18d92 == 0x18D92, "Common output path")
  ASSERT(tsl9_irq_provider_bank0_18dfe == 0x18DFE, "Bank0 return path")
  ASSERT(tsl9_irq_provider_extended_18e08 == 0x18E08, "Cold path")
  ASSERT(tsl9_irq_provider_bank1_18e12 == 0x18E12, "Bank1 return path")
}
