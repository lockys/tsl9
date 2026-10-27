#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 initializer numeric layout.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(UINT32_C(0x20003000)+1108==UINT32_C(0x20003454),"real memset destination");
ASSERT(UINT32_C(0x20003454)+28==UINT32_C(0x20003470),"request end");
ASSERT(UINT32_C(0x200033b8)+192==UINT32_C(0x20003478),"byte store");
ASSERT(UINT32_C(0x200033b8)+196==UINT32_C(0x2000347c),"word store");
ASSERT(UINT32_C(0x2000347c)+4<=UINT32_C(0x200033b8)+296,"inside earlier state request");
/* Numeric evidence only;no runtime provider or physical ownership proof. */
