#include "runtime_ble.h"
static da_flow shared_read(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->core.read?m->io->core.read(m->io->core.context,a,n,need,site,out):DA_HALT;
}
static da_flow shared_write(void*p,uint32_t a,uint32_t value,unsigned n,uint32_t known,uint32_t site){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->core.write?m->io->core.write(m->io->core.context,a,value,n,known,site):DA_HALT;
}
static da_flow core_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned count,da_scalar*out){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->core.call?m->io->core.call(m->io->core.context,kind,target,site,args,count,out):DA_HALT;
}
static da_flow core_schedule(void*p,uint32_t cb,uint32_t ticks,uint32_t site,da_scalar*out){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->core.schedule?m->io->core.schedule(m->io->core.context,cb,ticks,site,out):DA_HALT;
}
static da_flow report_call(void*p,const rp_request*r,rp_result*out){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->report_invoke?m->io->report_invoke(m->io->core.context,r,out):DA_HALT;
}
static da_flow transport_call(void*p,const bt_request*r,bt_result*out){
 rtb_machine*m=(rtb_machine*)p;return m->io&&m->io->transport_invoke?m->io->transport_invoke(m->io->core.context,r,out):DA_HALT;
}
static da_flow report_reply(void*p,const rp_reply*r){
 rtb_machine*m=(rtb_machine*)p;bt_source source;da_scalar ignored;
 if(r->wrapper_va!=0x8cfa){return DA_HALT;}
 source.kind=BT_BORROWED;source.address=0;source.data=r->data;source.known=r->known;source.available=r->length;
 m->transport_used=1;return bt_build(&m->transport,r->handle,r->command,&source,r->length,&ignored);
}
static int begin(rtb_machine*m,da_scalar*out){
 if(m->flow==DA_TRANSFER){return 0;}
 m->flow=DA_RETURNED;m->transport_used=0;m->boundary_va=m->boundary_address=m->needed_mask=0;
 if(out){out->value=out->known=0;}return 1;
}
static da_flow finish(rtb_machine*m,da_flow flow){
 m->flow=flow;
 if(flow!=DA_RETURNED){
  if(m->transport_used&&m->transport.flow!=DA_RETURNED){
   m->boundary_va=m->transport.boundary_va;m->boundary_address=m->transport.boundary_address;m->needed_mask=m->transport.needed_mask;
  }else{
   m->boundary_va=m->logic.boundary_va;m->boundary_address=m->logic.boundary_address;m->needed_mask=m->logic.needed_mask;
  }
 }return flow;
}
void rtb_init(rtb_machine*m,const rtb_backend*io,rp_storage scratch,rp_storage dependency){
 m->io=io;
 m->logic_backend.core.context=m;m->logic_backend.core.read=shared_read;m->logic_backend.core.write=shared_write;
 m->logic_backend.core.call=core_call;m->logic_backend.core.schedule=core_schedule;
 m->logic_backend.report_invoke=report_call;m->logic_backend.report_reply=report_reply;
 m->transport_backend.context=m;m->transport_backend.read=shared_read;m->transport_backend.write=shared_write;m->transport_backend.invoke=transport_call;
 dr_init(&m->logic,&m->logic_backend,scratch,dependency);bt_init(&m->transport,&m->transport_backend);
 m->flow=DA_RETURNED;m->transport_used=0;m->boundary_va=m->boundary_address=m->needed_mask=0;
}
da_flow rtb_run_pair(rtb_machine*m,uint32_t entry,uint32_t a0,uint32_t a1,da_scalar*out){
 if(!begin(m,out)){return m->flow;}return finish(m,dr_run_pair(&m->logic,entry,a0,a1,out));
}
da_flow rtb_events(rtb_machine*m,uint32_t task,uint32_t events,da_scalar*out){
 if(!begin(m,out)){return m->flow;}m->transport_used=1;return finish(m,bt_events(&m->transport,task,events,out));
}
da_flow rtb_build(rtb_machine*m,uint32_t handle,uint32_t command,const bt_source*source,uint32_t length,da_scalar*out){
 if(!begin(m,out)){return m->flow;}m->transport_used=1;return finish(m,bt_build(&m->transport,handle,command,source,length,out));
}
