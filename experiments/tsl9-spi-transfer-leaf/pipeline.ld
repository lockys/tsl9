OUTPUT_ARCH(riscv)
SECTIONS
{
    .pipeline : ALIGN(2)
    {
        KEEP(*(.pipeline))
        KEEP(*(.text.tsl9_spi_transfer_entry_16896))
        KEEP(*(.text.tsl9_spi_tx_poll_1689e))
        KEEP(*(.text.tsl9_spi_tx_ready_168a6))
        KEEP(*(.text.tsl9_spi_rx_poll_168b6))
        KEEP(*(.text.tsl9_spi_rx_done_168be))
        KEEP(*(.text.tsl9_spi_tx_wait_168c8))
        KEEP(*(.text.tsl9_spi_timeout_168d0))
        KEEP(*(.text.tsl9_spi_rx_wait_168d4))
    }
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.pipeline) == 352, "Consumer62 receiver70 read72 write76 SPI72")
    ASSERT(tsl9_flag_consumer_entry_17002 == 0, "Diagnostic partial-link origin")
    ASSERT(tsl9_flag_consumer_body == 8, "Consumer fall-through")
    ASSERT(tsl9_receive_entry_16b0a == 62, "Receiver definition")
    ASSERT(tsl9_receive_body == 76, "Receiver fall-through")
    ASSERT(tsl9_register_read_entry_16994 == 132, "Read definition")
    ASSERT(tsl9_register_read_body == 136, "Read fall-through")
    ASSERT(tsl9_register_write_entry_16a30 == 204, "Write definition")
    ASSERT(tsl9_register_write_body == 208, "Write fall-through")
    ASSERT(tsl9_spi_transfer_entry_16896 == 280, "SPI definition")
    ASSERT(tsl9_spi_tx_poll_1689e == 288, "TX poll")
    ASSERT(tsl9_spi_tx_ready_168a6 == 296, "TX ready")
    ASSERT(tsl9_spi_rx_poll_168b6 == 312, "RX poll")
    ASSERT(tsl9_spi_rx_done_168be == 320, "RX ready")
    ASSERT(tsl9_spi_tx_wait_168c8 == 330, "TX countdown")
    ASSERT(tsl9_spi_timeout_168d0 == 338, "Shared timeout")
    ASSERT(tsl9_spi_rx_wait_168d4 == 342, "RX countdown")
}
