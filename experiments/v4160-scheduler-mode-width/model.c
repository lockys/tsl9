#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Selected free slot, nonzero delay, valid index 0..14. No scan, physical
 * accesses or resident execution. out: branch PC, task, mask, scaled delay,
 * then three writes as address, width, value, followed by one read marker. */
void scheduler_selected_projection(uint32_t index, uint32_t callback,
                                   uint32_t mode, uint32_t delay,
                                   uint32_t argument, uint32_t task,
                                   uint32_t out[14])
{
    uint32_t slot = UINT32_C(0x2000be08) + index * UINT32_C(12);
    out[0] = mode == 0 ? UINT32_C(0x922c) : UINT32_C(0x91ea);
    out[1] = task & UINT32_C(0xff);
    out[2] = (UINT32_C(1) << index) & UINT32_C(0xffff);
    out[3] = (uint32_t)(delay * UINT32_C(1000)) / UINT32_C(625);
    out[4] = slot + UINT32_C(4); out[5] = 4; out[6] = callback;
    out[7] = slot; out[8] = 1; out[9] = mode & UINT32_C(0xff);
    out[10] = slot + UINT32_C(8); out[11] = 4; out[12] = argument;
    out[13] = 1; /* read gp+166 occurs after stores */
}
