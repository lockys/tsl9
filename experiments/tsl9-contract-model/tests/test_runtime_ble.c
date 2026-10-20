#include "runtime_ble.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP (RAM+0x4000u)
#define Q BT_QUEUE_BASE
#define D BT_DESCRIPTOR_BASE
#define ALLOC (RAM+0xd000u)
static uint8_t ram[65536],known[65536],scratch[84],sk[84],dep[8],dk[8],stream[2048];
static rtb_machine m;static rtb_backend io;static unsigned groups,checks,failures,upstream_native,posts,submits,stream_n;
static uint32_t stop_site;static da_flow stop_flow;
#define CHECK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram[a-RAM+i]<<(8*i);return v;}
static da_flow read_mem(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 unsigned i;(void)need;CHECK(p==ram);if(site==stop_site)return stop_flow;if(a<RAM||a-RAM>sizeof(ram)-n)return DA_HALT;
 out->value=out->known=0;for(i=0;i<n;i++){out->value|=(uint32_t)ram[a-RAM+i]<<(8*i);out->known|=(uint32_t)known[a-RAM+i]<<(8*i);}return DA_RETURNED;
}
static da_flow write_mem(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 unsigned i;CHECK(p==ram);if(site==stop_site)return stop_flow;if(a<RAM||a-RAM>sizeof(ram)-n)return DA_HALT;put(a,v,n);
 for(i=0;i<n;i++)known[a-RAM+i]=(uint8_t)(k>>(8*i));return DA_RETURNED;
}
static da_flow core_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned n,da_scalar*out){
 (void)site;(void)args;(void)n;CHECK(p==ram);if(kind==DA_NATIVE){++upstream_native;return DA_HALT;}
 if(kind!=DA_ROM)return DA_HALT;out->value=target==124?100u:0u;out->known=UINT32_MAX;return DA_RETURNED;
}
static da_flow report_call(void*p,const rp_request*r,rp_result*out){
 unsigned i;CHECK(p==ram);out->scalar.value=0;out->scalar.known=UINT32_MAX;out->memory_effects=0;
 if(r->callsite==stop_site)return stop_flow;
 for(i=0;i<r->buffer_length;i++){uint32_t a=r->arguments[1].value+i;
 if(r->target==72){r->buffer[i]=0;r->buffer_known[i]=255;}
 else if(a>=RAM&&a<RAM+sizeof(ram)){r->buffer[i]=ram[a-RAM];r->buffer_known[i]=known[a-RAM];}
 else{r->buffer[i]=(uint8_t)i;r->buffer_known[i]=255;}}
 out->memory_effects=1;return DA_RETURNED;
}
static da_flow transport_call(void*p,const bt_request*r,bt_result*out){
 unsigned i;CHECK(p==ram);out->scalar.value=0;out->scalar.known=UINT32_MAX;out->memory_effects=0;
 if(r->callsite==stop_site)return stop_flow;
 switch(r->target){
 case 316:out->scalar.value=1;break;
 case 184:out->scalar.value=23;break;
 case 296:out->scalar.value=ALLOC;break;
 case 76:
  for(i=0;i<r->arguments[2].value;i++){uint32_t a=r->arguments[1].value+i,b=r->arguments[0].value+i;
  if(a<RAM||a-RAM>=sizeof(ram)||b<RAM||b-RAM>=sizeof(ram))return DA_HALT;ram[b-RAM]=ram[a-RAM];known[b-RAM]=known[a-RAM];}
  out->memory_effects=1;break;
 case 212:
  ++submits;for(i=0;i<get(D+2,2)&&stream_n<sizeof(stream);i++)stream[stream_n++]=ram[get(D+4,4)-RAM+i];break;
 case 80:++posts;out->scalar.value=9;out->scalar.known=15;break;
 default:return DA_HALT;
 }return DA_RETURNED;
}
static void reset(void){
 rp_storage a={scratch,sk,84},b={dep,dk,8};memset(ram,0,sizeof(ram));memset(known,255,sizeof(known));memset(&io,0,sizeof(io));
 put(GP+84,RAM+0xc298,4);put(GP+175,1,1);put(GP+365,9,1);put(RAM+0xc792,7,2);put(RAM+0xc796,65534,2);
 put(GP+156,3,1);put(GP+158,7,2);put(GP+160,4,1);put(GP+162,8,2);put(GP+42,0x7788,2);
 io.core.context=ram;io.core.read=read_mem;io.core.write=write_mem;io.core.call=core_call;io.report_invoke=report_call;io.transport_invoke=transport_call;
 upstream_native=posts=submits=stream_n=0;stop_site=0;stop_flow=DA_HALT;rtb_init(&m,&io,a,b);
}
static void full_chain(void){
 da_scalar out;unsigned i,iterations=0;uint8_t expected[82];++groups;reset();
 CHECK(rtb_run_pair(&m,0x170e2,0,4,&out)==DA_RETURNED);CHECK(!upstream_native&&posts==1&&out.known==UINT32_MAX&&out.value==0);
 CHECK(get(GP+344,4)==62&&get(Q+2,2)==82&&get(Q+4,2)==0);
 CHECK(get(Q+6,2)==0x7f55&&get(Q+8,1)==0xa0&&get(Q+10,1)==76);
 for(i=0;i<76;i++){CHECK(ram[Q-RAM+11+i]==scratch[8+i]);CHECK(known[Q-RAM+11+i]==sk[8+i]);}
 memcpy(expected,&ram[Q-RAM+6],82);
 while(get(Q+2,2)&&iterations++<12){CHECK(rtb_events(&m,3,1,&out)==DA_RETURNED);if(get(Q+2,2))CHECK(rtb_events(&m,3,2,&out)==DA_RETURNED);}
 CHECK(iterations==6&&submits==5&&stream_n==82&&get(Q+4,2)==82&&get(Q+2,2)==0);
 CHECK(memcmp(expected,stream,82)==0);CHECK(!upstream_native);
}
static void overwrite_and_direct(void){
 uint8_t bytes[4]={9,8,7,6},masks[4]={255,255,15,255};bt_source s;da_scalar out;++groups;reset();
 CHECK(rtb_run_pair(&m,0x13160,0,0,&out)==DA_RETURNED);CHECK(out.known==0&&get(Q+2,2)==82);
 CHECK(rtb_events(&m,3,1,&out)==DA_RETURNED);CHECK(rtb_events(&m,3,2,&out)==DA_RETURNED);CHECK(stream_n==20);
 s.kind=BT_BORROWED;s.address=0;s.data=bytes;s.known=masks;s.available=4;
 CHECK(rtb_build(&m,7,0x55,&s,4,&out)==DA_RETURNED);CHECK(out.value==9&&out.known==15&&get(Q+2,2)==10&&get(Q+4,2)==0);CHECK(known[Q-RAM+13]==15);
 CHECK(rtb_events(&m,3,1,&out)==DA_RETURNED);CHECK(rtb_events(&m,3,2,&out)==DA_RETURNED);CHECK(stream_n==30&&stream[20]==0x55&&stream[22]==0x55&&stream[25]==9);
}
static void failure_paths(void){
 da_scalar out;unsigned t;++groups;
 for(t=0;t<2;t++){reset();stop_site=0x8df4;stop_flow=t?DA_TRANSFER:DA_HALT;
 CHECK(rtb_run_pair(&m,0x170e2,0,4,&out)==stop_flow);CHECK(m.boundary_va==0x8df4&&m.boundary_address==80);
 CHECK(get(GP+344,4)==62&&get(Q+2,2)==82&&!upstream_native);
 if(t){CHECK(rtb_events(&m,3,1,&out)==DA_TRANSFER);CHECK(!submits);}
 else{stop_site=0;CHECK(rtb_events(&m,3,1,&out)==DA_RETURNED);}
 }
 reset();io.transport_invoke=0;CHECK(rtb_run_pair(&m,0x13160,0,0,&out)==DA_HALT);CHECK(m.boundary_va==0x8d32&&m.boundary_address==316&&get(Q+2,2)==0);
 reset();stop_site=0x92b4;CHECK(rtb_run_pair(&m,0x170e2,0,4,&out)==DA_HALT);CHECK(m.boundary_va==0x92b4&&m.boundary_address==76&&get(Q+2,2)==0);
}
int main(void){full_chain();overwrite_and_direct();failure_paths();printf("RUNTIME_BLE_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
