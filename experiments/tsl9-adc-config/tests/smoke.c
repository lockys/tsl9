#include "adc_config.h"
#include <stdio.h>
#include <string.h>

typedef struct cell {uint32_t address;uint8_t value;} cell;
typedef struct event {uint32_t address,value,width,write;} event;
typedef struct fixture {
    cell cells[256];unsigned cells_used;
    event events[16];unsigned events_used;
    unsigned stop,mutate,budget;ml_flow flow;
    uint32_t mutate_address,mutate_value;
} fixture;
static unsigned checks,cases;
#define CHECK(x) do {checks++;if(!(x)){printf("failure line %u\n",(unsigned)__LINE__);return 1;}} while(0)
static uint8_t getbyte(fixture *f,uint32_t address)
{
    unsigned i;for(i=0;i<f->cells_used;i++)if(f->cells[i].address==address)return f->cells[i].value;
    return 0;
}
static void putbyte(fixture *f,uint32_t address,uint8_t value)
{
    unsigned i;for(i=0;i<f->cells_used;i++)if(f->cells[i].address==address){f->cells[i].value=value;return;}
    f->cells[f->cells_used].address=address;f->cells[f->cells_used].value=value;f->cells_used++;
}
static uint32_t getword(fixture *f,uint32_t address)
{
    uint32_t v=0;unsigned i;for(i=0;i<4;i++)v|=(uint32_t)getbyte(f,address+i)<<(8u*i);return v;
}
static void putword(fixture *f,uint32_t address,uint32_t value)
{
    unsigned i;for(i=0;i<4;i++)putbyte(f,address+i,(uint8_t)(value>>(8u*i)));
}
static ml_flow access(fixture *f,uint32_t address,uint32_t *value,unsigned width,unsigned write)
{
    event *e;unsigned n=f->events_used+1u;
    if(n==f->mutate)putword(f,f->mutate_address,f->mutate_value);
    e=&f->events[f->events_used++];e->address=address;e->width=width;e->write=write;
    e->value=write?*value:0;
    if(n==f->stop)return f->flow;
    if(write)putword(f,address,*value);
    else {*value=width==8?getbyte(f,address):getword(f,address);e->value=*value;}
    return ML_CONTINUE;
}
static ml_flow read8(void *p,uint32_t a,uint32_t *v){return access((fixture *)p,a,v,8,0);}
static ml_flow read32(void *p,uint32_t a,uint32_t *v){return access((fixture *)p,a,v,32,0);}
static ml_flow write32(void *p,uint32_t a,uint32_t v){return access((fixture *)p,a,&v,32,1);}
static void setup(fixture *f,uint32_t base,uint32_t config,uint32_t byte)
{
    static const uint32_t fields[8]={0x80010002u,0x12345678u,0x87654321u,0x000e0000u,0x40008000u,0,0x10000400u,0x00400010u};
    unsigned i;memset(f,0,sizeof(*f));f->budget=64;
    for(i=0;i<8;i++)putword(f,config+i*4u,fields[i]);
    putbyte(f,config+20u,(uint8_t)byte);
    putword(f,base+4u,0x55aa33ccu);putword(f,base+8u,0xa5c33c5au);putword(f,base+44u,0x10203040u);
}
/* Independent trace reference: literal source access schedule, full-width
 * fields and wrap. There is no pointer cast to any synthetic target address. */
