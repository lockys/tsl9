#include <stdint.h>
/* Event projection at callback return. Values are post-call inputs; no memory
   access or callback execution is performed here. out={pc, stored byte}. */
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void record_counter(uint32_t result, uint32_t old_byte,
                                         uint32_t threshold, uint32_t out[2]) {
    uint32_t next;
    if (result == 0u) { out[0] = 0x107eeu; out[1] = 0u; return; }
    next = (old_byte + 1u) & 255u;
    if (threshold <= next) { out[0] = 0x107fcu; out[1] = 0u; return; }
    out[0] = 0x107eeu; out[1] = next;
}
