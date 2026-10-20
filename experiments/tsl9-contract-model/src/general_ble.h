#ifndef TSL9_GENERAL_BLE_H
#define TSL9_GENERAL_BLE_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { GB_RETURNED, GB_HALT, GB_TRANSFER } gb_flow;
typedef enum { GB_NATIVE_HELPER, GB_ROM_ALLOC, GB_ROM_FREE, GB_ROM_COPY,
               GB_ROM_ZERO, GB_STACK_BOUNDARY, GB_MEMORY_BOUNDARY } gb_call_kind;
typedef struct { uint32_t value,known; } gb_scalar;
typedef struct {
    gb_call_kind kind;
    uint32_t callsite,target; /* ROM target is table byte offset, never guessed VA. */
    uint32_t arguments[4],known[4];unsigned argument_count;
    /* Explicit abstract stack/out buffer, distinct from a mapped native pointer.
       Callback may populate OUT bytes/masks only when its contract establishes them. */
    uint8_t *buffer,*buffer_known;size_t buffer_length;
} gb_request;
typedef struct {
    uint32_t wrapper_va,source_address; /* source_address0 denotes abstract stack. */
    uint16_t handle;uint8_t command;
    const uint8_t *data,*known;size_t length;
    size_t available;int bounded; /* Explicit borrowed span;0 bounded permits no readable bytes. */
} gb_reply_request;
struct gb_model;
typedef struct {
    void *context;
    /* No default return/noop: missing invoke is an explicit unclosed call. */
    gb_flow (*invoke)(void *,struct gb_model *,const gb_request *,gb_scalar *);
    gb_flow (*reply)(void *,struct gb_model *,const gb_reply_request *);
    /* Original delay, before low32(delay*1000)/625 conversion. */
    gb_flow (*schedule)(void *,struct gb_model *,uint32_t,uint32_t,uint32_t,uint32_t,gb_scalar *);
    /* Only outside-SRAM sources, including UID/Flash; never logs real identity. */
    void (*read)(void *,uint32_t,uint8_t *,uint8_t *,size_t);
    /* Complete14254/144CE post-auth command leaf adapter. Auth/eligibility in
       gb_dispatch precede it; missing hook retains the declared standalone slice. */
    gb_flow (*report_command)(void *,struct gb_model *,uint16_t,uint8_t,uint32_t,uint16_t);
} gb_backend;
typedef struct gb_model {
    tf_model *memory;gb_backend backend;
    gb_flow flow;uint16_t handle,length;uint8_t command,recognized;
    uint32_t payload_address,leaf,boundary_va,boundary_address;
    uint32_t transfer_va,transfer_address; /* Declared nonreturn, not an unknown frontier. */
    gb_request last_request;
    uint8_t boundary_buffer[1040],boundary_known[1040];
    uint32_t helper_calls,reply_calls,schedule_calls;
} gb_model;
void gb_init(gb_model *,tf_model *,const gb_backend *);
/* Native Runtime callback arguments. Incoming payload is already parser-validated
   length<=1040 and points to authoritative SRAM (normally2000B9D8). On GB_HALT,
   preserve all earlier writes; halt is an interpretation boundary, not native rejection. */
gb_flow gb_dispatch(gb_model *,uint16_t,uint8_t,uint32_t,uint16_t);
/* Native13C22 /139BA RAM slices, available for bridge connection callbacks too. */
gb_flow gb_registration(gb_model *,uint16_t,uint32_t);
gb_flow gb_report_mode(gb_model *,uint16_t,uint8_t);
#ifdef __cplusplus
}
#endif
#endif
