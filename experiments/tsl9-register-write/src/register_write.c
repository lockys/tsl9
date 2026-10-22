#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private register-write component only; never execute on the host.
#endif

/* The private call port models the entire C allocator bank as volatile.
 * Reserved architectural registers and downstream resident effects do not
 * acquire an ordinary C ABI guarantee from this clobber list. */
static __attribute__((always_inline)) inline uint32_t spi_transfer(uint32_t input)
{
    register uint32_t value __asm__("a0") = input;
    __asm__ volatile("jal ra, tsl9_spi_transfer_entry_16896\n"
                     : "+r"(value) : : "a1", "a2", "a3", "a4", "a5", "memory");
    return value;
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_register_write_entry_16a30(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw ra, 28(sp)\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_register_write_body(void)
{
    register uint32_t value __asm__("a0");
    register uint32_t address __asm__("a1");
    register uint32_t data __asm__("a2");
    __asm__ volatile("" : "=r"(value), "=r"(address), "=r"(data) : : "memory");

    register uint32_t first __asm__("a5") = value & 1u;
    __asm__ volatile("" : "+r"(first), "+r"(value) : : "memory");
    if (first != 0u) {
        register uintptr_t base __asm__("a5") = UINT32_C(0x40011000);
        __asm__ volatile("" : "+r"(base) : : "memory");
        register uint32_t pins __asm__("a4") = 16;
        __asm__ volatile("" : "+r"(base), "+r"(pins) : : "memory");
        *(volatile uint32_t *)(base - 2028u) = pins;
    }

    value &= 2u;
    __asm__ volatile("" : "+r"(value) : : "memory");
    if (value != 0u) {
        register uintptr_t base __asm__("a5") = UINT32_C(0x40011000);
        __asm__ volatile("" : "+r"(base) : : "memory");
        register uint32_t pins __asm__("a4") = 1;
        __asm__ volatile("" : "+r"(base), "+r"(pins) : : "memory");
        *(volatile uint32_t *)(base - 2028u) = pins;
    }

    value = 2;
    __asm__ volatile("" : "+r"(value) : : "memory");
    __asm__ volatile("sw a2, 12(sp)\nsw a1, 8(sp)\n"
                     : : "r"(value), "r"(address), "r"(data) : "memory");
    value = spi_transfer(value);

    /* Re-read the live saved slots after each possible opaque callee. */
    __asm__ volatile("lw a1, 8(sp)\n" : "=r"(address) : : "memory");
    value = address;
    __asm__ volatile("" : "+r"(value) : : "memory");
    value = spi_transfer(value);

    __asm__ volatile("lw a2, 12(sp)\n" : "=r"(data) : : "memory");
    value = data;
    __asm__ volatile("" : "+r"(value) : : "memory");
    value = spi_transfer(value);

    __asm__ volatile("lw ra, 28(sp)\n" : : : "memory");
    register uintptr_t base __asm__("a5") = UINT32_C(0x40011000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    register uint32_t pins __asm__("a4") = 17;
    __asm__ volatile("" : "+r"(base), "+r"(pins) : : "memory");
    *(volatile uint32_t *)(base - 2032u) = pins;
    __asm__ volatile("addi sp, sp, 32\nret\n" : : "r"(value) : "memory");
    __builtin_unreachable();
}
