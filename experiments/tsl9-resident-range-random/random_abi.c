#include <stddef.h>
#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only primary SDK callback assertions;no host model.
#endif
typedef uint32_t (*expected_seed_callback)(void);
#ifdef __cplusplus
#define ASSERT static_assert
ASSERT(__is_same(pfnSrandCB,expected_seed_callback),"primary seed callback type");
#else
#define ASSERT _Static_assert
ASSERT(__builtin_types_compatible_p(pfnSrandCB,expected_seed_callback),"primary seed callback type");
#endif
ASSERT(sizeof(void *)==4,"RV32 pointer bytes");
ASSERT(sizeof(uint32_t)==4,"word width");
ASSERT(sizeof(bleConfig_t)==64,"primary config bytes");
ASSERT(offsetof(bleConfig_t,srandCB)==36,"primary seed callback offset");
/* No allocation,implementation,stub or executable entry is defined. */
