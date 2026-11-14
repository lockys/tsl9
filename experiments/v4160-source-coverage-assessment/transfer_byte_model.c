#include <stdint.h>
#include <stddef.h>
/* Bounded event projection of the byte path, not a firmware ABI.
 * Caller supplies mapped memory, nonwrapping in-range addresses and capacity.
 * Distinct src/dst indices may alias; reads observe prior writes. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) uint32_t tsl9_byte_transfer(uint8_t *memory,
    uint32_t src, uint32_t dst, uint32_t length)
{
    uint32_t end=dst+length;
    if (end<=dst) return 0;
    while (dst<end) { uint8_t value=memory[src]; ++src; memory[dst]=value; ++dst; }
    return length;
}
#ifdef __cplusplus
}
#endif
