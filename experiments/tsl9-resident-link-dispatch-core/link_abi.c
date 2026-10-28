#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only candidate RV32 link-dispatch assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4 && sizeof(pfnLinkDBCB_t)==4,"RV32 data/callback pointer bytes");
ASSERT(sizeof(linkDBItem_t)==60,"candidate link-record stride");
ASSERT(__builtin_offsetof(linkDBItem_t,connectionHandle)==2,"link handle halfword");
ASSERT(__builtin_offsetof(linkDBItem_t,stateFlags)==4,"link flag byte");
ASSERT(__builtin_offsetof(linkDBItem_t,pEncParams)==44,"guarded release field");
ASSERT(LOOPBACK_CONNHANDLE==0xfffe && INVALID_CONNHANDLE==0xffff,"special handles");
ASSERT(LINKDB_STATUS_UPDATE_REMOVED==1 && LINKDB_STATUS_UPDATE_STATEFLAGS==2,"status event selectors");
ASSERT(FUNCITON_BASE_ADDRESSS+32*4==0x400b4,"candidate per-link iteration API slot");
ASSERT(12+4==16 && 28+4==32 && 44+4==48 && 60+4==64,"encoded own frame RA saves");
/* No runtime allocation,provider,radio operation or physical identity claim. */
