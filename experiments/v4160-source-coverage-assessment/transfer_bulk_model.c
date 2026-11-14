#include <stdint.h>
/* Single 36-byte bulk-step event projection, not firmware ABI. Caller ensures
 * aligned, valid, nonwrapping 36-byte ranges in a shared byte array. */
#ifdef __cplusplus
extern "C" {
#endif
static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void write32(uint8_t *p, uint32_t x) {
    p[0]=(uint8_t)x; p[1]=(uint8_t)(x>>8);
    p[2]=(uint8_t)(x>>16); p[3]=(uint8_t)(x>>24);
}
__declspec(dllexport) void tsl9_bulk_step(uint8_t *memory, uint32_t src, uint32_t dst) {
    uint32_t w[9],i;
    for (i=0;i<8;++i) w[i]=read32(memory+src+4*i);
    write32(memory+dst,w[0]);
    w[8]=read32(memory+src+32);
    for (i=1;i<9;++i) write32(memory+dst+4*i,w[i]);
}
#ifdef __cplusplus
}
#endif
