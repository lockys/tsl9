#include "host_io.h"
#include <string.h>

/* Named algorithm/frame operations, never a CPU or ISA interpreter. */
void op_set(op_host *h,unsigned reg,uint32_t value) {h->regs[reg]=value;h->known|=(uint32_t)1u<<reg;}
uint32_t op_bind(op_host *h,unsigned reg,uint32_t value) {op_set(h,reg,value);return value;}
int op_live(op_host *h,unsigned reg,uint32_t *out) {
    if(h->flow!=OP_RETURNED) return 0;
    if(!(h->known&((uint32_t)1u<<reg))) {h->flow=OP_UNKNOWN;return 0;}
    *out=h->regs[reg];return 1;
}
static int effect(op_host *h,op_event *event) {
    uint32_t registers[32],known=h->known;int memory=event->kind==OP_READ||event->kind==OP_WRITE;
    if(h->flow!=OP_RETURNED) return 0;
    if(memory)memcpy(registers,h->regs,sizeof(registers));
    event->flow=OP_RETURNED;
    if(!h->provider || !h->provider(h,event)) {if(h->flow==OP_RETURNED)h->flow=OP_UNKNOWN;return 0;}
    if(h->flow!=OP_RETURNED)return 0;
    if(memory&&event->flow==OP_RETURNED&&(known!=h->known||memcmp(registers,h->regs,sizeof(registers)))) {h->unsupported_memory_register_mutation=1u;h->flow=OP_UNKNOWN;return 0;}
    h->flow=event->flow;return h->flow==OP_RETURNED;
}
static int read_word(op_host *h,uint32_t site,uint32_t address,uint32_t *out) {
    op_event event;memset(&event,0,sizeof(event));event.kind=OP_READ;event.site=site;event.address=address;event.width=4u;
    if(!effect(h,&event))return 0;
    if(!event.value_known){h->flow=OP_UNKNOWN;return 0;}
    *out=event.value;return 1;
}
int op_slot(op_host *h,uint32_t site,uint32_t address,unsigned reg,uint32_t *out) {
    if(!read_word(h,site,address,out))return 0;
    op_set(h,reg,*out);return 1;
}
int op_write(op_host *h,uint32_t site,uint32_t address,uint32_t width,uint32_t value,uint32_t known) {
    op_event event;memset(&event,0,sizeof(event));event.kind=OP_WRITE;event.site=site;event.address=address;event.width=width;event.value=value;event.value_known=known;
    return effect(h,&event);
}
static int save(op_host *h,unsigned reg,uint32_t offset,uint32_t site) {
    uint32_t sp;if(!op_live(h,2u,&sp))return 0;
    return op_write(h,site,sp+offset,4u,h->regs[reg],(h->known>>reg)&1u);
}
int op_frame_head(op_host *h) {
    uint32_t sp;if(!op_live(h,2u,&sp))return 0;op_set(h,2u,sp-32u);return save(h,18u,16u,0x9b90u);
}
int op_frame_rest(op_host *h) {
    return save(h,9u,20u,0x9b9au)&&save(h,19u,12u,0x9b9cu)&&save(h,20u,8u,0x9b9eu)&&save(h,1u,28u,0x9ba0u)&&save(h,8u,24u,0x9ba2u);
}
static int restore(op_host *h,unsigned reg,uint32_t offset,uint32_t site) {
    uint32_t sp,value;if(!op_live(h,2u,&sp)||!read_word(h,site,sp+offset,&value))return 0;op_set(h,reg,value);return 1;
}
static int pop_frame(op_host *h) {uint32_t sp;if(!op_live(h,2u,&sp))return 0;op_set(h,2u,sp+32u);return 1;}
int op_restore_s0(op_host *h) {return restore(h,8u,24u,0x9be6u);}
int op_restore_tail(op_host *h) {
    return restore(h,1u,28u,0x9becu)&&restore(h,9u,20u,0x9beeu)&&restore(h,18u,16u,0x9bf0u)&&restore(h,19u,12u,0x9bf2u)&&restore(h,20u,8u,0x9bf4u)&&pop_frame(h);
}
int op_restore_null(op_host *h) {
    return restore(h,1u,28u,0x9bfau)&&restore(h,8u,24u,0x9bfcu)&&restore(h,9u,20u,0x9bfeu)&&restore(h,18u,16u,0x9c00u)&&restore(h,19u,12u,0x9c02u)&&restore(h,20u,8u,0x9c04u)&&pop_frame(h);
}
int op_call(op_host *h,op_kind kind,uint32_t site,uint32_t target,uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3) {
    op_event event;unsigned i;memset(&event,0,sizeof(event));event.kind=kind;event.site=site;event.raw_target=target;event.target=target&~1u;event.args[0]=a0;event.args[1]=a1;event.args[2]=a2;event.args[3]=a3;event.args_known=kind==OP_TRANSMIT?15u:7u;
    op_set(h,10u,a0);op_set(h,11u,a1);op_set(h,12u,a2);if(kind==OP_TRANSMIT)op_set(h,13u,a3);
    op_set(h,1u,site+(kind==OP_TRANSMIT?4u:2u));
    for(i=0;i<4u;i++)event.args[i]=h->regs[10u+i];
    if(!effect(h,&event))return 0;
    if(event.value_known)op_set(h,10u,event.value);else h->known&=~((uint32_t)1u<<10);
    return 1;
}
op_result op_finish(op_host *h,uint32_t value,uint32_t known) {
    op_result result;result.flow=h->flow;result.value=value;result.value_known=known&&h->flow==OP_RETURNED;result.caller_link_raw=h->regs[1];result.caller_link_target=h->regs[1]&~1u;result.caller_link_known=(h->known>>1)&1u;result.tail_delegated=h->delegated;return result;
}
op_result op_tail(op_host *h,uint32_t target,uint32_t buffer) {
    op_event event;uint32_t continuation=h->regs[1],continuation_known=(h->known>>1)&1u;op_result result;unsigned i;memset(&event,0,sizeof(event));event.kind=OP_RELEASE_TAIL;event.site=0x9bf8u;event.raw_target=target;event.target=target&~1u;op_set(h,10u,buffer);
    for(i=0;i<4u;i++){event.args[i]=h->regs[10u+i];if(h->known&((uint32_t)1u<<(10u+i)))event.args_known|=(uint32_t)1u<<i;}
    h->delegated=1u;
    if(!effect(h,&event))result=op_finish(h,0u,0u);
    else {if(event.value_known)op_set(h,10u,event.value);else h->known&=~((uint32_t)1u<<10);result=op_finish(h,event.value,event.value_known);}
    result.caller_link_raw=continuation;result.caller_link_target=continuation&~1u;result.caller_link_known=continuation_known;return result;
}
