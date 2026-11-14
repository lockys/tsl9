/* Local successful-access event projection, not an implementation of memory.
 * loaded must be the halfword read AFTER the first write; reads can alias it. */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_length_initialize_model(uint32_t gp, uint32_t s11, uint32_t a5,
                                     uint32_t loaded, uint32_t out[10]) {
    uint32_t value = (loaded & UINT32_C(65535)) | a5;
    out[0] = value;
    out[1] = gp + UINT32_C(138); out[2] = 2; out[3] = 0;
    out[4] = s11; out[5] = 2; out[6] = loaded & UINT32_C(65535);
    out[7] = gp + UINT32_C(142); out[8] = 2; out[9] = value & UINT32_C(65535);
}
#ifdef __cplusplus
}
#endif
