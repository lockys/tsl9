#ifndef TSL9_GENERAL_REPORTS_H
#define TSL9_GENERAL_REPORTS_H
#include "general_ble.h"
#ifdef __cplusplus
extern "C" {
#endif
struct gr_model;
typedef struct {
    uint32_t callsite,target,arguments[3],known[3]; /* ROM table offsets72/76 only. */
    uint8_t *buffer,*buffer_known;size_t buffer_length;
    const uint8_t *input,*input_known; /* abstract VALUE_VIEW source when known[1]=0 */
} gr_request;
typedef struct {
    void *context;
    gb_flow (*invoke)(void *,struct gr_model *,const gr_request *,gb_scalar *);
    gb_flow (*reply)(void *,struct gr_model *,const gb_reply_request *);
} gr_backend;
typedef struct {
    uint32_t address; /* Nonzero mapped native address;0 means explicit value view. */
    uint8_t *data,*known;size_t available;
} gr_view;
typedef struct gr_model {
    tf_model *memory;gr_backend backend;gb_flow flow;
    uint32_t entry,argument,boundary_va,boundary_address,needed_mask;
    uint32_t transfer_va,transfer_address;
    uint16_t handle,length;uint8_t command,recognized;
    gr_request last_request;
    /* Abstract caller SP+20..60; D0 cache=0/frame=12, D2 frame=0/cache=12.
       No invented native SP and no second authoritative native RAM. */
    uint8_t stack[41],known[41];size_t frame_offset,frame_length;
    uint32_t calls,replies;
} gr_model;
void gr_init(gr_model *,tf_model *,const gr_backend *);
/* Post-auth/eligibility command leaves14254/144CE only, not13E6A dispatcher.
   Native loads payload[0] even length0; readable SRAM byte is API precondition. */
gb_flow gr_command(gr_model *,uint16_t,uint8_t,uint32_t,uint16_t);
/* Exact139BA compares raw handle against U16 slots; SB narrows mode. */
gb_flow gr_mode(gr_model *,uint32_t,uint32_t);
/* Native139E6 producer. Mapped record+3 is live until synchronous wrapper copy.
   No DLC/minimum-record-length gate is introduced. */
gb_flow gr_d1(gr_model *,uint32_t);
/* Borrowed record descriptor; address0 uses live data/known for available bytes.
   The8-byte sink is checked only when reached, with no invented SP or DLC gate. */
gb_flow gr_d1_view(gr_model *,const gr_view *);
/* Exact829E directions:nonzero reads cache,zero writes it. index multiplication
   wraps U32; no guessed cache capacity check. View is12B readable/writable. */
gb_flow gr_cache_transfer(gr_model *,uint32_t,uint32_t,gr_view *);
/* Complete D392/D31A/D17C/D388/FF3C bodies. Pure raw getters can RETURNED with
   partial scalar known. D17C joins its pure returning branches; report control
   gates with unknown conditions HALT. Result and flow differ. */
gb_flow gr_getter(gr_model *,uint32_t,gb_scalar *);
#ifdef __cplusplus
}
#endif
#endif
