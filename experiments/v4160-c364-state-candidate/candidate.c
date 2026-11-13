#include "candidate.h"

void c364_candidate(const c364_bus *bus, uint32_t entry_value)
{
    uint32_t s0 = C364_INITIAL_S0;
    uint8_t flag;
    (void)entry_value; /* The observed sequence overwrites a0 before each call. */
    flag = bus->read8(bus->ctx, C364_BF10);
    if (flag != 0)
        bus->call(bus->ctx, UINT32_C(0xef76), 0, &s0);
    flag = bus->read8(bus->ctx, s0 + UINT32_C(22));
    if (flag != 0)
        bus->call(bus->ctx, UINT32_C(0xbd6e), 0, &s0);
    flag = bus->read8(bus->ctx, s0 + UINT32_C(23));
#if defined(C364_INTENTIONAL_STORE_ON_ZERO)
    if (flag != 0 || s0 != C364_INITIAL_S0) {
#elif defined(C364_INTENTIONAL_SKIP_REDIRECT_STORE)
    if (flag != 0 && s0 == C364_INITIAL_S0) {
#else
    if (flag != 0) {
#endif
#ifdef C364_INTENTIONAL_BUG
        bus->write8(bus->ctx, s0 + UINT32_C(23), 0);
#else
        bus->write8(bus->ctx, C364_BF13, 0);
#endif
    }
}
