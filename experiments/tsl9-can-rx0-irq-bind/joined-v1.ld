/* Genuine ET_REL composition; PC-derived ring address requires final original placement. */
SECTIONS
{
  .boot_code 0 : SUBALIGN(1)
  {
    *(.boot_code)
    *(.text.tsl9_ring_insert_entry_12bc8)
    *(.text.tsl9_ring_init_12bd0)
    *(.text.tsl9_ring_scan_12be0)
    *(.text.tsl9_ring_finish_12c12)
    *(.text.tsl9_ring_advance_12c1c)
    *(.text.tsl9_ring_irq_entry_12c24)
    *(.text.tsl9_ring_irq_frame_12c32)
    *(.text.tsl9_ring_irq_dispatch_12c3c)
    *(.text.tsl9_ring_irq_finish_12c4e)
    *(.text.tsl9_ring_irq_empty_12c54)
    *(.text.tsl9_irq_provider_18d78)
    *(.text.tsl9_irq_provider_standard_18d8a)
    *(.text.tsl9_irq_provider_common_18d92)
    *(.text.tsl9_irq_provider_bank0_18dfe)
    *(.text.tsl9_irq_provider_extended_18e08)
    *(.text.tsl9_irq_provider_bank1_18e12)
    tsl9_vector_entry_12c24 = tsl9_ring_irq_entry_12c24;
  }
  .initializer 0 : SUBALIGN(1) { *(.initializer) }
  .vectors 0 : SUBALIGN(1) { *(.vectors) }
}
