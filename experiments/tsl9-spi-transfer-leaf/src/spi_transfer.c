#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private SPI leaf only; never execute on the host.
#endif

/* Offline source candidate for nominal VA 0x16896.  Peripheral identity and
 * live hardware behavior remain unproved. Empty ports preserve the physical
 * register interface. Branch hints request code placement only; they assert
 * no hardware-ready probability. Polling, masks, countdowns and data remain C. */
#ifdef __cplusplus
extern "C"
#endif
__attribute__((noinline, used))
uint32_t tsl9_spi_transfer_entry_16896(uint32_t input)
{
    register uint32_t value __asm__("a0") = input;
    register uint32_t count __asm__("a5") = 255;
    __asm__ volatile ("" : "+r"(count) : : "memory");
    register uintptr_t base __asm__("a3") = UINT32_C(0x40013000);
    __asm__ volatile ("" : "+r"(base), "+r"(value) : : "memory");
    register uint32_t status __asm__("a4");

poll_write:
    status = *(volatile uint16_t *)(base + 8);
    status &= 2;
    __asm__ volatile ("" : "+r"(status) : : "memory");
    if (__builtin_expect_with_probability(status == 0u, 0, 1.0))
        goto wait_write;

    value = (uint16_t)value;
    __asm__ volatile ("" : "+r"(value) : : "memory");
    *(volatile uint16_t *)(base + 12) = (uint16_t)value;

    count = 255;
    __asm__ volatile ("" : "+r"(count) : : "memory");
    base = UINT32_C(0x40013000);
    __asm__ volatile ("" : "+r"(base) : : "memory");
poll_read:
    status = *(volatile uint16_t *)(base + 8);
    status &= 1;
    __asm__ volatile ("" : "+r"(status) : : "memory");
    if (__builtin_expect_with_probability(status == 0u, 0, 1.0))
        goto wait_read;
    value = *(volatile uint16_t *)(base + 12);
    value &= 255;
    __asm__ volatile ("" : "+r"(value), "+r"(base), "=r"(status), "+r"(count) : : "memory");
    return value;

wait_write:
    count = (count - 1) & 255;
    __asm__ volatile ("" : "+r"(count) : : "memory");
    if (count != 0)
        goto poll_write;

timeout:
    value = 0;
    __asm__ volatile ("" : "+r"(value), "+r"(base), "=r"(status), "=r"(count) : : "memory");
    return value;

wait_read:
    count = (count - 1) & 255;
    __asm__ volatile ("" : "+r"(count) : : "memory");
    if (count != 0)
        goto poll_read;
    goto timeout;
}
