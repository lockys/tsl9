/* Local register/read-event projection, not a complete packet implementation.
 * loaded is the byte supplied by a successful read, when a read occurs.
 * No faults, MMIO effects, concurrency, or target ABI are modeled. */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_checksum_model(uint32_t gp, uint32_t a4, uint32_t s10,
                            uint32_t a5, uint32_t loaded, uint32_t out[3]) {
    out[0] = UINT32_C(0x8a4c);
    out[1] = 0;
    out[2] = 0;
    if (a4 != s10) return;
    out[1] = 1;
    out[2] = gp + UINT32_C(165);
    if (a5 == (loaded & UINT32_C(255))) out[0] = UINT32_C(0x8a36);
}
#ifdef __cplusplus
}
#endif
