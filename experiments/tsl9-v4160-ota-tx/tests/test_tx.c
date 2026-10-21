#include "tx_native.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GP UINT32_C(0x20000000)
#define SP UINT32_C(0x20002000)
#define BASE UINT32_C(0x2000b18c)
#define SRC UINT32_C(0x30000000)
static unsigned checks,cases;
#define CHECK(v) do {++checks;if(!(v)){fprintf(stderr,"failure line %u\n",(unsigned)__LINE__);exit(1);}}while(0)
typedef struct fixture {
    uint8_t gp[2048],stack[8192],storage[4096],source[4096];
    tx_event events[5000];unsigned count,gates,tails;
    uint32_t gate_result[2],stop_at,mutation,tail_result;
    tx_flow stop_flow;
    tx_host h;
} fixture;
static fixture f;
static uint8_t *byte_at(fixture *p,uint32_t a)
{
    if(a-GP<sizeof(p->gp))return &p->gp[a-GP];
    if(a-(SP-4096u)<sizeof(p->stack))return &p->stack[a-(SP-4096u)];
    if(a-BASE<sizeof(p->storage))return &p->storage[a-BASE];
    if(a-SRC<sizeof(p->source))return &p->source[a-SRC];
    CHECK(0);return NULL;
}
static uint32_t get(fixture *p,uint32_t a,unsigned n)
{uint32_t v=0;unsigned i;for(i=0;i<n;++i)v|=(uint32_t)*byte_at(p,a+i)<<(8u*i);return v;}
static void put(fixture *p,uint32_t a,unsigned n,uint32_t v)
{unsigned i;for(i=0;i<n;++i)*byte_at(p,a+i)=(uint8_t)(v>>(8u*i));}
static tx_flow provider(tx_host *h,tx_event *e,void *user)
{
    fixture *p=(fixture *)user;
    CHECK(p->count<5000u);p->events[p->count++]=*e;
    if(p->stop_at==p->count)return p->stop_flow;
    if(e->kind==TX_READ) {
        e->value=e->address==0x4013cu?0x12345u:e->address==0x40050u?0x56789u:get(p,e->address,e->width);
        e->value_known=1;
        if(p->mutation==6u&&e->site==0x8a6au)e->value_known=0;
        if(p->mutation==7u&&e->site==0x8a6au)tx_set(h,17,99u);
    } else if(e->kind==TX_WRITE) {
        CHECK(e->value_known);put(p,e->address,e->width,e->value);
        if(p->mutation==8u&&e->site==0x8b32u)put(p,SP-8u,4,0x91929394u);
        if(p->mutation==9u&&e->site==0x8b62u&&h->loop_steps==1u)put(p,SRC+1u,1,201u);
    } else if(e->kind==TX_GATE_CALL) {
        unsigned gate=p->gates++;
        CHECK(gate<2u&&e->raw_target==0x12345u&&e->target==0x12344u);
        CHECK(e->args_known==15u);
        CHECK(h->regs[1]==e->site+2u);
        if(p->mutation==1u&&gate==0u) {
            tx_set(h,3,GP+512u);tx_set(h,18,9u);tx_set(h,9,SRC+32u);
            tx_set(h,8,3u);tx_set(h,19,0x45u);tx_set(h,12,0xcafebabeu);tx_set(h,13,0xfedcba98u);
        }
        if(p->mutation==1u&&gate==1u) {
            CHECK(e->args[0]==9u&&e->args[1]==GP+512u+128u);
            CHECK(e->args[2]==0xcafebabeu&&e->args[3]==0xfedcba98u);
        }
        if(p->mutation==2u)tx_set(h,8,65536u);
        if(p->mutation==3u)tx_set(h,9,BASE+10u);
        if(p->mutation==4u) {
            tx_set(h,2,SP-128u);
            put(p,SP-128u+28u,4,0x8899u);put(p,SP-128u+24u,4,0x101u);
            put(p,SP-128u+20u,4,0x102u);put(p,SP-128u+16u,4,0x103u);put(p,SP-128u+12u,4,0x104u);
        }
        tx_set(h,10,p->gate_result[gate]);
        if(p->mutation==5u)h->known&=~(UINT32_C(1)<<10);
    } else {
        CHECK(e->kind==TX_TAIL_CALL);++p->tails;
        CHECK(e->raw_target==0x56789u&&e->target==0x56788u);
        CHECK(e->args[1]==1u&&e->args[3]==BASE&&e->args_known==15u);
        CHECK(e->args[0]==get(p,e->args[2],1));
        tx_set(h,10,p->tail_result);tx_set(h,11,0xabcdu);
    }
    return TX_CONTINUE;
}
static void setup(void)
{
    unsigned i;memset(&f,0,sizeof(f));tx_host_init(&f.h,provider,&f);
    f.h.known=UINT32_MAX;for(i=0;i<32u;++i)f.h.regs[i]=0x70000000u+i;
    tx_set(&f.h,2,SP);tx_set(&f.h,3,GP);tx_set(&f.h,1,0x9091u);
    f.gate_result[0]=1u;f.gate_result[1]=1u;f.tail_result=0xabcdef01u;
    put(&f,GP+0x96u,2,7u);put(&f,GP+0x9au,2,7u);
    put(&f,GP+0x94u,1,0x31u);put(&f,GP+0x98u,1,0x32u);
    put(&f,GP+512u+0x9au,2,9u);put(&f,GP+512u+0x98u,1,0x33u);
    for(i=0;i<sizeof(f.source);++i)f.source[i]=(uint8_t)(i*13u+3u);
    ++cases;
}
static tx_result run(uint32_t length){return tsl9_ota_tx_8a56(&f.h,7u,0x24u,SRC,length);}
static void normal(unsigned lane,uint32_t n,uint32_t command,uint32_t source)
{
    uint32_t b=BASE+lane*1062u,sum=(n&255u)+(n>>8)+command,i;
    tx_result r=tsl9_ota_tx_8a56(&f.h,7u,command,source,n);
    CHECK(r.flow==TX_RETURNED&&r.tail_delegated&&r.value_known&&r.value==f.tail_result);
    CHECK(r.raw_target==0x56789u&&r.raw_link==0x9091u&&r.link==0x9090u);
    CHECK(f.h.regs[2]==SP&&f.h.regs[11]==0xabcdu&&f.tails==1u);
    CHECK(get(&f,b+6u,2)==0x7f55u&&get(&f,b+8u,1)==(command&255u));
    CHECK(get(&f,b+9u,1)==((n>>8)&255u)&&get(&f,b+10u,1)==(n&255u));
    CHECK(get(&f,b+2u,2)==((n+6u)&65535u)&&get(&f,b+4u,2)==0u);
    for(i=0;i<n;++i){uint32_t v=get(&f,source+i,1);CHECK(get(&f,b+11u+i,1)==v);sum+=v;}
    CHECK(get(&f,b+11u+n,1)==(sum&255u));CHECK(f.h.regs[14]==(sum&255u));
    CHECK(f.h.regs[15]==0x40000u);CHECK(f.h.regs[12]==GP+0x94u+4u*lane);
    if(n==0u)CHECK(f.h.regs[16]==0x70000010u);
    for(i=0;i<f.count;++i)if(f.events[i].kind==TX_WRITE&&(f.events[i].site==0x8b32u||f.events[i].site==0x8b36u))CHECK(f.events[i].width==2u);
}
int main(void)
{
    uint32_t lengths[]={0u,1u,255u,256u,1039u};unsigned i,j;tx_result r;tx_event prefix[5000];unsigned prefix_n;
    for(i=0;i<5u;++i)for(j=0;j<2u;++j){setup();if(j)f.gate_result[0]=0u;normal(j,lengths[i],0x24u,SRC);}
    for(i=0;i<2u;++i){setup();r=run(i?UINT32_MAX:1040u);CHECK(r.flow==TX_RETURNED&&!r.tail_delegated&&r.value==7u&&f.count==0u&&f.h.regs[2]==SP&&f.h.regs[15]==1039u);}
    setup();put(&f,GP+0x96u,2,8u);put(&f,GP+0x9au,2,8u);r=run(3u);CHECK(r.value==7u&&r.flow==TX_RETURNED&&f.gates==0u&&f.tails==0u);
    setup();f.gate_result[0]=2u;f.gate_result[1]=9u;r=run(3u);CHECK(r.value==9u&&f.gates==2u&&f.tails==0u&&f.h.regs[12]==1u);
    setup();r=tsl9_ota_tx_8a56(&f.h,0x10007u,0x24u,SRC,3u);CHECK(f.gates==0u&&r.value==0x10007u);
    setup();put(&f,GP+0x96u,2,0xfffeu);put(&f,GP+0x9au,2,0xfffeu);r=tsl9_ota_tx_8a56(&f.h,0xfffeu,0x24u,SRC,3u);CHECK(f.gates==0u&&!r.tail_delegated);
    setup();f.mutation=1u;f.gate_result[0]=0u;r=run(4u);CHECK(f.gates==2u&&r.tail_delegated&&get(&f,BASE+1062u+8u,1)==0x45u&&get(&f,BASE+1062u+2u,2)==9u&&f.h.regs[12]==GP+512u+0x98u);
    setup();f.mutation=2u;f.h.loop_budget=3u;r=run(1u);CHECK(r.flow==TX_UNKNOWN&&r.budget_exhausted&&f.h.loop_steps==3u&&f.tails==0u&&f.h.regs[2]==SP-32u);
    setup();f.mutation=3u;put(&f,BASE+10u,1,9u);r=run(4u);CHECK(r.tail_delegated);for(i=0;i<4u;++i)CHECK(get(&f,BASE+11u+i,1)==4u);
    setup();f.mutation=4u;r=run(1u);CHECK(r.tail_delegated&&r.raw_link==0x8899u&&f.h.regs[2]==SP-96u&&f.h.regs[8]==0x101u&&f.h.regs[18]==0x103u);
    setup();f.mutation=5u;r=run(1u);CHECK(r.flow==TX_UNKNOWN&&f.tails==0u);
    setup();f.mutation=6u;r=run(1u);CHECK(r.flow==TX_UNKNOWN&&f.gates==0u);
    setup();f.mutation=7u;r=run(1u);CHECK(r.flow==TX_UNKNOWN&&r.unsupported_memory_register_mutation);
    setup();f.mutation=8u;r=run(1u);CHECK(r.tail_delegated&&f.h.regs[8]==0x91929394u);
    setup();f.mutation=9u;r=run(3u);CHECK(r.tail_delegated&&get(&f,BASE+12u,1)==201u);
    setup();r=run(2u);CHECK(r.tail_delegated);prefix_n=f.count;memcpy(prefix,f.events,prefix_n*sizeof(tx_event));
    for(i=1u;i<=prefix_n;++i)for(j=0;j<3u;++j){setup();f.stop_at=i;f.stop_flow=j==0u?TX_UNKNOWN:j==1u?TX_HALT:TX_TRANSFER;r=run(2u);CHECK(r.flow==f.stop_flow&&f.count==i);CHECK(memcmp(prefix,f.events,i*sizeof(tx_event))==0);}
    printf("{\"passed\":true,\"groups\":4,\"cases\":%u,\"checks\":%u,\"synthetic_provider\":true,\"RV32_execution\":false}\n",cases,checks);return 0;
}
