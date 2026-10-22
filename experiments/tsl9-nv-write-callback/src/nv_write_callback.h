#ifndef TSL9_NV_WRITE_CALLBACK_H
#define TSL9_NV_WRITE_CALLBACK_H
#include "../../tsl9-v4160-flash-entry-order/src/flash_native.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Numeric MMIO/call projections, not recovered original C prototypes or
 * admitted physical register ABIs. The second write input is unused. */
uint32_t tsl9_delay_19764(uint32_t incoming_a0);
uint32_t tsl9_nv_write_callback_197be(uint32_t destination,uint32_t unused_a1,uint32_t source);
#ifdef __cplusplus
}
#endif
#endif
