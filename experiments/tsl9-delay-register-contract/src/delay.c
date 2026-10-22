#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error This is an offline RV32 reconstruction, not a host hardware driver.
#endif

/* Register ports only. The volatile accesses, arithmetic and loop below are C.
 * No copied instruction stream, absolute provider or target execution. */
#define DT_FIXED(reg, value) __extension__ ({ \
    register uint32_t dt_value __asm__(reg) = (uint32_t)(value); \
    __asm__ volatile("" : "+r"(dt_value) : : "memory"); dt_value; \
})

static __attribute__((always_inline)) inline uint32_t live_gp(void)
{
    register uint32_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}

static __attribute__((always_inline)) inline uint32_t zero_after_read(uint32_t *before)
{
    register uint32_t value __asm__("a4") = *before;
    register uint32_t zero __asm__("a3");
    /* Explicit ABI constant materialization, after the fresh read dependency. */
    __asm__ volatile("li %0, 0" : "=r"(zero), "+r"(value) : : "memory");
    *before = value;
    return zero;
}

static __attribute__((always_inline)) inline uint32_t outputs(
    uint32_t input, uint32_t product, uint32_t zero, uint32_t last, uint32_t base)
{
    register uint32_t a0 __asm__("a0") = input;
    register uint32_t a2 __asm__("a2") = product;
    register uint32_t a3 __asm__("a3") = zero;
    register uint32_t a4 __asm__("a4") = last;
    register uint32_t a5 __asm__("a5") = base;
    __asm__ volatile("" : "+r"(a0) : "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    return a0;
}

#define DT_READ32(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define DT_WRITE32(address, value) (*(volatile uint32_t *)(uintptr_t)(address) = (value))

#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_delay_registers_19764(uint32_t incoming_a0)
{
    const uint32_t base = DT_FIXED("a5", UINT32_C(0xe000f000));
    uint32_t value = DT_FIXED("a4", DT_READ32(base + 4u));
    const uint32_t zero = zero_after_read(&value);
    value = DT_FIXED("a4", value & UINT32_C(0xfffffffe));
    DT_WRITE32(base + 4u, value);
    value = DT_FIXED("a4", *(volatile uint8_t *)(uintptr_t)(live_gp() + 382u));
    const uint32_t product = DT_FIXED("a2", value * incoming_a0);
    DT_WRITE32(base + 16u, product);
    DT_WRITE32(base + 20u, zero);
    value = DT_FIXED("a4", DT_READ32(base));
    value = DT_FIXED("a4", value | 16u);
    DT_WRITE32(base, value);
    value = DT_FIXED("a4", DT_READ32(base));
    value = DT_FIXED("a4", value | 33u);
    DT_WRITE32(base, value);
    do {
        value = DT_FIXED("a4", DT_READ32(base + 4u));
        value = DT_FIXED("a4", value & 1u);
    } while (value == 0u);
    value = DT_FIXED("a4", DT_READ32(base));
    value = DT_FIXED("a4", value & UINT32_C(0xfffffffe));
    DT_WRITE32(base, value);
    return outputs(incoming_a0, product, zero, value, base);
}
