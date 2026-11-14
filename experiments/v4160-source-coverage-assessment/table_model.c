#include <stdint.h>

/* Bounded projection after a successful unsigned-byte load.  Table reads
 * are assumed successful; this is not a CPU emulator or a firmware entry. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) uint32_t tsl9_table_dispatch(uint32_t index, const uint8_t table[20])
{
    if (index > 4u) return UINT32_C(0x14098);
    const uint8_t *p = table + 4u * index;
    uint32_t offset = (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
                      ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
    return UINT32_C(0x1a6a4) + offset;
}
#ifdef __cplusplus
}
#endif
