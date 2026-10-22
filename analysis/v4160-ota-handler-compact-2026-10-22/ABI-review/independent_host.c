/* Independent source-derived narratives; synthetic memory/callees only. */
#include "ota_handler.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GP UINT32_C(0x21000000)
#define GP2 UINT32_C(0x21000100)
#define SP UINT32_C(0x21001000)
#define PAY UINT32_C(0x21002002)
#define OTHER UINT32_C(0x21003000)
#define FLASH UINT32_C(0x08001000)
typedef struct byte_cell { uint32_t address;uint8_t value; } byte_cell;
typedef struct fixture {
    byte_cell memory[5000];unsigned used;
    oh_effect events[1100];unsigned count,calls,quarters;
    unsigned scenario,source_pairs;
    uint32_t stop_site;oh_flow stop_flow;
} fixture;
static fixture f;
static unsigned checks,cases,dispatches;
#define CHECK(v) do { ++checks;if(!(v)){fprintf(stderr,"independent OTA handler check failed line %u: %s\n",(unsigned)__LINE__,#v);exit(1);} } while(0)
#define CAPACITY(v) do { if(!(v)){fprintf(stderr,"independent fixture capacity exhausted\n");exit(1);} } while(0)

static uint32_t load(const fixture *x,uint32_t address,unsigned width){
    uint32_t value=0;unsigned i,j;
    for(i=0;i<width/8u;++i)for(j=0;j<x->used;++j)
        if(x->memory[j].address==address+i){value|=(uint32_t)x->memory[j].value<<(i*8u);break;}
    return value;
}
static void store(fixture *x,uint32_t address,unsigned width,uint32_t value){
    unsigned i,j;
    for(i=0;i<width/8u;++i){
        for(j=0;j<x->used;++j)if(x->memory[j].address==address+i)break;
        if(j==x->used){CAPACITY(x->used<5000u);x->memory[x->used++].address=address+i;}
        x->memory[j].value=(uint8_t)(value>>(i*8u));
    }
}
static oh_flow provider(void *user,oh_host *h,oh_effect *e){
    fixture *x=(fixture *)user;unsigned i;
    CAPACITY(x->count<1100u);x->events[x->count++]=*e;
    if(e->kind==OH_READ){
        e->value=load(x,e->address,e->width);e->value_known=1;
        if(x->scenario==7u && e->source_site==0x9d10u)
            store(x,PAY+2u,32,load(x,PAY+2u,32)^1u);
    }else if(e->kind==OH_WRITE){
        store(x,e->address,e->width,e->value);
    }else{
        CHECK(e->kind==OH_CALL);++x->calls;
        if(e->callee==OH_QUARTER_9C0A){
            ++x->quarters;
            CHECK(h->values.buffer==x->quarters*256u);
            for(i=0;i<256u;++i)store(x,e->args[0]+i,8,load(x,e->args[1]+i,8));
            if(x->scenario==6u&&x->quarters==2u)return OH_TRANSFER;
        }
        if(e->source_site==x->stop_site)return x->stop_flow;
        e->value=0;e->value_known=1;
        if(e->callee==OH_QUARTER_9C0A){
            e->value=0xdeadbeefu; /* The original caller does not test this result. */
            if(x->scenario==8u){h->values.buffer=h->values.limit;h->values.page=0x1234u;h->values.context=0xa5a5u;}
        }else if(e->callee==OH_UID_92F2){
            if(x->scenario==9u){
                store(x,PAY,8,0);h->values.flash=0x123u;h->values.gp=GP2;
            }else if(x->scenario==10u){
                h->values.buffer=OTHER;h->values.sp=SP+0x100u-48u;
                h->values.context=0x8765u;h->values.flash=0x345u;h->values.gp=GP2;
                store(x,OTHER,8,0);store(x,h->values.sp+12u,8,0x77u);store(x,h->values.sp+13u,8,0x88u);
            }else if(x->scenario==16u){
                h->values.buffer=OTHER;h->values.context=0xcafeu;h->values.gp=GP2;
                store(x,OTHER,8,255);store(x,OTHER+1u,8,255);
            }else if(x->scenario==14u)e->value_known=0;
        }
    }
    return OH_CONTINUE;
}
static void init(oh_host *h,unsigned scenario){
    unsigned i;memset(&f,0,sizeof(f));memset(h,0,sizeof(*h));f.scenario=scenario;
    h->provider=provider;h->user=&f;h->values.gp=GP;h->values.sp=SP;
    h->values.return_address=0x12345679u;h->values.buffer=0x11u;h->values.flash=0x22u;
    h->values.context=0x33u;h->values.source=0x44u;h->values.page=0x55u;h->values.limit=0x66u;
    h->diagnostic_budget=2000u;
    for(i=0;i<8u;++i)h->args[i]=0xa0000000u+i;
    store(&f,GP+169u,8,1);store(&f,GP2+169u,8,0xaa);
    store(&f,PAY,8,0);store(&f,PAY+1u,8,0);
    store(&f,0x4004cu,32,0x31000001u);
    for(i=0;i<1024u;++i){
        uint32_t value=(i*29u+7u)&255u;
        store(&f,PAY+2u+i,8,value);store(&f,FLASH+i,8,value);
    }
}
static void run(oh_host *h,uint32_t command,uint32_t payload,uint32_t length){
    ++dispatches;tsl9_ota_handler_host_9c4a(h,0x1357u,command,payload,length);
}
static const oh_effect *at(oh_effect_kind kind,uint32_t site,unsigned nth){
    unsigned i;for(i=0;i<f.count;++i)if(f.events[i].kind==kind&&f.events[i].source_site==site){
        if(!nth)return &f.events[i];--nth;
    }
    return NULL;
}
static unsigned count_at(oh_effect_kind kind,uint32_t site){
    unsigned i,n=0;for(i=0;i<f.count;++i)if(f.events[i].kind==kind&&f.events[i].source_site==site)++n;return n;
}
static unsigned index_at(oh_effect_kind kind,uint32_t site){
    unsigned i;for(i=0;i<f.count;++i)if(f.events[i].kind==kind&&f.events[i].source_site==site)return i;
    CHECK(0);return 0;
}
static void exact_call(const oh_effect *e,oh_callee callee,uint32_t target){
    CHECK(e!=NULL);CHECK(e->callee==callee);CHECK(e->target==target);
}
static void guard_cases(void){
    oh_host h;
    init(&h,1);run(&h,0x10057u,PAY,1026);CHECK(h.flow==OH_CONTINUE&&f.calls==0);
    CHECK(at(OH_READ,0x9c9cu,0)==NULL);++cases;
    init(&h,2);store(&f,GP+169u,8,0);run(&h,'W',PAY,1);
    CHECK(h.flow==OH_CONTINUE&&f.calls==0);CHECK(at(OH_READ,0x9c9cu,0)!=NULL);
    CHECK(at(OH_READ,0x9caau,0)==NULL);
    init(&h,2);run(&h,'W',PAY,1025);CHECK(f.calls==0&&at(OH_READ,0x9caau,0)==NULL);++cases;
    init(&h,3);store(&f,PAY+1u,8,28);run(&h,'W',PAY,1026);
    CHECK(h.flow==OH_CONTINUE&&f.calls==0);CHECK(at(OH_READ,0x9caau,0)->address==PAY);
    CHECK(at(OH_READ,0x9caeu,0)->address==PAY+1u);++cases;
}
static void write_cases(void){
    oh_host h;const oh_effect *e;unsigned i,n=0;
    init(&h,4);run(&h,'W',PAY,1026);CHECK(h.flow==OH_CONTINUE&&f.quarters==4u);
    for(i=0;i<4u;++i){e=at(OH_CALL,0x9d00u,i);exact_call(e,OH_QUARTER_9C0A,0x9c0au);
        CHECK(e->args[0]==FLASH+256u*i&&e->args[1]==PAY+2u+256u*i);}
    for(i=0;i<f.count;++i)if(f.events[i].kind==OH_READ&&f.events[i].source_site==0x9d10u){
        CHECK(i+1u<f.count&&f.events[i+1u].source_site==0x9d16u);
        CHECK(f.events[i].width==32u&&f.events[i].address==FLASH+4u*n);
        CHECK(f.events[i+1u].width==32u&&f.events[i+1u].address==PAY+2u+4u*n);++n;
    }
    CHECK(n==256u);e=at(OH_CALL,0x9df4u,0);exact_call(e,OH_PAGE_REPLY_9B8E,0x9b8eu);
    CHECK(e->args[0]==0x1357u&&e->args[1]=='W'&&e->args[2]==0u);++cases;
    init(&h,5);f.stop_site=0x9cecu;f.stop_flow=OH_UNKNOWN;run(&h,'W',PAY-1u,1026);
    CHECK(h.flow==OH_UNKNOWN&&f.quarters==0u);e=at(OH_CALL,0x9cecu,0);
    exact_call(e,OH_COPY_SLOT_4C,0x31000001u);CHECK(e->args[0]==((PAY+1u)&~3u));
    CHECK(e->args[1]==PAY+1u&&e->args[2]==1024u);++cases;
    init(&h,6);store(&f,FLASH,32,0);
    /* Stop at the second call, after its synthetic write, without a broad cutoff matrix. */
    run(&h,'W',PAY,1026);CHECK(h.flow==OH_TRANSFER&&f.quarters==2u);
    CHECK(load(&f,FLASH,32)==load(&f,PAY+2u,32));
    CHECK(at(OH_READ,0x9d10u,0)==NULL&&at(OH_CALL,0x9df4u,0)==NULL);
    ++cases;
    init(&h,7);run(&h,'W',PAY,1026);CHECK(f.quarters==4u&&h.flow==OH_CONTINUE);
    CHECK(count_at(OH_READ,0x9d10u)==1u&&count_at(OH_READ,0x9d16u)==1u);
    CHECK(index_at(OH_READ,0x9d10u)<index_at(OH_READ,0x9d16u));
    e=at(OH_CALL,0x9d7au,0);exact_call(e,OH_SMALL_REPLY_13F66,0x13f66u);
    CHECK(e->args[1]=='W'&&e->args[2]==255u);CHECK(at(OH_CALL,0x9df4u,0)==NULL);++cases;
    init(&h,8);run(&h,'W',PAY,1026);CHECK(h.flow==OH_CONTINUE&&f.quarters==1u);
    e=at(OH_CALL,0x9df4u,0);CHECK(e!=NULL&&e->args[0]==0xa5a5u&&e->args[2]==0x1234u);++cases;
}
static void live_start_cases(void){
    oh_host h;const oh_effect *e;
    init(&h,9);store(&f,PAY,8,5);run(&h,'S',PAY,15);
    CHECK(h.flow==OH_CONTINUE);CHECK(load(&f,SP-48u+12u,8)==5u&&load(&f,SP-48u+13u,8)==1u);
    CHECK(index_at(OH_WRITE,0x9d92u)<index_at(OH_CALL,0x9d9au));
    CHECK(index_at(OH_WRITE,0x9d96u)<index_at(OH_CALL,0x9d9au));
    e=at(OH_WRITE,0x9da6u,0);CHECK(e!=NULL&&e->address==GP2+169u&&(e->value&255u)==0x23u);
    e=at(OH_CALL,0x9db4u,0);exact_call(e,OH_PACKET_REPLY_13E98,0x13e98u);
    CHECK(e->args[2]==SP-48u+12u&&e->args[3]==2u);++cases;
    init(&h,10);store(&f,PAY,8,5);run(&h,'S',PAY,15);
    CHECK(at(OH_READ,0x9da0u,0)->address==OTHER);e=at(OH_CALL,0x9db4u,0);
    CHECK(e!=NULL&&e->args[0]==0x8765u&&e->args[2]==SP+0x100u-48u+12u);
    CHECK(load(&f,e->args[2],8)==0x77u&&load(&f,e->args[2]+1u,8)==0x88u);
    CHECK(at(OH_WRITE,0x9da6u,0)->address==GP2+169u);++cases;
}
static void control_cases(void){
    oh_host h;const oh_effect *e;
    init(&h,11);f.stop_site=0x9d3au;f.stop_flow=OH_HALT;run(&h,'U',PAY,271);
    CHECK(h.flow==OH_HALT&&load(&f,GP+169u,8)==0u);e=at(OH_CALL,0x9d3au,0);
    exact_call(e,OH_UID_92F2,0x92f2u);CHECK(e->args[0]==PAY+1u&&e->args[1]==14u);
    CHECK(index_at(OH_WRITE,0x9d36u)<index_at(OH_CALL,0x9d3au));
    CHECK(at(OH_READ,0x9d40u,0)==NULL&&f.calls==1u);++cases;
    init(&h,12);store(&f,PAY,8,1);f.stop_site=0x9d5au;f.stop_flow=OH_HALT;run(&h,'U',PAY,15);
    CHECK(h.flow==OH_HALT);e=at(OH_CALL,0x9d5au,0);exact_call(e,OH_SCHEDULE_9124,0x9124u);
    CHECK(e->args[0]==0x8e18u&&e->args[1]==0&&e->args[2]==200u&&e->args[3]==0);
    CHECK(at(OH_CALL,0x9d6eu,0)==NULL&&at(OH_CALL,0x9d7au,0)==NULL);++cases;
    init(&h,13);run(&h,'E',PAY,271);CHECK(h.flow==OH_CONTINUE&&f.calls==0u);
    CHECK(at(OH_READ,0x9df8u,0)!=NULL&&at(OH_READ,0x9e06u,0)==NULL);++cases;
    init(&h,14);store(&f,PAY,8,1);run(&h,'E',PAY,15);
    CHECK(f.calls==0u&&load(&f,GP+169u,8)==1u);CHECK(at(OH_READ,0x9e06u,0)!=NULL);
    init(&h,14);run(&h,'E',PAY,15);CHECK(h.flow==OH_UNKNOWN&&f.calls==1u);
    CHECK(load(&f,GP+169u,8)==1u&&at(OH_CALL,0x9e30u,0)==NULL);++cases;
    init(&h,15);run(&h,'E',PAY,15);CHECK(h.flow==OH_CONTINUE&&load(&f,GP+169u,8)==0u);
    CHECK(index_at(OH_WRITE,0x9e2cu)<index_at(OH_CALL,0x9e30u));
    e=at(OH_CALL,0x9e44u,0);CHECK(e!=NULL&&e->args[0]==0x99e8u&&e->args[2]==400u);
    e=at(OH_CALL,0x9db4u,0);CHECK(e!=NULL&&e->args[1]=='E'&&e->args[2]==0&&e->args[3]==0);++cases;
    init(&h,16);f.stop_site=0x9df4u;f.stop_flow=OH_TRANSFER;run(&h,'R',PAY,16);
    CHECK(h.flow==OH_TRANSFER);CHECK(at(OH_READ,0x9de2u,0)->address==OTHER);
    CHECK(at(OH_READ,0x9de6u,0)->address==OTHER+1u);e=at(OH_CALL,0x9df4u,0);
    CHECK(e!=NULL&&e->args[0]==0xcafeu&&e->args[1]=='R'&&e->args[2]==65535u);++cases;
}
int main(void){
    guard_cases();write_cases();live_start_cases();control_cases();
    printf("{\"passed\":true,\"narrative_cases\":%u,\"dispatches\":%u,\"checks\":%u,\"synthetic_HOST_only\":true,\"physical_ABI_proof\":false}\n",cases,dispatches,checks);
    return 0;
}
