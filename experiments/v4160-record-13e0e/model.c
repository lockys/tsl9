#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Output: read count, first/second read addresses, write count,
 * first address/value, second address/value. Successful stable accesses only. */
void record_update_a1_one(uint32_t handle, uint16_t first, uint16_t second,
                          uint32_t out[8])
{
    unsigned i;
    for (i = 0; i < 8; ++i) out[i] = 0;
    out[0] = 1;
    out[1] = UINT32_C(0x2000c796);
    if (handle == (uint32_t)first) {
        out[3] = 2;
        out[4] = UINT32_C(0x2000c798);
    } else {
        out[0] = 2;
        out[2] = UINT32_C(0x2000c79a);
        if (handle == (uint32_t)second) {
            out[3] = 2;
            out[4] = UINT32_C(0x2000c79c);
        }
    }
    if (out[3]) {
        out[5] = 1;
        out[6] = out[4] + 1;
        out[7] = 0;
    }
}

#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Precondition: mode != 1. out: read count, two read addresses, write
 * count, then three (address, width, value) events. No physical access. */
void record_update_other(uint32_t handle, uint32_t mode, uint16_t first,
                         uint16_t second, uint32_t out[13])
{
    uint32_t slot = 0;
    unsigned i;
    for (i = 0; i < 13; ++i) out[i] = 0;
    out[0] = 1;
    out[1] = UINT32_C(0x2000c796);
    if ((mode == 2 && first == UINT16_C(0xfffe)) ||
        (mode != 2 && handle == (uint32_t)first)) {
        slot = out[1];
    } else {
        out[0] = 2;
        out[2] = UINT32_C(0x2000c79a);
        if ((mode == 2 && second == UINT16_C(0xfffe)) ||
            (mode != 2 && handle == (uint32_t)second)) slot = out[2];
    }
    if (slot) {
        out[3] = 3;
        out[4] = slot;
        out[5] = 2;
        out[6] = mode == 2 ? (handle & UINT32_C(0xffff)) : UINT32_C(0xfffe);
        out[7] = slot + 2;
        out[8] = 1;
        out[10] = slot + 3;
        out[11] = 1;
    }
}
