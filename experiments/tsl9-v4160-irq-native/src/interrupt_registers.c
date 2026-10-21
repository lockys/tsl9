#include "../../tsl9-v4160-interrupt-registers/src/interrupt_registers.h"
#include "native_io.h"

/* A branch owns its fresh read, RMW, store and normal return. Separate opaque
 * bases prevent a pre-branch load/select and duplicate return live ranges. */
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
{
    return update32(0x18u,mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_19142(uint32_t mask,uint32_t enabled)
{
    return update32(0x1cu,mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_19160(uint32_t mask,uint32_t enabled)
{
    return update32(0x0cu,mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_1917e(uint32_t mask,uint32_t enabled)
{
    return update32(0x10u,mask,enabled);
}
uint32_t tsl9_rebuild_interrupt_registers_9a42(void)
{
    uint32_t result;
    IR_CSR_CLEAR(0x88u);
    (void)update32(0x1cu,IR_MASK_LITERAL(0x02020006u),1u);
    (void)update32(0x18u,IR_MASK_LITERAL(0x101du),1u);
    (void)update32(0x10u,IR_MASK_LITERAL(0x02020006u),1u);
    (void)update32(0x10u,IR_MASK_LITERAL(0x02020006u),0u);
    (void)update32(0x0cu,IR_MASK_LITERAL(0x101du),1u);
    result=update32(0x0cu,IR_MASK_LITERAL(0x101du),0u);
    IR_WRITE8(UINT32_C(0xe000e42d),0u);
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x2000));
    IR_WRITE8(UINT32_C(0xe000e424),UINT8_C(0x20));
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x10));
    IR_WRITE8(UINT32_C(0xe000e427),UINT8_C(0x30));
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x80));
    IR_CSR_SET(0x88u);
    return ir_init_return(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));
}
