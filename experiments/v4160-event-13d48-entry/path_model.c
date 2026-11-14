#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Successful synthetic reads after the callee returns. The input values are
 * independently sampled at each named address, not an atomic snapshot.
 * out: pc, a0, sp, ra, read count, then up to four read addresses. */
void event_paths_projection(uint32_t h0, uint32_t m0, uint32_t h1,
                            uint32_t m1, uint32_t result, uint32_t sp,
                            uint32_t incoming_ra, uint32_t out[9])
{
    uint32_t count = 0, direct = 0;
    unsigned i;
    for (i = 0; i < 9; ++i) out[i] = 0;
    out[5 + count++] = UINT32_C(0x2000c796);
    if (h0 != UINT32_C(0xfffe)) {
        out[5 + count++] = UINT32_C(0x2000c799);
        if (m0 == 0) goto continuation;
    }
    out[5 + count++] = UINT32_C(0x2000c79a);
    if (h1 == UINT32_C(0xfffe)) direct = 1;
    else {
        out[5 + count++] = UINT32_C(0x2000c79d);
        direct = m1 != 0;
    }
continuation:
    out[0] = direct ? incoming_ra : (result == 0 ? UINT32_C(0x13da2) : UINT32_C(0x13d8a));
    out[1] = result;
    out[2] = direct ? sp : sp - UINT32_C(16);
    out[3] = direct ? incoming_ra : UINT32_C(0x13d50);
    out[4] = count;
}
