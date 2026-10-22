#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error This private RV32 IRQ component must not execute on the host.
#endif

/* Architectural live-register import only. No GP assignment or RAM snapshot. */
static __attribute__((always_inline)) inline uintptr_t live_gp(void)
{
    register uintptr_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, aligned(2))) void tsl9_irq_flag_leaf_16fb6(void)
{
    register uint32_t base __asm__("a5") = UINT32_C(0x40010000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    register uint32_t sample __asm__("a4") =
        *(volatile uint32_t *)(uintptr_t)(base + UINT32_C(1044));
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    base = (uint32_t)(base + UINT32_C(1024));
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    sample = sample & UINT32_C(64);
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    if (sample != 0u) {
        sample = UINT32_C(64);
        __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
        *(volatile uint32_t *)(uintptr_t)(base + UINT32_C(20)) = sample;
        volatile uint8_t *const flag = (volatile uint8_t *)(live_gp() + 360u);
        base = *flag;
        base = base | UINT32_C(1);
        __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
        *flag = (uint8_t)base;
        __asm__ volatile("" : : "r"(base), "r"(sample) : "memory");
    }

    /* Restore the original page base before a new status observation. Empty
     * register-bank ports constrain allocation/order without emitting work. */
    base = UINT32_C(0x40010000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    sample = *(volatile uint32_t *)(uintptr_t)(base + UINT32_C(1044));
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    base = (uint32_t)(base + UINT32_C(1024));
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    sample = sample & UINT32_C(128);
    __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
    if (sample != 0u) {
        sample = UINT32_C(128);
        __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
        *(volatile uint32_t *)(uintptr_t)(base + UINT32_C(20)) = sample;
        volatile uint8_t *const flag = (volatile uint8_t *)(live_gp() + 360u);
        base = *flag;
        base = base | UINT32_C(2);
        __asm__ volatile("" : "+r"(base), "+r"(sample) : : "memory");
        *flag = (uint8_t)base;
    }

    /* Conditional normal MRET projection, not a portable C return ABI. */
    __asm__ volatile("" : : "r"(sample), "r"(base) : "memory");
    __asm__ volatile("mret\n" : : : "memory");
    __builtin_unreachable();
}
