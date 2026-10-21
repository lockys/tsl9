#include "../../tsl9-v4160-interrupt-registers/src/interrupt_registers.h"
#include "../../tsl9-v4160-irq-native/src/native_io.h"

/* The helper path is unchanged from the byte-verified branch-first core. */
IR_INLINE uint32_t update32(uint32_t offset,uint32_t value,uint32_t enabled)
{
    if(enabled) {
        const uint32_t base=IR_BASE_ON();
        const uint32_t mask=IR_MASK_VALUE(value);
        const uint32_t before=IR_READ32(base+offset);
        const uint32_t after=before|mask;
        IR_WRITE32(base+offset,after);
        return ir_rcc_return(after,enabled,base,before);
    } else {
        const uint32_t base=IR_BASE_OFF();
        const uint32_t mask=IR_MASK_VALUE(value);
        const uint32_t before=IR_READ32(base+offset);
        const uint32_t after=before&~mask;
        IR_WRITE32(base+offset,after);
        return ir_rcc_return(after,enabled,before,base);
    }
}
uint32_t tsl9_rebuild_rcc_registers_19124(uint32_t mask,uint32_t enabled)
{ return update32(0x18u,mask,enabled); }
uint32_t tsl9_rebuild_rcc_registers_19142(uint32_t mask,uint32_t enabled)
{ return update32(0x1cu,mask,enabled); }
uint32_t tsl9_rebuild_rcc_registers_19160(uint32_t mask,uint32_t enabled)
{ return update32(0x0cu,mask,enabled); }
uint32_t tsl9_rebuild_rcc_registers_1917e(uint32_t mask,uint32_t enabled)
{ return update32(0x10u,mask,enabled); }
