#include <stdint.h>

/* Host-only stub; include the implementation in this translation unit. */
static volatile uint8_t memory_stub[3];
#define B0B0_DESTINATION (memory_stub[1])
#include "leaf.c"

static int check(uint32_t value)
{
    uint32_t result;
    memory_stub[0] = 0x5a;
    memory_stub[1] = 0x33;
    memory_stub[2] = 0xa5;
    result = v4160_b0b0_return_value(value);
    return memory_stub[0] == 0x5a && memory_stub[1] == (uint8_t)(value & 0xffu)
        && memory_stub[2] == 0xa5 && result == value;
}

int main(void)
{
    uint32_t i;
    for (i = 0; i < 256; ++i) {
        if (!check(i) || !check(0x12345600u | i) || !check(0xffffff00u | i))
            return 1;
    }
    return 0;
}
