#define _CRT_SECURE_NO_WARNINGS
#include "interrupt_registers.h"
#include "test_io.h"
#include <stdio.h>
#include <stdlib.h>

typedef struct Event { char kind;uint32_t a,b,c,d; } Event;
static Event events[32];
static unsigned length,cursor,groups,cases;
static unsigned long long checks;
static void check(int condition,const char *message)
{
    ++checks;
    if(!condition) {fprintf(stderr,"case%u event%u: %s\n",cases,cursor,message);exit(1);}
}
static void add(char k,uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{
    check(length<32u,"bounded independent effect trace");
    events[length].kind=k;events[length].a=a;events[length].b=b;
    events[length].c=c;events[length].d=d;++length;
}
static Event take(char k,uint32_t a,uint32_t b,uint32_t c,uint32_t d,int reading)
{
    Event e;
    check(cursor<length,"unexpected effect");e=events[cursor++];
    check(e.kind==k,"ordered effect kind");check(e.a==a,"address or A0");
    if(!reading)check(e.b==b,"value or A1");
    check(e.c==c,"A4 or zero metadata");check(e.d==d,"A5 or zero metadata");
    return e;
}
uint32_t tsl9_ir_test_read32(uint32_t a) {return take('R',a,0,0,0,1).b;}
void tsl9_ir_test_write32(uint32_t a,uint32_t v) {(void)take('W',a,v,0,0,0);}
void tsl9_ir_test_write8(uint32_t a,uint8_t v) {(void)take('B',a,v,0,0,0);}
void tsl9_ir_test_csr_clear(uint32_t v) {(void)take('C',0x800u,v,0,0,0);}
void tsl9_ir_test_csr_set(uint32_t v) {(void)take('S',0x800u,v,0,0,0);}
void tsl9_ir_test_rcc_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5) {(void)take('P',a0,a1,a4,a5,0);}
void tsl9_ir_test_init_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5) {(void)take('I',a0,a1,a4,a5,0);}
static void begin_case(void) {++cases;length=cursor=0;}
static void finish_case(void) {check(cursor==length,"missing effects or boundary output");}
typedef uint32_t (*Helper)(uint32_t,uint32_t);
static const Helper helpers[4]={tsl9_rebuild_rcc_registers_19124,tsl9_rebuild_rcc_registers_19142,
    tsl9_rebuild_rcc_registers_19160,tsl9_rebuild_rcc_registers_1917e};
static const uint32_t addresses[4]={0x40021018u,0x4002101cu,0x4002100cu,0x40021010u};
static void helper_case(unsigned index,uint32_t mask,uint32_t enabled,uint32_t before)
{
    const uint32_t expected=enabled?(before|mask):(before&~mask);
    begin_case();add('R',addresses[index],before,0,0);add('W',addresses[index],expected,0,0);
    add('P',expected,enabled,enabled?0x40021000u:before,enabled?before:0x40021000u);
    check(helpers[index](mask,enabled)==expected,"RMW normal A0 return");finish_case();
}
static void helper_grid(void)
{
    static const uint32_t values[]={0u,1u,0xffffffffu,0x80000000u,0x55aa55aau,0xaa55aa55u};
    static const uint32_t masks[]={0u,1u,0x101du,0x02020006u,0x80000000u,0xffffffffu};
    static const uint32_t flags[]={0u,1u,2u,0x80000000u,0xffffffffu};
    unsigned h,v,m,f;++groups;
    for(h=0;h<4;++h)for(v=0;v<6;++v)for(m=0;m<6;++m)for(f=0;f<5;++f)
        helper_case(h,masks[m],flags[f],values[v]);
}
static void helper_bit_basis(void)
{
    unsigned h,m,v,f;++groups;
    for(h=0;h<4;++h)for(m=0;m<32;++m)for(v=0;v<32;++v)for(f=0;f<2;++f)
        helper_case(h,UINT32_C(1)<<m,f,UINT32_C(1)<<v);
}
static void main_case(const uint32_t read_values[6])
{
    /* Original 20 ordered MMIO/CSR effects plus six helper and one init
     * boundary record. Repeated addresses deliberately receive fresh values. */
    static const uint32_t read_addresses[]={0x4002101cu,0x40021018u,0x40021010u,0x40021010u,0x4002100cu,0x4002100cu};
    static const uint32_t masks[]={0x02020006u,0x101du,0x02020006u,0x02020006u,0x101du,0x101du};
    static const unsigned on[]={1,1,1,0,1,0};
    uint32_t last=0;unsigned i;
    begin_case();add('C',0x800u,0x88u,0,0);
    for(i=0;i<6;++i) {
        last=on[i]?(read_values[i]|masks[i]):(read_values[i]&~masks[i]);
        add('R',read_addresses[i],read_values[i],0,0);add('W',read_addresses[i],last,0,0);
        add('P',last,on[i],on[i]?0x40021000u:read_values[i],on[i]?read_values[i]:0x40021000u);
    }
    add('B',0xe000e42du,0,0,0);add('W',0xe000e104u,0x2000u,0,0);
    add('B',0xe000e424u,0x20u,0,0);add('W',0xe000e104u,0x10u,0,0);
    add('B',0xe000e427u,0x30u,0,0);add('W',0xe000e104u,0x80u,0,0);
    add('S',0x800u,0x88u,0,0);add('I',last,0,0x80u,0xe000e000u);
    check(tsl9_rebuild_interrupt_registers_9a42()==last,"initializer normal A0 return");finish_case();
}
static void main_patterns(void)
{
    static const uint32_t patterns[]={0u,0xffffffffu,1u,0x80000000u,0x55aa55aau,0xaa55aa55u,0x101du,0x02020006u};
    uint32_t values[6];unsigned p,i;++groups;
    for(p=0;p<8;++p) {for(i=0;i<6;++i)values[i]=patterns[p];main_case(values);}
    for(p=0;p<8;++p) {for(i=0;i<6;++i)values[i]=patterns[(p+i)%8u];main_case(values);}
}
static void main_live_values(void)
{
    uint32_t values[6],seed=UINT32_C(0x534c3901);unsigned n,i;++groups;
    for(n=0;n<256;++n) {
        for(i=0;i<6;++i) {seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;values[i]=seed;}
        main_case(values);
    }
}
int main(void)
{
    helper_grid();helper_bit_basis();main_patterns();main_live_values();
    printf("{\"passed\":true,\"groups\":%u,\"cases\":%u,\"checks\":%llu}\n",groups,cases,checks);
    return 0;
}
