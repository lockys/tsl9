#ifndef TSL9_BLE_ROLE_H
#define TSL9_BLE_ROLE_H
#include "runtime_ble.h"
#include "ble_lifecycle.h"
#define BR_API_VERSION 1
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 da_flow (*state_changed)(void *,uint32_t,const bt_source *,da_scalar *);
 da_flow (*reserved)(void *);
 da_flow (*parameters_changed)(void *,uint32_t,uint32_t,uint32_t,uint32_t,da_scalar *);
} br_callbacks;
typedef struct {
 const br_callbacks *callbacks;void *context;uint32_t original_table_va;
} br_role_binding;
typedef struct {
 rtb_backend runtime;
 da_flow (*lifecycle_invoke)(void *,const bl_request *,da_scalar *);
 da_flow (*role_start)(void *,const bt_request *,const br_role_binding *,bt_result *);
} br_backend;
typedef struct {
 const br_backend *io;rtb_machine runtime;bl_machine lifecycle;
 rtb_backend runtime_backend;bl_backend lifecycle_backend;br_role_binding binding;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask;int lifecycle_used;
} br_machine;
/* Portable callback/context descriptor, NOT the physical resident-ROM table.
   Callback prototypes, table extent and native no-context thunks remain
   unverified. Never cast this descriptor or its C callbacks to a ROM table.
   role_start receives logical arg2 unknown plus this actual typed binding;
   the original19A78 is identity only, never an executable pointer.
   Binding/table/context may be retained while caller-owned machine is alive.
   RP buffers and BL U8/U16 objects are borrowed synchronously, not retained.
   Stable addresses, same runtime.core.context/RAM, non-reentrant API. */
void br_init(br_machine *,const br_backend *,rp_storage,rp_storage,bl_storage);
da_flow br_run_pair(br_machine *,uint32_t,uint32_t,uint32_t,da_scalar *);
da_flow br_events(br_machine *,uint32_t,uint32_t,da_scalar *);
da_flow br_build(br_machine *,uint32_t,uint32_t,const bt_source *,uint32_t,da_scalar *);
da_flow br_state(br_machine *,uint32_t,const bt_source *,da_scalar *);
da_flow br_parameters(br_machine *,uint32_t,uint32_t,uint32_t,uint32_t,da_scalar *);
da_flow br_registration(br_machine *,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
