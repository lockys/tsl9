#ifndef TSL9_GATT_PARSER_H
#define TSL9_GATT_PARSER_H
#include "ble_transport.h"
#define GP_API_VERSION 1
#define GP_RX_ADDRESS UINT32_C(0x2000b9d8)
#define GP_RX_CAPACITY 1040u
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {GP_ROM,GP_NATIVE} gp_kind;
typedef struct {
 gp_kind kind;uint32_t target,callsite;da_scalar arguments[6];unsigned argument_count;
 bt_source attribute,payload;
} gp_request;
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*write)(void *,uint32_t,uint32_t,unsigned,uint32_t,uint32_t);
 da_flow (*invoke)(void *,const gp_request *,da_scalar *);
} gp_backend;
typedef struct {
 const gp_backend *io;da_machine clock;da_backend clock_backend;
 da_flow flow;uint32_t boundary_va,boundary_address,needed_mask,reads,writes,calls,bytes,dispatches;
 gp_request last_request;int clock_returned;da_scalar clock_raw;
} gp_machine;
/* Complete 8B2E body, numeric addresses are logical identities only.
   Attribute/value descriptors are copied; pointed bytes stay live and may alias
   authoritative RAM. Attribute word4 is a logical UUID pointer even in borrowed
   views. No full-span preflight. Dispatch13E6A remains a required provider.
   CCCD324 forwards original operands/views, replacing sixth operand with 1.
   Raw32 length is NOT truncated: native loop compares low16(index) with raw32
   length; >65535 cannot finish normally. Supply bounded views/providers; no
   unbounded mapped reads in host tests. No invented target rejection or fuel.
   Stable machine/backend addresses, synchronous non-reentrant calls. Providers
   must not retain borrowed views. last_request is an unowned diagnostic copy;
   it does not extend buffer lifetime and must not be dereferenced afterwards.
   TRANSFER is sticky. No target IO or physical callback ABI. */
void gp_init(gp_machine *,const gp_backend *);
da_flow gp_write(gp_machine *,uint32_t,const bt_source *,const bt_source *,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
