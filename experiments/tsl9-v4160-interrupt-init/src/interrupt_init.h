#ifndef TSL9_REBUILD_INTERRUPT_INIT_H
#define TSL9_REBUILD_INTERRUPT_INIT_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* New reconstruction symbols, not aliases for original firmware addresses.
 * Results preserve the observed A0 written by the source's final RMW. */
uint32_t tsl9_rebuild_rcc_19124(uint32_t mask, uint32_t enabled);
uint32_t tsl9_rebuild_rcc_19142(uint32_t mask, uint32_t enabled);
uint32_t tsl9_rebuild_rcc_19160(uint32_t mask, uint32_t enabled);
uint32_t tsl9_rebuild_rcc_1917e(uint32_t mask, uint32_t enabled);
uint32_t tsl9_rebuild_interrupt_init_9a42(void);

#ifdef __cplusplus
}
#endif
#endif
