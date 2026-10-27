#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 private initializer numeric requirements.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void *)==4 && sizeof(uint32_t)==4,"RV32 word/pointer width");
ASSERT(UINT32_C(0x200033b8)+296==UINT32_C(0x200034e0),"requested state extent");
ASSERT(UINT32_C(0x200034e0)<=UINT32_C(0x200034e4),"zero word outside state request");
ASSERT(0+4<=4 && 4+4<=8 && 8+4<=12 && 12+4==16,"four saved words fit original frame");
/* Numeric constraints only;no object,provider,import or executable entry. */
