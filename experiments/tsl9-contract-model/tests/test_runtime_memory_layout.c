#include "runtime_memory_layout.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "fixtures/memory_witnesses_r57.h"
static unsigned checks,failures;
#define CHECK(x) do{checks++;if(!(x)){failures++;printf("FAIL line %u\n",(unsigned)__LINE__);}}while(0)
static int block(const char *path,long offset,unsigned char *out){
 FILE *f=fopen(path,"rb");int ok;if(!f)return 0;
 ok=fseek(f,offset,SEEK_SET)==0&&fread(out,1,148,f)==148;fclose(f);return ok;
}
static int cleared(const rml_layout *p){
 const unsigned char *b=(const unsigned char *)p;size_t i;
 for(i=0;i<sizeof(*p);i++)if(b[i])return 0;return 1;
}
static void values(const rml_layout *p,int boot){
 CHECK(p->reset==(boot?UINT32_C(0x2bd8):UINT32_C(0x183fe)));
 CHECK(p->gp==UINT32_C(0x20004000));CHECK(p->sp==UINT32_C(0x20010000));
 CHECK(p->data_load==(boot?UINT32_C(0x3e90):UINT32_C(0x1a7e0)));
 CHECK(p->data_start==UINT32_C(0x20004000));
 CHECK(p->data_end==(boot?UINT32_C(0x20004068):UINT32_C(0x20004088)));
 CHECK(p->bss_start==p->data_end);
 CHECK(p->bss_end==(boot?UINT32_C(0x200099a0):UINT32_C(0x2000c950)));
 CHECK(p->vector==(boot?UINT32_C(0x1038):UINT32_C(0x8038)));
 CHECK(p->mtvec_value==(p->vector|3u));
 CHECK(p->clock_entry==(boot?UINT32_C(0x2c78):UINT32_C(0x1849e)));
 CHECK(p->runtime_entry==(boot?UINT32_C(0x1a52):UINT32_C(0x8fe6)));
 CHECK(p->rom_entry==UINT32_C(0x40000));
 CHECK(p->data_bytes==(boot?104u:136u));CHECK(p->bss_bytes==(boot?22840u:35016u));
 CHECK(p->numeric_gap_to_sp==(boot?26208u:14000u));
}
static void ranges(const rml_layout *p){
 CHECK(rml_classify_range(p,p->data_start,1)==RML_RANGE_DATA);
 CHECK(rml_classify_range(p,p->data_end-4u,4)==RML_RANGE_DATA);
 CHECK(rml_classify_range(p,p->bss_start,4)==RML_RANGE_BSS);
 CHECK(rml_classify_range(p,p->bss_end-1u,1)==RML_RANGE_BSS);
 CHECK(rml_classify_range(p,p->data_end-1u,2)==RML_RANGE_CROSSES);
 CHECK(rml_classify_range(p,p->data_start-1u,2)==RML_RANGE_CROSSES);
 CHECK(rml_classify_range(p,p->bss_end-1u,2)==RML_RANGE_CROSSES);
 CHECK(rml_classify_range(p,p->bss_end,1)==RML_RANGE_OUTSIDE);
 CHECK(rml_classify_range(p,UINT32_C(0x20000004),4)==RML_RANGE_OUTSIDE);
 CHECK(rml_classify_range(p,UINT32_C(0x20000008),4)==RML_RANGE_OUTSIDE);
 CHECK(rml_classify_range(p,UINT32_C(0x20004180),4)==RML_RANGE_BSS);
 CHECK(rml_classify_range(p,p->data_start,0)==RML_RANGE_EMPTY);
 CHECK(rml_classify_range(p,UINT32_C(0xfffffff0),32)==RML_RANGE_WRAP);
 CHECK(rml_classify_range(NULL,p->data_start,1)==RML_RANGE_OUTSIDE);
}
static void negative(const unsigned char *p,uint32_t reset,uint32_t base,uint32_t length){
 static const unsigned corrupt[]={0,4,8,12,24,32,36,40,44,46,48,64,68,72,74,80,86,98,110,114,118,130,134,138,142,146};
 unsigned char q[148];rml_layout v;size_t i;
 for(i=0;i<sizeof(corrupt)/sizeof(corrupt[0]);i++){
  memcpy(q,p,148);q[corrupt[i]]^=1u;memset(&v,0xff,sizeof(v));
  CHECK(rml_decode_reset(q,148,reset,base,length,&v)==RML_BAD_PATTERN);CHECK(cleared(&v));
 }
 CHECK(rml_decode_reset(p,147,reset,base,length,&v)==RML_BAD_ARGUMENT);CHECK(cleared(&v));
 CHECK(rml_decode_reset(NULL,148,reset,base,length,&v)==RML_BAD_ARGUMENT);
 CHECK(rml_decode_reset(p,148,reset,base,length,NULL)==RML_BAD_ARGUMENT);
 CHECK(rml_decode_reset(p,148,reset,base,1,&v)==RML_OUTSIDE_IMAGE);
 memcpy(q,p,148);q[54]^=UINT8_C(0x40); /* BSS start immediate: break the shared endpoint. */
 CHECK(rml_decode_reset(q,148,reset,base,length,&v)==RML_BAD_LAYOUT);CHECK(cleared(&v));
 memcpy(q,p,148);q[55]^=UINT8_C(0x01); /* BSS start differs from copy end by16. */
 CHECK(rml_decode_reset(q,148,reset,base,length,&v)==RML_BAD_LAYOUT);
}
static void emit(const rml_layout *p){
 printf("{\"reset\":%" PRIu32 ",\"gp\":%" PRIu32 ",\"sp\":%" PRIu32
 ",\"data_load\":%" PRIu32 ",\"data_start\":%" PRIu32 ",\"data_end\":%" PRIu32
 ",\"bss_start\":%" PRIu32 ",\"bss_end\":%" PRIu32 ",\"vector\":%" PRIu32
 ",\"mtvec_value\":%" PRIu32 ",\"clock_entry\":%" PRIu32 ",\"runtime_entry\":%" PRIu32
 ",\"rom_entry\":%" PRIu32 ",\"data_bytes\":%" PRIu32 ",\"bss_bytes\":%" PRIu32
 ",\"numeric_gap_to_sp\":%" PRIu32 "}",p->reset,p->gp,p->sp,p->data_load,p->data_start,p->data_end,
 p->bss_start,p->bss_end,p->vector,p->mtvec_value,p->clock_entry,p->runtime_entry,p->rom_entry,
 p->data_bytes,p->bss_bytes,p->numeric_gap_to_sp);
}
static unsigned witness_checks,witness_failures,hand_witness_checks,gp_fixture_checks,gp_fixture_rows;
static int witness_cleared(const rml_witness_report *p){
 const unsigned char *b=(const unsigned char *)p;size_t i;
 for(i=0;i<sizeof(*p);i++)if(b[i])return 0;return 1;
}
static void witnesses(const rml_layout *runtime,const rml_layout *boot){
 unsigned before=checks,bad_before=failures;rml_layout shifted,high;size_t index;
 rml_witness w;rml_witness_report out;
 memset(&w,0,sizeof(w));w.use=RML_WITNESS_READ;w.gp_relative=1;
 w.address=UINT32_C(0x20004000);w.bytes=4;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.address==w.address&&out.bytes==4);
 CHECK(out.point_region==RML_RANGE_DATA&&out.window_region==RML_RANGE_DATA);
 CHECK(out.reset_copy_covers_window&&!out.reset_zero_covers_window&&!out.gp_wrapped);
 CHECK(!out.pointer_provider_required);
 w.address=UINT32_C(0x20004180);w.gp_offset=384;w.use=RML_WITNESS_POINTER_LOAD;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.point_region==RML_RANGE_BSS&&out.window_region==RML_RANGE_BSS);
 CHECK(out.reset_zero_covers_window&&!out.reset_copy_covers_window);
 CHECK(out.pointer_provider_required); /* Zeroing is not a callable provider. */
 CHECK(rml_observe_witness(boot,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_BSS&&out.pointer_provider_required);
 w.gp_relative=0;w.gp_offset=0;w.address=UINT32_C(0x20000000);
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_OUTSIDE&&out.pointer_provider_required);
 CHECK(!out.reset_copy_covers_window&&!out.reset_zero_covers_window);
 w.address=UINT32_C(0x20000004);
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_OUTSIDE&&out.pointer_provider_required);
 w.address=UINT32_C(0x20000008); /* Synthetic negative control: no source provider claim. */
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_OUTSIDE&&out.pointer_provider_required);
 w.address=UINT32_C(0x40070);
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_OUTSIDE&&out.pointer_provider_required);
 w.address=UINT32_C(0x2000c91c);w.bytes=0;w.use=RML_WITNESS_ADDRESS;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.point_region==RML_RANGE_BSS&&out.window_region==RML_RANGE_EMPTY);
 CHECK(!out.reset_copy_covers_window&&!out.reset_zero_covers_window);
 CHECK(rml_observe_witness(boot,&w,&out)==RML_OK);
 CHECK(out.point_region==RML_RANGE_OUTSIDE&&out.window_region==RML_RANGE_EMPTY);
 w.address=UINT32_C(0x19a94);
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.point_region==RML_RANGE_OUTSIDE&&out.window_region==RML_RANGE_EMPTY);
 w.address=UINT32_C(0x2000c790);w.bytes=1;w.use=RML_WITNESS_WRITE;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_BSS&&out.reset_zero_covers_window);
 w.address=runtime->data_end-1u;w.bytes=2;w.use=RML_WITNESS_READ;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_CROSSES&&!out.reset_copy_covers_window&&!out.reset_zero_covers_window);
 w.address=UINT32_C(0xfffffffe);w.bytes=4;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_WRAP);
 /* Preserve the existing conservative one-past uint32 endpoint policy. */
 w.address=UINT32_MAX;w.bytes=0;w.use=RML_WITNESS_ADDRESS;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.point_region==RML_RANGE_WRAP&&out.window_region==RML_RANGE_EMPTY);
 CHECK(rml_classify_range(runtime,UINT32_MAX,1u)==RML_RANGE_WRAP);
 w.bytes=4;w.use=RML_WITNESS_READ;
 w.address=UINT32_C(0x20004070);w.gp_offset=112;w.gp_relative=1;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_DATA);
 CHECK(rml_observe_witness(boot,&w,&out)==RML_OK);
 CHECK(out.window_region==RML_RANGE_BSS); /* Same GP does not make profiles interchangeable. */
 w.address=UINT32_C(0xa0004000);w.gp_offset=INT32_MIN;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);
 CHECK(out.gp_wrapped&&out.window_region==RML_RANGE_OUTSIDE);
 shifted=*runtime;shifted.gp+=4;shifted.data_start+=4;shifted.data_end+=4;
 shifted.bss_start+=4;shifted.bss_end+=4;shifted.sp+=4;
 w.address=UINT32_C(0x20004180);w.gp_offset=384;w.use=RML_WITNESS_POINTER_LOAD;
 memset(&out,0xff,sizeof(out));
 CHECK(rml_observe_witness(&shifted,&w,&out)==RML_BAD_LAYOUT);CHECK(witness_cleared(&out));
 high=*runtime;high.gp=UINT32_C(0xffff0000);high.data_start=high.gp;
 high.data_end=high.gp+136u;high.bss_start=high.data_end;high.bss_end=high.gp+UINT32_C(0x100);
 high.bss_bytes=high.bss_end-high.bss_start;high.sp=UINT32_C(0xffff1000);
 w.address=0;w.gp_offset=65536;
 CHECK(rml_observe_witness(&high,&w,&out)==RML_OK);CHECK(out.gp_wrapped);
 w.address=UINT32_C(0x20004180);w.gp_offset=384;
 CHECK(rml_observe_witness(NULL,&w,&out)==RML_BAD_ARGUMENT);CHECK(witness_cleared(&out));
 CHECK(rml_observe_witness(runtime,NULL,&out)==RML_BAD_ARGUMENT);CHECK(witness_cleared(&out));
 CHECK(rml_observe_witness(runtime,&w,NULL)==RML_BAD_ARGUMENT);
 w.gp_relative=2;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);CHECK(witness_cleared(&out));
 w.gp_relative=0;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.gp_offset=0;w.bytes=2;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=RML_WITNESS_ADDRESS;w.bytes=1;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=RML_WITNESS_READ;w.bytes=0;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.bytes=3;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=RML_WITNESS_WRITE;w.bytes=8;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=RML_WITNESS_SPAN;w.bytes=0;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=(rml_witness_use)99;w.bytes=4;CHECK(rml_observe_witness(runtime,&w,&out)==RML_BAD_ARGUMENT);
 w.use=RML_WITNESS_READ;shifted=*runtime;shifted.bss_end=shifted.bss_start-4u;
 CHECK(rml_observe_witness(&shifted,&w,&out)==RML_BAD_LAYOUT);CHECK(witness_cleared(&out));
 shifted=*runtime;shifted.data_bytes--;
 CHECK(rml_observe_witness(&shifted,&w,&out)==RML_BAD_LAYOUT);
 /* A synthetic geometry window is not a claimed ROM40048 byte footprint. */
 w.address=UINT32_C(0x2000c91c);w.bytes=52;w.use=RML_WITNESS_SPAN;
 CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);CHECK(out.window_region==RML_RANGE_BSS);
 w.bytes=53;CHECK(rml_observe_witness(runtime,&w,&out)==RML_OK);CHECK(out.window_region==RML_RANGE_CROSSES);
 hand_witness_checks=checks-before;
 for(index=0;index<R57_GP_FIXTURE_COUNT;index++){
  const r57_gp_fixture *f=&r57_gp_fixtures[index];unsigned profile;
  CHECK(f->original_pc!=0u);gp_fixture_rows++;
  for(profile=0;profile<2u;profile++){
   const rml_layout *p=profile?boot:runtime;
   rml_range point=profile?f->boot_point:f->runtime_point;
   rml_range window=profile?f->boot_window:f->runtime_window;
   CHECK(rml_observe_witness(p,&f->witness,&out)==RML_OK);
   CHECK(out.address==f->witness.address&&out.bytes==f->witness.bytes);
   CHECK(out.point_region==point);CHECK(out.window_region==window);
   CHECK(out.gp_wrapped==f->gp_wrapped);
   CHECK(out.pointer_provider_required==f->pointer_provider_required);
   CHECK(out.reset_copy_covers_window==(unsigned)(window==RML_RANGE_DATA));
   CHECK(out.reset_zero_covers_window==(unsigned)(window==RML_RANGE_BSS));
  }
 }
 gp_fixture_checks=checks-before-hand_witness_checks;
 witness_failures=failures-bad_before;
 witness_checks=checks-before;
}

