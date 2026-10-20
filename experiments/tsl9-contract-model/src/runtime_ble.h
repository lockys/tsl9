#ifndef TSL9_RUNTIME_BLE_H
#define TSL9_RUNTIME_BLE_H
#include "dnd_report.h"
#include "ble_transport.h"
#define RTB_API_VERSION 1
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 da_backend core;
 da_flow (*report_invoke)(void *,const rp_request *,rp_result *);
 da_flow (*transport_invoke)(void *,const bt_request *,bt_result *);
} rtb_backend;
typedef struct {
 const rtb_backend *io;dr_machine logic;bt_machine transport;
 dr_backend logic_backend;bt_backend transport_backend;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask;
 int transport_used;
} rtb_machine;
/* Caller owns stable machine/backend and RP buffers for all synchronous calls.
   DA/RP/BT use the same core.context/read/write. Reply is a direct C builder
   call, not an external opaque8CFA callback. ROM effects remain providers.
   No linked image, startup, IRQ, ROM ABI or over-air delivery is supplied. */
void rtb_init(rtb_machine *,const rtb_backend *,rp_storage,rp_storage);
da_flow rtb_run_pair(rtb_machine *,uint32_t,uint32_t,uint32_t,da_scalar *);
da_flow rtb_events(rtb_machine *,uint32_t,uint32_t,da_scalar *);
da_flow rtb_build(rtb_machine *,uint32_t,uint32_t,const bt_source *,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
