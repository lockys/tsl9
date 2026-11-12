/* Offline event candidate; no target pointers are dereferenced. */
#include <stdint.h>

typedef struct {
    void *ctx;
    uint32_t (*read_slot)(void *ctx, uint32_t address);
    /* Nonzero only when control returned normally and s0, s1, gp and sp
       retain the values required by the caller; memory effects are opaque. */
    int (*call)(void *ctx, uint32_t target, uint32_t a0, uint32_t a1, uint32_t a2);
    void (*store)(void *ctx, uint32_t address, unsigned width, uint32_t value);
    void (*tail)(void *ctx, uint32_t target);
} candidate_hooks;

/* All hooks must be non-null. A failed call stops before any direct store. */
int candidate_12e86(const candidate_hooks *h)
{
    uint32_t target = h->read_slot(h->ctx, 0x40048u) & ~1u;
    if (!h->call(h->ctx, target, 0x2000c494u, 0u, 256u)) return 0;
    h->store(h->ctx, 0x2000c593u, 1u, 0x5au);
    h->store(h->ctx, 0x2000c494u, 4u, 0x0b431402u);
    h->store(h->ctx, 0x2000c498u, 4u, 0x0d450c44u);
    h->store(h->ctx, 0x2000c49cu, 4u, 0x2b0c2c0au);
    h->store(h->ctx, 0x2000c4a0u, 4u, 0x5f1f501eu);
    h->store(h->ctx, 0x2000c4a4u, 4u, 0x2a211e20u);
    h->tail(h->ctx, 0x12e54u);
    return 1;
}
