#include "memory_leaves.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define G UINT32_C(0x4002420c)
#define SAVED UINT32_C(0xaabbccdd)
typedef struct cell { uint32_t address,value; } cell;
typedef struct event { unsigned kind,width;uint32_t address,value; } event;
typedef struct fixture {
    cell cells[512];unsigned used,n,expected_n;
    event actual[256],expected[256];
    unsigned stop_at,edit_at;ml_flow stop;
    uint32_t edit_address,edit_value;
} fixture;
static unsigned checks,cases;
#define CHECK(c) do { ++checks;if(!(c)){fprintf(stderr,"independent memory check failed at %d: %s\n",__LINE__,#c);exit(1);} } while(0)
static uint32_t get(fixture *f,uint32_t a)
{ unsigned i;for(i=0;i<f->used;i++)if(f->cells[i].address==a)return f->cells[i].value;return 0; }
static void put(fixture *f,uint32_t a,uint32_t v)
{ unsigned i;for(i=0;i<f->used;i++)if(f->cells[i].address==a){f->cells[i].value=v&255u;return;}CHECK(f->used<512);f->cells[f->used].address=a;f->cells[f->used++].value=v&255u; }
static uint32_t word(fixture *f,uint32_t a)
{ return get(f,a)|(get(f,a+1u)<<8)|(get(f,a+2u)<<16)|(get(f,a+3u)<<24); }
static void putword(fixture *f,uint32_t a,uint32_t v)
{ unsigned i;for(i=0;i<4;i++)put(f,a+i,v>>(i*8)); }
static ml_flow record(fixture *f,unsigned k,unsigned w,uint32_t a,uint32_t v)
{ event *e;CHECK(f->n<256);e=&f->actual[f->n++];e->kind=k;e->width=w;e->address=a;e->value=v;
  if(f->edit_at==f->n)put(f,f->edit_address,f->edit_value);
  return f->stop_at==f->n?f->stop:ML_CONTINUE; }
static ml_flow r8(void *u,uint32_t a,uint32_t *v)
{ fixture *f=(fixture*)u;*v=get(f,a);return record(f,1,8,a,*v); }
static ml_flow r32(void *u,uint32_t a,uint32_t *v)
{ fixture *f=(fixture*)u;*v=word(f,a);return record(f,1,32,a,*v); }
static ml_flow w8(void *u,uint32_t a,uint32_t v)
{ fixture *f=(fixture*)u;ml_flow s=record(f,2,8,a,v);if(s==ML_CONTINUE)put(f,a,v);return s; }
static ml_flow w32(void *u,uint32_t a,uint32_t v)
{ fixture *f=(fixture*)u;ml_flow s=record(f,2,32,a,v);if(s==ML_CONTINUE)putword(f,a,v);return s; }
static ml_flow fence(void *u){return record((fixture*)u,3,0,0,0);}
static void expected(fixture *f,unsigned k,unsigned w,uint32_t a,uint32_t v)
{ event *e=&f->expected[f->expected_n++];e->kind=k;e->width=w;e->address=a;e->value=v; }
static void prefix(fixture *f)
{ expected(f,1,32,G,SAVED);expected(f,2,32,G,0);expected(f,3,0,0,0); }
static void restore(fixture *f){expected(f,2,32,G,SAVED);}
static void reset(fixture *f,ml_io *io)
{ memset(f,0,sizeof(*f));memset(io,0,sizeof(*io));putword(f,G,SAVED);io->user=f;io->read8=r8;io->read32=r32;io->write8=w8;io->write32=w32;io->fence_i=fence;io->diagnostic_budget=128; }
static void trace(fixture *f,ml_result r,ml_flow flow,uint32_t known,uint32_t value)
{ unsigned i;CHECK(r.flow==flow);CHECK(r.known==known);if(known)CHECK(r.value==value);CHECK(f->n==f->expected_n);
  for(i=0;i<f->n;i++){CHECK(f->actual[i].kind==f->expected[i].kind);CHECK(f->actual[i].width==f->expected[i].width);CHECK(f->actual[i].address==f->expected[i].address);CHECK(f->actual[i].value==f->expected[i].value);} }
