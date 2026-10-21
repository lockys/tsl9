#ifndef TSL9_V4160_CLOCK_CONTRACT_H
#define TSL9_V4160_CLOCK_CONTRACT_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own semantic API; numeric addresses are never cast to host pointers. */
typedef enum {VC_RETURNED,VC_HALT,VC_TRANSFER,VC_OBSERVATION_LIMIT} vc_flow;
typedef enum {VC_READ32,VC_WRITE32} vc_kind;
typedef enum {VC_NONE,VC_BACKEND_UNKNOWN,VC_BRANCH_UNKNOWN,VC_BUDGET} vc_boundary;
typedef struct {uint32_t value,known;} vc_word;
typedef struct {vc_kind kind;uint32_t pc,address,value,known;} vc_request;
typedef struct {void *context;vc_flow (*invoke)(void *,const vc_request *,vc_word *);} vc_backend;
typedef struct {
    vc_backend backend;vc_flow flow;vc_boundary boundary;
    uint32_t operations,max_operations,boundary_pc,entry_sp,frame_sp;
    uint32_t hse_samples,pll_samples,switch_samples;
    unsigned frame_entered,frame_restored;
    vc_request last_request;
} vc_model;
void vc_init(vc_model *,const vc_backend *);
/* Original1874A..18834 semantic port. entry_sp is caller-supplied numeric
 * state, not proof of real RAM, IRQ behavior, crystal or hardware validity. */
vc_flow vc_clock(vc_model *,uint32_t entry_sp);
#ifdef __cplusplus
}
#endif
#endif
