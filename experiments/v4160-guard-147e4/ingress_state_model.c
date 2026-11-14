/* Local 0x89f6 register and successful-read projection; not a target ABI. */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_state_model(uint32_t gp, uint32_t a4, uint32_t s9,
                         uint32_t halfword, uint32_t initial_a2, uint32_t out[5]) {
    out[0] = UINT32_C(0x8a2a);
    out[1] = 0; /* No read if state differs. */
    out[2] = 0;
    out[3] = initial_a2; /* The unequal-state path leaves a2 unchanged. */
    out[4] = a4;
    if (a4 != s9) return;
    out[1] = 1;
    out[2] = gp + UINT32_C(138);
    out[3] = halfword & UINT32_C(65535);
    out[4] = UINT32_C(1039);
    out[0] = out[3] > UINT32_C(1039) ? UINT32_C(0x8a4c) : UINT32_C(0x8a06);
}
#ifdef __cplusplus
}
#endif
