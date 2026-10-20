#include "general_helpers.h"
#include <stdio.h>
#include <string.h>
static tf_model ram;static gh_model helper;static gh_backend io;
static uint8_t image[76800];static unsigned groups,checks,failures;
static gh_request trace[128];static unsigned trace_n;
static uint32_t stop_site,alloc_pointer,clock_raw,mmio_value,mmio_known,sched_cb,sched_delay;
static unsigned schedules,replies,clock_calls;
static gb_reply_request last_reply;static uint8_t reply_data[8];
static int mutate_reply,mutate_clock,mutate_free,unknown_clock,unknown_task,reject_unknown_write;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(i*8));ram.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(i*8);return v;}
static gb_flow invoke(void *p,gh_model *m,const gh_request *r,gb_scalar *out){(void)p;(void)m;
    if(trace_n<128)trace[trace_n++]=*r;
    if(r->callsite==stop_site)return GB_HALT;
    out->known=UINT32_MAX;out->value=0;
    if(r->kind==GH_ROM&&r->target==112)out->value=alloc_pointer;
    if(r->kind==GH_ROM&&r->target==124){++clock_calls;out->value=clock_raw;if(unknown_clock)out->known=0;if(mutate_clock)put(0x20004154,(clock_raw*10u)>>4,4);}
    if(r->kind==GH_ROM&&r->target==104&&mutate_free){put(0x200040ae,27,1);put(0x2000be0c,0x1234,4);if(unknown_task)ram.known[0x40ae]=0;}
    if(r->kind==GH_MMIO_READ){out->value=mmio_value;out->known=mmio_known;}
    if(r->kind==GH_MMIO_WRITE&&reject_unknown_write&&r->known[0]!=65535)return GB_HALT;
    /* These explicit synthetic callee returns do not implement13160/135D4. */
    return GB_RETURNED;
}
static gb_flow reply(void *p,gh_model *m,const gb_reply_request *r){(void)p;(void)m;++replies;last_reply=*r;
    if(r->length)memcpy(reply_data,r->data,r->length);
    if(mutate_reply){put(0x2000c796,42,2);put(0x2000c798,1,1);put(0x2000c799,0,1);}
    return stop_site==r->wrapper_va?GB_HALT:GB_RETURNED;
}
static gb_flow schedule(void *p,gh_model *m,uint32_t cb,uint32_t repeat,uint32_t delay,uint32_t arg,gb_scalar *out){(void)p;(void)m;(void)repeat;(void)arg;
    ++schedules;sched_cb=cb;sched_delay=delay;out->value=0;out->known=UINT32_MAX;
    return stop_site==0x9102?GB_HALT:GB_RETURNED;
}
static void fixture(void){memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(&io,0,sizeof(io));
    put(0x20004054,0x2000c298,4);put(0x200040ae,9,1);put(0x2000c792,65534,2);put(0x2000c796,65534,2);
    trace_n=0;stop_site=0;alloc_pointer=0x20005000;clock_raw=0;mmio_value=0xa5a4;mmio_known=65535;
    schedules=replies=clock_calls=0;sched_cb=sched_delay=0;mutate_reply=mutate_clock=mutate_free=unknown_clock=unknown_task=reject_unknown_write=0;memset(&last_reply,0,sizeof(last_reply));
    io.invoke=invoke;io.reply=reply;io.schedule=schedule;gh_init(&helper,&ram,&io);
}
static gb_flow run(uint32_t va,uint32_t a0){gb_scalar out;return gh_dispatch(&helper,va,a0,&out);}
static void slot(unsigned i,uint32_t cb,uint32_t arg,uint32_t repeat){uint32_t a=0x2000be08+12*i;put(a,repeat,4);put(a+4,cb,4);put(a+8,arg,4);}
static void connection(unsigned i,uint16_t h,uint8_t auth,uint8_t mode){uint32_t a=0x2000c792+4*i;put(a,h,2);put(a+2,auth,1);put(a+3,mode,1);}
static void cancel_first(void){++groups;fixture();slot(2,0x13be8,0x20005010,77);slot(4,0x13be8,0x20005020,88);
    CHECK(run(0x908e,0x13be8)==GB_RETURNED);CHECK(trace_n==2);CHECK(trace[0].kind==GH_ROM&&trace[0].target==104&&trace[0].callsite==0x90bc&&trace[0].arguments[0]==0x20005010);
    CHECK(get(0x2000be20,4)==77&&get(0x2000be24,4)==0&&get(0x2000be28,4)==0);CHECK(get(0x2000be3c,4)==0x13be8);
    CHECK(trace[1].target==92&&trace[1].arguments[0]==9&&trace[1].arguments[1]==4);
}
static void cancel_prefix_and_task_alias(void){++groups;fixture();slot(0,0x13be8,0x20005010,7);stop_site=0x90bc;
    CHECK(run(0x908e,0x13be8)==GB_HALT);CHECK(get(0x2000be0c,4)==0x13be8&&get(0x2000be10,4)==0x20005010);
    fixture();slot(0,0x13be8,0x20005010,7);mutate_free=1;stop_site=0x90ec;
    CHECK(run(0x908e,0x13be8)==GB_HALT);CHECK(get(0x2000be0c,4)==0&&get(0x2000be10,4)==0&&get(0x2000be08,4)==7);
    CHECK(trace_n==2&&trace[1].arguments[0]==27);CHECK(helper.boundary_va==0x90ec);
}
static void cancel_domain(void){unsigned i;gb_scalar result;++groups;
    for(i=0;i<15;i++){fixture();slot(i,0x12345678,0,55);CHECK(gh_dispatch(&helper,0x908e,0x12345678,&result)==GB_RETURNED);CHECK(trace_n==1&&trace[0].target==92&&trace[0].arguments[1]==(1u<<i));CHECK(get(0x2000be08+12*i,4)==55);}
    fixture();CHECK(gh_dispatch(&helper,0x908e,0x87654321,&result)==GB_RETURNED);CHECK(trace_n==0&&result.value==1&&result.known==UINT32_MAX);
    fixture();CHECK(run(0x908e,0)==GB_RETURNED);CHECK(trace_n==1&&trace[0].arguments[1]==1); /* Zero callback can match BSS. */
}
static void clock_overflow(void){gb_scalar out;++groups;fixture();clock_raw=UINT32_MAX;
    CHECK(gh_dispatch(&helper,0x81b0,0,&out)==GB_RETURNED);CHECK(out.value==0x0fffffff&&out.known==UINT32_MAX);CHECK(trace_n==1&&trace[0].target==124&&trace[0].callsite==0x81ba);
    fixture();io.invoke=NULL;gh_init(&helper,&ram,&io);CHECK(run(0x81b0,0)==GB_HALT);CHECK(helper.boundary_va==0x81ba);
}
static void mode1_threshold(void){++groups;fixture();connection(0,7,1,1);clock_raw=55;
    CHECK(run(0x13a62,0)==GB_RETURNED);CHECK(schedules==1&&sched_cb==0x135d4&&sched_delay==35);CHECK(get(0x20004154,4)==0);
    fixture();connection(1,9,1,1);clock_raw=58;stop_site=0x13ad2;
    CHECK(run(0x13a62,0)==GB_HALT);CHECK(get(0x20004154,4)==36);CHECK(trace_n==2&&trace[1].target==0x135d4&&trace[1].arguments[0]==0);
    fixture();connection(0,7,1,1);clock_raw=58;mutate_clock=1;CHECK(run(0x13a62,0)==GB_RETURNED);CHECK(schedules==1); /* Clock provider changesRAM before prior-clock load. */
}
static void mode1_gates(void){unsigned auth,mode,pause;++groups;
    for(auth=0;auth<2;auth++)for(mode=0;mode<5;mode++)for(pause=0;pause<2;pause++){
        fixture();connection(0,7,(uint8_t)auth,(uint8_t)mode);put(0x2000c790,pause,1);clock_raw=100;
        CHECK(run(0x13a62,0)==GB_RETURNED);CHECK(clock_calls==(auth&&mode==1?1u:0u));
    }
}
static void pending_marks_before_schedule(void){gb_scalar out;++groups;fixture();connection(1,9,1,4);stop_site=0x9102;
    CHECK(gh_dispatch(&helper,0x133fa,0,&out)==GB_HALT);CHECK(get(0x2000c790,1)==1);CHECK(sched_cb==0x13156&&sched_delay==300);
    fixture();connection(0,7,1,3);CHECK(gh_dispatch(&helper,0x133fa,0,&out)==GB_RETURNED);CHECK(out.value==1&&out.known==UINT32_MAX&&get(0x2000c790,1)==1);
}
static void mode0_unauthenticated_gate(void){++groups;fixture();connection(0,7,0,0);clock_raw=58;stop_site=0x13bd6;
    CHECK(run(0x13b5c,0)==GB_HALT);CHECK(get(0x20004158,4)==36);CHECK(trace_n==2&&trace[1].target==0x13160); /* Nativeproducer gate itself has noauthcheck. */
    fixture();connection(0,7,1,1);connection(1,9,0,0);CHECK(run(0x13b5c,0)==GB_RETURNED);CHECK(schedules==2&&sched_cb==0x13160&&sched_delay==100);CHECK(get(0x2000c790,1)==1);
}
static void report_all_cancel_then_callback(void){++groups;fixture();connection(0,7,0,0);clock_raw=58;put(0x200040af,0,1);slot(3,0x13be8,0,9);
    CHECK(run(0x13be8,0)==GB_RETURNED);CHECK(trace_n==3&&trace[0].target==92&&trace[1].target==124&&trace[2].target==0x13160);CHECK(sched_cb==0x13d9c&&sched_delay==300);
    fixture();io.invoke=NULL;gh_init(&helper,&ram,&io);slot(0,0x13be8,0,8);CHECK(run(0x13be8,0)==GB_HALT);CHECK(helper.boundary_va==0x90ec&&get(0x2000be0c,4)==0);CHECK(schedules==0);
}
static void activation_reply_rereads_second_slot(void){++groups;fixture();connection(0,7,1,0);put(0x2000c790,1,1);mutate_reply=1;
    CHECK(run(0x13d9c,0)==GB_RETURNED);CHECK(replies==2&&last_reply.handle==42&&last_reply.command==0xaf&&reply_data[0]==2);
    CHECK(get(0x2000bec0,1)==1&&get(0x2000bec4,2)==1&&get(0x2000bec8,4)==0);CHECK(get(0x2000becc,4)==alloc_pointer);
    CHECK(get(alloc_pointer,2)==435&&get(alloc_pointer+8,2)==130);
}
static void pattern_postsave_not_reporter(void){static const uint16_t expected[7]={1165,130,0,1465,150,0,0};unsigned i;++groups;fixture();
    CHECK(run(0x95ec,0)==GB_RETURNED);CHECK(trace_n==1&&trace[0].target==112&&trace[0].arguments[0]==18);CHECK(get(0x2000becc,4)==alloc_pointer&&replies==0);
    for(i=0;i<7;i++)CHECK(get(alloc_pointer+2*i,2)==expected[i]);
    fixture();alloc_pointer=0;CHECK(run(0x95ec,0)==GB_RETURNED);CHECK(get(0x2000becc,4)==0&&trace_n==1);
}
static void pattern_prior_free_boundary(void){++groups;fixture();put(0x2000becc,0x20005100,4);put(0x2000bec8,123,4);stop_site=0x9408;
    CHECK(run(0x95ec,0)==GB_HALT);CHECK(get(0x2000becc,4)==0x20005100&&get(0x2000bec8,4)==123);
    fixture();put(0x2000becc,0x20005100,4);put(0x2000bec8,123,4);stop_site=0x93d2;
    CHECK(run(0x95ec,0)==GB_HALT);CHECK(get(0x2000becc,4)==0&&get(0x2000bec8,4)==0);CHECK(trace_n==2&&trace[1].kind==GH_MMIO_WRITE&&trace[1].target==0x4000042c&&trace[1].arguments[0]==65535);
}
static void submit_prefix_and_mmio(void){++groups;fixture();put(0x2000bec0,1,1);put(0x2000bec2,9,1);put(0x2000bec1,9,1);put(0x2000bebc,77,4);put(0x2000bec4,88,4);stop_site=0x93ba;
    CHECK(run(0x9388,0)==GB_HALT);CHECK(get(0x2000bec2,1)==0&&get(0x2000bec1,1)==0&&get(0x2000bebc,4)==0&&get(0x2000bec4,4)==88);CHECK(helper.boundary_va==0x93ba);
    fixture();put(0x2000c29a,1,1);mmio_known=65534;CHECK(run(0x9388,0)==GB_RETURNED);CHECK(trace_n==3&&trace[2].target==0x40000400&&trace[2].arguments[0]==0xa5a5&&trace[2].known[0]==65535);
    fixture();put(0x2000c29a,1,1);mmio_known=0;CHECK(run(0x9388,0)==GB_RETURNED);CHECK(trace_n==3&&trace[2].known[0]==1); /* Only bit0 is established by OR. */
    fixture();put(0x2000c29a,1,1);mmio_known=0;reject_unknown_write=1;CHECK(run(0x9388,0)==GB_HALT);CHECK(helper.boundary_va==0x93c6&&trace_n==3); /* Explicit provider rejection cannot fall back. */
}
static void register_prefix_and_unknown_callback(void){gb_scalar out;++groups;fixture();stop_site=0x94e4;
    CHECK(gh_pattern_register(&helper,0xdeadbeef,0x12345678,65535,&out)==GB_HALT);CHECK(get(0x2000bec0,1)==1&&get(0x2000bec4,2)==65535&&get(0x2000bec8,4)==0x12345678);
    CHECK(trace_n==1&&trace[0].target==0xdeadbeef&&trace[0].arguments[0]==0&&trace[0].arguments[1]==0x12345678&&trace[0].arguments[2]==65535);
}
static uint32_t address_sum(uint32_t a,uint32_t b,uint32_t c){return a+b+c;}
static void pause_callback_and_wrap(void){++groups;fixture();put(0x2000c790,1,1);CHECK(run(0x13156,77)==GB_RETURNED);CHECK(get(0x2000c790,1)==0);
    fixture();connection(0,7,1,1);put(0x20004154,UINT32_MAX,4);CHECK(run(0x13a62,0)==GB_RETURNED);CHECK(sched_cb==0x135d4&&sched_delay==35);
    fixture();connection(0,7,1,1);clock_raw=56;stop_site=0x13ad2;CHECK(run(0x13a62,0)==GB_HALT);CHECK(get(0x20004154,4)==35);
}
static void unknown_prefixes(void){++groups;fixture();slot(0,0x13be8,0x20005010,7);mutate_free=unknown_task=1;
    CHECK(run(0x908e,0x13be8)==GB_HALT);CHECK(helper.boundary_va==0x90d0&&get(0x2000be0c,4)==0x1234&&get(0x2000be10,4)==0x20005010);
    fixture();connection(0,7,1,1);unknown_clock=1;CHECK(run(0x13a62,0)==GB_HALT);CHECK(helper.boundary_va==0x81ba&&get(0x20004154,4)==0);
    fixture();connection(0,7,1,0);stop_site=0x13d7a;CHECK(run(0x13d9c,0)==GB_HALT);CHECK(replies==1&&trace_n==0&&get(0x2000bec0,1)==0);
}
static void allocation_prefixes(void){gb_scalar out;++groups;fixture();alloc_pointer=0x20010000;
    CHECK(run(0x95ec,0)==GB_HALT);CHECK(get(0x2000becc,4)==0x20010000);CHECK(helper.boundary_va==0x9602&&helper.boundary_address==0x20010000);
    fixture();alloc_pointer=0;CHECK(gh_dispatch(&helper,0x93ee,UINT32_MAX,&out)==GB_RETURNED);CHECK(trace_n==1&&trace[0].arguments[0]==0xfffffffau&&out.value==0);
}
static void source_bound_bytes(void){++groups;
    CHECK(image[0x95fe - 0x8000]==0x93&&image[0x95ff - 0x8000]==0x07&&image[0x9600 - 0x8000]==0xd0&&image[0x9601 - 0x8000]==0x48);
    CHECK(image[0x13e12 - 0x8000]==0x17&&image[0x13e16 - 0x8000]==0x13);CHECK(address_sum(0x13e12u,0xffff5000u,1748u)==0x94e6);
    CHECK(address_sum(0x13454u,0u,0u-766u)==0x13156);CHECK(address_sum(0x13ba8u,0xfffff000u,1464u)==0x13160);
    CHECK(address_sum(0x13ae0u,0u,0u-1292u)==0x135d4);
}
int main(int argc,char **argv){FILE *f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f)return 3;if(fread(image,1,sizeof(image),f)!=sizeof(image)){fclose(f);return 4;}fclose(f);
    cancel_first();cancel_prefix_and_task_alias();cancel_domain();clock_overflow();mode1_threshold();mode1_gates();pending_marks_before_schedule();mode0_unauthenticated_gate();report_all_cancel_then_callback();activation_reply_rereads_second_slot();pattern_postsave_not_reporter();pattern_prior_free_boundary();submit_prefix_and_mmio();register_prefix_and_unknown_callback();source_bound_bytes();pause_callback_and_wrap();unknown_prefixes();allocation_prefixes();
    printf("GENERAL_HELPERS groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;
}
