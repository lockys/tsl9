#ifndef TSL9_GENERAL_DEEP_H
#define TSL9_GENERAL_DEEP_H
#include "general_ble.h"
#define GD_PACKET_API_VERSION 2
#ifdef __cplusplus
extern "C" {
#endif
struct gd_model;
typedef enum { GD_NATIVE, GD_ROM } gd_kind;
typedef struct {
    gd_kind kind;uint32_t callsite,target;
    uint32_t arguments[4],known[4];unsigned argument_count;
    uint8_t *buffer,*buffer_known;size_t buffer_length;
} gd_request;
typedef struct {
    void *context;
    /* ROM target is table byte offset (72/76/96), never guessed entryVA.
       Abstract OUT pointer has known[0]=0;source pointer/callsite explicit. */
    gb_flow (*invoke)(void *,struct gd_model *,const gd_request *,gb_scalar *);
    gb_flow (*reply)(void *,struct gd_model *,const gb_reply_request *);
} gd_backend;
typedef struct gd_model {
    tf_model *memory;gd_backend backend;
    gb_flow flow;uint32_t entry,argument,boundary_va,boundary_address,needed_mask;
    gd_request last_request;
    /* Abstract caller SP+12..95, never assigned a native address or treated
       as authoritative SRAM. A0 frame is stack+8/76B;B0 is stack/33B. */
    uint8_t stack[84],known[84];
    /* 9D9E has a separate callee stack OUT8 before caller descriptor stores. */
    uint8_t dependency_out[8],dependency_known[8];
    size_t frame_offset,frame_length;
    uint32_t calls,replies;uint8_t recognized;
} gd_model;
void gd_init(gd_model *,tf_model *,const gd_backend *);
/* Selected13160 uses the same freestanding report_packet body and these
   caller-owned scratch arrays;135D4 retains its existing host implementation.
   Legacy GD_ROM RETURNED declares all requested OUT bytes/masks supplied;
   RP's explicit memory_effects marker maps that existing provider contract.
   This adapter does not prove physical ROM semantics or native stack layout.
   Incidental a0 return is not exposed:
   GH callers/registry overwrite or ignore it; no guessed known scalar return.
   Missing dependency/needed unknown scalar stops with prefix retained. */
gb_flow gd_dispatch(gd_model *,uint32_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
