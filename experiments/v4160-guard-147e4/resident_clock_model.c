#include <stdint.h>
/* Reference candidate projection. callback_after is counter after the stub;
 * callback_delta is its return. Caller supplies a valid output array. */
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void resident_clock_model(uint32_t pointer, uint32_t before, uint32_t callback_after,
                          uint32_t callback_delta, uint32_t *out) {
    uint32_t called = pointer != 0;
    uint32_t value = called ? callback_after + callback_delta : before;
    out[0] = called;
    out[1] = called ? pointer & ~UINT32_C(1) : 0;
    out[2] = called;
    out[3] = value;
}
