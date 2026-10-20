#include "gatt_parser.h"
#include <stdio.h>
#include <string.h>
#define BASE UINT32_C(0x20004000)
#define M 32768u
#define ATTR (BASE+0x1000u)
#define UUID (BASE+0x1100u)
#define SERVICE (BASE+0x1200u)
#define INPUT (BASE+0x2000u)
#define AT(n) (BASE+(n))
typedef struct {uint32_t site,address,value;unsigned width;int write;} trace;
typedef struct {
 uint8_t ram[M],known[M];trace log[12000];unsigned logs,clock_calls,dispatch_calls,cccd_calls;
 uint32_t fail_site,mutate_site,mutate_address,mutate_value;unsigned mutate_width;
 da_flow fail_flow,dispatch_flow;da_scalar raw_clock,result;gp_request request;
 unsigned source_reads,read_limit;int reset_on_dispatch;
} fixture;
static fixture f;static gp_machine g;static gp_backend io;
static unsigned groups,checks,failures;
#define CK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%u expression=%s\n",(unsigned)__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){f.ram[a-BASE+i]=(uint8_t)(v>>(i*8));}}
static uint32_t get(uint32_t a,unsigned n){uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)f.ram[a-BASE+i]<<(i*8);return v;}
static void record(uint32_t a,unsigned n,uint32_t site,uint32_t v,int w){if(f.logs<12000){trace*t=&f.log[f.logs++];t->address=a;t->width=n;t->site=site;t->value=v;t->write=w;}}
static da_flow rd(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 fixture*q=(fixture*)p;unsigned i;(void)need;record(a,n,site,0,0);
 if(site==0x8c0e&&++q->source_reads>q->read_limit)return DA_HALT;
 if(site==q->fail_site)return q->fail_flow;
 if(a<BASE||a-BASE>M||n>M-(a-BASE))return DA_HALT;
 out->value=out->known=0;
 for(i=0;i<n;i++){out->value|=(uint32_t)q->ram[a-BASE+i]<<(i*8);out->known|=(uint32_t)q->known[a-BASE+i]<<(i*8);}
 if(site==q->mutate_site)put(q->mutate_address,q->mutate_value,q->mutate_width);
 return DA_RETURNED;
}
static da_flow wr(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 fixture*q=(fixture*)p;unsigned i;record(a,n,site,v,1);
 if(site==q->fail_site)return q->fail_flow;
 if(a<BASE||a-BASE>M||n>M-(a-BASE))return DA_HALT;
 for(i=0;i<n;i++){q->ram[a-BASE+i]=(uint8_t)(v>>(i*8));q->known[a-BASE+i]=(uint8_t)(k>>(i*8));}
 if(site==q->mutate_site)put(q->mutate_address,q->mutate_value,q->mutate_width);
 return DA_RETURNED;
}
static da_flow call(void*p,const gp_request*r,da_scalar*out){
 fixture*q=(fixture*)p;q->request=*r;record(r->target,0,r->callsite,0,0);
 if(r->kind==GP_ROM&&r->target==124){++q->clock_calls;*out=q->raw_clock;return r->callsite==q->fail_site?q->fail_flow:DA_RETURNED;}
 if(r->kind==GP_ROM&&r->target==324){++q->cccd_calls;*out=q->result;return r->callsite==q->fail_site?q->fail_flow:DA_RETURNED;}
 if(r->kind==GP_NATIVE&&r->target==0x13e6a){
  ++q->dispatch_calls;*out=q->result;if(q->reset_on_dispatch)put(AT(164),9,1);return q->dispatch_flow;
 }
 return DA_HALT;
}
static bt_source mapped(uint32_t a){bt_source s={BT_MAPPED,0,0,0,0};s.address=a;return s;}
static bt_source borrowed(const uint8_t*d,const uint8_t*k,uint32_t n){bt_source s={BT_BORROWED,0,0,0,0};s.data=d;s.known=k;s.available=n;return s;}
static void reset(void){
 memset(&f,0,sizeof(f));memset(f.known,255,sizeof(f.known));f.raw_clock.value=1600;f.raw_clock.known=UINT32_MAX;
 f.result.value=0x12345678;f.result.known=0xffff00ff;f.read_limit=1100;f.fail_flow=DA_HALT;
 put(ATTR,2,1);put(ATTR+4,UUID,4);put(ATTR+10,0x27,2);put(UUID,0xfef1,2);put(SERVICE,0xfef1,2);
 put(AT(36),SERVICE,4);put(AT(42),0x27,2);put(AT(168),1000,4);
 io.context=&f;io.read=rd;io.write=wr;io.invoke=call;gp_init(&g,&io);
}
static da_flow run(uint32_t n,da_scalar*out){bt_source a=mapped(ATTR),s=mapped(INPUT);return gp_write(&g,0xdead1234,&a,&s,n,0xabcdef01,out);}
static unsigned frame(uint8_t cmd,unsigned n){
 unsigned i;uint32_t sum=cmd+(n>>8)+(n&255);put(INPUT,0x55,1);put(INPUT+1,0x7f,1);put(INPUT+2,cmd,1);put(INPUT+3,n>>8,1);put(INPUT+4,n,1);
 for(i=0;i<n;i++){put(INPUT+5+i,(i*7u+3u)&255,1);sum+=(i*7u+3u)&255;}put(INPUT+5+n,sum,1);return n+6;
}
static unsigned find(uint32_t site,unsigned start){unsigned i;for(i=start;i<f.logs;i++)if(f.log[i].site==site)return i;return f.logs;}
static void gates(void){
 da_scalar out;bt_source a;uint8_t flag[9]={0},known[9]={0};++groups;
 reset();flag[8]=32;known[8]=32;a=borrowed(flag,known,9);CK(gp_write(&g,0,&a,0,999,0,&out)==DA_RETURNED);CK(out.value==8&&out.known==UINT32_MAX);CK(f.clock_calls==0&&f.logs==0);
 reset();put(ATTR,3,1);CK(run(999,&out)==DA_RETURNED);CK(out.value==0&&f.clock_calls==0);CK(find(0x8b48,0)==f.logs);
 reset();put(UUID,0x1234,2);CK(run(10,&out)==DA_RETURNED);CK(f.clock_calls==0&&find(0x8b7a,0)==f.logs);
 reset();put(ATTR+10,0x28,2);CK(run(1,&out)==DA_RETURNED);CK(f.clock_calls==0);
 reset();f.known[ATTR-BASE+8]=0;CK(run(0,&out)==DA_HALT);CK(g.needed_mask==32&&g.boundary_va==0x8b36);
}
static void cccd(void){
 da_scalar out;bt_source a,s;uint8_t data[8]={9},known[8]={255};++groups;
 reset();put(UUID,0x2902,2);a=mapped(ATTR);s=borrowed(data,known,8);
 CK(gp_write(&g,0xf1234567,&a,&s,0x12345678,0x98765432,&out)==DA_RETURNED);CK(f.cccd_calls==1&&f.clock_calls==0);
 CK(out.value==f.result.value&&out.known==f.result.known);CK(f.request.argument_count==6&&f.request.arguments[0].value==0xf1234567);
 CK(f.request.arguments[1].value==ATTR&&f.request.arguments[1].known==UINT32_MAX);
 CK(f.request.arguments[2].known==0&&f.request.payload.data==data&&f.request.payload.known==known);
 CK(f.request.arguments[3].value==0x12345678&&f.request.arguments[4].value==0x98765432&&f.request.arguments[5].value==1);
 CK(find(0x8b70,0)==f.logs&&find(0x8b7a,0)==f.logs);
 reset();put(UUID,0x2902,2);f.fail_site=0x8b6a;f.fail_flow=DA_TRANSFER;CK(run(0,&out)==DA_TRANSFER);CK(g.boundary_address==324);
 {unsigned calls=f.cccd_calls;CK(run(0,&out)==DA_TRANSFER);CK(f.cccd_calls==calls);}
}
static void timeout(void){
 da_scalar out;++groups;
 reset();put(AT(164),5,1);put(AT(168),701,4);CK(run(0,&out)==DA_RETURNED);CK(get(AT(164),1)==5&&get(AT(168),4)==1000);CK(find(0x8bbe,0)==f.logs);
 reset();put(AT(164),5,1);put(AT(168),700,4);CK(run(0,&out)==DA_RETURNED);CK(get(AT(164),1)==0&&find(0x8bbe,0)<find(0x8bc2,0));
 reset();f.raw_clock.known=0x7fffffff;CK(run(0,&out)==DA_RETURNED);CK(f.request.target==124&&f.request.argument_count==0);
 reset();f.raw_clock.known=0x7ffffffe;CK(run(0,&out)==DA_HALT);CK(g.boundary_va==0x81ba&&g.needed_mask==0x7fffffff&&f.clock_calls==1&&find(0x8bb0,0)==f.logs&&g.writes==0);
 reset();put(AT(168),UINT32_MAX-5,4);f.raw_clock.value=0;CK(run(0,&out)==DA_RETURNED);CK(find(0x8bbe,0)==f.logs);
 reset();f.fail_site=0x8bc2;CK(run(0,&out)==DA_HALT);CK(g.boundary_va==0x8bc2&&out.known==0);
}
static void frames(void){
 da_scalar out;unsigned n,i;bt_source a,s;++groups;
 reset();n=frame(0xa0,3);CK(run(n,&out)==DA_RETURNED);CK(out.value==0&&out.known==UINT32_MAX&&f.dispatch_calls==1);
 CK(f.request.kind==GP_NATIVE&&f.request.target==0x13e6a&&f.request.callsite==0x8cec);
 CK(f.request.arguments[0].value==0xdead1234&&f.request.arguments[1].value==0xa0&&f.request.arguments[2].value==GP_RX_ADDRESS&&f.request.arguments[3].value==3);
 CK(f.request.payload.kind==BT_MAPPED&&f.request.payload.address==GP_RX_ADDRESS);
 for(i=0;i<3;i++)CK(get(GP_RX_ADDRESS+i,1)==(i*7u+3u));CK(get(AT(164),1)==0&&get(AT(146),2)==3);
 reset();n=frame(0x19,2);a=mapped(ATTR);s=mapped(INPUT);CK(gp_write(&g,7,&a,&s,4,0,&out)==DA_RETURNED);CK(get(AT(164),1)==4&&f.dispatch_calls==0);
 s.address=INPUT+4;CK(gp_write(&g,7,&a,&s,n-4,0,&out)==DA_RETURNED);CK(f.dispatch_calls==1&&f.request.arguments[0].value==7);
 reset();n=frame(0xa1,0);CK(run(n,&out)==DA_RETURNED);CK(f.dispatch_calls==1&&get(AT(146),2)==0);
 reset();n=frame(0xa1,1040);CK(run(n,&out)==DA_RETURNED);CK(f.dispatch_calls==1&&get(AT(146),2)==1040);
 reset();n=frame(0xa1,1041);CK(run(5,&out)==DA_RETURNED);CK(get(AT(164),1)==0&&get(AT(150),2)==1041&&get(AT(173),1)==((0xa1+4+17)&255));
 reset();n=frame(0xa1,2);put(INPUT+n-1,0,1);CK(run(n,&out)==DA_RETURNED);CK(f.dispatch_calls==0&&get(AT(164),1)==0);
 reset();put(INPUT,0x55,1);put(INPUT+1,0x55,1);put(INPUT+2,0x7f,1);CK(run(3,&out)==DA_RETURNED);CK(get(AT(164),1)==0);
}
static void prefix(void){
 da_scalar out;unsigned n,pos;++groups;
 reset();n=frame(0xa0,1);f.fail_site=0x8cc0;CK(run(n,&out)==DA_HALT);CK(get(AT(146),2)==1&&get(GP_RX_ADDRESS,1)==0&&get(AT(164),1)==5);
 pos=find(0x8cb2,0);CK(pos<find(0x8cc0,0));CK(g.boundary_va==0x8cc0);
 reset();n=frame(0xa0,1);f.dispatch_flow=DA_HALT;CK(run(n,&out)==DA_HALT);CK(get(AT(164),1)==6&&g.boundary_va==0x8cec);
 reset();n=frame(0xa0,1);f.dispatch_flow=DA_TRANSFER;CK(run(n,&out)==DA_TRANSFER);CK(get(AT(164),1)==6);pos=f.logs;CK(run(0,&out)==DA_TRANSFER);CK(f.logs==pos);
 reset();put(AT(164),5,1);put(AT(146),1040,2);put(AT(173),77,1);CK(run(1,&out)==DA_RETURNED);CK(get(AT(164),1)==0&&get(AT(146),2)==1040&&get(AT(173),1)==77);
 reset();n=frame(0xa0,1);f.reset_on_dispatch=1;CK(run(n,&out)==DA_RETURNED);CK(get(AT(164),1)==0);
}
static void live_order(void){
 da_scalar out;unsigned n,pos;bt_source a,s;uint8_t known[6]={255,255,255,255,255,255};++groups;
 reset();put(AT(164),2,1);put(INPUT,0x6a,1);f.mutate_site=0x8c0a;f.mutate_address=INPUT;f.mutate_value=0x55;f.mutate_width=1;
 CK(run(1,&out)==DA_RETURNED);CK(get(AT(172),1)==0x55);CK(find(0x8c0a,0)<find(0x8c0e,0));
 reset();put(AT(164),4,1);put(AT(150),0x10,2);put(INPUT,1,1);CK(run(1,&out)==DA_RETURNED);CK(get(AT(150),2)==0x11);
 reset();put(AT(164),5,1);put(AT(150),1,2);put(INPUT,0x22,1);f.mutate_site=0x8cb2;f.mutate_address=AT(146);f.mutate_value=99;f.mutate_width=2;
 CK(run(1,&out)==DA_RETURNED);CK(get(GP_RX_ADDRESS,1)==0x22&&get(AT(164),1)==6&&get(AT(146),2)==99);
 reset();n=frame(0xa0,0);a=mapped(ATTR);s=borrowed(&f.ram[INPUT-BASE],known,n);CK(gp_write(&g,7,&a,&s,n,0,&out)==DA_RETURNED);CK(f.dispatch_calls==1);
 reset();put(AT(164),2,1);f.known[INPUT-BASE]=0x7f;put(INPUT,0x30,1);CK(run(1,&out)==DA_RETURNED);CK(f.known[AT(172)-BASE]==0x7f&&f.known[AT(173)-BASE]==0x7f);
 reset();n=frame(0x11,0);f.known[INPUT-BASE+n-1]=0;CK(run(n,&out)==DA_HALT);CK(get(AT(164),1)==6&&g.boundary_va==0x8cd6);
 reset();frame(0xa0,1);f.read_limit=8;CK(run(65536,&out)==DA_HALT);CK(f.source_reads==9&&f.dispatch_calls==1&&g.boundary_va==0x8c0e);
 reset();frame(0xa0,2);a=mapped(ATTR);s=borrowed(&f.ram[INPUT-BASE],known,4);CK(gp_write(&g,7,&a,&s,8,0,&out)==DA_HALT);CK(get(AT(164),1)==4&&g.boundary_va==0x8c0e);
 reset();n=frame(0x33,0);pos=n;for(unsigned j=0;j<n;j++)f.ram[INPUT-BASE+n+j]=f.ram[INPUT-BASE+j];CK(run(pos+n,&out)==DA_RETURNED);CK(f.dispatch_calls==2);
}
int main(void){gates();cccd();timeout();frames();prefix();live_order();printf("GATT_PARSER_RESULT groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;}
