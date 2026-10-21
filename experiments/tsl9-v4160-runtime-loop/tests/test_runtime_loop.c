#include "runtime_loop.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {ri_value memory[16384];ml_request trace[512];unsigned count;
    uint32_t calls,stop_call,stop_pc,mmio,mode_reads,arg_reads,change_slot;
    ri_flow stop_flow;int omit_route,dispatch_mutate,partial_shift;uint32_t wrong_route;
} fixture;
static fixture f;static ml_model m;static unsigned checks,groups;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"check %u line %d: %s\n",checks,__LINE__,#x);exit(1);}}while(0)
static ri_value w(uint32_t n){ri_value v={n,UINT32_MAX};return v;}
static ri_value *mem(uint32_t a){CHECK(a>=0x20000000&&a<=0x2000fffc&&(a&3)==0);return &f.memory[(a-0x20000000)/4];}
static void log_request(const ml_request *q){CHECK(f.count<512);f.trace[f.count++]=*q;}
static ri_flow effect(void *ctx,const ml_request *q,ri_value *out){
    CHECK(ctx==&f);log_request(q);if(f.stop_pc==q->pc)return f.stop_flow;
    if(q->kind==ML_READ32){CHECK(q->address.known==UINT32_MAX);*out=*mem(q->address.value);if(q->pc==0x9048)++f.arg_reads;}
    else if(q->kind==ML_READ8){CHECK(q->address.known==UINT32_MAX);*out=*mem(q->address.value);if(q->pc==0x9044)++f.mode_reads;}
    else if(q->kind==ML_WRITE32){
        CHECK(q->address.known==UINT32_MAX);
        if(q->pc==0x81a6){++f.mmio;CHECK(q->address.value==0x40003000&&q->data.value==0xaaaa);}
        else *mem(q->address.value)=q->data;
    }else CHECK(q->kind==ML_RETURN);
    return RI_RETURNED;
}
static ri_flow call(void *ctx,ml_model *model,const ml_request *q,ml_call_result *out){
    CHECK(ctx==&f&&model==&m);log_request(q);++f.calls;
    if(f.stop_call==f.calls)return f.stop_flow;
    if(f.change_slot&&q->pc==0x81a2)*mem(0x20000000)=w(f.change_slot);
    if(f.dispatch_mutate&&q->pc==0x9058){model->r.s[0]=w(2);model->r.s[1]=w(0x1234);model->r.a[0]=w(0xdeadbeef);}
    if(f.partial_shift&&q->pc==0x9058){model->r.s[0].value=0;model->r.s[0].known=UINT32_C(0xfffffffe);}
    if(!f.omit_route)out->returned_to=f.wrong_route?w(f.wrong_route):q->continuation;
    model->r.a[0]=w(f.calls);return RI_RETURNED;
}
static void fresh(void){ml_backend b;memset(&f,0,sizeof f);b.context=&f;b.effect=effect;b.call=call;ml_init(&m,ML_ID2966_0EE64183,&b);m.r.sp=w(0x20010000);m.r.gp=w(0x20004000);m.r.ra=w(0x1235);m.r.s[0]=w(7);m.r.s[1]=w(9);m.r.s[2]=w(11);}
static void initialization(void){
    static const uint32_t pc[]={0x9254,0x9258,0x925c,0x9260,0x9264,0x9268,0x926a,0x926e,0x9270,0x9274,0x9278,0x927c,0x9280,0x9284,0x928c};
    static const uint32_t target[]={0x18834,0x9a42,0x1973c,0x9f4c,0x131c2,0x8e88,0x9b4e,0x9958,0x9f12,0x12d92,0x14c8a,0x154a6,0x17040,0x173a2,0x17bf6};
    unsigned i;++groups;fresh();CHECK(ml_initialize_9250(&m)==RI_RETURNED);
    CHECK(f.calls==15&&m.r.sp.value==0x20010000&&m.return_target.value==0x1234&&m.r.ra.value==0x1235);
    for(i=0;i<14;i++)CHECK(f.trace[i+1].pc==pc[i]&&f.trace[i+1].target.value==target[i]);
    CHECK(f.trace[15].kind==ML_READ32&&f.trace[15].pc==0x9288);
    CHECK(f.trace[16].pc==pc[14]&&f.trace[16].tail&&f.trace[16].target.value==target[14]&&f.trace[16].continuation.value==0x1234);
    fresh();f.stop_call=3;f.stop_flow=RI_TRANSFER;CHECK(ml_initialize_9250(&m)==RI_TRANSFER&&f.calls==3&&m.r.sp.value==0x2000fff0);
    fresh();f.omit_route=1;CHECK(ml_initialize_9250(&m)==RI_HALT&&m.boundary==ML_UNKNOWN_CONTROL&&f.calls==1);
    fresh();f.wrong_route=0x8888;CHECK(ml_initialize_9250(&m)==RI_TRANSFER&&m.boundary==ML_OTHER_RETURN&&f.calls==1);
    fresh();m.r.ra.known=0;CHECK(ml_initialize_9250(&m)==RI_HALT&&m.boundary==ML_UNKNOWN_CONTROL&&m.boundary_pc==0x928c&&f.calls==15&&m.r.sp.value==0x20010000);
}
static void permanent_loop(void){
    unsigned i,loads=0;++groups;fresh();*mem(0x20000000)=w(0x200007d1);m.budget=14;f.change_slot=0x20000801;
    CHECK(ml_loop_8180(&m)==RI_LIMIT&&m.boundary==ML_BUDGET&&m.iterations==2&&f.mmio==2&&m.r.sp.value==0x2000fff0);
    CHECK(m.r.s[0].value==0xaaaa&&m.r.s[1].value==0x40003000&&m.r.s[2].value==0x20000000);
    CHECK(f.trace[0].pc==0x8182&&f.trace[1].pc==0x8186&&f.trace[1].registers.s[0].value==0xb000);
    for(i=0;i<f.count;i++)if(f.trace[i].pc==0x819c){CHECK(f.trace[i].target.value==(loads?0x20000800u:0x200007d0u));++loads;}
    CHECK(loads==2&&m.last_request.pc==0x8198);
    fresh();f.stop_call=2;f.stop_flow=RI_HALT;*mem(0x20000000)=w(0x200007d0);
    CHECK(ml_loop_8180(&m)==RI_HALT&&f.mmio==0&&m.r.sp.value==0x2000fff0&&m.iterations==0);
}
static void dispatcher(void){
    uint32_t record=0x2000be08;++groups;fresh();m.r.a[0]=w(3);m.r.a[1]=w(0x8001);
    *mem(record)=w(0);*mem(record+4)=w(0x2223);*mem(record+8)=w(0x9876);
    CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.value==0x8000&&m.r.sp.value==0x20010000&&m.return_target.value==0x1234);
    CHECK(f.mode_reads==1&&f.arg_reads==1&&mem(record+4)->value==0&&mem(record+8)->value==0);
    CHECK(f.trace[3].pc==0x9040&&f.trace[4].pc==0x9044&&f.trace[5].pc==0x9048&&f.trace[6].pc==0x9050&&f.trace[7].pc==0x9054&&f.trace[8].pc==0x9058);
    CHECK(f.trace[8].registers.a[0].value==0x9876&&f.trace[8].target.value==0x2222);
    fresh();m.r.a[1]=w(0x8000);CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.value==0&&m.slots_examined==15&&f.calls==0);
    fresh();m.r.a[1]=w(1);*mem(record+4)=w(0);CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.value==0&&f.mode_reads==0&&f.arg_reads==0&&f.calls==0);
    fresh();m.r.a[1]=w(1);*mem(record)=w(1);*mem(record+4)=w(0x2222);*mem(record+8)=w(0x9876);f.dispatch_mutate=1;
    CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.value==(0x1234u^4u)&&mem(record+4)->value==0x2222);
    fresh();m.r.a[1].value=2;m.r.a[1].known=2;CHECK(ml_dispatch_901a(&m)==RI_HALT&&m.boundary_pc==0x902c&&m.slots_examined==1&&f.calls==0);
}
static void main_and_handoff(void){
    ri_model ri;unsigned n;++groups;fresh();*mem(0x20000000)=w(0x200007d0);m.budget=30;
    CHECK(ml_main_9008(&m)==RI_LIMIT&&m.r.sp.value==0x2000ffe0&&f.mmio==1);
    for(n=0;n<f.count;n++)CHECK(f.trace[n].pc!=0x9012&&f.trace[n].pc!=0x9018);
    n=f.count;CHECK(ml_main_suffix_9012(&m)==RI_LIMIT&&f.count==n);
    fresh();*mem(0x20010000-4)=w(0x5679);m.r.sp=w(0x2000fff0);
    CHECK(ml_main_suffix_9012(&m)==RI_RETURNED&&m.result.value==0&&m.r.sp.value==0x20010000&&m.return_target.value==0x5678);
    fresh();memset(&ri,0,sizeof ri);ri.profile=RI_DEC2023_133D3705;ri.flow=RI_TRANSFER;ri.boundary=RI_MRET_BOUNDARY;ri.return_target=w(0x9008);ri.gp=w(0x20004000);ri.sp=w(0x20010000);ri.ra=w(0x6debe);ri.a0=w(0x6eb30);ri.a1=w(0x20002efc);ri.a2=w(0x20002ef8);ri.a4=w(0x20003614);ri.a5=w(0x20003618);f.stop_call=1;f.stop_flow=RI_HALT;
    CHECK(ml_main_from_resident(&m,&ri)==RI_HALT&&m.r.sp.value==0x2000ffe0&&f.calls==1&&f.trace[2].registers.a[0].value==0x6eb30);
    fresh();ri.return_target.known=0;CHECK(ml_main_from_resident(&m,&ri)==RI_HALT&&m.operations==0&&m.boundary==ML_BINDING);
    fresh();m.profile=ML_UNKNOWN_IMAGE;CHECK(ml_main_9008(&m)==RI_HALT&&m.operations==0);
}
static void slots_and_knowledge(void){
    unsigned i;uint32_t record;++groups;
    for(i=0;i<15;i++){
        fresh();record=0x2000be08+12*i;m.r.a[1]=w(UINT32_C(0x8000)|(UINT32_C(1)<<i));
        *mem(record)=w(1);*mem(record+4)=w(0x2223);*mem(record+8)=w(0x7654+i);
        CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.value==0x8000&&m.result.known==UINT32_MAX&&m.slots_examined==i+1);
        CHECK(f.trace[3].address.value==record+4&&f.trace[5].data.known==0&&f.calls==1);
        CHECK(f.trace[6].kind==ML_CALL&&f.trace[6].registers.a[0].value==0x7654+i&&f.trace[6].registers.a[3].value==0x2223);
    }
    fresh();m.r.a[1]=w(1);record=0x2000be08;*mem(record)=w(1);*mem(record+4)=w(0x2222);f.partial_shift=1;
    CHECK(ml_dispatch_901a(&m)==RI_RETURNED&&m.result.known==UINT32_C(0xfffffffc)&&m.result.value==0);
    fresh();m.r.a[1]=w(1);mem(record+4)->known=0;
    CHECK(ml_dispatch_901a(&m)==RI_HALT&&m.boundary==ML_UNKNOWN_CONDITION&&m.boundary_pc==0x9042&&f.mode_reads==0);
    fresh();m.r.a[1]=w(1);*mem(record+4)=w(0x2222);mem(record)->known=0;
    CHECK(ml_dispatch_901a(&m)==RI_HALT&&m.boundary_pc==0x904e&&f.arg_reads==1&&f.calls==0);
    fresh();m.r.a[1]=w(1);mem(record+4)->value=2;mem(record+4)->known=2;*mem(record)=w(0);
    CHECK(ml_dispatch_901a(&m)==RI_HALT&&m.boundary_pc==0x9058&&mem(record+4)->known==UINT32_MAX&&mem(record+4)->value==0&&f.calls==0);
}
static void provider_failures(void){
    ++groups;fresh();m.backend.effect=0;
    CHECK(ml_initialize_9250(&m)==RI_HALT&&m.boundary==ML_MISSING_PROVIDER&&m.operations==1&&f.count==0);
    fresh();m.backend.call=0;CHECK(ml_initialize_9250(&m)==RI_HALT&&m.boundary_pc==0x9254&&f.count==1);
    fresh();m.budget=0;CHECK(ml_main_9008(&m)==RI_LIMIT&&m.boundary==ML_BUDGET&&m.last_request.pc==0x900a&&f.count==0);
    fresh();m.budget=1;CHECK(ml_initialize_9250(&m)==RI_LIMIT&&m.r.ra.value==0x9258&&m.last_request.registers.ra.value==0x9258&&f.calls==0);
    fresh();f.stop_pc=0x9288;f.stop_flow=RI_LIMIT;
    CHECK(ml_initialize_9250(&m)==RI_LIMIT&&m.boundary==ML_PROVIDER_STOP&&f.calls==14&&m.r.sp.value==0x2000fff0);
    fresh();m.r.a[1]=w(1);*mem(0x2000be08)=w(0);*mem(0x2000be0c)=w(0x2222);*mem(0x2000be10)=w(0x9999);f.stop_call=1;f.stop_flow=RI_TRANSFER;
    CHECK(ml_dispatch_901a(&m)==RI_TRANSFER&&m.r.sp.value==0x2000fff0&&mem(0x2000be0c)->value==0&&mem(0x2000be10)->value==0&&m.last_request.pc==0x9058);
}
int main(void){initialization();permanent_loop();dispatcher();main_and_handoff();slots_and_knowledge();provider_failures();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;}
