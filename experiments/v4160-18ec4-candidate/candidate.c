/* Event-bus candidate derived from the static 0x18ec4 window, not an ABI. */
#include <stdint.h>

typedef uint32_t (*read32_fn)(void *context, uint32_t address);
typedef void (*write32_fn)(void *context, uint32_t address, uint32_t value);

uint32_t candidate_18ec4(void *context, read32_fn read32, write32_fn write32,
                         uint32_t a0)
{
    const uint32_t control = UINT32_C(0x40022010);
    const uint32_t address = UINT32_C(0x40022014);
    const uint32_t status = UINT32_C(0x4002200c);
    uint32_t value;

    a0 &= UINT32_C(0xffffff00);
    value = read32(context, control);
    write32(context, control, value | UINT32_C(0x20000));
    write32(context, address, a0);
    value = read32(context, control);
    write32(context, control, value | UINT32_C(0x40));
    while ((read32(context, status) & UINT32_C(1)) != 0) {
    }
    value = read32(context, control);
    write32(context, control, value & UINT32_C(0xfffdffff));
    return a0;
}
