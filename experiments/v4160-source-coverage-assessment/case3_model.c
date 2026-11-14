#include <stdint.h>

/* Case 3 through 0x13ba6 to 0x14098, conditional on successful accesses,
 * a normally returning leaf and no asynchronous interference.  Records are
 * synthetic 16-bit reads. Outputs describe an event, not a physical store. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void tsl9_case3(uint32_t handle, uint32_t first,
                                     uint32_t second, uint32_t out[4])
{
    out[0] = UINT32_C(0x14098);
    out[1] = 0; /* no write */
    out[2] = 0;
    out[3] = 0;
    if (handle == first) {
        out[1] = 1;
        out[2] = UINT32_C(0x2000c799);
        out[3] = 4;
    } else if (handle == second) {
        out[1] = 1;
        out[2] = UINT32_C(0x2000c79d);
        out[3] = 4;
    }
}
#ifdef __cplusplus
}
#endif
