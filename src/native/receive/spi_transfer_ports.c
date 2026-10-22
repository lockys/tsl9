#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private SPI regions only; never execute on the host.
#endif

/* Architectural regions, not separately callable C ABI functions. The linker
 * must prove adjacency and every compressed control relocation. A source-level
 * unreachable marks the end of a region; the hardware edge is an explicit
 * branch or the documented fall-through into the next region. No readiness
 * probability, peripheral identity, IRQ behavior or hardware success is assumed.
 * C supplies constants, volatile data accesses, masks and countdown arithmetic.
 * Five compressed control instructions remain explicit architectural ports.
 * Local self-labels prevent assembler expansion; standard symbolic RVC
 * relocations name real region functions and are resolved by the linker. */
#ifdef __cplusplus
#define SPI_LINK extern "C"
#else
#define SPI_LINK
#endif
#define SPI_REGION SPI_LINK __attribute__((used, noinline, aligned(2)))

SPI_REGION uint32_t tsl9_spi_transfer_entry_16896(uint32_t input)
{
    register uint32_t count __asm__("a5") = 255;
    __asm__ volatile("" : "+r"(count) : : "memory");
    register uintptr_t base __asm__("a3") = UINT32_C(0x40013000);
    register uint32_t value __asm__("a0") = input;
    __asm__ volatile("" : "+r"(base), "+r"(value) : : "memory");
    /* Architectural fall-through to tx_poll, not a C call. */
    __builtin_unreachable();
}

SPI_REGION void tsl9_spi_tx_poll_1689e(void)
{
    register uintptr_t base __asm__("a3");
    __asm__ volatile("" : "=r"(base) : : "memory");
    register uint32_t status __asm__("a4") =
        *(volatile uint16_t *)(base + 8);
    status &= 2;
    __asm__ volatile("1: c.beqz a4, 1b\n"
                     ".reloc 1b, R_RISCV_RVC_BRANCH, tsl9_spi_tx_wait_168c8\n"
                     : "+r"(status) : : "memory");
    /* Otherwise fall through to tx_ready. */
    __builtin_unreachable();
}

SPI_REGION void tsl9_spi_tx_ready_168a6(void)
{
    register uint32_t value __asm__("a0");
    register uintptr_t base __asm__("a3");
    __asm__ volatile("" : "=r"(value), "=r"(base) : : "memory");
    value = (uint16_t)value;
    __asm__ volatile("" : "+r"(value) : : "memory");
    *(volatile uint16_t *)(base + 12) = (uint16_t)value;
    register uint32_t count __asm__("a5") = 255;
    __asm__ volatile("" : "+r"(count) : : "memory");
    base = UINT32_C(0x40013000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    /* Architectural fall-through to rx_poll. */
    __builtin_unreachable();
}

SPI_REGION void tsl9_spi_rx_poll_168b6(void)
{
    register uintptr_t base __asm__("a3");
    __asm__ volatile("" : "=r"(base) : : "memory");
    register uint32_t status __asm__("a4") =
        *(volatile uint16_t *)(base + 8);
    status &= 1;
    __asm__ volatile("1: c.beqz a4, 1b\n"
                     ".reloc 1b, R_RISCV_RVC_BRANCH, tsl9_spi_rx_wait_168d4\n"
                     : "+r"(status) : : "memory");
    /* Otherwise fall through to rx_done. */
    __builtin_unreachable();
}

SPI_REGION uint32_t tsl9_spi_rx_done_168be(void)
{
    register uintptr_t base __asm__("a3");
    __asm__ volatile("" : "=r"(base) : : "memory");
    register uint32_t value __asm__("a0") =
        *(volatile uint16_t *)(base + 12);
    value &= 255;
    __asm__ volatile("" : "+r"(value) : : "memory");
    return value;
}

SPI_REGION void tsl9_spi_tx_wait_168c8(void)
{
    register uint32_t count __asm__("a5");
    __asm__ volatile("" : "=r"(count) : : "memory");
    count = (count - 1) & 255;
    __asm__ volatile("1: c.bnez a5, 1b\n"
                     ".reloc 1b, R_RISCV_RVC_BRANCH, tsl9_spi_tx_poll_1689e\n"
                     : "+r"(count) : : "memory");
    /* Expired count falls through to timeout with physical a5 == 0. */
    __builtin_unreachable();
}

SPI_REGION uint32_t tsl9_spi_timeout_168d0(void)
{
    register uint32_t value __asm__("a0") = 0;
    __asm__ volatile("" : "+r"(value) : : "memory");
    return value;
}

SPI_REGION void tsl9_spi_rx_wait_168d4(void)
{
    register uint32_t count __asm__("a5");
    __asm__ volatile("" : "=r"(count) : : "memory");
    count = (count - 1) & 255;
    __asm__ volatile("1: c.bnez a5, 1b\n"
                     ".reloc 1b, R_RISCV_RVC_BRANCH, tsl9_spi_rx_poll_168b6\n"
                     : "+r"(count) : : "memory");
    __asm__ volatile("1: c.j 1b\n"
                     ".reloc 1b, R_RISCV_RVC_JUMP, tsl9_spi_timeout_168d0\n"
                     : : : "memory");
    __builtin_unreachable();
}
