#include "../../tsl9-v4160-interrupt-registers/src/interrupt_registers.h"
#include "callframe_io.h"

uint32_t tsl9_rebuild_interrupt_registers_9a42(void)
{
    uint32_t result;
    CF_CSR_DECLARE;
    CF_CSR_CLEAR();
    CF_FAST_DECLARE;
    (void)CF_CALL(tsl9_rebuild_rcc_registers_19142,CF_FAST_MASK(),1u);
    CF_SLOW_DECLARE;
    (void)CF_CALL(tsl9_rebuild_rcc_registers_19124,CF_SLOW_MASK(),1u);
    (void)CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),1u);
    (void)CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),0u);
    (void)CF_CALL(tsl9_rebuild_rcc_registers_19160,CF_SLOW_MASK(),1u);
    result=CF_FINAL_CLEAR(tsl9_rebuild_rcc_registers_19160,CF_SLOW_MASK());
    CF_NVIC_DECLARE;
    CF_ZERO8(0x42du);
    CF_WRITE32(0x104u,0x2000u);
    CF_WRITE8(0x424u,0x20u);
    CF_WRITE32(0x104u,0x10u);
    CF_WRITE8(0x427u,0x30u);
    CF_WRITE32(0x104u,0x80u);
    CF_CSR_SET();
    return CF_RETURN(result);
}
