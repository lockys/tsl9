#include <stdint.h>

/* Capability diagnostic only: do not execute or use as a target provider. */
register uint32_t port_owned_s0 __asm__("s0");

#ifdef __cplusplus
extern "C"
#endif
uint32_t probe_owned_s0(uint32_t replacement)
{
    uint32_t previous = port_owned_s0;
    port_owned_s0 = replacement;
    return previous;
}
