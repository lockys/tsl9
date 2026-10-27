#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 loader/source/frame numeric assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
#define SOURCE(a) ((a)-UINT32_C(0x20000000)+UINT32_C(0x40270))
ASSERT(sizeof(void*)==4 && sizeof(uint32_t)==4,"RV32 widths");
ASSERT(SOURCE(UINT32_C(0x2000202c))==UINT32_C(0x4229c),"first lookup source");
ASSERT(SOURCE(UINT32_C(0x200022be))==UINT32_C(0x4252e),"selector source");
ASSERT(SOURCE(UINT32_C(0x20002426))==UINT32_C(0x42696),"selector exclusive end");
ASSERT(UINT32_C(0x20000040)<=UINT32_C(0x2000202c) && UINT32_C(0x20002426)<=UINT32_C(0x20002e74),"all new RAM code inside retained first-copy extent");
ASSERT(UINT32_C(0x200033b8)+196==UINT32_C(0x2000347c) && UINT32_C(0x200033b8)+204==UINT32_C(0x20003484),"earlier list-head zero-request relations");
ASSERT(44+4==48 && 28+4==32 && 12+4==16,"real own-frame RA slots");
ASSERT(48+1==49 && 8+16==24,"actual message request extents");
/* No provider,physical mapping,list termination or live-memory proof. */
