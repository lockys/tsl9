#include "dispatch2.h"
int tsl9_dispatch2_model(uint32_t entry, uint32_t command, uint8_t state_byte,
                         tsl9_dispatch2_result *out)
{
    uint32_t read_state = 0;
    if (out == 0 || (entry != 0x14230u && entry != 0x1425eu)) return 0;
    out->destination = TSL9_AT_141FA;
    out->state_read_requested = 0;
    out->scheduler_requested = 0;
    out->scheduler_callback = 0;
    out->scheduler_delay = 0;
    if (entry == 0x14230u) {
        read_state = (((command + 86u) & 255u) <= 1u);
    } else if (command > 193u) {
        if (command == 208u) read_state = 1;
        else out->destination = TSL9_AT_141F6;
    } else if (command >= 192u) {
        read_state = 1;
    } else {
        read_state = (((command + 71u) & 255u) <= 2u);
    }
    if (read_state) {
        out->state_read_requested = 1;
        if (state_byte == 0u) {
            out->scheduler_requested = 1;
            out->scheduler_callback = 0x13f88u;
            out->scheduler_delay = 300u;
            out->destination = TSL9_AT_14098;
        }
    }
    return 1;
}
