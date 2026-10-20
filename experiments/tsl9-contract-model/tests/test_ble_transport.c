#include "ble_transport.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define Q BT_QUEUE_BASE
#define D BT_DESCRIPTOR_BASE
#define SRC (RAM+0x1000u)
#define ALLOC (RAM+0xd000u)
static uint8_t data[0x20000],known[0x20000];
static bt_machine m;static bt_backend io;
static unsigned checks,failures,groups,roms[512],read_calls,write_calls;
static uint32_t query,mtu,alloc_result,submit_status,message;
static uint32_t halt_read,halt_write,stop_site,stop_target,mutate;
static da_flow stop_flow;
static int claim_copy;
static uint32_t last_task,last_event,last_delay,copy_src,copy_dst,copy_n,table_id;
#define CHECK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){data[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)data[a-RAM+i]<<(8*i);return v;}
static da_flow read_mem(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 unsigned i;(void)p;(void)need;(void)site;++read_calls;out->value=out->known=0;
 if(a<RAM||a-RAM>sizeof(data)-n||a==halt_read)return DA_HALT;
 for(i=0;i<n;i++){out->value|=(uint32_t)data[a-RAM+i]<<(8*i);out->known|=(uint32_t)known[a-RAM+i]<<(8*i);}return DA_RETURNED;
}
static da_flow write_mem(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 unsigned i;(void)p;(void)site;++write_calls;if(a<RAM||a-RAM>sizeof(data)-n||a==halt_write)return DA_HALT;
 for(i=0;i<n;i++){data[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=(uint8_t)(k>>(8*i));}return DA_RETURNED;
}
static da_flow invoke(void*p,const bt_request*r,bt_result*out){
 unsigned i;(void)p;if(r->target<512)roms[r->target]++;out->scalar.value=0;out->scalar.known=UINT32_MAX;out->memory_effects=0;
 if((stop_target&&r->target==stop_target)||(stop_site&&r->callsite==stop_site))return stop_flow;
 switch(r->target){
 case 316:
  out->scalar.value=query;
  if(mutate==1){put(RAM+0x409c,99,1);put(RAM+0x409e,55,2);}
  if(mutate==2)put(RAM+0x402a,0x9911,2);
  break;
 case 184:out->scalar.value=mtu;out->scalar.known=65535;break;
 case 296:
  out->scalar.value=alloc_result;
  if(mutate==3){put(Q+4,2,2);put(D+2,1,2);}
  break;
 case 76:
  copy_dst=r->arguments[0].value;copy_src=r->arguments[1].value;copy_n=r->arguments[2].value;
  if(claim_copy){for(i=0;i<copy_n;i++){uint32_t a=copy_src+i,b=copy_dst+i;if(a<RAM||a-RAM>=sizeof(data)||b<RAM||b-RAM>=sizeof(data))return DA_HALT;data[b-RAM]=data[a-RAM];known[b-RAM]=known[a-RAM];}out->memory_effects=1;}break;
 case 212:
  CHECK(r->arguments[1].value==D||r->arguments[1].value==D+8);
  out->scalar.value=submit_status;
  if(mutate==4){put(Q+4,7,2);put(D+2,3,2);}
  break;
 case 300:if(mutate==5)put(Q,0,1);break;
 case 80:case 88:
  last_task=r->arguments[0].value;last_event=r->arguments[1].value;
  last_delay=r->target==88?r->arguments[2].value:0;
  out->scalar.value=0x12345678;out->scalar.known=0xff00ff00;break;
 case 108:out->scalar.value=message;break;
 case 420:table_id=r->arguments[2].value;break;
 default:break;
 }return DA_RETURNED;
}
static void reset(void){
 memset(data,0,sizeof(data));memset(known,255,sizeof(known));memset(roms,0,sizeof(roms));
 query=1;mtu=23;alloc_result=ALLOC;submit_status=message=0;halt_read=halt_write=stop_site=stop_target=mutate=0;
 stop_flow=DA_HALT;claim_copy=1;last_task=last_event=last_delay=copy_src=copy_dst=copy_n=table_id=0;read_calls=write_calls=0;
 put(RAM+0x409c,3,1);put(RAM+0x409e,7,2);put(RAM+0x40a0,4,1);put(RAM+0x40a2,8,2);put(RAM+0x402a,0x7788,2);
 io.context=0;io.read=read_mem;io.write=write_mem;io.invoke=invoke;bt_init(&m,&io);
}
static bt_source mapped(uint32_t a){bt_source s;s.kind=BT_MAPPED;s.address=a;s.data=s.known=0;s.available=0;return s;}
static void builder(void){
 bt_source s;da_scalar out;unsigned i;uint8_t expected[9]={0x55,0x7f,0xa0,0,3,1,2,3,0xa9};
 ++groups;reset();s=mapped(SRC);put(SRC,0x030201,3);
 CHECK(bt_build(&m,7,0x1234a0,&s,3,&out)==DA_RETURNED);
 for(i=0;i<9;i++)CHECK(data[Q-RAM+6+i]==expected[i]);
 CHECK(get(Q+2,2)==9&&get(Q+4,2)==0);CHECK(last_task==3&&last_event==1);CHECK(roms[316]==1&&roms[80]==1);CHECK(out.value==0x12345678&&out.known==0xff00ff00);
 reset();CHECK(bt_build(&m,0x10007,0,0,0,&out)==DA_RETURNED);CHECK(!roms[316]&&!write_calls&&out.value==0x10007&&out.known==UINT32_MAX);
 reset();halt_read=RAM+0x409e;CHECK(bt_build(&m,7,0,0,1040,&out)==DA_RETURNED);CHECK(!read_calls&&!write_calls&&out.value==7);
 reset();CHECK(bt_build(&m,7,0,0,0,&out)==DA_RETURNED);CHECK(get(Q+2,2)==6&&get(Q+11,1)==0);
 reset();s=mapped(SRC);for(i=0;i<1039;i++)put(SRC+i,i,1);CHECK(bt_build(&m,7,0xa0,&s,1039,&out)==DA_RETURNED);CHECK(get(Q+2,2)==1045&&get(Q+9,1)==4&&get(Q+10,1)==15);
}
static void alias_and_prefix(void){
 bt_source s;da_scalar out;++groups;reset();s=mapped(Q+10);CHECK(bt_build(&m,7,0xa0,&s,3,&out)==DA_RETURNED);
 CHECK(get(Q+11,1)==3&&get(Q+12,1)==3&&get(Q+13,1)==3);
 reset();s=mapped(SRC);put(SRC,0x030201,3);halt_read=SRC+1;
 CHECK(bt_build(&m,7,0xa0,&s,3,&out)==DA_HALT);CHECK(get(Q+6,2)==0x7f55&&get(Q+11,1)==1&&get(Q+2,2)==0);CHECK(m.boundary_va==0x8dfa&&m.boundary_address==SRC+1);
 reset();s=mapped(SRC);put(SRC,0x0201,2);known[SRC-RAM+1]=15;
 CHECK(bt_build(&m,7,0xa0,&s,2,&out)==DA_RETURNED);CHECK(known[Q-RAM+12]==15);CHECK(known[Q-RAM+13]!=255);
 reset();s.kind=BT_BORROWED;s.address=0;s.data=&data[SRC-RAM];s.known=&known[SRC-RAM];s.available=1;put(SRC,9,1);
 CHECK(bt_build(&m,7,0xa0,&s,2,&out)==DA_HALT);CHECK(get(Q+11,1)==9&&get(Q+2,2)==0);
}
static void builder_gates(void){
 bt_source s;da_scalar out;++groups;reset();put(RAM+0x40a2,7,2);s=mapped(SRC);query=2;
 CHECK(bt_build(&m,7,0,&s,0,&out)==DA_RETURNED);CHECK(roms[316]==2&&!write_calls&&out.value==2&&out.known==UINT32_MAX);
 reset();put(RAM+0x409e,65534,2);put(RAM+0x40a2,65534,2);CHECK(bt_build(&m,65534,0,0,0,&out)==DA_RETURNED);CHECK(!roms[316]);
 reset();mutate=1;CHECK(bt_build(&m,7,0xa0,0,0,&out)==DA_RETURNED);CHECK(last_task==99&&get(Q+8,1)==0xa0);
 reset();stop_site=0x8df4;stop_flow=DA_TRANSFER;CHECK(bt_build(&m,7,0xa0,0,0,&out)==DA_TRANSFER);CHECK(get(Q+2,2)==6);CHECK(bt_events(&m,3,1,&out)==DA_TRANSFER);
}
static void event1(void){
 da_scalar out;unsigned i;uint32_t remaining[]={20,1,0,32767,32768,65535};++groups;
 for(i=0;i<6;i++){reset();put(Q+2,remaining[i],2);CHECK(bt_events(&m,3,0xabcd0003,&out)==DA_RETURNED);CHECK(out.value==0xabcd0002&&out.known==UINT32_MAX);
 if(remaining[i]&&remaining[i]<32768){CHECK(get(D+2,2)==(remaining[i]<20?remaining[i]:20));CHECK(get(Q,1)==10&&last_task==3&&last_event==2);}else CHECK(get(Q+2,2)==0&&!roms[184]);}
 for(i=0;i<4;i++){reset();mtu=i;put(Q+2,9,2);CHECK(bt_events(&m,3,1,&out)==DA_RETURNED);CHECK(get(D+2,2)==(i==3?0u:9u));}
 reset();query=3;put(Q+2,20,2);CHECK(bt_events(&m,3,1,&out)==DA_RETURNED);CHECK(get(Q+2,2)==0&&!roms[184]);
 reset();put(RAM+0x409e,65534,2);put(Q+2,5,2);CHECK(bt_events(&m,3,1,&out)==DA_RETURNED);CHECK(roms[316]&&get(D+2,2)==5);
 reset();CHECK(bt_events(&m,0x103,1,&out)==DA_RETURNED);CHECK(out.value==0&&!roms[316]);
}
static void prep2(void){put(Q,10,1);put(Q+2,9,2);put(Q+4,1,2);put(D+2,2,2);put(Q+7,0x2211,2);}
static void event2(void){
 da_scalar out;++groups;reset();prep2();CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);
 CHECK(copy_src==Q+7&&copy_dst==ALLOC&&copy_n==2);CHECK(get(D+4,4)==ALLOC&&get(D,2)==0x7788&&get(Q+4,2)==3);CHECK(roms[212]==1&&!roms[300]&&last_event==1&&out.value==0);
 reset();prep2();mutate=3;CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(copy_src==Q+8&&copy_n==1&&get(Q+4,2)==3);
 reset();prep2();mutate=4;CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(get(Q+4,2)==10);
 reset();prep2();mutate=2;query=3;CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(get(D,2)==0x9911);
 reset();put(Q+2,99,2);CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(!roms[296]&&get(Q+2,2)==0);
}
static void retries(void){
 da_scalar out;++groups;reset();prep2();alloc_result=0;put(D+4,999,4);CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(get(D+4,4)==0&&get(Q,1)==9&&!roms[300]&&last_event==2&&last_delay==2);
 reset();prep2();query=2;CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(roms[300]==1&&!roms[212]&&get(Q,1)==9);
 reset();prep2();submit_status=1;mutate=5;CHECK(bt_events(&m,3,2,&out)==DA_RETURNED);CHECK(get(Q,1)==255&&roms[300]==1);
 reset();prep2();claim_copy=0;CHECK(bt_events(&m,3,2,&out)==DA_HALT);CHECK(m.boundary_va==0x896a&&m.boundary_address==76&&!roms[316]&&get(D+4,4)==ALLOC);
}
static void other_events(void){
 da_scalar out;++groups;reset();CHECK(bt_events(&m,999,0xf000800b,&out)==DA_RETURNED);CHECK(out.value==0xf000000b&&roms[108]==1&&!roms[420]);
 reset();message=SRC;put(SRC,176,1);put(SRC+4,42,1);CHECK(bt_events(&m,3,0x8000,&out)==DA_RETURNED);CHECK(roms[300]==1&&roms[104]==1);
 reset();CHECK(bt_events(&m,999,0x1234000b,&out)==DA_RETURNED);CHECK(out.value==0x12340003&&roms[420]==1&&table_id==0x19a78);
 reset();CHECK(bt_events(&m,3,0x12340004,&out)==DA_RETURNED);CHECK(out.value==0x12340000&&roms[424]==1);
 reset();CHECK(bt_events(&m,3,0x12340000,&out)==DA_RETURNED);CHECK(out.value==0);
}
static void stop_prefix(void){
 da_scalar out;unsigned i;uint32_t sites[]={0x8952,0x896a,0x8976,0x89c2,0x89dc};
 ++groups;for(i=0;i<5;i++){reset();prep2();stop_site=sites[i];CHECK(bt_events(&m,3,2,&out)==DA_HALT);CHECK(m.boundary_va==sites[i]);if(i)CHECK(get(D+4,4)==ALLOC);CHECK(out.known==0);}
 reset();prep2();stop_site=0x896a;stop_flow=DA_TRANSFER;CHECK(bt_events(&m,3,2,&out)==DA_TRANSFER);CHECK(bt_build(&m,7,1,0,0,&out)==DA_TRANSFER);CHECK(roms[76]==1);
 reset();known[Q-RAM]=0;CHECK(bt_events(&m,3,2,&out)==DA_HALT);CHECK(m.boundary_address==Q&&!roms[296]);
 reset();halt_write=Q+4;CHECK(bt_build(&m,7,0,0,0,&out)==DA_HALT);CHECK(get(Q+2,2)==6&&!roms[80]);
}
int main(void){builder();alias_and_prefix();builder_gates();event1();event2();retries();other_events();stop_prefix();printf("BLE_TRANSPORT_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
