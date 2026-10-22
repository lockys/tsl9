/* Independent source-derived callback scenarios; hosted effects, no ISA engine. */
#include "callback.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { GP=0x21000000u, SP=0x21001000u, QUEUE=0x2000b18cu,
       DESC=0x2000bdf8u, MESSAGE=0x21003000u, BUFFER=0x21004000u };
typedef struct byte_cell { uint32_t address;uint8_t value; } byte_cell;
typedef struct fixture {
    byte_cell bytes[2048];unsigned used;
    cb_effect effects[256];unsigned count;
    unsigned scenario;
    uint32_t message,gate_result,capacity,allocation,send_result;
    uint32_t first_gate_count;
    uint32_t stop_site;
    cb_flow stop_flow;
} fixture;
static unsigned checks,cases;
#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"independent callback check failed line %u: %s\n",(unsigned)__LINE__,#v);exit(1);}}while(0)
static uint32_t load(fixture *f,uint32_t address,unsigned width){
    uint32_t result=0;unsigned i,j;
    for(i=0;i<width/8u;++i)for(j=0;j<f->used;++j)
        if(f->bytes[j].address==address+i){result|=(uint32_t)f->bytes[j].value<<(i*8u);break;}
    return result;
}
static void store(fixture *f,uint32_t address,unsigned width,uint32_t value){
    unsigned i,j;
    for(i=0;i<width/8u;++i){
        for(j=0;j<f->used;++j)if(f->bytes[j].address==address+i)break;
        if(j==f->used){CHECK(f->used<2048u);f->bytes[f->used++].address=address+i;}
        f->bytes[j].value=(uint8_t)(value>>(i*8u));
    }
}
static cb_flow provider(void *user,cb_host *h,cb_effect *e){
    fixture *f=(fixture *)user;
    CHECK(f->count<256u);f->effects[f->count++]=*e;
    if(e->kind==CB_READ){e->value=load(f,e->address,e->width);
        if(f->scenario==6u && e->source_site==0x868eu)h->values.gp+=0x100u;}
    else if(e->kind==CB_WRITE)store(f,e->address,e->width,e->value);
    else if(e->kind==CB_OPAQUE_CALL){
        if(e->source_site==f->stop_site)return f->stop_flow;
        switch(e->source_site){
        case 0x8640u:
            h->args[0]=f->message;
            if(f->scenario==1u){h->values.lane=0x42000u;h->values.events=0x12348008u;}
            break;
        case 0x865cu:
            if(f->scenario==1u)h->values.record=MESSAGE+0x100u;
            break;
        case 0x86e0u: case 0x87c6u:
            ++f->first_gate_count;h->args[0]=f->gate_result;break;
        case 0x8704u:h->args[0]=f->capacity;break;
        case 0x87a2u:
            h->args[0]=f->allocation;
            if(f->scenario==2u)store(f,QUEUE,8,0u);
            break;
        case 0x87bau:
            if(f->scenario==3u){h->values.gp=GP+0x200u;h->values.connection=0xabcd1234u;}
            break;
        case 0x8812u:
            h->args[0]=f->send_result;
            if(f->scenario==4u){store(f,QUEUE+4u,16,65530u);store(f,DESC+2u,16,10u);}
            break;
        case 0x8884u:
            if(f->scenario==5u){
                unsigned slot;h->values.events=0x88888888u;h->values.sp=SP-48u+0x100u;
                for(slot=4u;slot<=44u;slot+=4u)store(f,h->values.sp+slot,32,0xbeef0000u+slot);
                store(f,h->values.sp+44u,32,0x87654321u);
            }
            break;
        default:break;
        }
    }
    return CB_CONTINUE;
}
static void init(fixture *f,cb_host *h){
    static const uint32_t slots[]={0x6cu,0x12cu,0x68u,0x13cu,0xb8u,0x50u,
                                  0x128u,0x4cu,0x58u,0xd4u,0x1a8u,0x1a4u};
    unsigned i;
    memset(f,0,sizeof(*f));memset(h,0,sizeof(*h));
    h->provider=provider;h->user=f;h->values.gp=GP;h->values.sp=SP;
    h->values.return_address=0x12345679u;h->values.events=0xf0u;
    h->diagnostic_budget=2000u;
    for(i=0;i<8u;++i)h->args[i]=0xa0000000u+i;
    store(f,GP+0x94u,8,7u);store(f,GP+0x98u,8,8u);
    store(f,GP+0x96u,16,0xfffeu);store(f,GP+0x9au,16,0x4321u);
    store(f,GP+0x2au,16,0x5678u);store(f,GP+0x22au,16,0x1357u);
    store(f,QUEUE,8,1u);store(f,QUEUE+2u,16,20u);store(f,QUEUE+4u,16,4u);
    store(f,DESC+2u,16,6u);store(f,MESSAGE,8,0xb0u);store(f,MESSAGE+4u,8,0x23u);
    for(i=0;i<sizeof(slots)/sizeof(slots[0]);++i)
        store(f,0x40000u+slots[i],32,0x30000001u+slots[i]*2u);
    store(f,0x4212cu,32,0x30001235u);
    f->message=MESSAGE;f->allocation=BUFFER;f->gate_result=1u;f->capacity=23u;
}
static const cb_effect *event_at(const fixture *f,cb_effect_kind kind,uint32_t site){
    unsigned i;for(i=0;i<f->count;++i)if(f->effects[i].kind==kind&&f->effects[i].source_site==site)return &f->effects[i];
    return NULL;
}
static void normal(cb_host *h,uint32_t result){
    CHECK(h->flow==CB_CONTINUE);CHECK(h->result==result);CHECK(h->values.sp==SP);
    CHECK(h->values.events==0xf0u);CHECK(h->values.return_address==0x12345679u);++cases;
}
int main(void){
    fixture f;cb_host h;const cb_effect *e;uint32_t n;
    /* Fullword XOR, bit15 priority over bit3, null/non-B0/B0 receive paths. */
    for(n=0;n<3u;++n){
        init(&f,&h);if(n==0u)f.message=0u;if(n==1u)store(&f,MESSAGE,8,0xafu);
        tsl9_callback_host_8614(&h,0x12345678u,0xbeef8008u);normal(&h,0xbeef0008u);
        CHECK(!event_at(&f,CB_OPAQUE_CALL,0x8884u));
        CHECK((event_at(&f,CB_OPAQUE_CALL,0x865cu)!=NULL)==(n==2u));
        CHECK((event_at(&f,CB_OPAQUE_CALL,0x8666u)!=NULL)==(n!=0u));
        if(n==1u){e=event_at(&f,CB_OPAQUE_CALL,0x8666u);CHECK(e&&e->args[4]==0xafu);}
    }
    init(&f,&h);f.scenario=1u;tsl9_callback_host_8614(&h,7u,0x8000u);normal(&h,0x12340008u);
    e=event_at(&f,CB_OPAQUE_CALL,0x865cu);CHECK(e&&e->target==0x30001235u&&e->args[0]==MESSAGE+8u&&e->args[1]==0x23u);
    e=event_at(&f,CB_OPAQUE_CALL,0x8666u);CHECK(e&&e->args[0]==MESSAGE+0x100u);
    init(&f,&h);tsl9_callback_host_8614(&h,0x12345678u,0x80000008u);normal(&h,0x80000000u);
    e=event_at(&f,CB_OPAQUE_CALL,0x8884u);CHECK(e&&e->args[0]==0x12345678u&&e->args[1]==0u&&e->args[2]==0x19de0u);
    CHECK(!event_at(&f,CB_READ,0x868eu));
    init(&f,&h);tsl9_callback_host_8614(&h,0x107u,4u);normal(&h,0u);
    CHECK(!event_at(&f,CB_OPAQUE_CALL,0x886au));
    /* Exact-one gate is deliberately different from later low-bit gate. */
    for(n=2u;n<=3u;++n){
        init(&f,&h);f.gate_result=n;tsl9_callback_host_8614(&h,7u,1u);normal(&h,0u);
        CHECK(load(&f,QUEUE+2u,16)==0u);CHECK(!event_at(&f,CB_OPAQUE_CALL,0x8704u));
    }
    for(n=0u;n<4u;++n){
        init(&f,&h);f.capacity=n;tsl9_callback_host_8614(&h,7u,1u);normal(&h,0u);
        CHECK(load(&f,DESC+2u,16)==(n==3u?0u:16u));CHECK(load(&f,QUEUE,8)==10u);
    }
    init(&f,&h);store(&f,QUEUE+2u,16,0x8004u);store(&f,QUEUE+4u,16,4u);
    tsl9_callback_host_8614(&h,7u,1u);normal(&h,0u);CHECK(load(&f,QUEUE+2u,16)==0u);
    init(&f,&h);f.allocation=0u;f.scenario=2u;tsl9_callback_host_8614(&h,7u,2u);normal(&h,0u);
    CHECK(load(&f,QUEUE,8)==255u);e=event_at(&f,CB_OPAQUE_CALL,0x87f8u);
    CHECK(e&&e->args[0]==7u&&e->args[1]==2u&&e->args[2]==2u);
    init(&f,&h);f.gate_result=3u;f.scenario=3u;tsl9_callback_host_8614(&h,7u,2u);normal(&h,0u);
    e=event_at(&f,CB_OPAQUE_CALL,0x87c6u);CHECK(e&&e->args[0]==0xabcd1234u&&e->args[1]==GP+0x280u);
    CHECK(event_at(&f,CB_OPAQUE_CALL,0x8812u)!=NULL);CHECK(!event_at(&f,CB_OPAQUE_CALL,0x87d8u));
    init(&f,&h);f.scenario=4u;tsl9_callback_host_8614(&h,7u,2u);normal(&h,0u);
    CHECK(load(&f,QUEUE+4u,16)==4u);CHECK(load(&f,QUEUE,8)==1u);
    e=event_at(&f,CB_OPAQUE_CALL,0x87bau);CHECK(e&&e->args[0]==BUFFER&&e->args[1]==QUEUE+10u&&e->args[2]==6u);
    init(&f,&h);f.send_result=5u;tsl9_callback_host_8614(&h,7u,2u);normal(&h,0u);
    CHECK(event_at(&f,CB_OPAQUE_CALL,0x87d8u)!=NULL);CHECK(load(&f,QUEUE,8)==0u);
    init(&f,&h);tsl9_callback_host_8614(&h,7u,4u);normal(&h,0u);e=event_at(&f,CB_OPAQUE_CALL,0x886au);
    CHECK(e&&e->target_register==6u&&e->defined_argument_mask==63u&&e->args[0]==0xfffeu&&
          e->args[1]==12u&&e->args[2]==24u&&e->args[3]==0u&&e->args[4]==200u&&e->args[5]==7u);
    init(&f,&h);f.scenario=5u;tsl9_callback_host_8614(&h,7u,8u);
    CHECK(h.flow==CB_CONTINUE&&h.result==0x88888880u&&h.values.sp==SP+0x100u);
    CHECK(h.values.return_address==0x87654321u&&h.values.events==0xbeef0028u);++cases;
    init(&f,&h);f.scenario=6u;tsl9_callback_host_8614(&h,7u,4u);
    CHECK(h.flow==CB_UNKNOWN);CHECK(f.effects[f.count-1u].source_site==0x868eu);++cases;
    for(n=CB_HALT;n<=CB_UNKNOWN;++n){
        unsigned i;init(&f,&h);f.stop_site=0x8640u;f.stop_flow=(cb_flow)n;
        tsl9_callback_host_8614(&h,7u,0x8000u);CHECK(h.flow==(cb_flow)n);
        CHECK(h.values.sp==SP-48u);CHECK(f.effects[f.count-1u].source_site==0x8640u);
        for(i=0;i<f.count;++i)CHECK(f.effects[i].source_site!=0x866cu);++cases;
    }
    printf("{\"cases\":%u,\"checks\":%u,\"conditional_HOST_only\":true,\"physical_GPR_or_ROM_proof\":false}\n",cases,checks);
    return 0;
}
