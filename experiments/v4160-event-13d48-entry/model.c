#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Abstract projection. Stubbed callee returns result and publishes the
 * post-call halfword; no physical stack, call, or memory access occurs.
 * Inputs and outputs use RV32 unsigned arithmetic. */
void event_entry_projection(uint32_t post_half, uint32_t result,
                            uint32_t sp, uint32_t ra, uint32_t out[9])
{
    post_half &= UINT32_C(0xffff);
    out[0] = post_half == UINT32_C(0xfffe) ? UINT32_C(0x13d72) : UINT32_C(0x13d68);
    out[1] = result;
    out[2] = post_half;
    out[3] = UINT32_C(0xfffe);
    out[4] = UINT32_C(0x2000c794);
    out[5] = sp - UINT32_C(16);
    out[6] = sp - UINT32_C(4);
    out[7] = ra;
    out[8] = UINT32_C(0x135e6);
}
