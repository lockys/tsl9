#include <stdint.h>

/* Projection of the four-byte comparison only. Inputs represent successful,
 * stable reads; no memory effects, outgoing branches or calls are modeled. */
int v4160_four_byte_match(const uint8_t input[4], const uint8_t configured[4])
{
    static const uint8_t fallback[4] = { 0x41, 0x61, 0x42, 0x62 };
    unsigned i;
    for (i = 0; i < 4; ++i)
        if (input[i] != configured[i] && input[i] != fallback[i])
            return 0;
    return 1;
}
