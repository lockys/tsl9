#include "ble_transport.h"
#define FULL UINT32_MAX
#define A(n) (UINT32_C(0x20004000)+(n))
static da_scalar literal(uint32_t v){da_scalar s;s.value=v;s.known=FULL;return s;}
static int halt_at(bt_machine*m,uint32_t site,uint32_t address,uint32_t need){
 m->flow=DA_HALT;m->boundary_va=site;m->boundary_address=address;m->needed_mask=need;return 0;
}
static int effect(bt_machine*m,da_flow f,uint32_t site,uint32_t address){
 if(f==DA_RETURNED){return 1;}
 m->flow=f;m->boundary_va=site;m->boundary_address=address;m->needed_mask=0;return 0;
}
static int begin(bt_machine*m,da_scalar*out){
 if(m->flow==DA_TRANSFER){return 0;}
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=0;
 m->reads=m->writes=m->calls=m->commits=0;
 if(out){out->value=out->known=0;}return 1;
}
static int need(bt_machine*m,da_scalar v,uint32_t mask,uint32_t site,uint32_t address){
 return (v.known&mask)==mask?1:halt_at(m,site,address,mask);
}
static int read_s(bt_machine*m,uint32_t a,unsigned n,uint32_t site,da_scalar*out){
 uint32_t mask=n==4?FULL:(UINT32_C(1)<<(n*8))-1;
 out->value=out->known=0;++m->reads;
 if(!effect(m,m->io&&m->io->read?m->io->read(m->io->context,a,n,0,site,out):DA_HALT,site,a)){return 0;}
 out->value&=mask;out->known=(out->known&mask)|~mask;return 1;
}
static int write_s(bt_machine*m,uint32_t a,da_scalar v,unsigned n,uint32_t site){
 ++m->writes;
 return effect(m,m->io&&m->io->write?m->io->write(m->io->context,a,v.value,n,v.known,site):DA_HALT,site,a);
}
static int equal(bt_machine*m,da_scalar a,uint32_t b,uint32_t mask,uint32_t site,uint32_t address,int*out){
 if(((a.value^b)&a.known&mask)!=0){*out=0;return 1;}
 if(!need(m,a,mask,site,address)){return 0;}*out=1;return 1;
}
static da_scalar add_s(da_scalar a,da_scalar b){
 da_scalar s;unsigned bit,carry=1;s.value=a.value+b.value;s.known=0;
 for(bit=0;bit<32;bit++){
  uint32_t mask=UINT32_C(1)<<bit;unsigned av,bv,cv,values=0,next=0;
  unsigned aa=(a.known&mask)?((a.value&mask)?2u:1u):3u;
  unsigned bb=(b.known&mask)?((b.value&mask)?2u:1u):3u;
  for(av=0;av<2;av++){for(bv=0;bv<2;bv++){for(cv=0;cv<2;cv++){
   if((aa&(1u<<av))&&(bb&(1u<<bv))&&(carry&(1u<<cv))){
    unsigned v=av+bv+cv;values|=1u<<(v&1u);next|=1u<<(v>>1);
   }
  }}}
  if(values==1||values==2){s.known|=mask;}carry=next;
 }return s;
}
static int invoke(bt_machine*m,uint32_t target,uint32_t site,const da_scalar*args,unsigned count,int memory,bt_result*out){
 unsigned i;bt_request r;r.target=target;r.callsite=site;r.argument_count=count;r.memory_effects_required=memory;
 for(i=0;i<6;i++){r.arguments[i].value=i<count?args[i].value:0;r.arguments[i].known=i<count?args[i].known:0;}
 m->last_request.target=target;m->last_request.callsite=site;m->last_request.argument_count=count;m->last_request.memory_effects_required=memory;
 for(i=0;i<6;i++){m->last_request.arguments[i].value=r.arguments[i].value;m->last_request.arguments[i].known=r.arguments[i].known;}
 out->scalar.value=out->scalar.known=0;out->memory_effects=0;++m->calls;
 if(!effect(m,m->io&&m->io->invoke?m->io->invoke(m->io->context,&r,out):DA_HALT,site,target)){return 0;}
 return !memory||out->memory_effects==1?1:halt_at(m,site,target,0);
}
static int query_link(bt_machine*m,da_scalar handle,uint32_t site,bt_result*out){
 da_scalar args[2];args[0]=handle;args[1]=literal(BT_QUERY_ADDRESS);return invoke(m,316,site,args,2,0,out);
}
static int post(bt_machine*m,uint32_t task,uint32_t event,uint32_t site,bt_result*out){
 da_scalar args[2];args[0]=literal(task);args[1]=literal(event);return invoke(m,80,site,args,2,0,out);
}
static int source_byte(bt_machine*m,const bt_source*s,uint32_t i,da_scalar*out){
 if(s->kind==BT_MAPPED){return read_s(m,s->address+i,1,0x8dfa,out);}
 if(s->kind!=BT_BORROWED||!s->data||!s->known||i>=s->available){return halt_at(m,0x8dfa,0,255);}
 out->value=s->data[i];out->known=UINT32_C(0xffffff00)|s->known[i];return 1;
}
void bt_init(bt_machine*m,const bt_backend*io){
 unsigned i;m->io=io;m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=0;
 m->reads=m->writes=m->calls=m->commits=0;m->last_request.target=m->last_request.callsite=0;m->last_request.argument_count=0;m->last_request.memory_effects_required=0;
 for(i=0;i<6;i++){m->last_request.arguments[i].value=m->last_request.arguments[i].known=0;}
}
da_flow bt_build(bt_machine*m,uint32_t handle,uint32_t command,const bt_source*source,uint32_t length,da_scalar*out){
 bt_source src;bt_result result;da_scalar h,ret,sum,v;uint32_t slot,base,frame,i;int match;
 if(!begin(m,out)){return m->flow;}ret=literal(handle);
 if(length>1039){if(out){out->value=ret.value;out->known=ret.known;}return m->flow;}
 /* Snapshot the view only; never snapshot the bytes it denotes. */
 src.kind=source?source->kind:BT_BORROWED;src.address=source?source->address:0;
 src.data=source?source->data:0;src.known=source?source->known:0;src.available=source?source->available:0;
 for(slot=0;slot<2;slot++){
  uint32_t ha=A(158)+4*slot;
  if(!read_s(m,ha,2,slot?0x8d3a:0x8d0e,&h)){return m->flow;}
  if(!equal(m,h,handle,FULL,slot?0x8d3e:0x8d1a,ha,&match)){return m->flow;}
  if(!match||handle==65534){continue;}
  if(!query_link(m,literal(handle),slot?0x8d58:0x8d32,&result)){return m->flow;}
  ret.value=result.scalar.value;ret.known=result.scalar.known;
  if(!equal(m,ret,1,FULL,slot?0x8d5e:0x8d36,316,&match)){return m->flow;}
  if(!match){continue;}
  base=BT_QUEUE_BASE+BT_QUEUE_STRIDE*slot;frame=base+6;
  if(!write_s(m,frame,literal(0x7f55),2,0x8d90)||
     !write_s(m,frame+4,literal(length),1,0x8d94)||
     !write_s(m,frame+3,literal(length>>8),1,0x8d9e)||
     !write_s(m,frame+2,literal(command),1,0x8da4)){return m->flow;}
  sum=literal((command+(length&255)+(length>>8))&255);
  for(i=0;i<length;i++){
   if(!source_byte(m,&src,i,&v)){return m->flow;}
   sum=add_s(sum,v);
   if(!write_s(m,frame+5+i,v,1,0x8e06)){return m->flow;}
  }
  if(!write_s(m,frame+5+length,sum,1,0x8dba)||
     !write_s(m,base+2,literal(length+6),2,0x8dd6)||
     !write_s(m,base+4,literal(0),2,0x8dda)){return m->flow;}
  ++m->commits;
  if(!read_s(m,A(156)+4*slot,1,0x8dee,&v)||!need(m,v,255,0x8dee,A(156)+4*slot)){return m->flow;}
  if(!post(m,v.value,1,0x8df4,&result)){return m->flow;}
  ret.value=result.scalar.value;ret.known=result.scalar.known;break;
 }
 if(out){out->value=ret.value;out->known=ret.known;}return m->flow;
}
static int retry(bt_machine*m,uint32_t slot,uint32_t task,uint32_t read_site,uint32_t write_site,uint32_t call_site){
 da_scalar n,args[3];bt_result ignored;uint32_t base=BT_QUEUE_BASE+BT_QUEUE_STRIDE*slot;
 if(!read_s(m,base,1,read_site,&n)){return 0;}n=add_s(n,literal(FULL));
 if(!write_s(m,base,n,1,write_site)){return 0;}
 args[0]=literal(task);args[1]=literal(2);args[2]=literal(2);return invoke(m,88,call_site,args,3,0,&ignored);
}
da_flow bt_events(bt_machine*m,uint32_t task,uint32_t events,da_scalar*out){
 da_scalar v,h,total,cursor,args[6],length,ptr;bt_result result;uint32_t slot,base,descriptor,remaining,chunk;int match;
 if(!begin(m,out)){return m->flow;}
 if(events&0x8000){
  args[0]=literal(task);if(!invoke(m,108,0x87f0,args,1,0,&result)){return m->flow;}
  ptr.value=result.scalar.value;ptr.known=result.scalar.known;
  if(!equal(m,ptr,0,FULL,0x87f4,108,&match)){return m->flow;}
  if(!match){
   if(!need(m,ptr,FULL,0x87f6,108)||!read_s(m,ptr.value,1,0x87f6,&v)||!equal(m,v,176,255,0x87fe,ptr.value,&match)){return m->flow;}
   if(match){
    if(!read_s(m,ptr.value+4,1,0x8802,&v)){return m->flow;}
    args[0]=literal(ptr.value+8);args[1]=v;if(!invoke(m,300,0x880c,args,2,0,&result)){return m->flow;}
   }
   args[0]=ptr;if(!invoke(m,104,0x8816,args,1,0,&result)){return m->flow;}
  }
  if(out){out->value=events^0x8000;out->known=FULL;}return m->flow;
 }
 if(events&8){
  args[0]=literal(task);args[1]=literal(0);args[2]=literal(0x19a78);
  if(!invoke(m,420,0x8a34,args,3,0,&result)){return m->flow;}
  if(out){out->value=events^8;out->known=FULL;}return m->flow;
 }
 for(slot=0;slot<2;slot++){
  if(!read_s(m,A(156)+4*slot,1,slot?0x8848:0x883e,&v)||
     !equal(m,v,task,FULL,slot?0x8850:0x8844,A(156)+4*slot,&match)){return m->flow;}
  if(match){break;}
 }
 if(slot==2){if(out){out->value=0;out->known=FULL;}return m->flow;}
 if(!read_s(m,A(158)+4*slot,2,0x885e,&h)){return m->flow;}
 base=BT_QUEUE_BASE+BT_QUEUE_STRIDE*slot;descriptor=BT_DESCRIPTOR_BASE+8*slot;
 if(events&1){
  if(!read_s(m,base+2,2,0x8884,&total)||!read_s(m,base+4,2,0x8888,&cursor)||
     !query_link(m,h,0x8890,&result)||!equal(m,result.scalar,1,FULL,0x8894,316,&match)){return m->flow;}
  if(match){
   if(!need(m,total,65535,0x8898,base+2)||!need(m,cursor,65535,0x8898,base+4)){return m->flow;}
   remaining=(total.value-cursor.value)&65535;
   if(remaining&&remaining<32768){
    args[0]=h;if(!invoke(m,184,0x88b4,args,1,0,&result)||!need(m,result.scalar,65535,0x88ca,184)){return m->flow;}
    chunk=(result.scalar.value-3)&65535;if(remaining<chunk){chunk=remaining;}
    if(!write_s(m,descriptor+2,literal(chunk),2,remaining<((result.scalar.value-3)&65535)?0x88f8:0x88ce)||
       !write_s(m,base,literal(10),1,0x88e2)||!post(m,task,2,0x88ec,&result)){return m->flow;}
   }else if(!write_s(m,base+2,literal(0),2,0x8908)){return m->flow;}
  }else if(!write_s(m,base+2,literal(0),2,0x8908)){return m->flow;}
  if(out){out->value=events^1;out->known=FULL;}return m->flow;
 }
 if(events&2){
  if(!read_s(m,base,1,0x892a,&v)||!equal(m,v,0,255,0x892e,base,&match)){return m->flow;}
  if(match){if(!write_s(m,base+2,literal(0),2,0x89f4)){return m->flow;}}
  else{
   if(!read_s(m,descriptor+2,2,0x8946,&length)){return m->flow;}
   args[0]=h;args[1]=literal(27);args[2]=length;args[3]=literal(0);args[4]=literal(0);
   if(!invoke(m,296,0x8952,args,5,0,&result)){return m->flow;}
   ptr.value=result.scalar.value;ptr.known=result.scalar.known;
   /* The original store precedes its null/unknown branch consumption. */
   if(!write_s(m,descriptor+4,ptr,4,0x8954)||!equal(m,ptr,0,FULL,0x8956,296,&match)){return m->flow;}
   if(match){if(!retry(m,slot,task,0x89e4,0x89ea,0x89a8)){return m->flow;}}
   else{
    if(!need(m,ptr,FULL,0x8956,296)||!read_s(m,base+4,2,0x8958,&cursor)||!read_s(m,descriptor+2,2,0x8960,&length)){return m->flow;}
    args[0]=ptr;args[1]=add_s(cursor,literal(base+6));args[2]=length;
    if(!invoke(m,76,0x896a,args,3,1,&result)||!query_link(m,h,0x8976,&result)||!need(m,result.scalar,1,0x8978,316)){return m->flow;}
    match=(result.scalar.value&1)!=0;
    if(match){
     if(!read_s(m,A(42),2,0x89b0,&v)||!write_s(m,descriptor,v,2,0x89b8)){return m->flow;}
     args[0]=h;args[1]=literal(descriptor);args[2]=literal(0);
     if(!invoke(m,212,0x89c2,args,3,0,&result)||!equal(m,result.scalar,0,FULL,0x89c4,212,&match)){return m->flow;}
    }
    if(match){
     if(!read_s(m,base+4,2,0x89c6,&cursor)||!read_s(m,descriptor+2,2,0x89ca,&length)){return m->flow;}
     v=add_s(cursor,length);
     if(!write_s(m,base+4,v,2,0x89d4)||!post(m,task,1,0x89dc,&result)){return m->flow;}
    }else{
     args[0]=literal(descriptor);args[1]=literal(27);
     if(!invoke(m,300,0x8988,args,2,0,&result)||!retry(m,slot,task,0x8994,0x899a,0x89a8)){return m->flow;}
    }
   }
  }
  if(out){out->value=events^2;out->known=FULL;}return m->flow;
 }
 if(events&4){
  args[0]=h;args[1]=literal(12);args[2]=literal(24);args[3]=literal(0);args[4]=literal(200);args[5]=literal(task);
  if(!invoke(m,424,0x8a1a,args,6,0,&result)){return m->flow;}
  if(out){out->value=events^4;out->known=FULL;}return m->flow;
 }
 if(out){out->value=0;out->known=FULL;}return m->flow;
}
