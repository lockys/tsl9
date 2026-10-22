#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 register contract only; never execute on the host.
#endif

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline)) void tsl9_init_writes_9f4c(void)
{
    /* Empty register ports preserve the original first three instruction
     * boundaries: form A4 high bits, then A5 base, then finish A4.
     * The ports emit no instructions and perform no MMIO access. */
    register uint32_t first_high __asm__("a4") = UINT32_C(0x5000);
    __asm__ volatile("" : "+r"(first_high) : : "memory");
    register uint32_t base __asm__("a5") = UINT32_C(0x40003000);
    __asm__ volatile("" : "+r"(first_high), "+r"(base) : : "memory");
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)base;
    registers[0] = (uint32_t)(first_high + UINT32_C(0x555));
    registers[1] = UINT32_C(3);
    registers[2] = UINT32_C(1500);
    registers[0] = UINT32_C(0xaaaa);
    registers[0] = UINT32_C(0xcccc);

    /* Preserve the original private normal-exit register values. */
    register uint32_t a4 __asm__("a4") = UINT32_C(0xcccc);
    register uint32_t a5 __asm__("a5") = base;
    __asm__ volatile("" : : "r"(a4), "r"(a5) : "memory");
}
