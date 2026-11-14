#include <stdint.h>
/* 0x12920 event projection. Inputs are then-live values after the first
 * provider returns; provider identity, memory read and call are external. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void tsl9_filter_second(uint32_t sp, uint32_t s0,
    uint32_t s1, uint32_t provider, uint32_t out[5])
{
    out[0]=provider & UINT32_C(0xfffffffe);
    out[1]=sp+UINT32_C(32);
    out[2]=s1;
    out[3]=s0>112u ? 112u : s0;
    out[4]=UINT32_C(0x1293c);
}
#ifdef __cplusplus
}
#endif
