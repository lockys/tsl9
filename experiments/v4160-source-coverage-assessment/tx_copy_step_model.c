/* Event projection only: caller supplies value from a successful byte read. */
#include <stdint.h>
#ifdef _WIN32
#define EXPORTED __declspec(dllexport)
#else
#define EXPORTED
#endif
#ifdef __cplusplus
extern "C" {
#endif
EXPORTED void tx_copy_step(uint32_t index, uint32_t length, uint32_t src,
                           uint32_t dst, uint32_t sum, uint32_t value,
                           uint32_t out[7]) {
    out[0] = 0x8b14u; out[1] = index; out[2] = sum;
    out[3] = out[4] = out[5] = out[6] = 0;
    if ((index & 0xffffu) < length) {
        out[0] = 0x8b0au; out[1] = index + 1u;
        out[2] = (sum + value) & 255u;
        out[3] = 1; out[4] = src + index; out[5] = dst + index + 5u;
        out[6] = value;
    }
}
#ifdef __cplusplus
}
#endif
