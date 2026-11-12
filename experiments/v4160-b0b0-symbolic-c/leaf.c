#include <stdint.h>
extern volatile uint8_t destination;
uint32_t candidate(uint32_t x) { destination = (uint8_t)x; return x; }
