#ifndef TSL9_DND_REPORT_H
#define TSL9_DND_REPORT_H
#include "report_packet.h"
#define DR_API_VERSION 1
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 da_backend core;
 da_flow (*report_invoke)(void *,const rp_request *,rp_result *);
 da_flow (*report_reply)(void *,const rp_reply *);
} dr_backend;
typedef struct {
 const dr_backend *io;da_machine core;rp_machine packet;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask;
 int packet_invoked;
} dr_machine;
/* The backend table and machine must outlive all calls and remain at stable
   addresses until reinitialized. Calls are synchronous and non-reentrant.
   RP and DA share core.read and core.context; no second native RAM model.
   Native identity13160 is an ordinary C call to RP, never a numeric function
   pointer cast. Buffer pointers cannot be retained after run returns.
   ROM/MMIO/scheduling/8CFA effects are still explicit external contracts;
   this binder supplies no startup, ISR, ROM ABI or physical transport. */
void dr_init(dr_machine *,const dr_backend *,rp_storage,rp_storage);
da_flow dr_run_pair(dr_machine *,uint32_t,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
