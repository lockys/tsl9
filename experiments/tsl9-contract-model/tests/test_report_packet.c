#include "report_packet.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP UINT32_C(0x20004000)
#define CFG UINT32_C(0x2000c298)
#define CFG2 UINT32_C(0x2000c400)
#define AUTH UINT32_C(0x2000c790)
#define FULL UINT32_MAX
static uint8_t ram[65536],bits[65536],stack[84],known[84],dependency[8],dep_known[8];
static rp_machine machine;static rp_backend backend;static rp_request events[32];
static uint8_t packets[2][76],packet_bits[2][76];static uint16_t handles[2];
static unsigned event_count,replies,groups,checks,failures,flag_reads;
static uint32_t stop_site,ticks,ticks_known;static int transfer_stop,mutate_reply,partial_descriptor,partial_uid,bad_zero,partial_copy,mutate_flags,unclaimed_copy;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram[a-RAM+i]=(uint8_t)(v>>(8*i));bits[a-RAM+i]=255;}}
static da_flow stop(uint32_t site){return site==stop_site?(transfer_stop?DA_TRANSFER:DA_HALT):DA_RETURNED;}
static da_flow read_ram(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar *out){
 unsigned i;(void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;
 out->value=out->known=0;
 if(site==0x17f6c){++flag_reads;if(mutate_flags)put(a,flag_reads==1?1u:2u,1);}
 for(i=0;i<n;i++){out->value|=(uint32_t)ram[a-RAM+i]<<(8*i);out->known|=(uint32_t)bits[a-RAM+i]<<(8*i);}
 return (out->known&need)==need?DA_RETURNED:DA_HALT;
}
static da_flow invoke(void *p,const rp_request *r,rp_result *out){
 uint32_t i,source=r->arguments[1].value;(void)p;if(event_count<32)events[event_count++]=*r;
 out->scalar.value=out->scalar.known=0;out->memory_effects=0;
 if(r->target==96){CHECK(r->argument_count==2&&r->arguments[0].value==9&&r->arguments[1].value==1);out->scalar.value=ticks;out->scalar.known=ticks_known;return stop(r->callsite);}
 if(unclaimed_copy&&r->callsite==0x92b4)return DA_RETURNED;
 CHECK((r->target==72||r->target==76)&&r->argument_count==3&&r->arguments[0].known==0);
 CHECK(r->buffer&&r->buffer_known&&r->arguments[2].value==r->buffer_length);
 if(stop(r->callsite)!=DA_RETURNED&&!partial_copy)return stop(r->callsite);
 for(i=0;i<r->buffer_length;i++){
  if(partial_copy&&r->callsite==stop_site&&i==1)break;
  if(r->target==72){r->buffer[i]=(uint8_t)(bad_zero&&i==0);r->buffer_known[i]=255;}
  else if(source>=RAM&&source<RAM+65536){r->buffer[i]=ram[source-RAM+i];r->buffer_known[i]=bits[source-RAM+i];}
  else if(source==0x08077b00){r->buffer[i]=(uint8_t)(0x10+i);r->buffer_known[i]=(uint8_t)(partial_descriptor&&i>=2?0:255);}
  else if(source==0x1ffff7ec||source==0x1ffff7e8){r->buffer[i]=(uint8_t)((source==0x1ffff7ec?0x70:0x90)+i);r->buffer_known[i]=(uint8_t)(partial_uid&&i==3?0x0f:255);}
  else return DA_HALT;
 }
 out->memory_effects=1;return stop(r->callsite);
}
static da_flow reply(void *p,const rp_reply *r){
 (void)p;CHECK(r->wrapper_va==0x8cfa&&r->callsite==0x133bc&&r->command==0xa0&&r->length==76);
 CHECK(r->data==stack+8&&r->known==known+8);
 if(replies<2){memcpy(packets[replies],r->data,76);memcpy(packet_bits[replies],r->known,76);handles[replies]=r->handle;}++replies;
 if(mutate_reply){unsigned i;put(GP+84,CFG2,4);put(AUTH+6,33,2);for(i=0;i<112;i++)put(CFG2+i,0x50+i,1);put(CFG2+4,8,1);put(0x2000bf44,0xee,1);}
 return stop(r->callsite);
}
static void fixture(void){
 rp_storage a={stack,known,84},b={dependency,dep_known,8};unsigned i;
 memset(ram,0,sizeof(ram));memset(bits,255,sizeof(bits));memset(stack,0xee,sizeof(stack));memset(known,255,sizeof(known));memset(dependency,0xee,sizeof(dependency));
 memset(dep_known,255,sizeof(dep_known));memset(events,0,sizeof(events));memset(packets,0,sizeof(packets));memset(packet_bits,0,sizeof(packet_bits));
 put(GP+84,CFG,4);put(GP+365,9,1);put(AUTH+2,65534,2);put(AUTH+6,65534,2);
 for(i=0;i<112;i++)put(CFG+i,0xa0+i,1);put(CFG+4,0,1);
 for(i=0;i<19;i++)put(0x2000bf44+i,0xc0+i,1);
 event_count=replies=flag_reads=0;stop_site=0;ticks=1600;ticks_known=FULL;transfer_stop=mutate_reply=partial_descriptor=partial_uid=bad_zero=partial_copy=mutate_flags=unclaimed_copy=0;
 backend.context=0;backend.read=read_ram;backend.invoke=invoke;backend.reply=reply;rp_init(&machine,&backend,a,b);
}
static void connection(unsigned index,uint16_t h,uint8_t auth,uint8_t mode){uint32_t a=AUTH+4*index;put(a+2,h,2);put(a+4,auth,1);put(a+5,mode,1);}
static da_flow run(void){return rp_run_a0(&machine,0x12345678);}
static void no_connections_prelude(void){++groups;fixture();CHECK(run()==DA_RETURNED);CHECK(event_count==5&&replies==0);
 CHECK(events[0].callsite==0x9db4&&events[0].buffer_length==8&&events[0].buffer==dependency);
 CHECK(events[1].callsite==0x1319a&&events[1].target==72&&events[1].buffer==stack+8&&events[1].buffer_length==76);
 CHECK(events[2].callsite==0x92b4&&events[3].callsite==0x92ce&&events[4].callsite==0x131cc);
 CHECK(stack[8]==0&&stack[9]==0x10&&stack[10]==0x11&&stack[48]==0xc0&&known[48]==255);
}
static void unauth_packet(void){unsigned i;++groups;fixture();connection(0,7,0,0);CHECK(run()==DA_RETURNED);CHECK(replies==1&&handles[0]==7&&packets[0][3]==1&&event_count==7);
 CHECK(packets[0][0]==0&&packets[0][1]==0x10&&packets[0][2]==0x11&&packets[0][4]==0x70&&packets[0][12]==0x90);
 for(i=18;i<40;i++)CHECK(packets[0][i]==0);for(i=59;i<76;i++)CHECK(packets[0][i]==0);CHECK(packets[0][40]==0xc0&&packets[0][58]==0xd2);
}
static void auth_payload_and_masks(void){unsigned i;++groups;fixture();connection(0,7,1,0);put(0x2000c91c,1,1);bits[0xc91c]=3;mutate_flags=1;
 CHECK(run()==DA_RETURNED);CHECK(replies==1&&flag_reads==2);CHECK((packets[0][18]&24)==24);
 CHECK(packets[0][20]==0x1a&&packets[0][21]==4&&packets[0][22]==0&&packets[0][23]==7);
 for(i=0;i<16;i++)CHECK(packets[0][24+i]==ram[CFG-RAM+i]);for(i=0;i<16;i++)CHECK(packets[0][59+i]==ram[CFG-RAM+96+i]);
 fixture();connection(0,7,1,0);ticks_known=0x7ffff;partial_descriptor=partial_uid=1;CHECK(run()==DA_RETURNED);
 CHECK(packet_bits[0][1]==255&&packet_bits[0][2]==255&&packet_bits[0][7]==15&&packet_bits[0][15]==15);
 fixture();connection(0,7,1,0);ticks_known=0x3ffff;CHECK(run()==DA_HALT);CHECK(machine.boundary_va==0x16f36&&machine.needed_mask==0x7ffff&&replies==0);
}
static void slot_inheritance_and_live_copy(void){++groups;fixture();connection(0,7,1,0);connection(1,8,0,0);CHECK(run()==DA_RETURNED);CHECK(replies==2);
 CHECK(packets[1][3]==1&&packets[1][18]==0&&packets[1][19]==0);
 CHECK(packets[1][20]==packets[0][20]&&packets[1][21]==packets[0][21]&&packets[1][22]==packets[0][22]&&packets[1][23]==packets[0][23]);
 fixture();connection(0,7,1,0);connection(1,8,1,0);mutate_reply=1;CHECK(run()==DA_RETURNED);CHECK(replies==2&&handles[1]==33);
 CHECK(packets[0][24]==0xa0&&packets[1][24]==0x50&&packets[1][59]==0xb0);CHECK(packets[0][40]==0xc0&&packets[1][40]==0xc0);
}
static void gates_and_zero_contract(void){++groups;fixture();connection(0,65534,1,0);bits[AUTH+5-RAM]=0;CHECK(run()==DA_RETURNED);CHECK(replies==0);
 fixture();connection(0,7,1,1);bits[AUTH+4-RAM]=0;CHECK(run()==DA_RETURNED);CHECK(replies==0);
 fixture();connection(0,65535,0,0);CHECK(run()==DA_RETURNED);CHECK(replies==1&&handles[0]==65535);
 fixture();bad_zero=1;CHECK(run()==DA_HALT);CHECK(machine.boundary_va==0x1319a&&machine.boundary_address==72);
 fixture();connection(0,7,0,0);unclaimed_copy=1;CHECK(run()==DA_HALT);CHECK(machine.boundary_va==0x92b4&&replies==0); /* A returned no-op cannot prove ROM copy effects. */
}
static void failures_preserve_prefix(void){unsigned i,t;static const uint32_t sites[]={0x9db4,0x1319a,0x92b4,0x92ce,0x131cc,0x16f36,0x13398,0x133aa,0x133bc};
 ++groups;for(t=0;t<2;t++)for(i=0;i<sizeof(sites)/sizeof(sites[0]);i++){unsigned before;fixture();connection(0,7,1,0);stop_site=sites[i];transfer_stop=(int)t;partial_copy=1;
 CHECK(run()==(t?DA_TRANSFER:DA_HALT));CHECK(machine.boundary_va==sites[i]);
 if(sites[i]==0x9db4){CHECK(dependency[0]==0x10&&dep_known[0]==255&&known[0]==0);}
 if(t){before=event_count;CHECK(run()==DA_TRANSFER);CHECK(event_count==before);}
 }
 fixture();connection(0,7,0,0);bits[AUTH+5-RAM]=0;CHECK(run()==DA_HALT);CHECK(machine.boundary_va==0x131ee&&stack[11]==0);
}
static void invalid_storage(void){rp_storage a={stack,known,83},b={dependency,dep_known,8};++groups;fixture();rp_init(&machine,&backend,a,b);CHECK(run()==DA_HALT);CHECK(event_count==0&&machine.boundary_va==0x13160);}
int main(void){no_connections_prelude();unauth_packet();auth_payload_and_masks();slot_inheritance_and_live_copy();gates_and_zero_contract();failures_preserve_prefix();invalid_storage();printf("REPORT_PACKET_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