int main(void)
{
    fixture f;ml_io io;ml_result r;unsigned i,j;uint32_t a;
    /* 1: null compare still guards, then returns false. */
    reset(&f,&io);prefix(&f);restore(&f);r=tsl9_candidate_compare_200004bc(&io,0,0,7);trace(&f,r,ML_CONTINUE,1,0);cases++;
    /* 2: zero count is false, not a vacuous equality. */
    reset(&f,&io);prefix(&f);restore(&f);r=tsl9_candidate_compare_200004bc(&io,100,7,0);trace(&f,r,ML_CONTINUE,1,0);cases++;
    /* 3: all matching loads are fresh and ordered. */
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++){put(&f,100+i,7);expected(&f,1,8,100+i,7);}restore(&f);r=tsl9_candidate_compare_200004bc(&io,100,7,3);trace(&f,r,ML_CONTINUE,1,1);cases++;
    /* 4: full A1, never a low-byte reinterpretation. */
    reset(&f,&io);put(&f,100,255);prefix(&f);expected(&f,1,8,100,255);restore(&f);r=tsl9_candidate_compare_200004bc(&io,100,511,1);trace(&f,r,ML_CONTINUE,1,0);cases++;
    /* 5: mismatch stops before a later source read. */
    reset(&f,&io);put(&f,100,7);put(&f,101,8);prefix(&f);expected(&f,1,8,100,7);expected(&f,1,8,101,8);restore(&f);r=tsl9_candidate_compare_200004bc(&io,100,7,3);trace(&f,r,ML_CONTINUE,1,0);cases++;
    /* 6: source aliases the MMIO guard: read the newly zeroed byte. */
    reset(&f,&io);prefix(&f);expected(&f,1,8,G,0);restore(&f);r=tsl9_candidate_compare_200004bc(&io,G,0,1);trace(&f,r,ML_CONTINUE,1,1);CHECK(word(&f,G)==SAVED);cases++;
    /* 7: provider edits the next byte after the first source read. */
    reset(&f,&io);put(&f,100,7);put(&f,101,7);f.edit_at=4;f.edit_address=101;f.edit_value=9;prefix(&f);expected(&f,1,8,100,7);expected(&f,1,8,101,9);restore(&f);r=tsl9_candidate_compare_200004bc(&io,100,7,2);trace(&f,r,ML_CONTINUE,1,0);cases++;
    /* 8: fill truncates bytes and returns the advanced destination. */
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++)expected(&f,2,8,100+i,0xab);restore(&f);r=tsl9_candidate_fill_2000039c(&io,100,0x12ab,3);trace(&f,r,ML_CONTINUE,1,103);CHECK(get(&f,102)==0xab);cases++;
    /* 9: destination arithmetic wraps without a mid-loop null guard. */
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++)expected(&f,2,8,UINT32_C(0xfffffffe)+i,6);restore(&f);r=tsl9_candidate_fill_2000039c(&io,UINT32_C(0xfffffffe),6,3);trace(&f,r,ML_CONTINUE,1,1);CHECK(get(&f,0)==6);cases++;
    /* 10: writes into the guard are visible, then restored; early exits too. */
    reset(&f,&io);prefix(&f);expected(&f,2,8,G,0x55);restore(&f);r=tsl9_candidate_fill_2000039c(&io,G,0x55,1);trace(&f,r,ML_CONTINUE,1,G+1u);CHECK(word(&f,G)==SAVED);
    for(j=0;j<2;j++){reset(&f,&io);prefix(&f);restore(&f);a=j?100u:0u;r=tsl9_candidate_fill_2000039c(&io,a,7,j?0u:4u);trace(&f,r,ML_CONTINUE,1,a);}cases++;
    /* 11: copy interleaves each read/write, returns original destination. */
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++){put(&f,100+i,10+i);expected(&f,1,8,100+i,10+i);expected(&f,2,8,200+i,10+i);}restore(&f);r=tsl9_candidate_copy_20000332(&io,200,100,3);trace(&f,r,ML_CONTINUE,1,200);CHECK(get(&f,202)==12);cases++;
    /* 12: forward overlap deliberately feeds back overwritten bytes. */
    reset(&f,&io);prefix(&f);for(i=0;i<5;i++)put(&f,100+i,i+1);for(i=0;i<4;i++){expected(&f,1,8,100+i,1);expected(&f,2,8,101+i,1);}restore(&f);r=tsl9_candidate_copy_20000332(&io,101,100,4);trace(&f,r,ML_CONTINUE,1,101);CHECK(get(&f,104)==1);cases++;
    /* 13: copy source zero comes from the preceding guard write. */
    reset(&f,&io);prefix(&f);expected(&f,1,8,G,0);expected(&f,2,8,200,0);restore(&f);r=tsl9_candidate_copy_20000332(&io,200,G,1);trace(&f,r,ML_CONTINUE,1,200);CHECK(word(&f,G)==SAVED);cases++;
    /* 14: copy null/zero paths all preserve guard sequence and destination. */
    for(j=0;j<3;j++){reset(&f,&io);prefix(&f);restore(&f);a=j==0?0u:200u;r=tsl9_candidate_copy_20000332(&io,a,j==1?0u:100u,j==2?0u:3u);trace(&f,r,ML_CONTINUE,1,a);}cases++;
    /* 15: both read and write address domains include modular zero. */
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++){put(&f,UINT32_C(0xfffffffe)+i,4);expected(&f,1,8,UINT32_C(0xfffffffe)+i,4);}restore(&f);r=tsl9_candidate_compare_200004bc(&io,UINT32_C(0xfffffffe),4,3);trace(&f,r,ML_CONTINUE,1,1);
    reset(&f,&io);prefix(&f);for(i=0;i<3;i++){put(&f,100+i,10+i);expected(&f,1,8,100+i,10+i);expected(&f,2,8,UINT32_C(0xfffffffe)+i,10+i);}restore(&f);r=tsl9_candidate_copy_20000332(&io,UINT32_C(0xfffffffe),100,3);trace(&f,r,ML_CONTINUE,1,UINT32_C(0xfffffffe));cases++;
    /* 16: stops retain only observed prefixes, never fabricated cleanup. */
    for(j=1;j<=3;j++){reset(&f,&io);put(&f,100,7);f.stop_at=4;f.stop=(ml_flow)j;prefix(&f);expected(&f,1,8,100,7);r=tsl9_candidate_compare_200004bc(&io,100,7,2);trace(&f,r,(ml_flow)j,0,0);CHECK(word(&f,G)==0);}
    reset(&f,&io);f.stop_at=3;f.stop=ML_HALT;prefix(&f);r=tsl9_candidate_fill_2000039c(&io,100,7,1);trace(&f,r,ML_HALT,0,0);CHECK(word(&f,G)==0);
    reset(&f,&io);io.diagnostic_budget=3;prefix(&f);r=tsl9_candidate_copy_20000332(&io,200,100,1);trace(&f,r,ML_UNKNOWN,0,0);CHECK(word(&f,G)==0);cases++;
    printf("{\"narrative_cases\":%u,\"assertions\":%u,\"synthetic_HOST_only\":true,\"physical_ABI_proof\":false}\n",cases,checks);return 0;
}
