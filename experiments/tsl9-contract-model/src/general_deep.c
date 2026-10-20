#include "general_deep.h"
#include "report_packet.h"
#include <string.h>
#define FULL UINT32_MAX
#define A(x) (TF_RAM_BASE+UINT32_C(x))
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
    {0x10280,UINT32_C(0x20004050),0x10280,2,0},
    {0xceb0,UINT32_C(0x2000bf40),0xceb4,1,0},
    {0xd388,UINT32_C(0x2000bf61),0xd38c,1,0},
    {0xffa8,UINT32_C(0x2000bfae),0xffac,1,0},
    {0xf510,UINT32_C(0x2000bf91),0xf514,1,0},
    {0xdd6c,UINT32_C(0x2000bf64),0xdd70,1,0},
    {0xc2fe,UINT32_C(0x2000bf18),0xc302,1,3},
    {0xdec2,UINT32_C(0x2000bf65),0xdec6,1,0},
    {0xff3c,UINT32_C(0x2000bfa4),0xff44,4,0},
    {0xcea6,UINT32_C(0x2000bf41),0xceaa,1,0},
    {0xff7a,UINT32_C(0x2000bfa8),0xff82,2,4},
    {0x10286,UINT32_C(0x20004052),0x10286,1,0},
    {0x81f8,UINT32_C(0x2000bee9),0x81fc,1,0},
    {0xb23c,UINT32_C(0x2000befa),0xb240,2,0},
    {0xb246,UINT32_C(0x2000bef8),0xb24a,2,0},
    {0xb228,UINT32_C(0x2000bef6),0xb22c,2,0},
    {0xb232,UINT32_C(0x2000bef4),0xb236,1,0},
    {0xd31a,UINT32_C(0x2000bf5e),0xd31e,2,0},
    {0xd2a6,UINT32_C(0x2000bf5c),0xd2aa,2,0},
    {0xd392,UINT32_C(0x2000bf62),0xd396,2,0},
    {0xaafe,UINT32_C(0x2000bee7),0xab02,1,0},
    {0xab08,UINT32_C(0x2000bee6),0xab0c,1,0},
};
static int halt(gd_model*m,uint32_t va,uint32_t address,uint32_t mask){
 m->flow=GB_HALT;m->boundary_va=va;m->boundary_address=address;m->needed_mask=mask;return 0;
}
static int read_ram(gd_model*m,uint32_t va,uint32_t address,unsigned width,uint32_t needed,uint32_t*out){
 uint32_t v=0,k=0,off;unsigned i;
 if(!m->memory||address<TF_RAM_BASE||width>4||address-TF_RAM_BASE>TF_RAM_SIZE-width)return halt(m,va,address,needed);
 off=address-TF_RAM_BASE;
 for(i=0;i<width;i++){v|=(uint32_t)m->memory->ram[off+i]<<(8*i);k|=(uint32_t)m->memory->known[off+i]<<(8*i);}
 if(width<4)needed&=(UINT32_C(1)<<(8*width))-1;
 if((k&needed)!=needed)return halt(m,va,address,needed);
 *out=v;return 1;
}
static void store(gd_model*m,size_t off,uint32_t v,unsigned width){
 unsigned i;for(i=0;i<width;i++){m->stack[off+i]=(uint8_t)(v>>(8*i));m->known[off+i]=255;}
}
static uint32_t local(const gd_model*m,size_t off,unsigned width){
 uint32_t v=0;unsigned i;for(i=0;i<width;i++)v|=(uint32_t)m->stack[off+i]<<(8*i);return v;
}
static void merge(gd_model*m,size_t off,unsigned width,uint32_t clear,uint32_t value){
 /* Output-needed getter bits only. ROM zero baseline and native stores establish retained bits. */
 unsigned i;uint32_t old=local(m,off,width),v=(old&~clear)|value;
 for(i=0;i<width;i++){uint8_t c=(uint8_t)(clear>>(8*i));m->stack[off+i]=(uint8_t)(v>>(8*i));m->known[off+i]|=c;}
}
static int primitive(gd_model*m,gd_request*r,gb_scalar*out){
 m->last_request=*r;++m->calls;out->value=0;out->known=0;
 {gb_flow flow=m->backend.invoke?m->backend.invoke(m->backend.context,m,r,out):GB_HALT;if(flow==GB_TRANSFER){m->flow=flow;return 0;}if(flow!=GB_RETURNED)return halt(m,r->callsite,r->target,0);}
 return 1;
}
static int out_call(gd_model*m,uint32_t site,uint32_t target,uint32_t source,uint8_t*buffer,uint8_t*known,size_t n){
 gd_request r;gb_scalar out;memset(&r,0,sizeof(r));r.kind=GD_ROM;r.callsite=site;r.target=target;
 r.argument_count=3;r.arguments[1]=source;r.arguments[2]=(uint32_t)n;r.known[1]=r.known[2]=FULL;
 r.buffer=buffer;r.buffer_known=known;r.buffer_length=n;return primitive(m,&r,&out);
}
static int zero_frame(gd_model*m,uint32_t site,size_t off,size_t n){
 size_t i;if(!out_call(m,site,72,0,m->stack+off,m->known+off,n))return 0;
 /* Claimed ROM-zero RETURNED must supply its write contract. */
 for(i=0;i<n;i++)if(m->known[off+i]!=255||m->stack[off+i]!=0)return halt(m,site,72,255);
 return 1;
}
static int getter(gd_model*m,uint32_t va,uint32_t need,uint32_t*out){
 size_t i;for(i=0;i<sizeof(leaves)/sizeof(leaves[0]);i++)if(leaves[i].va==va){
  const leaf*l=&leaves[i];uint32_t v,mask=need;if(l->op&&l->op!=4)mask=FULL;
  if(!read_ram(m,l->site,l->address,l->width,mask,&v))return 0;
  if(l->op==1)v=v!=0;else if(l->op==2)v=v>=2;else if(l->op==3)v=v==1;
  /* Signed LH upper bits excluded by both callers' explicit masks. */
  *out=v;return 1;
 }return halt(m,va,va,need);
}
static int pair2(gd_model*m,uint32_t site1,uint32_t a1,uint32_t site2,uint32_t a2,uint32_t*out){
 uint32_t x,y;if(!read_ram(m,site1,a1,1,255,&x)||!read_ram(m,site2,a2,1,255,&y))return 0;
 *out=(x==2)|((y==2)<<1);return 1;
}
static int a894(gd_model*m,uint32_t*out){
 uint32_t x,y,z=4,w,v;if(!read_ram(m,0xa898,A(0xbed9),1,255,&x)||!read_ram(m,0xa8a0,A(0xbed8),1,255,&y))return 0;
 v=((uint32_t)(x-1)<2)|(y<<1);
 if(y==0){if(!read_ram(m,0xa8bc,A(0xbedb),1,3,&z))return 0;z<<=2;}
 if(!read_ram(m,0xa8ca,A(0xbeda),1,1,&w))return 0;
 *out=(v|z|(w<<3))&15;return 1;
}
static int aea4(gd_model*m,uint32_t*out){
 uint32_t v;if(!getter(m,0xa886,1,&v))return 0;if(v){*out=2;return 1;}
 if(!read_ram(m,0xaeb4,A(0xbee0),1,255,&v))return 0;if(v){*out=1;return 1;}
 if(!read_ram(m,0xaec0,A(0xbee8),1,255,&v))return 0;*out=v==2?3:0;return 1;
}
static int dee2(gd_model*m,uint32_t*out){
 static const uint32_t addresses[]={A(0xbf66),A(0xbf68),A(0xbf67),A(0xbf69)};
 static const uint32_t sites[]={0xdee6,0xdef0,0xdf06,0xdf1a};unsigned i;uint32_t v,x=0;
 for(i=0;i<4;i++){if(!read_ram(m,sites[i],addresses[i],1,255,&v))return 0;x|=(v==1)<<i;}*out=x;return 1;
}
static int pressure(gd_model*m,unsigned index,uint32_t*out){
 uint32_t v;if(!read_ram(m,0xffe2,A(0x4164),1,255,&v))return 0;
 if((uint8_t)(v-7)<=1){*out=0;return 1;}return read_ram(m,0x10000,A(0xbfaa)+index*2,2,0x7ff,out);
}
static int d17c(gd_model*m,uint32_t*out){
 uint32_t v;if(!read_ram(m,0xd180,A(0xbf60),1,255,&v))return 0;if(v){*out=2;return 1;}
 if(!read_ram(m,0xd18c,A(0xbf58),2,65535,&v))return 0;*out=v!=0;return 1;
}
static int send_reply(gd_model*m,uint32_t site,uint16_t handle,uint8_t command){
 gb_reply_request r;memset(&r,0,sizeof(r));r.wrapper_va=0x8cfa;r.handle=handle;r.command=command;
 r.data=m->stack+m->frame_offset;r.known=m->known+m->frame_offset;r.length=m->frame_length;++m->replies;
 {gb_flow flow=m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT;if(flow==GB_TRANSFER){m->flow=flow;return 0;}if(flow!=GB_RETURNED)return halt(m,site,0x8cfa,0);}return 1;
}
#define GET(va,need) do{if(!getter(m,(va),(need),&v))return m->flow;}while(0)
#define RD(site,a,n,k,out) do{if(!read_ram(m,(site),(a),(n),(k),&(out)))return m->flow;}while(0)
#define COPY(site,source,off,n) do{if(!out_call(m,(site),76,(source),m->stack+(off),m->known+(off),(n)))return m->flow;}while(0)
static da_flow packet_flow(gb_flow f){return f==GB_RETURNED?DA_RETURNED:f==GB_TRANSFER?DA_TRANSFER:DA_HALT;}
static da_flow packet_read(void *p,uint32_t address,unsigned width,uint32_t need,uint32_t site,da_scalar *out){
 gd_model *m=(gd_model *)p;unsigned i;out->value=out->known=0;
 if(!read_ram(m,site,address,width,need,&out->value))return packet_flow(m->flow);
 for(i=0;i<width;i++)out->known|=(uint32_t)m->memory->known[address-TF_RAM_BASE+i]<<(8*i);
 return DA_RETURNED;
}
static da_flow packet_invoke(void *p,const rp_request *r,rp_result *out){
 gd_model *m=(gd_model *)p;gd_request request;gb_scalar value={0,0};gb_flow f;unsigned i;
 memset(&request,0,sizeof(request));request.kind=GD_ROM;request.callsite=r->callsite;request.target=r->target;request.argument_count=r->argument_count;
 for(i=0;i<r->argument_count;i++){request.arguments[i]=r->arguments[i].value;request.known[i]=r->arguments[i].known;}
 request.buffer=r->buffer;request.buffer_known=r->buffer_known;request.buffer_length=r->buffer_length;m->last_request=request;++m->calls;
 f=m->backend.invoke?m->backend.invoke(m->backend.context,m,&request,&value):GB_HALT;
 out->scalar.value=value.value;out->scalar.known=value.known;
 /* Legacy GD_ROM RETURNED declares completed buffer bytes/masks. This adapter
    maps that host contract; it is not evidence about resident-ROM execution. */
 out->memory_effects=f==GB_RETURNED&&r->buffer?1:0;return packet_flow(f);
}
static da_flow packet_reply(void *p,const rp_reply *r){
 gd_model *m=(gd_model *)p;gb_reply_request request;memset(&request,0,sizeof(request));
 request.wrapper_va=r->wrapper_va;request.handle=r->handle;request.command=r->command;
 request.data=r->data;request.known=r->known;request.length=r->length;request.available=r->length;request.bounded=1;++m->replies;
 return packet_flow(m->backend.reply?m->backend.reply(m->backend.context,m,&request):GB_HALT);
}
static gb_flow a0_body(gd_model *m){
 rp_machine packet;rp_backend io;rp_storage scratch={m->stack,m->known,84},dependency={m->dependency_out,m->dependency_known,8};da_flow flow;
 m->frame_offset=RP_FRAME_OFFSET;m->frame_length=RP_FRAME_BYTES;
 io.context=m;io.read=packet_read;io.invoke=packet_invoke;io.reply=packet_reply;
 rp_init(&packet,&io,scratch,dependency);flow=rp_run_a0(&packet,m->argument);
 m->boundary_va=packet.boundary_va;m->boundary_address=packet.boundary_address;m->needed_mask=packet.needed_mask;
 m->calls=packet.calls;m->replies=packet.replies;
 return flow==DA_RETURNED?GB_RETURNED:flow==DA_TRANSFER?GB_TRANSFER:GB_HALT;
}
static gb_flow b0_body(gd_model*m){
 uint32_t v,x,h;unsigned i;RD(0x135d8,A(0xc790),1,255,v);if(v)return GB_RETURNED;
 m->frame_offset=0;m->frame_length=33;if(!zero_frame(m,0x135fa,0,33))return m->flow;
 GET(0x10280,0x1ff);merge(m,0,4,0x1ff,v&0x1ff);GET(0xceb0,7);merge(m,0,4,0xe00,(v&7)<<9);
 if(!pair2(m,0xa8de,A(0xbed6),0xa8e8,A(0xbed7),&v))return m->flow;merge(m,0,4,0x3000,(v&3)<<12);
 if(!aea4(m,&v))return m->flow;merge(m,0,4,0xc000,(v&3)<<14);
 if(!dee2(m,&v))return m->flow;merge(m,0,4,0xf0000,(v&15)<<16);
 if(!a894(m,&v))return m->flow;merge(m,2,1,0,v<<4);
 GET(0xd388,127);merge(m,0,4,UINT32_C(0x7f000000),(v&127)<<24);GET(0xffa8,1);merge(m,0,4,UINT32_C(0x80000000),v<<31);
 GET(0xf510,255);merge(m,4,4,1,v==0);
 GET(0xdd6c,1);RD(0x136cc,A(0xc248),2,0x4000,x);merge(m,4,4,6,((v&1)<<1)|((((x>>14)^1)&1)<<2));
 GET(0xf848,1);merge(m,4,4,8,(v&1)<<3);GET(0xc2fe,1);merge(m,4,4,16,(v&1)<<4);GET(0xdec2,1);merge(m,4,4,32,(v&1)<<5);
 GET(0xff3c,UINT32_C(0x03ffffff));merge(m,4,4,UINT32_C(0xffffffc0),v<<6);COPY(0x1373a,A(0x40e8),8,4);
 GET(0xcea6,255);store(m,12,v,1);
 if(!pressure(m,1,&v))return m->flow;merge(m,12,4,UINT32_C(0x0007ff00),(v&0x7ff)<<8);
 if(!pressure(m,0,&v))return m->flow;merge(m,12,4,UINT32_C(0x3ff80000),(v&0x7ff)<<19);
 GET(0xff7a,0x3fff);merge(m,12,4,UINT32_C(0xc0000000),v<<30);merge(m,16,2,0xfff,(v>>2)&0xfff);
 if(!d17c(m,&v))return m->flow;merge(m,16,2,0x3000,(v&3)<<12);
 GET(0x10286,1);merge(m,16,2,0x4000,(v&1)<<14);GET(0x81f8,1);merge(m,16,2,0x8000,v<<15);COPY(0x137fc,A(0x40fc),18,5);
 GET(0xb23c,0x3ff);store(m,23,v,1);merge(m,24,1,3,(v>>8)&3);
 GET(0xb246,0x7ff);merge(m,24,1,0xfc,(v&63)<<2);merge(m,25,1,31,(v>>6)&31);
 GET(0xb228,0x7ff);store(m,26,v>>3,1);merge(m,25,1,0xe0,(v&7)<<5);GET(0xb232,255);store(m,27,v,1);
 /* D31A getter precedes D2A6/D392, despite wire layout. */
 GET(0xd31a,0x1ff);merge(m,30,1,0xc0,(v&3)<<6);merge(m,31,1,127,(v>>2)&127);
 GET(0xd2a6,0xfff);store(m,28,v,1);merge(m,29,1,15,(v>>8)&15);
 GET(0xd392,0x3ff);merge(m,29,1,0xf0,(v&15)<<4);merge(m,30,1,63,(v>>4)&63);
 GET(0xaafe,31);merge(m,31,1,128,(v&1)<<7);merge(m,32,1,15,(v>>1)&15);GET(0xab08,15);merge(m,32,1,0xf0,v<<4);
 for(i=0;i<2;i++){
  uint32_t slot=A(0xc790)+i*4;RD(0x1391c,slot+2,2,65535,h);if(h==65534)continue;
  RD(0x13924,slot+5,1,255,v);if(v!=1)continue;RD(0x1392c,slot+4,1,255,v);if(!v)continue;
  RD(0x13936,slot+2,2,65535,h);if(!send_reply(m,0x13944,(uint16_t)h,0xb0))return m->flow;
 }return GB_RETURNED;
}
void gd_init(gd_model*m,tf_model*memory,const gd_backend*b){memset(m,0,sizeof(*m));m->memory=memory;if(b)m->backend=*b;}
gb_flow gd_dispatch(gd_model*m,uint32_t va,uint32_t arg){
 if(m->flow==GB_TRANSFER)return m->flow;
 m->entry=va;m->argument=arg;m->flow=GB_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=0;
 m->frame_offset=m->frame_length=0;m->recognized=0;m->calls=m->replies=0;
 memset(m->stack,0,sizeof(m->stack));memset(m->known,0,sizeof(m->known));memset(m->dependency_out,0,sizeof(m->dependency_out));
 memset(m->dependency_known,0,sizeof(m->dependency_known));memset(&m->last_request,0,sizeof(m->last_request));
 if(va==0x13160){m->recognized=1;m->flow=a0_body(m);}else if(va==0x135d4){m->recognized=1;m->flow=b0_body(m);}else halt(m,va,va,0);
 return m->flow;
}

