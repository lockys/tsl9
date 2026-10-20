#ifndef TSL9_BLE_LIFECYCLE_H
#define TSL9_BLE_LIFECYCLE_H
#include "ble_transport.h"
#define BL_API_VERSION 1
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint8_t *advertise,*advertise_known;
 uint16_t *mtu,*mtu_known;
} bl_storage;
typedef struct {
 uint32_t target,callsite;da_scalar arguments[3];unsigned argument_count;
 const uint8_t *byte,*byte_known;
 const uint16_t *half,*half_known;
} bl_request;
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*write)(void *,uint32_t,uint32_t,unsigned,uint32_t,uint32_t);
 da_flow (*invoke)(void *,const bl_request *,da_scalar *);
} bl_backend;
typedef struct {
 const bl_backend *io;bl_storage storage;da_flow flow;
 uint32_t boundary_va,boundary_address,needed_mask,calls,reads,writes;
 bl_request last_request;
} bl_machine;
/* Caller owns distinct U8 advertise and U16 MTU C objects plus masks.
   Typed pointers replace logical original stack arguments, never fake SP.
   Provider callbacks are synchronous and must not retain these local values.
   Source view descriptor is snapshotted; source bytes remain live after calls.
   API names describe inferred roles, not verified resident-ROM prototypes.
   Backend/machine/storage must outlive calls at stable addresses, non-reentrant. */
void bl_init(bl_machine *,const bl_backend *,bl_storage);
da_flow bl_advertise(bl_machine *,uint32_t,da_scalar *);
da_flow bl_registration(bl_machine *,uint32_t,uint32_t,da_scalar *);
da_flow bl_state(bl_machine *,uint32_t,const bt_source *,da_scalar *);
da_flow bl_parameters(bl_machine *,uint32_t,uint32_t,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
