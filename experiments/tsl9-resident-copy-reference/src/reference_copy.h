#ifndef TSL9_REFERENCE_COPY_H
#define TSL9_REFERENCE_COPY_H
#include "uid_helper.h"
#ifdef __cplusplus
extern "C" {
#endif
/* A finite source-specific data/effect model, not a CPU or native ABI adapter.
 * Explicit opt-in names the retained Dec2023 carrier, NOT the physical device.
 * Numeric addresses are never cast to host pointers. Effect callbacks preserve
 * model control; they may change shared synthetic memory, including aliases.
 * RETURNED attests only the declared synthetic primitive. Nonreturn retains all
 * preceding effects and does not run an invented MMIO cleanup/finally block. */
typedef enum { RP_PHYSICAL_UNKNOWN=0, RP_DEC2023_133D3705=1 } rp_profile;
typedef enum { RP_READ32,RP_WRITE32,RP_FENCE_I,RP_READ8,RP_WRITE8,RP_RETURN } rp_kind;
typedef enum { RP_NONE,RP_BINDING,RP_PROVIDER_MISSING,RP_PROVIDER_STOP,
               RP_BUDGET,RP_CONDITION_UNKNOWN } rp_boundary;
typedef struct {
    rp_kind kind;uint32_t pc,index;
    bc_value address,data,raw_target,target;
} rp_request;
typedef struct {
    void *context;
    bc_flow (*effect)(void *,const rp_request *,bc_value *);
} rp_backend;
typedef struct rp_model {
    rp_profile profile;rp_backend backend;
    bc_value destination,source,length,ra,result,saved_mmio,return_target;
    uint32_t index,index_set,operations,budget,stores_returned;
    bc_flow flow;rp_boundary boundary;uint32_t boundary_pc;
    rp_request last_request;
} rp_model;
void rp_init(rp_model *,rp_profile,const rp_backend *);
/* A distinct host activation after HALT/TRANSFER; never original-PC resumption.
 * This resets diagnostics, not the backend's synthetic memory or MMIO state. */
void rp_new_activation(rp_model *);
bc_flow rp_copy(rp_model *,bc_value dst,bc_value src,bc_value n,bc_value ra);
/* Exact selected UB source callsites / BOOT225E seam only. Caller registers
 * are preserved by this reference leaf; writes may alias saved-register data.
 * Shared memory/effect provider and explicit reference profile remain required.
 * No profile substitution for RC_WCH_64BE955_V130 or actual installed ROM. */
bc_flow rp_uid_copy(rp_model *,ub_model *,const ub_request *,bc_value *);
bc_flow rp_boot_copy(rp_model *,const bc_request *,bc_value *);
#ifdef __cplusplus
}
#endif
#endif
