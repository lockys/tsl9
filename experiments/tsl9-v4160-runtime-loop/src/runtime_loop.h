#ifndef TSL9_V4160_RUNTIME_LOOP_H
#define TSL9_V4160_RUNTIME_LOOP_H
#include "resident_entry.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Reuse only the prior model's value/flow vocabulary. Runtime source profile is
 * separate from the resident candidate. Fixed frame/data flows, not an ISA
 * interpreter or physical ABI. Numeric target addresses never become pointers.
 * Memory/RET callbacks preserve registers. Whole-callee callbacks may change
 * registers/shared memory but preserve engine control/budget. RETURNED requires
 * explicit returned_to knowledge; zero/default status is never a continuation.
 * Call observation is after the local link-RA assignment, including at unknown
 * target, missing-provider or budget boundaries. A tail call forms no new link.
 * Unrepresented registers/physical effects remain unknown. */
typedef enum { ML_UNKNOWN_IMAGE=0,ML_ID2966_0EE64183=1 } ml_profile;
typedef enum { ML_READ8,ML_READ32,ML_WRITE32,ML_RETURN,ML_CALL } ml_kind;
typedef enum { ML_NONE,ML_BINDING,ML_MISSING_PROVIDER,ML_PROVIDER_STOP,
               ML_PROVIDER_TRANSFER,ML_BUDGET,ML_UNKNOWN_CONDITION,
               ML_UNKNOWN_CONTROL,ML_OTHER_RETURN } ml_boundary;
typedef struct {
    ri_value sp,gp,ra,s[3],a[8];
} ml_registers;
typedef struct {
    ml_kind kind;uint32_t pc,tail;
    ri_value address,data,raw_target,target,continuation;
    ml_registers registers;
} ml_request;
typedef struct {ri_value returned_to;} ml_call_result;
struct ml_model;
typedef struct {
    void *context;
    ri_flow (*effect)(void *,const ml_request *,ri_value *);
    ri_flow (*call)(void *,struct ml_model *,const ml_request *,ml_call_result *);
} ml_backend;
typedef struct ml_model {
    ml_profile profile;ml_backend backend;ml_registers r;
    ri_flow flow;ml_boundary boundary;uint32_t boundary_pc;
    uint32_t operations,budget,calls,iterations,slots_examined;
    ri_value result,return_target;ml_request last_request;
} ml_model;
void ml_init(ml_model *,ml_profile,const ml_backend *);
/* Select a distinct host activation after nonreturn; not native-PC resumption.
 * Preserves registers/provider memory and resets only control diagnostics. */
void ml_new_activation(ml_model *);
ri_flow ml_initialize_9250(ml_model *);
ri_flow ml_loop_8180(ml_model *);
ri_flow ml_main_9008(ml_model *);
/* Separate explicit entry for the source9012 suffix. Never runs automatically
 * after the infinite loop's host budget or nonreturn. */
ri_flow ml_main_suffix_9012(ml_model *);
/* Incoming task/event register snapshots are r.a[0]/r.a[1], without guessed
 * portable C argument types. Callback sees all modeled argument registers. */
ri_flow ml_dispatch_901a(ml_model *);
/* Only exact selected RI MRET with known9008 is admitted. Transfers the available
 * GP/SP/RA/a0/a1/a2/a4/a5 knowledge; other registers remain caller snapshots.
 * This does not infer installed ROM, physical MRET or scheduler ABI. */
ri_flow ml_main_from_resident(ml_model *,const ri_model *);
#ifdef __cplusplus
}
#endif
#endif
