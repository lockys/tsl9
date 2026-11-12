/* Informal semantic candidate, not compiled or integrated. Numeric addresses only. */
#include <stdint.h>

typedef struct {
    void *ctx;
    uint32_t (*load_slot)(void *, uint32_t);
    void (*external_call)(void *, uint32_t, uint32_t, uint32_t, uint32_t);
    uint8_t (*read_byte)(void *, uint32_t);
    void (*default_call)(void *, uint32_t, int); /* final flag: tail transfer */
} hooks;

void candidate_131c2(const hooks *h)
{
    static const uint32_t src[6] = {0x08077a00, 0x08077900, 0x08077800, 0x08077700, 0x08077600, 0x08077500};
    static const uint32_t dst[6] = {0x2000c29c, 0x2000c494, 0x2000c30c, 0x2000c594, 0x2000c694, 0x2000c40c};
    static const uint32_t len[6] = {112, 256, 256, 256, 256, 133};
    static const uint32_t fallback[6] = {0x1316a, 0x12e86, 0x12f18, 0x12f7a, 0x13084, 0x13108};
    unsigned i, j;
    for (i = 0; i < 6; ++i) {
        uint32_t target = h->load_slot(h->ctx, 0x4004c);
        h->external_call(h->ctx, target & ~UINT32_C(1), dst[i], src[i], len[i]);
        if (i == 0) {
            for (j = 0; j < 4; ++j) {
                uint8_t b = h->read_byte(h->ctx, dst[0] + 12 + j);
                if (b < 32 || b > 126) {
                    h->default_call(h->ctx, fallback[0], 0);
                    break;
                }
            }
        } else if (h->read_byte(h->ctx, dst[i] + len[i] - 1) != 0x5a) {
            h->default_call(h->ctx, fallback[i], i == 5);
            if (i == 5) return;
        }
    }
}