int main(int argc,char **argv){
 static const uint32_t origins[]={UINT32_C(0x2000c034),UINT32_C(0x2000bebc),UINT32_C(0x2000be08),UINT32_C(0x2000c790),UINT32_C(0x2000b18c),UINT32_C(0x19a94),UINT32_C(0x2000bfd0),UINT32_C(0x2000bfe8),UINT32_C(0x2000bfc4),UINT32_C(0x2000c79c),UINT32_C(0x2000c8a8),UINT32_C(0x1a76c),UINT32_C(0x2000c28c),UINT32_C(0x2000c1b4),UINT32_C(0x2000bfb4),UINT32_C(0x2000c490),UINT32_C(0x2000c308),UINT32_C(0x2000c590),UINT32_C(0x2000c690),UINT32_C(0x2000c408),UINT32_C(0x2000c298),UINT32_C(0x1a334),UINT32_C(0x2000bed0),UINT32_C(0x2000bee0),UINT32_C(0x2000beec),UINT32_C(0x2000befc),UINT32_C(0x2000bf18),UINT32_C(0x2000bf24),UINT32_C(0x2000bf34),UINT32_C(0x2000bf44),UINT32_C(0x2000bf58),UINT32_C(0x2000bf64),UINT32_C(0x2000bf80),UINT32_C(0x2000bf8c),UINT32_C(0x2000bfa4),UINT32_C(0x2000c91c),UINT32_C(0x2000c790)};
 unsigned char r[148],b[148];rml_layout runtime,boot;size_t i;
 if(argc!=3||!block(argv[1],0x103feL,r)||!block(argv[2],0x1bd8L,b)){fprintf(stderr,"Cannot read declared reset code ranges\n");return 2;}
 CHECK(rml_decode_reset(r,148,UINT32_C(0x183fe),UINT32_C(0x8000),76800,&runtime)==RML_OK);
 CHECK(rml_decode_reset(b,148,UINT32_C(0x2bd8),UINT32_C(0x1000),12288,&boot)==RML_OK);
 values(&runtime,0);values(&boot,1);ranges(&runtime);ranges(&boot);
 negative(r,UINT32_C(0x183fe),UINT32_C(0x8000),76800);negative(b,UINT32_C(0x2bd8),UINT32_C(0x1000),12288);
 for(i=0;i<sizeof(origins)/sizeof(origins[0]);i++){
  int ram=origins[i]>=UINT32_C(0x20000000);
  CHECK(rml_classify_range(&runtime,origins[i],1)==(ram?RML_RANGE_BSS:RML_RANGE_OUTSIDE));
  CHECK(rml_classify_range(&boot,origins[i],1)==RML_RANGE_OUTSIDE);
 }
 CHECK(rml_classify_range(&runtime,UINT32_C(0x2000c91c),52)==RML_RANGE_BSS);
 CHECK(UINT32_C(0x2000c91c)+52u==runtime.bss_end);
 CHECK(rml_classify_range(&runtime,UINT32_C(0x2000c790),10)==RML_RANGE_BSS);
 CHECK(rml_classify_range(&runtime,UINT32_C(0x2000bfb0),20)==RML_RANGE_BSS);
 CHECK(runtime.data_end!=boot.data_end);CHECK(runtime.bss_end!=boot.bss_end);
 witnesses(&runtime,&boot);
 printf("RUNTIME_MEMORY_RESULT {\"passed\":%s,\"checks\":%u,\"failures\":%u,\"runtime\":",failures?"false":"true",checks,failures);
 emit(&runtime);printf(",\"boot\":");emit(&boot);
 printf(",\"legacy_checks\":%u,\"legacy_failures\":%u,\"witness_checks\":%u,\"witness_failures\":%u,\"hand_witness_checks\":%u,\"gp_fixture_checks\":%u,\"gp_fixture_rows\":%u,\"origin_references_checked\":%u,\"target_executed\":false,\"emulation\":false,\"hardware\":false}\n",checks-witness_checks,failures-witness_failures,witness_checks,witness_failures,hand_witness_checks,gp_fixture_checks,gp_fixture_rows,(unsigned)(sizeof(origins)/sizeof(origins[0])));
 return failures?1:0;
}
