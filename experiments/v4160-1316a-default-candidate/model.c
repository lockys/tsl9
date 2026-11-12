/* Informal event contract, not target code. See README for its domain. */
#include <stdint.h>

struct interface {
    void *ctx;
    uint32_t (*read32)(void *, uint32_t pc, uint32_t address);
    void (*store)(void *, uint32_t pc, uint32_t address, unsigned width, uint32_t value);
    /* Return zero if the opaque callee does not return normally.  The callback
       may modify the backing memory, including slots and the gp pointer. */
    int (*call)(void *, uint32_t pc, uint32_t target,
                uint32_t a0, uint32_t a1, uint32_t a2);
    /* Other argument/register values at the tail are unspecified. */
    void (*tail)(void *, uint32_t pc, uint32_t target);
};

void model_1316a(const struct interface *i, uint32_t gp)
{
    uint32_t target = i->read32(i->ctx, 0x13172u, 0x40048u);
    if (!i->call(i->ctx, 0x13188u, target & ~1u, 0x2000c29cu, 0u, 112u)) return;
    i->store(i->ctx, 0x1318eu, 0x2000c29eu, 2u, 0xfffu);
    i->store(i->ctx, 0x13194u, 0x2000c2a0u, 1u, 1u);
    i->store(i->ctx, 0x1319cu, 0x2000c2a4u, 2u, 257u);
    uint32_t ptr = i->read32(i->ctx, 0x131a4u, gp + 84u);
    target = i->read32(i->ctx, 0x131a6u, 0x4004cu);
    if (!i->call(i->ctx, 0x131b4u, target & ~1u, ptr + 12u, 0x1a69cu, 4u)) return;
    i->tail(i->ctx, 0x131beu, 0x13138u);
}
