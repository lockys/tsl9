#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 required-leaf numeric assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void *)==4 && sizeof(uint32_t)==4 && sizeof(uint16_t)==2,"RV32 widths");
ASSERT(UINT32_C(0x200033b8)+296==UINT32_C(0x200034e0),"state request end");
ASSERT(UINT32_C(0x200034e0)+4==UINT32_C(0x200034e4),"first adjacent word");
ASSERT(UINT32_C(0x200034e4)+4==UINT32_C(0x200034e8),"second adjacent word");
ASSERT(UINT32_C(0x200034e8)+4-UINT32_C(0x200033b8)==308,"conditional combined zero request span");
/* No object,provider,import or executable entry. Physical ownership unproved. */
