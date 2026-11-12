#include "leaf.h"

#ifndef B0B0_DESTINATION
#define B0B0_DESTINATION (*(volatile uint8_t *)(uintptr_t)0x2000beebu)
#endif

uint32_t v4160_b0b0_return_value(uint32_t value)
{
    B0B0_DESTINATION = (uint8_t)value;
    return value;
}
