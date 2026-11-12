#ifndef V4160_102B2_VALUE_CANDIDATE_H
#define V4160_102B2_VALUE_CANDIDATE_H
#include <stdint.h>

struct value_event {
    uint16_t value;
    uint8_t store;
};

/* out must point to a writable, non-volatile struct value_event. */
void value_candidate(uint8_t p6, uint8_t p7, uint16_t old,
                     struct value_event *out);
#endif
