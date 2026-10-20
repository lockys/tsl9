#ifndef TSL9_CAN_RECEIVE_H
#define TSL9_CAN_RECEIVE_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { CR_RETURNED,CR_HALT,CR_TRANSFER } cr_flow;
typedef enum { CR_NONE,CR_RAM,CR_VIEW } cr_buffer_kind;
typedef struct { cr_buffer_kind kind;uint32_t address;uint8_t *data,*known;uint32_t available; } cr_buffer;
typedef struct { uint32_t value,known; } cr_scalar;
typedef enum {
 CR_COPY,CR_FREE,CR_ALLOC,CR_CSR_CLEAR,CR_CSR_SET,
 CR_MMIO_READ,CR_MMIO_WRITE,CR_REPLY,CR_D1_TAIL,CR_NATIVE_CALL
} cr_operation;
typedef struct {
 cr_operation operation;uint32_t va,target;unsigned slot,width,count;
 uint32_t arguments[4],argument_known[4],value,known,length;
 cr_buffer source,destination;
} cr_request;
typedef struct { uint32_t value,known;int memory_effects; } cr_result;
struct cr_model;
typedef struct { void *context;cr_flow (*invoke)(void *,struct cr_model *,const cr_request *,cr_result *); } cr_backend;
typedef struct cr_model {
 tf_model *memory;cr_backend backend;cr_flow flow;cr_request last_request;
 uint32_t boundary_va,boundary_address,needed_mask,operations;
 uint32_t result,result_known;int result_defined;
 uint32_t consumed,debug_calls,debug_replies,d1_calls,dispatch_calls;
 uint8_t debug_value[60],debug_known[60];
 /* Diagnostic abstract byte views only; authoritative native SRAM is memory. */
 uint8_t record_value[12],record_known[12],control_value[12],control_known[12];
} cr_model;
typedef struct { cr_buffer record;cr_scalar argument; } cr_arguments;
enum {
 CR_QUEUE=0x12A68,CR_DEBUG=0x82C8,CR_DISPATCH=0x14AF8,
 CR_CLEAR_COUNTER=0x8202,CR_PULSE_ALLOC=0x93EE,CR_PULSE_BUILD=0x9432,
 CR_PULSE_START=0x9388,CR_PULSE_STOP=0x93CC,CR_TOGGLE=0x9B14
};
void cr_init(cr_model *,tf_model *,const cr_backend *);
void cr_resume(cr_model *);
cr_flow cr_run(cr_model *,uint32_t,const cr_arguments *);
/* Real entries only:15048 is an internal tail, not a callable entry.
   RAM binds a native SRAM pointer. VIEW binds a synchronous borrowed abstract
   record; address stays0, never a fabricated native SP. Queue COPY creates a
   12-byte VIEW before clearing native queue ID. No second native SRAM exists.
   COPY providers apply byte/mask effects and set memory_effects; all external
   flow is explicit. CR_REPLY maps actual8CFA; CR_D1_TAIL maps completed139E6;
   CR_NATIVE_CALL is limited to existing SC1290A/12864 body adapters. Other
   unported dispatcher leaves HALT at source selection, not opaque fallback.
   Debug's raw auth scalar can have unknown irrelevant bits while flow returns.
   COPY cached DLC and reply live DLC differ by native reread; no added guard.
   CR_TRANSFER never means RETURNED or unknown. last_request VIEW pointers are
   sanitized; immediate provider has live views. resume is host restart only. */
#ifdef __cplusplus
}
#endif
#endif
