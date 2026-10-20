#include "dnd_actions.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP UINT32_C(0x20004000)
#define CFG UINT32_C(0x2000c298)
#define AUTH UINT32_C(0x2000c790)
#define HEAP UINT32_C(0x2000d000)
#define FULL UINT32_MAX
#define MMREAD ((da_kind)2)
#define MMWRITE ((da_kind)3)
typedef struct {da_kind kind;uint32_t target,site;da_scalar a[4];unsigned n;} effect;
static uint8_t bytes[65536],bits[65536];
static da_machine machine;static da_backend backend;static effect logbook[256];
static unsigned logs,schedules,groups,checks,failures;static uint32_t cb,delay,fail_site,clock_raw,clock_known;
static da_scalar allocation,schedule_result,native_result,mmio_state;static int transfer_stop;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,uint32_t k,unsigned n){unsigned i;for(i=0;i<n;i++){bytes[a-RAM+i]=(uint8_t)(v>>(8*i));bits[a-RAM+i]=(uint8_t)(k>>(8*i));}}
static uint32_t get(uint32_t a,unsigned n){uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)bytes[a-RAM+i]<<(i*8);return v;}
static uint32_t known(uint32_t a,unsigned n){uint32_t k=0;unsigned i;for(i=0;i<n;i++)k|=(uint32_t)bits[a-RAM+i]<<(i*8);return k;}
static da_flow stop(uint32_t site){return site==fail_site?(transfer_stop?DA_TRANSFER:DA_HALT):DA_RETURNED;}
#ifdef DA_EFFECTS_API_VERSION
static da_flow read_ram(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar *out){
 (void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;
 out->value=get(a,n);out->known=known(a,n);return (out->known&need)==need?DA_RETURNED:DA_HALT;
}
static da_flow write_ram(void *p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 (void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;put(a,v,k,n);return DA_RETURNED;
}
static da_flow call(void *p,da_kind kind,uint32_t target,uint32_t site,const da_scalar *a,unsigned n,da_scalar *out){
#else
static da_flow read_ram(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,uint32_t *out){
 (void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;*out=get(a,n);return (known(a,n)&need)==need?DA_RETURNED:DA_HALT;
}
static da_flow write_ram(void *p,uint32_t a,uint32_t v,unsigned n,uint32_t site){
 (void)p;if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;put(a,v,FULL,n);return DA_RETURNED;
}
static da_flow call(void *p,da_kind kind,uint32_t target,uint32_t site,const uint32_t *args,unsigned n,da_scalar *out){
 da_scalar a[4];unsigned j;for(j=0;j<n;j++){a[j].value=args[j];a[j].known=FULL;}
#endif
 unsigned i;(void)p;if(logs<256){effect *r=&logbook[logs++];r->kind=kind;r->target=target;r->site=site;r->n=n;for(i=0;i<n&&i<4;i++)r->a[i]=a[i];}
 if(stop(site)!=DA_RETURNED)return stop(site);out->value=out->known=0;
 if(kind==DA_ROM&&target==112){CHECK(n==1);*out=allocation;return DA_RETURNED;}
 if(kind==DA_ROM&&target==104)return DA_RETURNED;
 if(kind==DA_ROM&&target==124){out->value=clock_raw;out->known=clock_known;return DA_RETURNED;}
 if(kind==DA_ROM&&(target==56||target==88||target==92)){out->value=0;out->known=FULL;return DA_RETURNED;}
 if(kind==DA_NATIVE&&target==0x13160){CHECK(n==1&&a[0].value==0&&a[0].known==FULL);*out=native_result;return DA_RETURNED;}
 if(kind==MMREAD){CHECK(target==0x40000400&&n==1&&a[0].value==16);*out=mmio_state;return DA_RETURNED;}
 if(kind==MMWRITE){CHECK(n==2&&a[1].value==16&&a[1].known==FULL);return DA_RETURNED;}
 return DA_HALT;
}
#ifdef DA_EFFECTS_API_VERSION
static da_flow schedule(void *p,uint32_t callback,uint32_t ticks,uint32_t site,da_scalar *out){
#else
static da_flow schedule(void *p,uint32_t callback,uint32_t ticks,uint32_t site){
#endif
 (void)p;++schedules;cb=callback;delay=ticks;
#ifdef DA_EFFECTS_API_VERSION
 if(out)*out=schedule_result;
#endif
 return stop(site);
}
static void fixture(void){
 memset(bytes,0,sizeof(bytes));memset(bits,255,sizeof(bits));memset(bytes+HEAP-RAM,0xa5,256);memset(logbook,0,sizeof(logbook));
 put(GP+84,CFG,FULL,4);put(AUTH+2,65534,FULL,2);put(AUTH+6,65534,FULL,2);
 backend.context=0;backend.read=read_ram;backend.write=write_ram;backend.call=call;backend.schedule=schedule;da_init(&machine,&backend);
 logs=schedules=0;cb=delay=fail_site=0;transfer_stop=0;allocation.value=HEAP;allocation.known=FULL;
 clock_raw=100;clock_known=FULL;schedule_result.value=0x55555555;schedule_result.known=0x00ff00ff;
 native_result.value=0x13579bdf;native_result.known=0x0f0f0f0f;mmio_state.value=0xa55a;mmio_state.known=65535;
}
static da_flow run(uint32_t entry,uint32_t arg,da_scalar *out){return da_run_pair(&machine,entry,arg,0,out);}
static void entries_and_clock(void){
 static const uint32_t entries[]={0x9432,0x93ee,0x9388,0x93cc,0x13b5c,0x133fa,0x81b0,0x13156};
 static const uint32_t raw[]={0,1,3,4,0x7fffffff,0x80000000,0xffffffff};unsigned i;da_scalar out;++groups;
 for(i=0;i<sizeof(entries)/sizeof(entries[0]);i++)CHECK(da_recognizes(entries[i]));
 for(i=0;i<sizeof(raw)/sizeof(raw[0]);i++){fixture();clock_raw=raw[i];CHECK(run(0x81b0,0,&out)==DA_RETURNED);CHECK(out.value==(uint32_t)(raw[i]*UINT32_C(10))/16u&&out.known==FULL);}
 fixture();clock_known=0x7fffffff;CHECK(run(0x81b0,0,&out)==DA_RETURNED);CHECK(out.value==62&&out.known==FULL);
 fixture();clock_known=0x3fffffff;CHECK(run(0x81b0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x81ba);
}
static void pulse_payloads(void){unsigned n,i;da_scalar out;++groups;
 for(n=0;n<=19;n++){fixture();CHECK(run(0x9432,n,&out)==DA_RETURNED);CHECK(out.value==HEAP&&out.known==FULL);CHECK(logs==1&&logbook[0].target==112&&logbook[0].a[0].value==(n+1)*6);
  for(i=0;i<n;i++){CHECK(get(HEAP+i*6,2)==3000);CHECK(get(HEAP+i*6+2,2)==40);CHECK(get(HEAP+i*6+4,2)==80);}
  CHECK(get(HEAP+n*6,2)==0);CHECK(get(HEAP+n*6+2,4)==0xa5a5a5a5);
 }
 {const uint32_t values[]={20,250,65536,0x80000000,0xffffffff};for(i=0;i<5;i++){fixture();CHECK(run(0x9432,values[i],&out)==DA_RETURNED);CHECK(logbook[0].a[0].value==12);CHECK(get(HEAP,2)==3000&&get(HEAP+2,2)==(values[i]&65535));CHECK(get(HEAP+4,4)==0&&get(HEAP+8,4)==0xa5a5a5a5);}}
}
static void pulse_null_and_known_prefix(void){da_scalar out;++groups;fixture();allocation.value=0;bits[GP+84-RAM]=0;
 CHECK(run(0x9432,20,&out)==DA_RETURNED);CHECK(get(0x2000becc,4)==0&&known(0x2000becc,4)==FULL&&logs==1);
 fixture();allocation.known=0;CHECK(run(0x9432,20,&out)==DA_HALT);CHECK(machine.boundary_va==0x94a8&&get(0x2000becc,4)==HEAP&&known(0x2000becc,4)==0);
 fixture();allocation.known=0x20000000;CHECK(run(0x9432,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x9478&&known(0x2000becc,4)==0x20000000);
}
static void pulse_cleanup_and_mmio(void){da_scalar out;++groups;fixture();put(0x2000becc,HEAP+128,FULL,4);put(0x2000bec8,777,FULL,4);put(CFG+2,1,FULL,1);put(0x2000bec0,9,FULL,1);
 CHECK(run(0x9432,1,&out)==DA_RETURNED);CHECK(logs==9&&logbook[0].target==104&&logbook[0].a[0].value==HEAP+128);
 CHECK(logbook[1].target==0x4000042c&&logbook[1].a[0].value==65535);CHECK(logbook[2].target==0x4000043c);
 CHECK(logbook[4].target==0x40000400&&logbook[4].a[0].value==(0xa55a&65534));CHECK(logbook[5].target==112);
 CHECK(get(0x2000bec8,4)==0&&get(0x2000bec2,1)==0&&get(0x2000bec1,1)==0&&get(0x2000bebc,4)==0);
 /* start adds 3 effects after allocation: the total is nine, checked below. */
 CHECK(logs==9&&logbook[8].target==0x40000400&&logbook[8].a[0].value==(0xa55a|1));
 fixture();put(CFG+2,0,0,1);put(0x2000bec0,1,1,1);mmio_state.known=0;CHECK(run(0x9388,99,&out)==DA_RETURNED);
 CHECK(logs==3&&logbook[2].a[0].known==1&&out.value==99&&out.known==FULL);
 fixture();put(0x2000becc,HEAP,0x20000000,4);CHECK(run(0x93ee,2,&out)==DA_RETURNED);CHECK(logbook[0].a[0].known==0x20000000);
}
static void pending_slots_and_results(void){da_scalar out;++groups;fixture();CHECK(run(0x133fa,123,&out)==DA_RETURNED);CHECK(out.value==0&&out.known==FULL&&schedules==0);
 fixture();put(AUTH+2,1,FULL,2);put(AUTH+5,1,FULL,1);put(AUTH+4,1,FULL,1);
 CHECK(run(0x13b5c,0,&out)==DA_RETURNED);CHECK(get(AUTH,1)==1&&schedules==1&&cb==0x13156&&delay==300);CHECK(out.value==1&&out.known==FULL&&logs==0);
 fixture();put(AUTH+2,1,FULL,2);put(AUTH+5,0,FULL,1);put(AUTH+6,2,FULL,2);put(AUTH+9,1,FULL,1);put(AUTH+8,1,FULL,1);
 CHECK(run(0x13b5c,0,&out)==DA_RETURNED);CHECK(schedules==2&&cb==0x13160&&delay==100);CHECK(out.value==schedule_result.value&&out.known==schedule_result.known);
 fixture();put(AUTH,7,FULL,1);CHECK(run(0x13156,0xaabbccdd,&out)==DA_RETURNED);CHECK(get(AUTH,1)==0&&out.value==0xaabbccdd&&out.known==FULL);
}
static void report_timing_and_wrap(void){unsigned delta;da_scalar out;++groups;
 for(delta=0;delta<=35;delta++){fixture();put(AUTH+2,1,FULL,2);put(AUTH+5,0,FULL,1);clock_raw=1600;put(GP+344,1000-delta,FULL,4);
  CHECK(run(0x13b5c,0,&out)==DA_RETURNED);
  if(delta<35){CHECK(schedules==1&&cb==0x13160&&delay==35&&logs==1);CHECK(out.value==schedule_result.value&&out.known==schedule_result.known);CHECK(get(GP+344,4)==1000-delta);}
  else{CHECK(schedules==0&&logs==2&&logbook[1].target==0x13160);CHECK(get(GP+344,4)==1000);CHECK(out.value==native_result.value&&out.known==native_result.known);}
 }
 fixture();put(AUTH+2,1,FULL,2);clock_raw=0;put(GP+344,0xfffffff0,FULL,4);CHECK(run(0x13b5c,0,&out)==DA_RETURNED);CHECK(delay==35);
}
static void failures_and_sticky_transfer(void){unsigned i,t;da_scalar out;
 const uint32_t sites[]={0x9408,0x940e,0x9416,0x93d2,0x93d6,0x93da,0x93e8,0x9430,0x9454,0x9488,0x948c,0x9490,0x9478,0x938c,0x938e,0x9396,0x93a2,0x93aa,0x93b2,0x93ba,0x93be,0x93c6};
 ++groups;for(t=0;t<2;t++)for(i=0;i<sizeof(sites)/sizeof(sites[0]);i++){fixture();put(0x2000becc,HEAP+128,FULL,4);put(CFG+2,1,FULL,1);fail_site=sites[i];transfer_stop=(int)t;
 CHECK(run(0x9432,1,&out)==(t?DA_TRANSFER:DA_HALT));CHECK(machine.boundary_va==sites[i]);if(t){unsigned previous=logs;CHECK(run(0x13156,0,&out)==DA_TRANSFER);CHECK(logs==previous);}}
 fixture();put(AUTH+2,1,FULL,2);fail_site=0x13bd6;transfer_stop=1;CHECK(run(0x13b5c,0,&out)==DA_TRANSFER);CHECK(machine.boundary_va==0x13bd6&&get(GP+344,4)==62);
}
static void integrated_core_effects(void){da_scalar out;unsigned i;++groups;fixture();put(GP+175,1,FULL,1);allocation.value=0;
 CHECK(da_run_pair(&machine,0x17048,256,1,&out)==DA_RETURNED);CHECK(logs==1&&logbook[0].target==112&&logbook[0].a[0].value==12);
 fixture();CHECK(da_run_pair(&machine,0x170e2,0,12,&out)==DA_RETURNED);CHECK(out.value==8&&out.known==FULL);
 for(i=0;i<logs;i++)CHECK(logbook[i].kind!=DA_NATIVE||logbook[i].target!=0x13b5c);
}
int main(void){entries_and_clock();pulse_payloads();pulse_null_and_known_prefix();pulse_cleanup_and_mmio();pending_slots_and_results();report_timing_and_wrap();failures_and_sticky_transfer();integrated_core_effects();printf("DND_EFFECTS_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
