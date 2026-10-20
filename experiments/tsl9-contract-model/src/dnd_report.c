#include "dnd_report.h"
static da_flow shared_read(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar *out){
 dr_machine *m=(dr_machine *)p;
 return m->io&&m->io->core.read?m->io->core.read(m->io->core.context,a,n,need,site,out):DA_HALT;
}
static da_flow shared_write(void *p,uint32_t a,uint32_t value,unsigned n,uint32_t known,uint32_t site){
 dr_machine *m=(dr_machine *)p;
 return m->io&&m->io->core.write?m->io->core.write(m->io->core.context,a,value,n,known,site):DA_HALT;
}
static da_flow packet_invoke(void *p,const rp_request *r,rp_result *out){
 dr_machine *m=(dr_machine *)p;
 return m->io&&m->io->report_invoke?m->io->report_invoke(m->io->core.context,r,out):DA_HALT;
}
static da_flow packet_reply(void *p,const rp_reply *r){
 dr_machine *m=(dr_machine *)p;
 return m->io&&m->io->report_reply?m->io->report_reply(m->io->core.context,r):DA_HALT;
}
static da_flow local_packet(dr_machine *m,uint32_t argument,da_scalar *out){
 m->packet_invoked=1;if(out){out->value=0;out->known=0;}
 return rp_run_a0(&m->packet,argument);
}
static da_flow core_call(void *p,da_kind kind,uint32_t target,uint32_t site,const da_scalar *args,unsigned count,da_scalar *out){
 dr_machine *m=(dr_machine *)p;
 if(kind==DA_NATIVE&&target==0x13160){
  if(count!=1)return DA_HALT;
  return local_packet(m,args[0].value,out);
 }
 return m->io&&m->io->core.call?m->io->core.call(m->io->core.context,kind,target,site,args,count,out):DA_HALT;
}
static da_flow core_schedule(void *p,uint32_t cb,uint32_t ticks,uint32_t site,da_scalar *out){
 dr_machine *m=(dr_machine *)p;
 return m->io&&m->io->core.schedule?m->io->core.schedule(m->io->core.context,cb,ticks,site,out):DA_HALT;
}
void dr_init(dr_machine *m,const dr_backend *io,rp_storage scratch,rp_storage dependency){
 da_backend core;rp_backend packet;m->io=io;
 core.context=m;core.read=shared_read;core.write=shared_write;core.call=core_call;core.schedule=core_schedule;
 packet.context=m;packet.read=shared_read;packet.invoke=packet_invoke;packet.reply=packet_reply;
 da_init(&m->core,&core);rp_init(&m->packet,&packet,scratch,dependency);
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=0;m->packet_invoked=0;
}
da_flow dr_run_pair(dr_machine *m,uint32_t entry,uint32_t a0,uint32_t a1,da_scalar *out){
 if(m->flow==DA_TRANSFER)return m->flow;
 m->packet_invoked=0;m->boundary_va=m->boundary_address=m->needed_mask=0;
 if(out){out->value=0;out->known=0;}
 if(entry==0x13160)m->flow=local_packet(m,a0,out);
 else m->flow=da_run_pair(&m->core,entry,a0,a1,out);
 if(m->flow!=DA_RETURNED){
  if(m->packet_invoked&&m->packet.flow!=DA_RETURNED){
   m->boundary_va=m->packet.boundary_va;m->boundary_address=m->packet.boundary_address;m->needed_mask=m->packet.needed_mask;
  }else{m->boundary_va=m->core.boundary_va;m->boundary_address=m->core.boundary_address;}
 }
 return m->flow;
}
