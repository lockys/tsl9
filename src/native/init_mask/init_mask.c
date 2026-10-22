#include <stdint.h>
#include "../irq/native_io.h"

/* Numeric register operation recovered from V4.1.60 [0x19106,0x19124).
 * Keep the two branch-specific normal A4/A5 outputs as well as A0/A1.
 * The shared adapter contains only the minimal register-bound ABI bridge;
 * the fresh volatile read, bit operation and write remain ordinary C. */
#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_rebuild_register_mask_19106(uint32_t mask, uint32_t enabled)
{
    if (enabled) {
        const uint32_t base = IR_BASE_ON();
        const uint32_t value = IR_MASK_VALUE(mask);
        const uint32_t before = IR_READ32(base + 0x14u);
        const uint32_t after = before | value;
        IR_WRITE32(base + 0x14u, after);
        return ir_rcc_return(after, enabled, base, before);
    } else {
        const uint32_t base = IR_BASE_OFF();
        const uint32_t value = IR_MASK_VALUE(mask);
        const uint32_t before = IR_READ32(base + 0x14u);
        const uint32_t after = before & ~value;
        IR_WRITE32(base + 0x14u, after);
        return ir_rcc_return(after, enabled, before, base);
    }
}
