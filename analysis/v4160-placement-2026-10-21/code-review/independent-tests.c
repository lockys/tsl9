#include "interrupt_registers.h"
#include "test_io.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define BASE UINT32_C(0x40021000)
typedef struct event {char kind;uint32_t address,value,a,b;} event;
static event expected[40];
static unsigned count,seen,cases,checks,groups;
static uint32_t samples[6],sample_index,csr;
static void require(int ok,const char *message)
{
    ++checks;if(!ok){fprintf(stderr,"FAIL %s case%u event%u\n",message,cases,seen);exit(1);}
}
static void add(char kind,uint32_t address,uint32_t value,uint32_t a,uint32_t b)
{
    require(count<40u,"bounded synthetic event plan");expected[count].kind=kind;
    expected[count].address=address;expected[count].value=value;expected[count].a=a;expected[count++].b=b;
}
static void effect(char kind,uint32_t address,uint32_t value,uint32_t a,uint32_t b)
{
    event e;require(seen<count,"bounded effects, no unexpected effect");e=expected[seen++];
    require(e.kind==kind,"exact effect width/order");require(e.address==address,"address or A0");
    require(e.value==value,"sample/value or A1");require(e.a==a,"normal A4");require(e.b==b,"normal A5");
}
uint32_t tsl9_ir_test_read32(uint32_t address)
{
    uint32_t v;require(sample_index<6u,"only planned fresh samples");v=samples[sample_index++];
    effect('R',address,v,0,0);return v;
}
void tsl9_ir_test_write32(uint32_t address,uint32_t value)
{
    effect('W',address,value,0,0);
    /* Explicit environment-only CSR drift: no machine GPR mutation. */
    csr^=value&UINT32_C(0x00880000);
}
void tsl9_ir_test_write8(uint32_t address,uint8_t value)
{
    effect('B',address,(uint32_t)value,0,0);
}
void tsl9_ir_test_csr_clear(uint32_t mask)
{
    effect('C',0x800u,mask,0,0);csr&=~mask;
}
void tsl9_ir_test_csr_set(uint32_t mask)
{
    effect('S',0x800u,mask,0,0);csr|=mask;
}
void tsl9_ir_test_rcc_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5)
{
    effect('H',a0,a1,a4,a5);
}
void tsl9_ir_test_init_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5)
{
    effect('I',a0,a1,a4,a5);
}
typedef uint32_t (*helper)(uint32_t,uint32_t);
static const helper helpers[4]={tsl9_rebuild_rcc_registers_19124,tsl9_rebuild_rcc_registers_19142,
    tsl9_rebuild_rcc_registers_19160,tsl9_rebuild_rcc_registers_1917e};
static const uint32_t addresses[4]={BASE+24u,BASE+28u,BASE+12u,BASE+16u};
static uint32_t planned_helper(uint32_t address,uint32_t before,uint32_t mask,uint32_t enabled)
{
    uint32_t after=enabled?(before|mask):(before&~mask);
    add('R',address,before,0,0);add('W',address,after,0,0);
    add('H',after,enabled,enabled?BASE:before,enabled?before:BASE);
    return after;
}
static void one_helper(unsigned which,uint32_t before,uint32_t mask,uint32_t enabled)
{
    uint32_t want,result;++cases;count=seen=sample_index=0;samples[0]=before;
    want=planned_helper(addresses[which],before,mask,enabled);
    result=helpers[which](mask,enabled);
    require(result==want,"returned A0 helper result");require(seen==count&&sample_index==1u,"complete single fresh read");
}
static void main_case(uint32_t seed,uint32_t initial_csr)
{
    static const uint32_t order[6]={BASE+28u,BASE+24u,BASE+16u,BASE+16u,BASE+12u,BASE+12u};
    static const uint32_t masks[6]={0x02020006u,0x101du,0x02020006u,0x02020006u,0x101du,0x101du};
    static const uint32_t enables[6]={1,1,1,0,1,0};
    unsigned i;uint32_t want=0,expected_csr=initial_csr&~UINT32_C(0x88),result;
    ++cases;count=seen=sample_index=0;csr=initial_csr;add('C',0x800u,0x88u,0,0);
    for(i=0;i<6u;++i){
        samples[i]=seed^(UINT32_C(0x9e3779b9)*(i+1u))^(i&1u?UINT32_MAX:0u);
        want=planned_helper(order[i],samples[i],masks[i],enables[i]);
        expected_csr^=want&UINT32_C(0x00880000);
    }
    add('B',0xe000e42du,0,0,0);add('W',0xe000e104u,0x2000u,0,0);
    add('B',0xe000e424u,0x20u,0,0);add('W',0xe000e104u,0x10u,0,0);
    add('B',0xe000e427u,0x30u,0,0);add('W',0xe000e104u,0x80u,0,0);
    add('S',0x800u,0x88u,0,0);add('I',want,0,0x80u,0xe000e000u);
    result=tsl9_rebuild_interrupt_registers_9a42();
    require(result==want,"main A0 last independent clear sample");
    require(csr==(expected_csr|0x88u),"CSR set uses current state after environment drift");
    require(seen==count&&sample_index==6u,"complete20 effects and7 output observations");
}
int main(void)
{
    static const uint32_t words[]={0,UINT32_MAX,0x80000000u,0x7fffffffu,0xaaaaaaaau,0x55555555u,
        0x101du,0x02020006u,0x12345678u,0xdeadbeefu,0x89abcdefu};
    static const uint32_t masks[]={0,UINT32_MAX,1,0x80000000u,0x101du,0x02020006u,0xaaaaaaaau,0x55555555u,0x7fffffffu};
    static const uint32_t enabled[]={0,1,2,3,0x80000000u,UINT32_MAX,0x100u,0x7fffffffu};
    unsigned h,w,m,e,i;
    ++groups;
    for(h=0;h<4u;++h)for(w=0;w<11u;++w)for(m=0;m<9u;++m)for(e=0;e<8u;++e)
        one_helper(h,words[w],masks[m],enabled[e]);
    ++groups;for(i=0;i<256u;++i)main_case(i*UINT32_C(0x01010101),i*UINT32_C(0x10203041));
    ++groups;
    for(h=0;h<4u;++h)for(i=0;i<32u;++i)for(e=0;e<3u;++e)
        one_helper(h,~(UINT32_C(1)<<i),UINT32_C(1)<<i,enabled[e]);
    ++groups;for(i=0;i<12u;++i)main_case(UINT32_MAX-i*UINT32_C(0x10001001),i&1u?UINT32_MAX:0);
    printf("{\"passed\":true,\"groups\":%u,\"cases\":%u,\"checks\":%u}\n",groups,cases,checks);
    return 0;
}
