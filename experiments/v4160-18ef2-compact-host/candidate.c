/* Informal event-bus candidate, not an ABI or code-generation reconstruction. */
#include <stdint.h>

typedef struct {
    void *context;
    uint32_t (*read32)(void *context, uint32_t address);
    void (*write32)(void *context, uint32_t address, uint32_t value);
} event_bus;

uint32_t candidate_18ef2(const event_bus *bus, uint32_t a0, uint32_t a1)
{
    const uint32_t status = UINT32_C(0x4002200c);
    const uint32_t control = UINT32_C(0x40022010);
    uint32_t value;
    uint32_t offset;
    a0 &= UINT32_C(0xffffff00);
    value = bus->read32(bus->context, control);
    bus->write32(bus->context, control, value | UINT32_C(0x10000));
    while (bus->read32(bus->context, status) & UINT32_C(1)) { }
    while (bus->read32(bus->context, status) & UINT32_C(2)) { }
    for (offset = 0; offset != UINT32_C(256); offset += UINT32_C(4)) {
        value = bus->read32(bus->context, (uint32_t)(a1 + offset));
        bus->write32(bus->context, (uint32_t)(a0 + offset), value);
        while (bus->read32(bus->context, status) & UINT32_C(2)) { }
    }
    value = bus->read32(bus->context, control);
    bus->write32(bus->context, control, value | UINT32_C(0x200000));
    while (bus->read32(bus->context, status) & UINT32_C(1)) { }
    value = bus->read32(bus->context, control);
    bus->write32(bus->context, control, value & UINT32_C(0xfffeffff));
    return a0;
}
