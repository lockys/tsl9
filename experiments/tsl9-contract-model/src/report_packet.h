#ifndef TSL9_REPORT_PACKET_H
#define TSL9_REPORT_PACKET_H
#include "dnd_actions.h"
#define RP_API_VERSION 2
#define RP_SCRATCH_BYTES 84u
#define RP_DEPENDENCY_BYTES 8u
#define RP_FRAME_OFFSET 8u
#define RP_FRAME_BYTES 76u
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {uint8_t *data,*known;uint32_t length;} rp_storage;
typedef struct {
 uint32_t callsite,target;da_scalar arguments[3];unsigned argument_count;
 uint8_t *buffer,*buffer_known;uint32_t buffer_length;
} rp_request;
typedef struct {da_scalar scalar;int memory_effects;} rp_result;
typedef struct {
 uint32_t callsite,wrapper_va;uint16_t handle;uint8_t command;
 const uint8_t *data,*known;uint32_t length;
} rp_reply;
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*invoke)(void *,const rp_request *,rp_result *);
 da_flow (*reply)(void *,const rp_reply *);
} rp_backend;
typedef struct {
 rp_backend io;rp_storage scratch,dependency;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask,calls,replies;
 rp_request last_request;
} rp_machine;
/* Buffers are real caller-owned C objects. SCRATCH maps the diagnostic native
   SP+12..95 span; this API never invents an integer native SP address.
   ROM72/76 requests use buffer fields; arguments[0]={0,0} is a logical OUT
   identity, never an executable native pointer. A target provider must use the
   actual buffer address and prove the ROM ABI. Calls are synchronous; providers
   must not retain scratch pointers after run returns. No heap or device IO.
   Returned ROM72/76 effects must explicitly set result.memory_effects=1 and
   supply every output byte/mask; a returned no-op is an unclosed contract.
   HALT/TRANSFER may leave a partial effect and never rolls it back.
   Missing/failed effects retain preceding scratch and authoritative RAM prefix.
   Incidental native a0 is deliberately not exposed as a fabricated scalar. */
void rp_init(rp_machine *,const rp_backend *,rp_storage,rp_storage);
da_flow rp_run_a0(rp_machine *,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
