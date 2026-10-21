#ifndef TSL9_WCH_MEMCMP_CONTRACT_H
#define TSL9_WCH_MEMCMP_CONTRACT_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own semantic API. Numeric target addresses never become host pointers. */
typedef enum { MC_READ32, MC_WRITE32, MC_FENCE_I, MC_READ8 } mc_kind;
typedef enum { MC_RETURNED, MC_BACKEND_UNKNOWN, MC_PROFILE_UNKNOWN,
               MC_OBSERVATION_LIMIT } mc_flow;
typedef struct { mc_kind kind; uint32_t pc, address, value; } mc_request;
/* Zero means unknown completion/effects, not a target return value. */
typedef struct { void *context;
    int (*invoke)(void *, const mc_request *, uint32_t *);
} mc_backend;
typedef struct {
    mc_backend backend;
    mc_request last;
    uint32_t operations, max_operations, saved_mmio, return_value, boundary_pc;
    unsigned saved_known, restored, return_known, xwchc_profile;
    mc_flow flow;
} mc_model;
void mc_init(mc_model *, const mc_backend *, unsigned xwchc_profile);
/* Conditional port of the SDK reference resident RAM[20000442,2000048A).
 * Not proof of installed TSL9 ROM, ABI, interrupt behavior or OTA readiness. */
mc_flow mc_compare(mc_model *, uint32_t src1, uint32_t src2, uint32_t length);
#ifdef __cplusplus
}
#endif
#endif
