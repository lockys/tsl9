#include "ble_role.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP (RAM+0x4000u)
#define AUTH (RAM+0xc790u)
#define Q BT_QUEUE_BASE
#define D BT_DESCRIPTOR_BASE
#define ALLOC (RAM+0xd000u)
static br_machine m;static br_backend io;
static uint8_t ram[65536],known[65536],scratch[84],sk[84],dep[8],dk[8],event_data[12],event_known[12],adv,ak,stream[128];
static uint16_t mtu,mk;static const br_role_binding *saved;
static unsigned groups,checks,failures,role_calls,old_table_leaks,mtu_calls,updates,submits,stream_n;
static uint32_t stop_site,last_task,last_event,last_delay;static da_flow stop_flow;
#define CHECK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram[a-RAM+i]<<(8*i);return v;}
static da_flow read_mem(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 unsigned i;(void)need;CHECK(p==ram);if(site==stop_site)return stop_flow;if(a<RAM||a-RAM>sizeof(ram)-n)return DA_HALT;
 out->value=out->known=0;for(i=0;i<n;i++){out->value|=(uint32_t)ram[a-RAM+i]<<(8*i);out->known|=(uint32_t)known[a-RAM+i]<<(8*i);}return DA_RETURNED;
}
static da_flow write_mem(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 unsigned i;CHECK(p==ram);if(site==stop_site)return stop_flow;if(a<RAM||a-RAM>sizeof(ram)-n)return DA_HALT;put(a,v,n);for(i=0;i<n;i++)known[a-RAM+i]=(uint8_t)(k>>(8*i));return DA_RETURNED;
}
static da_flow core_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned n,da_scalar*out){
 (void)site;(void)args;(void)n;CHECK(p==ram);if(kind!=DA_ROM)return DA_HALT;out->value=target==124?100u:0u;out->known=UINT32_MAX;return DA_RETURNED;
}
static da_flow report_call(void*p,const rp_request*r,rp_result*out){
 unsigned i;CHECK(p==ram);out->scalar.value=0;out->scalar.known=UINT32_MAX;out->memory_effects=0;
 for(i=0;i<r->buffer_length;i++){uint32_t a=r->arguments[1].value+i;if(r->target==72){r->buffer[i]=0;r->buffer_known[i]=255;}
 else if(a>=RAM&&a<RAM+sizeof(ram)){r->buffer[i]=ram[a-RAM];r->buffer_known[i]=known[a-RAM];}
 else{r->buffer[i]=(uint8_t)i;r->buffer_known[i]=255;}}
 out->memory_effects=1;return DA_RETURNED;
}
static da_flow life_call(void*p,const bl_request*r,da_scalar*out){
 CHECK(p==ram);out->value=5;out->known=15;if(r->callsite==stop_site)return stop_flow;
 if(r->target==216){++mtu_calls;CHECK(r->half==&mtu&&mtu==247&&mk==65535);}
 if(r->target==88){++updates;last_task=r->arguments[0].value;last_event=r->arguments[1].value;last_delay=r->arguments[2].value;}return DA_RETURNED;
}
static da_flow role_start(void*p,const bt_request*r,const br_role_binding*b,bt_result*out){
 CHECK(p==ram);++role_calls;CHECK(r->target==420&&r->callsite==0x8a34&&r->argument_count==3&&r->arguments[0].value==9&&r->arguments[1].value==0);
 CHECK(r->arguments[2].known==0&&b->original_table_va==0x19a78&&b->context==&m);
 CHECK(b->callbacks&&b->callbacks->state_changed&&b->callbacks->parameters_changed&&!b->callbacks->reserved);
 saved=b;out->scalar.value=99;out->scalar.known=255;out->memory_effects=0;return DA_RETURNED;
}
static da_flow transport_call(void*p,const bt_request*r,bt_result*out){
 unsigned i;CHECK(p==ram);out->scalar.value=0;out->scalar.known=UINT32_MAX;out->memory_effects=0;if(r->callsite==stop_site)return stop_flow;
 switch(r->target){
 case 420:++old_table_leaks;return DA_HALT;
 case 316:out->scalar.value=1;break;
 case 184:out->scalar.value=23;break;
 case 296:out->scalar.value=ALLOC;break;
 case 76:for(i=0;i<r->arguments[2].value;i++){uint32_t a=r->arguments[1].value+i,b=r->arguments[0].value+i;
  if(a<RAM||a-RAM>=sizeof(ram)||b<RAM||b-RAM>=sizeof(ram))return DA_HALT;ram[b-RAM]=ram[a-RAM];known[b-RAM]=known[a-RAM];}out->memory_effects=1;break;
 case 212:++submits;for(i=0;i<get(D+2,2)&&stream_n<sizeof(stream);i++)stream[stream_n++]=ram[get(D+4,4)-RAM+i];break;
 case 80:break;
 case 424:++updates;CHECK(r->arguments[0].value==7&&r->arguments[5].value==3);break;
 default:return DA_HALT;
 }return DA_RETURNED;
}
static bt_source event_view(void){bt_source s;s.kind=BT_BORROWED;s.address=0;s.data=event_data;s.known=event_known;s.available=12;return s;}
static void reset(void){
 rp_storage a={scratch,sk,84},b={dep,dk,8};bl_storage c;memset(ram,0,sizeof(ram));memset(known,255,sizeof(known));memset(&io,0,sizeof(io));memset(event_data,0,12);memset(event_known,255,12);
 put(GP+84,RAM+0xc298,4);put(GP+175,1,1);put(GP+365,9,1);put(GP+156,3,1);put(GP+160,4,1);put(GP+158,65534,2);put(GP+162,65534,2);put(AUTH+2,65534,2);put(AUTH+6,65534,2);put(GP+42,0x7788,2);
 io.runtime.core.context=ram;io.runtime.core.read=read_mem;io.runtime.core.write=write_mem;io.runtime.core.call=core_call;io.runtime.report_invoke=report_call;io.runtime.transport_invoke=transport_call;io.lifecycle_invoke=life_call;io.role_start=role_start;
 c.advertise=&adv;c.advertise_known=&ak;c.mtu=&mtu;c.mtu_known=&mk;adv=ak=0;mtu=mk=0;saved=0;role_calls=old_table_leaks=mtu_calls=updates=submits=stream_n=0;stop_site=last_task=last_event=last_delay=0;stop_flow=DA_HALT;br_init(&m,&io,a,b,c);
}
static void callbacks_to_packets(void){
 da_scalar out;bt_source s;unsigned i;++groups;reset();s=event_view();
 CHECK(br_events(&m,9,8,&out)==DA_RETURNED&&out.value==0&&role_calls==1&&!old_table_leaks);
 if(!saved)return;
 event_data[2]=5;event_data[10]=7;CHECK(saved->callbacks->state_changed(saved->context,4,&s,&out)==DA_RETURNED);CHECK(get(GP+158,2)==7&&mtu_calls==1&&adv==1);
 CHECK(br_registration(&m,7,2,&out)==DA_RETURNED&&get(AUTH+2,2)==7);
 CHECK(br_run_pair(&m,0x170e2,0,4,&out)==DA_RETURNED&&get(Q+2,2)==82);for(i=0;i<76;i++)CHECK(ram[Q-RAM+11+i]==scratch[8+i]);
 CHECK(br_events(&m,3,1,&out)==DA_RETURNED);CHECK(br_events(&m,3,2,&out)==DA_RETURNED);CHECK(submits==1&&stream_n==20&&stream[0]==0x55&&stream[2]==0xa0);
 CHECK(saved->callbacks->parameters_changed(saved->context,7,30,0,200,&out)==DA_RETURNED);CHECK(updates==1&&last_task==3&&last_event==4&&last_delay==4800);
 CHECK(br_events(&m,3,4,&out)==DA_RETURNED&&updates==2);
 event_data[2]=6;event_data[4]=7;CHECK(saved->callbacks->state_changed(saved->context,2,&s,&out)==DA_RETURNED);CHECK(get(GP+158,2)==65534&&get(AUTH+2,2)==65534&&out.value==7);
}
static void failure_paths(void){
 da_scalar out;bt_source s;unsigned t;++groups;
 for(t=0;t<2;t++){reset();s=event_view();event_data[2]=5;event_data[10]=7;stop_site=0x85da;stop_flow=t?DA_TRANSFER:DA_HALT;
 CHECK(br_state(&m,4,&s,&out)==stop_flow);CHECK(m.boundary_va==0x85da&&m.boundary_address==372&&get(GP+158,2)==7&&mtu_calls==1);
 if(t){CHECK(br_events(&m,9,8,&out)==DA_TRANSFER&&!role_calls);}else{stop_site=0;CHECK(br_events(&m,9,8,&out)==DA_RETURNED&&role_calls==1);}
 }
 reset();io.role_start=0;CHECK(br_events(&m,9,8,&out)==DA_HALT);CHECK(!old_table_leaks&&m.boundary_va==0x8a34&&m.boundary_address==420);
 reset();s=event_view();event_data[2]=5;event_data[10]=7;io.lifecycle_invoke=0;CHECK(br_state(&m,4,&s,&out)==DA_HALT);CHECK(get(GP+158,2)==7&&m.boundary_va==0x8aaa&&m.boundary_address==80);
}
int main(void){callbacks_to_packets();failure_paths();printf("BLE_ROLE_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