static void reference(fixture *f,uint32_t base,uint32_t config)
{
    uint32_t v[14]={0},out;unsigned n;
    const uint32_t addresses[14]={base+4u,config+24u,config,config+28u,config+4u,base+4u,base+8u,config+12u,config+16u,config+8u,base+8u,base+44u,config+20u,base+44u};
    for(n=0;n<14;n++){
        unsigned write=n==5||n==10||n==13;
        if(n>=f->budget)return;
        if(n==5)v[n]=(v[0]&0xe0f0feffu)|v[1]|v[2]|v[3]|(v[4]<<8);
        if(n==10)v[n]=(v[6]&0xfff1f7fdu)|v[7]|v[8]|(v[9]<<1);
        if(n==13)v[n]=(v[11]&0xff0fffffu)|(((v[12]-1u)&255u)<<20);
        out=v[n];if(access(f,addresses[n],&out,n==12?8u:32u,write)!=ML_CONTINUE)return;
        v[n]=out;
    }
}
static int compare_case(fixture initial,uint32_t base,uint32_t config)
{
    fixture expected=initial,actual=initial;ml_io io;ml_result result;unsigned i;
    memset(&io,0,sizeof(io));io.user=&actual;io.read8=read8;io.read32=read32;io.write32=write32;io.diagnostic_budget=initial.budget;io.flow=ML_HALT;
    reference(&expected,base,config);result=tsl9_adc_config_io(&io,base,config);cases++;
    CHECK(actual.events_used==expected.events_used);
    for(i=0;i<expected.events_used;i++){
        CHECK(actual.events[i].address==expected.events[i].address);
        CHECK(actual.events[i].value==expected.events[i].value);
        CHECK(actual.events[i].width==expected.events[i].width);
        CHECK(actual.events[i].write==expected.events[i].write);
    }
    CHECK(actual.cells_used==expected.cells_used);
    for(i=0;i<expected.cells_used;i++)CHECK(getbyte(&actual,expected.cells[i].address)==expected.cells[i].value);
    if(initial.stop&&initial.stop<=initial.budget){CHECK(result.flow==initial.flow);CHECK(!result.known);}
    else if(initial.budget<14){CHECK(result.flow==ML_UNKNOWN);CHECK(!result.known);}
    else {CHECK(result.flow==ML_CONTINUE);CHECK(result.known==1);CHECK(result.value==base);}
    CHECK(io.effects==(initial.stop&&initial.stop<=initial.budget?initial.stop:(initial.budget<14?initial.budget:14)));
    return 0;
}
int main(void)
{
    fixture f;unsigned i,j;const uint32_t bytes[4]={0,1,128,255};
    for(i=0;i<4;i++){setup(&f,0x1000u,0x2000u,bytes[i]);CHECK(compare_case(f,0x1000u,0x2000u)==0);}
    setup(&f,0xfffffffcu,0x2000u,1);CHECK(compare_case(f,0xfffffffcu,0x2000u)==0);
    setup(&f,0x1000u,0xfffffff0u,0);CHECK(compare_case(f,0x1000u,0xfffffff0u)==0);
    setup(&f,0x1000u,0xff8u,255);CHECK(compare_case(f,0x1000u,0xff8u)==0);
    setup(&f,0,0x2000u,1);CHECK(compare_case(f,0,0x2000u)==0);
    setup(&f,0x1000u,0,1);CHECK(compare_case(f,0x1000u,0)==0);
    setup(&f,0,0,1);CHECK(compare_case(f,0,0)==0);
    for(i=1;i<=14;i++)for(j=ML_HALT;j<=ML_UNKNOWN;j++){
        setup(&f,0x1000u,0x2000u,0);f.stop=i;f.flow=(ml_flow)j;CHECK(compare_case(f,0x1000u,0x2000u)==0);
    }
    for(i=0;i<14;i++){
        setup(&f,0x1000u,0x2000u,0);f.budget=i;CHECK(compare_case(f,0x1000u,0x2000u)==0);
    }
    for(i=1;i<=14;i++){
        setup(&f,0x1000u,0xff8u,0);f.mutate=i;f.mutate_address=i%2?0x1004u:0x1008u;f.mutate_value=0xdeadbeefu;
        CHECK(compare_case(f,0x1000u,0xff8u)==0);
    }
    printf("{\"passed\":true,\"cases\":%u,\"checks\":%u,\"synthetic_only\":true}\n",cases,checks);return 0;
}
