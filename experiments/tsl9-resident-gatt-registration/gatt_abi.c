#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only candidate RV32 GATT layout assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void*)==4,"RV32 pointers");
ASSERT(sizeof(gattAttrType_t)==8,"candidate type stride");
ASSERT(__builtin_offsetof(gattAttrType_t,len)==0,"UUID length byte");
ASSERT(__builtin_offsetof(gattAttrType_t,uuid)==4,"UUID pointer");
ASSERT(sizeof(gattAttribute_t)==16,"candidate attribute stride");
ASSERT(__builtin_offsetof(gattAttribute_t,type)==0,"attribute type");
ASSERT(__builtin_offsetof(gattAttribute_t,permissions)==8,"permission byte");
ASSERT(__builtin_offsetof(gattAttribute_t,handle)==10,"assigned handle halfword");
ASSERT(__builtin_offsetof(gattAttribute_t,pValue)==12,"value pointer");
ASSERT(sizeof(gattServiceCBs_t)==12,"three callback pointers");
ASSERT(FUNCITON_BASE_ADDRESSS+63*4==0x40130,"candidate register-service slot");
ASSERT(GATT_PRIMARY_SERVICE_UUID==0x2800 && GATT_CHARACTER_UUID==0x2803 && GATT_CLIENT_CHAR_CFG_UUID==0x2902,"candidate UUID roles");
ASSERT(GATT_PERMIT_READ==1 && GATT_PERMIT_WRITE==2,"candidate permission bits");
ASSERT(12+4==16 && 28+4==32,"encoded own frame RA saves");
/* No runtime object,provider,radio operation or physical layout assertion. */
