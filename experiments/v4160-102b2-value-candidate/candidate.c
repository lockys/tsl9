#include "candidate.h"

void value_candidate(uint8_t p6, uint8_t p7, uint16_t old,
                     struct value_event *out)
{
    uint16_t raw = (uint16_t)((uint16_t)p6 | ((uint16_t)(p7 & 1u) << 8));
    uint16_t value = raw == 0x1ffu ? 0u : raw;
    out->value = value;
    out->store = (uint8_t)(old != value);
}
