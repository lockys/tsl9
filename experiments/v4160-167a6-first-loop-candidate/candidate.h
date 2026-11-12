#ifndef V4160_167A6_FIRST_LOOP_CANDIDATE_H
#define V4160_167A6_FIRST_LOOP_CANDIDATE_H

#include <stdint.h>

/* All callbacks must be valid and return normally. The snapshot is opaque. */
struct first_loop_callbacks {
    const void *(*snapshot)(void *context);
    uint8_t (*read_byte)(void *context, const void *snapshot, unsigned offset);
    void (*dispatch)(void *context, uint8_t value);
};

void first_loop_167a6(uint32_t event, void *context,
                       const struct first_loop_callbacks *callbacks);

#endif
