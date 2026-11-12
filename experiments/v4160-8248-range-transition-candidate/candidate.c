#include <stdint.h>

/* Abstract observations, not an ABI or the helper's return value. */
typedef struct {
    uint8_t store;          /* 0: no store, 1: store value below */
    uint8_t value;
    uint8_t call_d052;
    uint8_t tail_167a6;
    uint32_t event_argument;
} transition_8248;

/* d052_result is the independently observed full register value after return.
 * Effects of either external call on memory and registers are not represented. */
transition_8248 candidate_8248(uint32_t x, uint32_t lower, uint32_t upper,
                               uint8_t old, uint32_t event_argument,
                               uint32_t d052_result)
{
    transition_8248 r = {0, 0, 0, 0, 0};
    if (x < lower || upper < x) {
        if (old != 0) { r.store = 1; r.value = 0; }
    } else if (old == 0) {
        r.store = 1;
        r.value = 1;
        r.call_d052 = 1;
        if (d052_result == 4) {
            r.tail_167a6 = 1;
            r.event_argument = event_argument;
        }
    }
    return r;
}
