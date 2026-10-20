#include "gatt_parser.h"
#define FULL UINT32_MAX
#define A(n) (UINT32_C(0x20004000)+(n))
static da_scalar literal(uint32_t v){da_scalar s;s.value=v;s.known=FULL;return s;}
static void source_copy(bt_source*d,const bt_source*s){
 d->kind=s?s->kind:BT_BORROWED;d->address=s?s->address:0;d->data=s?s->data:0;d->known=s?s->known:0;d->available=s?s->available:0;
}
static void request_clear(gp_request*r,gp_kind kind,uint32_t target,uint32_t site,unsigned count){
 unsigned i;r->kind=kind;r->target=target;r->callsite=site;r->argument_count=count;
 for(i=0;i<6;i++){r->arguments[i].value=r->arguments[i].known=0;}source_copy(&r->attribute,0);source_copy(&r->payload,0);
}
static int halt_at(gp_machine*m,uint32_t site,uint32_t address,uint32_t mask){
 m->flow=DA_HALT;m->boundary_va=site;m->boundary_address=address;m->needed_mask=mask;return 0;
}
static int effect(gp_machine*m,da_flow f,uint32_t site,uint32_t address){
 if(f==DA_RETURNED)return 1;m->flow=f;m->boundary_va=site;m->boundary_address=address;m->needed_mask=0;return 0;
}
static int need(gp_machine*m,da_scalar v,uint32_t mask,uint32_t site,uint32_t address){
 return (v.known&mask)==mask?1:halt_at(m,site,address,mask);
}
static int equal(gp_machine*m,da_scalar a,da_scalar b,uint32_t mask,uint32_t site,uint32_t address,int*out){
 uint32_t both=a.known&b.known;if(((a.value^b.value)&both&mask)!=0){*out=0;return 1;}
 if((both&mask)!=mask)return halt_at(m,site,address,mask);*out=1;return 1;
}
static int read_s(gp_machine*m,uint32_t a,unsigned n,uint32_t site,da_scalar*out){
 uint32_t mask=n==4?FULL:(UINT32_C(1)<<(n*8))-1;out->value=out->known=0;++m->reads;
 if(!effect(m,m->io&&m->io->read?m->io->read(m->io->context,a,n,0,site,out):DA_HALT,site,a))return 0;
 out->value&=mask;out->known=(out->known&mask)|~mask;return 1;
}
static int write_s(gp_machine*m,uint32_t a,da_scalar v,unsigned n,uint32_t site){
 ++m->writes;return effect(m,m->io&&m->io->write?m->io->write(m->io->context,a,v.value,n,v.known,site):DA_HALT,site,a);
}
static int source_read(gp_machine*m,const bt_source*s,uint32_t offset,unsigned n,uint32_t site,da_scalar*out){
 unsigned i;uint32_t mask=n==4?FULL:(UINT32_C(1)<<(n*8))-1;
 if(s->kind==BT_MAPPED)return read_s(m,s->address+offset,n,site,out);
 ++m->reads;if(s->kind!=BT_BORROWED||!s->data||!s->known||offset>s->available||n>s->available-offset)return halt_at(m,site,0,mask);
 out->value=out->known=0;for(i=0;i<n;i++){out->value|=(uint32_t)s->data[offset+i]<<(i*8);out->known|=(uint32_t)s->known[offset+i]<<(i*8);}out->known|=~mask;return 1;
}
static da_scalar add_s(da_scalar a,da_scalar b){
 da_scalar s;unsigned bit,carry=1;s.value=a.value+b.value;s.known=0;
 for(bit=0;bit<32;bit++){
  uint32_t mask=UINT32_C(1)<<bit;unsigned av,bv,cv,values=0,next=0;
  unsigned aa=(a.known&mask)?((a.value&mask)?2u:1u):3u;
  unsigned bb=(b.known&mask)?((b.value&mask)?2u:1u):3u;
  for(av=0;av<2;av++){for(bv=0;bv<2;bv++){for(cv=0;cv<2;cv++){
   if((aa&(1u<<av))&&(bb&(1u<<bv))&&(carry&(1u<<cv))){unsigned v=av+bv+cv;values|=1u<<(v&1u);next|=1u<<(v>>1);}
  }}}
  if(values==1||values==2)s.known|=mask;carry=next;
 }return s;
}
static int invoke(gp_machine*m,const gp_request*r,da_scalar*out){
 unsigned i;m->last_request.kind=r->kind;m->last_request.target=r->target;m->last_request.callsite=r->callsite;m->last_request.argument_count=r->argument_count;
 for(i=0;i<6;i++){m->last_request.arguments[i].value=r->arguments[i].value;m->last_request.arguments[i].known=r->arguments[i].known;}
 source_copy(&m->last_request.attribute,&r->attribute);source_copy(&m->last_request.payload,&r->payload);
 out->value=out->known=0;++m->calls;return effect(m,m->io&&m->io->invoke?m->io->invoke(m->io->context,r,out):DA_HALT,r->callsite,r->target);
}
static da_flow clock_call(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned count,da_scalar*out){
 gp_machine*m=(gp_machine*)p;gp_request r;unsigned i;int ok;
 if(kind!=DA_ROM||target!=124||count>6)return DA_HALT;request_clear(&r,GP_ROM,target,site,count);
 for(i=0;i<count;i++){r.arguments[i].value=args[i].value;r.arguments[i].known=args[i].known;}
 ok=invoke(m,&r,out);m->clock_returned=ok;m->clock_raw.value=out->value;m->clock_raw.known=out->known;return m->flow;
}
static int now_value(gp_machine*m,da_scalar*out){
 da_flow f;m->clock_returned=0;m->clock_raw.value=m->clock_raw.known=0;f=da_run(&m->clock,0x81b0,0,out);
 if(f==DA_RETURNED)return 1;m->flow=f;m->boundary_va=m->clock.boundary_va;m->boundary_address=m->clock.boundary_address;
 m->needed_mask=m->clock_returned?UINT32_C(0x7fffffff):0;return 0;
}
static int add_sum(gp_machine*m,da_scalar v){
 da_scalar sum;return read_s(m,A(173),1,0x8c4c,&sum)&&write_s(m,A(173),add_s(sum,v),1,0x8c52);
}
static int state(gp_machine*m,uint32_t v,uint32_t site){return write_s(m,A(164),literal(v),1,site);}
static int parse_byte(gp_machine*m,da_scalar mode,da_scalar v,uint32_t handle){
 int match;da_scalar len,count,next,sum;gp_request r;da_scalar ignored;
 if(!equal(m,mode,literal(0),255,0x8c12,A(164),&match))return 0;
 if(match){if(!equal(m,v,literal(0x55),255,0x8c18,0,&match))return 0;return state(m,match?1u:0u,match?0x8c1eu:0x8cf0u);}
 if(!equal(m,mode,literal(1),255,0x8c26,A(164),&match))return 0;
 if(match){
  if(!equal(m,v,literal(0x7f),255,0x8c2e,0,&match))return 0;
  if(!match)return state(m,0,0x8cf0);return state(m,2,0x8c34)&&write_s(m,A(173),literal(0),1,0x8c38);
 }
 if(!equal(m,mode,literal(2),255,0x8c3e,A(164),&match))return 0;
 if(match)return state(m,3,0x8c44)&&write_s(m,A(172),v,1,0x8c48)&&add_sum(m,v);
 if(!equal(m,mode,literal(3),255,0x8c58,A(164),&match))return 0;
 if(match){len.value=v.value<<8;len.known=(v.known<<8)|255;return state(m,4,0x8c5e)&&write_s(m,A(150),len,2,0x8c66)&&add_sum(m,v);}
 if(!equal(m,mode,literal(4),255,0x8c6c,A(164),&match))return 0;
 if(match){
  if(!write_s(m,A(146),literal(0),2,0x8c70)||!read_s(m,A(150),2,0x8c74,&len))return 0;
  len.known=(len.known&v.known)|(len.known&len.value)|(v.known&v.value);len.value|=v.value;
  if(!write_s(m,A(150),len,2,0x8c7a)||!equal(m,len,literal(0),65535,0x8c7e,A(150),&match))return 0;
  if(match){if(!state(m,6,0x8c8e))return 0;}
  else{if(!need(m,len,65535,0x8c88,A(150)))return 0;if(!state(m,len.value>1040?0u:5u,len.value>1040?0x8c94u:0x8c8eu))return 0;}
  return add_sum(m,v);
 }
 if(!equal(m,mode,literal(5),255,0x8c9a,A(164),&match))return 0;
 if(match){
  if(!read_s(m,A(146),2,0x8c9e,&count)||!need(m,count,65535,0x8ca6,A(146)))return 0;
  if(count.value>1039)return state(m,0,0x8cf0);next=literal((count.value+1)&65535);
  if(!write_s(m,A(146),next,2,0x8cb2)||!write_s(m,GP_RX_ADDRESS+count.value,v,1,0x8cc0)||
     !read_s(m,A(150),2,0x8cc4,&len)||!need(m,len,65535,0x8cc8,A(150)))return 0;
  if(next.value>=len.value&&!state(m,6,0x8c8e))return 0;return add_sum(m,v);
 }
 if(!equal(m,mode,literal(6),255,0x8cce,A(164),&match))return 0;
 if(match){
  if(!read_s(m,A(173),1,0x8cd2,&sum)||!equal(m,sum,v,255,0x8cd6,A(173),&match))return 0;
  if(match){
   request_clear(&r,GP_NATIVE,0x13e6a,0x8cec,4);
   if(!read_s(m,A(150),2,0x8cda,&r.arguments[3])||!read_s(m,A(172),1,0x8ce6,&r.arguments[1]))return 0;
   r.arguments[0]=literal(handle);r.arguments[2]=literal(GP_RX_ADDRESS);r.payload.kind=BT_MAPPED;r.payload.address=GP_RX_ADDRESS;
   ++m->dispatches;if(!invoke(m,&r,&ignored))return 0;
  }
 }return state(m,0,0x8cf0);
}
void gp_init(gp_machine*m,const gp_backend*io){
 m->io=io;m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->reads=m->writes=m->calls=m->bytes=m->dispatches=0;
 request_clear(&m->last_request,GP_ROM,0,0,0);m->clock_returned=0;m->clock_raw.value=m->clock_raw.known=0;
 m->clock_backend.context=m;m->clock_backend.read=0;m->clock_backend.write=0;m->clock_backend.call=clock_call;m->clock_backend.schedule=0;da_init(&m->clock,&m->clock_backend);
}
da_flow gp_write(gp_machine*m,uint32_t handle,const bt_source*attribute,const bt_source*payload,uint32_t length,uint32_t fifth,da_scalar*out){
 bt_source attr,src;da_scalar v,pointer,uuid,service,ah,sh,now,last,mode;gp_request r;da_scalar ret;uint32_t i;int match;
 if(m->flow==DA_TRANSFER)return m->flow;
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->reads=m->writes=m->calls=m->bytes=m->dispatches=0;
 if(out){out->value=out->known=0;}source_copy(&attr,attribute);source_copy(&src,payload);
 if(!source_read(m,&attr,8,1,0x8b2e,&v)||!need(m,v,32,0x8b36,attr.address+8))return m->flow;
 if(v.value&32){if(out)*out=literal(8);return m->flow;}
 if(!source_read(m,&attr,0,1,0x8b3a,&v)||!equal(m,v,literal(2),255,0x8b40,attr.address,&match))return m->flow;
 if(!match){if(out)*out=literal(0);return m->flow;}
 if(!source_read(m,&attr,4,4,0x8b48,&pointer)||!need(m,pointer,FULL,0x8b52,attr.address+4)||
    !read_s(m,pointer.value,2,0x8b52,&uuid)||!equal(m,uuid,literal(0x2902),65535,0x8b5c,pointer.value,&match))return m->flow;
 if(match){
  request_clear(&r,GP_ROM,324,0x8b6a,6);source_copy(&r.attribute,&attr);source_copy(&r.payload,&src);
  r.arguments[0]=literal(handle);if(attr.kind==BT_MAPPED)r.arguments[1]=literal(attr.address);if(src.kind==BT_MAPPED)r.arguments[2]=literal(src.address);
  r.arguments[3]=literal(length);r.arguments[4]=literal(fifth);r.arguments[5]=literal(1);
  if(invoke(m,&r,&ret)&&out){out->value=ret.value;out->known=ret.known;}return m->flow;
 }
 if(!read_s(m,A(36),4,0x8b70,&pointer)||!need(m,pointer,FULL,0x8b72,A(36))||
    !read_s(m,pointer.value,2,0x8b72,&service)||!equal(m,uuid,service,65535,0x8b76,pointer.value,&match))return m->flow;
 if(!match){if(out)*out=literal(0);return m->flow;}
 if(!source_read(m,&attr,10,2,0x8b7a,&ah)||!read_s(m,A(42),2,0x8b7e,&sh)||!equal(m,ah,sh,65535,0x8b82,A(42),&match))return m->flow;
 if(!match){if(out)*out=literal(0);return m->flow;}
 if(!now_value(m,&now)||!read_s(m,A(168),4,0x8bb0,&last)||!need(m,last,FULL,0x8bba,A(168)))return m->flow;
 if((uint32_t)(now.value-last.value)>299&&!state(m,0,0x8bbe))return m->flow;
 if(!write_s(m,A(168),now,4,0x8bc2))return m->flow;
 /* Full32 source offset and native low16 guard are intentionally distinct.
    Oversized host tests require finite borrowed views or bounded providers. */
 for(i=0;(i&65535)<length;i++){
  if(!read_s(m,A(164),1,0x8c0a,&mode)||!source_read(m,&src,i,1,0x8c0e,&v))return m->flow;
  if(!parse_byte(m,mode,v,handle))return m->flow;++m->bytes;
 }if(out)*out=literal(0);return m->flow;
}
