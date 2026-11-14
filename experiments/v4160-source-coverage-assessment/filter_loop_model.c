#include <stdint.h>
/* Bounded per-iteration event projection, not the firmware ABI.
 * The caller supplies four successfully read halfwords and current registers;
 * returned fields are events, not physical memory or provider execution. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void tsl9_filter_iteration(uint32_t sp, uint32_t s0,
    uint32_t s1, uint32_t s3, uint32_t s4, const uint16_t in[4], uint32_t out[12])
{
    unsigned i;
    out[0]=UINT32_C(0x18ba2); out[1]=sp+12u; out[2]=UINT32_C(0x1298a);
    out[3]=s0+8u; out[4]=(s1+1u)&255u;
    out[5]=s1&255u; out[6]=s4&255u; out[7]=s3;
    for (i=0;i<4;++i) out[8+i]=((uint32_t)in[i]<<5)&65535u;
}
#ifdef __cplusplus
}
#endif
