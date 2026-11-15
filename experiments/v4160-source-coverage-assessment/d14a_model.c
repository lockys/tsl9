/* Offline semantic model only. Callbacks represent successful byte accesses;
 * the caller supplies stable ordinary memory and receives the access order.
 * No target ABI, CPU, traps, asynchronous writes, or tail callee is modeled. */
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint8_t (*d14a_read)(void *, uint32_t);
typedef void (*d14a_write)(void *, uint32_t, uint8_t);

#if defined(_WIN32)
__declspec(dllexport)
#endif
uint32_t d14a_model(void *ctx, d14a_read read_byte, d14a_write write_byte,
                    uint32_t p, uint32_t gp)
{
    const uint8_t a = read_byte(ctx, p + 3u);
    const uint8_t old = read_byte(ctx, gp + 232u);
    const uint8_t b = read_byte(ctx, p + 5u);
    const uint8_t c = read_byte(ctx, p + 7u);
    const uint8_t d = read_byte(ctx, p + 9u);
    if (old != a || read_byte(ctx, gp + 233u) != b ||
        read_byte(ctx, gp + 234u) != c || read_byte(ctx, gp + 235u) != d) {
        write_byte(ctx, gp + 232u, a);
        write_byte(ctx, gp + 233u, b);
        write_byte(ctx, gp + 234u, c);
        write_byte(ctx, gp + 235u, d);
        return 0x13c4eu;
    }
    return 0u; /* sentinel for return, not the actual return address */
}
#ifdef __cplusplus
}
#endif
