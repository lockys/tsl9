#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32-only static component; never execute on a host or device.
#endif
static __attribute__((always_inline)) inline uint32_t live_gp(void)
{
    register uint32_t gp __asm__("gp");
    __asm__ volatile("" : "=r"(gp) : : "memory");
    return gp;
}
#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_dispatch_external_821e(uint32_t index)
{
    register uint32_t incoming __asm__("a0") = index;
    __asm__ volatile("" : "+r"(incoming) : : "memory");
    register uint32_t result __asm__("a5") = live_gp() + 84u;
    __asm__ volatile("" : "+r"(result) : : "memory");
    result = *(volatile uint32_t *)(uintptr_t)result;
    __asm__ volatile("" : "+r"(result) : : "memory");
    register uint32_t condition __asm__("a4") =
        *(volatile uint8_t *)(uintptr_t)(result + 4u);
    result = 0;
    __asm__ volatile("" : "+r"(result), "+r"(condition) : : "memory");
    condition &= 8u;
    __asm__ volatile("" : "+r"(condition), "+r"(result) : : "memory");
    if (condition != 0)
        goto finish;
    condition = 2;
    __asm__ volatile("" : "+r"(condition), "+r"(result) : : "memory");
    result = 0;
    __asm__ volatile("" : "+r"(result) : "r"(condition) : "memory");
    if (incoming > condition)
        goto finish;
    result = live_gp() + 192u;
    __asm__ volatile("" : "+r"(result) : "r"(incoming), "r"(condition) : "memory");
    result += incoming;
    __asm__ volatile("" : "+r"(result) : "r"(incoming), "r"(condition) : "memory");
    result = *(volatile uint8_t *)(uintptr_t)(result + 1u);
    __asm__ volatile("" : "+r"(result) : "r"(condition) : "memory");
    result = result < 3u ? 1u : 0u;
finish:
    incoming = result;
    __asm__ volatile("" : "+r"(incoming) : "r"(result), "r"(condition) : "memory");
    return incoming;
}
