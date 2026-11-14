#include <stdint.h>
/* Event projection for cases 0/1, not an independently callable firmware ABI.
 * Inputs first/second represent successful unsigned 16-bit record reads.
 * Callee 0x12ad0 is NOT executed; its effects and return are not established. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void tsl9_case01(uint32_t index, uint32_t handle,
    uint32_t first, uint32_t second, uint32_t out[5])
{
    uint32_t mode = index == 0 ? 0u : 3u;
    out[0] = 0; out[1] = 0; out[2] = 0;
    out[3] = UINT32_C(0x12ad0);
    out[4] = index == 0 ? 0u : 2u;
    if (handle == first) {
        out[0] = 1; out[1] = UINT32_C(0x2000c799); out[2] = mode;
    } else if (handle == second) {
        out[0] = 1; out[1] = UINT32_C(0x2000c79d); out[2] = mode;
    }
}
#ifdef __cplusplus
}
#endif
