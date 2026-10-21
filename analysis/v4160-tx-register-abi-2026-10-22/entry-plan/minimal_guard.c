#include <stdint.h>

/* Compiler diagnostic only. Neither target function is executed. */
#ifdef __cplusplus
extern "C" {
#endif

__attribute__((noinline))
uint32_t probe_guard_memory(uint32_t result, uint32_t address, uint32_t unused, uint32_t length)
{
    register uint32_t limit __asm__("a5") = 1039u;
    (void)unused;
    __asm__ volatile("" : "+r"(limit) : : "memory");
    if (length > limit) return result;
    {
        register uint32_t saved __asm__("s0") = length;
        __asm__ volatile("" : "+r"(saved) : : "memory");
        *(volatile uint32_t *)(uintptr_t)address = saved;
    }
    return result;
}

__attribute__((noinline))
uint32_t probe_guard_register_only(uint32_t result, uint32_t address, uint32_t unused, uint32_t length)
{
    register uint32_t limit __asm__("a5") = 1039u;
    (void)unused;
    __asm__ volatile("" : "+r"(limit));
    if (length > limit) return result;
    {
        register uint32_t saved __asm__("s0") = length;
        __asm__ volatile("" : "+r"(saved) : : "memory");
        *(volatile uint32_t *)(uintptr_t)address = saved;
    }
    return result;
}

#ifdef __cplusplus
}
#endif
