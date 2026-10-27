#include <stddef.h>
#include <stdint.h>
#include "requirements-v1.h"
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 original callback layout assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#define SAME_CLOCK __is_same(pfnGetSysClock,uint32_t (*)(void))
#define SAME_STATUS __is_same(pfnLibStatusErrorCB,void (*)(uint8_t,uint32_t))
#else
#define ASSERT _Static_assert
#define SAME_CLOCK _Generic((pfnGetSysClock)0,uint32_t (*)(void):1,default:0)
#define SAME_STATUS _Generic((pfnLibStatusErrorCB)0,void (*)(uint8_t,uint32_t):1,default:0)
#endif
ASSERT(sizeof(void*)==4 && sizeof(pfnGetSysClock)==4,"RV32 callback pointer widths");
ASSERT(SAME_CLOCK && SAME_STATUS,"primary clock/status callback types");
ASSERT(sizeof(bleClockConfig_t)==16 && offsetof(bleClockConfig_t,getClockValue)==0,"clock callback copy slot");
ASSERT(offsetof(bleClockConfig_t,ClockMaxCount)==4 && offsetof(bleClockConfig_t,ClockFrequency)==8,"clock fields");
ASSERT(offsetof(bleClockConfig_t,ClockAccuracy)==10 && offsetof(bleClockConfig_t,irqEnable)==12,"clock validity fields");
ASSERT(sizeof(bleConfig_t)==64 && offsetof(bleConfig_t,staCB)==52,"primary BLE status callback field");
ASSERT(TSL9_SDK_BLE_CONFIG+52==TSL9_SDK_STATUS_POINTER,"conditional copied status pointer");
ASSERT(16+52==68 && 16+64==80 && 68+4<=80,"original APP status field and copied extent");
ASSERT(TSL9_ORIGINAL_RAW_CLOCK_CALLBACK_END-TSL9_ORIGINAL_RAW_CLOCK_CALLBACK==90,"complete existing APP callback body");
ASSERT(TSL9_APP_CLOCK_FREQUENCY_NUMERIC>0 && TSL9_APP_CLOCK_ACCURACY_NUMERIC>0,"actual nonzero numeric clock fields");
/* No object,callee replacement,live-target or physical timing assertion. */
