#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Projection assumes each of the first three calls returns normally and the
 * last supplies queue_status in a0. No real calls or stack stores occur.
 * out: exit kind (0=return,1=tail), restored sp, three call targets,
 * first a0, second a0, tail a0..a3 and tail target (zero on return). */
void callback_projection(uint32_t queue_status, uint32_t sp, uint32_t out[12])
{
    unsigned i;
    for (i = 0; i < 12; ++i) out[i] = 0;
    out[1] = sp;
    out[2] = UINT32_C(0x90b0);
    out[3] = UINT32_C(0x13d48);
    out[4] = UINT32_C(0x81aa);
    out[5] = UINT32_C(0x13dd4);
    if (queue_status == 0) {
        out[0] = 1;
        out[7] = UINT32_C(0x13f88);
        out[9] = 300;
        out[11] = UINT32_C(0x9124);
    }
}
