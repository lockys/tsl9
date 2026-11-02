#include "dispatch2.h"
int tsl9_dispatch2_model(uint32_t entry, uint32_t command, uint32_t queue_result,
                         tsl9_dispatch2_result *out)
{
    uint32_t seek_queue = 0;
    if (out == 0 || (entry != 0x14230u && entry != 0x1425eu)) return 0;
    out->destination = TSL9_AT_141FA;
    out->queue_requested = 0;
    out->scheduler_requested = 0;
    out->scheduler_callback = 0;
    out->scheduler_delay = 0;
    if (entry == 0x14230u) {
        seek_queue = (((command + 86u) & 255u) <= 1u);
    } else if (command > 193u) {
        if (command == 208u) seek_queue = 1;
        else out->destination = TSL9_AT_141F6;
    } else if (command >= 192u) {
        seek_queue = 1;
    } else {
        seek_queue = (((command + 71u) & 255u) <= 2u);
    }
    if (seek_queue) {
        out->queue_requested = 1;
        if (queue_result == 0u) {
            out->scheduler_requested = 1;
            out->scheduler_callback = 0x13f88u;
            out->scheduler_delay = 300u;
            out->destination = TSL9_AT_14098;
        }
    }
    return 1;
}
