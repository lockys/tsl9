#include "startup_clock.h"
#include <stdio.h>
#include <string.h>
typedef struct {uint32_t address,value,known,site;int write;} event;
typedef struct {
 uint32_t regs[3],known[3];event log[12000];unsigned logs,committed,hse,pll,sw;
 unsigned ready_after,pll_after,switch_after,read_limit,reads;
 int final_ready;uint32_t stop_site,unknown_site,unknown_mask;da_flow stop_flow;
} fixture;
static fixture f;static sc_machine m;static sc_backend io;
static unsigned groups,checks,failures;
#define CK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%u expression=%s\n",(unsigned)__LINE__,#x);}}while(0)
static unsigned index_of(uint32_t a){return (a-SC_CONTROL)/4;}
static void log_event(uint32_t a,uint32_t v,uint32_t k,uint32_t site,int w){if(f.logs<12000){event*e=&f.log[f.logs++];e->address=a;e->value=v;e->known=k;e->site=site;e->write=w;}}
static da_flow rd(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 fixture*q=(fixture*)p;unsigned i;if(n!=4||need||a<SC_CONTROL||a>SC_INTERRUPT||(a&3))return DA_HALT;
 i=index_of(a);++q->reads;
 if(site==0x184f6){++q->hse;if(q->ready_after&&q->hse>=q->ready_after)q->regs[i]|=0x20000;else q->regs[i]&=~UINT32_C(0x20000);}
 if(site==0x18510){if(q->final_ready>=0){if(q->final_ready)q->regs[i]|=0x20000;else q->regs[i]&=~UINT32_C(0x20000);}}
 if(site==0x1855a){++q->pll;if(q->pll_after&&q->pll>=q->pll_after)q->regs[i]|=0x2000000;else q->regs[i]&=~UINT32_C(0x2000000);}
 if(site==0x18578){++q->sw;q->regs[i]=(q->regs[i]&~UINT32_C(12))|((q->switch_after&&q->sw>=q->switch_after)?8u:0u);}
 out->value=q->regs[i];out->known=q->known[i];if(site==q->unknown_site)out->known&=~q->unknown_mask;
 log_event(a,out->value,out->known,site,0);if(q->reads>q->read_limit)return DA_HALT;
 return site==q->stop_site?q->stop_flow:DA_RETURNED;
}
static da_flow wr(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 fixture*q=(fixture*)p;log_event(a,v,k,site,1);
 if(site==q->stop_site)return q->stop_flow;
 if(n!=4||a<SC_CONTROL||a>SC_INTERRUPT||(a&3))return DA_HALT;
 q->regs[index_of(a)]=v;q->known[index_of(a)]=k;++q->committed;return DA_RETURNED;
}
static void reset(void){
 memset(&f,0,sizeof(f));for(unsigned i=0;i<3;i++)f.known[i]=UINT32_MAX;
 f.ready_after=f.pll_after=f.switch_after=1;f.final_ready=-1;f.read_limit=10000;f.stop_flow=DA_HALT;
 io.context=&f;io.read=rd;io.write=wr;sc_init(&m,&io);
}
static const uint32_t sites[15]={0x184ae,0x184b8,0x184c4,0x184d0,0x184dc,0x184e2,0x184ee,0x18532,0x18536,0x1853e,0x18544,0x1854e,0x18558,0x1856c,0x18574};
static const uint32_t addresses[15]={SC_CONTROL,SC_CONFIG,SC_CONTROL,SC_CONTROL,SC_CONFIG,SC_INTERRUPT,SC_CONTROL,SC_CONFIG,SC_CONFIG,SC_CONFIG,SC_CONFIG,SC_CONFIG,SC_CONTROL,SC_CONFIG,SC_CONFIG};
static const uint32_t values[15]={1,0,1,1,0,0x9f0000,0x10001,0,0,0x400,0x400,0x290400,0x1030001,0x290400,0x290402};
static void success(void){
 unsigned j=0;++groups;reset();CK(sc_run(&m)==DA_RETURNED);CK(f.committed==15&&f.hse==1&&f.pll==1&&f.sw==1&&m.hse_iterations==1);
 for(unsigned i=0;i<f.logs;i++)if(f.log[i].write){CK(j<15);if(j<15){CK(f.log[i].site==sites[j]&&f.log[i].address==addresses[j]);CK(f.log[i].value==values[j]&&f.log[i].known==UINT32_MAX);}++j;}
 CK(j==15&&m.reads==f.reads&&m.writes==f.committed&&m.hse_ready==1);
 reset();f.ready_after=3;f.pll_after=4;f.switch_after=5;CK(sc_run(&m)==DA_RETURNED);CK(f.hse==3&&f.pll==4&&f.sw==5&&m.hse_iterations==3);
}
static void hse_boundaries(void){
 ++groups;reset();f.ready_after=0;CK(sc_run(&m)==DA_RETURNED);CK(f.hse==4096&&m.hse_iterations==4096&&f.committed==7&&f.pll==0&&f.sw==0);
 CK(f.logs&&f.log[f.logs-1].site==0x18510&&m.hse_ready==0);
 reset();f.ready_after=4096;CK(sc_run(&m)==DA_RETURNED);CK(f.hse==4096&&f.committed==15);
 reset();f.ready_after=0;f.final_ready=1;CK(sc_run(&m)==DA_RETURNED);CK(f.hse==4096&&f.pll==1&&f.committed==15);
 reset();f.final_ready=0;CK(sc_run(&m)==DA_RETURNED);CK(f.hse==1&&f.committed==7&&f.pll==0);
}
static void prefix(void){
 ++groups;
 for(unsigned i=0;i<15;i++)for(unsigned flow=0;flow<2;flow++){
  reset();f.stop_site=sites[i];f.stop_flow=flow?DA_TRANSFER:DA_HALT;
  CK(sc_run(&m)==f.stop_flow);CK(f.committed==i&&m.boundary_va==sites[i]&&m.boundary_address==addresses[i]);
  if(flow){unsigned logs=f.logs;CK(sc_run(&m)==DA_TRANSFER&&logs==f.logs);}
 }
 reset();f.stop_site=0x184a2;CK(sc_run(&m)==DA_HALT&&f.committed==0&&m.boundary_va==0x184a2);
 reset();io.read=0;CK(sc_run(&m)==DA_HALT&&m.boundary_va==0x184a2);
 reset();io.write=0;CK(sc_run(&m)==DA_HALT&&m.boundary_va==0x184ae);
}
static void unknown(void){
 ++groups;reset();f.unknown_site=0x184f6;f.unknown_mask=0x20000;CK(sc_run(&m)==DA_HALT);CK(m.boundary_va==0x18504&&m.needed_mask==0x20000&&f.committed==7&&m.hse_iterations==1);
 reset();f.unknown_site=0x18510;f.unknown_mask=0x20000;CK(sc_run(&m)==DA_HALT);CK(m.boundary_va==0x18516&&f.committed==7);
 reset();f.unknown_site=0x1855a;f.unknown_mask=0x2000000;CK(sc_run(&m)==DA_HALT);CK(m.boundary_va==0x18560&&m.needed_mask==0x2000000&&f.committed==13);
 reset();f.unknown_site=0x18578;f.unknown_mask=12;CK(sc_run(&m)==DA_HALT);CK(m.boundary_va==0x1857c&&m.needed_mask==12&&f.committed==15);
 reset();for(unsigned i=0;i<3;i++)f.known[i]=0;f.ready_after=0;f.unknown_site=0;CK(sc_run(&m)==DA_HALT);CK(f.log[1].known==1&&m.boundary_va==0x18504);
 reset();f.unknown_site=0x184f6;f.unknown_mask=~UINT32_C(0x20000);CK(sc_run(&m)==DA_RETURNED&&f.committed==15);
}
static void finite_provider(void){
 ++groups;reset();f.pll_after=0;f.read_limit=30;CK(sc_run(&m)==DA_HALT);CK(f.pll>1&&f.committed==13&&m.boundary_va==0x1855a);
 reset();f.switch_after=0;f.read_limit=40;CK(sc_run(&m)==DA_HALT);CK(f.sw>1&&f.committed==15&&m.boundary_va==0x18578);
 reset();f.stop_site=0x18578;f.stop_flow=DA_TRANSFER;CK(sc_run(&m)==DA_TRANSFER&&f.committed==15&&m.boundary_va==0x18578);
}
int main(void){success();hse_boundaries();prefix();unknown();finite_provider();printf("STARTUP_CLOCK_RESULT groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;}
