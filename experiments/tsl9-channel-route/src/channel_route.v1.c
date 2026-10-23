#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 architectural regions only; never execute on a HOST or device.
#endif

/* Original [0x12ABE,0x12AD0). Three architectural regions, not three C ABI
 * functions. C owns argument moves and the zero constant; explicit ports
 * retain original control widths and no-link tails. Both actual providers
 * remain undefined. Do not substitute a guessed ABI or an ABS provider.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))

REGION void tsl9_queue_external_12abe(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    __asm__ volatile("" : "=r"(a0), "=r"(a1) : : "memory");
    register uint32_t a5 __asm__("a5") = a1;
    __asm__ volatile("" : "+r"(a5) : "r"(a0) : "memory");
    __asm__ volatile(".Lchannel_nonzero:\nc.bnez a0, .Lchannel_nonzero\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_channel_nonzero_12aca" : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_channel_zero_12ac2(void)
{
    register uint32_t a2 __asm__("a2");
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("" : "=r"(a2), "=r"(a5) : : "memory");
    register uint32_t a1 __asm__("a1") = a2;
    __asm__ volatile("" : "+r"(a1), "+r"(a5) : : "memory");
    register uint32_t a0 __asm__("a0") = a5;
    __asm__ volatile("" : "+r"(a0) : "r"(a1) : "memory");
    __asm__ volatile("jal zero, tsl9_channel_external_128fe" : : "r"(a0), "r"(a1) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_channel_nonzero_12aca(void)
{
    register uint32_t a3 __asm__("a3") = 0;
    __asm__ volatile("" : "+r"(a3) : : "memory");
    __asm__ volatile("jal zero, tsl9_channel_external_16cc4" : : "r"(a3) : "memory");
    __builtin_unreachable();
}
