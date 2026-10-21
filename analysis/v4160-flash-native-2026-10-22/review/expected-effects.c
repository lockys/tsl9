#include "flash_native.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { fn_request request;fn_word answer; } event;
typedef struct {
 event events[1024];unsigned count,index,ctrl_reads,busy,partial;
 uint32_t destination,source,selected_source;fn_word final_ctrl;
} fixture;
static unsigned checks,cases;
#define CHECK(x) do { ++checks;if(!(x)){fprintf(stderr,"REVIEW_FAIL line%u case%u event%u: %s\n",(unsigned)__LINE__,cases,f->index,#x);exit(1);} } while(0)
static fn_word full(uint32_t value) { fn_word x={value,UINT32_MAX};return x; }
static void add(fixture *f,fn_kind kind,uint32_t site,uint32_t address,fn_word value,fn_word answer) {
 event *e;CHECK(f->count<1024u);e=&f->events[f->count++];
 e->request.kind=kind;e->request.site=site;e->request.address=address;
 e->request.value=value.value;e->request.known=value.known;e->request.width=32u;e->answer=answer;
}
static void wr(fixture *f,uint32_t site,uint32_t address,fn_word value) { fn_word z={0u,0u};add(f,FN_WRITE32_REQUEST,site,address,value,z); }
static void rd(fixture *f,uint32_t site,uint32_t address,fn_word answer) { fn_word z={0u,0u};add(f,FN_READ32_REQUEST,site,address,z,answer); }
static fn_word control(fixture *f,uint32_t site) {
 fn_word x={0xa5000073u^(++f->ctrl_reads*0x103u),f->partial?0u:UINT32_MAX};
 rd(f,site,0x40022010u,x);f->final_ctrl=x;return x;
}
static fn_word set(fn_word v,uint32_t mask) { v.value|=mask;v.known|=mask;return v; }
static fn_word clear(fn_word v,uint32_t mask) { v.value&=~mask;v.known|=mask;return v; }
static void poll(fixture *f,uint32_t site,uint32_t mask) {
 fn_word x={mask,mask};if(f->busy)rd(f,site,0x4002200cu,x);
 x.value=0u;rd(f,site,0x4002200cu,x);
}
static void unlock(fixture *f) {
 wr(f,0x18ea8u,0x40022004u,full(0x45670123u));wr(f,0x18eaeu,0x40022004u,full(0xcdef89abu));
 wr(f,0x18eb0u,0x40022024u,full(0x45670123u));wr(f,0x18eb2u,0x40022024u,full(0xcdef89abu));
}
static fn_word lock(fixture *f) { fn_word x=set(control(f,0x18ebau),0x8000u);wr(f,0x18ec0u,0x40022010u,x);return x; }
static fn_word erase(fixture *f) {
 fn_word x=set(control(f,0x18ec8u),0x20000u);wr(f,0x18ed4u,0x40022010u,x);
 wr(f,0x18ed6u,0x40022014u,full(f->destination&0xffffff00u));
 x=set(control(f,0x18ed8u),64u);wr(f,0x18edeu,0x40022010u,x);poll(f,0x18ee0u,1u);
 x=clear(control(f,0x18ee6u),0x20000u);wr(f,0x18eeeu,0x40022010u,x);return x;
}
static fn_word program(fixture *f) {
 unsigned i;fn_word x=set(control(f,0x18ef6u),0x10000u);wr(f,0x18f00u,0x40022010u,x);
 poll(f,0x18f02u,1u);poll(f,0x18f0cu,2u);
 for(i=0;i<64u;i++) {
  uint32_t value=0x10203040u+i;
  if(f->busy&&i==1u)value=0xdeadbeefu;
  rd(f,0x18f1eu,f->selected_source+4u*i,full(value));
  wr(f,0x18f26u,(f->destination&0xffffff00u)+4u*i,full(value));poll(f,0x18f2au,2u);
 }
 x=set(control(f,0x18f36u),0x200000u);wr(f,0x18f3eu,0x40022010u,x);poll(f,0x18f44u,1u);
 x=clear(control(f,0x18f4au),0x10000u);wr(f,0x18f52u,0x40022010u,x);return x;
}
static fn_flow provider(void *p,fn_host *h,const fn_request *q,fn_word *answer) {
 fixture *f=(fixture *)p;event *e;(void)h;CHECK(f->index<f->count);e=&f->events[f->index++];
 CHECK(q->kind==e->request.kind);CHECK(q->site==e->request.site);CHECK(q->address==e->request.address);
 CHECK(q->value==e->request.value);CHECK(q->known==e->request.known);CHECK(q->width==32u);
 *answer=e->answer;return FN_RETURNED;
}
static void same(fixture *f,fn_word a,fn_word b) { CHECK(a.value==b.value);CHECK(a.known==b.known); }
static void one(uint32_t entry,unsigned mode) {
 fixture store,*f=&store;fn_host h;fn_word expected[32],value,final;unsigned i;uint32_t sp=0x20008000u;
 memset(f,0,sizeof(*f));++cases;f->busy=mode;f->partial=mode;f->destination=mode?0xffffffafu:0x080010a5u;
 f->source=mode?0xfffffff0u:0x20005000u;f->selected_source=f->source;
 fn_host_init(&h,provider,f);h.poll_budget=3u;
 for(i=0;i<32u;i++)h.regs[i]=expected[i]=full(0x90000000u+i);
 h.regs[1]=expected[1]=full(0x12345678u);h.regs[2]=expected[2]=full(sp);
 expected[10]=full(f->destination);expected[11]=full(f->source);
 if(entry==0x9c0au) {
  fn_word z={0u,0u};wr(f,0x9c0cu,sp-8u,expected[8]);wr(f,0x9c0eu,sp-12u,expected[9]);
  wr(f,0x9c10u,sp-4u,expected[1]);wr(f,0x9c14u,sp-20u,full(f->source));
  add(f,FN_CSR_CLEAR_REQUEST,0x9c1au,0x800u,full(136u),z);unlock(f);wr(f,0x18e94u,0x4002200cu,full(49u));
  (void)erase(f);if(mode)f->selected_source=f->source+0x1000u;
  rd(f,0x9c30u,sp-20u,full(f->selected_source));(void)program(f);final=lock(f);
  add(f,FN_CSR_SET_REQUEST,0x9c3cu,0x800u,full(136u),z);
  rd(f,0x9c40u,sp-4u,expected[1]);rd(f,0x9c42u,sp-8u,expected[8]);rd(f,0x9c44u,sp-12u,expected[9]);
  expected[10]=full(f->destination&0xffffff00u);expected[11]=full(f->selected_source);expected[12]=full(256u);
  expected[13]=full(0x8000u);expected[14]=full(0x40022000u);expected[15]=final;expected[16]=full(0x1020307fu);
 } else if(entry==0x18e90u) { wr(f,0x18e94u,0x4002200cu,expected[10]);expected[15]=full(0x40022000u); }
 else if(entry==0x18e98u) { unlock(f);expected[13]=full(0x45670123u);expected[14]=full(0xcdef89abu);expected[15]=full(0x40022000u); }
 else if(entry==0x18eb6u) { final=lock(f);expected[13]=full(0x8000u);expected[14]=full(0x40022000u);expected[15]=final; }
 else if(entry==0x18ec4u) { final=erase(f);expected[10]=full(f->destination&0xffffff00u);expected[13]=full(0xfffdffffu);expected[14]=final;expected[15]=full(0x40022000u); }
 else { final=program(f);expected[10]=full(f->destination&0xffffff00u);expected[12]=full(256u);expected[13]=full(0xfffeffffu);expected[14]=final;expected[15]=full(0x40022000u);expected[16]=full(0x1020307fu); }
 value=full(f->destination);CHECK(fn_run(&h,entry,value,full(f->source))==FN_RETURNED);
 CHECK(f->index==f->count&&h.operations==f->count&&h.normal_register_outputs_valid==1u);
 CHECK(h.words_written==((entry==0x9c0au||entry==0x18ef2u)?64u:0u));
 for(i=0;i<32u;i++)same(f,h.regs[i],expected[i]);
}
int main(void) {
 uint32_t entries[]={0x9c0au,0x18e90u,0x18e98u,0x18eb6u,0x18ec4u,0x18ef2u};unsigned i,mode;
 for(i=0;i<6u;i++)for(mode=0;mode<2u;mode++)one(entries[i],mode);
 printf("{\"passed\":true,\"groups\":1,\"cases\":%u,\"checks\":%u,\"synthetic_effects_only\":true}\n",cases,checks);return 0;
}
