#include "interrupt_init.h"
#include "test_io.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct effect { char kind; uint32_t address,value; } effect;
static effect trace[32];
static unsigned used,read_count,checks,groups;
static uint32_t inputs[6],csr,environment_delta;
static const uint32_t init_read_addresses[6]={
    0x4002101c,0x40021018,0x40021010,0x40021010,0x4002100c,0x4002100c
};
static void require(int okay,const char *message) {
    ++checks;
    if(!okay) { fprintf(stderr,"REVIEW_FAIL %s\n",message); exit(17); }
}
static void emit(char kind,uint32_t address,uint32_t value) {
    require(used<32,"bounded trace");
    trace[used].kind=kind;trace[used].address=address;trace[used++].value=value;
}
uint32_t tsl9_test_read32(uint32_t address) {
    uint32_t value;
    require(read_count<6,"bounded fresh reads");
    value=inputs[read_count++];emit('r',address,value);return value;
}
void tsl9_test_write32(uint32_t address,uint32_t value) {
    emit('w',address,value);
    if(address==0xe000e104 && value==0x80)csr^=environment_delta;
}
void tsl9_test_write8(uint32_t address,uint8_t value) {emit('b',address,value);}
void tsl9_test_csr_clear(uint32_t mask) {emit('c',0x800,mask);csr&=~mask;}
void tsl9_test_csr_set(uint32_t mask) {emit('s',0x800,mask);csr|=mask;}
uint32_t tsl9_review_csr_snapshot(void) {return csr;}
void tsl9_review_csr_restore(uint32_t value) {emit('t',0x800,value);csr=value;}
static void reset(uint32_t original_csr) {
    used=read_count=0;csr=original_csr;environment_delta=0;
    memset(trace,0,sizeof trace);memset(inputs,0,sizeof inputs);
}
static void effect_is(unsigned index,char kind,uint32_t address,uint32_t value) {
    require(index<used,"effect exists");require(trace[index].kind==kind,"effect width and order");
    require(trace[index].address==address,"effect address");require(trace[index].value==value,"effect value");
}
static void verify_init(uint32_t start_csr,uint32_t delta) {
    uint32_t result=tsl9_rebuild_interrupt_init_9a42();unsigned i;
    require(read_count==6 && used==20,"six fresh reads and twenty effects");
    effect_is(0,'c',0x800,0x88);
    for(i=0;i<6;++i)effect_is(1+2*i,'r',init_read_addresses[i],inputs[i]);
    effect_is(2,'w',0x4002101c,inputs[0]|0x02020006);
    effect_is(4,'w',0x40021018,inputs[1]|0x101d);
    effect_is(6,'w',0x40021010,inputs[2]|0x02020006);
    effect_is(8,'w',0x40021010,inputs[3]&0xfdfdfff9u);
    effect_is(10,'w',0x4002100c,inputs[4]|0x101d);
    effect_is(12,'w',0x4002100c,inputs[5]&0xffffefe2u);
    effect_is(13,'b',0xe000e42d,0);
    effect_is(14,'w',0xe000e104,0x2000);
    effect_is(15,'b',0xe000e424,0x20);
    effect_is(16,'w',0xe000e104,0x10);
    effect_is(17,'b',0xe000e427,0x30);
    effect_is(18,'w',0xe000e104,0x80);
    effect_is(19,'s',0x800,0x88);
    require(result==(inputs[5]&0xffffefe2u),"source A0 result from last fresh word");
    require(csr==(((start_csr&0xffffff77u)^delta)|0x88u),"set current CSR bits rather than restore snapshot");
}
typedef uint32_t (*helper)(uint32_t,uint32_t);
static void helpers(void) {
    static helper functions[]={tsl9_rebuild_rcc_19124,tsl9_rebuild_rcc_19142,tsl9_rebuild_rcc_19160,tsl9_rebuild_rcc_1917e};
    static const uint32_t addresses[]={0x40021018,0x4002101c,0x4002100c,0x40021010};
    static const uint32_t words[]={0,0xffffffffu,0x81234567,0x04088010,0x10203040};
    static const uint32_t masks[]={0,0xffffffffu,0x02020006,0x101d,0x80000001u};
    static const uint32_t enabled[]={0,1,0x100,0xffffffffu};
    unsigned f,v,m,e;++groups;
    for(f=0;f<4;++f)for(v=0;v<5;++v)for(m=0;m<5;++m)for(e=0;e<4;++e){
        uint32_t expected=enabled[e]?words[v]|masks[m]:words[v]&~masks[m];
        uint32_t actual;reset(0x12345678);inputs[0]=words[v];
        actual=functions[f](masks[m],enabled[e]);
        require(used==2 && read_count==1,"helper one fresh RMW");
        effect_is(0,'r',addresses[f],words[v]);effect_is(1,'w',addresses[f],expected);
        require(actual==expected,"helper return word");require(csr==0x12345678,"helper CSR unaffected");
    }
}
static void changing_words(void) {
    static const uint32_t samples[]={0x55555555,0xa5a5a5a5u,0xffffffffu,0x12345678,0x80000000u,0xfedcba98u};
    unsigned i;++groups;reset(0);for(i=0;i<6;++i)inputs[i]=samples[i];verify_init(0,0);
}
static void changing_csr(void) {
    static const uint32_t original[]={0,8,0x80,0x88,0xffffffffu,0x80000200u};
    unsigned i,j;++groups;
    for(i=0;i<6;++i){reset(original[i]);environment_delta=0x80000200u;
        for(j=0;j<6;++j)inputs[j]=0x11223344u*(j+1);
        verify_init(original[i],environment_delta);
    }
}
static void bit_patterns(void) {
    unsigned bit,j;uint32_t seed=0x13579bdf;++groups;
    for(bit=0;bit<256;++bit){uint32_t original=seed;
        reset(original);
        for(j=0;j<6;++j){seed=seed*1664525u+1013904223u;inputs[j]=seed;}
        environment_delta=1u<<(bit%32);verify_init(original,environment_delta);
    }
}
int main(void) {
    helpers();changing_words();changing_csr();bit_patterns();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;
}
