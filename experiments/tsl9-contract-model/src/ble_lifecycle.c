#include "ble_lifecycle.h"
#define FULL UINT32_MAX
#define GP UINT32_C(0x20004000)
#define AUTH UINT32_C(0x2000c790)
static da_scalar value(uint32_t v){da_scalar s;s.value=v;s.known=FULL;return s;}
static void output(da_scalar*out,da_scalar v){if(out){out->value=v.value;out->known=v.known;}}
static int halt_at(bl_machine*m,uint32_t site,uint32_t address,uint32_t mask){
 m->flow=DA_HALT;m->boundary_va=site;m->boundary_address=address;m->needed_mask=mask;return 0;
}
static int effect(bl_machine*m,da_flow f,uint32_t site,uint32_t address){
 if(f==DA_RETURNED){return 1;}m->flow=f;m->boundary_va=site;m->boundary_address=address;m->needed_mask=0;return 0;
}
static int begin(bl_machine*m,da_scalar*out){
 if(m->flow==DA_TRANSFER){return 0;}m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->calls=m->reads=m->writes=0;
 if(out){out->value=out->known=0;}return 1;
}
static int read_s(bl_machine*m,uint32_t address,unsigned n,uint32_t site,da_scalar*out){
 uint32_t mask=n==4?FULL:(UINT32_C(1)<<(n*8))-1;out->value=out->known=0;++m->reads;
 if(!effect(m,m->io&&m->io->read?m->io->read(m->io->context,address,n,0,site,out):DA_HALT,site,address)){return 0;}
 out->value&=mask;out->known=(out->known&mask)|~mask;return 1;
}
static int write_s(bl_machine*m,uint32_t address,da_scalar v,unsigned n,uint32_t site){
 ++m->writes;return effect(m,m->io&&m->io->write?m->io->write(m->io->context,address,v.value,n,v.known,site):DA_HALT,site,address);
}
static int equal(bl_machine*m,da_scalar a,da_scalar b,uint32_t mask,uint32_t site,uint32_t address,int*out){
 if(((a.value^b.value)&a.known&b.known&mask)!=0){*out=0;return 1;}
 if((a.known&b.known&mask)!=mask){return halt_at(m,site,address,mask);}
 *out=1;return 1;
}
static void source_snapshot(bt_source*out,const bt_source*in){
 out->kind=in?in->kind:BT_BORROWED;out->address=in?in->address:0;
 out->data=in?in->data:0;out->known=in?in->known:0;out->available=in?in->available:0;
}
static int source_read(bl_machine*m,const bt_source*s,uint32_t offset,unsigned n,uint32_t site,da_scalar*out){
 unsigned i;uint32_t mask=n==4?FULL:(UINT32_C(1)<<(8*n))-1;
 if(s->kind==BT_MAPPED){return read_s(m,s->address+offset,n,site,out);}
 if(s->kind!=BT_BORROWED||!s->data||!s->known||offset>s->available||n>s->available-offset){return halt_at(m,site,0,mask);}
 out->value=0;out->known=~mask;
 for(i=0;i<n;i++){out->value|=(uint32_t)s->data[offset+i]<<(8*i);out->known|=(uint32_t)s->known[offset+i]<<(8*i);}return 1;
}
static int call(bl_machine*m,uint32_t target,uint32_t site,const da_scalar*args,unsigned count,int buffer,da_scalar*out){
 bl_request r;unsigned i;r.target=target;r.callsite=site;r.argument_count=count;
 r.byte=buffer==1?m->storage.advertise:0;r.byte_known=buffer==1?m->storage.advertise_known:0;
 r.half=buffer==2?m->storage.mtu:0;r.half_known=buffer==2?m->storage.mtu_known:0;
 m->last_request.target=target;m->last_request.callsite=site;m->last_request.argument_count=count;
 m->last_request.byte=r.byte;m->last_request.byte_known=r.byte_known;m->last_request.half=r.half;m->last_request.half_known=r.half_known;
 for(i=0;i<3;i++){
  r.arguments[i].value=i<count?args[i].value:0;r.arguments[i].known=i<count?args[i].known:0;
  m->last_request.arguments[i].value=r.arguments[i].value;m->last_request.arguments[i].known=r.arguments[i].known;
 }
 out->value=out->known=0;++m->calls;
 return effect(m,m->io&&m->io->invoke?m->io->invoke(m->io->context,&r,out):DA_HALT,site,target);
}
static int advertise(bl_machine*m,uint32_t raw,da_scalar*out){
 da_scalar args[3];if(!m->storage.advertise||!m->storage.advertise_known){return halt_at(m,0x85c2,0,255);}
 *m->storage.advertise=(uint8_t)raw;*m->storage.advertise_known=255;
 args[0]=value(773);args[1]=value(1);args[2].value=args[2].known=0;
 return call(m,372,0x85da,args,3,1,out);
}
static int registration(bl_machine*m,da_scalar handle,uint32_t mode,da_scalar*out){
 da_scalar h;uint32_t slot,base;int match;
 if(mode==2){
  if(!read_s(m,AUTH+2,2,0x13c4e,&h)||!equal(m,h,value(65534),FULL,0x13c56,AUTH+2,&match)){return 0;}
  if(match){slot=0;}else{
   if(!read_s(m,AUTH+6,2,0x13c5a,&h)||!equal(m,h,value(65534),FULL,0x13c5e,AUTH+6,&match)){return 0;}
   if(!match){output(out,handle);return 1;}slot=1;
  }
  base=AUTH+4*slot;
  if(!write_s(m,base+2,handle,2,0x13c68)||!write_s(m,base+4,value(0),1,0x13c6c)||!write_s(m,base+5,value(0),1,0x13c90)){return 0;}
 }else{
  uint32_t first_site=mode==1?0x13c42:0x13c36;
  if(!read_s(m,AUTH+2,2,first_site,&h)||!equal(m,h,handle,FULL,mode==1?0x13c46:0x13c3a,AUTH+2,&match)){return 0;}
  if(match){slot=0;}else{
   if(!read_s(m,AUTH+6,2,mode==1?0x13c7c:0x13c96,&h)||
      !equal(m,h,handle,FULL,mode==1?0x13c80:0x13c9a,AUTH+6,&match)){return 0;}
   if(!match){output(out,handle);return 1;}slot=1;
  }
  base=AUTH+4*slot;
  if(mode==1){if(!write_s(m,base+4,value(1),1,0x13c8c)){return 0;}}
  else if(!write_s(m,base+2,value(65534),2,0x13ca6)||!write_s(m,base+4,value(0),1,0x13c6c)){return 0;}
  if(!write_s(m,base+5,value(0),1,0x13c90)){return 0;}
 }
 output(out,handle);return 1;
}
void bl_init(bl_machine*m,const bl_backend*io,bl_storage storage){
 unsigned i;m->io=io;m->storage.advertise=storage.advertise;m->storage.advertise_known=storage.advertise_known;m->storage.mtu=storage.mtu;m->storage.mtu_known=storage.mtu_known;
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->calls=m->reads=m->writes=0;
 m->last_request.target=m->last_request.callsite=m->last_request.argument_count=0;
 m->last_request.byte=m->last_request.byte_known=0;m->last_request.half=m->last_request.half_known=0;
 for(i=0;i<3;i++){m->last_request.arguments[i].value=m->last_request.arguments[i].known=0;}
}
da_flow bl_advertise(bl_machine*m,uint32_t raw,da_scalar*out){
 da_scalar ret;if(!begin(m,out)){return m->flow;}if(advertise(m,raw,&ret)){output(out,ret);}return m->flow;
}
da_flow bl_registration(bl_machine*m,uint32_t handle,uint32_t mode,da_scalar*out){
 if(!begin(m,out)){return m->flow;}registration(m,value(handle),mode,out);return m->flow;
}
da_flow bl_state(bl_machine*m,uint32_t state,const bt_source*source,da_scalar*out){
 bt_source src;da_scalar h,slots,args[3],ret,task;uint32_t slot,base;int match;unsigned capacity;
 if(!begin(m,out)){return m->flow;}ret=value(state);
 if(state<2||state>4){output(out,ret);return m->flow;}
 source_snapshot(&src,source);
 if(!source_read(m,&src,2,1,state==4?0x8a58:0x8aea,&h)||
    !equal(m,h,value(state==4?5:6),255,state==4?0x8a5e:0x8af0,src.kind==BT_MAPPED?src.address+2:0,&match)){return m->flow;}
 if(!match){output(out,ret);return m->flow;}
 if(state==4){
  if(!read_s(m,GP+158,2,0x8a64,&slots)||!source_read(m,&src,10,2,0x8a6a,&h)||
     !equal(m,slots,value(65534),FULL,0x8a6e,GP+158,&match)){return m->flow;}
  if(match){slot=0;}else{
   if(!read_s(m,GP+162,2,0x8a72,&slots)||!equal(m,slots,value(65534),FULL,0x8a76,GP+162,&match)){return m->flow;}
   if(!match){args[0]=h;if(call(m,380,0x8a82,args,1,0,&ret)){output(out,ret);}return m->flow;}slot=1;
  }
  base=GP+156+4*slot;
  if(!write_s(m,base+2,h,2,0x8a9e)||!read_s(m,base,1,0x8aa4,&task)){return m->flow;}
  args[0]=task;args[1]=value(4);if(!call(m,80,0x8aaa,args,2,0,&ret)){return m->flow;}
  if(!m->storage.mtu||!m->storage.mtu_known){halt_at(m,0x8ab0,0,65535);return m->flow;}
  *m->storage.mtu=247;*m->storage.mtu_known=65535;
  if(!read_s(m,base,1,0x8ab4,&task)||!read_s(m,base+2,2,0x8abc,&h)){return m->flow;}
  args[0]=h;args[1].value=args[1].known=0;args[2]=task;
  if(!call(m,216,0x8ac2,args,3,2,&ret)||!read_s(m,GP+158,2,0x8ac6,&slots)||
     !equal(m,slots,value(65534),FULL,0x8ace,GP+158,&match)){return m->flow;}
  capacity=1;
  if(!match){if(!read_s(m,GP+162,2,0x8ad2,&slots)||!equal(m,slots,value(65534),FULL,0x8ad8,GP+162,&match)){return m->flow;}capacity=match?1u:0u;}
  if(advertise(m,capacity,&ret)){output(out,ret);}return m->flow;
 }
 if(!source_read(m,&src,4,2,0x8af4,&h)||!read_s(m,GP+158,2,0x8af8,&slots)||
    !equal(m,slots,h,FULL,0x8afc,GP+158,&match)){return m->flow;}
 if(match){slot=0;}else{
  if(!read_s(m,GP+162,2,0x8b00,&slots)||!equal(m,slots,h,FULL,0x8b04,GP+162,&match)){return m->flow;}
  if(!match){output(out,ret);return m->flow;}slot=1;
 }
 if(!write_s(m,GP+158+4*slot,value(65534),2,0x8b14)||!advertise(m,1,&ret)||
    !source_read(m,&src,4,2,0x8b1c,&h)){return m->flow;}
 registration(m,h,0,out);return m->flow;
}
da_flow bl_parameters(bl_machine*m,uint32_t handle,uint32_t interval,uint32_t latency,uint32_t timeout,da_scalar*out){
 da_scalar h,task,args[3],ret;uint32_t slot;int match;
 if(!begin(m,out)){return m->flow;}
 if(!read_s(m,GP+158,2,0x8778,&h)||!equal(m,h,value(handle),FULL,0x877c,GP+158,&match)){return m->flow;}
 if(match){slot=0;}else{
  if(!read_s(m,GP+162,2,0x8780,&h)||!equal(m,h,value(handle),FULL,0x8784,GP+162,&match)){return m->flow;}
  if(!match){output(out,value(handle));return m->flow;}slot=1;
 }
 if(((interval-12)&65535)<=12&&latency==0&&timeout==200){output(out,value(handle));return m->flow;}
 if(!read_s(m,GP+156+4*slot,1,0x87b0,&task)){return m->flow;}
 args[0]=task;args[1]=value(4);args[2]=value(4800);
 if(call(m,88,0x87bc,args,3,0,&ret)){output(out,ret);}return m->flow;
}
