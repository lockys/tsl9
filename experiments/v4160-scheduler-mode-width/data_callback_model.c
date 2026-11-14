#include <stdint.h>

/* Semantic projection, not a physical memory model. Reads succeed and the
 * called function returns preserving the saved return-address stack word. */
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllexport) void scheduler_data_callback(uint32_t byte, uint32_t word,
    uint32_t gp, uint32_t pointer, uint32_t sp, uint32_t ra, uint32_t *out)
{
    uint32_t n = 0;
#define EVENT(kind, addr, size, value) do { \
    out[5 + n*4] = (kind); out[6 + n*4] = (addr); \
    out[7 + n*4] = (size); out[8 + n*4] = (value); ++n; \
} while (0)
    EVENT(1, gp + 84u, 4, pointer);
    EVENT(1, pointer + 96u, 1, byte);
    if ((byte & 192u) != 0) {
        EVENT(1, UINT32_C(0x2000bef0), 4, word);
        if (word != 0) {
            EVENT(2, sp - 4u, 4, ra);
            EVENT(2, UINT32_C(0x2000bef0), 4, 0);
            EVENT(3, UINT32_C(0x90b0), 0, UINT32_C(0xb254));
            EVENT(1, sp - 4u, 4, ra);
            out[0] = 1; out[1] = UINT32_C(0x90b0); out[2] = UINT32_C(0xb29a);
            out[3] = sp; out[4] = ra; out[33] = n;
            return;
        }
    }
    out[0] = 0; out[1] = ra; out[2] = 0;
    out[3] = sp; out[4] = ra; out[33] = n;
#undef EVENT
}
#ifdef __cplusplus
}
#endif
