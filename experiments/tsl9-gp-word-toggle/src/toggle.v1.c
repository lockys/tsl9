#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 static reconstruction only; never execute on a HOST or device.
#endif

/* Original [0x9B36,0x9B4E). Its physical peripheral/purpose is unknown.
 * C owns the unsigned byte guard and volatile word read/XOR2/write.
 * Empty ports bind GP and then-live A4/A5 without extra scratch writes.
 * No frame, call, IRQ masking or atomicity is introduced.
 */
#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, aligned(2)))
void tsl9_queue_external_9b36(void)
{
    register uint32_t gp __asm__("gp");
    __asm__ volatile("" : "=r"(gp) : : "memory");

    register uint32_t a5 __asm__("a5") =
        *(volatile uint8_t *)(uintptr_t)(gp + 168u);
    __asm__ volatile("" : "+r"(a5) : : "memory");
    if (a5 != 0u)
        return;

    a5 = UINT32_C(0x40011000);
    __asm__ volatile("" : "+r"(a5) : : "memory");
    register uint32_t a4 __asm__("a4") =
        *(volatile uint32_t *)(uintptr_t)(a5 - 2036u);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) : : "memory");
    a4 ^= 2u;
    __asm__ volatile("" : "+r"(a4), "+r"(a5) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 2036u) = a4;
    __asm__ volatile("" : "+r"(a4), "+r"(a5) : : "memory");
}
