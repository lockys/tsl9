#include "host_io.h"
#include <string.h>

void tx_host_init(tx_host *h,tx_provider provider,void *user)
{
    memset(h,0,sizeof(*h));h->provider=provider;h->user=user;
    h->loop_budget=4096u;h->known=1u;
}
uint32_t tx_set(tx_host *h,unsigned reg,uint32_t value)
{
    if(reg!=0u)h->regs[reg]=value;
    h->known|=UINT32_C(1)<<reg;return value;
}
uint32_t tx_get(tx_host *h,unsigned reg)
{
    if((h->known&(UINT32_C(1)<<reg))==0u)h->flow=TX_UNKNOWN;
    return h->regs[reg];
}
static void dispatch(tx_host *h,tx_event *event,int memory)
{
    uint32_t before[32],known=h->known;
    tx_flow flow;
    if(h->flow!=TX_CONTINUE)return;
    memcpy(before,h->regs,sizeof(before));++h->event_count;
    flow=h->provider?h->provider(h,event,h->user):TX_UNKNOWN;
    if(memory&&(known!=h->known||memcmp(before,h->regs,sizeof(before))!=0)) {
        h->unsupported_memory_register_mutation=1;h->flow=TX_UNKNOWN;return;
    }
    if(flow!=TX_CONTINUE)h->flow=flow;
}
uint32_t tx_read(tx_host *h,uint32_t site,uint32_t address,unsigned width,unsigned reg)
{
    tx_event e;uint32_t mask;
    memset(&e,0,sizeof(e));e.kind=TX_READ;e.site=site;e.address=address;e.width=width;
    dispatch(h,&e,1);
    if(h->flow!=TX_CONTINUE)return 0u;
    mask=width==1u?255u:width==2u?65535u:UINT32_MAX;
    if(!e.value_known){h->known&=~(UINT32_C(1)<<reg);h->flow=TX_UNKNOWN;return e.value&mask;}
    return tx_set(h,reg,e.value&mask);
}
void tx_write(tx_host *h,uint32_t site,uint32_t address,unsigned width,uint32_t value,int known)
{
    tx_event e;memset(&e,0,sizeof(e));e.kind=TX_WRITE;e.site=site;e.address=address;e.width=width;
    e.value=value&(width==1u?255u:width==2u?65535u:UINT32_MAX);e.value_known=known;
    dispatch(h,&e,1);
}
static void frame_write(tx_host *h,uint32_t site,unsigned offset,unsigned reg)
{
    uint32_t sp=tx_get(h,2);if(h->flow!=TX_CONTINUE)return;
    tx_write(h,site,sp+offset,4u,h->regs[reg],(h->known&(UINT32_C(1)<<reg))!=0u);
}
static void frame_read(tx_host *h,uint32_t site,unsigned offset,unsigned reg)
{
    uint32_t sp=tx_get(h,2);if(h->flow!=TX_CONTINUE)return;
    (void)tx_read(h,site,sp+offset,4u,reg);
}
void tx_frame(tx_host *h)
{
    uint32_t sp=tx_get(h,2);if(h->flow!=TX_CONTINUE)return;tx_set(h,2,sp-32u);
    frame_write(h,0x8a60u,24u,8u);frame_write(h,0x8a62u,20u,9u);
    frame_write(h,0x8a64u,16u,18u);frame_write(h,0x8a66u,12u,19u);
    frame_write(h,0x8a68u,28u,1u);
}
void tx_pop_frame(tx_host *h)
{
    uint32_t sp=tx_get(h,2);if(h->flow==TX_CONTINUE)tx_set(h,2,sp+32u);
}
void tx_restore_failure(tx_host *h)
{
    frame_read(h,0x8abeu,28u,1u);frame_read(h,0x8ac0u,24u,8u);
    frame_read(h,0x8ac2u,20u,9u);frame_read(h,0x8ac4u,16u,18u);
    frame_read(h,0x8ac6u,12u,19u);if(h->flow==TX_CONTINUE)tx_pop_frame(h);
}
void tx_restore_head(tx_host *h)
{
    frame_read(h,0x8b26u,28u,1u);frame_read(h,0x8b28u,20u,9u);
    frame_read(h,0x8b2au,16u,18u);frame_read(h,0x8b2cu,12u,19u);
}
void tx_restore_s0(tx_host *h){frame_read(h,0x8b40u,24u,8u);}
static void call_event(tx_host *h,tx_event *e,uint32_t raw)
{
    unsigned i;e->raw_target=raw;e->target=raw&~1u;
    for(i=0;i<4u;++i){e->args[i]=h->regs[10u+i];if(h->known&(UINT32_C(1)<<(10u+i)))e->args_known|=1u<<i;}
}
void tx_gate(tx_host *h,uint32_t site,uint32_t target,uint32_t a0,uint32_t a1)
{
    tx_event e;memset(&e,0,sizeof(e));e.kind=TX_GATE_CALL;e.site=site;
    tx_set(h,10,a0);tx_set(h,11,a1);tx_set(h,1,site+2u);
    call_event(h,&e,target);dispatch(h,&e,0);
    if(h->flow==TX_CONTINUE&&(h->known&(UINT32_C(1)<<10))==0u)h->flow=TX_UNKNOWN;
}
void tx_tail(tx_host *h,uint32_t target,uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3)
{
    tx_event e;memset(&e,0,sizeof(e));e.kind=TX_TAIL_CALL;e.site=0x8b50u;
    tx_set(h,10,a0);tx_set(h,11,a1);tx_set(h,12,a2);tx_set(h,13,a3);
    h->tail_delegated=1;h->delegated_raw_target=target;
    h->delegated_raw_link=h->regs[1];h->delegated_link_known=(h->known&2u)!=0u;
    call_event(h,&e,target);dispatch(h,&e,0);
    if(h->flow==TX_CONTINUE)h->flow=TX_RETURNED;
}
void tx_budget(tx_host *h)
{
    if(h->loop_steps>=h->loop_budget){h->budget_exhausted=1;h->flow=TX_UNKNOWN;}
    else ++h->loop_steps;
}
tx_result tx_finish(tx_host *h,int local_return)
{
    tx_result r;memset(&r,0,sizeof(r));
    if(local_return&&h->flow==TX_CONTINUE)h->flow=TX_RETURNED;
    r.flow=h->flow;r.value=h->regs[10];r.value_known=(h->known&(UINT32_C(1)<<10))!=0u;
    r.tail_delegated=h->tail_delegated;r.budget_exhausted=h->budget_exhausted;
    r.unsupported_memory_register_mutation=h->unsupported_memory_register_mutation;
    r.raw_target=h->tail_delegated?h->delegated_raw_target:h->regs[1];r.target=r.raw_target&~1u;
    r.raw_link=h->tail_delegated?h->delegated_raw_link:h->regs[1];r.link=r.raw_link&~1u;
    r.link_known=h->tail_delegated?h->delegated_link_known:(h->known&2u)!=0u;
    return r;
}
