#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Assumes successful independent stack/pointer reads. The mode-zero provider
 * returns the supplied result; no provider or physical memory side effects
 * are modeled. saved is s0,ra,s1,s2,s3,s4. out records the projected exit,
 * restored registers, stack-read order, pointer load and optional call. */
void scheduler_resident_exit(uint32_t mode, uint32_t task, uint32_t sp,
                             const uint32_t saved[6], uint32_t target,
                             uint32_t result, uint32_t out[20])
{
    uint32_t i;
    out[0] = (mode != 0);
    out[1] = mode ? target : saved[1];
    out[2] = mode ? task : (uint32_t)(result == 0);
    out[3] = sp + UINT32_C(32);
    for (i=0; i<6; ++i) out[4+i]=saved[i];
    out[10] = sp + (mode ? UINT32_C(24) : UINT32_C(28));
    out[11] = sp + (mode ? UINT32_C(28) : UINT32_C(24));
    out[12] = sp + UINT32_C(20); out[13] = sp + UINT32_C(16);
    out[14] = sp + UINT32_C(12); out[15] = sp + UINT32_C(8);
    out[16] = mode ? UINT32_C(0x4022c) : UINT32_C(0x40058);
    out[17] = mode ? 0 : 1;
    out[18] = mode ? 0 : task;
    out[19] = mode ? 0 : UINT32_C(0x9230);
}
