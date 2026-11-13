#include <stdint.h>

uint32_t candidate_18e90_direct(uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)0x4002200c = value;
    return value;
}
