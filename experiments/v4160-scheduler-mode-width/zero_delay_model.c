#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* At 0x914a, selected slot index 0..14. saved contains the synthetic
 * successfully loaded stack words s0,ra,s1,s3,s4,s2, in that order.
 * This returns a projection, not actual memory writes or a resident call. */
void scheduler_zero_insert(uint32_t index, uint32_t callback,
                           uint32_t argument, uint32_t task,
                           uint32_t target, uint32_t sp,
                           const uint32_t saved[6], uint32_t out[23])
{
    uint32_t slot = UINT32_C(0x2000be08) + index * UINT32_C(12);
    uint32_t i;
    out[0] = task & UINT32_C(255);
    out[1] = (UINT32_C(1) << index) & UINT32_C(0xffff);
    out[2] = target;
    out[3] = sp + UINT32_C(32);
    for (i = 0; i < 6; ++i) out[4+i] = saved[i];
    out[10] = slot + UINT32_C(4); out[11] = 4; out[12] = callback;
    out[13] = slot; out[14] = 1; out[15] = 0;
    out[16] = slot + UINT32_C(8); out[17] = 4; out[18] = argument;
    out[19] = UINT32_C(0x40050); out[20] = target;
    out[21] = task & UINT32_C(255); out[22] = 1;
}
