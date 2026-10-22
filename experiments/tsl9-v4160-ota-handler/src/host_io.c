#include "ota_handler.h"
#include "io.h"
#include <string.h>
static oh_flow dispatch(oh_host *h,oh_effect *e)
{
    oh_values before=h->values;uint32_t args[8];oh_flow flow;memcpy(args,h->args,sizeof(args));
    if(h->flow!=OH_CONTINUE)return h->flow;
    if(!h->provider || (h->diagnostic_budget && h->effects>=h->diagnostic_budget)){h->flow=OH_UNKNOWN;return h->flow;}
    h->effects++;flow=h->provider(h->user,h,e);
    if(e->kind!=OH_CALL && (memcmp(&before,&h->values,sizeof(before)) || memcmp(args,h->args,sizeof(args))))flow=OH_UNKNOWN;
    if(e->kind==OH_READ && !e->value_known && flow==OH_CONTINUE)flow=OH_UNKNOWN;
    h->flow=flow;return flow;
}
uint32_t oh_host_read(oh_host *h,uint32_t site,uint32_t address,uint32_t width)
{
    oh_effect e;memset(&e,0,sizeof(e));e.kind=OH_READ;e.source_site=site;e.address=address;e.width=width;
    if(dispatch(h,&e)!=OH_CONTINUE)return 0;
    return width==8?e.value&255u:e.value;
}
void oh_host_write(oh_host *h,uint32_t site,uint32_t address,uint32_t width,uint32_t value)
{
    oh_effect e;memset(&e,0,sizeof(e));e.kind=OH_WRITE;e.source_site=site;e.address=address;e.width=width;e.value=width==8?value&255u:value;e.value_known=1;(void)dispatch(h,&e);
}
void oh_host_call(oh_host *h,uint32_t site,oh_callee kind,uint32_t target,uint32_t mask)
{
    oh_effect e;memset(&e,0,sizeof(e));e.kind=OH_CALL;e.source_site=site;e.callee=kind;e.target=target;e.defined_argument_mask=mask;
    if(kind==OH_COPY_SLOT_4C)h->args[5]=target;
    memcpy(e.args,h->args,sizeof(e.args));
    if(dispatch(h,&e)!=OH_CONTINUE)return;
    h->args[0]=e.value;h->return_value_known=e.value_known;
}
void oh_host_enter(oh_host *h)
{
    static const uint32_t site[8]={0x9c4cu,0x9c4eu,0x9c50u,0x9c52u,0x9c54u,0x9c56u,0x9c58u,0};
    static const uint32_t slot[7]={40u,32u,44u,36u,28u,24u,20u};
    uint32_t value[7]={h->values.buffer,h->values.context,h->values.return_address,h->values.flash,h->values.source,h->values.page,h->values.limit};unsigned i;
    h->values.sp-=48u;
    for(i=0;i<7u;i++){oh_host_write(h,site[i],h->values.sp+slot[i],32,value[i]);if(OH_STOP(h))return;}
}
void oh_host_leave(oh_host *h)
{
    uint32_t *value[7]={&h->values.return_address,&h->values.buffer,&h->values.flash,&h->values.context,&h->values.source,&h->values.page,&h->values.limit};unsigned i;
    for(i=0;i<7u;i++){uint32_t x=oh_host_read(h,0x9c7au+2u*i,h->values.sp+44u-4u*i,32);if(OH_STOP(h))return;*value[i]=x;}
    h->values.sp+=48u;
}
