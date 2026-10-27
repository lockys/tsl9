#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 handler/scheduler bank numeric assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(16*12==192 && (48-16)*12==384 && 48*12==576,"disjoint original scheduler index banks");
ASSERT(16*12+(48-16)*12==48*12,"exact numeric union,no gap or overlap");
ASSERT((47>>4)==2 && (47&15)==15 && (1u<<(47&15))==0x8000u,"original task/event index encoding");
ASSERT(12+4==16 && 28+4==32 && 44+4==48,"original own-frame RA slots");
/* Numeric access extent only;not a physical allocation,IRQ or timing proof. */
