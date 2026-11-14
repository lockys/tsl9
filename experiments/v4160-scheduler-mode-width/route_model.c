#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Stable synthetic +4 words; no concurrent modification. No physical reads,
 * writes or provider calls. Returns route and selected index only:
 * 0 zero-delay insert, 1 existing-key match, 2 general insert, 3 full.
 * 15 is the no-slot sentinel. A zero callback is treated as an ordinary key. */
void scheduler_route(uint32_t callback, uint32_t delay,
                     const uint32_t words[15], uint32_t out[2])
{
    uint32_t i;
    if (delay == 0) {
        for (i = 0; i < 15; ++i) {
            if (words[i] == 0) { out[0] = 0; out[1] = i; return; }
        }
    }
    for (i = 0; i < 15; ++i) {
        if (words[i] == callback) { out[0] = 1; out[1] = i; return; }
    }
    for (i = 0; i < 15; ++i) {
        if (words[i] == 0) { out[0] = 2; out[1] = i; return; }
    }
    out[0] = 3; out[1] = 15;
}
