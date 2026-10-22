OUTPUT_ARCH(riscv)
SECTIONS
{
  .irq : ALIGN(2)
  {
    KEEP(*(.text.tsl9_ring_irq_entry_12c24))
    KEEP(*(.text.tsl9_ring_irq_frame_12c32))
    KEEP(*(.text.tsl9_ring_irq_dispatch_12c3c))
    KEEP(*(.text.tsl9_ring_irq_finish_12c4e))
    KEEP(*(.text.tsl9_ring_irq_empty_12c54))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.irq) == 52, "Bounded original interrupt adapter")
  ASSERT(tsl9_ring_irq_entry_12c24 == 0, "Diagnostic ET_REL origin")
  ASSERT(tsl9_ring_irq_frame_12c32 == 14, "Conditional frame")
  ASSERT(tsl9_ring_irq_dispatch_12c3c == 24, "Then-live provider return")
  ASSERT(tsl9_ring_irq_finish_12c4e == 42, "Ring return and MRET")
  ASSERT(tsl9_ring_irq_empty_12c54 == 48, "Empty status MRET")
}
