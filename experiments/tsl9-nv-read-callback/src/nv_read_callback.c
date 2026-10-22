#include "nv_read_callback.h"

uint32_t tsl9_nv_read_callback_1979a(uint32_t source,uint32_t words,uint32_t destination)
{
    /* Fresh slot access precedes the actual indirect call in source.
     * Compiler frame/register scheduling still needs machine-code review. */
    uint32_t target=*(volatile uint32_t *)(uintptr_t)UINT32_C(0x4004c);
    tsl9_nv_copy_normal_projection_fn copy=(tsl9_nv_copy_normal_projection_fn)(uintptr_t)target;
    (void)copy(destination,source,words<<2);
    return 0;
}
