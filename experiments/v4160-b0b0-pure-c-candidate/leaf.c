#include <stdint.h>

/* Override only for a host test with a volatile uint8_t lvalue. */
#ifndef B0B0_DESTINATION
#define B0B0_DESTINATION (*(volatile uint8_t *)(uintptr_t)0x2000beebu)
#endif

void v4160_b0b0(uint32_t value)
{
    B0B0_DESTINATION = (uint8_t)value;
}
