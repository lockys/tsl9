#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 primary header ABI assertions only.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
ASSERT(__is_same(pTaskEventHandlerFn, uint16_t (*)(uint8_t, uint16_t)), "primary task handler type");
#else
#define ASSERT _Static_assert
ASSERT(_Generic((pTaskEventHandlerFn)0, uint16_t (*)(uint8_t, uint16_t): 1, default: 0), "primary task handler type");
#endif
ASSERT(sizeof(void *) == 4, "RV32 pointer width");
ASSERT(sizeof(tmosTaskID) == 1, "primary task ID width");
ASSERT(sizeof(tmosEvents) == 2, "primary event and result width");
/* No function, object, runtime adapter or installed private-ABI claim. */
