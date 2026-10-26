#include <stdint.h>
#include <stddef.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#ifdef __cplusplus
#define CHECK static_assert
#define ALIGN alignof
#else
#define CHECK _Static_assert
#define ALIGN _Alignof
#endif
CHECK(sizeof(void*)==4,"RV32 pointer width");
CHECK(sizeof(rfConfig_t)==32 && ALIGN(rfConfig_t)==4,"Primary RF configuration ABI candidate only");
CHECK(offsetof(rfConfig_t,LLEMode)==0,"Primary field LLEMode");
CHECK(offsetof(rfConfig_t,Channel)==1,"Primary field Channel");
CHECK(offsetof(rfConfig_t,Frequency)==4,"Primary field Frequency");
CHECK(offsetof(rfConfig_t,accessAddress)==8,"Primary field accessAddress");
CHECK(offsetof(rfConfig_t,CRCInit)==12,"Primary field CRCInit");
CHECK(offsetof(rfConfig_t,rfStatusCB)==16,"Primary field rfStatusCB");
CHECK(offsetof(rfConfig_t,ChannelMap)==20,"Primary field ChannelMap");
CHECK(offsetof(rfConfig_t,Resv)==24,"Primary field Resv");
CHECK(offsetof(rfConfig_t,HeartPeriod)==25,"Primary field HeartPeriod");
CHECK(offsetof(rfConfig_t,HopPeriod)==26,"Primary field HopPeriod");
CHECK(offsetof(rfConfig_t,HopIndex)==27,"Primary field HopIndex");
CHECK(offsetof(rfConfig_t,RxMaxlen)==28,"Primary field RxMaxlen");
CHECK(offsetof(rfConfig_t,TxMaxlen)==29,"Primary field TxMaxlen");

/* Original APP constructor constraints only;not an executable replacement. */
CHECK(0x17644u - 342u == 0x174eeu,"original callback literal");
CHECK(sizeof(rfConfig_t)==32 && 32u<=36u && 36u+12u==48u,"configuration lies below three saved registers in own48-byte frame");
CHECK(0x40000u+452u==0x40034u+100u*4u,"RF configuration table word");
CHECK(0x40000u+448u==0x40034u+99u*4u,"RF initialization table word");
CHECK(0x2000c7a0u + 268u <= 0x2000c958u,"original APP RF context lies numerically within original zero interval");

/* Primary callback layout/types;compile-only,not installed RAM or runtime proof. */
CHECK(sizeof(bleConfig_t)==64,"primary library configuration bytes");
CHECK(offsetof(bleConfig_t,tsCB)==44,"primary temperature callback offset");
CHECK(offsetof(bleConfig_t,rcCB)==48,"primary calibration callback offset");
CHECK(sizeof(((bleConfig_t *)0)->tsCB)==4 && sizeof(((bleConfig_t *)0)->rcCB)==4,"RV32 callback widths");
typedef uint16_t (*tsl9_primary_temp_type)(void);
typedef void (*tsl9_primary_calibration_type)(void);
#ifdef __cplusplus
CHECK(__is_same(pfnTempSampleCB,tsl9_primary_temp_type),"primary sample result is uint16_t");
CHECK(__is_same(pfnLSICalibrationCB,tsl9_primary_calibration_type),"primary calibration signature");
#else
CHECK(__builtin_types_compatible_p(pfnTempSampleCB,tsl9_primary_temp_type),"primary sample result is uint16_t");
CHECK(__builtin_types_compatible_p(pfnLSICalibrationCB,tsl9_primary_calibration_type),"primary calibration signature");
#endif
