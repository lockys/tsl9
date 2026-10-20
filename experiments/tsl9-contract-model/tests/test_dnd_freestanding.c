#include "dnd_actions.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP UINT32_C(0x20004000)
#define CFG UINT32_C(0x2000c298)
#define FULL UINT32_MAX
typedef struct{da_kind kind;uint32_t target,site,a[4];unsigned count;} call_record;
static uint8_t bytes[65536],known[65536];
static da_machine machine;static da_backend backend;
static call_record calls[64];static unsigned count,schedules,groups,checks,failures;
static uint32_t random_value,random_known,registration,registration_known,stop_site,mutation,last_cb,last_delay;
static int transfer_call;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){bytes[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)bytes[a-RAM+i]<<(8*i);return v;}
static da_flow stop(uint32_t site){return site==stop_site?(transfer_call?DA_TRANSFER:DA_HALT):DA_RETURNED;}
static da_flow read_ram(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar *out){
 uint32_t mask=0;unsigned i;(void)p;if(stop(site)!=DA_RETURNED)return stop(site);
 if(a<RAM||n>4||a>RAM+65536-n)return DA_HALT;out->value=get(a,n);
 for(i=0;i<n;i++)mask|=(uint32_t)known[a-RAM+i]<<(8*i);out->known=mask;return (mask&need)==need?DA_RETURNED:DA_HALT;
}
static da_flow write_ram(void *p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 unsigned i;(void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(a<RAM||n>4||a>RAM+65536-n)return DA_HALT;put(a,v,n);for(i=0;i<n;i++)known[a-RAM+i]=(uint8_t)(k>>(8*i));return DA_RETURNED;
}
static da_flow call(void *p,da_kind kind,uint32_t target,uint32_t site,const da_scalar *args,unsigned n,da_scalar *out){
 uint32_t a[4];unsigned j;for(j=0;j<n;j++)a[j]=args[j].value;
 unsigned i;(void)p;if(count<64){call_record *r=&calls[count++];r->kind=kind;r->target=target;r->site=site;r->count=n;for(i=0;i<n&&i<4;i++)r->a[i]=a[i];}
 if(stop(site)!=DA_RETURNED)return stop(site);out->value=out->known=0;
 if(kind==DA_ROM){
  if(target==56){out->value=random_value;out->known=random_known;if(mutation==1)put(CFG+4,0,1);}
  else if(target==72){CHECK(n==3&&a[0]==GP+364&&a[1]==0&&a[2]==1);put(a[0],0,1);}
  else if(target==128){CHECK(n==1&&a[0]==0x170e2);out->value=registration;out->known=registration_known;}
  else if(target==112){out->value=0;out->known=FULL;}
   else if(target!=80&&target!=88&&target!=92&&target!=104)return DA_HALT;
  if(site==0x170b6&&mutation==2)put(GP+365,27,1);
  if(site==0x16fbc&&mutation==3)put(GP+365,27,1);
  if(site==0x90bc&&mutation==4){put(GP+174,27,1);put(0x2000be0c,0xdead,4);}
 }else return DA_HALT;
 return DA_RETURNED;
}
static da_flow schedule(void *p,uint32_t cb,uint32_t delay,uint32_t site,da_scalar *out){
 (void)p;out->value=out->known=0;++schedules;last_cb=cb;last_delay=delay;return stop(site);
}
static void fixture(void){
 memset(bytes,0,sizeof(bytes));memset(known,255,sizeof(known));memset(calls,0,sizeof(calls));
 put(0x2000c792,65534,2);put(0x2000c796,65534,2);put(GP+84,CFG,4);put(GP+175,1,1);put(GP+365,9,1);put(GP+194,3,1);put(0x2000bfb1,1,1);
 backend.context=0;backend.read=read_ram;backend.write=write_ram;backend.call=call;backend.schedule=schedule;da_init(&machine,&backend);
 count=schedules=0;random_value=1234;random_known=registration_known=FULL;registration=7;stop_site=mutation=last_cb=last_delay=0;transfer_call=0;
}
static da_flow run(uint32_t entry,uint32_t a0,uint32_t a1,da_scalar *out){
#ifdef DA_CORE_API_VERSION
 return da_run_pair(&machine,entry,a0,a1,out);
#else
 (void)a1;return da_run(&machine,entry,a0,out);
#endif
}
static void disabled_is_lazy(void){da_scalar out;++groups;fixture();known[GP+84-RAM]=0;
 CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(count==0);
 CHECK(run(0x17024,0,0,&out)==DA_RETURNED);CHECK(count==0);
}
static void interval_domains(void){unsigned n,j,q;da_scalar out;++groups;
 for(n=0;n<16;n++)for(j=0;j<2;j++)for(q=0;q<3;q++){
  uint32_t selected=n==15?1:n,base=selected<=1?2000:selected==2?3000:(selected-2)*5000,mod=selected<=1?1001:selected==2?2001:5001;
  fixture();put(GP+364,1,1);put(CFG+3,n,1);put(CFG+4,j,1);random_value=q==0?0:q==1?5000:FULL;
  CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(count==3&&calls[0].target==56&&calls[0].site==0x16f80);
  CHECK(calls[1].target==88&&calls[1].count==3&&calls[1].a[0]==9&&calls[1].a[1]==1&&calls[1].a[2]==((base+(j?random_value%mod:0))*1000)/625);
  CHECK(calls[2].target==88&&calls[2].a[1]==4&&calls[2].a[2]==80);
 }
}
static void masks_live_reads_and_gates(void){da_scalar out;++groups;fixture();put(GP+364,1,1);random_known=0;
 CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(count==3);
 fixture();put(GP+364,1,1);put(CFG+4,1,1);random_known=0;CHECK(run(0x16f4a,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x16f9e&&count==1);
 fixture();put(GP+364,1,1);put(CFG+4,1,1);random_known=0;mutation=1;CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);
 fixture();put(GP+364,1,1);put(CFG+3,2,1);put(CFG+4,0,1);known[CFG+3-RAM]=15;known[CFG+4-RAM]=1;mutation=3;
 CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(calls[1].a[0]==9&&calls[2].a[0]==27);
 fixture();put(GP+364,1,1);put(CFG+3,15,1);put(GP+194,0,1);CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(count==0);
 put(CFG+8,16,1);put(GP+180,1,1);CHECK(run(0x16f4a,0,0,&out)==DA_RETURNED);CHECK(count==3);
}
static void raw_enable_and_feedback(void){da_scalar out;++groups;fixture();put(CFG+7,3,1);
 CHECK(run(0x17048,256,1,&out)==DA_RETURNED);CHECK(get(GP+364,1)==0);
 CHECK(count==2&&calls[0].kind==DA_ROM&&calls[0].target==112&&calls[0].a[0]==12);
 CHECK(calls[1].target==88&&calls[1].a[1]==2&&calls[1].a[2]==2880000);
 fixture();put(GP+175,0,1);known[GP+84-RAM]=0;CHECK(run(0x17048,1,1,&out)==DA_RETURNED);CHECK(count==0);
 fixture();known[GP+175-RAM]=0;CHECK(run(0x17048,1,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x81aa);
 fixture();known[GP+175-RAM]=0;CHECK(run(0x17048,0,0,&out)==DA_RETURNED);CHECK(count==2&&schedules==1);
}
static void disable_and_cleanup(void){da_scalar out;++groups;fixture();put(0x2000bfb4,99,1);put(0x2000bf0c,11,1);put(GP+187,88,1);mutation=2;
 CHECK(run(0x17048,0,0,&out)==DA_RETURNED);
 CHECK(count==2&&calls[0].target==92&&calls[0].a[0]==9&&calls[0].a[1]==2&&calls[1].a[0]==27&&calls[1].a[1]==1);
 CHECK(schedules==1&&last_cb==0x13b5c&&last_delay==20&&get(0x2000bfb4,1)==0);
 CHECK(get(0x2000bf0c,1)==11&&get(GP+187,1)==88);
 fixture();put(0x2000bfb4,99,1);stop_site=0x170c0;
 CHECK(run(0x17048,0,0,&out)==DA_HALT);CHECK(get(0x2000bfb4,1)==99&&schedules==0);
 fixture();put(0x2000bfb4,99,1);stop_site=0x170d0;transfer_call=1;
 CHECK(run(0x17048,0,0,&out)==DA_TRANSFER);CHECK(get(0x2000bfb4,1)==99&&schedules==1);
}
static void cancel_exact_order(void){da_scalar out;++groups;fixture();put(0x2000bfb4,9,1);put(0x2000be0c,0x1049a,4);put(0x2000be10,0x20006000,4);put(0x2000be18,0x1049a,4);mutation=4;
 CHECK(run(0x1049a,0,0,&out)==DA_RETURNED);CHECK(get(0x2000bfb4,1)==0&&get(0x2000be0c,4)==0&&get(0x2000be10,4)==0&&get(0x2000be18,4)==0x1049a);
 CHECK(count==2&&calls[0].target==104&&calls[1].target==92&&calls[1].a[0]==27&&calls[1].a[1]==1);
 fixture();put(0x2000bfb4,9,1);put(0x2000be0c,0x1049a,4);known[GP+174-RAM]=0;
 CHECK(run(0x1049a,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x90d0&&get(0x2000bfb4,1)==0&&get(0x2000be0c,4)==0x1049a);
 fixture();put(0x2000be0c,0x1049a,4);stop_site=0x90ec;CHECK(run(0x1049a,0,0,&out)==DA_HALT);CHECK(get(0x2000be0c,4)==0&&get(0x2000be10,4)==0);
}
static void task_pair_and_actions(void){static const uint32_t masks[]={0,1,2,4,7,UINT32_C(0x80000009)};unsigned i;da_scalar out;++groups;
 for(i=0;i<6;i++){fixture();put(CFG+8,9,1);put(CFG+4,16,1);put(0x2000bee0,1,1);
  CHECK(run(0x170e2,0xdeadbeef,masks[i],&out)==DA_RETURNED);
  CHECK(out.known==FULL&&out.value==((masks[i]&1)?masks[i]^1u:(masks[i]&2)?masks[i]^2u:(masks[i]&4)?masks[i]^4u:0));
  if(masks[i]&1)CHECK(get(GP+187,1)==9&&get(0x2000bf0c,1)==1);
  if((masks[i]&7)==4)CHECK(count==0); /* mode0 has no eligible handle; no external native edge */
 }
 fixture();put(CFG+3,15,1);put(CFG+8,14,1);CHECK(run(0x170e2,0,1,&out)==DA_RETURNED);CHECK(get(GP+187,1)==3);
 fixture();CHECK(da_run(&machine,0x170e2,7,&out)==DA_RETURNED);CHECK(out.known==FULL&&out.value==0);
}
static void initialization_return_words(void){static const uint32_t value[]={FULL,UINT32_C(0xaabbcc42),0};unsigned i;da_scalar out;++groups;
 for(i=0;i<3;i++){fixture();registration=value[i];registration_known=i==1?255u:FULL;put(GP+364,99,1);
  CHECK(run(0x17176,0,0,&out)==DA_RETURNED);CHECK(get(GP+364,1)==0&&get(GP+365,1)==(value[i]&255u));
  CHECK(count==2&&calls[1].target==128);
 }
 fixture();registration_known=254;CHECK(run(0x17176,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x1719a&&get(GP+365,1)==9);
 fixture();stop_site=0x1718a;put(GP+364,55,1);CHECK(run(0x17176,0,0,&out)==DA_HALT);CHECK(get(GP+364,1)==55);
}
static void nested_interval_is_local(void){da_scalar out;++groups;fixture();put(GP+364,1,1);
 CHECK(run(0xb57e,12,0,&out)==DA_RETURNED);CHECK(count==3&&calls[0].kind==DA_ROM&&calls[0].target==56&&get(0x2000bf0c,1)==12);
 fixture();put(GP+364,1,1);stop_site=0x16f80;CHECK(run(0xb57e,1,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x16f80&&get(0x2000bf0c,1)==0);
 fixture();put(GP+364,1,1);stop_site=0x16fd4;transfer_call=1;CHECK(run(0xb57e,1,0,&out)==DA_TRANSFER);CHECK(machine.boundary_va==0x16fd4);
 CHECK(run(0x17048,0,0,&out)==DA_TRANSFER);
}
int main(void){
 disabled_is_lazy();interval_domains();masks_live_reads_and_gates();raw_enable_and_feedback();disable_and_cleanup();cancel_exact_order();task_pair_and_actions();initialization_return_words();nested_interval_is_local();
 printf("DND_FREESTANDING_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;
}
