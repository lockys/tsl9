#include <stdint.h>
/* State=3/s7=3, successful stores/read; loaded is the byte actually read
 * after the state and length writes, including any effects of aliasing. */
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
void ingress_length_high_model(uint32_t gp, uint32_t s1, uint32_t input,
                               uint32_t loaded, uint32_t *out) {
    out[0] = UINT32_C(0x897e);
    out[1] = gp + UINT32_C(156); out[2] = 4;
    out[3] = gp + UINT32_C(142); out[4] = input << 8;
    out[5] = s1; out[6] = loaded;
    out[7] = gp + UINT32_C(165); out[8] = (input + loaded) & UINT32_C(255);
}
