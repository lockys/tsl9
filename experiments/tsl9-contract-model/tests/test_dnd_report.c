#include "dnd_report.h"
#include <stdio.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define GP UINT32_C(0x20004000)
#define CFG UINT32_C(0x2000c298)
#define AUTH UINT32_C(0x2000c790)
#define FULL UINT32_MAX
static dr_machine machine;static dr_backend backend;
static uint8_t ram[65536],known[65536],scratch[84],scratch_known[84],dependency[8],dep_known[8];
static unsigned groups,checks,failures,native_calls,rom_calls,replies,out_calls;static uint32_t stop_site;static int transfer_stop,unclaimed_copy;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram[a-RAM+i]=(uint8_t)(v>>(8*i));known[a-RAM+i]=255;}}
static da_flow stop(uint32_t site){return site==stop_site?(transfer_stop?DA_TRANSFER:DA_HALT):DA_RETURNED;}
static da_flow read_ram(void *p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar *out){
 unsigned i;CHECK(p==ram);if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;
 out->value=out->known=0;for(i=0;i<n;i++){out->value|=(uint32_t)ram[a-RAM+i]<<(8*i);out->known|=(uint32_t)known[a-RAM+i]<<(8*i);}
 return (out->known&need)==need?DA_RETURNED:DA_HALT;
}
static da_flow write_ram(void *p,uint32_t a,uint32_t v,unsigned n,uint32_t mask,uint32_t site){
 unsigned i;CHECK(p==ram);if(stop(site)!=DA_RETURNED)return stop(site);if(n>4||a<RAM||a>RAM+65536-n)return DA_HALT;
 put(a,v,n);for(i=0;i<n;i++)known[a-RAM+i]=(uint8_t)(mask>>(8*i));return DA_RETURNED;
}
static da_flow call(void *p,da_kind kind,uint32_t target,uint32_t site,const da_scalar *args,unsigned n,da_scalar *out){
 CHECK(p==ram);out->value=out->known=0;
 if(kind==DA_NATIVE){++native_calls;return DA_HALT;}++rom_calls;
 if(stop(site)!=DA_RETURNED)return stop(site);
 if(kind==DA_ROM&&target==124){out->value=100;out->known=FULL;return DA_RETURNED;}
 if(kind==DA_ROM&&target==112){CHECK(n==1&&args[0].value==12);out->value=0;out->known=FULL;return DA_RETURNED;}
 if(kind==DA_ROM&&(target==56||target==88||target==92)){out->known=FULL;return DA_RETURNED;}
 return DA_HALT;
}
static da_flow schedule(void *p,uint32_t cb,uint32_t delay,uint32_t site,da_scalar *out){CHECK(p==ram);CHECK(cb==0x13160&&delay==35);out->value=0xdeadbeef;out->known=0x00ff00ff;return stop(site);}
static da_flow report_invoke(void *p,const rp_request *r,rp_result *out){
 unsigned i;CHECK(p==ram);++out_calls;out->scalar.value=out->scalar.known=0;out->memory_effects=0;
 if(stop(r->callsite)!=DA_RETURNED){if(r->buffer_length){r->buffer[0]=0x12;r->buffer_known[0]=255;}return stop(r->callsite);}
 if(r->target==96){out->scalar.value=0;out->scalar.known=FULL;return DA_RETURNED;}
 if(unclaimed_copy&&r->callsite==0x92b4)return DA_RETURNED;
 for(i=0;i<r->buffer_length;i++){
  uint32_t a=r->arguments[1].value+i;
  if(r->target==72){r->buffer[i]=0;r->buffer_known[i]=255;}
  else if(a>=RAM&&a<RAM+65536){r->buffer[i]=ram[a-RAM];r->buffer_known[i]=known[a-RAM];}
  else{r->buffer[i]=(uint8_t)i;r->buffer_known[i]=255;}
 }
 out->memory_effects=1;return DA_RETURNED;
}
static da_flow report_reply(void *p,const rp_reply *r){CHECK(p==ram);++replies;CHECK(r->data==scratch+8&&r->known==scratch_known+8&&r->length==76&&r->handle==7&&r->command==0xa0);return stop(r->callsite);}
static void fixture(void){
 rp_storage a={scratch,scratch_known,84},b={dependency,dep_known,8};memset(ram,0,sizeof(ram));memset(known,255,sizeof(known));memset(&backend,0,sizeof(backend));
 put(GP+84,CFG,4);put(GP+175,1,1);put(GP+365,9,1);put(AUTH+2,7,2);put(AUTH+6,65534,2);
 backend.core.context=ram;backend.core.read=read_ram;backend.core.write=write_ram;backend.core.call=call;backend.core.schedule=schedule;backend.report_invoke=report_invoke;backend.report_reply=report_reply;
 native_calls=rom_calls=replies=out_calls=0;stop_site=0;transfer_stop=unclaimed_copy=0;dr_init(&machine,&backend,a,b);
}
static void direct_and_core_chain(void){da_scalar out;++groups;fixture();CHECK(dr_run_pair(&machine,0x13160,123,0,&out)==DA_RETURNED);CHECK(native_calls==0&&replies==1&&out_calls==7&&out.known==0);
 fixture();CHECK(dr_run_pair(&machine,0x13b5c,0,0,&out)==DA_RETURNED);CHECK(native_calls==0&&rom_calls==1&&replies==1&&out.known==0);
 fixture();CHECK(dr_run_pair(&machine,0x170e2,0,12,&out)==DA_RETURNED);CHECK(out.value==8&&out.known==FULL&&replies==1&&native_calls==0);
}
static void deferred_scalar_and_feedback(void){da_scalar out;++groups;fixture();put(GP+344,62,4);CHECK(dr_run_pair(&machine,0x13b5c,0,0,&out)==DA_RETURNED);CHECK(out.value==0xdeadbeef&&out.known==0x00ff00ff&&out_calls==0);
 fixture();CHECK(dr_run_pair(&machine,0x17048,1,1,&out)==DA_RETURNED);CHECK(native_calls==0&&rom_calls==4&&ram[GP+364-RAM]==1);CHECK(ram[0xbecc]==0&&replies==0); /* interval ROM56/88/88 precedes feedback allocation. */
}
static void failures_keep_inner_sites(void){unsigned t;da_scalar out;++groups;for(t=0;t<2;t++){fixture();stop_site=0x92b4;transfer_stop=(int)t;
 CHECK(dr_run_pair(&machine,0x170e2,0,4,&out)==(t?DA_TRANSFER:DA_HALT));CHECK(machine.boundary_va==0x92b4&&machine.boundary_address==76);
 CHECK(ram[GP+344-RAM]==62&&scratch[12]==0x12&&scratch_known[12]==255&&replies==0&&native_calls==0);
 if(t){unsigned n=rom_calls+out_calls;CHECK(dr_run_pair(&machine,0x13b5c,0,0,&out)==DA_TRANSFER);CHECK(rom_calls+out_calls==n);}
 }
 fixture();known[AUTH+5-RAM]=0;CHECK(dr_run_pair(&machine,0x13160,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x131ee&&machine.needed_mask==255);
 fixture();unclaimed_copy=1;CHECK(dr_run_pair(&machine,0x13160,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x92b4&&replies==0);
}
static void absent_backend_is_not_fallback(void){da_scalar out;rp_storage a={scratch,scratch_known,84},b={dependency,dep_known,8};++groups;fixture();backend.report_invoke=0;
 CHECK(dr_run_pair(&machine,0x170e2,0,4,&out)==DA_HALT);CHECK(native_calls==0&&machine.boundary_va==0x9db4);
 fixture();backend.report_reply=0;CHECK(dr_run_pair(&machine,0x13160,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x133bc&&replies==0);
 dr_init(&machine,0,a,b);CHECK(dr_run_pair(&machine,0x13160,0,0,&out)==DA_HALT);CHECK(machine.boundary_va==0x9db4);
}
int main(void){direct_and_core_chain();deferred_scalar_and_feedback();failures_keep_inner_sites();absent_backend_is_not_fallback();printf("DND_REPORT_RESULT groups=%u checks=%u failures=%u\n",groups,checks,failures);return failures?1:0;}
