/* Host-only design: the included candidate cannot use its absolute address. */
#include <stdint.h>

/* Optional header defines HOST_B0B0_MEMORY as a host-backed array of at
 * least three volatile uint8_t elements. Never map it to the target address. */
#ifdef HOST_B0B0_STUB_HEADER
#include HOST_B0B0_STUB_HEADER
#else
static volatile uint8_t memory_stub[3];
#define HOST_B0B0_MEMORY memory_stub
#endif
#ifdef B0B0_DESTINATION
#error Do not override B0B0_DESTINATION directly in the host harness
#endif
#define B0B0_DESTINATION (HOST_B0B0_MEMORY[1])
#include "leaf.c"

static int check(uint32_t value)
{
    HOST_B0B0_MEMORY[0] = 0x5a;
    HOST_B0B0_MEMORY[1] = 0x33;
    HOST_B0B0_MEMORY[2] = 0xa5;
    v4160_b0b0(value);
    return HOST_B0B0_MEMORY[0] == 0x5a && HOST_B0B0_MEMORY[1] == (uint8_t)(value & 0xffu)
        && HOST_B0B0_MEMORY[2] == 0xa5;
}

int main(void)
{
    uint32_t i;
    for (i = 0; i < 256; ++i) {
        if (!check(i) || !check(i | UINT32_C(0x12345600)) ||
            !check(i | UINT32_C(0xffffff00))) return 1;
    }
    return 0;
}
