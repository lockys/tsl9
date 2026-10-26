#include <stddef.h>
#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only original RV32 SDK structure assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#define ALIGNOF alignof
#else
#define ASSERT _Static_assert
#define ALIGNOF _Alignof
#endif
ASSERT(sizeof(void *) == 4, "RV32 pointer width");
ASSERT(sizeof(bleConfig_t) == 64, "candidate configuration size");
ASSERT(ALIGNOF(bleConfig_t) == 4, "candidate configuration alignment");
ASSERT(offsetof(bleConfig_t, MEMAddr) == 0, "MEMAddr offset");
ASSERT(offsetof(bleConfig_t, MEMLen) == 4, "MEMLen offset");
ASSERT(offsetof(bleConfig_t, staCB) == 52, "status callback offset");
ASSERT(sizeof(((bleConfig_t *)0)->staCB) == 4, "status callback pointer width");
ASSERT(offsetof(bleConfig_t, SNVAddr) == 8, "SNVAddr offset");
ASSERT(offsetof(bleConfig_t, SNVBlock) == 12, "SNVBlock offset");
ASSERT(offsetof(bleConfig_t, SNVNum) == 14, "SNVNum offset");
ASSERT(offsetof(bleConfig_t, readFlashCB) == 56, "readFlashCB offset");
ASSERT(offsetof(bleConfig_t, writeFlashCB) == 60, "writeFlashCB offset");
ASSERT(sizeof(bleClockConfig_t) == 16, "clock configuration size");
ASSERT(ALIGNOF(bleClockConfig_t) == 4, "clock configuration alignment");
ASSERT(offsetof(bleClockConfig_t, getClockValue) == 0, "getClockValue offset");
ASSERT(offsetof(bleClockConfig_t, ClockMaxCount) == 4, "ClockMaxCount offset");
ASSERT(offsetof(bleClockConfig_t, ClockFrequency) == 8, "ClockFrequency offset");
ASSERT(offsetof(bleClockConfig_t, ClockAccuracy) == 10, "ClockAccuracy offset");
ASSERT(offsetof(bleClockConfig_t, irqEnable) == 12, "irqEnable offset");
/* No object, function, host model, MMIO access or executable entry is defined. */
