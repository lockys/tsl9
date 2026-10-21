#include "interrupt_registers.h"
#include "irq_io.h"

/* RCC helper normal outputs depend on its original enabled/disabled path.
 * Preserve exact A1 bits, not merely its truth value. The physical base in
 * A4/A5 is 0x40021000, not the full address of the individual register. */
IR_INLINE uint32_t update32(uint32_t address,uint32_t mask,uint32_t enabled)
{
    const uint32_t before=IR_READ32(address);
    const uint32_t after=enabled?(before|mask):(before&~mask);
    IR_WRITE32(address,after);
    if(enabled)IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),before);
    else IR_RCC_OUTPUTS(after,enabled,before,UINT32_C(0x40021000));
    return after;
}
uint32_t tsl9_rebuild_rcc_registers_19124(uint32_t mask,uint32_t enabled)
{
    return update32(UINT32_C(0x40021018),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_19142(uint32_t mask,uint32_t enabled)
{
    return update32(UINT32_C(0x4002101c),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_19160(uint32_t mask,uint32_t enabled)
{
    return update32(UINT32_C(0x4002100c),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_registers_1917e(uint32_t mask,uint32_t enabled)
{
    return update32(UINT32_C(0x40021010),mask,enabled);
}
uint32_t tsl9_rebuild_interrupt_registers_9a42(void)
{
    uint32_t result;
    IR_CSR_CLEAR(UINT32_C(0x88));
    (void)update32(UINT32_C(0x4002101c),UINT32_C(0x02020006),1u);
    (void)update32(UINT32_C(0x40021018),UINT32_C(0x101d),1u);
    (void)update32(UINT32_C(0x40021010),UINT32_C(0x02020006),1u);
    (void)update32(UINT32_C(0x40021010),UINT32_C(0x02020006),0u);
    (void)update32(UINT32_C(0x4002100c),UINT32_C(0x101d),1u);
    result=update32(UINT32_C(0x4002100c),UINT32_C(0x101d),0u);
    IR_WRITE8(UINT32_C(0xe000e42d),0u);
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x2000));
    IR_WRITE8(UINT32_C(0xe000e424),UINT8_C(0x20));
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x10));
    IR_WRITE8(UINT32_C(0xe000e427),UINT8_C(0x30));
    IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x80));
    IR_CSR_SET(UINT32_C(0x88));
    IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));
    return result;
}
