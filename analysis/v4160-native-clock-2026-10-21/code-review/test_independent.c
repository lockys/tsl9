#include "native_clock.h"
#include "test_io.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct event {char kind;uint32_t address,value;} event;
static event expected[32];
static unsigned planned,observed,groups,checks,cases;
static void require(int okay,const char *why) {
    ++checks;if(!okay){fprintf(stderr,"REVIEW_FAIL %s\n",why);exit(17);}
}
static void queue(char kind,uint32_t address,uint32_t value) {
    require(planned<32,"bounded planned events");
    expected[planned].kind=kind;expected[planned].address=address;
    expected[planned++].value=value;
}
static uint32_t consume(char kind,uint32_t address,uint32_t value,int writes) {
    event *e;require(observed<planned,"no extra primitive");e=&expected[observed++];
    require(e->kind==kind,"primitive width and order");
    require(e->address==address,"current exact address");
    if(writes)require(e->value==value,"source arithmetic write value");
    return e->value;
}
uint32_t tsl9_nc_test_gp(void){return consume('g',0,0,0);}
uint32_t tsl9_nc_test_read32(uint32_t address){return consume('r',address,0,0);}
uint8_t tsl9_nc_test_read8(uint32_t address){return (uint8_t)consume('b',address,0,0);}
void tsl9_nc_test_write32(uint32_t address,uint32_t value){(void)consume('w',address,value,1);}
void tsl9_nc_test_write8(uint32_t address,uint8_t value){(void)consume('c',address,value,1);}
void tsl9_nc_test_write16(uint32_t address,uint16_t value){(void)consume('h',address,value,1);}
static void reset(void){planned=observed=0;++cases;}
static void finish(void){require(observed==planned,"all expected primitives happened");}

/* Addresses and event order follow source 18838/18882/18884/1889E/
 * 188B4/188CE/18850/18858/1885A/18864/18868/1886C/18872. */
static void query_case(uint32_t selector,uint32_t multiplier_sample,uint32_t source_sample,
                       uint32_t special,uint32_t external,uint32_t fallback,
                       uint32_t prescaler,uint8_t shift,uint32_t live_word,
                       const uint32_t gp[4]) {
    uint32_t provisional,field,multiplier,base,index;
    reset();queue('r',0x40021004,selector);field=selector&12u;
    if(field==4)provisional=32000000u;
    else if(field!=8)provisional=8000000u;
    else {
        queue('r',0x40021004,multiplier_sample);
        queue('r',0x40021004,source_sample);
        multiplier=((multiplier_sample>>18)&15u)+2u;
        if(multiplier==17)multiplier=18;
        if(!(source_sample&0x10000u)) {
            queue('r',0x40023800,special);base=(special&16u)?8000000u:4000000u;
        } else {
            queue('r',0x40021004,external);
            if((external&0xc00000u)==0xc00000u)base=16000000u;
            else {queue('r',0x40021004,fallback);base=(fallback&0x20000u)?4000000u:8000000u;}
        }
        provisional=multiplier*base;
    }
    queue('g',0,gp[0]);queue('w',gp[0]+108u,provisional);
    queue('r',0x40021004,prescaler);index=(prescaler>>4)&15u;
    queue('g',0,gp[1]);queue('b',gp[1]+64u+index,shift);
    queue('g',0,gp[2]);queue('r',gp[2]+108u,live_word);
    queue('g',0,gp[3]);queue('w',gp[3]+108u,live_word>>(shift&31u));
    tsl9_rebuild_clock_query_18834();finish();
}
static void selectors(void) {
    static const uint32_t gp[]={0x1000,0x2000,0x3000,0x4000};
    static const uint32_t select[]={0,4,12,0xffffffffu,0x80000004u,0x55555550};
    unsigned i;++groups;
    for(i=0;i<6;++i)query_case(select[i],0,0,0,0,0,0x70,3,0xf1234567u,gp);
}
static void multiplier_branches(void) {
    static const uint32_t gp[]={0xfffffff0u,0xffffffc0u,0xffffff94u,0x80000000u};
    unsigned m,s,e;++groups;
    for(m=0;m<16;++m)for(s=0;s<2;++s) {
        query_case(8,(m<<18)|0x123u,0,s?16u:0u,0,0,0x91,35,0xf0f0ffffu,gp);
        for(e=0;e<4;++e)
            query_case(8,(m<<18)|0x444u,0x10000,0,
                       e==0?0xc00000u:e==1?0x400000u:e==2?0x800000u:0u,
                       s?0x80020000u:0x80000000u,0xa5,1,0xabcdef12u,gp);
    }
}
static void live_shift_and_fresh_scalar(void) {
    static const uint32_t gp[]={0x20004000,0x20005000,0x20006000,0x20007000};
    unsigned index,byte;++groups;
    for(index=0;index<16;++index)for(byte=0;byte<256;++byte)
        query_case(4,0,0,0,0,0,index<<4,(uint8_t)byte,0x87654321u^(index*0x10203u),gp);
}
static void derive(uint32_t scalar,const uint32_t gp[3]) {
    uint32_t quotient=(scalar/8000000u)&255u;
    reset();queue('g',0,gp[0]);queue('r',gp[0]+108u,scalar);
    queue('g',0,gp[1]);queue('c',gp[1]+382u,quotient);
    queue('g',0,gp[2]);queue('h',gp[2]+380u,(quotient*1000u)&65535u);
    tsl9_rebuild_clock_fields_1973c();finish();
}
static void unsigned_derived_fields(void) {
    static const uint32_t gp[]={0xffffff94u,0xfffffe82u,0x20004000};
    static const uint32_t edges[]={0,7999999,8000000,8000001,2040000000u,
                                 2048000000u,2056000000u,0x80000000u,0xffffffffu};
    unsigned i,q;++groups;
    for(i=0;i<9;++i)derive(edges[i],gp);
    for(q=0;q<=536;++q) {
        uint32_t scalar=q*8000000u;derive(scalar,gp);
        if(scalar<0xffffffffu)derive(scalar+1,gp);
    }
}
int main(void) {
    selectors();multiplier_branches();live_shift_and_fresh_scalar();unsigned_derived_fields();
    printf("{\"passed\":true,\"groups\":%u,\"cases\":%u,\"checks\":%u}\n",groups,cases,checks);
    return 0;
}
