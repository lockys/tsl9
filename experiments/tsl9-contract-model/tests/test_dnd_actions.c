#include "ram_bridge.h"
#include <stdio.h>
#include <string.h>
#define CFG UINT32_C(0x2000c298)
#define CFG2 UINT32_C(0x2000c500)
#define FULL UINT32_MAX
static tf_model ram;
static gh_model helper;
static gh_backend backend;
static unsigned groups,checks,failures,calls,schedules;
static uint32_t rng,rng_known,cb,delay,stop_site,mutation;
static int transfer_call;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static void known(uint32_t a,uint8_t k){ram.known[a-TF_RAM_BASE]=k;}
static gb_flow invoke(void *p,gh_model *m,const gh_request *r,gb_scalar *out){
 (void)p;(void)m;++calls;
 if(r->callsite==stop_site)return transfer_call?GB_TRANSFER:GB_HALT;
 if(r->kind==GH_ROM&&r->target==124&&r->argument_count==0){out->value=100;out->known=FULL;return GB_RETURNED;}
 if(r->kind!=GH_ROM||r->target!=56||r->argument_count!=0)return GB_HALT;
 CHECK(r->callsite==0xa1c2);out->value=rng;out->known=rng_known;
 if(mutation==1){put(TF_GP+188,3,1);put(TF_GP+182,9,1);}
 if(mutation==2||mutation==3){put(TF_GP+84,CFG2,4);put(CFG2+3,mutation==3?15u:0u,1);put(CFG2+4,0,1);put(CFG2+5,3,1);}
 return GB_RETURNED;
}
static gb_flow schedule(void *p,gh_model *m,uint32_t callback,uint32_t mode,uint32_t ticks,uint32_t arg,gb_scalar *out){
 (void)p;CHECK(mode==0&&arg==0);++schedules;cb=callback;delay=ticks;out->value=0;out->known=0;
 return m->last_request.callsite==stop_site?(transfer_call?GB_TRANSFER:GB_HALT):GB_RETURNED;
}
static void fixture(void){
 memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(&backend,0,sizeof(backend));
 put(TF_GP+84,CFG,4);put(0x2000bfb1,1,1);backend.invoke=invoke;backend.schedule=schedule;
 gh_init(&helper,&ram,&backend);calls=schedules=0;cb=delay=stop_site=mutation=0;rng=0;rng_known=FULL;transfer_call=0;
}
static gb_flow run(uint32_t entry,uint32_t a){gb_scalar out;return gh_dispatch(&helper,entry,a,&out);}
static void other_modes_wrap_duration(void){
 unsigned mode,i;uint32_t raw[]={0,1,256,UINT32_MAX,UINT32_C(4294968)};++groups;
 for(mode=0;mode<256;mode++)if(mode!=1)for(i=0;i<5;i++){
  fixture();put(0x2000bfb1,mode,1);known(TF_GP+84,0);
  CHECK(run(0xa212,raw[i])==GB_RETURNED);CHECK(helper.recognized);
  CHECK(get(0x2000bfb4,1)==1&&schedules==1&&cb==0x1049a);
  CHECK(delay==(uint32_t)((raw[i]?raw[i]:1u)*UINT32_C(1000)));
 }
}
static void selector_flags(void){
 unsigned bits;++groups;
 for(bits=0;bits<4;bits++){
  fixture();put(CFG+5,bits,1);put(TF_GP+184,3,1);
  CHECK(run(0xa212,2)==GB_RETURNED);
  CHECK(get(TF_GP+187,1)==((bits==0||bits==2)?2u:0u));
  CHECK(get(0x2000bf0c,1)==((bits==0||bits==2)?1u:0u));
  CHECK(schedules==((bits==1||bits==2)?1u:0u));
  if(schedules)CHECK(cb==0x9e8e&&delay==2000&&get(TF_GP+183,1)==1&&get(TF_GP+184,1)==0);
 }
 fixture();put(CFG+5,3,1);known(TF_GP+180,0);known(TF_GP+195,0);CHECK(run(0xa212,9)==GB_RETURNED);
 fixture();put(CFG+5,1,1);put(CFG+3,15,1);CHECK(run(0xa212,8)==GB_RETURNED);CHECK(schedules==0);
}
static void zero_order_and_no_extra_reads(void){
 ++groups;fixture();put(CFG+5,1,1);known(TF_GP+195,0);
 CHECK(run(0xa212,0)==GB_HALT);CHECK(helper.boundary_va==0x8232&&schedules==0);
 fixture();put(CFG+5,1,1);put(TF_GP+195,3,1);known(CFG+3,0);
 CHECK(run(0xa212,1)==GB_RETURNED);CHECK(schedules==0);
 fixture();put(CFG+5,1,1);known(CFG+3,0);CHECK(run(0xa212,0)==GB_RETURNED);CHECK(schedules==0);
 fixture();put(CFG+5,1,1);put(CFG+4,8,1);known(TF_GP+195,0);CHECK(run(0xa212,1)==GB_RETURNED);
}
static void priority_four_stores(void){
 uint32_t a[]={1,256,UINT32_MAX};unsigned i;++groups;
 for(i=0;i<3;i++){fixture();put(TF_GP+180,2,1);put(0x2000bee0,7,1);known(TF_GP+84,0);
  CHECK(run(0xa128,a[i])==GB_RETURNED);CHECK(get(0x2000bf34,4)==UINT32_C(0x01000301));CHECK(get(TF_GP+187,1)==0&&calls==0);
 }
 fixture();put(TF_GP+180,1,1);known(0x2000bee0,0);CHECK(run(0xa128,0)==GB_RETURNED);
 fixture();put(TF_GP+180,1,1);put(0x2000bee0,0,1);CHECK(run(0xa128,1)==GB_RETURNED);CHECK(get(0x2000bf34,4)==0);
}
static void countdown_transition(void){
 unsigned count;static const uint8_t inputs[]={0,1,2,255};unsigned i;++groups;
 for(count=0;count<256;count++)for(i=0;i<4;i++){
  fixture();put(TF_GP+187,count,1);put(TF_GP+186,inputs[i],1);put(TF_GP+188,3,1);known(TF_GP+84,0);
  CHECK(run(0xa128,0)==GB_RETURNED);
  CHECK(get(TF_GP+187,1)==(count?count-1:0));
  CHECK(get(TF_GP+186,1)==(count==1?(inputs[i]?0u:1u):inputs[i]));
  CHECK(get(0x2000bf0c,1)==(count==1?(inputs[i]?12u:10u):0u));
 }
}
static void configured_actions_truth_table(void){
 /* Recorded branch outcomes, ordered cfg4 high2 / cfg9 low2 / old toggle. */
 static const uint8_t requests[4][2]={{1,3},{9,11},{9,11},{12,10}};
 unsigned high,low,old,block;++groups;
 for(high=0;high<4;high++)for(low=0;low<4;low++)for(old=0;old<2;old++)for(block=0;block<2;block++){
  uint32_t state=high==2?(old?0u:1u):high,value=low==0?0u:low==1?1u:low==2?old:1u,expected=state==0&&block?0u:requests[state][value];
  fixture();put(CFG+4,high<<6,1);put(CFG+9,low,1);put(TF_GP+188,old,1);put(TF_GP+186,old,1);put(TF_GP+182,block,1);rng=1;rng_known=1;
  CHECK(run(0xa128,256)==GB_RETURNED);CHECK(get(TF_GP+187,1)==0);
  CHECK(get(TF_GP+188,1)==state&&get(TF_GP+186,1)==value);
  CHECK(get(0x2000bf0c,1)==expected);CHECK(calls==(low==3?1u:0u));
 }
 fixture();put(TF_GP+187,9,1);known(TF_GP+84,0);CHECK(run(0xa128,1)==GB_RETURNED);CHECK(get(TF_GP+187,1)==9);
}
static void unknown_masks_and_exact_prefix(void){
 ++groups;fixture();put(CFG+4,64,1);put(CFG+9,1,1);known(CFG+4,192);known(CFG+9,3);
 CHECK(run(0xa128,7)==GB_RETURNED);CHECK(get(0x2000bf0c,1)==11);
 fixture();known(TF_GP+84,0);CHECK(run(0xa128,256)==GB_HALT);CHECK(get(TF_GP+187,1)==0&&helper.boundary_va==0xa15c);
 fixture();put(CFG+9,3,1);rng=1;rng_known=0;put(TF_GP+186,77,1);
 CHECK(run(0xa128,7)==GB_HALT);CHECK(get(TF_GP+187,1)==7&&get(TF_GP+186,1)==77&&get(0x2000bf0c,1)==0&&helper.boundary_va==0xa1c4);
 fixture();put(CFG+5,1,1);put(TF_GP+184,255,1);known(TF_GP+184,3);
 CHECK(run(0xa212,1)==GB_RETURNED);CHECK(get(TF_GP+184,1)==0);
}
static void provider_mutation_and_stop(void){
 ++groups;fixture();put(CFG+9,3,1);rng=1;rng_known=1;mutation=1;
 CHECK(run(0xa128,1)==GB_RETURNED);CHECK(get(0x2000bf0c,1)==10);
 fixture();put(CFG+5,2,1);put(CFG+9,3,1);rng=1;mutation=2;
 CHECK(run(0xa212,3)==GB_RETURNED);CHECK(schedules==1&&cb==0x9e8e&&delay==3000);
 fixture();put(CFG+5,2,1);put(CFG+9,3,1);rng=1;mutation=3;
 CHECK(run(0xa212,3)==GB_RETURNED);CHECK(schedules==0&&get(TF_GP+187,1)==3);
 fixture();put(CFG+4,192,1);put(CFG+9,3,1);stop_site=0xa1c2;
 CHECK(run(0xa128,7)==GB_HALT);CHECK(get(TF_GP+187,1)==7&&get(TF_GP+188,1)==3&&get(0x2000bf0c,1)==0);
 fixture();put(CFG+9,3,1);stop_site=0xa1c2;transfer_call=1;CHECK(run(0xa128,1)==GB_TRANSFER);
 CHECK(get(TF_GP+187,1)==1&&get(0x2000bf0c,1)==0);
}
static void schedule_failure_keeps_prefix(void){
 ++groups;fixture();put(CFG+5,1,1);put(TF_GP+184,2,1);stop_site=0xa284;
 CHECK(run(0xa212,UINT32_MAX)==GB_HALT);CHECK(get(TF_GP+184,1)==3&&get(TF_GP+183,1)==1&&schedules==1&&delay==UINT32_C(4294966296));
 fixture();put(0x2000bfb1,2,1);stop_site=0x106b4;transfer_call=1;
 CHECK(run(0xa212,0)==GB_TRANSFER);CHECK(get(0x2000bfb4,1)==1&&schedules==1&&delay==1000);
}
static void b57e_raw_guard_and_refresh(void){
 static const uint32_t raw[]={0,1,11,12,17,18,19,256,257,UINT32_C(0xffffff01)};unsigned i;++groups;
 for(i=0;i<10;i++){
  int admitted=((raw[i]-1u)&255u)<=17u;
  fixture();put(CFG+8,16,1);put(0x2000bee0,1,1);put(TF_GP+180,7,1);
  CHECK(run(0xb57e,raw[i])==GB_RETURNED);CHECK(get(0x2000bf0c,1)==(admitted?(raw[i]&255u):0u));
  CHECK(schedules==(admitted&&(raw[i]<=11||raw[i]==18)?1u:0u));
  CHECK(get(TF_GP+180,1)==(admitted&&(raw[i]<=11||raw[i]==18)?0u:7u));
  if(schedules)CHECK(cb==0x9e94&&delay==10000);
 }
 fixture();put(CFG+8,16,1);put(0x2000bee0,1,1);put(0x2000bf0c,77,1);stop_site=0x9f1a;
 CHECK(run(0xb57e,1)==GB_HALT);CHECK(get(TF_GP+180,1)==0&&get(0x2000bf0c,1)==77);
}
static void refresh_and_clear_callbacks(void){
 ++groups;fixture();put(TF_GP+183,1,1);known(TF_GP+84,0);CHECK(run(0x9e8e,123)==GB_RETURNED);CHECK(get(TF_GP+183,1)==0);
 fixture();put(CFG+8,16,1);put(0x2000bee0,1,1);put(TF_GP+354,2,1);
 CHECK(run(0x9e94,0)==GB_RETURNED);CHECK(get(TF_GP+180,1)==1);
 fixture();put(TF_GP+354,3,1);put(CFG+8,16,1);put(0x2000bee0,1,1);CHECK(run(0x9e94,0)==GB_RETURNED);CHECK(get(TF_GP+180,1)==0);
}
static void nested_interval_boundary_is_preserved(void){
 ++groups;fixture();put(TF_GP+364,1,1);put(TF_GP+180,7,1);stop_site=0x16f80;
 CHECK(run(0xb57e,1)==GB_HALT);CHECK(helper.boundary_va==0x16f80);
 CHECK(get(TF_GP+180,1)==7&&get(0x2000bf0c,1)==0);
 fixture();put(TF_GP+364,1,1);stop_site=0x16f80;transfer_call=1;
 CHECK(run(0xb57e,1)==GB_TRANSFER);CHECK(helper.boundary_va==0x16f80);
}
static void report_primitive_boundary_is_preserved(void){
 uint32_t sites[]={0x81ba,0x13bd6};unsigned i,t;gb_scalar out;++groups;
 for(i=0;i<2;i++)for(t=0;t<2;t++){
  fixture();stop_site=sites[i];transfer_call=(int)t;
  CHECK(gh_dispatch_pair(&helper,0x170e2,0,4,&out)==(t?GB_TRANSFER:GB_HALT));
  CHECK(helper.boundary_va==sites[i]&&get(TF_GP+344,4)==(i?62u:0u));
  CHECK(helper.last_request.callsite==sites[i]&&out.known==0);
 }
}
static void default_bridge_task_reaches_actions(void){
 static ta_model model;gb_scalar out;++groups;memset(&model,0,sizeof(model));model.ota.image=TC_RUNTIME;
 memset(model.memory.known,255,sizeof(model.memory.known));
 model.memory.ram[TF_GP+84-TF_RAM_BASE]=(uint8_t)(CFG&255u);model.memory.ram[TF_GP+85-TF_RAM_BASE]=(uint8_t)((CFG>>8)&255u);model.memory.ram[TF_GP+86-TF_RAM_BASE]=(uint8_t)((CFG>>16)&255u);model.memory.ram[TF_GP+87-TF_RAM_BASE]=(uint8_t)((CFG>>24)&255u);
 model.memory.ram[0xbfb1]=1;model.memory.ram[CFG+8-TF_RAM_BASE]=7;
 ta_set_helper_backend(&model,NULL);
 CHECK(ta_dispatch_dnd(&model,0x170e2,0,1,&out)==GB_RETURNED);
 CHECK(out.known==FULL&&out.value==0&&model.memory.ram[TF_GP+187-TF_RAM_BASE]==7&&model.memory.ram[0xbf0c]==1);
 model.memory.ram[TF_GP+183-TF_RAM_BASE]=1;model.memory.ram[0xbe0c]=0x8e;model.memory.ram[0xbe0d]=0x9e;
 CHECK(ta_dispatch_runtime(&model,1)==0);CHECK(model.memory.ram[TF_GP+183-TF_RAM_BASE]==0);
 CHECK(model.memory.ram[0xbe0c]==0&&model.memory.ram[0xbe0d]==0&&model.memory.unknown_effects==0);
}
int main(void){
 other_modes_wrap_duration();selector_flags();zero_order_and_no_extra_reads();priority_four_stores();countdown_transition();configured_actions_truth_table();unknown_masks_and_exact_prefix();provider_mutation_and_stop();schedule_failure_keeps_prefix();b57e_raw_guard_and_refresh();refresh_and_clear_callbacks();default_bridge_task_reaches_actions();
 nested_interval_boundary_is_preserved();
 report_primitive_boundary_is_preserved();
 printf("DND_ACTIONS_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;
}
