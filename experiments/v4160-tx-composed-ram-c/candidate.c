/* Abstract [0x8ace,0x8b14) RAM slice; see README for caller obligations. */
#include <stdint.h>
#include <limits.h>

_Static_assert(CHAR_BIT == 8, "requires octets");

struct tx_composed_result {
    uint32_t a0, a1, a2, a3, a4, a5, a6;
    uint32_t s0, s1, s3;
};

struct tx_composed_result tx_composed(volatile unsigned char ram[],
    uint32_t origin, uint32_t base_index, uint32_t source_index,
    uint32_t bank, uint32_t length, uint32_t command, uint32_t entry_a6)
{
    const uint32_t base = UINT32_C(0x2000b18c);
    uint32_t d_index = (uint32_t)((uintmax_t)base_index +
                                  (uintmax_t)bank * 1062u + 6u);
    uint32_t d = (uint32_t)((uintmax_t)base + (uintmax_t)bank * 1062u + 6u);
    uint32_t i = 0;
    uint32_t sum = (uint32_t)((uintmax_t)(length >> 8) +
                              (uintmax_t)(length & 255u) + (uintmax_t)command);
    uint32_t a6 = entry_a6;
    struct tx_composed_result out;

    ram[d_index] = 0x55u;
    ram[(uintmax_t)d_index + 1u] = 0x7fu;
    ram[(uintmax_t)d_index + 4u] = (unsigned char)length;
    ram[(uintmax_t)d_index + 3u] = (unsigned char)(length >> 8);
    ram[(uintmax_t)d_index + 2u] = (unsigned char)command;
    sum &= 255u;
    while ((i & 65535u) < length) {
        uint32_t value = ram[(uintmax_t)source_index + i];
        a6 = (uint32_t)((uintmax_t)d + i);
        sum = (uint32_t)((uintmax_t)sum + (uintmax_t)value);
        ram[(uintmax_t)d_index + i + 5u] = (unsigned char)value;
        sum &= 255u;
        i = (uint32_t)((uintmax_t)i + 1u);
    }
    out.a0 = i & 65535u; out.a1 = i; out.a2 = bank; out.a3 = base;
    out.a4 = sum; out.a5 = d; out.a6 = a6;
    out.s0 = length; out.s1 = (uint32_t)((uintmax_t)origin + source_index);
    out.s3 = command;
    return out;
}
