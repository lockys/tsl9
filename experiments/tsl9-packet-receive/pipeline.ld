OUTPUT_ARCH(riscv)
SECTIONS
{
    .pipeline : ALIGN(2)
    {
        KEEP(*(.pipeline))
        KEEP(*(.text.tsl9_receive_buffer_entry_16a7c))
        KEEP(*(.text.tsl9_packet_receive_body))
        KEEP(*(.text.tsl9_packet_receive_finish_16afe))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.pipeline) == 494, "Original 352B composition plus packet142B")
    ASSERT(tsl9_flag_consumer_entry_17002 == 0, "Diagnostic partial-link origin")
    ASSERT(tsl9_flag_consumer_body == 8, "Consumer body")
    ASSERT(tsl9_receive_entry_16b0a == 62, "Receiver entry")
    ASSERT(tsl9_receive_body == 76, "Receiver body")
    ASSERT(tsl9_register_read_entry_16994 == 132, "Read entry")
    ASSERT(tsl9_register_read_body == 136, "Read body")
    ASSERT(tsl9_register_write_entry_16a30 == 204, "Write entry")
    ASSERT(tsl9_register_write_body == 208, "Write body")
    ASSERT(tsl9_spi_transfer_entry_16896 == 280, "Genuine SPI definition")
    ASSERT(tsl9_spi_tx_poll_1689e == 288, "TX poll")
    ASSERT(tsl9_spi_tx_ready_168a6 == 296, "TX ready")
    ASSERT(tsl9_spi_rx_poll_168b6 == 312, "RX poll")
    ASSERT(tsl9_spi_rx_done_168be == 320, "RX ready")
    ASSERT(tsl9_spi_tx_wait_168c8 == 330, "TX countdown")
    ASSERT(tsl9_spi_timeout_168d0 == 338, "SPI timeout")
    ASSERT(tsl9_spi_rx_wait_168d4 == 342, "RX countdown")
    ASSERT(tsl9_receive_buffer_entry_16a7c == 352, "Genuine packet definition")
    ASSERT(tsl9_packet_receive_body == 366, "Packet entry fall-through")
    ASSERT(tsl9_packet_receive_finish_16afe == 482, "Packet body fall-through")
}
