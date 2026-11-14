/* Local RV32 length-to-state projection; no hardware write is performed. */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_length_route_model(uint32_t gp, uint32_t length, uint32_t out[3]) {
    out[0] = UINT32_C(0x89a8);
    out[1] = gp + UINT32_C(156);
    out[2] = length == 0 ? 6u : (length <= UINT32_C(1040) ? 5u : 0u);
}
#ifdef __cplusplus
}
#endif
