#ifndef TSL9_STATE167_COMPARE_H
#define TSL9_STATE167_COMPARE_H
#include <stdint.h>
/* Ordinary-path comparison; callers supply synthetic or locally obtained values. */
uint8_t tsl9_state167_compare(uint32_t source_word, uint32_t computed_value);
#endif
