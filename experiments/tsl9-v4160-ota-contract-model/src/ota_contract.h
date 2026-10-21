#ifndef TSL9_V4160_OTA_CONTRACT_H
#define TSL9_V4160_OTA_CONTRACT_H
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own host-model interface, not the original C ABI or a wire sender. Numeric
 * memory/callee requests require explicit synthetic providers. */
typedef enum {OC_RETURNED,OC_HALT,OC_TRANSFER} oc_flow;
typedef enum {OC_READ8,OC_READ32,OC_WRITE8,OC_IDENTITY,OC_COPY,OC_PROGRAM256,OC_ALLOC,OC_TX,OC_RELEASE,OC_SCHEDULE,OC_SMALL_REPLY} oc_kind;
typedef enum {OC_NO_BOUNDARY,OC_PROVIDER_UNKNOWN,OC_OPERAND_UNKNOWN,OC_CONDITION_UNKNOWN} oc_boundary;
typedef struct {
    oc_kind kind;uint32_t pc,target,address,source,length,value,known,connection,command;
    uint8_t payload[2],payload_known[2];
} oc_request;
typedef struct {uint32_t value,known;} oc_scalar;
typedef struct {void *context;oc_flow (*invoke)(void *,const oc_request *,oc_scalar *);} oc_backend;
typedef struct {
    oc_backend backend;oc_flow flow;oc_boundary boundary;oc_request last_request;
    uint32_t gp,gp_known,boundary_pc,operations,program_calls,response_attempts,page,page_known;
} oc_model;
void oc_init(oc_model *,const oc_backend *);
/* Original9C4A register relations a0=connection,a1=command,a2=payload,a3=len.
 * This models that body, not parser/registration or original-hardware success.
 * No fabricated original a0 return value is exposed. */
oc_flow oc_dispatch(oc_model *,uint32_t,uint32_t,uint32_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
