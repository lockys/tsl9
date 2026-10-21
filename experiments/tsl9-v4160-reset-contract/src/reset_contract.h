#ifndef TSL9_V4160_RESET_CONTRACT_H
#define TSL9_V4160_RESET_CONTRACT_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own semantic interface. No CPU execution, target memory cast or driver. */
typedef enum {RC_RETURNED, RC_HALT, RC_TRANSFER, RC_OBSERVATION_LIMIT} rc_flow;
typedef enum {RC_READ32, RC_WRITE32, RC_CSR_WRITE, RC_CSR_SET, RC_CLOCK, RC_HANDOFF} rc_kind;
typedef enum {RC_NO_BOUNDARY, RC_PROVIDER_UNKNOWN, RC_CALLEE_TRANSFER, RC_ROM_BOUNDARY, RC_BUDGET} rc_boundary;
typedef struct {uint32_t value, known;} rc_scalar;
typedef struct {rc_kind kind;uint32_t pc,address,value,known,csr,target;} rc_request;
typedef struct {void *context;rc_flow (*invoke)(void *,const rc_request *,rc_scalar *);} rc_backend;
typedef struct {
    rc_backend backend;rc_flow flow;rc_boundary boundary;
    uint32_t operations,max_operations,boundary_pc,initial_gp,initial_sp;
    uint32_t copied_words,zero_words,handoff_target;
    rc_request last_request;
} rc_model;
void rc_init(rc_model *,const rc_backend *);
/* Original186AA..18734. No original C ABI, physical RAM validity or ROM
 * acceptance is implied. A terminal transfer is a source-analysis boundary. */
rc_flow rc_reset(rc_model *);
#ifdef __cplusplus
}
#endif
#endif
