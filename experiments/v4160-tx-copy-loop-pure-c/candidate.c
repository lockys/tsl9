#include <stdint.h>

/* Preconditions and the exact entry/exit boundary are in README.md. */
struct tx_loop_registers {
    uint32_t a0, a1, a4, a6;
};

struct tx_loop_registers tx_copy_loop(volatile uint8_t ram[],
    uint32_t s0, uint32_t s1, uint32_t a5,
    uint32_t a1, uint32_t a4, uint32_t a6)
{
    struct tx_loop_registers result;
    for (;;) {
        uint32_t a0 = a1 & UINT32_C(0xffff);
        if (a0 >= s0) {
            result.a0 = a0;
            result.a1 = a1;
            result.a4 = a4;
            result.a6 = a6;
            return result;
        }
        a0 = ram[s1 + a1];
        a6 = a5 + a1;
        a1 += UINT32_C(1);
        a4 = (uint32_t)((uintmax_t)a4 + (uintmax_t)a0);
        ram[a6 + UINT32_C(5)] = (uint8_t)a0;
        a4 &= UINT32_C(255);
    }
}
