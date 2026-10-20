#ifndef TSL9_GATT_RUNTIME_H
#define TSL9_GATT_RUNTIME_H
#include "ble_role.h"
#include "gatt_parser.h"
#define GR_API_VERSION 1
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 da_flow (*reserved0)(void *);
 da_flow (*write)(void *,uint32_t,const bt_source *,const bt_source *,uint32_t,uint32_t,da_scalar *);
 da_flow (*reserved2)(void *);
} gr_callbacks;
typedef struct {
 const gr_callbacks *callbacks;void *context;uint32_t original_table_va;
} gr_gatt_binding;
typedef struct {
 uint32_t target,callsite;da_scalar arguments[4];unsigned argument_count;
} gr_registration_request;
typedef struct {
 br_backend role;
 da_flow (*gatt_invoke)(void *,const gp_request *,da_scalar *);
 da_flow (*register_attributes)(void *,const gr_registration_request *,const gr_gatt_binding *,da_scalar *);
} gr_backend;
typedef struct {
 const gr_backend *io;br_machine role;gp_machine gatt;
 br_backend role_backend;gp_backend gatt_backend;gr_gatt_binding binding;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask;int path;
} gr_machine;
/* Portable context-aware read-only C table {NULL,write,NULL}, not a physical
   ROM ABI. Provider may retain binding while machine lives. Original19A94 is
   identity only. register_attributes models ONLY ROM304 component at8FA4,
   args GP,4,16,actual typed binding; meanings/attribute extent remain unknown.
   Table pointer numeric operand is unknown, never original executable address.
   Uses role.runtime.core.context/RAM and its DA_ROM124 clock provider.
   Binding public calls and retained callbacks are non-reentrant; IRQ/ROM thunks,
   full startup and native ABI remain unproved. TRANSFER closes both children. */
void gr_init(gr_machine *,const gr_backend *,rp_storage,rp_storage,bl_storage);
da_flow gr_write(gr_machine *,uint32_t,const bt_source *,const bt_source *,uint32_t,uint32_t,da_scalar *);
da_flow gr_register_attributes(gr_machine *,da_scalar *);
da_flow gr_run_pair(gr_machine *,uint32_t,uint32_t,uint32_t,da_scalar *);
da_flow gr_events(gr_machine *,uint32_t,uint32_t,da_scalar *);
da_flow gr_build(gr_machine *,uint32_t,uint32_t,const bt_source *,uint32_t,da_scalar *);
da_flow gr_state(gr_machine *,uint32_t,const bt_source *,da_scalar *);
da_flow gr_parameters(gr_machine *,uint32_t,uint32_t,uint32_t,uint32_t,da_scalar *);
da_flow gr_registration(gr_machine *,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
