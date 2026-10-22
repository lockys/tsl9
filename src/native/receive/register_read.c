#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private register-read provider only; never execute on the host.
#endif

/* RA/SP belong exclusively to architectural frame ports. Other physical
 * registers outside the C allocator bank stay reserved. SPI effects remain
 * open; the clobber list is a compiler contract, not a complete callee ABI. */
static __attribute__((always_inline)) inline void select_pin(uint32_t value)
{
    register uintptr_t base __asm__("a5") = UINT32_C(0x40011000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    register uint32_t bits __asm__("a4") = value;
    __asm__ volatile("" : "+r"(base), "+r"(bits) : : "memory");
    *(volatile uint32_t *)(base - UINT32_C(2028)) = bits;
}

static __attribute__((always_inline)) inline void transfer(uint32_t value)
{
    register uint32_t a0 __asm__("a0") = value;
    __asm__ volatile("jal ra, tsl9_spi_transfer_entry_16896\n"
                     : "+r"(a0)
                     : : "a1", "a2", "a3", "a4", "a5", "memory");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_register_read_entry_16994(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw ra, 28(sp)\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_register_read_body(void)
{
    register uint32_t channel __asm__("a0");
    __asm__ volatile("" : "=r"(channel) : : "memory");
    register uint32_t first_bit __asm__("a5") = channel & UINT32_C(1);
    __asm__ volatile("" : "+r"(channel), "+r"(first_bit) : : "memory");
    if (first_bit != 0u)
        select_pin(UINT32_C(16));

    channel &= UINT32_C(2);
    __asm__ volatile("" : "+r"(channel) : : "memory");
    if (channel != 0u)
        select_pin(UINT32_C(1));

    register uint32_t command __asm__("a0") = 3;
    __asm__ volatile("" : "+r"(command) : : "memory");
    __asm__ volatile("sw a1, 12(sp)\n" : : : "memory");
    transfer(command);

    register uint32_t address __asm__("a1");
    __asm__ volatile("lw a1, 12(sp)\n" : "=r"(address) : : "memory");
    transfer(address);
    transfer(0);

    /* Reload the actual saved slot after the last possible SPI callee. */
    __asm__ volatile("lw ra, 28(sp)\n" : : : "memory");
    register uintptr_t base __asm__("a5") = UINT32_C(0x40011000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    register uint32_t bits __asm__("a4") = UINT32_C(17);
    __asm__ volatile("" : "+r"(base), "+r"(bits) : : "memory");
    *(volatile uint32_t *)(base - UINT32_C(2032)) = bits;
    __asm__ volatile("addi sp, sp, 32\nret\n" : : : "memory");
    __builtin_unreachable();
}
