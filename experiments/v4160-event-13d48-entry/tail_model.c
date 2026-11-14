#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Event projection after 0x135e6. The 0x81b0 result and following gp-relative
 * read are inputs; no physical reads, stores, calls or jumps are performed.
 * out: target, a0..a3 (only a0 defined for 0x13346), sp, ra,
 * read flag/address, write flag/address/value, call flag/target. */
void event_tail_projection(uint32_t result, uint32_t clock, uint32_t previous,
                           uint32_t gp, uint32_t sp, uint32_t ra, uint32_t out[14])
{
    unsigned i;
    for (i = 0; i < 14; ++i) out[i] = 0;
    out[5] = sp;
    out[6] = ra;
    if (result != 0) {
        out[0] = UINT32_C(0x9124);
        out[1] = UINT32_C(0x13346);
        out[3] = 100;
        return;
    }
    out[7] = 1;
    out[8] = gp + UINT32_C(344);
    out[12] = 1;
    out[13] = UINT32_C(0x81b0);
    if (clock - previous <= UINT32_C(34)) {
        out[0] = UINT32_C(0x9124);
        out[1] = UINT32_C(0x13346);
        out[3] = 35;
    } else {
        out[0] = UINT32_C(0x13346);
        out[9] = 1;
        out[10] = gp + UINT32_C(344);
        out[11] = clock;
    }
}
