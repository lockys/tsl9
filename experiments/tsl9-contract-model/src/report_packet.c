#include "report_packet.h"
#define FULL UINT32_MAX
#define BASE UINT32_C(0x20000000)
#define A(x) (BASE+UINT32_C(x))
typedef struct {uint32_t va,address,site;unsigned width,op;} leaf;
static const leaf leaves[]={
    {0xf8e0,UINT32_C(0x20004116),0xf8e0,1,0},
    {0xafc0,UINT32_C(0x200040c4),0xafc0,1,0},
    {0xf8ec,UINT32_C(0x20004117),0xf8ec,1,0},
    {0xa886,UINT32_C(0x2000bed1),0xa88a,1,1},
    {0xd16e,UINT32_C(0x2000bf58),0xd172,2,1},
    {0xd24c,UINT32_C(0x2000bf5b),0xd250,1,1},
    {0x17f68,UINT32_C(0x2000c91c),0x17f6c,1,0},
    {0xb3de,UINT32_C(0x2000beef),0xb3e2,1,2},
    {0xc1f6,UINT32_C(0x2000bf12),0xc1fa,1,0},
    {0xcbae,UINT32_C(0x2000bf26),0xcbb2,1,0},
    {0x843a,UINT32_C(0x2000416c),0x843a,1,0},
    {0xf564,UINT32_C(0x2000bf99),0xf568,1,0},
    {0xf5c8,UINT32_C(0x2000bf9e),0xf5cc,1,0},
    {0xf596,UINT32_C(0x2000bf9b),0xf59a,1,0},
    {0xf5fa,UINT32_C(0x2000bfa0),0xf5fe,1,0},
    {0xab12,UINT32_C(0x2000bee0),0xab16,1,0},
    {0xf848,UINT32_C(0x20004115),0xf848,1,0},
};
static int halt(rp_machine *m,uint32_t site,uint32_t address,uint32_t mask){
 m->flow=DA_HALT;m->boundary_va=site;m->boundary_address=address;m->needed_mask=mask;return 0;
}
static int effect(rp_machine *m,da_flow flow,uint32_t site,uint32_t address){
 if(flow==DA_RETURNED)return 1;m->flow=flow;m->boundary_va=site;m->boundary_address=address;m->needed_mask=0;return 0;
}
static void clear_request(rp_request *r){
 unsigned i;r->callsite=r->target=0;r->argument_count=0;r->buffer=0;r->buffer_known=0;r->buffer_length=0;
 for(i=0;i<3;i++){r->arguments[i].value=0;r->arguments[i].known=0;}
}
static int read_ram(rp_machine *m,uint32_t site,uint32_t address,unsigned width,uint32_t needed,uint32_t *out){
 da_scalar value={0,0};if(width<4)needed&=(UINT32_C(1)<<(width*8))-1;
 if(!effect(m,m->io.read?m->io.read(m->io.context,address,width,needed,site,&value):DA_HALT,site,address)){
  if(m->flow==DA_HALT)m->needed_mask=needed;return 0;
 }
 if((value.known&needed)!=needed)return halt(m,site,address,needed);*out=value.value;return 1;
}
static void store(rp_machine *m,uint32_t off,uint32_t value,unsigned width){
 unsigned i;for(i=0;i<width;i++){m->scratch.data[off+i]=(uint8_t)(value>>(8*i));m->scratch.known[off+i]=255;}
}
static uint32_t local(const rp_machine *m,uint32_t off,unsigned width){
 uint32_t v=0;unsigned i;for(i=0;i<width;i++)v|=(uint32_t)m->scratch.data[off+i]<<(8*i);return v;
}
static void merge(rp_machine *m,uint32_t off,unsigned width,uint32_t clear,uint32_t value){
 uint32_t v=(local(m,off,width)&~clear)|value;unsigned i;
 for(i=0;i<width;i++){m->scratch.data[off+i]=(uint8_t)(v>>(8*i));m->scratch.known[off+i]|=(uint8_t)(clear>>(8*i));}
}
static int primitive(rp_machine *m,rp_request *r,rp_result *out){
 unsigned i;
 /* Copy only defined fields and active arguments, without an implicit libc
    struct-copy dependency in the freestanding RV32 object. */
 m->last_request.callsite=r->callsite;m->last_request.target=r->target;
 m->last_request.argument_count=r->argument_count;m->last_request.buffer=r->buffer;
 m->last_request.buffer_known=r->buffer_known;m->last_request.buffer_length=r->buffer_length;
 for(i=0;i<3;i++){
  m->last_request.arguments[i].value=i<r->argument_count?r->arguments[i].value:0;
  m->last_request.arguments[i].known=i<r->argument_count?r->arguments[i].known:0;
 }
 ++m->calls;out->scalar.value=out->scalar.known=0;out->memory_effects=0;
 if(!effect(m,m->io.invoke?m->io.invoke(m->io.context,r,out):DA_HALT,r->callsite,r->target))return 0;
 return !r->buffer||out->memory_effects==1?1:halt(m,r->callsite,r->target,0);
}
static int out_call(rp_machine *m,uint32_t site,uint32_t target,uint32_t source,uint8_t *buffer,uint8_t *known,uint32_t n){
 rp_request r;rp_result ignored;clear_request(&r);r.callsite=site;r.target=target;r.argument_count=3;
 r.arguments[1].value=source;r.arguments[1].known=FULL;r.arguments[2].value=n;r.arguments[2].known=FULL;
 r.buffer=buffer;r.buffer_known=known;r.buffer_length=n;return primitive(m,&r,&ignored);
}
static int zero_frame(rp_machine *m,uint32_t site,uint32_t off,uint32_t n){
 uint32_t i;if(!out_call(m,site,72,0,m->scratch.data+off,m->scratch.known+off,n))return 0;
 for(i=0;i<n;i++)if(m->scratch.known[off+i]!=255||m->scratch.data[off+i]!=0)return halt(m,site,72,255);return 1;
}
static int getter(rp_machine *m,uint32_t va,uint32_t need,uint32_t *out){
 unsigned i;
 for(i=0;i<sizeof(leaves)/sizeof(leaves[0]);i++){
  const leaf *l=&leaves[i];uint32_t v,mask=l->op?FULL:need;
  if(l->va!=va)continue;
  if(!read_ram(m,l->site,l->address,l->width,mask,&v))return 0;
  if(l->op==1)v=v!=0;else if(l->op==2)v=v>=2;*out=v;return 1;
 }
 return halt(m,va,va,need);
}
static int gate8214(rp_machine *m,unsigned channel,uint32_t *out){
 uint32_t p,v;if(!read_ram(m,0x8218,A(0x4054),4,FULL,&p)||!read_ram(m,0x821a,p+4,1,8,&v))return 0;
 if((v&8)||channel>2){*out=0;return 1;}if(!read_ram(m,0x8232,A(0x40c1)+channel,1,255,&v))return 0;*out=v<3;return 1;
}
static int timer16f26(rp_machine *m,uint32_t *out){
 rp_request r;rp_result result;da_scalar value;uint32_t task;if(!read_ram(m,0x16f32,A(0x416d),1,255,&task))return 0;
 clear_request(&r);r.callsite=0x16f36;r.target=96;r.argument_count=2;
 r.arguments[0].value=task;r.arguments[0].known=FULL;r.arguments[1].value=1;r.arguments[1].known=FULL;
 if(!primitive(m,&r,&result))return 0;value=result.scalar;
 if((value.known&0x7ffff)!=0x7ffff)return halt(m,0x16f36,96,0x7ffff);
 *out=((value.value*UINT32_C(10))>>4)+50;return 1;
}
static int send_reply(rp_machine *m,uint32_t site,uint16_t handle,uint8_t command){
 rp_reply r;r.callsite=site;r.wrapper_va=0x8cfa;r.handle=handle;r.command=command;
 r.data=m->scratch.data+RP_FRAME_OFFSET;r.known=m->scratch.known+RP_FRAME_OFFSET;r.length=RP_FRAME_BYTES;++m->replies;
 return effect(m,m->io.reply?m->io.reply(m->io.context,&r):DA_HALT,site,0x8cfa);
}
#define GET(va,need) do{if(!getter(m,(va),(need),&v))return m->flow;}while(0)
#define RD(site,a,n,k,out) do{if(!read_ram(m,(site),(a),(n),(k),&(out)))return m->flow;}while(0)
#define COPY(site,source,off,n) do{if(!out_call(m,(site),76,(source),m->scratch.data+(off),m->scratch.known+(off),(n)))return m->flow;}while(0)
static da_flow a0_body(rp_machine*m){
 uint32_t v,x,y,p,h,auth;unsigned i;
 if(!out_call(m,0x9db4,76,UINT32_C(0x08077b00),m->dependency.data,m->dependency.known,8))return m->flow;
 for(i=0;i<8;i++){m->scratch.data[i]=m->dependency.data[i];m->scratch.known[i]=m->dependency.known[i];}
 if(!zero_frame(m,0x1319a,8,76))return m->flow;
 store(m,8,0,1);m->scratch.data[9]=m->scratch.data[0];m->scratch.known[9]=m->scratch.known[0];m->scratch.data[10]=m->scratch.data[1];m->scratch.known[10]=m->scratch.known[1];
 COPY(0x92b4,UINT32_C(0x1ffff7ec),12,8);COPY(0x92ce,UINT32_C(0x1ffff7e8),20,6);
 COPY(0x131cc,A(0xbf44),48,19);
 for(i=0;i<2;i++){
  uint32_t slot=A(0xc790)+i*4;RD(0x131e6,slot+2,2,65535,h);if(h==65534)continue;
  RD(0x131ee,slot+5,1,255,v);if(v!=0)continue;RD(0x131fa,slot+4,1,255,auth);store(m,11,1,1);
  if(!auth){store(m,26,0,2);if(!zero_frame(m,0x133ea,32,16)||!zero_frame(m,0x133f6,67,16))return m->flow;}
  else{
   GET(0xf8e0,0x7f);merge(m,11,1,0,v<<1);GET(0xafc0,0x3f);merge(m,11,1,0,v<<2);
   GET(0xf8ec,0x1f);RD(0x13232,A(0x4164),1,15,x);merge(m,11,1,0,(v<<3)|(x<<4));
   GET(0xa886,255);store(m,26,v,1);GET(0xd16e,127);merge(m,26,1,0,v<<1);GET(0xd24c,63);merge(m,26,1,0,v<<2);
   GET(0x17f68,1);merge(m,26,1,0,(v<<3)&8);GET(0x17f68,2);merge(m,26,1,0,(v<<3)&16);
   GET(0xb3de,7);merge(m,26,1,0,v<<5);GET(0xc1f6,3);merge(m,26,1,0,v<<6);GET(0xcbae,1);merge(m,26,1,0,v<<7);
   GET(0x843a,255);store(m,27,v,1);GET(0xf564,127);merge(m,27,1,0,v<<1);GET(0xf5c8,63);merge(m,27,1,0,v<<2);
   GET(0xf596,31);merge(m,27,1,0,v<<3);GET(0xf5fa,15);merge(m,27,1,0,v<<4);GET(0xab12,7);merge(m,27,1,0,v<<5);GET(0xf848,3);merge(m,27,1,0,v<<6);
   if(!gate8214(m,0,&v))return m->flow;x=0;
   if(!v){RD(0x13330,A(0x4054),4,FULL,p);RD(0x13334,p+4,1,8,y);x=((y>>3)^1)&1;}merge(m,27,1,0,x<<7);
   if(!timer16f26(m,&v))return m->flow;store(m,28,v,2);RD(0x8298,A(0xbfb1),1,63,v);store(m,30,v&63,1);
   if(!gate8214(m,0,&v))return m->flow;store(m,31,v,1);
   if(!gate8214(m,1,&v))return m->flow;merge(m,31,1,0,v<<1);
   if(!gate8214(m,2,&v))return m->flow;RD(0x13388,A(0x4054),4,FULL,p);merge(m,31,1,0,v<<2);
   COPY(0x13398,p,32,16);RD(0x1339a,A(0x4054),4,FULL,p);COPY(0x133aa,p+96,67,16);
  }
  RD(0x133ae,slot+2,2,65535,h);if(!send_reply(m,0x133bc,(uint16_t)h,0xa0))return m->flow;
 }return DA_RETURNED;
}
void rp_init(rp_machine *m,const rp_backend *io,rp_storage scratch,rp_storage dependency){
 m->io.context=io?io->context:0;m->io.read=io?io->read:0;m->io.invoke=io?io->invoke:0;m->io.reply=io?io->reply:0;
 m->scratch=scratch;m->dependency=dependency;m->flow=DA_RETURNED;
 m->boundary_va=m->boundary_address=m->needed_mask=m->calls=m->replies=0;clear_request(&m->last_request);
}
da_flow rp_run_a0(rp_machine *m,uint32_t argument){
 uint32_t i;(void)argument;if(m->flow==DA_TRANSFER)return m->flow;
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->calls=m->replies=0;clear_request(&m->last_request);
 if(!m->scratch.data||!m->scratch.known||m->scratch.length<RP_SCRATCH_BYTES||
    !m->dependency.data||!m->dependency.known||m->dependency.length<RP_DEPENDENCY_BYTES){halt(m,0x13160,0,0);return m->flow;}
 for(i=0;i<RP_SCRATCH_BYTES;i++){m->scratch.data[i]=0;m->scratch.known[i]=0;}
 for(i=0;i<RP_DEPENDENCY_BYTES;i++){m->dependency.data[i]=0;m->dependency.known[i]=0;}
 m->flow=a0_body(m);return m->flow;
}
