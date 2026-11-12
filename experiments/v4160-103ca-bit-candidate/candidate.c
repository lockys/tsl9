#include <stdint.h>

/* Abstract events, not memory accesses. p7 is the read at 0x103ca. */
struct bit_event {
    uint8_t value;
    uint8_t store;
};

struct bit_event bit_candidate(uint8_t p7, uint8_t old)
{
    struct bit_event event;
    event.value = (uint8_t)((p7 >> 1) & 1u);
    event.store = (uint8_t)(old != event.value);
    return event;
}
