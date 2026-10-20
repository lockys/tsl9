#include "can_receive.h"
#include <string.h>
#include <stdio.h>
#define ALL UINT32_C(0xffffffff)
#define A(x) (TF_RAM_BASE+UINT32_C(x))
#define Q A(0xc034)
#define AUTH A(0xc790)
static tf_model ram;static cr_model model;
static cr_request events[512];static uint8_t event_bytes[512][3];static unsigned nevents;
static unsigned groups,checks,failures,copies,replies,d1;
static uint8_t image[76800],frames[2][60],framek[2][60];static uint32_t lens[2],handles[2];
static uint32_t fail_site,alloc_value,alloc_mask;
static cr_flow fail_flow;
static int no_effects,mutate_debug,activate_second,partial_copy,mutate_cache;
static uint32_t io_value,io_known;
static unsigned observer_after_copy;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static uint32_t read(uint32_t a,unsigned n){uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static cr_buffer rv(uint32_t a){cr_buffer b;memset(&b,0,sizeof(b));b.kind=CR_RAM;b.address=a;return b;}
static int byte(cr_buffer b,unsigned i,uint8_t **v,uint8_t **k){if(b.kind==CR_RAM){uint32_t a=b.address+i;if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE)return 0;*v=&ram.ram[a-TF_RAM_BASE];*k=&ram.known[a-TF_RAM_BASE];return 1;}if(b.kind!=CR_VIEW||!b.data||!b.known||i>=b.available)return 0;*v=b.data+i;*k=b.known+i;return 1;}
static cr_flow backend(void *ctx,cr_model*m,const cr_request*q,cr_result*r){
 unsigned i;uint8_t *v,*k,*d,*dk;(void)ctx;CHECK(m->memory==&ram);CHECK(nevents<512);if(nevents>=512)return CR_HALT;events[nevents]=*q;
 for(i=0;i<3;i++)if(byte(q->source,i,&v,&k))event_bytes[nevents][i]=*v;
 ++nevents;
 if(q->va==fail_site&&!partial_copy)return fail_flow;
 r->value=0;r->known=0;
 if(q->operation==CR_COPY){
  ++copies;if(q->argument_known[2]!=ALL)return CR_HALT;
  for(i=0;i<q->length;i++){if(!byte(q->source,i,&v,&k)||!byte(q->destination,i,&d,&dk))return CR_HALT;*d=*v;*dk=*k;if(q->va==fail_site&&partial_copy)return fail_flow;}
  r->memory_effects=!no_effects;
  if(mutate_debug&&q->va==0x834c){put(A(0xd002),5,1);put(AUTH+2,9,2);}
  if(mutate_cache&&q->va==0x82c0&&q->source.kind==CR_VIEW){q->source.data[3]=0xa5;q->source.known[3]=15;}
  if(observer_after_copy&&q->va==0x82c0){
   if(observer_after_copy==1&&byte(q->source,3,&v,&k)){*v=2;*k=255;}
   if(observer_after_copy==2&&byte(q->source,4,&v,&k)){*v=14;*k=255;}
   if(observer_after_copy==3)put(TF_GP+220,0,4);
  }
  return CR_RETURNED;
 }
 if(q->operation==CR_REPLY){
  CHECK(replies<2);if(replies<2){lens[replies]=q->arguments[3];handles[replies]=q->arguments[0];memcpy(frames[replies],q->source.data,q->source.available<60?q->source.available:60);memcpy(framek[replies],q->source.known,q->source.available<60?q->source.available:60);}
  ++replies;if(activate_second&&replies==1){put(AUTH+6,11,2);put(AUTH+8,4,1);put(AUTH+9,2,1);}return CR_RETURNED;
 }
 if(q->operation==CR_D1_TAIL){++d1;CHECK(q->va==0x15048&&q->target==0x139e6);CHECK(q->source.kind==CR_VIEW||q->source.kind==CR_RAM);return CR_RETURNED;}
 if(q->operation==CR_MMIO_READ){r->value=io_value;r->known=io_known;return CR_RETURNED;}
 if(q->operation==CR_ALLOC){r->value=alloc_value;r->known=alloc_mask;return q->argument_known[0]==ALL?CR_RETURNED:CR_HALT;}
 if(q->operation==CR_GENERAL_CALL){CHECK(q->target==0x13a62&&q->count==1);CHECK(q->source.kind==CR_RAM||q->source.kind==CR_VIEW);CHECK(q->argument_known[0]==(q->source.kind==CR_RAM?ALL:0));return CR_RETURNED;}
 if(q->operation==(cr_operation)11){CHECK(q->target==0x9102&&q->count==4);CHECK(q->arguments[0]==0x1063c&&q->arguments[1]==0&&q->arguments[2]==2000&&q->arguments[3]==0);for(i=0;i<4;i++)CHECK(q->argument_known[i]==ALL);r->value=0xdeadbeef;r->known=0;return CR_RETURNED;}
 if(q->operation==CR_FREE||q->operation==CR_NATIVE_CALL||q->operation==CR_MMIO_WRITE||q->operation==CR_CSR_CLEAR||q->operation==CR_CSR_SET)return CR_RETURNED;
 return CR_HALT;
}
static void fresh(void){cr_backend b;memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(events,0,sizeof(events));nevents=copies=replies=d1=0;fail_site=0;fail_flow=CR_HALT;alloc_value=0;alloc_mask=ALL;io_value=0;io_known=0;observer_after_copy=0;no_effects=mutate_debug=activate_second=partial_copy=mutate_cache=0;put(TF_GP+84,A(0xd100),4);put(AUTH+2,7,2);put(AUTH+6,65534,2);put(A(0xbfb1),1,1);b.context=NULL;b.invoke=backend;cr_init(&model,&ram,&b);}
static cr_arguments record(uint32_t a){cr_arguments r;memset(&r,0,sizeof(r));r.record=rv(a);return r;}
static void frame(uint32_t a,uint16_t id,uint8_t dlc,uint8_t channel){unsigned i;put(a,id,2);put(a+2,dlc,1);for(i=0;i<8;i++)put(a+3+i,0x30+i,1);put(a+11,channel,1);}
static const cr_request *find(cr_operation op,uint32_t va){unsigned i;for(i=0;i<nevents;i++)if(events[i].operation==op&&events[i].va==va)return &events[i];return NULL;}
static uint8_t observed_byte(cr_operation op,uint32_t va,unsigned off){unsigned i;for(i=0;i<nevents;i++)if(events[i].operation==op&&events[i].va==va)return event_bytes[i][off];return 255;}
static void debug_scalar_and_effects(void){
 cr_arguments a;const cr_request*q;++groups;fresh();frame(A(0xd000),0x12ff,9,3);a=record(A(0xd000));put(AUTH+4,2,1);put(AUTH+5,2,1);ram.known[0xc794]=2;put(AUTH,128,1);
 CHECK(cr_run(&model,CR_DEBUG,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==2&&model.result_known==0xffffff02);CHECK(copies==0&&replies==0);
 fresh();frame(A(0xd000),0x12ff,1,3);a=record(A(0xd000));put(AUTH+4,1,1);put(AUTH+5,2,1);mutate_debug=activate_second=1;
 CHECK(cr_run(&model,CR_DEBUG,&a)==CR_RETURNED);CHECK(replies==2&&copies==2);CHECK(handles[0]==9&&handles[1]==11); /* second live native handle is11; corrected below */
 CHECK(lens[0]==7&&lens[1]==7);CHECK(frames[0][0]==0x32&&frames[0][1]==255&&frames[0][2]==0x30);CHECK(framek[0][3]==0&&framek[0][6]==0);CHECK(frames[1][3]==0x31&&framek[1][6]==255);CHECK(model.result==4&&model.result_known==ALL);
 q=find(CR_COPY,0x834c);CHECK(q&&q->length==1&&q->source.address==A(0xd003)&&q->destination.kind==CR_VIEW&&q->destination.address==0);
 fresh();frame(A(0xd000),0x401,1,0);a=record(A(0xd000));put(AUTH+4,1,1);put(AUTH+5,2,1);fail_site=0x835e;fail_flow=CR_TRANSFER;
 CHECK(cr_run(&model,CR_DEBUG,&a)==CR_TRANSFER);CHECK(copies==1&&replies==0&&!model.result_defined);
}
static void dispatch_schema(void){
 cr_arguments a;const cr_request*q;++groups;fresh();frame(A(0xd000),0x401,0,2);a=record(A(0xd000));ram.known[0xd002]=0;ram.known[0xd00b]=0;
 CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(d1==1&&nevents==1&&!model.result_defined);q=find(CR_D1_TAIL,0x15048);CHECK(q&&q->source.address==A(0xd000)&&q->source.kind==CR_RAM);
 fresh();a=record(A(0xd000));frame(A(0xd000),0,8,0);ram.known[0xd000]=254;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(nevents==0);
 fresh();frame(A(0xd000),0x132,8,0);a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&read(A(0xc1c0),2)==0x132&&nevents==1);
 fresh();put(A(0xbfb1),5,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(model.boundary_va==0x14b1a&&model.boundary_address==0x151e2);
 fresh();put(A(0xbfb1),128,1);ram.known[0xbfb1]=128;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(model.boundary_va==0x1524a&&model.boundary_address==0x105c8);
 fresh();CHECK(cr_run(&model,0x15048,&a)==CR_HALT&&model.boundary_va==0x15048);
}
static void queue_flow_and_snapshot(void){
 const cr_request*q;++groups;fresh();frame(Q,0x401,1,0);fail_site=0x15048;fail_flow=CR_TRANSFER;
 CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_TRANSFER);CHECK(read(Q,2)==0&&read(Q+2,1)==1&&copies==1);CHECK(model.consumed==1&&model.dispatch_calls==1);CHECK(find(CR_CSR_CLEAR,0x12aa6)&&find(CR_CSR_SET,0x12aba));q=find(CR_D1_TAIL,0x15048);CHECK(q&&q->source.kind==CR_VIEW&&q->source.address==0&&q->source.data==model.record_value&&q->source.data[0]==1&&q->source.data[1]==4);CHECK(!model.result_defined);
 fresh();frame(Q,0x401,1,0);fail_site=0x12ab4;fail_flow=CR_TRANSFER;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_TRANSFER);CHECK(read(Q,2)==0x401&&model.consumed==0&&!find(CR_CSR_SET,0x12aba));
 fresh();frame(Q,0x401,1,0);fail_site=0x12aba;fail_flow=CR_TRANSFER;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_TRANSFER);CHECK(read(Q,2)==0&&model.consumed==1&&model.debug_calls==0);
 fresh();frame(Q,0x401,9,0);put(AUTH+4,2,1);put(AUTH+5,2,1);ram.known[0xc794]=2;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_RETURNED);CHECK(read(Q,2)==0&&model.debug_calls==1&&model.dispatch_calls==0&&d1==0);
 fresh();ram.known[0xc034]=254;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_HALT);CHECK(model.boundary_va==0x12aa4&&copies==0);
}
static void control_echo_and_counter(void){
 const cr_request*q;++groups;fresh();frame(Q,1,4,2);put(Q+3,181,1);put(Q+4,98,1);put(Q+5,90,1);put(Q+6,85,1);put(A(0xd104),8,1);fail_site=0x12b82;fail_flow=CR_TRANSFER;
 CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_TRANSFER);CHECK(read(Q,2)==0&&copies==2);q=find(CR_NATIVE_CALL,0x12b82);CHECK(q&&q->target==0x12864&&q->source.kind==CR_VIEW&&q->source.data[6]==86&&q->source.data[11]==0);
 fresh();frame(Q,1,4,2);put(Q+3,181,1);put(Q+4,98,1);put(Q+5,0,1);put(Q+6,0,1);put(TF_GP+193,9,1);put(TF_GP+176,0,1);io_value=0x12345678;io_known=0xabcdef01;
 CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_RETURNED);CHECK(read(TF_GP+193,1)==0);q=find(CR_MMIO_WRITE,0x9b26);CHECK(q&&q->target==0x4001080c&&q->value==(0x12345678^2u)&&q->known==io_known);
 q=find(CR_NATIVE_CALL,0x12b3c);CHECK(q&&q->target==0x1290a&&q->arguments[0]==2&&observed_byte(CR_NATIVE_CALL,0x12b3c,0)==0);
 q=find(CR_NATIVE_CALL,0x12b56);CHECK(q&&q->arguments[0]==1&&q->source.data[0]==1&&q->source.available==2);
 CHECK(model.dispatch_calls==0);
}
static void allocation_prefix(void){
 cr_arguments a;const cr_request*q;++groups;fresh();memset(&a,0,sizeof(a));a.argument.value=UINT32_MAX;a.argument.known=ALL;put(A(0xbecc),A(0xd400),4);put(A(0xbec8),7,4);fail_site=0x9430;fail_flow=CR_TRANSFER;
 CHECK(cr_run(&model,CR_PULSE_ALLOC,&a)==CR_TRANSFER);CHECK(read(A(0xbecc),4)==0&&read(A(0xbec8),4)==0);CHECK(find(CR_FREE,0x9408)&&find(CR_MMIO_WRITE,0x93e8));q=find(CR_ALLOC,0x9430);CHECK(q&&q->arguments[0]==0xfffffffa&&q->argument_known[0]==ALL);
 fresh();put(A(0xbecc),A(0xd400),4);fail_site=0x9408;fail_flow=CR_TRANSFER;CHECK(cr_run(&model,CR_PULSE_ALLOC,&a)==CR_TRANSFER);CHECK(read(A(0xbecc),4)==A(0xd400)&&!find(CR_MMIO_WRITE,0x93d2));
 fresh();put(A(0xbec8),7,4);a.argument.value=2;CHECK(cr_run(&model,CR_PULSE_ALLOC,&a)==CR_RETURNED);CHECK(read(A(0xbec8),4)==7&&!find(CR_FREE,0x9408)&&!find(CR_MMIO_WRITE,0x93d2));CHECK(model.result_defined&&model.result==0&&model.result_known==ALL);
}
static void pulse_records_and_masks(void){
 cr_arguments a;const cr_request*q;unsigned i;++groups;fresh();memset(&a,0,sizeof(a));a.argument.value=2;a.argument.known=ALL;alloc_value=A(0xd400);
 CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_RETURNED);CHECK(read(A(0xbecc),4)==A(0xd400));for(i=0;i<2;i++){CHECK(read(A(0xd400)+6*i,2)==3000);CHECK(read(A(0xd402)+6*i,2)==40&&read(A(0xd404)+6*i,2)==80);}CHECK(read(A(0xd40c),2)==0&&!find(CR_MMIO_WRITE,0x93ba));
 fresh();alloc_value=A(0xd400);a.argument.value=128;a.argument.known=0xffffff80;CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_RETURNED);CHECK(read(A(0xd400),2)==3000&&read(A(0xd402),2)==128&&ram.known[0xd402]==128&&ram.known[0xd403]==255);CHECK(read(A(0xd404),4)==0);
 fresh();alloc_value=A(0xd400);a.argument.value=2;a.argument.known=ALL;put(A(0xd102),128,1);ram.known[0xd102]=128;io_value=0xa5a4;io_known=0xfffc;
 CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_RETURNED);CHECK(read(A(0xbec2),1)==0&&read(A(0xbec1),1)==0&&read(A(0xbebc),4)==0);q=find(CR_MMIO_WRITE,0x93c6);CHECK(q&&q->value==0xa5a5&&q->known==0xfffd);
}
static void effect_boundary(void){
 cr_arguments a;++groups;fresh();frame(Q,0x401,1,0);no_effects=1;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_HALT);CHECK(copies==1&&read(Q,2)==0x401&&model.boundary_va==0x12ab4);CHECK(model.record_value[0]==1&&model.record_known[0]==255);
 fresh();frame(Q,0x401,1,0);partial_copy=1;fail_site=0x12ab4;fail_flow=CR_HALT;CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_HALT);CHECK(read(Q,2)==0x401&&model.record_known[0]==255&&model.record_known[1]==0);
 fresh();a=record(A(0xd000));frame(A(0xd000),0x401,1,0);put(AUTH+4,1,1);put(AUTH+5,2,1);model.backend.invoke=NULL;CHECK(cr_run(&model,CR_DEBUG,&a)==CR_HALT);CHECK(model.boundary_va==0x834c&&model.debug_known[0]==255&&model.debug_known[1]==255);
}
static void additional_alias_and_partial_sinks(void){
 cr_arguments a;const cr_request*q;++groups;
 fresh();memset(&a,0,sizeof(a));a.argument.value=2;a.argument.known=0xfffffffe;put(A(0xbecc),A(0xd400),4);put(A(0xbec8),7,4);
 CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_HALT);CHECK(model.boundary_va==0x9430&&read(A(0xbecc),4)==0&&read(A(0xbec8),4)==0&&find(CR_FREE,0x9408));q=find(CR_ALLOC,0x9430);CHECK(q&&q->argument_known[0]!=ALL);
 fresh();alloc_value=A(0xd400);alloc_mask=0xfffffffe;a.argument.value=2;a.argument.known=ALL;
 CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_HALT);CHECK(model.boundary_va==0x9488&&read(A(0xbecc),4)==A(0xd400)&&ram.known[0xbecc]==254);CHECK(read(A(0xd400),2)==0);
 fresh();alloc_value=A(0xbecc);a.argument.value=2;a.argument.known=ALL;
 CHECK(cr_run(&model,CR_PULSE_BUILD,&a)==CR_RETURNED);CHECK(read(A(0xbecc),4)==0x00280bb8&&read(A(0xbed2),2)==3000&&read(A(0xbed8),2)==0);
 fresh();frame(A(0xd000),0x401,1,0);a=record(A(0xd000));ram.known[0xd000]=254;
 CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(model.boundary_va==0x14d56&&model.needed_mask==1&&d1==0);
 fresh();frame(A(0xd000),0x401,2,0);a=record(A(0xd000));ram.known[0xd002]=254;put(AUTH+4,1,1);put(AUTH+5,2,1);
 CHECK(cr_run(&model,CR_DEBUG,&a)==CR_HALT);CHECK(model.boundary_va==0x834c&&model.debug_known[0]==255&&model.debug_known[1]==255&&replies==0);
 fresh();frame(A(0xd000),0x401,16,0);a=record(A(0xd000));ram.known[0xd002]=16;put(AUTH+4,1,1);put(AUTH+5,2,1);
 CHECK(cr_run(&model,CR_DEBUG,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==1&&copies==0&&replies==0);
}
static void all_source_selectors(void){
 static const struct{uint16_t id;uint32_t leaf;} expected[]={{130u,0x14e0e},{258u,0x14e1a},{259u,0x14e30},{280u,0x14b8c},{297u,0x14e3c},{306u,0x14e48},{505u,0x14e58},{524u,0x14e64},{553u,0x14bb4},{568u,0x14e70},{579u,0x14bde},{585u,0x14e7c},{599u,0x14e8e},{602u,0x14e9a},{605u,0x14ea6},{614u,0x14c14},{627u,0x14eb2},{658u,0x14c38},{659u,0x14ed0},{692u,0x14edc},{694u,0x14ee2},{737u,0x14c62},{741u,0x14eee},{755u,0x14ef2},{786u,0x14efe},{799u,0x14c86},{801u,0x14f0a},{818u,0x14f16},{819u,0x14f38},{820u,0x14f44},{825u,0x14cc6},{826u,0x14f66},{850u,0x14cea},{880u,0x15090},{921u,0x150aa},{925u,0x14f78},{947u,0x14f84},{950u,0x14d1c},{962u,0x14fa0},{963u,0x14d40},{978u,0x14fde},{984u,0x14fd2},{991u,0x1501e},{994u,0x14fe4},{995u,0x14d7a},{1001u,0x14ff0},{1013u,0x14d9e},{1021u,0x15030},{1022u,0x15024},{1025u,0x15040},{1029u,0x14dd8},{1250u,0x1504c},{1251u,0x1505e},{1267u,0x15070},{1656u,0x14dfc},{1657u,0x1507a},{2047u,0x150b6}};
 static const uint16_t full_ids[]={0x132,0x292,0x2b4,0x352,0x3d2,0x3df,0x3fd,0x4e2,0x4e3,0x332,0x3b3,0x679};
 static const struct{uint16_t id;uint32_t va,target;} observers[]={{0x102,0x14e2c,0xdd7c},{0x273,0x14ebe,0xeffe},{0x3c2,0x14fb0,0xb5ba},{0x3e9,0,0},{0x3f5,0x14db0,0xa5fe}};
 unsigned i,j;int complete;cr_arguments a;cr_flow f;++groups;
 for(i=0;i<sizeof(expected)/sizeof(expected[0]);i++){fresh();frame(A(0xd000),expected[i].id,8,0);a=record(A(0xd000));f=cr_run(&model,CR_DISPATCH,&a);
  if(expected[i].id==0x401){CHECK(f==CR_RETURNED&&d1==1&&nevents==1);continue;}
  complete=0;for(j=0;j<sizeof(full_ids)/sizeof(full_ids[0]);j++)if(expected[i].id==full_ids[j])complete=1;
  if(complete){CHECK(f==CR_RETURNED);CHECK(copies==((expected[i].id==0x4e2||expected[i].id==0x4e3||expected[i].id==0x332)?0u:1u));continue;}
  for(j=0;j<sizeof(observers)/sizeof(observers[0]);j++)if(expected[i].id==observers[j].id)break;
  if(j<sizeof(observers)/sizeof(observers[0])){CHECK(f==(observers[j].va?CR_HALT:CR_RETURNED));CHECK(model.boundary_va==observers[j].va&&model.boundary_address==observers[j].target);CHECK(copies==(expected[i].id==0x332?0u:1u));}
  else{CHECK(f==CR_HALT);CHECK(model.boundary_address==expected[i].leaf&&nevents==0);}
 }
}
static void native_anchors(void){
 static const struct{uint32_t va;uint8_t b[4];} points[]={{0x15048,{0x6f,0xe0,0xff,0x99}},{0x12ab6,{0x23,0x10,0x04,0x00}},{0x834e,{0x83,0xc6,0x24,0x00}},{0x13a42,{0xef,0x50,0x8f,0xab}},{0x9430,{0x02,0x83,0x41,0x11}}};
 unsigned i,j;++groups;for(i=0;i<sizeof(points)/sizeof(points[0]);i++)for(j=0;j<4;j++)CHECK(image[points[i].va-0x8000+j]==points[i].b[j]);
}
/* R17: native cache producers. These assertions were added before the port. */
static void cache_only_routes(void){
 static const struct{uint16_t id;uint8_t gate,index;} cases[]={{0x132,0,1},{0x292,0,3},{0x2b4,0,4},{0x352,0,6},{0x352,1,7},{0x3d2,0,11},{0x3df,0,12},{0x3fd,0,14},{0x4e2,5,16},{0x4e3,5,17}};
 unsigned i,j;cr_arguments a;const cr_request*q;++groups;
 for(i=0;i<sizeof(cases)/sizeof(cases[0]);i++){fresh();frame(A(0xd000),cases[i].id,255,7);put(A(0xd003),cases[i].gate,1);ram.known[0xd002]=0;ram.known[0xd007]=0xf0;a=record(A(0xd000));
  CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&d1==0&&nevents==1);q=find(CR_COPY,0x82c0);CHECK(q&&q->slot==76&&q->target==0x4004c&&q->length==12&&q->source.address==A(0xd000)&&q->destination.address==A(0xc1b4)+12*cases[i].index);
  for(j=0;j<12;j++){CHECK(ram.ram[0xc1b4+12*cases[i].index+j]==ram.ram[0xd000+j]);CHECK(ram.known[0xc1b4+12*cases[i].index+j]==ram.known[0xd000+j]);}
 }
}
static void cache_observer_prefixes(void){
 static const struct{uint16_t id;uint8_t gate,index;uint32_t va,target;} cases[]={{0x102,0,0,0x14e2c,0xdd7c},{0x273,0,2,0x14ebe,0xeffe},{0x3c2,0,9,0x14fb0,0xb5ba},{0x3c2,1,10,0x14fb0,0xb5ba},{0x3e9,0,13,0,0},{0x3f5,0,15,0x14db0,0xa5fe}};
 unsigned i,j;cr_arguments a;++groups;
 for(i=0;i<sizeof(cases)/sizeof(cases[0]);i++){fresh();frame(A(0xd000),cases[i].id,0,2);put(A(0xd003),cases[i].gate,1);a=record(A(0xd000));
  CHECK(cr_run(&model,CR_DISPATCH,&a)==(cases[i].va?CR_HALT:CR_RETURNED));CHECK(model.boundary_va==cases[i].va&&model.boundary_address==cases[i].target);CHECK(copies==1&&nevents==1&&d1==0);for(j=0;j<12;j++)CHECK(ram.ram[0xc1b4+12*cases[i].index+j]==ram.ram[0xd000+j]);
 }
 fresh();frame(A(0xd000),0x332,0,2);put(A(0xd003),2,1);ram.known[0xd003]=2;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==0&&nevents==0);
 fresh();frame(A(0xd000),0x3c2,0,2);put(A(0xd003),2,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(copies==0&&model.boundary_va==0x14fb0&&model.boundary_address==0xb5ba);
}
static void cache_gate_masks(void){
 cr_arguments a;unsigned i;++groups;
 for(i=2;i<4;i++){fresh();frame(A(0xd000),0x352,8,0);put(A(0xd003),i,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==0&&nevents==0);}
 fresh();frame(A(0xd000),0x352,8,0);put(A(0xd003),0,1);ram.known[0xd003]=0xfd;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(model.boundary_va==0x14cf0&&model.needed_mask==2&&copies==0);
 fresh();frame(A(0xd000),0x3fd,8,0);put(A(0xd003),1,1);ram.known[0xd003]=1;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED&&copies==0);
 fresh();frame(A(0xd000),0x4e2,8,0);put(A(0xd003),0,1);ram.known[0xd003]=1;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED&&copies==0);
 fresh();frame(A(0xd000),0x4e3,8,0);put(A(0xd003),5,1);ram.known[0xd003]=7;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED&&copies==1);CHECK(ram.known[0xc1b4+17*12+3]==7);
 fresh();frame(A(0xd000),0x4e2,8,0);put(A(0xd003),5,1);ram.known[0xd003]=3;a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(model.boundary_va==0x15054&&model.needed_mask==4&&copies==0);
}
static void cache_nonreturn_prefix(void){
 cr_arguments a;cr_flow f;unsigned i;++groups;
 for(i=0;i<2;i++){fresh();frame(A(0xd000),0x102,8,0);a=record(A(0xd000));fail_site=0x82c0;partial_copy=1;fail_flow=i?CR_TRANSFER:CR_HALT;f=cr_run(&model,CR_DISPATCH,&a);CHECK(f==fail_flow);CHECK(copies==1&&nevents==1&&ram.ram[0xc1b4]==2&&ram.ram[0xc1b5]==0&&model.boundary_address!=0xdd7c);CHECK(cr_run(&model,CR_DISPATCH,&a)==f&&nevents==1);}
 fresh();frame(A(0xd000),0x132,8,0);a=record(A(0xd000));no_effects=1;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(copies==1&&model.boundary_va==0x82c0&&ram.ram[0xc1c0]==0x32);
 fresh();frame(A(0xd000),0x132,8,0);memset(&a,0,sizeof(a));a.record.kind=CR_VIEW;a.record.data=model.record_value;a.record.known=model.record_known;a.record.available=12;memcpy(model.record_value,&ram.ram[0xd000],12);memcpy(model.record_known,&ram.known[0xd000],12);CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&ram.ram[0xc1c0]==0x32&&events[0].source.kind==CR_VIEW&&events[0].argument_known[1]==0);
 fresh();memset(&a,0,sizeof(a));a.record.kind=CR_VIEW;a.record.data=model.record_value;a.record.known=model.record_known;a.record.available=2;model.record_value[0]=0x32;model.record_value[1]=1;model.record_known[0]=model.record_known[1]=255;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_HALT);CHECK(copies==1&&ram.ram[0xc1c0]==0x32&&ram.ram[0xc1c1]==1&&ram.ram[0xc1c2]==0);
}
static void cache_raw_entry_and_overlap(void){
 cr_arguments a;unsigned i;uint8_t before[24];const cr_request*q;++groups;
 fresh();frame(A(0xd000),0x132,255,7);a=record(A(0xd000));a.argument.value=0;a.argument.known=ALL;a.cache_index.value=0x40000001;a.cache_index.known=ALL;
 CHECK(cr_run(&model,CR_CACHE,&a)==CR_RETURNED);CHECK(read(A(0xc1c0),2)==0x132&&copies==1);q=find(CR_COPY,0x82c0);CHECK(q&&q->source.address==A(0xd000)&&q->destination.address==A(0xc1c0));
 a.record=rv(A(0xd100));a.argument.value=0x80000000;a.argument.known=0x80000000;a.cache_index.value=1;a.cache_index.known=0x3fffffff;CHECK(cr_run(&model,CR_CACHE,&a)==CR_RETURNED);CHECK(read(A(0xd100),2)==0x132&&copies==2);CHECK(events[1].source.address==A(0xc1c0)&&events[1].destination.address==A(0xd100));
 fresh();a=record(A(0xd000));a.argument.known=0xfffffffe;a.cache_index.known=ALL;CHECK(cr_run(&model,CR_CACHE,&a)==CR_HALT);CHECK(model.boundary_va==0x82ba&&copies==0&&model.needed_mask==1);
 fresh();a=record(A(0xd000));a.argument.known=ALL;a.cache_index.value=1;a.cache_index.known=0xfffffffe;CHECK(cr_run(&model,CR_CACHE,&a)==CR_HALT);CHECK(model.boundary_va==0x82c0&&copies==0&&model.needed_mask!=0);
 fresh();a=record(A(0xd000));a.argument.known=ALL;a.cache_index.value=19;a.cache_index.known=ALL;put(A(0xd000),0xabcd,2);CHECK(cr_run(&model,CR_CACHE,&a)==CR_RETURNED);CHECK(read(A(0xc1b4)+19*12,2)==0xabcd); /* Native has no index bound. */
 fresh();for(i=0;i<24;i++){before[i]=(uint8_t)(0x50+i);put(A(0xc1b2)+i,before[i],1);}a=record(A(0xc1b2));a.argument.known=ALL;a.cache_index.known=ALL;
 CHECK(cr_run(&model,CR_CACHE,&a)==CR_RETURNED);for(i=0;i<12;i++)CHECK(ram.ram[0xc1b4+i]==before[i%2]); /* Explicit provider forward byte order, not inferred ROM alias guarantee. */
 fresh();frame(A(0xd000),0x352,0,0);put(A(0xd003),1,1);memset(&a,0,sizeof(a));a.record.kind=CR_VIEW;a.record.data=model.record_value;a.record.known=model.record_known;a.record.available=12;memcpy(model.record_value,&ram.ram[0xd000],12);memcpy(model.record_known,&ram.known[0xd000],12);mutate_cache=1;
 CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&ram.ram[0xc1b4+7*12+3]==1&&model.record_value[3]==0xa5&&model.record_known[3]==15); /* Native gate was read before COPY. */
 fresh();a=record(0);a.argument.known=ALL;a.cache_index.known=ALL;CHECK(cr_run(&model,CR_CACHE,&a)==CR_HALT);CHECK(copies==1&&events[0].source.kind==CR_RAM&&events[0].source.address==0&&events[0].argument_known[1]==ALL);
 fresh();memset(&a,0,sizeof(a));a.record.kind=CR_VIEW;a.record.data=model.record_value;a.record.known=model.record_known;a.record.available=0;a.argument.known=ALL;a.cache_index.known=ALL;CHECK(cr_run(&model,CR_CACHE,&a)==CR_HALT);CHECK(copies==1&&events[0].source.kind==CR_VIEW&&events[0].argument_known[1]==0);
}
/* R18: actual native observers, not opaque decoding callbacks. */
static cr_arguments borrowed(uint32_t addr,unsigned cap){
 cr_arguments a;memset(&a,0,sizeof(a));a.record.kind=CR_VIEW;a.record.data=model.record_value;a.record.known=model.record_known;a.record.available=cap;memcpy(model.record_value,&ram.ram[addr-TF_RAM_BASE],12);memcpy(model.record_known,&ram.known[addr-TF_RAM_BASE],12);return a;
}
static void observer_d25a(void){
 cr_arguments a;const cr_request*q;unsigned i;++groups;
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);put(A(0xd004),2,1);put(A(0xd005),4,1);put(A(0xd006),3,1);a=record(A(0xd000));
 CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_RETURNED);CHECK(read(A(0xbf5c),2)==450&&nevents==1&&!model.result_defined);q=find(CR_GENERAL_CALL,0xd2a0);CHECK(q&&q->target==0x13a62&&q->source.address==A(0xd000)&&q->arguments[0]==A(0xd000)&&q->argument_known[0]==ALL);CHECK(read(A(0xbf5e),2)==0);
 CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_RETURNED&&nevents==1);
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),2,1);ram.known[0xd003]=2;a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_RETURNED&&nevents==0);
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);ram.known[0xd003]=1;a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_HALT&&model.boundary_va==0xd262&&model.needed_mask==2&&nevents==0);
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);put(A(0xbf5c),65535,2);ram.known[0xd005]=0;a=borrowed(A(0xd000),12);CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_RETURNED);CHECK(nevents==1&&ram.known[0xbf5c]!=255&&(ram.known[0xbf5c]|((unsigned)ram.known[0xbf5d]<<8))!=65535&&model.last_request.source.data==NULL);q=find(CR_GENERAL_CALL,0xd2a0);CHECK(q&&q->source.kind==CR_VIEW&&q->source.address==0&&q->argument_known[0]==0&&q->source.data==model.record_value);for(i=0;i<256;i++){unsigned expected=((0x300u+i)+(49u<<6))/2u;unsigned known=ram.known[0xbf5c]|((unsigned)ram.known[0xbf5d]<<8);CHECK(((read(A(0xbf5c),2)^expected)&known)==0);}
 for(i=0;i<2;i++){fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);a=record(A(0xd000));fail_site=0xd2a0;fail_flow=i?CR_TRANSFER:CR_HALT;CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==fail_flow);CHECK(read(A(0xbf5c),2)!=0&&nevents==1);CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==fail_flow&&nevents==1);}
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);a=borrowed(A(0xd000),6);CHECK(cr_run(&model,CR_OBSERVE_D25A,&a)==CR_HALT&&model.boundary_va==0xd266&&model.boundary_address==0&&nevents==0);
}
static void observer_f918_fc22(void){
 cr_arguments a;unsigned i,j;static const unsigned modes[]={0,1,2,3,4,255};++groups;
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),14,1);put(TF_GP+290,9,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_F918,&a)==CR_RETURNED);CHECK(read(TF_GP+281,1)==7&&read(TF_GP+290,1)==0&&nevents==0);
 put(TF_GP+290,9,1);CHECK(cr_run(&model,CR_OBSERVE_F918,&a)==CR_RETURNED&&read(TF_GP+290,1)==9);
 for(i=0;i<sizeof(modes)/sizeof(modes[0]);i++)for(j=0;j<4;j++){unsigned expected;fresh();memset(&a,0,sizeof(a));a.argument.value=modes[i];a.argument.known=ALL;put(TF_GP+290,j,1);put(A(0xc253),1,1);expected=modes[i]==3?(j==0||j==1?2:1):modes[i];CHECK(cr_run(&model,CR_OBSERVE_FC22,&a)==CR_RETURNED);CHECK(read(TF_GP+290,1)==expected&&nevents==0);}
 fresh();memset(&a,0,sizeof(a));a.argument.value=3;a.argument.known=ALL;CHECK(cr_run(&model,CR_OBSERVE_FC22,&a)==CR_RETURNED&&read(TF_GP+290,1)==1);
 fresh();memset(&a,0,sizeof(a));a.argument.value=0xffffff80;a.argument.known=0x80;CHECK(cr_run(&model,CR_OBSERVE_FC22,&a)==CR_RETURNED);CHECK(read(TF_GP+290,1)==128&&ram.known[0x4122]==128);
 fresh();memset(&a,0,sizeof(a));a.argument.value=3;a.argument.known=0xfffffffe;CHECK(cr_run(&model,CR_OBSERVE_FC22,&a)==CR_HALT&&model.boundary_va==0xfc24&&model.needed_mask==1);
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),2,1);ram.known[0xd004]=0xf1;put(TF_GP+290,9,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_F918,&a)==CR_HALT);CHECK(model.boundary_va==0xf924&&read(TF_GP+281,1)==0&&read(TF_GP+290,1)==9);
}
static void observer_f932(void){
 cr_arguments a;unsigned mode,bit,i;const cr_request*q;++groups;
 for(mode=0;mode<4;mode++)for(bit=0;bit<2;bit++){unsigned wanted=(0xf0u|bit);fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),wanted,1);put(TF_GP+284,mode,1);put(TF_GP+285,bit,1);put(TF_GP+286,bit,1);a=record(A(0xd000));if(mode==1)wanted=(wanted&0xf1)|2;if(mode==2)wanted=(wanted&0xf1)|6;CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==CR_RETURNED);CHECK(read(A(0xd004),1)==wanted);CHECK(nevents==((mode==1||mode==2)?1u:0u));if(nevents){q=find(CR_NATIVE_CALL,0xf976);CHECK(q&&q->target==0x12864&&q->arguments[0]==A(0xd000)&&q->argument_known[0]==ALL);}}
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),0xa4,1);put(TF_GP+285,0,1);put(TF_GP+286,1,1);a=borrowed(A(0xd000),12);CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==CR_RETURNED);CHECK(model.record_value[4]==0xa5&&nevents==1&&model.last_request.source.data==NULL);q=find(CR_NATIVE_CALL,0xf976);CHECK(q&&q->source.kind==CR_VIEW&&q->argument_known[0]==0&&q->source.data==model.record_value);
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),1,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==CR_RETURNED);CHECK(read(TF_GP+285,1)==1&&read(TF_GP+286,1)==1&&nevents==0);
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),0xff,1);ram.known[0xd004]=1;put(TF_GP+284,1,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==CR_RETURNED);CHECK(read(A(0xd004),1)==0xf3&&ram.known[0xd004]==15&&read(TF_GP+285,1)==1);
 fresh();frame(A(0xd000),0x3b3,8,0);ram.known[0x411c]=0xfe;a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==CR_HALT&&model.boundary_va==0xf938&&nevents==0);
 for(i=0;i<2;i++){fresh();frame(A(0xd000),0x3b3,8,0);put(TF_GP+284,2,1);a=record(A(0xd000));fail_site=0xf976;fail_flow=i?CR_TRANSFER:CR_HALT;CHECK(cr_run(&model,CR_OBSERVE_F932,&a)==fail_flow);CHECK(read(A(0xd004),1)==0x37&&nevents==1);}
}
static void observer_c544(void){
 cr_arguments a;unsigned n,expected;const cr_request*q;++groups;
 fresh();frame(A(0xd000),0x679,8,0);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_RETURNED&&nevents==0);
 for(n=0;n<32;n++){fresh();frame(A(0xd000),0x679,8,0);put(A(0xd007),120,1);put(TF_GP+220,1u<<9,4);put(TF_GP+224,(n<<8)|(2u<<13),4);a=record(A(0xd000));expected=n==0?120:n<=10?((120+n*10)&255):n<=20?(n-10)*10:0;if(n&&expected>100)expected=100;CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_RETURNED);CHECK(read(A(0xd007),1)==expected);CHECK(nevents==(n?1u:0u));if(n){CHECK(read(A(0xd008),1)==0x36);q=find(CR_NATIVE_CALL,0xc5ec);CHECK(q&&q->target==0x12864&&q->source.address==A(0xd000));}}
 fresh();frame(A(0xd000),0x679,8,0);put(TF_GP+220,(1u<<9)|(1u<<10)|(0xabcdU<<16),4);put(TF_GP+224,0xef,4);a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_RETURNED);CHECK(read(A(0xd004),3)==0xefabcd&&nevents==1);
 fresh();frame(A(0xd000),0x679,0,0);put(TF_GP+220,(1u<<9)|(1u<<10)|(0xabcdU<<16),4);put(TF_GP+224,0xef,4);a=borrowed(A(0xd000),12);CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_RETURNED);CHECK(model.record_value[4]==0xcd&&model.record_value[5]==0xab&&model.record_value[6]==0xef&&nevents==0);
 fresh();frame(A(0xd000),0x679,8,0);put(TF_GP+220,1u<<9,4);ram.known[0x40dc]=0;ram.known[0x40de]=ram.known[0x40df]=0;put(TF_GP+224,31u<<8,4);ram.known[0xd007]=0x80;a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_RETURNED);CHECK(read(A(0xd007),1)==0&&ram.known[0xd007]==255&&nevents==1);
 fresh();frame(A(0xd000),0x679,8,0);put(TF_GP+220,1u<<9,4);ram.known[0x40dd]=0xfd;a=record(A(0xd000));CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_HALT&&model.boundary_va==0xc54e&&nevents==0);
 fresh();frame(A(0xd000),0x679,8,0);put(TF_GP+220,(1u<<9)|(1u<<10)|(0xabcdU<<16),4);put(TF_GP+224,0xef,4);a=borrowed(A(0xd000),6);CHECK(cr_run(&model,CR_OBSERVE_C544,&a)==CR_HALT);CHECK(model.boundary_va==0xc57a&&model.record_value[4]==0xcd&&model.record_value[5]==0xab&&nevents==0);
}
static void observer_callers_live_and_flow(void){
 cr_arguments a;const cr_request*q;unsigned i;++groups;
 fresh();frame(A(0xd000),0x332,8,0);put(A(0xd003),1,1);a=borrowed(A(0xd000),12);observer_after_copy=1;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&nevents==1&&model.record_value[3]==2&&read(A(0xc1b4)+5*12+3,1)==1&&read(A(0xbf5c),2)==0);
 fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),0,1);a=record(A(0xd000));observer_after_copy=2;put(TF_GP+284,1,1);CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&read(TF_GP+281,1)==7&&read(TF_GP+290,1)==0&&read(A(0xd004),1)==2);q=find(CR_NATIVE_CALL,0xf976);CHECK(q&&nevents==2&&events[0].operation==CR_COPY);
 fresh();frame(A(0xd000),0x679,8,0);put(TF_GP+220,(1u<<9)|(1u<<10),4);a=record(A(0xd000));observer_after_copy=3;CHECK(cr_run(&model,CR_DISPATCH,&a)==CR_RETURNED);CHECK(copies==1&&nevents==1&&read(A(0xd004),1)==0x31);
 for(i=0;i<2;i++){fresh();frame(A(0xd000),0x3b3,8,0);put(A(0xd004),14,1);put(TF_GP+290,9,1);put(TF_GP+284,1,1);a=record(A(0xd000));fail_site=0x82c0;fail_flow=i?CR_TRANSFER:CR_HALT;CHECK(cr_run(&model,CR_DISPATCH,&a)==fail_flow);CHECK(read(TF_GP+281,1)==0&&read(TF_GP+290,1)==9&&read(A(0xd004),1)==14&&nevents==1);}
}
/* R19: independent arithmetic oracle; numbers deliberately compile with exact
   prior C/H for a consistent-ABI RED, before introducing new enum names. */
