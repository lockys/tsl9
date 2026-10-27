#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only original RV32 frame/word assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4 && sizeof(uint16_t)==2,"original numeric widths");
ASSERT(12+4==16 && 28+4==32 && 44+4==48,"encoded own-frame RA save slots");
/* Frame-free leaves add no target allocation or callback body. */
