#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only candidate RV32 connection-event assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4,"RV32 pointer bytes");
ASSERT(__builtin_offsetof(linkDBItem_t,connectionHandle)==2,"60-byte record handle halfword offset");
ASSERT(__builtin_offsetof(linkDBItem_t,stateFlags)==4,"state flag byte offset");
ASSERT(LOOPBACK_CONNHANDLE==0xfffe,"loopback exclusion");
ASSERT(LINKDB_STATUS_UPDATE_REMOVED==1 && LINKDB_STATUS_UPDATE_STATEFLAGS==2,"event selector meanings");
ASSERT(LINK_CONNECTED==1,"up-state query mask");
ASSERT(FUNCITON_BASE_ADDRESSS+30*4==0x400ac,"candidate register slot");
ASSERT(FUNCITON_BASE_ADDRESSS+31*4==0x400b0,"candidate state slot");
ASSERT(12+4==16 && 28+4==32 && 44+4==48,"encoded own frame RA saves");
/* No runtime object,provider,radio operation or physical hardware assertion. */
