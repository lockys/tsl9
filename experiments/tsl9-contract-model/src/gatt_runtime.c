#include "gatt_runtime.h"
static da_flow callback_write(void*p,uint32_t h,const bt_source*a,const bt_source*v,uint32_t n,uint32_t fifth,da_scalar*out){
 return gr_write((gr_machine*)p,h,a,v,n,fifth,out);
}
/* Portable table, never cast to a physical resident-ROM callback structure. */
static const gr_callbacks callbacks={0,callback_write,0};
static void*context(gr_machine*m){return m->io?m->io->role.runtime.core.context:0;}
static da_flow shared_read(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.core.read?m->io->role.runtime.core.read(context(m),a,n,need,site,out):DA_HALT;
}
static da_flow shared_write(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.core.write?m->io->role.runtime.core.write(context(m),a,v,n,k,site):DA_HALT;
}
static da_flow core_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned n,da_scalar*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.core.call?m->io->role.runtime.core.call(context(m),kind,target,site,args,n,out):DA_HALT;
}
static da_flow core_schedule(void*p,uint32_t cb,uint32_t ticks,uint32_t site,da_scalar*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.core.schedule?m->io->role.runtime.core.schedule(context(m),cb,ticks,site,out):DA_HALT;
}
static da_flow report_call(void*p,const rp_request*r,rp_result*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.report_invoke?m->io->role.runtime.report_invoke(context(m),r,out):DA_HALT;
}
static da_flow transport_call(void*p,const bt_request*r,bt_result*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.runtime.transport_invoke?m->io->role.runtime.transport_invoke(context(m),r,out):DA_HALT;
}
static da_flow lifecycle_call(void*p,const bl_request*r,da_scalar*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.lifecycle_invoke?m->io->role.lifecycle_invoke(context(m),r,out):DA_HALT;
}
static da_flow role_start(void*p,const bt_request*r,const br_role_binding*b,bt_result*out){
 gr_machine*m=(gr_machine*)p;return m->io&&m->io->role.role_start?m->io->role.role_start(context(m),r,b,out):DA_HALT;
}
static da_flow gatt_call(void*p,const gp_request*r,da_scalar*out){
 gr_machine*m=(gr_machine*)p;
 if(r->kind==GP_ROM&&r->target==124)return core_call(m,DA_ROM,r->target,r->callsite,r->arguments,r->argument_count,out);
 return m->io&&m->io->gatt_invoke?m->io->gatt_invoke(context(m),r,out):DA_HALT;
}
static void close_children(gr_machine*m){m->role.flow=DA_TRANSFER;m->gatt.flow=DA_TRANSFER;}
static int begin(gr_machine*m,da_scalar*out,int path){
 /* A retained BR callback may have completed between public GR activations. */
 if(m->flow==DA_TRANSFER)return 0;
 if(m->role.flow==DA_TRANSFER){
  m->flow=DA_TRANSFER;m->boundary_va=m->role.boundary_va;m->boundary_address=m->role.boundary_address;m->needed_mask=m->role.needed_mask;close_children(m);return 0;
 }
 if(m->gatt.flow==DA_TRANSFER){
  m->flow=DA_TRANSFER;m->boundary_va=m->gatt.boundary_va;m->boundary_address=m->gatt.boundary_address;m->needed_mask=m->gatt.needed_mask;close_children(m);return 0;
 }
 m->flow=DA_RETURNED;m->path=path;m->boundary_va=m->boundary_address=m->needed_mask=0;
 if(out){out->value=out->known=0;}return 1;
}
static da_flow finish(gr_machine*m,da_flow flow){
 m->flow=flow;
 if(flow!=DA_RETURNED){
  if(m->path==1){m->boundary_va=m->gatt.boundary_va;m->boundary_address=m->gatt.boundary_address;m->needed_mask=m->gatt.needed_mask;}
  if(m->path==2){m->boundary_va=m->role.boundary_va;m->boundary_address=m->role.boundary_address;m->needed_mask=m->role.needed_mask;}
 }
 if(flow==DA_TRANSFER)close_children(m);return flow;
}
void gr_init(gr_machine*m,const gr_backend*io,rp_storage scratch,rp_storage dependency,bl_storage storage){
 m->io=io;m->role_backend.runtime.core.context=m;m->role_backend.runtime.core.read=shared_read;m->role_backend.runtime.core.write=shared_write;
 m->role_backend.runtime.core.call=core_call;m->role_backend.runtime.core.schedule=core_schedule;
 m->role_backend.runtime.report_invoke=report_call;m->role_backend.runtime.transport_invoke=transport_call;m->role_backend.lifecycle_invoke=lifecycle_call;m->role_backend.role_start=role_start;
 m->gatt_backend.context=m;m->gatt_backend.read=shared_read;m->gatt_backend.write=shared_write;m->gatt_backend.invoke=gatt_call;
 br_init(&m->role,&m->role_backend,scratch,dependency,storage);gp_init(&m->gatt,&m->gatt_backend);
 m->binding.callbacks=&callbacks;m->binding.context=m;m->binding.original_table_va=0x19a94;
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=0;m->path=0;
}
da_flow gr_write(gr_machine*m,uint32_t h,const bt_source*a,const bt_source*v,uint32_t n,uint32_t fifth,da_scalar*out){
 if(!begin(m,out,1))return m->flow;return finish(m,gp_write(&m->gatt,h,a,v,n,fifth,out));
}
da_flow gr_register_attributes(gr_machine*m,da_scalar*out){
 gr_registration_request r;da_scalar ret;da_flow f;unsigned i;
 if(!begin(m,out,3))return m->flow;
 r.target=304;r.callsite=0x8fa4;r.argument_count=4;
 for(i=0;i<4;i++){r.arguments[i].value=0;r.arguments[i].known=i<3?UINT32_MAX:0;}
 r.arguments[0].value=UINT32_C(0x20004000);r.arguments[1].value=4;r.arguments[2].value=16;ret.value=ret.known=0;
 f=m->io&&m->io->register_attributes?m->io->register_attributes(context(m),&r,&m->binding,&ret):DA_HALT;
 if(f!=DA_RETURNED){m->boundary_va=r.callsite;m->boundary_address=r.target;}
 else if(out){out->value=ret.value;out->known=ret.known;}
 return finish(m,f);
}
da_flow gr_run_pair(gr_machine*m,uint32_t e,uint32_t a,uint32_t b,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_run_pair(&m->role,e,a,b,out));
}
da_flow gr_events(gr_machine*m,uint32_t a,uint32_t b,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_events(&m->role,a,b,out));
}
da_flow gr_build(gr_machine*m,uint32_t h,uint32_t cmd,const bt_source*s,uint32_t n,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_build(&m->role,h,cmd,s,n,out));
}
da_flow gr_state(gr_machine*m,uint32_t state,const bt_source*s,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_state(&m->role,state,s,out));
}
da_flow gr_parameters(gr_machine*m,uint32_t h,uint32_t a,uint32_t b,uint32_t c,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_parameters(&m->role,h,a,b,c,out));
}
da_flow gr_registration(gr_machine*m,uint32_t h,uint32_t mode,da_scalar*out){
 if(!begin(m,out,2))return m->flow;return finish(m,br_registration(&m->role,h,mode,out));
}
