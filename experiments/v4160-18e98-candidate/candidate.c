#include <stdint.h>

typedef void (*write_event)(void *context, uint32_t address, uint32_t value);

/* Callback must be valid and return normally; no target hardware access here. */
void candidate_18e98(void *context, write_event write)
{
    write(context, UINT32_C(0x40022004), UINT32_C(0x45670123));
    write(context, UINT32_C(0x40022004), UINT32_C(0xcdef89ab));
    write(context, UINT32_C(0x40022024), UINT32_C(0x45670123));
    write(context, UINT32_C(0x40022024), UINT32_C(0xcdef89ab));
}
