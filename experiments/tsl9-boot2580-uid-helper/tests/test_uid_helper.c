#include "uid_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks,groups;
#define T(x) do{++checks;if(!(x)){fprintf(stderr,"line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
#define RAM UINT32_C(0x20000000)
#define STACK (RAM+0x1000u)
#define INPUT (RAM+0x200u)
typedef struct {
    uint8_t ram[8192],known[8192],id[12];
    ub_request events[100];unsigned count,copies,returns,stop_at,transfer_at;
    unsigned mutate_slot,mutate_ra,mutate_late_input;
    uint32_t target_first,target_second;
} fixture;
static fixture f;static ub_model u;
static bc_value known(uint32_t v){bc_value r;r.value=v;r.known=UINT32_MAX;return r;}
static bc_value get(uint32_t a,unsigned width) {
    bc_value v={0,0};unsigned i;
    for(i=0;i<width;i++)if(a+i>=RAM&&a+i-RAM<sizeof f.ram){
        v.value|=(uint32_t)f.ram[a+i-RAM]<<(8*i);v.known|=(uint32_t)f.known[a+i-RAM]<<(8*i);
    }return v;
}
static void set(uint32_t a,bc_value v,unsigned width){
    unsigned i;T(a>=RAM&&a-RAM+width<=sizeof f.ram);
    for(i=0;i<width;i++){f.ram[a+i-RAM]=(uint8_t)(v.value>>(8*i));f.known[a+i-RAM]=(uint8_t)(v.known>>(8*i));}
}
static uint8_t id_byte(uint32_t a){T(a>=0x1ffff7e8u&&a<0x1ffff7f4u);return f.id[a-0x1ffff7e8u];}
static bc_flow effect(void *ctx,const ub_request *q,bc_value *out){
    (void)ctx;T(f.count<100);f.events[f.count++]=*q;
    if(f.count==f.stop_at)return BC_HALT;if(f.count==f.transfer_at)return BC_TRANSFER;
    if(q->kind==UB_RETURN){++f.returns;return BC_RETURNED;}
    if(q->address.known!=UINT32_MAX)return BC_HALT;
    if(q->kind==UB_READ32&&q->address.value==0x4004c){
        *out=known(f.copies?f.target_second:f.target_first);return BC_RETURNED;
    }
    if(q->kind==UB_WRITE32)set(q->address.value,q->data,4);
    else if(q->kind==UB_READ8||q->kind==UB_READ32){
        *out=get(q->address.value,q->kind==UB_READ8?1u:4u);
        if(f.mutate_late_input&&q->pc==0x1c9c){set(STACK-32,known(0xee),1);f.mutate_late_input=0;}
    }return BC_RETURNED;
}
static bc_flow copy(void *ctx,ub_model *model,const ub_request *q,bc_value *out){
    unsigned i;(void)ctx;T(f.count<100);f.events[f.count++]=*q;
    if(f.count==f.stop_at)return BC_HALT;if(f.count==f.transfer_at)return BC_TRANSFER;
    T(q->args[0].known==UINT32_MAX&&q->args[1].known==UINT32_MAX);
    T(q->target.known==UINT32_MAX&&q->target.value==((f.copies?f.target_second:f.target_first)&~1u));
    for(i=0;i<q->args[2].value;i++)set(q->args[0].value+i,known(id_byte(q->args[1].value+i)),1);
    ++f.copies;
    if(f.mutate_ra&&f.copies==1)set(model->sp.value+12,known(0x4444),4);
    if(f.mutate_slot&&f.copies==1)f.target_second=0xa001;
    *out=q->args[0];return BC_RETURNED;
}
static void setup(void){
    ub_backend b;unsigned i;memset(&f,0,sizeof f);memset(f.known,255,sizeof f.known);
    for(i=0;i<12;i++)f.id[i]=(uint8_t)(0x70+i);
    f.target_first=f.target_second=0x9001;
    b.context=&f;b.effect=effect;b.copy=copy;ub_init(&u,&b);
    u.sp=known(STACK);u.ra=known(0x2222);u.s0=known(0x12121212);u.s1=known(0x34343434);u.s2=known(0x56565656);
    for(i=0;i<14;i++)set(INPUT+i,known(f.id[i<8?i+4:i-8]),1);
}
static void build_geometry(void){
    unsigned i; ++groups;setup();
    T(ub_build(&u,known(INPUT))==BC_RETURNED);
    T(f.copies==2&&f.count==12&&u.sp.value==STACK);
    for(i=0;i<14;i++)T(get(INPUT+i,1).value==f.id[i<8?i+4:i-8]);
    T(get(INPUT,1).value==get(INPUT+12,1).value&&get(INPUT+1,1).value==get(INPUT+13,1).value);
    T(f.events[0].pc==0x1c4c&&f.events[1].pc==0x1c52);
    T(f.events[5].pc==0x1c66&&f.events[5].args[1].value==0x1ffff7ec);
    T(f.events[7].pc==0x1c6e&&f.events[11].pc==0x1c80&&f.events[11].args[1].value==0x1ffff7e8);
    T(f.events[11].tail&&f.events[11].continuation.value==0x2222&&u.return_target.value==0x2222);
    T(u.s0.value==0x12121212&&u.s1.value==0x34343434&&u.s2.value==0x56565656);
}
static void match_and_frame(void){
    ++groups;setup();T(ub_compare(&u,known(INPUT),known(14))==BC_RETURNED);
    T(u.result.value==0&&u.result.known==UINT32_MAX&&u.compared==14);
    T(u.sp.value==STACK&&u.s0.value==0x12121212&&u.ra.value==0x2222&&u.return_target.value==0x2222);
    T(f.events[0].pc==0x1c8a&&f.events[1].pc==0x1c90);
    T(f.events[14].pc==0x1c9c&&f.events[15].pc==0x1ca4);
    T(f.events[42].pc==0x1cb4&&f.events[43].pc==0x1cb6&&f.events[44].pc==0x1cba);
}
static void length_and_mismatch(void){
    ++groups;setup();T(ub_compare(&u,known(INPUT),known(15))==BC_RETURNED);
    T(u.result.value==1&&f.count==1&&f.copies==0&&u.sp.value==STACK&&f.events[0].pc==0x1cc2);
    setup();set(INPUT+2,known(0xff),1);T(ub_compare(&u,known(INPUT),known(14))==BC_RETURNED);
    T(u.result.value==1&&u.compared==3&&f.count==23);
    setup();f.known[INPUT-RAM]=0;T(ub_compare(&u,known(INPUT),known(14))==BC_HALT);
    T(u.boundary==UB_UNKNOWN_CONDITION&&u.boundary_pc==0x1ca8&&u.compared==1&&f.returns==0);
}
static void fresh_reads(void){
    ++groups;setup();f.mutate_slot=1;T(ub_build(&u,known(INPUT))==BC_RETURNED);
    T(f.events[5].target.value==0x9000&&f.events[11].target.value==0xa000);
    setup();f.mutate_late_input=1;T(ub_compare(&u,known(INPUT),known(14))==BC_RETURNED);
    T(u.result.value==1&&u.compared==1);
}
static void unknown_and_transfer(void){
    unsigned n;bc_value length; ++groups;setup();u.budget=0;
    T(ub_build(&u,known(INPUT))==BC_HALT&&u.boundary==UB_BUDGET&&u.sp.value==STACK-16);
    T(f.count==0);n=f.count;T(ub_compare(&u,known(INPUT),known(14))==BC_HALT&&f.count==n);
    setup();f.stop_at=2;T(ub_build(&u,known(INPUT))==BC_HALT);
    T(u.sp.value==STACK-16&&get(STACK-12,4).value==0x34343434&&f.copies==0);
    setup();f.transfer_at=6;T(ub_build(&u,known(INPUT))==BC_TRANSFER&&u.sp.value==STACK-16);
    setup();f.mutate_ra=1;T(ub_compare(&u,known(INPUT),known(14))==BC_TRANSFER);
    T(u.return_target.value==0x4444&&u.compared==0);
    setup();length.value=14;length.known=255;
    T(ub_compare(&u,known(INPUT),length)==BC_HALT&&u.boundary_pc==0x1c84&&f.count==0);
}
static void bridge(void){
    bc_model caller;bc_request q;bc_value out; ++groups;setup();memset(&caller,0,sizeof caller);
    memset(&q,0,sizeof q);caller.body_sp=known(STACK);q.kind=BC_IDENTITY;q.pc=0x22da;
    q.target=known(0x1c82);q.argc=2;q.args[0]=known(INPUT);q.args[1]=known(14);
    T(ub_identity_bridge(&caller,&q,&u,&out)==BC_RETURNED);
    T(out.value==0&&out.known==UINT32_MAX&&caller.body_sp.value==STACK&&u.return_target.value==0x22dc);
    setup();caller.body_sp=known(STACK);f.mutate_ra=1;
    T(ub_identity_bridge(&caller,&q,&u,&out)==BC_TRANSFER&&caller.body_sp.value==STACK-32);
    setup();q.pc=0x9999;T(ub_identity_bridge(&caller,&q,&u,&out)==BC_HALT&&f.count==0);
}
int main(void){build_geometry();match_and_frame();length_and_mismatch();fresh_reads();unknown_and_transfer();bridge();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"original_executed\":false,\"hardware\":false}\n",groups,checks);return 0;}
