/* Saved SDK candidate layout only; no SDK function calls or target execution. */
#include <stdint.h>
#include <stddef.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 ILP32 metadata only"
#endif
#if defined(__cplusplus)
#define CHECK static_assert
#define ALIGNOF alignof
#define DATA extern "C" __attribute__((used,section(".rodata.tsl9_sdk_boot_layout"),aligned(4)))
#else
#define CHECK _Static_assert
#define ALIGNOF _Alignof
#define DATA __attribute__((used,section(".rodata.tsl9_sdk_boot_layout"),aligned(4)))
#endif
CHECK(sizeof(void*)==4,"RV32 pointer width");
typedef uint32_t (*pfnSrandCB)( void );
typedef uint32_t (*pfnIdleCB)( uint32_t );
typedef void (*pfnLSICalibrationCB)( void );
typedef uint16_t (*pfnTempSampleCB)( void );
typedef void (*pfnLibStatusErrorCB)( uint8_t code, uint32_t status );
typedef uint32_t (*pfnFlashReadCB)( uint32_t addr, uint32_t num, uint32_t *pBuf );
typedef uint32_t (*pfnFlashWriteCB)( uint32_t addr, uint32_t num, uint32_t *pBuf );
typedef uint32_t (*pfnGetSysClock)( void );
typedef struct tag_ble_config
{
    uint32_t MEMAddr;               // library memory start address
    uint16_t MEMLen;                // library memory size
    uint32_t SNVAddr;               // SNV flash start address( if NULL,bonding information will not be saved )
    uint16_t SNVBlock;              // SNV flash block size ( default 256 )
    uint8_t SNVNum;                 // SNV flash block number ( default 1 )
    uint8_t BufNumber;              // Maximum number of sent and received packages cached by the controller( default 5 )
                                    // Must be greater than the number of connections.
    uint16_t BufMaxLen;             // Maximum length (in octets) of the data portion of each HCI data packet( default 27 )
                                    // SC enable,must be greater than 69
                                    // ATT_MTU = BufMaxLen-4,Range[23,ATT_MAX_MTU_SIZE]
    uint8_t TxNumEvent;             // Maximum number of TX data in a connection event ( default 1 )
    uint8_t RxNumEvent;             // Maximum number of RX data in a connection event ( default equal to BufNumber )
    uint8_t TxPower;                // Transmit power level( default LL_TX_POWEER_0_DBM(0dBm) )
    uint8_t ConnectNumber;          // Connect number,lower two bits are peripheral number,followed by central number

    uint8_t WindowWidening;         // Wait rf start window(us)
    uint8_t WaitWindow;             // Wait event arrive window in one system clock
    uint8_t MacAddr[6];             // MAC address,little-endian
    uint16_t ClockFrequency;        // The timing clock frequency(Hz)
    uint16_t ClockAccuracy;         // The timing clock accuracy(ppm)
    pfnSrandCB srandCB;             // Register a program that generate a random seed
    pfnIdleCB idleCB;               // Register a program that set idle
    pfnTempSampleCB tsCB;           // Register a program that read the current temperature,determine whether calibration is need
    pfnLSICalibrationCB rcCB;       // Register a program that LSI clock calibration
    pfnLibStatusErrorCB staCB;      // Register a program that library status callback
    pfnFlashReadCB readFlashCB;     // Register a program that read flash
    pfnFlashWriteCB writeFlashCB;   // Register a program that write flash
} bleConfig_t; // Library initialization call BLE_LibInit function
typedef struct tag_ble_clock_config
{
  pfnGetSysClock getClockValue;
  uint32_t ClockMaxCount;         // The maximum count value
  uint16_t ClockFrequency;        // The timing clock frequency(Hz)
  uint16_t ClockAccuracy;         // The timing clock accuracy(ppm)
  uint8_t  irqEnable;             // resv
}bleClockConfig_t;
CHECK(sizeof(bleConfig_t)==64,"bleConfig_t size");
CHECK(ALIGNOF(bleConfig_t)==4,"bleConfig_t alignment");
CHECK(offsetof(bleConfig_t,MEMAddr)==0,"bleConfig_t.MEMAddr offset");
CHECK(sizeof(((bleConfig_t*)0)->MEMAddr)==4,"bleConfig_t.MEMAddr bytes");
CHECK(offsetof(bleConfig_t,MEMLen)==4,"bleConfig_t.MEMLen offset");
CHECK(sizeof(((bleConfig_t*)0)->MEMLen)==2,"bleConfig_t.MEMLen bytes");
CHECK(offsetof(bleConfig_t,SNVAddr)==8,"bleConfig_t.SNVAddr offset");
CHECK(sizeof(((bleConfig_t*)0)->SNVAddr)==4,"bleConfig_t.SNVAddr bytes");
CHECK(offsetof(bleConfig_t,SNVBlock)==12,"bleConfig_t.SNVBlock offset");
CHECK(sizeof(((bleConfig_t*)0)->SNVBlock)==2,"bleConfig_t.SNVBlock bytes");
CHECK(offsetof(bleConfig_t,SNVNum)==14,"bleConfig_t.SNVNum offset");
CHECK(sizeof(((bleConfig_t*)0)->SNVNum)==1,"bleConfig_t.SNVNum bytes");
CHECK(offsetof(bleConfig_t,BufNumber)==15,"bleConfig_t.BufNumber offset");
CHECK(sizeof(((bleConfig_t*)0)->BufNumber)==1,"bleConfig_t.BufNumber bytes");
CHECK(offsetof(bleConfig_t,BufMaxLen)==16,"bleConfig_t.BufMaxLen offset");
CHECK(sizeof(((bleConfig_t*)0)->BufMaxLen)==2,"bleConfig_t.BufMaxLen bytes");
CHECK(offsetof(bleConfig_t,TxNumEvent)==18,"bleConfig_t.TxNumEvent offset");
CHECK(sizeof(((bleConfig_t*)0)->TxNumEvent)==1,"bleConfig_t.TxNumEvent bytes");
CHECK(offsetof(bleConfig_t,RxNumEvent)==19,"bleConfig_t.RxNumEvent offset");
CHECK(sizeof(((bleConfig_t*)0)->RxNumEvent)==1,"bleConfig_t.RxNumEvent bytes");
CHECK(offsetof(bleConfig_t,TxPower)==20,"bleConfig_t.TxPower offset");
CHECK(sizeof(((bleConfig_t*)0)->TxPower)==1,"bleConfig_t.TxPower bytes");
CHECK(offsetof(bleConfig_t,ConnectNumber)==21,"bleConfig_t.ConnectNumber offset");
CHECK(sizeof(((bleConfig_t*)0)->ConnectNumber)==1,"bleConfig_t.ConnectNumber bytes");
CHECK(offsetof(bleConfig_t,WindowWidening)==22,"bleConfig_t.WindowWidening offset");
CHECK(sizeof(((bleConfig_t*)0)->WindowWidening)==1,"bleConfig_t.WindowWidening bytes");
CHECK(offsetof(bleConfig_t,WaitWindow)==23,"bleConfig_t.WaitWindow offset");
CHECK(sizeof(((bleConfig_t*)0)->WaitWindow)==1,"bleConfig_t.WaitWindow bytes");
CHECK(offsetof(bleConfig_t,MacAddr)==24,"bleConfig_t.MacAddr offset");
CHECK(sizeof(((bleConfig_t*)0)->MacAddr)==6,"bleConfig_t.MacAddr bytes");
CHECK(offsetof(bleConfig_t,ClockFrequency)==30,"bleConfig_t.ClockFrequency offset");
CHECK(sizeof(((bleConfig_t*)0)->ClockFrequency)==2,"bleConfig_t.ClockFrequency bytes");
CHECK(offsetof(bleConfig_t,ClockAccuracy)==32,"bleConfig_t.ClockAccuracy offset");
CHECK(sizeof(((bleConfig_t*)0)->ClockAccuracy)==2,"bleConfig_t.ClockAccuracy bytes");
CHECK(offsetof(bleConfig_t,srandCB)==36,"bleConfig_t.srandCB offset");
CHECK(sizeof(((bleConfig_t*)0)->srandCB)==4,"bleConfig_t.srandCB bytes");
CHECK(offsetof(bleConfig_t,idleCB)==40,"bleConfig_t.idleCB offset");
CHECK(sizeof(((bleConfig_t*)0)->idleCB)==4,"bleConfig_t.idleCB bytes");
CHECK(offsetof(bleConfig_t,tsCB)==44,"bleConfig_t.tsCB offset");
CHECK(sizeof(((bleConfig_t*)0)->tsCB)==4,"bleConfig_t.tsCB bytes");
CHECK(offsetof(bleConfig_t,rcCB)==48,"bleConfig_t.rcCB offset");
CHECK(sizeof(((bleConfig_t*)0)->rcCB)==4,"bleConfig_t.rcCB bytes");
CHECK(offsetof(bleConfig_t,staCB)==52,"bleConfig_t.staCB offset");
CHECK(sizeof(((bleConfig_t*)0)->staCB)==4,"bleConfig_t.staCB bytes");
CHECK(offsetof(bleConfig_t,readFlashCB)==56,"bleConfig_t.readFlashCB offset");
CHECK(sizeof(((bleConfig_t*)0)->readFlashCB)==4,"bleConfig_t.readFlashCB bytes");
CHECK(offsetof(bleConfig_t,writeFlashCB)==60,"bleConfig_t.writeFlashCB offset");
CHECK(sizeof(((bleConfig_t*)0)->writeFlashCB)==4,"bleConfig_t.writeFlashCB bytes");
CHECK(sizeof(bleClockConfig_t)==16,"bleClockConfig_t size");
CHECK(ALIGNOF(bleClockConfig_t)==4,"bleClockConfig_t alignment");
CHECK(offsetof(bleClockConfig_t,getClockValue)==0,"bleClockConfig_t.getClockValue offset");
CHECK(sizeof(((bleClockConfig_t*)0)->getClockValue)==4,"bleClockConfig_t.getClockValue bytes");
CHECK(offsetof(bleClockConfig_t,ClockMaxCount)==4,"bleClockConfig_t.ClockMaxCount offset");
CHECK(sizeof(((bleClockConfig_t*)0)->ClockMaxCount)==4,"bleClockConfig_t.ClockMaxCount bytes");
CHECK(offsetof(bleClockConfig_t,ClockFrequency)==8,"bleClockConfig_t.ClockFrequency offset");
CHECK(sizeof(((bleClockConfig_t*)0)->ClockFrequency)==2,"bleClockConfig_t.ClockFrequency bytes");
CHECK(offsetof(bleClockConfig_t,ClockAccuracy)==10,"bleClockConfig_t.ClockAccuracy offset");
CHECK(sizeof(((bleClockConfig_t*)0)->ClockAccuracy)==2,"bleClockConfig_t.ClockAccuracy bytes");
CHECK(offsetof(bleClockConfig_t,irqEnable)==12,"bleClockConfig_t.irqEnable offset");
CHECK(sizeof(((bleClockConfig_t*)0)->irqEnable)==1,"bleClockConfig_t.irqEnable bytes");
DATA const uint32_t tsl9_sdk_boot_layout[60] = {
    (uint32_t)(sizeof(bleConfig_t)),
    (uint32_t)(ALIGNOF(bleConfig_t)),
    (uint32_t)(offsetof(bleConfig_t,MEMAddr)),
    (uint32_t)(offsetof(bleConfig_t,MEMLen)),
    (uint32_t)(offsetof(bleConfig_t,SNVAddr)),
    (uint32_t)(offsetof(bleConfig_t,SNVBlock)),
    (uint32_t)(offsetof(bleConfig_t,SNVNum)),
    (uint32_t)(offsetof(bleConfig_t,BufNumber)),
    (uint32_t)(offsetof(bleConfig_t,BufMaxLen)),
    (uint32_t)(offsetof(bleConfig_t,TxNumEvent)),
    (uint32_t)(offsetof(bleConfig_t,RxNumEvent)),
    (uint32_t)(offsetof(bleConfig_t,TxPower)),
    (uint32_t)(offsetof(bleConfig_t,ConnectNumber)),
    (uint32_t)(offsetof(bleConfig_t,WindowWidening)),
    (uint32_t)(offsetof(bleConfig_t,WaitWindow)),
    (uint32_t)(offsetof(bleConfig_t,MacAddr)),
    (uint32_t)(offsetof(bleConfig_t,ClockFrequency)),
    (uint32_t)(offsetof(bleConfig_t,ClockAccuracy)),
    (uint32_t)(offsetof(bleConfig_t,srandCB)),
    (uint32_t)(offsetof(bleConfig_t,idleCB)),
    (uint32_t)(offsetof(bleConfig_t,tsCB)),
    (uint32_t)(offsetof(bleConfig_t,rcCB)),
    (uint32_t)(offsetof(bleConfig_t,staCB)),
    (uint32_t)(offsetof(bleConfig_t,readFlashCB)),
    (uint32_t)(offsetof(bleConfig_t,writeFlashCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->MEMAddr)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->MEMLen)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->SNVAddr)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->SNVBlock)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->SNVNum)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->BufNumber)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->BufMaxLen)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->TxNumEvent)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->RxNumEvent)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->TxPower)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->ConnectNumber)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->WindowWidening)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->WaitWindow)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->MacAddr)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->ClockFrequency)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->ClockAccuracy)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->srandCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->idleCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->tsCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->rcCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->staCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->readFlashCB)),
    (uint32_t)(sizeof(((bleConfig_t*)0)->writeFlashCB)),
    (uint32_t)(sizeof(bleClockConfig_t)),
    (uint32_t)(ALIGNOF(bleClockConfig_t)),
    (uint32_t)(offsetof(bleClockConfig_t,getClockValue)),
    (uint32_t)(offsetof(bleClockConfig_t,ClockMaxCount)),
    (uint32_t)(offsetof(bleClockConfig_t,ClockFrequency)),
    (uint32_t)(offsetof(bleClockConfig_t,ClockAccuracy)),
    (uint32_t)(offsetof(bleClockConfig_t,irqEnable)),
    (uint32_t)(sizeof(((bleClockConfig_t*)0)->getClockValue)),
    (uint32_t)(sizeof(((bleClockConfig_t*)0)->ClockMaxCount)),
    (uint32_t)(sizeof(((bleClockConfig_t*)0)->ClockFrequency)),
    (uint32_t)(sizeof(((bleClockConfig_t*)0)->ClockAccuracy)),
    (uint32_t)(sizeof(((bleClockConfig_t*)0)->irqEnable))
};
