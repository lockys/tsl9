#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 parser/scheduler numeric assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(108+4==112 && 60+12*4==108,"parser saved registers and RA");
ASSERT(44+4==48 && 8+9*4==44,"scheduler own frame");
ASSERT(28+4==32 && 12+4*4==28,"removal own frame");
ASSERT(16*12==192 && 48*12==576,"different original scan and ID numeric extents");
ASSERT(32+5==37 && 37<=UINT8_MAX,"masked five-byte popcount extent");
/* No runtime provider,physical RAM ownership or scheduler compatibility proof. */
