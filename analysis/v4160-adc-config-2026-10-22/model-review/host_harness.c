#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "adc_config.h"

/* This is a synthetic typed-I/O oracle, not a CPU/register simulator. */
typedef struct event { unsigned kind; uint32_t address,value; } event;
typedef struct fixture {
    uint8_t memory[256],initial[256],expected_memory[256];
    event expected[14];
    uint32_t base,config;
    unsigned scenario,index,stop,checks;
    ml_flow stop_flow;
    int failed;
} fixture;
static unsigned cases,total_checks;
#define REQUIRE(F,X) do { (F)->checks++; if(!(X)){fprintf(stderr,"failure line %u scenario %u effect %u\n",(unsigned)__LINE__,(F)->scenario,(F)->index);(F)->failed=1;} } while(0)
static uint32_t word(const uint8_t *m,uint32_t a)
{
    uint32_t v=0;unsigned i;for(i=0;i<4;i++)v|=(uint32_t)m[(a+i)&255u]<<(8u*i);return v;
}
static void store(uint8_t *m,uint32_t a,uint32_t v)
{
    unsigned i;for(i=0;i<4;i++)m[(a+i)&255u]=(uint8_t)(v>>(8u*i));
}
static void mutate(fixture *f,uint8_t *m,unsigned at)
{
    if(f->scenario==4u){
        if(at==6u){store(m,f->base+8u,UINT32_C(0xf1e2d3c4));store(m,f->config+12u,UINT32_C(0x80000021));}
        if(at==12u)m[(f->config+20u)&255u]=255u;
    }
}
static void oracle(fixture *f)
{
    static const unsigned kind[14]={32,32,32,32,32,132,32,32,32,32,132,32,8,132};
    static const unsigned offset[14]={4,24,0,28,4,4,8,12,16,8,8,44,20,44};
    static const unsigned cfg[14]={0,1,1,1,1,0,0,1,1,1,0,0,1,0};
    uint8_t m[256];uint32_t v[14]={0};unsigned i;
    memcpy(m,f->initial,sizeof(m));
    for(i=0;i<14;i++){
        uint32_t a=(cfg[i]?f->config:f->base)+offset[i];mutate(f,m,i);
        f->expected[i].kind=kind[i];f->expected[i].address=a;
        if(i==5u)v[i]=(v[0]&UINT32_C(0xe0f0feff))|v[1]|v[2]|v[3]|(v[4]<<8);
        else if(i==10u)v[i]=(v[6]&UINT32_C(0xfff1f7fd))|v[7]|v[8]|(v[9]<<1);
        else if(i==13u)v[i]=(v[11]&UINT32_C(0xff0fffff))|(((v[12]-1u)&255u)<<20);
        else v[i]=kind[i]==8u?m[a&255u]:word(m,a);
        f->expected[i].value=v[i];if(kind[i]==132u)store(m,a,v[i]);
    }
    memcpy(f->expected_memory,m,sizeof(m));
}
static ml_flow callback(fixture *f,unsigned kind,uint32_t address,uint32_t *value)
{
    unsigned i=f->index;
    REQUIRE(f,i<14u);if(i>=14u)return ML_UNKNOWN;
    REQUIRE(f,kind==f->expected[i].kind);REQUIRE(f,address==f->expected[i].address);
    f->index++;if(i==f->stop)return f->stop_flow;
    mutate(f,f->memory,i);
    if(kind==132u){REQUIRE(f,*value==f->expected[i].value);store(f->memory,address,*value);}
    else {*value=kind==8u?UINT32_C(0xa5f00000)|f->memory[address&255u]:word(f->memory,address);REQUIRE(f,(*value&(kind==8u?255u:UINT32_MAX))==f->expected[i].value);}
    return ML_CONTINUE;
}
static ml_flow r8(void *p,uint32_t a,uint32_t *v){return callback((fixture *)p,8u,a,v);}
static ml_flow r32(void *p,uint32_t a,uint32_t *v){return callback((fixture *)p,32u,a,v);}
static ml_flow w32(void *p,uint32_t a,uint32_t v){return callback((fixture *)p,132u,a,&v);}
static int one(unsigned scenario,unsigned stop,ml_flow flow,unsigned budget,unsigned byte20)
{
    fixture f;ml_io io;ml_result result;unsigned i,completed;
    memset(&f,0,sizeof(f));memset(&io,0,sizeof(io));f.scenario=scenario;f.stop=stop;f.stop_flow=flow;
    f.base=scenario==5u?UINT32_C(0xfffffff0):32u;
    f.config=scenario==1u?f.base:scenario==2u?f.base-8u:scenario==3u?f.base-12u:128u;
    for(i=0;i<256u;i++)f.initial[i]=(uint8_t)(i*37u+scenario*19u+0x63u);
    store(f.initial,f.config+0u,UINT32_C(0x80000000));store(f.initial,f.config+4u,UINT32_C(0x0081f203));
    store(f.initial,f.config+8u,UINT32_C(0xc0123456));store(f.initial,f.config+12u,UINT32_C(0x40000020));
    store(f.initial,f.config+16u,UINT32_C(0x20000040));store(f.initial,f.config+24u,UINT32_C(0x10000080));
    store(f.initial,f.config+28u,UINT32_C(0x08000100));f.initial[(f.config+20u)&255u]=(uint8_t)byte20;
    memcpy(f.memory,f.initial,sizeof(f.memory));oracle(&f);
    io.user=&f;io.read8=r8;io.read32=r32;io.write32=w32;io.diagnostic_budget=budget;
    io.flow=ML_HALT;io.effects=77u; /* The typed call must start a fresh trace. */
    result=tsl9_adc_config_io(&io,f.base,f.config);
    completed=budget<14u?budget:stop<14u?stop+1u:14u;
    REQUIRE(&f,f.index==completed);REQUIRE(&f,io.effects==completed);
    if(budget<14u){REQUIRE(&f,result.flow==ML_UNKNOWN&&result.known==0u);}
    else if(stop<14u){REQUIRE(&f,result.flow==flow&&result.known==0u);}
    else {REQUIRE(&f,result.flow==ML_CONTINUE&&result.known==1u&&result.value==f.base);REQUIRE(&f,memcmp(f.memory,f.expected_memory,sizeof(f.memory))==0);}
    /* Independently reconstruct only completed successful effects. A stopped
     * write must not be committed, and no later synthetic mutation may occur. */
    memcpy(f.expected_memory,f.initial,sizeof(f.expected_memory));
    for(i=0;i<completed;i++)if(i!=stop){mutate(&f,f.expected_memory,i);if(f.expected[i].kind==132u)store(f.expected_memory,f.expected[i].address,f.expected[i].value);}
    REQUIRE(&f,memcmp(f.memory,f.expected_memory,sizeof(f.memory))==0);
    total_checks+=f.checks;cases++;return !f.failed;
}
int main(void)
{
    unsigned scenario,stop,flow,budget,byte;int ok=1;
    for(scenario=0;scenario<6u;scenario++)for(byte=0;byte<3u;byte++)ok=one(scenario,99u,ML_CONTINUE,14u,byte==0u?0u:byte==1u?1u:255u)&&ok;
    for(stop=0;stop<14u;stop++)for(flow=1;flow<=3u;flow++)ok=one(4u,stop,(ml_flow)flow,14u,1u)&&ok;
    for(budget=0;budget<14u;budget++)ok=one(4u,99u,ML_CONTINUE,budget,1u)&&ok;
    if(!ok)return 1;
    printf("{\"passed\":true,\"cases\":%u,\"checks\":%u,\"ordered_effects\":14,\"synthetic_IO\":true,\"RV32_execution\":false}\n",cases,total_checks);return 0;
}
