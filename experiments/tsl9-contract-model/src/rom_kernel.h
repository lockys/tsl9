#ifndef TSL9_ROM_KERNEL_H
#define TSL9_ROM_KERNEL_H
#include "rom_candidate.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { RK_RETURNED, RK_HALT, RK_TRANSFER } rk_flow;
typedef enum { RK_MMIO_READ, RK_MMIO_WRITE, RK_FENCE_I, RK_NATIVE_CALL, RK_TASK_HANDLER } rk_kind;
typedef struct {rk_kind kind;uint32_t callsite,target,arguments[4];unsigned count,width;} rk_request;
typedef struct {uint32_t value,known;} rk_result;
struct rk_model;
typedef struct {
    void *context;
    /* Explicit synthetic boundary. Native task handlers return an event mask;
       indirect and radio/idle calls require known-return flow, never default noop. */
    rk_flow (*invoke)(void *,struct rk_model *,const rk_request *,rk_result *);
} rk_backend;
typedef struct rk_model {
    rc_adapter *candidate;tf_model *memory;rk_backend backend;
    rk_flow flow;rk_request last_request;
    uint32_t unknown_va,unknown_address,operations,handlers,callbacks;
} rk_model;
int rk_attach(rk_model *,rc_adapter *,const rk_backend *);
void rk_resume(rk_model *);
/* No allocation or freeing: native4314A simply zeros the shared queue head. */
rk_flow rk_queue_reset(rk_model *);
/* Declared task ABI is U8; register methods preserve the full entry register
   before native comparisons. Return flow does not conflate status with success. */
rk_flow rk_msg_send(rk_model *,uint8_t,uint32_t,uint32_t *);
rk_flow rk_msg_send_register(rk_model *,uint32_t,uint32_t,uint32_t *);
rk_flow rk_msg_receive(rk_model *,uint8_t,uint32_t *);
rk_flow rk_msg_receive_register(rk_model *,uint32_t,uint32_t *);
/* Complete selected SystemProcess control body. Deep radio/idle and handlers
   remain typed providers. Native loop can starve; host guard is explicit HALT. */
rk_flow rk_system_process(rk_model *);
rk_flow rk_internal_dispatch(rk_model *,uint8_t,uint16_t,uint16_t *);
rk_flow rk_internal_message_dispatch(rk_model *,uint8_t,uint16_t,uint16_t *);
#ifdef __cplusplus
}
#endif
#endif
