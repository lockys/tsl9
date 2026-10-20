#ifndef TSL9_SPI_CAN_H
#define TSL9_SPI_CAN_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { SC_RETURNED,SC_HALT,SC_TRANSFER } sc_flow;
typedef enum { SC_NONE,SC_RAM,SC_VIEW } sc_buffer_kind;
typedef struct {
    sc_buffer_kind kind;
    uint32_t address;
    uint8_t *data,*known;
    uint32_t available;
} sc_buffer;
typedef enum {
    SC_MMIO_READ,SC_MMIO_WRITE,SC_CSR_CLEAR,SC_CSR_SET,
    SC_ROM_COPY,SC_ROM_MEMSET,SC_ROM_CALL,SC_INTERRUPT_RETURN
} sc_operation;
typedef struct {
    sc_operation operation;
    uint32_t va,target,value,known;
    unsigned width,slot,count;
    uint32_t arguments[3],argument_known[3],length;
    sc_buffer source,destination;
} sc_request;
typedef struct {
    uint32_t value,known;
    /* COPY/MEMSET require explicit completion of described byte/mask effects.
       The provider applies them to live views or the same tf_model SRAM. */
    int memory_effects;
} sc_result;
struct sc_model;
typedef struct {
    void *context;
    sc_flow (*invoke)(void *,struct sc_model *,const sc_request *,sc_result *);
} sc_backend;
typedef struct sc_model {
    tf_model *memory;
    sc_backend backend;
    sc_flow flow;
    sc_request last_request;
    uint32_t unknown_va,unknown_address,operations,spin_budget;
    uint32_t result,result_known;
    int result_defined;
    uint32_t queued,queue_full,rx_rejected;
    uint8_t received[20],received_known[20];
    unsigned received_length;
} sc_model;
typedef struct { uint32_t registers[4];sc_buffer buffer; } sc_arguments;
enum {
    SC_TIME_MS=0x81B0,SC_GATE=0x8214,SC_RELOAD=0x165CC,SC_SPI_BYTE=0x1660A,
    SC_WRITE_BYTES=0x16652,SC_MODIFY=0x166B2,SC_READ_REGISTER=0x16708,
    SC_SET_MODE=0x16750,SC_WRITE_REGISTER=0x167A4,SC_RECEIVE_BUFFER=0x167F0,
    SC_RECEIVE_PENDING=0x1687E,SC_SET_MASK=0x168C4,SC_SEND=0x168F0,
    SC_ACCEPT_ALL=0x169E6,SC_FILTERS=0x16A38,SC_CLEAR_FILTERS=0x16B20,
    SC_SPECIAL_FILTERS=0x16B48,SC_RESET=0x16B78,SC_CONTROLLER_INIT=0x16BF4,
    SC_TASK=0x16C6C,SC_EXTI_IRQ=0x16D22,SC_DRAIN=0x16D6E,
    SC_PERIPHERAL_INIT=0x16DAC,SC_QUEUE=0x129D8,SC_ROUTE_SEND=0x12864,
    SC_ROUTE_FILTERS=0x1290A,SC_CAN_FIFO0_IRQ=0x12A34,
    SC_CAN_TRANSMIT=0x189F8,SC_CAN_RECEIVE=0x18ACC,
    SC_CHANNEL0_FILTERS=0x12780,SC_CHANNEL0_CLEAR=0x12820,
    SC_ROUTE_CLEAR=0x128EC,SC_MODE_CLEANUP=0x1291C,
    SC_NATIVE_FILTER_INIT=0x188F6,SC_STATE_CLEANUP=0x10586,
    SC_CANCEL_CALLBACK=0x908E
};
#define SC_QUEUE_ADDRESS UINT32_C(0x2000C034)
#define SC_FLAGS_ADDRESS UINT32_C(0x20004168)
#define SC_TASK_ADDRESS UINT32_C(0x2000416B)
/* Explicit host flow restart only; no native-PC/stack/IRQ resume is claimed. */
void sc_init(sc_model *,tf_model *,const sc_backend *);
void sc_resume(sc_model *);
/* registers are original raw32 operands. Buffer binds the native pointer operand:
   SEND/ROUTE_SEND -> a0; WRITE_BYTES -> a2; FILTERS/QUEUE -> a1;
   CAN_TRANSMIT -> a1; CAN_RECEIVE -> a2. VIEW is a live host byte/mask view,
   never a fabricated native stack address. Other arguments keep native widths.
   CHANNEL0_FILTERS -> a0 buffer, a1 raw32 byte count (native cap112);
   NATIVE_FILTER_INIT -> a0 live20-byte descriptor; MODE_CLEANUP -> raw32 a0;
   ROUTE_CLEAR -> raw32 channel a0; CANCEL_CALLBACK -> raw32 callback a0.
   CHANNEL0_CLEAR/STATE_CLEANUP take no operands. Successful TASK event1
   executes complete mode0 cleanup then returns events XOR1. MODE_CLEANUP1
   includes the fixed110-byte/aligned ROM199FC source path of native19944; its general
   overlapping/unaligned memcpy entry is not exported or claimed closed.
   Missing primitive provider preserves prefix and halts; no default noop.
   Void/unchecked caller results have result_defined=0 instead of guessed zero.
   MRET requires explicit SC_TRANSFER from SC_INTERRUPT_RETURN. */
sc_flow sc_run(sc_model *,uint32_t,const sc_arguments *);
#ifdef __cplusplus
}
#endif
#endif

