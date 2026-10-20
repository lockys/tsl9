#include "ble_role.h"
static da_flow callback_state(void*p,uint32_t state,const bt_source*s,da_scalar*out){return br_state((br_machine*)p,state,s,out);}
static da_flow callback_parameters(void*p,uint32_t h,uint32_t a,uint32_t b,uint32_t c,da_scalar*out){return br_parameters((br_machine*)p,h,a,b,c,out);}
/* This is our portable context-aware contract, NOT a resident-ROM wire table. */
static const br_callbacks callbacks={callback_state,0,callback_parameters};
static da_flow shared_read(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 br_machine*m=(br_machine*)p;return m->io&&m->io->runtime.core.read?m->io->runtime.core.read(m->io->runtime.core.context,a,n,need,site,out):DA_HALT;
}
static da_flow shared_write(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t known,uint32_t site){
 br_machine*m=(br_machine*)p;return m->io&&m->io->runtime.core.write?m->io->runtime.core.write(m->io->runtime.core.context,a,v,n,known,site):DA_HALT;
}
static da_flow core_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned count,da_scalar*out){
 br_machine*m=(br_machine*)p;return m->io&&m->io->runtime.core.call?m->io->runtime.core.call(m->io->runtime.core.context,kind,target,site,args,count,out):DA_HALT;
}
static da_flow core_schedule(void*p,uint32_t cb,uint32_t ticks,uint32_t site,da_scalar*out){
 br_machine*m=(br_machine*)p;return m->io&&m->io->runtime.core.schedule?m->io->runtime.core.schedule(m->io->runtime.core.context,cb,ticks,site,out):DA_HALT;
}
static da_flow report_call(void*p,const rp_request*r,rp_result*out){
 br_machine*m=(br_machine*)p;return m->io&&m->io->runtime.report_invoke?m->io->runtime.report_invoke(m->io->runtime.core.context,r,out):DA_HALT;
}
static da_flow lifecycle_call(void*p,const bl_request*r,da_scalar*out){
 br_machine*m=(br_machine*)p;return m->io&&m->io->lifecycle_invoke?m->io->lifecycle_invoke(m->io->runtime.core.context,r,out):DA_HALT;
}
static da_flow transport_call(void*p,const bt_request*r,bt_result*out){
 br_machine*m=(br_machine*)p;
 if(r->target==420){
  bt_request typed;unsigned i;
  if(r->argument_count!=3||r->arguments[2].known!=UINT32_MAX||r->arguments[2].value!=0x19a78||!m->io||!m->io->role_start){return DA_HALT;}
  typed.target=r->target;typed.callsite=r->callsite;typed.argument_count=3;typed.memory_effects_required=r->memory_effects_required;
  for(i=0;i<6;i++){typed.arguments[i].value=i<2?r->arguments[i].value:0;typed.arguments[i].known=i<2?r->arguments[i].known:0;}
  return m->io->role_start(m->io->runtime.core.context,&typed,&m->binding,out);
 }
 return m->io&&m->io->runtime.transport_invoke?m->io->runtime.transport_invoke(m->io->runtime.core.context,r,out):DA_HALT;
}
static int begin(br_machine*m,da_scalar*out){
 if(m->flow==DA_TRANSFER){return 0;}m->flow=DA_RETURNED;m->lifecycle_used=0;m->boundary_va=m->boundary_address=m->needed_mask=0;
 if(out){out->value=out->known=0;}return 1;
}
static da_flow finish(br_machine*m,da_flow flow){
 m->flow=flow;
 if(flow!=DA_RETURNED){
  if(m->lifecycle_used){m->boundary_va=m->lifecycle.boundary_va;m->boundary_address=m->lifecycle.boundary_address;m->needed_mask=m->lifecycle.needed_mask;}
  else{m->boundary_va=m->runtime.boundary_va;m->boundary_address=m->runtime.boundary_address;m->needed_mask=m->runtime.needed_mask;}
 }return flow;
}
void br_init(br_machine*m,const br_backend*io,rp_storage scratch,rp_storage dependency,bl_storage storage){
 m->io=io;m->runtime_backend.core.context=m;m->runtime_backend.core.read=shared_read;m->runtime_backend.core.write=shared_write;
 m->runtime_backend.core.call=core_call;m->runtime_backend.core.schedule=core_schedule;
 m->runtime_backend.report_invoke=report_call;m->runtime_backend.transport_invoke=transport_call;
 m->lifecycle_backend.context=m;m->lifecycle_backend.read=shared_read;m->lifecycle_backend.write=shared_write;m->lifecycle_backend.invoke=lifecycle_call;
 rtb_init(&m->runtime,&m->runtime_backend,scratch,dependency);bl_init(&m->lifecycle,&m->lifecycle_backend,storage);
 m->binding.callbacks=&callbacks;m->binding.context=m;m->binding.original_table_va=0x19a78;
 m->flow=DA_RETURNED;m->lifecycle_used=0;m->boundary_va=m->boundary_address=m->needed_mask=0;
}
da_flow br_run_pair(br_machine*m,uint32_t entry,uint32_t a0,uint32_t a1,da_scalar*out){
 if(!begin(m,out)){return m->flow;}return finish(m,rtb_run_pair(&m->runtime,entry,a0,a1,out));
}
da_flow br_events(br_machine*m,uint32_t task,uint32_t events,da_scalar*out){
 if(!begin(m,out)){return m->flow;}return finish(m,rtb_events(&m->runtime,task,events,out));
}
da_flow br_build(br_machine*m,uint32_t handle,uint32_t command,const bt_source*s,uint32_t length,da_scalar*out){
 if(!begin(m,out)){return m->flow;}return finish(m,rtb_build(&m->runtime,handle,command,s,length,out));
}
da_flow br_state(br_machine*m,uint32_t state,const bt_source*s,da_scalar*out){
 if(!begin(m,out)){return m->flow;}m->lifecycle_used=1;return finish(m,bl_state(&m->lifecycle,state,s,out));
}
da_flow br_parameters(br_machine*m,uint32_t h,uint32_t a,uint32_t b,uint32_t c,da_scalar*out){
 if(!begin(m,out)){return m->flow;}m->lifecycle_used=1;return finish(m,bl_parameters(&m->lifecycle,h,a,b,c,out));
}
da_flow br_registration(br_machine*m,uint32_t handle,uint32_t mode,da_scalar*out){
 if(!begin(m,out)){return m->flow;}m->lifecycle_used=1;return finish(m,bl_registration(&m->lifecycle,handle,mode,out));
}
