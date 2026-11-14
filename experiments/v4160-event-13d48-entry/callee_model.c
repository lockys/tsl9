#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Inputs are successive successful halfword/byte reads, not a snapshot.
 * This projection records events, not physical accesses or scheduler calls.
 * out: return, sp, ra, read count, six read addresses, write flag/address/
 * value, call flag/target/a0/a1/a2/a3. Input widths: 16,8,8,16,8,8. */
void event_callee_projection(uint32_t h0, uint32_t m0, uint32_t a0,
                             uint32_t h1, uint32_t m1, uint32_t a1,
                             uint32_t sp, uint32_t ra, uint32_t out[19])
{
    unsigned i, count = 0, selected = 0;
    for (i = 0; i < 19; ++i) out[i] = 0;
    out[1] = sp; out[2] = ra;
    out[4 + count++] = UINT32_C(0x2000c796);
    if (h0 != UINT32_C(0xfffe)) {
        out[4 + count++] = UINT32_C(0x2000c799);
        if (m0 != 0) {
            out[4 + count++] = UINT32_C(0x2000c798);
            selected = a0 != 0;
        }
    }
    if (!selected) {
        out[4 + count++] = UINT32_C(0x2000c79a);
        if (h1 != UINT32_C(0xfffe)) {
            out[4 + count++] = UINT32_C(0x2000c79d);
            if (m1 != 0) {
                out[4 + count++] = UINT32_C(0x2000c79c);
                selected = a1 != 0;
            }
        }
    }
    out[3] = count;
    if (selected) {
        out[0] = 1;
        out[10] = 1; out[11] = UINT32_C(0x2000c794); out[12] = 1;
        out[13] = 1; out[14] = UINT32_C(0x9124); out[15] = UINT32_C(0x1333c);
        out[17] = 300;
    }
}
