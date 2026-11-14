#include <stdint.h>
/* Conditional read event projection; not an ABI-compatible replacement.
 * Only meaningful when the synthetic byte load completes without a trap. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void guard_147e4(uint32_t incoming_a5, uint32_t s0,
                                       uint32_t byte_value, uint32_t *out)
{
    out[0] = UINT32_C(0x1491a); out[1] = 0; out[2] = 0; out[3] = 255;
    if (incoming_a5 != 255) return;
    out[1] = 1; out[2] = s0 + 1u; out[3] = byte_value & 255u;
    if (out[3] == incoming_a5) out[0] = UINT32_C(0x147f4);
}
#ifdef __cplusplus
}
#endif
