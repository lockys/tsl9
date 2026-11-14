#include <stdint.h>
/* Event projection only: two successful bytes, stable state/gp, no traps or
 * intervening writes. out carries exit PC, write count, address/value pairs. */
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_prefix_model(uint32_t gp, uint32_t first, uint32_t second, uint32_t *out) {
    out[0] = UINT32_C(0x8a4c); out[1] = 0;
    out[2] = 0; out[3] = 0; out[4] = 0; out[5] = 0; out[6] = 0; out[7] = 0;
    if (first != UINT32_C(0x55)) return;
    out[1] = 1; out[2] = gp + UINT32_C(156); out[3] = 1;
    if (second != UINT32_C(0x7f)) return;
    out[0] = UINT32_C(0x897e); out[1] = 3;
    out[4] = gp + UINT32_C(156); out[5] = 2;
    out[6] = gp + UINT32_C(165); out[7] = 0;
}
