#include "memory_leaves.h"
#include <stdio.h>
#include <string.h>
#define GUARD UINT32_C(0x4002420c)
typedef struct cell {uint32_t address,value;} cell;
typedef struct event {uint32_t kind,address,value;} event;
typedef struct mock {
    cell cells[256];uint32_t cells_n;
    event events[256];uint32_t events_n;
    uint32_t stop_at;ml_flow stop_flow;
    uint32_t mutate_address,mutate_value,mutate_enabled;
    uint32_t change_guard_on_read;
} mock;
static uint32_t cases,checks;
#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"check failed line %d\n",__LINE__);return 0;}}while(0)
static uint32_t get8(mock *m,uint32_t a){uint32_t i;for(i=0;i<m->cells_n;++i)if(m->cells[i].address==a)return m->cells[i].value;return 0;}
static void put8(mock *m,uint32_t a,uint32_t v){uint32_t i;for(i=0;i<m->cells_n;++i)if(m->cells[i].address==a){m->cells[i].value=v&255u;return;}if(m->cells_n<256){m->cells[m->cells_n].address=a;m->cells[m->cells_n++].value=v&255u;}}
static uint32_t get32(mock *m,uint32_t a){return get8(m,a)|(get8(m,a+1u)<<8)|(get8(m,a+2u)<<16)|(get8(m,a+3u)<<24);}
static void put32(mock *m,uint32_t a,uint32_t v){uint32_t i;for(i=0;i<4;++i)put8(m,a+i,v>>(8*i));}
static ml_flow record(mock *m,uint32_t kind,uint32_t address,uint32_t value)
{
    uint32_t n=m->events_n;if(n>=256)return ML_UNKNOWN;
    m->events[n].kind=kind;m->events[n].address=address;m->events[n].value=value;m->events_n=n+1;
    return m->stop_at && m->events_n==m->stop_at?m->stop_flow:ML_CONTINUE;
}
static ml_flow read8(void *u,uint32_t a,uint32_t *v)
{
    mock *m=(mock *)u;ml_flow f;*v=get8(m,a);f=record(m,1,a,*v);if(f!=ML_CONTINUE)return f;
    if(m->mutate_enabled){put8(m,m->mutate_address,m->mutate_value);m->mutate_enabled=0;}
    if(m->change_guard_on_read)put32(m,GUARD,UINT32_C(0xdeadbeef));return ML_CONTINUE;
}
static ml_flow read32(void *u,uint32_t a,uint32_t *v){mock *m=(mock *)u;*v=get32(m,a);return record(m,3,a,*v);}
static ml_flow write8(void *u,uint32_t a,uint32_t v){mock *m=(mock *)u;ml_flow f=record(m,2,a,v);if(f==ML_CONTINUE)put8(m,a,v);return f;}
static ml_flow write32(void *u,uint32_t a,uint32_t v){mock *m=(mock *)u;ml_flow f=record(m,4,a,v);if(f==ML_CONTINUE)put32(m,a,v);return f;}
static ml_flow fence_i(void *u){return record((mock *)u,5,0,0);}
static void start(mock *m,ml_io *io)
{
    ++cases;memset(m,0,sizeof(*m));memset(io,0,sizeof(*io));put32(m,GUARD,UINT32_C(0x1234abcd));io->user=m;
    io->read8=read8;io->read32=read32;io->write8=write8;io->write32=write32;io->fence_i=fence_i;io->diagnostic_budget=256;
}
static int guard_events(mock *m)
{
    CHECK(m->events_n>=4);CHECK(m->events[0].kind==3 && m->events[0].address==GUARD && m->events[0].value==UINT32_C(0x1234abcd));
    CHECK(m->events[1].kind==4 && m->events[1].address==GUARD && m->events[1].value==0);CHECK(m->events[2].kind==5);
    CHECK(m->events[m->events_n-1].kind==4 && m->events[m->events_n-1].address==GUARD && m->events[m->events_n-1].value==UINT32_C(0x1234abcd));
    CHECK(get32(m,GUARD)==UINT32_C(0x1234abcd));return 1;
}
static int suite(void)
{
    mock m;ml_io io;ml_result out;uint32_t i,j;
    /* Full expected word, zero/null rules, fresh reads and early mismatch. */
    start(&m,&io);put8(&m,100,255);out=tsl9_candidate_compare_200004bc(&io,100,UINT32_C(0x1ff),1);CHECK(out.known && out.value==0);CHECK(m.events_n==5);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_compare_200004bc(&io,0,0,4);CHECK(out.known && !out.value);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_compare_200004bc(&io,100,0,0);CHECK(out.known && !out.value);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,7);put8(&m,101,8);put8(&m,102,7);out=tsl9_candidate_compare_200004bc(&io,100,7,3);CHECK(out.known && !out.value);CHECK(m.events_n==6 && m.events[3].address==100 && m.events[4].address==101);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,9);m.mutate_enabled=1;m.mutate_address=101;m.mutate_value=9;out=tsl9_candidate_compare_200004bc(&io,100,9,2);CHECK(out.known && out.value==1);CHECK(m.events[4].value==9);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,UINT32_MAX,3);put8(&m,0,3);out=tsl9_candidate_compare_200004bc(&io,UINT32_MAX,3,2);CHECK(out.known && out.value==1);CHECK(m.events[3].address==UINT32_MAX && m.events[4].address==0);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_compare_200004bc(&io,GUARD,0,4);CHECK(out.known && out.value==1);for(i=3;i<7;++i)CHECK(m.events[i].value==0);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,2);m.change_guard_on_read=1;out=tsl9_candidate_compare_200004bc(&io,100,2,1);CHECK(out.known && out.value==1);CHECK(guard_events(&m));
    /* Byte truncation and end-pointer result, including wrap and MMIO alias. */
    start(&m,&io);out=tsl9_candidate_fill_2000039c(&io,100,UINT32_C(0x1ff),3);CHECK(out.known && out.value==103);for(i=0;i<3;++i)CHECK(get8(&m,100+i)==255);CHECK(m.events_n==7);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_fill_2000039c(&io,0,7,3);CHECK(out.known && out.value==0);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_fill_2000039c(&io,100,7,0);CHECK(out.known && out.value==100);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_fill_2000039c(&io,UINT32_MAX,UINT32_C(0x123),2);CHECK(out.known && out.value==1);CHECK(get8(&m,UINT32_MAX)==35 && get8(&m,0)==35);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_fill_2000039c(&io,GUARD,127,1);CHECK(out.known && out.value==GUARD+1u);CHECK(m.events[3].kind==2 && m.events[3].value==127);CHECK(guard_events(&m));
    /* Forward interleaving, not memcpy/memmove snapshots. */
    start(&m,&io);put8(&m,100,1);put8(&m,101,2);put8(&m,102,3);put8(&m,103,4);out=tsl9_candidate_copy_20000332(&io,101,100,3);CHECK(out.known && out.value==101);for(i=100;i<104;++i)CHECK(get8(&m,i)==1);for(i=0;i<3;++i){CHECK(m.events[3+2*i].kind==1 && m.events[3+2*i].address==100+i);CHECK(m.events[4+2*i].kind==2 && m.events[4+2*i].address==101+i);}CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,4);put8(&m,101,5);out=tsl9_candidate_copy_20000332(&io,100,100,2);CHECK(out.known && out.value==100);CHECK(get8(&m,100)==4 && get8(&m,101)==5);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_copy_20000332(&io,0,100,2);CHECK(out.known && !out.value);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_copy_20000332(&io,100,0,2);CHECK(out.known && out.value==100);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);out=tsl9_candidate_copy_20000332(&io,100,200,0);CHECK(out.known && out.value==100);CHECK(m.events_n==4);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,UINT32_MAX,8);put8(&m,0,9);out=tsl9_candidate_copy_20000332(&io,100,UINT32_MAX,2);CHECK(out.known && out.value==100);CHECK(get8(&m,100)==8 && get8(&m,101)==9);CHECK(m.events[5].address==0);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,8);put8(&m,101,9);out=tsl9_candidate_copy_20000332(&io,UINT32_MAX,100,2);CHECK(out.known && out.value==UINT32_MAX);CHECK(get8(&m,UINT32_MAX)==8 && get8(&m,0)==9);CHECK(guard_events(&m));
    start(&m,&io);put8(&m,100,77);out=tsl9_candidate_copy_20000332(&io,GUARD+1u,100,1);CHECK(out.known && out.value==GUARD+1u);CHECK(m.events[4].kind==2 && m.events[4].value==77);CHECK(guard_events(&m));
    /* Bounded HOST stops preserve the effect prefix, without fake restore. */
    for(j=ML_HALT;j<=ML_UNKNOWN;++j){start(&m,&io);m.stop_at=4;m.stop_flow=(ml_flow)j;out=tsl9_candidate_compare_200004bc(&io,100,0,1);CHECK(!out.known && out.flow==(ml_flow)j);CHECK(m.events_n==4 && m.events[3].kind==1);CHECK(get32(&m,GUARD)==0);}
    start(&m,&io);io.diagnostic_budget=3;out=tsl9_candidate_fill_2000039c(&io,100,7,1);CHECK(!out.known && out.flow==ML_UNKNOWN);CHECK(m.events_n==3 && get32(&m,GUARD)==0);
    start(&m,&io);io.read8=0;out=tsl9_candidate_copy_20000332(&io,100,200,1);CHECK(!out.known && out.flow==ML_UNKNOWN);CHECK(m.events_n==3 && get32(&m,GUARD)==0);
    start(&m,&io);m.stop_at=2;m.stop_flow=ML_TRANSFER;out=tsl9_candidate_fill_2000039c(&io,100,0,1);CHECK(!out.known && out.flow==ML_TRANSFER);CHECK(m.events_n==2 && get32(&m,GUARD)==UINT32_C(0x1234abcd));
    return 1;
}
int main(void){if(!suite())return 1;printf("{\"groups\":4,\"cases\":%u,\"checks\":%u}\n",(unsigned)cases,(unsigned)checks);return 0;}
