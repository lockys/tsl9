#include "ram_bridge.h"
#include <stdio.h>
#include <string.h>
static tf_model ram;
static gh_model helper;
static gh_backend io;
static gh_request log_calls[64];
static unsigned groups,checks,failures,log_count,schedule_count;
static uint32_t rng_value,rng_known,registration_value,registration_known,stop_site;
static uint32_t last_cb,last_mode,last_delay,last_arg;
static int mutate_task,clear_jitter,transfer_call;
static int mutate_interval_task,mutate_cfg_pointer,unknown_status;
#define CFG UINT32_C(0x2000c298)
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t value,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(value>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static gb_flow invoke(void *p,gh_model *m,const gh_request *r,gb_scalar *v){
 (void)p;(void)m;if(log_count<64)log_calls[log_count++]=*r;
 if(r->callsite==stop_site)return transfer_call?GB_TRANSFER:GB_HALT;
  if(!(r->kind==GH_ROM&&(r->target==56||r->target==72||r->target==80||r->target==88||r->target==92||r->target==104||r->target==112||r->target==128)))return GB_HALT;
 v->value=0;v->known=UINT32_MAX;
 if(r->kind==GH_ROM&&r->target==56){v->value=rng_value;v->known=rng_known;if(clear_jitter)put(CFG+4,0,1);}
 if(r->kind==GH_ROM&&r->target==72){CHECK(r->argument_count==3&&r->arguments[0]==TF_GP+364&&r->arguments[1]==0&&r->arguments[2]==1);put(TF_GP+364,0,1);}
 if(r->kind==GH_ROM&&r->target==128){CHECK(r->argument_count==1&&r->arguments[0]==0x170e2);v->value=registration_value;v->known=registration_known;}
 if(r->callsite==0x170b6&&mutate_task)put(TF_GP+365,27,1);
 if(r->callsite==0x16fbc&&mutate_interval_task)put(TF_GP+365,27,1);
 if(r->kind==GH_ROM&&r->target==56&&mutate_cfg_pointer){put(TF_GP+84,0x2000c400,4);put(0x2000c403,10,1);put(0x2000c404,0,1);}
 if(r->kind==GH_ROM&&(r->target==80||r->target==88||r->target==92)&&unknown_status)v->known=0;
 return GB_RETURNED;
}
static gb_flow schedule(void *p,gh_model *m,uint32_t cb,uint32_t mode,uint32_t delay,uint32_t arg,gb_scalar *v){
 (void)p;(void)m;++schedule_count;last_cb=cb;last_mode=mode;last_delay=delay;last_arg=arg;v->known=0;v->value=0;
 return stop_site==0x170d0?GB_HALT:GB_RETURNED;
}
static void fixture(void){
 memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(&io,0,sizeof(io));memset(log_calls,0,sizeof(log_calls));
 put(TF_GP+84,CFG,4);put(TF_GP+175,1,1);put(TF_GP+365,9,1);put(0x2000bfb1,1,1);put(TF_GP+194,3,1);put(0x2000c792,65534,2);put(0x2000c796,65534,2);
 io.invoke=invoke;io.schedule=schedule;gh_init(&helper,&ram,&io);
 log_count=schedule_count=0;rng_value=1234;rng_known=registration_known=UINT32_MAX;registration_value=7;stop_site=0;mutate_task=clear_jitter=transfer_call=0;mutate_interval_task=mutate_cfg_pointer=unknown_status=0;last_cb=last_mode=last_delay=last_arg=0;
}
static gb_flow run(uint32_t entry,uint32_t a0,uint32_t a1,gb_scalar *out){
#ifdef GH_DND_CORE_API_VERSION
 return gh_dispatch_pair(&helper,entry,a0,a1,out);
#else
 /* Legacy API shim only permits observing a behavioral RED on R19. */
 (void)a1;return gh_dispatch(&helper,entry,a0,out);
#endif
}
static void disabled_does_not_read_config(void){gb_scalar out;++groups;fixture();ram.known[TF_GP+84-TF_RAM_BASE]=0;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(helper.recognized&&log_count==0);
 CHECK(run(0x17024,0,0,&out)==GB_RETURNED);CHECK(log_count==0);
}
static void interval_domain(void){unsigned n,j;uint32_t q;gb_scalar out;++groups;
 for(n=0;n<16;n++)for(j=0;j<2;j++)for(q=0;q<3;q++){
  uint32_t selected=n==15?1:n,base=selected<=1?2000:selected==2?3000:(selected-2)*5000,mod=selected<=1?1001:selected==2?2001:5001;
  fixture();put(TF_GP+364,1,1);put(CFG+3,n,1);put(CFG+4,j,1);rng_value=q==0?0:q==1?5000:UINT32_MAX;
  CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3);
  CHECK(log_calls[0].kind==GH_ROM&&log_calls[0].target==56&&log_calls[0].argument_count==0&&log_calls[0].callsite==0x16f80);
  CHECK(log_calls[1].target==88&&log_calls[1].argument_count==3&&log_calls[1].arguments[0]==9&&log_calls[1].arguments[1]==1&&log_calls[1].arguments[2]==((base+(j?rng_value%mod:0))*1000)/625);
  CHECK(log_calls[2].target==88&&log_calls[2].arguments[1]==4&&log_calls[2].arguments[2]==80);
 }
}
static void interval_unknown_and_gates(void){gb_scalar out;++groups;fixture();put(TF_GP+364,1,1);rng_known=0;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3&&log_calls[1].arguments[2]==3200);
 fixture();put(TF_GP+364,1,1);put(CFG+4,1,1);rng_known=0;
 CHECK(run(0x16f4a,0,0,&out)==GB_HALT);CHECK(log_count==1);
 fixture();put(TF_GP+364,1,1);put(CFG+4,1,1);rng_known=0;clear_jitter=1;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3);
 fixture();put(TF_GP+364,1,1);put(CFG+3,15,1);put(TF_GP+194,0,1); /*8214(1)==1*/
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==0);
 put(CFG+8,16,1);put(TF_GP+180,1,1);
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3);
 fixture();put(TF_GP+364,1,1);put(CFG+3,15,1);put(CFG+4,8,1);
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3); /*cfg4bit3 makes8214 return0*/
}
static void fullword_enable_and_admission(void){gb_scalar out;++groups;fixture();put(CFG+7,3,1);
 CHECK(run(0x17048,0x100,1,&out)==GB_RETURNED);CHECK(get(TF_GP+364,1)==0);
  CHECK(log_count==2&&log_calls[0].kind==GH_ROM&&log_calls[0].target==112&&log_calls[0].arguments[0]==12);
 CHECK(log_calls[1].target==88&&log_calls[1].arguments[1]==2&&log_calls[1].arguments[2]==2880000);
 fixture();put(TF_GP+364,7,1);put(TF_GP+175,0,1);ram.known[TF_GP+84-TF_RAM_BASE]=0;
 CHECK(run(0x17048,1,1,&out)==GB_RETURNED);CHECK(get(TF_GP+364,1)==7&&log_count==0);
 fixture();ram.known[TF_GP+175-TF_RAM_BASE]=0;
 CHECK(run(0x17048,1,0,&out)==GB_HALT);CHECK(helper.boundary_va==0x81aa&&get(TF_GP+364,1)==0);
}
static void disable_exact_prefix(void){gb_scalar out;++groups;fixture();put(TF_GP+364,1,1);put(0x2000bfb4,99,1);put(0x2000bf0c,11,1);put(TF_GP+187,88,1);ram.known[TF_GP+175-TF_RAM_BASE]=0;mutate_task=1;
 CHECK(run(0x17048,0,0,&out)==GB_RETURNED);CHECK(log_count==2&&log_calls[0].target==92&&log_calls[0].arguments[1]==2&&log_calls[0].arguments[0]==9);
 CHECK(log_calls[1].target==92&&log_calls[1].arguments[1]==1&&log_calls[1].arguments[0]==27);
 CHECK(schedule_count==1&&last_cb==0x13b5c&&last_mode==0&&last_delay==20&&last_arg==0);
 CHECK(get(TF_GP+364,1)==0&&get(0x2000bfb4,1)==0&&get(0x2000bf0c,1)==11&&get(TF_GP+187,1)==88);
 fixture();put(0x2000bfb4,99,1);stop_site=0x170c0;
 CHECK(run(0x17048,0,0,&out)==GB_HALT);CHECK(get(0x2000bfb4,1)==99&&schedule_count==0);
 fixture();put(0x2000bfb4,99,1);stop_site=0x170d0;
 CHECK(run(0x17048,0,0,&out)==GB_HALT);CHECK(get(0x2000bfb4,1)==99&&schedule_count==1);
}
static void clear_uses_precise_cancel_order(void){gb_scalar out;++groups;fixture();put(0x2000bfb4,9,1);put(0x2000be0c,0x1049a,4);put(0x2000be10,0,4);ram.known[TF_GP+174-TF_RAM_BASE]=0;
 CHECK(run(0x1049a,0,0,&out)==GB_HALT);CHECK(get(0x2000bfb4,1)==0&&get(0x2000be0c,4)==0x1049a&&get(0x2000be10,4)==0);
 CHECK(helper.boundary_va==0x90d0);
}
static void task_priority_and_disabled_reaches_action(void){uint32_t masks[]={7,9,UINT32_C(0x80000009),8,0};unsigned i;gb_scalar out;++groups;
 for(i=0;i<5;i++){fixture();put(CFG+3,15,1);put(CFG+8,14,1);
  CHECK(run(0x170e2,0xdeadbeef,masks[i],&out)==GB_RETURNED);
  CHECK(out.known==UINT32_MAX&&out.value==((masks[i]&1)?masks[i]^1:0));
  CHECK(log_count==0);
  if(masks[i]&1)CHECK(get(TF_GP+187,1)==3&&get(0x2000bf0c,1)==1);
 }
 fixture();put(CFG+8,14,1);put(0x2000bfb1,2,1);
 CHECK(run(0x170e2,0,1,&out)==GB_RETURNED);CHECK(schedule_count==1&&last_cb==0x1049a&&last_delay==14000);
 fixture();put(CFG+8,9,1);put(CFG+9,3,1);stop_site=0xa1c2;
 CHECK(run(0x170e2,0,1,&out)==GB_HALT);CHECK(out.known==0&&helper.boundary_va==0xa1c2&&get(TF_GP+187,1)==9);
}
static void task_event2_observation_gate(void){gb_scalar out;++groups;fixture();put(TF_GP+364,1,1);put(CFG+4,16,1);put(0x2000bee0,2,1);
 CHECK(run(0x170e2,0,6,&out)==GB_RETURNED);CHECK(out.value==4&&out.known==UINT32_MAX&&get(TF_GP+364,1)==1&&log_count==0);
 fixture();put(CFG+4,16,1);ram.known[0xbee0]=0;
 CHECK(run(0x170e2,0,2,&out)==GB_HALT);CHECK(helper.boundary_va==0xab16);
 fixture();put(CFG+4,0,1);ram.known[0xbee0]=0;
  CHECK(run(0x170e2,0,2,&out)==GB_RETURNED);CHECK(out.value==0&&log_count==3&&log_calls[0].target==112&&log_calls[0].arguments[0]==18);
}
static void task_init_raw_return_and_zero_boundary(void){gb_scalar out;++groups;fixture();put(TF_GP+364,55,1);registration_value=UINT32_MAX;
 CHECK(run(0x17176,0,0,&out)==GB_RETURNED);CHECK(get(TF_GP+364,1)==0&&get(TF_GP+365,1)==255&&log_count==2);
 fixture();registration_value=0xaabbcc42;registration_known=255;
 CHECK(run(0x17176,0,0,&out)==GB_RETURNED);CHECK(get(TF_GP+365,1)==0x42);
 fixture();registration_known=254;
 CHECK(run(0x17176,0,0,&out)==GB_HALT);CHECK(get(TF_GP+365,1)==9&&helper.boundary_va==0x1719a);
 fixture();put(TF_GP+364,55,1);stop_site=0x1718a;
 CHECK(run(0x17176,0,0,&out)==GB_HALT);CHECK(get(TF_GP+364,1)==55&&log_count==1);
 fixture();put(CFG+6,1,1);put(TF_GP+175,0,1);
 CHECK(run(0x17176,0,0,&out)==GB_RETURNED);CHECK(get(TF_GP+364,1)==0&&get(TF_GP+365,1)==7&&log_count==2);
}
static void post_event_and_missing_flow(void){gb_scalar out;++groups;fixture();put(TF_GP+364,2,1);
 CHECK(run(0x17024,0,0,&out)==GB_RETURNED);CHECK(log_count==1&&log_calls[0].target==80&&log_calls[0].arguments[0]==9&&log_calls[0].arguments[1]==1);
 fixture();put(TF_GP+364,1,1);io.invoke=NULL;gh_init(&helper,&ram,&io);
 CHECK(run(0x16f4a,0,0,&out)==GB_HALT);CHECK(helper.boundary_va==0x16f80);
 fixture();put(TF_GP+364,1,1);stop_site=0x16fbc;transfer_call=1;
 CHECK(run(0x16f4a,0,0,&out)==GB_TRANSFER);CHECK(run(0x17024,0,0,&out)==GB_TRANSFER);
}
static ta_model bridge;
static uint8_t image[76800];
static void bridge_a1_default_stops_after_known_enable(void){unsigned i;gb_flow f;++groups;
 ta_init(&bridge,TC_RUNTIME,image,sizeof(image),NULL,NULL,NULL);
 memset(bridge.memory.known,255,sizeof(bridge.memory.known));memset(bridge.memory.ram,0,sizeof(bridge.memory.ram));
 for(i=0;i<4;i++)bridge.memory.ram[0x4054+i]=(uint8_t)(CFG>>(8*i));
 bridge.memory.ram[0xc792]=7;bridge.memory.ram[0xc794]=1;bridge.memory.ram[0xc796]=0xfe;bridge.memory.ram[0xc797]=0xff;bridge.memory.ram[0x40af]=1;bridge.memory.ram[0xb9d8]=1;
 f=gb_dispatch(&bridge.general,7,0xa1,0x2000b9d8,1);
 CHECK(f==GB_HALT);CHECK(bridge.memory.ram[TF_GP+364-TF_RAM_BASE]==1);
#ifdef GH_DND_CORE_API_VERSION
 CHECK(bridge.helpers.boundary_va==0x16f80);CHECK(bridge.helpers.last_request.kind==GH_ROM&&bridge.helpers.last_request.target==56);
#else
 CHECK(0); /* Explicitly missing core routing, not a successful external stub. */
#endif
}
static unsigned bridge_rom_calls,bridge_alloc_calls;
static rc_adapter task_candidate;
static int register_candidate;
static int bridge_rng_missing;
static void bridge_put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){bridge.memory.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));bridge.memory.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t bridge_get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)bridge.memory.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static gb_flow bridge_core_provider(void *p,gh_model *h,const gh_request *r,gb_scalar *out){
 (void)p;(void)h;if(r->kind!=GH_ROM)return GB_HALT;++bridge_rom_calls;out->value=UINT32_MAX;out->known=UINT32_MAX;
 if(r->callsite==0xa1c2&&bridge_rng_missing)return GB_HALT;
 if(r->target==72){CHECK(r->argument_count==3);bridge_put(r->arguments[0],0,1);return GB_RETURNED;}
 if(r->target==128&&register_candidate){uint8_t task=255;if(!rc_task_register(&task_candidate,r->arguments[0],&task))return GB_HALT;out->value=task;return GB_RETURNED;}
 CHECK(r->target==56||r->target==88);return GB_RETURNED;
}
static cr_flow bridge_pulse_provider(void *p,cr_model *c,const cr_request *r,cr_result *out){
 (void)p;(void)c;++bridge_alloc_calls;CHECK(r->operation==CR_ALLOC);
 memset(out,0,sizeof(*out));out->known=UINT32_MAX;return CR_RETURNED; /* Explicit allocation failure0, not unknown. */
}
static void reset_bridge(void){unsigned i;
 ta_init(&bridge,TC_RUNTIME,image,sizeof(image),NULL,NULL,NULL);
 memset(bridge.memory.known,255,sizeof(bridge.memory.known));memset(bridge.memory.ram,0,sizeof(bridge.memory.ram));
 for(i=0;i<4;i++)bridge.memory.ram[0x4054+i]=(uint8_t)(CFG>>(8*i));
 bridge.memory.ram[0xc792]=7;bridge.memory.ram[0xc794]=1;bridge.memory.ram[0xc796]=0xfe;bridge.memory.ram[0xc797]=0xff;bridge.memory.ram[0x40af]=1;bridge.memory.ram[0xb9d8]=1;
 bridge_rom_calls=bridge_alloc_calls=0;register_candidate=0;
}
static void bridge_a1_with_typed_primitives(void){gh_backend h;cr_backend c;gb_flow f;++groups;reset_bridge();memset(&h,0,sizeof(h));memset(&c,0,sizeof(c));h.invoke=bridge_core_provider;c.invoke=bridge_pulse_provider;ta_set_helper_backend(&bridge,&h);ta_set_receive_backend(&bridge,&c);
 f=gb_dispatch(&bridge.general,7,0xa1,0x2000b9d8,1);
 CHECK(f==GB_RETURNED&&!bridge.halted);CHECK(bridge.memory.ram[0x416c]==1);CHECK(bridge_rom_calls==3&&bridge_alloc_calls==1);
}
static void bridge_clear_callback_is_known(void){unsigned i;uint32_t before;uint16_t remaining;++groups;reset_bridge();
 for(i=0;i<4;i++)bridge.memory.ram[0xbe0c+i]=(uint8_t)(UINT32_C(0x1049a)>>(8*i));
 bridge.memory.ram[0xbfb4]=4;before=bridge.memory.unknown_effects;remaining=ta_dispatch_runtime(&bridge,1);
 CHECK(remaining==0&&!bridge.halted);CHECK(bridge.memory.ram[0xbfb4]==0&&bridge.memory.unknown_effects==before);
}
static void task_event4_consumes_one_bit(void){gb_scalar out;++groups;fixture();
 CHECK(run(0x170e2,0,12,&out)==GB_RETURNED);CHECK(out.value==8&&out.known==UINT32_MAX);CHECK(log_count==0&&schedule_count==0);
}
static unsigned event_fallback_calls;
static int event_fallback(void *p,unsigned off,uint8_t task,uint16_t events,uint32_t ticks){
 (void)p;++event_fallback_calls;CHECK(off==80&&task==9&&events==1&&ticks==0);return 0;
}
static void bridge_post_event_uses_existing_provider(void){gb_scalar out;++groups;reset_bridge();event_fallback_calls=0;bridge.external_features.rom_status=event_fallback;bridge_put(TF_GP+364,1,1);bridge_put(TF_GP+365,9,1);
#ifdef GH_DND_CORE_API_VERSION
 CHECK(ta_dispatch_dnd(&bridge,0x17024,0,0,&out)==GB_RETURNED);CHECK(event_fallback_calls==1&&!bridge.halted);
#else
 (void)out;CHECK(0);
#endif
}
static int prepare_registered_task(void){gh_backend h;gb_scalar out;memset(&h,0,sizeof(h));h.invoke=bridge_core_provider;ta_set_helper_backend(&bridge,&h);
 if(!rc_attach(&task_candidate,&bridge.memory,RC_WCH_64BE955_V130,NULL)||!rc_prepare(&task_candidate,0x2000418c,0x7000,14)||!ta_attach_candidate(&bridge,&task_candidate))return 0;
 register_candidate=1;
#ifdef GH_DND_CORE_API_VERSION
 return ta_dispatch_dnd(&bridge,0x17176,0,0,&out)==GB_RETURNED;
#else
 (void)out;return 0;
#endif
}
static void registered_task_reaches_kernel(void){uint32_t task,base,status=99;int ready;++groups;reset_bridge();ready=prepare_registered_task();CHECK(ready);if(!ready)return;
 task=bridge_get(TF_GP+365,1);base=bridge_get(0x20003094,4);CHECK(task==3);
 bridge_put(CFG+4,16,1);bridge_put(0x2000bee0,1,1);bridge_put(TF_GP+364,1,1);
 CHECK(rc_set_event(&task_candidate,task,2,&status)==1&&status==0);CHECK(ta_system_process(&bridge)==RK_RETURNED);
 CHECK(!bridge.halted&&bridge.kernel.handlers==1&&bridge_get(base+task*2,2)==0&&bridge_get(TF_GP+364,1)==1);
}
static void registered_task_halts_at_missing_action(void){uint32_t task,base,status=99;int ready;++groups;bridge_rng_missing=0;reset_bridge();ready=prepare_registered_task();CHECK(ready);if(!ready)return;
 task=bridge_get(TF_GP+365,1);base=bridge_get(0x20003094,4);bridge_put(CFG+8,3,1);bridge_put(0x2000bfb1,1,1);
 CHECK(rc_set_event(&task_candidate,task,1,&status)==1&&status==0);CHECK(ta_system_process(&bridge)==RK_RETURNED);
 CHECK(!bridge.halted&&bridge_get(base+task*2,2)==0&&bridge_get(TF_GP+187,1)==3&&bridge_get(0x2000bf0c,1)==1);
 reset_bridge();ready=prepare_registered_task();CHECK(ready);if(!ready)return;bridge_rng_missing=1;bridge_put(CFG+9,3,1);bridge_put(0x2000bfb1,1,1);
 task=bridge_get(TF_GP+365,1);base=bridge_get(0x20003094,4);bridge_put(CFG+8,3,1);
 CHECK(rc_set_event(&task_candidate,task,1,&status)==1&&status==0);CHECK(ta_system_process(&bridge)==RK_HALT);
 CHECK(bridge.halted&&bridge_get(base+task*2,2)==0);CHECK(bridge.helpers.boundary_va==0xa1c2&&bridge.helpers.last_request.target==56&&bridge_get(TF_GP+187,1)==3);bridge_rng_missing=0;
}
static void interval_live_alias_and_unused_status(void){gb_scalar out;++groups;
 fixture();put(TF_GP+364,1,1);mutate_interval_task=1;unknown_status=1;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_count==3&&log_calls[1].arguments[0]==9&&log_calls[2].arguments[0]==27);
 fixture();put(TF_GP+364,1,1);put(CFG+3,2,1);put(CFG+4,1,1);rng_known=0;mutate_cfg_pointer=1;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_calls[1].arguments[2]==4800&&get(TF_GP+84,4)==0x2000c400);
 fixture();put(TF_GP+364,1,1);put(CFG+3,2,1);ram.known[CFG+3-TF_RAM_BASE]=15;ram.known[CFG+4-TF_RAM_BASE]=1;
 CHECK(run(0x16f4a,0,0,&out)==GB_RETURNED);CHECK(log_calls[1].arguments[2]==4800);
}
static void undeclared_native_entry_stops(void){gb_scalar out;++groups;fixture();
 CHECK(run(0xdeadbeef,0,0,&out)==GB_HALT);CHECK(!helper.recognized&&log_count==0);
}
int main(void){
 disabled_does_not_read_config();interval_domain();interval_unknown_and_gates();fullword_enable_and_admission();disable_exact_prefix();clear_uses_precise_cancel_order();task_priority_and_disabled_reaches_action();task_event2_observation_gate();task_init_raw_return_and_zero_boundary();post_event_and_missing_flow();bridge_a1_default_stops_after_known_enable();bridge_a1_with_typed_primitives();bridge_clear_callback_is_known();task_event4_consumes_one_bit();
 bridge_post_event_uses_existing_provider();registered_task_reaches_kernel();registered_task_halts_at_missing_action();
 interval_live_alias_and_unused_status();undeclared_native_entry_stops();
 printf("DND_CORE_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;
}
