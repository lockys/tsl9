#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Projection after match, index 0..14, byte task. Provider assumed to return,
 * preserve saved registers and gp, and have no modeled memory effects. Output
 * records only the explicit memory/call events, not provider side effects. */
void scheduler_match_projection(uint32_t index, uint32_t old_argument,
                                uint32_t mode, uint32_t argument,
                                uint32_t task, uint32_t target,
                                uint32_t out[15])
{
    uint32_t slot = UINT32_C(0x2000be08) + index * UINT32_C(12);
    out[0] = task & UINT32_C(255);
    out[1] = UINT32_C(1) << index;
    out[2] = slot + UINT32_C(8); out[3] = old_argument;
    out[4] = old_argument != 0;
    out[5] = old_argument ? UINT32_C(0x40068) : 0;
    out[6] = old_argument ? target : 0;
    out[7] = old_argument ? old_argument : 0;
    out[8] = task & UINT32_C(255);
    out[9] = slot; out[10] = mode & UINT32_C(255);
    out[11] = slot + UINT32_C(8); out[12] = argument;
    out[13] = 1; out[14] = 4;
}
