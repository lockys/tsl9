#include <stdint.h>
#include <stdio.h>
int v4160_four_byte_match(const uint8_t input[4], const uint8_t configured[4]);
int main(void)
{
    static const uint8_t fallback[4] = {0x41, 0x61, 0x42, 0x62};
    uint8_t configured[4] = {0x10, 0x20, 0x30, 0x40}, input[4];
    unsigned mask, i, value, checks = 0;
    for (mask = 0; mask < 16; ++mask) {
        for (i = 0; i < 4; ++i) input[i] = (mask & (1u << i)) ? fallback[i] : configured[i];
        if (!v4160_four_byte_match(input, configured)) return 1;
        ++checks;
        for (i = 0; i < 4; ++i) {
            uint8_t saved = input[i];
            for (value = 0; value < 256; ++value) {
                int expected = value == fallback[i] || value == configured[i];
                input[i] = (uint8_t)value;
                if (v4160_four_byte_match(input, configured) != expected) return 2;
                ++checks;
            }
            input[i] = saved;
        }
    }
    for (i = 0; i < 4; ++i) configured[i] = input[i] = fallback[i];
    if (!v4160_four_byte_match(input, configured)) return 3;
    printf("PASS: %u mixed and per-position exhaustive cases; duplicate alternatives accepted\n", checks + 1);
    return 0;
}
