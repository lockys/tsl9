#ifndef TSL9_V4160_SYSTEM_CLOCK_QUERY_H
#define TSL9_V4160_SYSTEM_CLOCK_QUERY_H
#include "runtime_loop.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Source-specific numeric host dataflow, never original/ISA execution. A memory
 * provider preserves engine control/budget and supplies register/RAM knowledge
 * explicitly; any change of registers
 * is a separately declared synthetic environment effect, not proof of physical
 * interrupts or ABI. Requests snapshot state before the effect. Addresses never
 * become host pointers. Unknown arithmetic remains conservative bit knowledge.
 * RETURN observes a raw/normalized target, not an original callee return value. */
typedef enum { SF_UNKNOWN_IMAGE=0,SF_ID2966_0EE64183=1 } sf_profile;
typedef enum { SF_READ32,SF_READ8,SF_WRITE32,SF_WRITE8,SF_WRITE16,SF_RETURN } sf_kind;
typedef enum { SF_NONE,SF_BINDING,SF_MISSING_PROVIDER,SF_PROVIDER_STOP,
               SF_PROVIDER_TRANSFER,SF_BUDGET,SF_UNKNOWN_CONDITION } sf_boundary;
typedef struct {
    sf_kind kind;uint32_t pc;ri_value address,data,raw_target,target;
    ml_registers registers;
} sf_request;
struct sf_model;
typedef struct {
    void *context;
    ri_flow (*effect)(void *,struct sf_model *,const sf_request *,ri_value *);
} sf_backend;
typedef struct sf_model {
    sf_profile profile;sf_backend backend;ml_registers r;
    ri_flow flow;sf_boundary boundary;uint32_t boundary_pc,operations,budget;
    ri_value return_target;sf_request last_request;
} sf_model;
void sf_init(sf_model *,sf_profile,const sf_backend *);
/* Distinct host activation only; preserves registers/provider memory/budget. */
void sf_new_activation(sf_model *);
ri_flow sf_query_18834(sf_model *);
ri_flow sf_derive_1973c(sf_model *);
/* Exact original ML9254->18834/925C->1973C only. Transfers all represented
 * registers and explicit return knowledge. The middle9A42 remains a provider.
 * SF/ML observation budgets and nonreturns stay distinct. No new native ABI. */
ri_flow sf_ml_init_call(sf_model *,ml_model *,const ml_request *,ml_call_result *);
#ifdef __cplusplus
}
#endif
#endif
