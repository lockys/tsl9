OUTPUT_ARCH(riscv)
ENTRY(tsl9_flag_consumer_entry_17002)
SECTIONS
{
  .ring 0x12BC8 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_ring_insert_entry_12bc8))
    KEEP(*(.text.tsl9_ring_init_12bd0))
    KEEP(*(.text.tsl9_ring_scan_12be0))
    KEEP(*(.text.tsl9_ring_finish_12c12))
    KEEP(*(.text.tsl9_ring_advance_12c1c))
  }
  .irq 0x12C24 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_ring_irq_entry_12c24))
    KEEP(*(.text.tsl9_ring_irq_frame_12c32))
    KEEP(*(.text.tsl9_ring_irq_dispatch_12c3c))
    KEEP(*(.text.tsl9_ring_irq_finish_12c4e))
    KEEP(*(.text.tsl9_ring_irq_empty_12c54))
  }
  .spi 0x16896 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_spi_transfer_entry_16896))
    KEEP(*(.text.tsl9_spi_tx_poll_1689e))
    KEEP(*(.text.tsl9_spi_tx_ready_168a6))
    KEEP(*(.text.tsl9_spi_rx_poll_168b6))
    KEEP(*(.text.tsl9_spi_rx_done_168be))
    KEEP(*(.text.tsl9_spi_tx_wait_168c8))
    KEEP(*(.text.tsl9_spi_timeout_168d0))
    KEEP(*(.text.tsl9_spi_rx_wait_168d4))
  }
  .read 0x16994 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_register_read_entry_16994))
    KEEP(*(.text.tsl9_register_read_body))
  }
  .write 0x16A30 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_register_write_entry_16a30))
    KEEP(*(.text.tsl9_register_write_body))
  }
  .packet 0x16A7C : ALIGN(2)
  {
    KEEP(*(.text.tsl9_receive_buffer_entry_16a7c))
    KEEP(*(.text.tsl9_packet_receive_body))
    KEEP(*(.text.tsl9_packet_receive_finish_16afe))
  }
  .receiver 0x16B0A : ALIGN(2)
  {
    KEEP(*(.text.tsl9_receive_entry_16b0a))
    KEEP(*(.text.tsl9_receive_body))
  }
  .consumer 0x17002 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_flag_consumer_entry_17002))
    KEEP(*(.text.tsl9_flag_consumer_body))
  }
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
  ASSERT(SIZEOF(.irq) == 52, "Original IRQ span")
  ASSERT(SIZEOF(.provider) == 164, "Original provider span")
  ASSERT(tsl9_ring_irq_entry_12c24 == 0x12C24, "IRQ entry")
  ASSERT(tsl9_ring_irq_frame_12c32 == 0x12C32, "IRQ conditional frame")
  ASSERT(tsl9_ring_irq_dispatch_12c3c == 0x12C3C, "Provider JAL continuation")
  ASSERT(tsl9_ring_irq_finish_12c4e == 0x12C4E, "Ring JAL continuation")
  ASSERT(tsl9_ring_irq_empty_12c54 == 0x12C54, "Empty MRET")
  ASSERT(tsl9_irq_provider_18d78 == 0x18D78, "Provider entry")
  ASSERT(tsl9_irq_provider_standard_18d8a == 0x18D8A, "Provider standard")
  ASSERT(tsl9_irq_provider_common_18d92 == 0x18D92, "Provider common")
  ASSERT(tsl9_irq_provider_bank0_18dfe == 0x18DFE, "Provider bank0")
  ASSERT(tsl9_irq_provider_extended_18e08 == 0x18E08, "Provider cold path")
  ASSERT(tsl9_irq_provider_bank1_18e12 == 0x18E12, "Provider bank1")
  ASSERT(SIZEOF(.ring) == 92, "Original ring span")
  ASSERT(SIZEOF(.spi) == 72, "Original SPI span")
  ASSERT(SIZEOF(.read) == 72, "Original register-read span")
  ASSERT(SIZEOF(.write) == 76, "Original register-write span")
  ASSERT(SIZEOF(.packet) == 142, "Original packet span")
  ASSERT(SIZEOF(.receiver) == 70, "Original receiver span")
  ASSERT(SIZEOF(.consumer) == 62, "Original consumer span")
  ASSERT(tsl9_ring_insert_entry_12bc8 == 0x12BC8, "Ring entry placement")
  ASSERT(tsl9_ring_init_12bd0 == 0x12BD0, "PC-derived base placement")
  ASSERT(tsl9_ring_scan_12be0 == 0x12BE0, "Ring scan placement")
  ASSERT(tsl9_ring_finish_12c12 == 0x12C12, "Ring restore placement")
  ASSERT(tsl9_ring_advance_12c1c == 0x12C1C, "Ring advance placement")
  ASSERT(tsl9_spi_transfer_entry_16896 == 0x16896, "SPI entry placement")
  ASSERT(tsl9_register_read_entry_16994 == 0x16994, "Read entry placement")
  ASSERT(tsl9_register_write_entry_16a30 == 0x16A30, "Write entry placement")
  ASSERT(tsl9_receive_buffer_entry_16a7c == 0x16A7C, "Packet entry placement")
  ASSERT(tsl9_packet_receive_finish_16afe == 0x16AFE, "Packet ring continuation")
  ASSERT(tsl9_receive_entry_16b0a == 0x16B0A, "Receiver entry placement")
  ASSERT(tsl9_flag_consumer_entry_17002 == 0x17002, "Consumer entry placement")
}