static unsigned reference_checksum(uint32_t a,unsigned dlc){unsigned i,sum=(read(a,1)+read(a+1,1))&255;for(i=0;i+1<dlc;i++)sum=(sum+read(a+3+i,1))&255;return sum;}
static void checksum_dynamic_lengths(void){
 cr_arguments a;unsigned dlc,i,want;++groups;
 for(dlc=0;dlc<256;dlc++){fresh();for(i=0;i<257;i++)put(A(0xd000)+i,(i*37+19)&255,1);put(A(0xd002),dlc,1);a=record(A(0xd000));want=reference_checksum(A(0xd000),dlc);CHECK(cr_run(&model,0xebbc,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==want&&model.result_known==ALL);CHECK(nevents==0);}
 fresh();frame(A(0xd000),0x1234,255,0);a=borrowed(A(0xd000),12);CHECK(cr_run(&model,0xebbc,&a)==CR_HALT);CHECK(model.boundary_va==0xebde&&model.boundary_address==0&&nevents==0);
 fresh();frame(A(0xd000),0x1234,2,0);ram.known[0xd002]=254;a=record(A(0xd000));CHECK(cr_run(&model,0xebbc,&a)==CR_HALT&&model.boundary_va==0xebd2&&model.needed_mask==1);
 fresh();a=record(A(0xd001));CHECK(cr_run(&model,0xebbc,&a)==CR_HALT&&model.boundary_va==0xebbc);
}
static void predicate_masks_and_fixed_byte(void){
 cr_arguments a;unsigned i;++groups;
 fresh();frame(A(0xd000),0x1234,8,0);put(A(0xd00a),reference_checksum(A(0xd000),8),1);a=record(A(0xd000));CHECK(cr_run(&model,0x1051c,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==1&&model.result_known==ALL&&nevents==0);
 put(A(0xd00a),read(A(0xd00a),1)^1u,1);CHECK(cr_run(&model,0x1051c,&a)==CR_RETURNED&&model.result==0&&model.result_known==ALL);
 /* DLC9 includes byte10 itself. With zero ID and all preceding bytes zero,
    every byte10 value is a valid fixed-byte comparison. */
 for(i=0;i<256;i++){fresh();put(A(0xd002),9,1);put(A(0xd00a),i,1);a=record(A(0xd000));CHECK(cr_run(&model,0x1051c,&a)==CR_RETURNED&&model.result_defined&&model.result==1&&model.result_known==ALL);}
 fresh();put(A(0xd002),2,1);ram.known[0xd003]=254;put(A(0xd00a),128,1);a=record(A(0xd000));CHECK(cr_run(&model,0x1051c,&a)==CR_RETURNED&&model.result==0&&model.result_known==ALL);
 fresh();put(A(0xd002),2,1);ram.known[0xd003]=254;a=record(A(0xd000));CHECK(cr_run(&model,0x1051c,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==1&&model.result_known==0xfffffffe&&nevents==0);
 fresh();a=borrowed(A(0xd000),10);CHECK(cr_run(&model,0x1051c,&a)==CR_HALT&&model.boundary_va==0x10528&&model.boundary_address==0);
}
static void gate_true_false_and_schedule(void){
 cr_arguments a;const cr_request*q;unsigned yes;++groups;
 for(yes=0;yes<2;yes++){fresh();frame(A(0xd000),0x3e9,8,0);put(A(0xd00a),reference_checksum(A(0xd000),8)^!yes,1);put(TF_GP+193,77,1);a=record(A(0xd000));a.argument.value=0x1051c;a.argument.known=ALL;CHECK(cr_run(&model,0x106b8,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==yes&&model.result_known==ALL);CHECK(read(TF_GP+193,1)==(yes?0u:77u));CHECK(nevents==yes);if(yes){q=find((cr_operation)11,0x106de);CHECK(q&&q->source.kind==CR_NONE&&q->destination.kind==CR_NONE&&q->target==0x9102);}}
 fresh();put(TF_GP+193,77,1);a=borrowed(A(0xd000),12);a.argument.value=0x1051c;a.argument.known=ALL;CHECK(cr_run(&model,0x106b8,&a)==CR_RETURNED&&model.result==1&&read(TF_GP+193,1)==0);CHECK(model.last_request.source.data==NULL&&model.last_request.arguments[0]==0x1063c);
 /* Real shared SRAM alias: counter[0] is source byte3. It is read before
    the clear and never causes the saved predicate result to be recomputed. */
 fresh();put(TF_GP+192,2,1);put(TF_GP+193,77,1);put(TF_GP+200,77,1);a=record(TF_GP+190);a.argument.value=0x1051c;a.argument.known=ALL;CHECK(cr_run(&model,0x106b8,&a)==CR_RETURNED);CHECK(model.result_defined&&model.result==1&&read(TF_GP+193,1)==0&&nevents==1);
}
static void gate_unknown_and_nonreturn(void){
 cr_arguments a;unsigned i;++groups;
 for(i=0;i<2;i++){fresh();put(TF_GP+193,77,1);a=record(A(0xd000));a.argument.value=i?0x12340:0x1051c;a.argument.known=i?ALL:0xfffffffd;CHECK(cr_run(&model,0x106b8,&a)==CR_HALT);CHECK(model.boundary_va==0x106c2&&model.boundary_address==a.argument.value&&nevents==0&&read(TF_GP+193,1)==77);CHECK(!model.result_defined);}
 for(i=0;i<2;i++){fresh();a=record(A(0xd000));a.argument.value=i?0x1051c:0x1051d;a.argument.known=i?0xfffffffe:ALL;CHECK(cr_run(&model,0x106b8,&a)==CR_RETURNED&&model.result_defined&&model.result==1&&nevents==1);}
 fresh();put(A(0xd002),2,1);ram.known[0xd003]=254;put(TF_GP+193,77,1);a=record(A(0xd000));a.argument.value=0x1051c;a.argument.known=ALL;CHECK(cr_run(&model,0x106b8,&a)==CR_HALT);CHECK(model.boundary_va==0x106c6&&model.needed_mask==1&&read(TF_GP+193,1)==77&&nevents==0&&!model.result_defined);
 for(i=0;i<2;i++){fresh();put(TF_GP+193,77,1);a=record(A(0xd000));a.argument.value=0x1051c;a.argument.known=ALL;fail_site=0x106de;fail_flow=i?CR_TRANSFER:CR_HALT;CHECK(cr_run(&model,0x106b8,&a)==fail_flow);CHECK(read(TF_GP+193,1)==0&&nevents==1&&!model.result_defined);CHECK(cr_run(&model,0x106b8,&a)==fail_flow&&nevents==1);}
 fresh();put(TF_GP+193,77,1);a=record(A(0xd000));a.argument.value=0x1051c;a.argument.known=ALL;model.backend.invoke=NULL;CHECK(cr_run(&model,0x106b8,&a)==CR_HALT);CHECK(read(TF_GP+193,1)==0&&model.boundary_va==0x106de&&model.boundary_address==0x9102);
}
static void dispatcher_gate_prefix(void){
 cr_arguments a;unsigned yes;const cr_request*q;++groups;
 for(yes=0;yes<2;yes++){fresh();frame(A(0xd000),0x3e9,8,0);put(A(0xd00a),reference_checksum(A(0xd000),8)^!yes,1);put(TF_GP+193,77,1);a=record(A(0xd000));CHECK(cr_run(&model,CR_DISPATCH,&a)==(yes?CR_HALT:CR_RETURNED));CHECK(copies==1&&read(A(0xc1b4)+13*12,2)==0x3e9);CHECK(read(TF_GP+193,1)==(yes?0u:77u));CHECK(nevents==1+yes);CHECK(!model.result_defined);if(yes){CHECK(model.boundary_va==0x1500e&&model.boundary_address==0xad16);q=find((cr_operation)11,0x106de);CHECK(q&&q->arguments[0]==0x1063c);}else CHECK(model.boundary_va==0);}
 fresh();frame(Q,0x3e9,8,0);put(Q+10,reference_checksum(Q,8),1);frame(Q+12,0x132,0,0);put(TF_GP+193,77,1);CHECK(cr_run(&model,CR_QUEUE,NULL)==CR_HALT);CHECK(read(Q,2)==0&&read(Q+12,2)==0x132&&model.consumed==1);CHECK(read(TF_GP+193,1)==0&&model.boundary_va==0x1500e&&model.last_request.source.data==NULL);
}
int main(int argc,char**argv){FILE*f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f||fread(image,1,sizeof(image),f)!=sizeof(image)){if(f)fclose(f);return 2;}fclose(f);debug_scalar_and_effects();dispatch_schema();queue_flow_and_snapshot();control_echo_and_counter();allocation_prefix();pulse_records_and_masks();effect_boundary();additional_alias_and_partial_sinks();all_source_selectors();native_anchors();cache_only_routes();cache_observer_prefixes();cache_gate_masks();cache_nonreturn_prefix();cache_raw_entry_and_overlap();observer_d25a();observer_f918_fc22();observer_f932();observer_c544();observer_callers_live_and_flow();checksum_dynamic_lengths();predicate_masks_and_fixed_byte();gate_true_false_and_schedule();gate_unknown_and_nonreturn();dispatcher_gate_prefix();printf("CAN_RECEIVE_RESULT groups=%u checks=%u failures=%u original_executed=0 hardware=0\n",groups,checks,failures);return failures?1:0;}
