#include <stdint.h>

/* Conditional successful-access event projection, not the firmware ABI.
 * index is 0..13; fields has 4 halfwords; reads has 7 independent words;
 * out has room for 18 words (address, value pairs); buffers must be valid
 * and mutually non-overlapping. No MMIO is performed. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void filter_selected(uint32_t index, const uint16_t *fields,
                                          const uint32_t *reads, uint32_t *out)
{
    uint32_t mask = 1u << index;
    uint32_t offsets[9] = {0x600u,0x61cu,0x60cu,0x640u+8u*index,
                           0x644u+8u*index,0x604u,0x614u,0x61cu,0x600u};
    uint32_t values[9] = {reads[0]|1u,reads[1]&~mask,reads[2]&~mask,
                          ((uint32_t)fields[3]<<16)|fields[1],
                          ((uint32_t)fields[2]<<16)|fields[0],
                          reads[3]|mask,reads[4]&~mask,reads[5]|mask,reads[6]&~1u};
    for (uint32_t i=0;i<9u;i++) { out[2u*i]=0x40006000u+offsets[i]; out[2u*i+1u]=values[i]; }
}
#ifdef __cplusplus
}
#endif
