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
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
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
