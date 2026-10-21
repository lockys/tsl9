#include "page_reply.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks,cases;
#define CHECK(x) do {checks++;if(!(x)){fprintf(stderr,"failure line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
typedef struct cell {uint32_t address,value,known;} cell;
typedef struct fixture {op_host h;cell memory[96];unsigned cells;op_event events[64];unsigned count,stop;op_flow stop_flow;unsigned unknown_read,mutate,null_alloc,memory_regs;uint32_t index;} fixture;
static void put(fixture *f,uint32_t a,uint32_t v,uint32_t k){unsigned i;cell c={a,v,k};for(i=0;i<f->cells;i++)if(f->memory[i].address==a){f->memory[i].value=v;f->memory[i].known=k;return;}CHECK(f->cells<96);f->memory[f->cells++]=c;}
static cell get(fixture *f,uint32_t a){unsigned i;cell c={a,0,0};for(i=0;i<f->cells;i++)if(f->memory[i].address==a)return f->memory[i];return c;}
static int provide(op_host *h,op_event *e){fixture *f=(fixture *)h->user;unsigned at=f->count;CHECK(at<64);f->events[f->count++]=*e;
 if(e->kind==OP_WRITE)put(f,e->address,e->value,e->value_known);
 if(e->kind==OP_READ){cell c=get(f,e->address);e->value=c.value;e->value_known=c.known;if(f->unknown_read==at+1u)e->value_known=0;}
 if(f->memory_regs&&e->kind==OP_WRITE)op_set(h,9u,0xbaddu);
 if(e->kind==OP_ALLOCATE){CHECK(e->raw_target==0xa001u&&e->target==0xa000u);CHECK(e->args[0]==1026u&&e->args[1]==0x44u&&e->args[2]==f->index);CHECK(h->regs[1]==0x9bb0u&&h->regs[15]==0xa001u);e->value=f->null_alloc?0u:0x3000u;e->value_known=1u;
  if(f->mutate==1u){op_set(h,9u,0x1234ffffu);op_set(h,18u,0x50000u);put(f,0x5004cu,0xc101u,1u);}
  if(f->mutate==5u){h->known&=~((uint32_t)1u<<9);}
  if(f->mutate==6u){put(f,0x2000101cu,0xabcdu,1u);op_set(h,11u,0x7788u);}
 }
 if(e->kind==OP_COPY_BYTES){uint32_t idx=f->mutate==1u?0x1234ffffu:f->index;uint32_t source=(uint32_t)(((uint64_t)0x20004u+idx)<<10);CHECK(e->args[0]==0x3002u&&e->args[1]==source&&e->args[2]==1024u);CHECK(e->raw_target==(f->mutate==1u?0xc101u:0xc001u));CHECK(h->regs[1]==0x9bd6u);e->value=0xf00du;e->value_known=1u;
  if(f->mutate==2u){op_set(h,19u,0x99u);op_set(h,20u,0x55u);op_set(h,8u,0x3500u);}
 }
 if(e->kind==OP_TRANSMIT){CHECK(e->target==0x8a56u&&e->args[0]==(f->mutate==2u?0x99u:0x33u));CHECK(e->args[1]==(f->mutate==2u?0x55u:0x44u)&&e->args[2]==(f->mutate==2u?0x3500u:0x3000u)&&e->args[3]==1026u);CHECK(h->regs[1]==0x9be4u);op_set(h,11u,0x11223344u);op_set(h,12u,0xaabbccddu);e->value=0xdeadu;e->value_known=1u;
  if(f->mutate==3u){op_set(h,8u,0x7770u);op_set(h,18u,0x60000u);put(f,0x60068u,0xf101u,1u);put(f,0x20001018u,0x9876u,1u);put(f,0x2000101cu,0xabcdu,1u);}
  if(f->mutate==4u){unsigned i;op_set(h,2u,0x20002000u);for(i=0;i<6;i++)put(f,0x20002000u+8u+4u*i,0x9001u+i*2u,1u);}
 }
 if(e->kind==OP_RELEASE_TAIL){CHECK(e->args[0]==(f->mutate==3u?0x7770u:(f->mutate==2u?0x3500u:0x3000u)));CHECK(e->raw_target==(f->mutate==3u?0xf101u:0xf001u));CHECK(e->target==(e->raw_target&~1u));CHECK(e->args[1]==0x11223344u&&e->args[2]==0xaabbccddu);CHECK(h->regs[1]==(f->mutate==3u?0xabcdu:(f->mutate==4u?0x900bu:0x1111u)));e->value=0xfeed1234u;e->value_known=1u;}
 if(f->stop==at+1u)e->flow=f->stop_flow;
 return 1;
}
static void init(fixture *f,uint32_t idx){unsigned i;memset(f,0,sizeof(*f));f->index=idx;f->h.provider=provide;f->h.user=f;f->h.known=0xffffffffu;for(i=0;i<32;i++)f->h.regs[i]=0x1000u+i;f->h.regs[2]=0x20001020u;f->h.regs[1]=0x1111u;put(f,0x40070u,0xa001u,1u);put(f,0x4004cu,0xc001u,1u);put(f,0x40068u,0xf001u,1u);put(f,0x50068u,0xf001u,1u);}
static op_result run(fixture *f){cases++;return tsl9_ota_page_reply_9b8e(&f->h,0x33u,0x44u,f->index);}
static void normal_cases(void){static const uint32_t indexes[]={0u,1u,0xffffu,0x10000u,0x12345678u,0xffffffffu,0xfffdfffcu};unsigned i,j;static const uint32_t sites[]={0x9b90,0x9b96,0x9b9a,0x9b9c,0x9b9e,0x9ba0,0x9ba2,0x9bae,0x9bb6,0x9bba,0x9bc2,0x9bd4,0x9be0,0x9be6,0x9be8,0x9bec,0x9bee,0x9bf0,0x9bf2,0x9bf4,0x9bf8};
 static const unsigned saves[]={0,2,3,4,5,6};static const uint32_t offsets[]={16,20,12,8,28,24},values[]={0x1012,0x1009,0x1013,0x1014,0x1111,0x1008};
 for(i=0;i<sizeof(indexes)/sizeof(indexes[0]);i++){fixture f;op_result r;init(&f,indexes[i]);r=run(&f);CHECK(r.flow==OP_RETURNED&&r.value_known&&r.value==0xfeed1234u&&r.tail_delegated);CHECK(r.caller_link_raw==0x1111u&&r.caller_link_target==0x1110u&&r.caller_link_known);CHECK(f.count==21u);for(j=0;j<f.count;j++)CHECK(f.events[j].site==sites[j]);for(j=0;j<6u;j++){op_event e=f.events[saves[j]];CHECK(e.kind==OP_WRITE&&e.width==4u&&e.address==0x20001000u+offsets[j]&&e.value==values[j]&&e.value_known);}
 CHECK(f.events[1].kind==OP_READ&&f.events[1].width==4u&&f.events[1].address==0x40070u);CHECK(f.events[10].kind==OP_READ&&f.events[10].address==0x4004cu);CHECK(f.events[13].kind==OP_READ&&f.events[13].address==0x20001018u);CHECK(f.events[14].kind==OP_READ&&f.events[14].address==0x40068u);CHECK(f.events[15].address==0x2000101cu&&f.events[16].address==0x20001014u&&f.events[17].address==0x20001010u&&f.events[18].address==0x2000100cu&&f.events[19].address==0x20001008u);
 CHECK(get(&f,0x3001u).value==(indexes[i]&255u));CHECK(get(&f,0x3000u).value==((indexes[i]>>8)&255u));CHECK(f.h.regs[2]==0x20001020u);CHECK(f.h.regs[8]==0x1008u&&f.h.regs[9]==0x1009u&&f.h.regs[18]==0x1012u);CHECK(f.events[0].width==4u&&f.events[8].width==1u&&f.events[9].width==1u);}
}
static void mutations(void){unsigned m;for(m=1;m<=6;m++){fixture f;op_result r;init(&f,0x10001u);f.mutate=m;if(m==6)f.null_alloc=1;r=run(&f);if(m==5){CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==8u);continue;}CHECK(r.flow==OP_RETURNED);if(m==1){CHECK(get(&f,0x3000u).value==255u&&get(&f,0x3001u).value==255u);}if(m==3){CHECK(r.caller_link_raw==0xabcdu&&f.h.regs[8]==0x9876u);}if(m==4){CHECK(f.h.regs[2]==0x20002020u&&f.h.regs[8]==0x9009u&&r.caller_link_raw==0x900bu);}if(m==6){CHECK(r.value==0u&&r.value_known&&!r.tail_delegated&&f.count==14u);CHECK(f.h.regs[11]==0x7788u&&r.caller_link_raw==0xabcdu);}}}
static void stopped_prefix(void){fixture baseline;op_result r;unsigned at,k;init(&baseline,0x12345678u);r=run(&baseline);CHECK(r.flow==OP_RETURNED);for(at=1;at<=baseline.count;at++)for(k=OP_UNKNOWN;k<=OP_TRANSFER;k++){fixture f;unsigned j;init(&f,0x12345678u);f.stop=at;f.stop_flow=(op_flow)k;r=run(&f);CHECK(r.flow==(op_flow)k&&!r.value_known&&f.count==at);for(j=0;j<at;j++)CHECK(f.events[j].kind==baseline.events[j].kind&&f.events[j].site==baseline.events[j].site&&f.events[j].address==baseline.events[j].address&&f.events[j].value==baseline.events[j].value);}
 for(at=1;at<=baseline.count;at++)if(baseline.events[at-1u].kind==OP_READ){fixture f;init(&f,3u);f.unknown_read=at;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==at);}
 {fixture f;init(&f,1u);f.memory_regs=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.h.unsupported_memory_register_mutation&&f.count==1u);CHECK(get(&f,0x20001010u).known);}
}
int main(void){normal_cases();mutations();stopped_prefix();printf("{\"passed\":true,\"groups\":3,\"cases\":%u,\"checks\":%u,\"synthetic_provider\":true,\"RV32_execution\":false}\n",cases,checks);return 0;}
