#include "candidate.h"

void first_loop_167a6(uint32_t event, void *context,
                       const struct first_loop_callbacks *callbacks)
{
    unsigned offset;
    for (offset = 0; offset < 254; offset += 2) {
        const void *snapshot = callbacks->snapshot(context);
        uint8_t key = callbacks->read_byte(context, snapshot, offset);
        if ((uint32_t)key == event) {
            uint8_t value = callbacks->read_byte(context, snapshot, offset + 1);
            callbacks->dispatch(context, value);
        }
    }
}
