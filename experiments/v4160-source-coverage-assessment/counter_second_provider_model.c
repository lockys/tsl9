#include <stdint.h>
/* Event projection only: sequential entry and normal provider return assumed. */
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void counter_second_provider(uint32_t gp, uint32_t s2, uint32_t target,
                             uint32_t result, uint32_t out[7]) {
    out[0] = 0; out[1] = 0; out[2] = 0; out[3] = 0; out[4] = 0;
    out[5] = 0x8abeu; out[6] = 0;
    if (s2 == 0xfffeu) return;
    out[0] = 1; out[1] = s2; out[2] = gp + 128u;
    out[3] = target & ~1u; out[4] = 0x8ab6u;
    out[5] = result == 1u ? 0x8aceu : 0x8abeu; out[6] = 1;
}
#ifdef __cplusplus
}
#endif
