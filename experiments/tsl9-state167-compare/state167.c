#include "state167.h"
uint8_t tsl9_state167_compare(uint32_t source_word, uint32_t computed_value)
{
    return (uint8_t)((source_word >> 16) == computed_value);
}
