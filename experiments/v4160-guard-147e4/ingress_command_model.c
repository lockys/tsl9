#include <stdint.h>
/* State=2, s6=2; loaded is the byte read after preceding two writes.
 * Event projection assumes successful access and no concurrent changes. */
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_command_model(uint32_t gp, uint32_t s1, uint32_t command,
                           uint32_t loaded, uint32_t *out) {
    out[0] = UINT32_C(0x897e);
    out[1] = gp + UINT32_C(156); out[2] = 3;
    out[3] = gp + UINT32_C(164); out[4] = command;
    out[5] = s1; out[6] = loaded;
    out[7] = gp + UINT32_C(165); out[8] = (command + loaded) & UINT32_C(255);
}
