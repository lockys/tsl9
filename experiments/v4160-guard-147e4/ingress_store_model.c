#include <stdint.h>

/* Event projection only: successful accesses, no trap or implicit provider
 * effects. loaded_length is supplied AFTER the two recorded writes; caller
 * must account for aliasing or other changes when choosing it. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void ingress_store_model(uint32_t gp, uint32_t index,
                                               uint32_t byte_value,
                                               uint32_t loaded_length,
                                               uint32_t *out)
{
    unsigned i;
    for (i = 0; i < 9; ++i) out[i] = 0;
    if (index > UINT32_C(1039)) {
        out[0] = UINT32_C(0x8a4c);
        return;
    }
    out[0] = index + 1u < (loaded_length & UINT32_C(0xffff))
        ? UINT32_C(0x89a8) : UINT32_C(0x89dc);
    out[1] = 2;
    out[2] = gp + UINT32_C(138); out[3] = 2; out[4] = index + 1u;
    out[5] = UINT32_C(0x2000b9d8) + index; out[6] = 1; out[7] = byte_value & UINT32_C(255);
    out[8] = gp + UINT32_C(142);
}
#ifdef __cplusplus
}
#endif
