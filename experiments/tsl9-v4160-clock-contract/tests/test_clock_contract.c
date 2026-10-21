#include "clock_contract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define REG UINT32_C(0x40021000)
static unsigned checks,groups;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
typedef struct {
    vc_word words[5];uint32_t sp8,sp12;
    vc_request trace[30000];unsigned count,cut,hse,pll,sw;
    unsigned ready_at,pll_at,switch_at;int fresh_ready,selector_override,counter_override,partial_counter,unknown_fresh,unknown_sample,unknown_switch;
    uint32_t counter_value;vc_flow cut_flow;
} fixture;
static fixture f,g;
static vc_flow provider(void *ctx,const vc_request *q,vc_word *out){
    fixture *x=(fixture *)ctx;unsigned slot;
    CHECK(x->count<30000);x->trace[x->count++]=*q;
    if(x->cut && x->count==x->cut)return x->cut_flow;
    if(q->address==REG)slot=0;else if(q->address==REG+4)slot=1;else if(q->address==REG+8)slot=2;
    else if(q->address==x->sp8)slot=3;else if(q->address==x->sp12)slot=4;else{CHECK(0);return VC_HALT;}
    if(q->kind==VC_READ32){
        if(q->pc==0x187a2){x->hse++;if(x->ready_at && x->hse>=x->ready_at)x->words[0].value|=0x20000;else x->words[0].value&=~UINT32_C(0x20000);if(x->counter_override)x->words[3].value=x->counter_value;if(x->unknown_sample)x->words[0].known&=~UINT32_C(0x20000);}
        if(q->pc==0x187bc){if(x->fresh_ready)x->words[0].value|=0x20000;else x->words[0].value&=~UINT32_C(0x20000);if(x->unknown_fresh)x->words[0].known&=~UINT32_C(0x20000);}
        if(q->pc==0x187a8 && x->partial_counter)x->words[3].known=UINT32_C(0xfffffffe);
        if(q->pc==0x187ca && x->selector_override)x->words[4].value=2;
        if(q->pc==0x18806){x->pll++;if(x->pll_at && x->pll>=x->pll_at)x->words[0].value|=0x2000000;else x->words[0].value&=~UINT32_C(0x2000000);}
        if(q->pc==0x18824){x->sw++;if(x->switch_at && x->sw>=x->switch_at)x->words[1].value=(x->words[1].value&~UINT32_C(12))|8;else x->words[1].value&=~UINT32_C(12);if(x->unknown_switch)x->words[1].known&=~UINT32_C(12);}
        *out=x->words[slot];
    }else{CHECK(q->kind==VC_WRITE32);x->words[slot].value=q->value;x->words[slot].known=q->known;}
    return VC_RETURNED;
}
static void reset(fixture *x,vc_model *m,uint32_t sp){unsigned i;vc_backend b;memset(x,0,sizeof(*x));for(i=0;i<5;i++)x->words[i].known=UINT32_MAX;x->sp8=sp-8;x->sp12=sp-4;x->ready_at=x->pll_at=x->switch_at=1;x->fresh_ready=1;b.context=x;b.invoke=provider;vc_init(m,&b);}
static void normal(void){
    static const uint32_t pcs[]={0x1874e,0x1875a,0x1875c,0x18764,0x18766,0x18770,0x18772,0x1877c,0x1877e,0x18788,0x1878e,0x18790,0x18792,0x18794,0x1879a,0x187a2,0x187a6,0x187a8,0x187ac,0x187ae,0x187bc,0x187c8,0x187ca,0x187d6,0x187de,0x187e0,0x187e2,0x187e4,0x187ea,0x187ec,0x187f0,0x187f2,0x187fa,0x187fc,0x18804,0x18806,0x18810,0x18818,0x1881a,0x18820,0x18824};
    vc_model m;unsigned i;reset(&f,&m,0x20010000);CHECK(vc_clock(&m,0x20010000)==VC_RETURNED);
    CHECK(f.count==41 && m.operations==41 && m.hse_samples==1 && m.pll_samples==1 && m.switch_samples==1);
    CHECK(m.entry_sp==0x20010000 && m.frame_sp==0x2000fff0 && m.frame_entered && m.frame_restored && m.boundary==VC_NONE);
    CHECK(f.words[0].value==0x3030001 && f.words[1].value==0x29040a && f.words[2].value==0x9f0000 && f.words[3].value==1 && f.words[4].value==1);
    for(i=0;i<41;i++)CHECK(f.trace[i].pc==pcs[i]);
    CHECK(f.trace[23].kind==VC_READ32 && f.trace[24].kind==VC_WRITE32 && f.trace[23].address==REG+4 && f.trace[24].value==f.trace[26].value);
    groups++;
}
static void timeout_and_cold_tail(void){vc_model m;reset(&f,&m,0x20010000);f.ready_at=0;f.fresh_ready=0;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.hse==4096 && m.hse_samples==4096);CHECK(f.count==24594 && f.words[3].value==4096 && f.words[4].value==0 && !f.pll && !f.sw && m.frame_restored);CHECK(f.trace[f.count-2].pc==0x18830 && f.trace[f.count-1].pc==0x187ca);reset(&f,&m,0x20010000);f.fresh_ready=0;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.hse==1 && !f.pll && f.words[4].value==0);groups++;}
static void fresh_reads_and_aliases(void){vc_model m;reset(&f,&m,0x20010000);f.ready_at=0;f.counter_override=1;f.counter_value=4095;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.hse==1 && f.words[3].value==4096 && f.pll==1);reset(&f,&m,0x20010000);f.counter_override=1;f.counter_value=UINT32_MAX;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.words[3].value==0);reset(&f,&m,0x20010000);f.selector_override=1;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && !f.pll && !f.sw && f.words[4].value==2);reset(&f,&m,8);CHECK(vc_clock(&m,8)==VC_RETURNED && m.frame_sp==UINT32_C(0xfffffff8) && f.trace[11].address==0 && f.trace[12].address==4);groups++;}
static void delayed_and_nonreturning_polls(void){vc_model m;reset(&f,&m,0x20010000);f.ready_at=3;f.pll_at=4;f.switch_at=5;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.hse==3 && f.pll==4 && f.sw==5 && f.words[3].value==3);reset(&f,&m,0x20010000);f.pll_at=0;m.max_operations=80;CHECK(vc_clock(&m,0x20010000)==VC_OBSERVATION_LIMIT && m.boundary==VC_BUDGET && m.boundary_pc==0x18806 && !m.frame_restored && !f.sw && f.words[0].value&0x1000000);reset(&f,&m,0x20010000);f.switch_at=0;m.max_operations=80;CHECK(vc_clock(&m,0x20010000)==VC_OBSERVATION_LIMIT && m.boundary_pc==0x18824 && !m.frame_restored && f.words[1].value&2);groups++;}
static void unknown_bits(void){vc_model m;reset(&f,&m,0x20010000);f.words[0].known=0;CHECK(vc_clock(&m,0x20010000)==VC_HALT && m.boundary==VC_BRANCH_UNKNOWN && m.boundary_pc==0x187b0);CHECK(f.trace[1].known==1 && f.trace[1].value==1);reset(&f,&m,0x20010000);f.unknown_fresh=1;CHECK(vc_clock(&m,0x20010000)==VC_HALT && m.boundary_pc==0x187c2 && !m.frame_restored);reset(&f,&m,0x20010000);f.partial_counter=1;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.words[3].value==1 && f.words[3].known==UINT32_C(0xfffffffc));reset(&f,&m,0x20010000);f.words[1].known=0;CHECK(vc_clock(&m,0x20010000)==VC_RETURNED && f.words[1].known!=UINT32_MAX);reset(&f,&m,0x20010000);f.unknown_switch=1;CHECK(vc_clock(&m,0x20010000)==VC_HALT && m.boundary_pc==0x18828);groups++;}
static void cuts(void){vc_model m;unsigned i,j;reset(&g,&m,0x20010000);CHECK(vc_clock(&m,0x20010000)==VC_RETURNED);for(j=0;j<2;j++)for(i=1;i<=41;i++){reset(&f,&m,0x20010000);f.cut=i;f.cut_flow=j?VC_TRANSFER:VC_HALT;CHECK(vc_clock(&m,0x20010000)==f.cut_flow && f.count==i && !m.frame_restored);CHECK(!memcmp(f.trace,g.trace,i*sizeof(vc_request)));if(i==1)CHECK(!m.frame_entered);else CHECK(m.frame_entered);}groups++;}
static void budgets_and_missing(void){vc_model m;reset(&f,&m,0x20010000);m.max_operations=0;CHECK(vc_clock(&m,0x20010000)==VC_OBSERVATION_LIMIT && !f.count && !m.frame_entered);reset(&f,&m,0x20010000);m.max_operations=13;CHECK(vc_clock(&m,0x20010000)==VC_OBSERVATION_LIMIT && f.count==13 && f.words[3].value==0 && f.words[4].value==0 && m.boundary_pc==0x18794);vc_init(&m,NULL);CHECK(vc_clock(&m,0x20010000)==VC_HALT && m.operations==1 && !m.frame_entered);groups++;}
int main(void){normal();timeout_and_cold_tail();fresh_reads_and_aliases();delayed_and_nonreturning_polls();unknown_bits();cuts();budgets_and_missing();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"synthetic_backend_only\":true}\n",groups,checks);return 0;}
