#include "ble_lifecycle.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP (RAM+0x4000u)
#define AUTH (RAM+0xc790u)
#define SRC (RAM+0x1000u)
static bl_machine m;static bl_backend io;static uint8_t ram[65536],known[65536],adv,ak;static uint16_t mtu,mk;
static unsigned groups,checks,failures,calls,posts,updates,disconnects;static uint32_t stop_site,mutation,last_task,last_event,last_delay;
static da_flow stop_flow;
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
static da_flow invoke(void*p,const bl_request*r,da_scalar*out){
 CHECK(p==ram);++calls;out->value=0xabcdef12;out->known=0x00ff00ff;
 if(r->callsite==stop_site)return stop_flow;
 switch(r->target){
 case 80:++posts;last_task=r->arguments[0].value;last_event=r->arguments[1].value;if(mutation==1){put(GP+156,99,1);put(GP+158,11,2);}break;
 case 88:++updates;last_task=r->arguments[0].value;last_event=r->arguments[1].value;last_delay=r->arguments[2].value;break;
 case 216:CHECK(r->half==&mtu&&r->half_known==&mk&&mtu==247&&mk==65535);CHECK(r->arguments[1].known==0);
  if(mutation==1){CHECK(r->arguments[0].value==11&&r->arguments[2].value==99);put(GP+162,12,2);}break;
 case 372:CHECK(r->byte==&adv&&r->byte_known==&ak&&ak==255);CHECK(r->arguments[0].value==773&&r->arguments[1].value==1&&r->arguments[2].known==0);
  if(mutation==2)put(SRC+4,8,2);break;
 case 380:++disconnects;CHECK(r->arguments[0].value==7);break;
 default:return DA_HALT;
 }return DA_RETURNED;
}
static bt_source source(void){bt_source s;s.kind=BT_MAPPED;s.address=SRC;s.data=s.known=0;s.available=0;return s;}
static void reset(void){
 bl_storage s;memset(ram,0,sizeof(ram));memset(known,255,sizeof(known));calls=posts=updates=disconnects=0;stop_site=mutation=last_task=last_event=last_delay=0;stop_flow=DA_HALT;adv=ak=0;mtu=mk=0;
 put(GP+156,3,1);put(GP+160,4,1);put(GP+158,65534,2);put(GP+162,65534,2);put(AUTH+2,65534,2);put(AUTH+6,65534,2);
 io.context=ram;io.read=read_mem;io.write=write_mem;io.invoke=invoke;s.advertise=&adv;s.advertise_known=&ak;s.mtu=&mtu;s.mtu_known=&mk;bl_init(&m,&io,s);
}
static void connected(void){
 bt_source s;da_scalar out;++groups;reset();s=source();put(SRC+2,5,1);put(SRC+10,7,2);
 CHECK(bl_state(&m,4,&s,&out)==DA_RETURNED);CHECK(get(GP+158,2)==7&&get(GP+162,2)==65534&&posts==1&&last_task==3&&last_event==4);CHECK(adv==1&&calls==3&&out.value==0xabcdef12&&out.known==0x00ff00ff);
 reset();put(GP+158,9,2);put(SRC+2,5,1);put(SRC+10,7,2);CHECK(bl_state(&m,4,&s,&out)==DA_RETURNED);CHECK(get(GP+162,2)==7&&last_task==4&&adv==0);
 reset();put(GP+158,9,2);put(GP+162,10,2);put(SRC+2,5,1);put(SRC+10,7,2);CHECK(bl_state(&m,4,&s,&out)==DA_RETURNED);CHECK(disconnects==1&&!posts&&calls==1);
 reset();put(SRC+2,5,1);put(SRC+10,7,2);mutation=1;CHECK(bl_state(&m,4,&s,&out)==DA_RETURNED);CHECK(adv==0);
}
static void disconnected(void){
 bt_source s;da_scalar out;++groups;reset();s=source();put(GP+158,7,2);put(AUTH+2,7,2);put(AUTH+4,0x1111,2);put(SRC+2,6,1);put(SRC+4,7,2);
 CHECK(bl_state(&m,2,&s,&out)==DA_RETURNED);CHECK(get(GP+158,2)==65534&&get(AUTH+2,2)==65534&&get(AUTH+4,2)==0&&adv==1&&out.value==7&&out.known==UINT32_MAX);
 reset();put(GP+158,7,2);put(AUTH+2,7,2);put(AUTH+6,8,2);put(SRC+2,6,1);put(SRC+4,7,2);mutation=2;
 CHECK(bl_state(&m,3,&s,&out)==DA_RETURNED);CHECK(get(AUTH+2,2)==7&&get(AUTH+6,2)==65534&&out.value==8);
}
static void noops_and_storage(void){
 bt_source s;da_scalar out;++groups;reset();CHECK(bl_state(&m,0,0,&out)==DA_RETURNED&&out.value==0&&out.known==UINT32_MAX);CHECK(bl_state(&m,1,0,&out)==DA_RETURNED&&out.value==1);CHECK(!calls);
 s=source();put(SRC+2,4,1);CHECK(bl_state(&m,4,&s,&out)==DA_RETURNED&&out.value==4&&!calls);
 CHECK(bl_state(&m,0xffffffff,0,&out)==DA_RETURNED&&out.value==0xffffffff&&!calls);
 reset();CHECK(bl_advertise(&m,0x1234,&out)==DA_RETURNED&&adv==0x34&&out.known==0x00ff00ff);
 reset();m.storage.advertise=0;CHECK(bl_advertise(&m,1,&out)==DA_HALT&&!calls);
 reset();s.kind=BT_BORROWED;s.address=0;s.data=ram;s.known=known;s.available=2;CHECK(bl_state(&m,4,&s,&out)==DA_HALT&&!calls);
}
static void parameters(void){
 unsigned i;da_scalar out;uint32_t intervals[]={11,12,24,25,65548};++groups;
 for(i=0;i<5;i++){reset();put(GP+158,7,2);CHECK(bl_parameters(&m,7,intervals[i],0,200,&out)==DA_RETURNED);
 if(i==0||i==3){CHECK(updates==1&&last_task==3&&last_event==4&&last_delay==4800&&out.value==0xabcdef12);}else CHECK(!updates&&out.value==7&&out.known==UINT32_MAX);}
 reset();put(GP+158,65534,2);CHECK(bl_parameters(&m,65534,12,1,200,&out)==DA_RETURNED&&updates==1);
 reset();put(GP+158,7,2);CHECK(bl_parameters(&m,0x10007,11,0,200,&out)==DA_RETURNED&&!updates&&out.value==0x10007);
 reset();put(GP+162,7,2);CHECK(bl_parameters(&m,7,12,0,201,&out)==DA_RETURNED&&updates==1&&last_task==4);
}
static void registration(void){
 da_scalar out;++groups;reset();CHECK(bl_registration(&m,7,2,&out)==DA_RETURNED);CHECK(get(AUTH+2,2)==7&&get(AUTH+4,2)==0&&out.value==7);
 CHECK(bl_registration(&m,7,1,&out)==DA_RETURNED&&get(AUTH+4,1)==1);
 CHECK(bl_registration(&m,7,99,&out)==DA_RETURNED&&get(AUTH+2,2)==65534&&get(AUTH+4,2)==0);
 reset();put(AUTH+2,8,2);CHECK(bl_registration(&m,7,2,&out)==DA_RETURNED&&get(AUTH+6,2)==7);
 reset();put(AUTH+2,8,2);put(AUTH+6,9,2);CHECK(bl_registration(&m,7,2,&out)==DA_RETURNED&&get(AUTH+6,2)==9);
}
static void failures_and_prefix(void){
 unsigned t;bt_source s;da_scalar out;++groups;
 for(t=0;t<2;t++){reset();s=source();put(SRC+2,5,1);put(SRC+10,7,2);stop_site=0x8aaa;stop_flow=t?DA_TRANSFER:DA_HALT;
 CHECK(bl_state(&m,4,&s,&out)==stop_flow);CHECK(get(GP+158,2)==7&&mtu==0&&calls==1&&m.boundary_va==0x8aaa&&m.boundary_address==80);
 if(t){CHECK(bl_parameters(&m,7,30,0,200,&out)==DA_TRANSFER&&calls==1);}
 }
 reset();s=source();put(SRC+2,6,1);put(SRC+4,7,2);put(GP+158,7,2);stop_site=0x85da;
 CHECK(bl_state(&m,2,&s,&out)==DA_HALT);CHECK(get(GP+158,2)==65534&&m.boundary_va==0x85da&&m.boundary_address==372);
 reset();s=source();known[SRC-RAM+2]=0;CHECK(bl_state(&m,4,&s,&out)==DA_HALT&&!calls);
}
int main(void){connected();disconnected();noops_and_storage();parameters();registration();failures_and_prefix();printf("BLE_LIFECYCLE_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
