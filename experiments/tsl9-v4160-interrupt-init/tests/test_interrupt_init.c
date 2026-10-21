#include "interrupt_init.h"
#include "test_io.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct event { char kind; uint32_t address, value; } event;
static event events[64];
static unsigned count, reads, checks, groups;
static uint32_t words[4], csr, samples[6];
static int scripted, mutate_csr;
static void check(int okay, const char *message) {
    ++checks;
    if (!okay) { fprintf(stderr, "FAIL: %s\n", message); exit(1); }
}
static void record(char kind, uint32_t address, uint32_t value) {
    check(count < 64, "bounded synthetic trace");
    events[count].kind=kind; events[count].address=address;
    events[count++].value=value;
}
static unsigned slot(uint32_t address) {
    switch(address) {
    case 0x40021018: return 0;
    case 0x4002101c: return 1;
    case 0x4002100c: return 2;
    case 0x40021010: return 3;
    default: check(0,"only proven RCC read domain"); return 0;
    }
}
uint32_t tsl9_test_read32(uint32_t address) {
    uint32_t value=words[slot(address)];
    if (scripted) { check(reads<6,"six fresh RCC samples"); value=samples[reads]; }
    ++reads; record('R',address,value); return value;
}
void tsl9_test_write32(uint32_t address, uint32_t value) {
    record('W',address,value);
    if(address==0xe000e104) {
        if(mutate_csr && value==0x80) csr ^= 0x80000200u;
    } else words[slot(address)]=value;
}
void tsl9_test_write8(uint32_t address, uint8_t value) {
    check(address==0xe000e42d || address==0xe000e424 || address==0xe000e427,
          "only proven byte-write addresses");
    record('B',address,value);
}
void tsl9_test_csr_clear(uint32_t mask) { record('C',0x800,mask); csr &= ~mask; }
void tsl9_test_csr_set(uint32_t mask) { record('S',0x800,mask); csr |= mask; }
static void reset(uint32_t value) {
    unsigned i;
    count=reads=0; scripted=mutate_csr=0; csr=value;
    for(i=0;i<4;++i) words[i]=value;
    memset(events,0,sizeof events);
}
static void same(unsigned i,char kind,uint32_t address,uint32_t value) {
    check(i<count,"effect exists");
    check(events[i].kind==kind,"effect width/order");
    check(events[i].address==address,"effect exact address");
    check(events[i].value==value,"effect exact value");
}
typedef uint32_t (*helper)(uint32_t,uint32_t);
static void helper_cases(void) {
    static helper functions[]={tsl9_rebuild_rcc_19124,tsl9_rebuild_rcc_19142,
                              tsl9_rebuild_rcc_19160,tsl9_rebuild_rcc_1917e};
    static const uint32_t addresses[]={0x40021018,0x4002101c,0x4002100c,0x40021010};
    static const uint32_t masks[]={0,1,0x02020006,0x101d,0x80000000u,0xffffffffu};
    static const uint32_t values[]={0,0x88,0x55555555,0xaaaaaaaau,0xffffffffu};
    static const uint32_t enabled[]={0,1,2,0x80000000u};
    unsigned f,m,v,e;
    ++groups;
    for(f=0;f<4;++f)for(m=0;m<6;++m)for(v=0;v<5;++v)for(e=0;e<4;++e) {
        uint32_t expected=enabled[e]?(values[v]|masks[m]):(values[v]&~masks[m]);
        uint32_t result;
        reset(values[v]); result=functions[f](masks[m],enabled[e]);
        check(count==2 && reads==1,"one RMW only");
        same(0,'R',addresses[f],values[v]); same(1,'W',addresses[f],expected);
        check(result==expected,"helper A0 result");
        check(csr==values[v],"helper does not alter CSR");
    }
}
static uint32_t expected_init(const uint32_t *v) {
    return v[5]&~UINT32_C(0x101d);
}
static void init_trace(const uint32_t *v) {
    same(0,'C',0x800,0x88);
    same(1,'R',0x4002101c,v[0]); same(2,'W',0x4002101c,v[0]|0x02020006);
    same(3,'R',0x40021018,v[1]); same(4,'W',0x40021018,v[1]|0x101d);
    same(5,'R',0x40021010,v[2]); same(6,'W',0x40021010,v[2]|0x02020006);
    same(7,'R',0x40021010,v[3]); same(8,'W',0x40021010,v[3]&~UINT32_C(0x02020006));
    same(9,'R',0x4002100c,v[4]); same(10,'W',0x4002100c,v[4]|0x101d);
    same(11,'R',0x4002100c,v[5]); same(12,'W',0x4002100c,expected_init(v));
    same(13,'B',0xe000e42d,0); same(14,'W',0xe000e104,0x2000);
    same(15,'B',0xe000e424,0x20); same(16,'W',0xe000e104,0x10);
    same(17,'B',0xe000e427,0x30); same(18,'W',0xe000e104,0x80);
    same(19,'S',0x800,0x88);
    check(count==20 && reads==6,"complete ordered twenty-effect trace");
}
static void fixed_trace(void) {
    uint32_t v[6]={0,0,0,0x02020006,0,0x101d};
    uint32_t result;
    ++groups; reset(0); result=tsl9_rebuild_interrupt_init_9a42();
    init_trace(v); check(result==0,"init returns final RMW A0");
    check(csr==0x88,"unconditionally set bits initially clear");
}
static void fresh_reads(void) {
    static const uint32_t v[]={0x01010101,0x02020202,0x88888888u,0x12345678,
                               0xffffeeeeu,0xabcdef01u};
    unsigned i; uint32_t result;
    ++groups; reset(0x100); scripted=1;
    for(i=0;i<6;++i)samples[i]=v[i];
    result=tsl9_rebuild_interrupt_init_9a42();init_trace(v);
    check(result==expected_init(v),"return uses last fresh MMIO sample");
    check(csr==0x188,"preserve other CSR bits");
}
static void csr_cases(void) {
    static const uint32_t values[]={0,8,0x80,0x88,0xffffffffu,0x80000200u};
    unsigned i; uint32_t result;
    ++groups;
    for(i=0;i<6;++i) {
        reset(values[i]); result=tsl9_rebuild_interrupt_init_9a42();
        check(csr==(values[i]|0x88),"set rather than restore incoming CSR");
        check(result==((values[i]|0x101d)&~UINT32_C(0x101d)),"init return with seeded registers");
        same(0,'C',0x800,0x88); same(19,'S',0x800,0x88);
    }
    reset(0x200);mutate_csr=1;(void)tsl9_rebuild_interrupt_init_9a42();
    check(csr==0x80000088u,"CSR set preserves current unrelated bits");
}
int main(void) {
    helper_cases();fixed_trace();fresh_reads();csr_cases();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);
    return 0;
}
