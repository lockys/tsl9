#ifndef TSL9_ADC_CONFIG_H
#define TSL9_ADC_CONFIG_H
#include "memory_leaves.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Numeric-address effect projection of candidate 0x1892e, not a register ABI.
 * A failed callback ends the exact attempted-effect prefix without cleanup. */
ml_result tsl9_adc_config_io(ml_io *,uint32_t base,uint32_t config);
uint32_t tsl9_adc_config_1892e(uint32_t base,uint32_t config);
#ifdef __cplusplus
}
#endif
#endif
