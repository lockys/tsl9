#ifndef TSL9_V4160_GATT_INGRESS_H
#define TSL9_V4160_GATT_INGRESS_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own semantic interface; no original callback ABI or physical memory access. */
typedef enum {GI_RETURNED,GI_HALT,GI_TRANSFER,GI_OBSERVATION_LIMIT} gi_flow;
typedef enum {GI_READ,GI_WRITE,GI_CLOCK,GI_CCC,GI_DISPATCH} gi_kind;
typedef enum {GI_NONE,GI_PROVIDER_UNKNOWN,GI_OPERAND_UNKNOWN,GI_CONDITION_UNKNOWN,GI_BUDGET} gi_boundary;
typedef struct {uint32_t value,known;} gi_scalar;
typedef struct {
    gi_kind kind;uint32_t pc,target,address,width,value,known,args[6];
} gi_request;
typedef struct {void *context;gi_flow (*invoke)(void *,const gi_request *,gi_scalar *);} gi_backend;
typedef struct {
    gi_backend backend;uint32_t gp,gp_known,max_operations,operations,index;
    gi_flow flow;gi_boundary boundary;uint32_t boundary_pc,dispatches;
    gi_scalar result;gi_request last_request;
} gi_model;
void gi_init(gi_model *,const gi_backend *);
/* The source compares low16(index) against the full original a3 length.
 * max_operations is an observer budget, never an invented target length guard. */
gi_flow gi_receive(gi_model *,uint32_t context,uint32_t attribute,uint32_t chunk,
                   uint32_t length,uint32_t offset,uint32_t method);
#ifdef __cplusplus
}
#endif
#endif
