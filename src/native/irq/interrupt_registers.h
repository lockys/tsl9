#ifndef TSL9_INTERRUPT_REGISTERS_H
#define TSL9_INTERRUPT_REGISTERS_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Normal-boundary contracts only. This is not an interrupt-state or board ABI proof. */
uint32_t tsl9_rebuild_rcc_registers_19124(uint32_t mask,uint32_t enabled);
uint32_t tsl9_rebuild_rcc_registers_19142(uint32_t mask,uint32_t enabled);
uint32_t tsl9_rebuild_rcc_registers_19160(uint32_t mask,uint32_t enabled);
uint32_t tsl9_rebuild_rcc_registers_1917e(uint32_t mask,uint32_t enabled);
uint32_t tsl9_rebuild_interrupt_registers_9a42(void);
#ifdef __cplusplus
}
#endif
#endif
