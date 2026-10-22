#ifndef TSL9_BLE_TRANSPORT_H
#define TSL9_BLE_TRANSPORT_H
#include "dnd_actions.h"
#define BT_API_VERSION 1
#define BT_QUEUE_BASE UINT32_C(0x2000b18c)
#define BT_QUEUE_STRIDE 1062u
#define BT_DESCRIPTOR_BASE UINT32_C(0x2000bdf8)
#define BT_QUERY_ADDRESS UINT32_C(0x20004088)
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {BT_BORROWED,BT_MAPPED} bt_source_kind;
typedef struct {
 bt_source_kind kind;uint32_t address;
 const uint8_t *data,*known;uint32_t available;
} bt_source;
typedef struct {
 uint32_t target,callsite;da_scalar arguments[6];unsigned argument_count;
 int memory_effects_required;
} bt_request;
typedef struct {da_scalar scalar;int memory_effects;} bt_result;
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*write)(void *,uint32_t,uint32_t,unsigned,uint32_t,uint32_t);
 da_flow (*invoke)(void *,const bt_request *,bt_result *);
} bt_backend;
typedef struct {
 const bt_backend *io;da_flow flow;
 uint32_t boundary_va,boundary_address,needed_mask,reads,writes,calls,commits;
 bt_request last_request;
} bt_machine;
/* All memory is supplied by the backend. Numeric RAM/source/ROM addresses are
   original logical identities, never cast to executable host/native pointers.
   A real target backend must prove mapping, ROM ABI and buffer ownership.
   Borrowed source is synchronously read byte-by-byte after header stores;
   it may alias authoritative RAM. No full-source preflight or snapshot.
   Backend table/machine remain alive at stable addresses; non-reentrant calls.
   ROM76 RETURNED must explicitly claim memory_effects=1. Failed providers
   preserve their actual prefix. No original binary execution, heap, device IO.
   Inputs/normal event return retain raw32 bits; do not truncate task/handle.
   ROM420 table identity19A78 still requires an actual linked callback binding. */
void bt_init(bt_machine *,const bt_backend *);
da_flow bt_build(bt_machine *,uint32_t,uint32_t,const bt_source *,uint32_t,da_scalar *);
da_flow bt_events(bt_machine *,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
