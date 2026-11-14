/* Host-only projection; not a port at the original address. */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
uint32_t callback_b0d0(uint32_t flag, uint8_t counters[3])
{
    if ((flag & 1u) == 0u) return 0u;
    for (unsigned i = 0; i < 3u; ++i) {
        if (counters[i] <= 2u) counters[i]++;
    }
    return flag ^ 1u;
}
#ifdef __cplusplus
}
#endif
