/* Abstract events only; not a hardware or ABI implementation. */
#include <stdint.h>

typedef uint32_t (*read32_fn)(void *, uint32_t);
typedef void (*write32_fn)(void *, uint32_t, uint32_t);

uint32_t candidate_18e90(void *context, write32_fn write32, uint32_t input)
{
    write32(context, UINT32_C(0x4002200c), input);
    return input;
}

uint32_t candidate_18eb6(void *context, read32_fn read32, write32_fn write32,
                         uint32_t input)
{
    uint32_t value = read32(context, UINT32_C(0x40022010));
    write32(context, UINT32_C(0x40022010), value | UINT32_C(0x8000));
    return input;
}
