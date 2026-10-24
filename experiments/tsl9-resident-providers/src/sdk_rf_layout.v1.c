#include <stdint.h>
#ifdef __cplusplus
#define DATA extern "C" const
#define ALIGN_OF(T) alignof(T)
#else
#define DATA const
#define ALIGN_OF(T) _Alignof(T)
#endif
typedef void (*pfnRFStatusCB_t)( uint8_t sta, uint8_t rsr, uint8_t *rxBuf );
typedef struct tag_rf_config
{
    uint8_t LLEMode;                  //!< BIT0   0=basic, 1=auto def@LLE_MODE_TYPE
                                      //!< BIT1   0=whitening on, 1=whitening off def@LLE_WHITENING_TYPE
                                      //!< BIT4-5 00-1M  01-2M  10-coded(S8) 11-coded(S2) def@LLE_PHY_TYPE
                                      //!< BIT6   0=data channel(0-39)
                                      //!<        1=rf frequency (2400000kHz-2483500kHz)
                                      //!< BIT7   0=the first byte of the receive buffer is rssi
                                      //!<        1=the first byte of the receive buffer is package type
    uint8_t Channel;                  //!< rf channel(0-39)
    uint32_t Frequency;               //!< rf frequency (2400000kHz-2483500kHz)
    uint32_t accessAddress;           //!< access address,32bit PHY address
    uint32_t CRCInit;                 //!< crc initial value
    pfnRFStatusCB_t rfStatusCB;       //!< status call back
    uint32_t ChannelMap;              //!< indicating  Used and Unused data channels.Every channel is represented with a
                                      //!< bit positioned as per the data channel index,The LSB represents data channel index 0
    uint8_t Resv;
    uint8_t HeartPeriod;              //!< The heart package interval shall be an integer multiple of 100ms
    uint8_t HopPeriod;                //!< hop period( T=32n*RTC clock ),default is 8
    uint8_t HopIndex;                 //!< indicate the hopIncrement used in the data channel selection algorithm,default is 17
    uint8_t RxMaxlen;                 //!< Maximum data length received in rf-mode(default 251)
    uint8_t TxMaxlen;                 //!< Maximum data length transmit in rf-mode(default 251)
} rfConfig_t;
DATA uint32_t tsl9_rf_profile_layout[] __attribute__((used)) = {
    sizeof(rfConfig_t),
    ALIGN_OF(rfConfig_t),
    sizeof(pfnRFStatusCB_t),
    __builtin_offsetof(rfConfig_t,LLEMode),
    __builtin_offsetof(rfConfig_t,Channel),
    __builtin_offsetof(rfConfig_t,Frequency),
    __builtin_offsetof(rfConfig_t,accessAddress),
    __builtin_offsetof(rfConfig_t,CRCInit),
    __builtin_offsetof(rfConfig_t,rfStatusCB),
    __builtin_offsetof(rfConfig_t,ChannelMap),
    __builtin_offsetof(rfConfig_t,Resv),
    __builtin_offsetof(rfConfig_t,HeartPeriod),
    __builtin_offsetof(rfConfig_t,HopPeriod),
    __builtin_offsetof(rfConfig_t,HopIndex),
    __builtin_offsetof(rfConfig_t,RxMaxlen),
    __builtin_offsetof(rfConfig_t,TxMaxlen)
};
