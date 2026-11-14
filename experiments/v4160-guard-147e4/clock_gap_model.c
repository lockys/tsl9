#include <stdint.h>

/* Successful accesses; prior is the value read before the optional write.
 * Output is an event projection, not physical memory or device behavior. */
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void clock_gap_model(uint32_t gp, uint32_t now, uint32_t prior, uint32_t *out) {
    uint32_t clear = (now - prior) > UINT32_C(299);
    out[0] = gp + UINT32_C(160); /* read address */
    out[1] = clear;
    out[2] = clear ? gp + UINT32_C(156) : 0;
    out[3] = gp + UINT32_C(160); /* timestamp write address */
    out[4] = now;
}
