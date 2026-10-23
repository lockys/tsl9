#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 static component only; do not execute on a HOST or device.
#endif

/* Ports bind live physical registers; every algorithm/access below is C.
 * The empty strings contain no copied opcodes or executable algorithms. */
static __attribute__((always_inline)) inline uint32_t live_gp(void)
{
    register uint32_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}

static __attribute__((always_inline)) inline uint32_t fixed_a5(uint32_t input)
{
    register uint32_t value __asm__("a5") = input;
    __asm__ volatile("" : "+r"(value) : : "memory");
    return value;
}

#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_queue_status_81aa(void)
{
    /* ID2966 V4.1.60: GP+167, not the older firmware's GP+175. */
    return *(volatile uint8_t *)(uintptr_t)(live_gp() + 167u);
}

#ifdef __cplusplus
extern "C"
#endif
void tsl9_queue_clear_820c(uint32_t index)
{
    register uint32_t incoming __asm__("a0") = index;
    __asm__ volatile("" : "+r"(incoming) : : "memory");
    const uint32_t maximum = fixed_a5(2u);
    if (incoming <= maximum) {
        uint32_t address = fixed_a5(live_gp() + 192u);
        address = fixed_a5(address + incoming);
        *(volatile uint8_t *)(uintptr_t)(address + 1u) = 0;
    }
    /* The original void helper preserves incoming A0 on every normal path. */
    __asm__ volatile("" : : "r"(incoming) : "memory");
}
