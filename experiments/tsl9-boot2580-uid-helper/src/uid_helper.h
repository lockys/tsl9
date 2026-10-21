#ifndef TSL9_BOOT2580_UID_HELPER_H
#define TSL9_BOOT2580_UID_HELPER_H
#include "boot_command.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Finite source-specific helper/frame-data reconstruction; not a CPU stepper.
 * Numeric addresses never become host pointers. Every effect needs a provider.
 * Engine control/budgets must be preserved by providers. Memory effects preserve
 * modeled registers; copy providers may change sp/s0/s1/s2/ra and synthetic
 * memory. RETURNED for a copy establishes return through its stated continuation
 * only conditionally; it does not prove ROM ABI or physical return control. */
typedef enum { UB_READ8,UB_READ32,UB_WRITE32,UB_COPY,UB_RETURN } ub_kind;
typedef enum { UB_NONE,UB_PROVIDER_MISSING,UB_PROVIDER_STOP,UB_BUDGET,
               UB_UNKNOWN_CONDITION,UB_UNKNOWN_CONTROL,UB_CONTROL_TRANSFER } ub_boundary;
typedef struct {
    ub_kind kind;uint32_t pc,argc,tail;
    bc_value address,data,args[3],slot,raw_target,target,continuation;
} ub_request;
struct ub_model;
typedef struct {
    void *context;
    bc_flow (*effect)(void *,const ub_request *,bc_value *);
    bc_flow (*copy)(void *,struct ub_model *,const ub_request *,bc_value *);
} ub_backend;
typedef struct ub_model {
    ub_backend backend;
    bc_value sp,s0,s1,s2,ra,result,return_target;
    bc_flow flow;ub_boundary boundary;
    uint32_t boundary_pc,operations,budget,compared,copy_attempts;
    ub_request last_request;
} ub_model;
/* Initializers/functions require a valid object. Initial register words are
 * unknown unless the caller supplies a synthetic/source-bound snapshot. */
void ub_init(ub_model *,const ub_backend *);
/* New host activation, not original instruction/control resumption. Does not
 * reset memory or register data; required after HALT/TRANSFER. */
void ub_new_activation(ub_model *);
bc_flow ub_build(ub_model *,bc_value output);
bc_flow ub_compare(ub_model *,bc_value incoming,bc_value length);
/* Thin whole-helper seam for exact BC_IDENTITY sites22AC/22DA only. Uses the
 * command's live bodySP and source return PC; caller supplies saved-register
 * knowledge/backend. SP prefix effects propagate even on nonreturn. A normal
 * return is accepted only with the matching normalized return target. Other
 * known return routes become TRANSFER; unknown routes stop without a success.
 * No device identifiers or packets are assembled by this function. */
bc_flow ub_identity_bridge(bc_model *,const bc_request *,ub_model *,bc_value *);
#ifdef __cplusplus
}
#endif
#endif
