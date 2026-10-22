OUTPUT_ARCH(riscv)
ENTRY(tsl9_spi_transfer_entry_16896)
SECTIONS
{
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
    /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
    ASSERT(SIZEOF(.spi) == 72, "Exact SPI leaf footprint")
    ASSERT(tsl9_spi_transfer_entry_16896 == 0x16896, "Entry")
    ASSERT(tsl9_spi_tx_poll_1689e == 0x1689e, "TX polling fall-through")
    ASSERT(tsl9_spi_tx_ready_168a6 == 0x168a6, "TX ready fall-through")
    ASSERT(tsl9_spi_rx_poll_168b6 == 0x168b6, "RX polling fall-through")
    ASSERT(tsl9_spi_rx_done_168be == 0x168be, "RX ready fall-through")
    ASSERT(tsl9_spi_tx_wait_168c8 == 0x168c8, "TX countdown")
    ASSERT(tsl9_spi_timeout_168d0 == 0x168d0, "Shared timeout")
    ASSERT(tsl9_spi_rx_wait_168d4 == 0x168d4, "RX countdown")
}
