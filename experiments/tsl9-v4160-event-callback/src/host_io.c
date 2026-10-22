#include "callback.h"
#include "io.h"
#include <string.h>
static cb_flow dispatch(cb_host *h,cb_effect *e)
{
    cb_values before=h->values;uint32_t args[8];cb_flow flow;memcpy(args,h->args,sizeof(args));
    if(h->flow!=CB_CONTINUE)return h->flow;
    if(!h->provider || (h->diagnostic_budget && h->effects>=h->diagnostic_budget)){h->flow=CB_UNKNOWN;return h->flow;}
    h->effects++;flow=h->provider(h->user,h,e);
    if(e->kind!=CB_OPAQUE_CALL && (memcmp(&before,&h->values,sizeof(before)) || memcmp(args,h->args,sizeof(args))))flow=CB_UNKNOWN;
    h->flow=flow;return flow;
}
uint32_t cb_host_read(cb_host *h,uint32_t site,uint32_t address,uint32_t width)
{
    cb_effect e;memset(&e,0,sizeof(e));e.kind=CB_READ;e.source_site=site;e.address=address;e.width=width;
    if(dispatch(h,&e)!=CB_CONTINUE)return 0u;
    return width==8?(e.value&255u):width==16?(e.value&65535u):e.value;
}
void cb_host_write(cb_host *h,uint32_t site,uint32_t address,uint32_t width,uint32_t value)
{
    cb_effect e;memset(&e,0,sizeof(e));e.kind=CB_WRITE;e.source_site=site;e.address=address;e.width=width;e.value=width==8?(value&255u):width==16?(value&65535u):value;(void)dispatch(h,&e);
}
void cb_host_call(cb_host *h,uint32_t site,uint32_t target,uint32_t target_register,uint32_t mask)
{
    cb_effect e;memset(&e,0,sizeof(e));h->args[target_register]=target;e.kind=CB_OPAQUE_CALL;e.source_site=site;e.target=target;e.target_register=target_register;e.defined_argument_mask=mask;memcpy(e.args,h->args,sizeof(e.args));(void)dispatch(h,&e);
}
void cb_host_frame_enter(cb_host *h)
{
    static const uint32_t sites[11]={0x861au,0x861cu,0x861eu,0x8620u,0x8622u,0x8624u,0x8626u,0x8628u,0x862au,0x862cu,0x862eu};
    static const uint32_t slots[11]={40u,44u,36u,32u,28u,24u,20u,16u,12u,8u,4u};
    uint32_t values[11]={h->values.events,h->values.return_address,h->values.record,h->values.lane,h->values.span,h->values.task,h->values.connection,h->values.cursor,h->values.rom_base,h->values.base_copy,h->values.shared_base};unsigned i;
    h->values.sp-=48u;h->args[5]=h->args[1]<<16;
    for(i=0;i<11u;i++){cb_host_write(h,sites[i],h->values.sp+slots[i],32,values[i]);if(CB_STOP(h))return;}
}
void cb_host_frame_leave(cb_host *h)
{
    uint32_t *values[11]={&h->values.return_address,&h->values.events,&h->values.record,&h->values.lane,&h->values.span,&h->values.task,&h->values.connection,&h->values.cursor,&h->values.rom_base,&h->values.base_copy,&h->values.shared_base};unsigned i;
    for(i=0;i<11u;i++){uint32_t value=cb_host_read(h,0x866cu+2u*i,h->values.sp+44u-4u*i,32);if(CB_STOP(h))return;*values[i]=value;}
    h->values.sp+=48u;
}
