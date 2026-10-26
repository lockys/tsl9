#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
#define CHECK static_assert
#define ALIGN alignof
#else
#define CHECK _Static_assert
#define ALIGN _Alignof
#endif
typedef void (*pfnRFStatusCB_t)( uint8_t sta, uint8_t rsr, uint8_t *rxBuf );
typedef struct tag_rf_config {
uint8_t LLEMode;
uint8_t Channel;
uint32_t Frequency;
uint32_t accessAddress;
uint32_t CRCInit;
pfnRFStatusCB_t rfStatusCB;
uint32_t ChannelMap;
uint8_t Resv;
uint8_t HeartPeriod;
uint8_t HopPeriod;
uint8_t HopIndex;
uint8_t RxMaxlen;
uint8_t TxMaxlen;
} rfConfig_t;
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
