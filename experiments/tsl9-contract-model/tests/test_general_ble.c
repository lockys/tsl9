#include "general_ble.h"
#include <stdio.h>
#include <string.h>
static tf_model ram;static gb_model model;
static uint8_t image[76800];static unsigned checks,failures,groups;
static uint32_t stop_target,trace[128],args[128][4];static unsigned trace_n;
static gb_reply_request last_reply;static uint8_t reply_data[1040],reply_known[1040];
static uint32_t sched_callback,sched_delay,sched_arg;static unsigned sched_n;
static uint8_t filter2[12];static unsigned partial_cache_stop;
static unsigned rewrite_on_reset;static uint8_t tx_record[12];
static unsigned stop_uid_copy;
static unsigned rewrite_reply_source;
static uint32_t scalar_9312,scalar_d392,scalar_d31a,scalar_d17c,scalar_d388,scalar_ff3c;
#define CHECK(x) do {++checks;if(!(x)){++failures;printf("FAIL line=%u %s\n",(unsigned)__LINE__,#x);}} while(0)
static void put(uint32_t a,uint32_t v,unsigned n) {unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t word(uint32_t a,unsigned n) {uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static void uid_read(void *p,uint32_t a,uint8_t *d,uint8_t *k,size_t n) {
    size_t i;(void)p;for(i=0;i<n;i++){d[i]=0;k[i]=(uint8_t)(a+i>=0x1ffff7e8u&&a+i<0x1ffff7f4u?255:0);}
}
static gb_flow invoke(void *p,gb_model *m,const gb_request *r,gb_scalar *s) {
    size_t i;uint32_t a;(void)p;(void)m;
    if(trace_n<128){trace[trace_n]=r->target;memcpy(args[trace_n],r->arguments,sizeof(args[trace_n]));++trace_n;}
    s->value=0;s->known=UINT32_MAX;if(r->target==stop_target&&r->kind==GB_NATIVE_HELPER)return GB_HALT;
    if(r->kind==GB_ROM_ALLOC)s->value=0x20008000u;
    else if(r->kind==GB_ROM_ZERO){if(r->buffer){memset(r->buffer,0,r->buffer_length);memset(r->buffer_known,255,r->buffer_length);}else for(i=0;i<r->arguments[2];i++)put(r->arguments[0]+(uint32_t)i,0,1);}
    else if(r->kind==GB_ROM_COPY){
        if(stop_uid_copy&&r->arguments[1]>=0x1ffff7e8u&&r->arguments[1]<0x1ffff7f4u)return GB_HALT;
        for(i=0;i<r->arguments[2];i++){
            uint8_t v,k;uint32_t source=r->arguments[1]+(uint32_t)i;
            if(source>=TF_RAM_BASE&&source<TF_RAM_BASE+TF_RAM_SIZE){v=ram.ram[source-TF_RAM_BASE];k=ram.known[source-TF_RAM_BASE];}
            else uid_read(NULL,source,&v,&k,1);
            if(r->buffer){r->buffer[i]=v;r->buffer_known[i]=k;}
            else {a=r->arguments[0]-TF_RAM_BASE+(uint32_t)i;ram.ram[a]=v;ram.known[a]=k;}
        }
    } else if(r->kind==GB_NATIVE_HELPER){
        if(r->target==0x9312)s->value=scalar_9312;
        else if(r->target==0x17966)s->value=1;
        else if(r->target==0x829e){a=0xc1b4+12*r->arguments[1];memcpy(r->buffer,ram.ram+a,12);memcpy(r->buffer_known,ram.known+a,12);if(partial_cache_stop){r->buffer[4]=42;r->buffer_known[4]=255;return GB_HALT;}}
        else if(r->target==0xd392)s->value=scalar_d392;
        else if(r->target==0xd31a)s->value=scalar_d31a;
        else if(r->target==0xd17c)s->value=scalar_d17c;
        else if(r->target==0xd388)s->value=scalar_d388;
        else if(r->target==0xff3c)s->value=scalar_ff3c;
        else if(r->target==0xb57e)put(model.payload_address,99,1); /* Deliberate shared source mutation. */
        else if(r->target==0x9e0a)put(0x200040af,0,1);
        else if(r->target==0x1290a&&r->arguments[0]==2)memcpy(filter2,r->buffer,12);
        else if(r->target==0x10586&&rewrite_on_reset)put(model.payload_address+1,0x23,1);
        else if(r->target==0x12864)memcpy(tx_record,r->buffer,12);
    }
    return GB_RETURNED; /* Explicit synthetic helper-return fixture, never native execution. */
}
static gb_flow reply(void *p,gb_model *m,const gb_reply_request *r){(void)p;(void)m;last_reply=*r;if(rewrite_reply_source&&r->command==0xba)put(model.payload_address,9,1);if(r->length){memcpy(reply_data,r->data,r->length);memcpy(reply_known,r->known,r->length);}return GB_RETURNED;}
static gb_flow schedule(void *p,gb_model *m,uint32_t cb,uint32_t repeat,uint32_t delay,uint32_t arg,gb_scalar *s){(void)p;(void)m;(void)repeat;++sched_n;sched_callback=cb;sched_delay=delay;sched_arg=arg;s->value=0;s->known=UINT32_MAX;return GB_RETURNED;}
static void fixture(void){gb_backend io={0};
    memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));
    put(0x20004054,0x2000c298,4);put(0x20004058,0x2000c308,4);put(0x20004060,0x2000c490,4);put(0x20004064,0x2000c590,4);put(0x20004068,0x2000c690,4);
    put(0x2000c792,7,2);put(0x2000c796,0xfffe,2);put(0x2000c794,1,1);put(0x200040af,1,1);
    memcpy(ram.ram+0xc2a4,"1234",4);trace_n=0;stop_target=0;sched_n=0;memset(&last_reply,0,sizeof(last_reply));
    scalar_9312=0x1234;scalar_d392=5;scalar_d31a=6;scalar_d17c=2;scalar_d388=7;scalar_ff3c=0x89abcdef;partial_cache_stop=0;rewrite_on_reset=0;stop_uid_copy=0;rewrite_reply_source=0;memset(filter2,0,sizeof(filter2));memset(tx_record,0,sizeof(tx_record));
    io.invoke=invoke;io.reply=reply;io.schedule=schedule;io.read=uid_read;gb_init(&model,&ram,&io);
}
static gb_flow run(uint8_t cmd,uint16_t n){return gb_dispatch(&model,7,cmd,0x2000b9d8,n);}
static void auth_mixture(void){++groups;fixture();put(0x2000c794,0,1);put(0x2000c795,4,1);memcpy(ram.ram+0xb9d8,"1a3b",4);
    CHECK(run(0xa8,4)==GB_RETURNED);CHECK(word(0x2000c794,1)==1);CHECK(word(0x2000c795,1)==0);CHECK(trace_n==1&&trace[0]==0x13be8);
    fixture();put(0x2000c794,0,1);memcpy(ram.ram+0xb9d8,"1x3b",4);CHECK(run(0xa8,4)==GB_RETURNED);CHECK(last_reply.command==0xa8&&reply_data[0]==0);CHECK(word(0x2000c794,1)==0);
}
static void registration_and_eligibility(void){++groups;fixture();put(0x2000c792,0xfffe,2);put(0x2000c794,0,1);CHECK(run(0xa0,0)==GB_RETURNED);CHECK(word(0x2000c792,2)==7);CHECK(sched_callback==0x13be8&&sched_delay==300);CHECK(last_reply.command==0xa8&&reply_data[0]==255);
    fixture();put(0x200040af,0,1);CHECK(run(0xa7,1)==GB_RETURNED);CHECK(sched_callback==0x13d9c&&sched_delay==300);CHECK(last_reply.length==0&&trace_n==0);
    fixture();put(0x200040af,0,1);CHECK(run(0xc1,0)==GB_RETURNED);CHECK(sched_callback==0x13d9c);
}
static void echo_alias(void){++groups;fixture();put(0x2000b9d8,5,1);CHECK(run(0xa2,0)==GB_RETURNED);CHECK(trace_n==1&&trace[0]==0xb57e);CHECK(last_reply.command==0xa2&&reply_data[0]==99);
}
static void password_partial_effect(void){++groups;fixture();memcpy(ram.ram+0xb9ea,"1234",4);put(0x2000b9ee,0x04030201,4);stop_target=0x12f58;
    CHECK(run(0xa9,26)==GB_HALT);CHECK(word(0x2000c2a4,4)==0x04030201);CHECK(word(0x2000c794,1)==1);CHECK(last_reply.length==0);CHECK(model.boundary_va==0x12f58);
}
static void metadata_pre_auth(void){++groups;fixture();put(0x2000c794,0,1);CHECK(run(0xae,270)==GB_RETURNED);CHECK(trace_n>=5&&trace[0]==76&&trace[1]==76&&trace[2]==0x908e&&trace[3]==0x9e0a&&trace[4]==0xe096);CHECK(last_reply.command==0xae&&reply_data[0]==1);
    fixture();put(0x2000c794,0,1);put(0x2000b9d8,1,1);CHECK(run(0xad,14)==GB_RETURNED);CHECK(trace_n==2&&trace[0]==76&&trace[1]==76&&last_reply.length==0);
}
static void config_slots_retained(void){unsigned i;++groups;fixture();for(i=16;i<96;i++)put(0x2000c298+i,0x5a,1);
    for(i=24;i<40;i++)put(0x2000b9d8+i,i,1);memcpy(ram.ram+0xb9fc,"abcd",4);for(i=59;i<75;i++)put(0x2000b9d8+i,100+i,1);
    CHECK(run(0xa3,76)==GB_RETURNED);CHECK(word(0x2000c298,1)==24);CHECK(word(0x2000c2a4,4)==0x64636261);CHECK(word(0x2000c2f8,1)==159);
    for(i=16;i<96;i++)CHECK(word(0x2000c298+i,1)==0x5a);
}
static void mapping_alias_and_guard(void){unsigned i;++groups;fixture();for(i=0;i<256;i++)put(0x2000b9d8+i,i,1);put(0x2000bad7,0x5a,1);
    CHECK(run(0xab,256)==GB_RETURNED);CHECK(word(0x2000c490,4)==0x03020100);CHECK(word(0x2000c58f,1)==0x5a);
    fixture();put(0x2000b9d8,2,1);CHECK(run(0xba,1)==GB_RETURNED);CHECK(trace_n>=2&&trace[0]==0x124d0&&trace[1]==0x134e4);
}
static void report_sources(void){unsigned i;++groups;fixture();put(0x2000b9d8,1,1);for(i=0;i<8;i++)put(0x2000c1b4+4*12+3+i,10+i,1);
    CHECK(run(0xd2,1)==GB_RETURNED);CHECK(word(0x2000c795,1)==3);CHECK(last_reply.command==0xd2&&last_reply.length==8);CHECK(reply_data[0]==10&&reply_data[5]==15&&reply_data[6]==0&&reply_data[7]==0);
    fixture();put(0x2000b9d8,1,1);stop_target=0xd392;CHECK(run(0xd0,1)==GB_HALT);CHECK(word(0x2000c795,1)==3);CHECK(model.boundary_va==0xd392&&last_reply.length==0);
    fixture();put(0x2000b9d8,1,1);CHECK(run(0xd1,1)==GB_RETURNED);CHECK(word(0x2000c795,1)==4);CHECK(last_reply.length==0);
}
static void status_word(void){++groups;fixture();put(0x2000bfb1,6,1);put(0x20004160,1,1);put(0x20004161,2,1);put(0x20004162,3,1);put(0x20004163,4,1);put(0x20004164,5,1);
    CHECK(run(0xc1,0)==GB_RETURNED);CHECK(last_reply.length==4&&last_reply.command==0xc1);CHECK((uint32_t)reply_data[0]==28);CHECK(reply_data[1]==5&&reply_data[2]==6&&reply_data[3]==0xe0);
}
static void debug_stale_word(void){++groups;fixture();put(0x2000b9d8,0xffff,2);CHECK(run(0xc0,2)==GB_RETURNED);CHECK(word(0x2000c795,1)==2);CHECK(last_reply.command==0xbc&&reply_data[0]==1);CHECK(trace_n>=4&&trace[0]==0x10586&&trace[1]==0x128ba);
}
static void explicit_all_commands(void){static const uint8_t commands[]={69,83,85,87,160,161,162,163,164,165,166,167,168,169,171,173,174,175,176,185,186,187,192,193,208,209,210,240};
    static const uint32_t leaves[]={0x13ea2,0x13ea2,0x13ea2,0x13ea2,0x14032,0x14704,0x14730,0x140a2,0x14772,0x14788,0x141a8,0x1471e,0x13ef6,0x147c8,0x141c6,0x13f4e,0x13f7e,0x149ec,0x141fe,0x148f6,0x1487e,0x14228,0x144e2,0x146ee,0x14254,0x144ce,0x14254,0x142e2};unsigned i;++groups;
    for(i=0;i<sizeof(commands);i++){fixture();(void)run(commands[i],0);CHECK(model.recognized==1&&model.leaf==leaves[i]);}
    fixture();CHECK(run(0xaa,0)==GB_RETURNED);CHECK(model.recognized==0);fixture();CHECK(run('R',0)==GB_RETURNED);CHECK(model.recognized==0);
}
static void missing_backend_is_boundary(void){++groups;fixture();model.backend.invoke=NULL;put(0x2000b9d8,9,1);CHECK(run(0xbb,1)==GB_HALT);CHECK(model.boundary_va==0x15378);CHECK(last_reply.length==0);
    fixture();model.backend.invoke=NULL;put(0x2000b9d8,1,1);CHECK(run(0xb0,1)==GB_HALT);CHECK(word(0x2000c795,1)==1);CHECK(model.boundary_va==0x13a62);
}
static void stack_alias_and_boundary_state(void){unsigned i;++groups;fixture();put(0x2000b9d8,65535,2);for(i=0;i<7;i++)put(0x2000b9da+2*i,0x1001+i,2);
    CHECK(run(0xc0,16)==GB_RETURNED);CHECK(last_reply.command==0xbc&&reply_data[0]==1);CHECK(filter2[0]==7&&filter2[1]==16); /* Native sp20 alias, not per-channel reject. */
    fixture();partial_cache_stop=1;put(0x2000b9d8,1,1);CHECK(run(0xd2,1)==GB_HALT);CHECK(word(0x2000c795,1)==3);CHECK(model.last_request.buffer_length==12);CHECK(model.boundary_buffer[4]==42&&model.boundary_known[4]==255);
    partial_cache_stop=0;CHECK(gb_registration(&model,7,0)==GB_RETURNED);CHECK(word(0x2000c792,2)==65534);
}
static void debug_read_after_reset(void){++groups;fixture();put(0x2000b9d8,1,1);put(0x2000b9da,42,1);ram.known[0xb9d9]=0;rewrite_on_reset=1;
    CHECK(run(0xc0,3)==GB_RETURNED);CHECK(word(0x2000c795,1)==2);CHECK(trace_n>=3&&trace[0]==0x10586&&trace[1]==76&&trace[2]==0x12864);CHECK(tx_record[0]==0x23&&tx_record[1]==1&&tx_record[2]==1&&tx_record[3]==42);CHECK(last_reply.command==0xbc&&reply_data[0]==1);
}
static void all_gate_domains(void){
    /* Independent values from native13FDE..14090 bounded route projection. */
    static const uint8_t gated[]={161,163,164,165,166,167,170,171,176,185,186,187,192,193,208,209,210,240};
    unsigned c,i,expected,pre;++groups;
    for(c=0;c<256;c++){
        fixture();put(0x200040af,0,1);expected=0;for(i=0;i<sizeof(gated);i++)if(gated[i]==c)expected=1;
        CHECK(run((uint8_t)c,0)==GB_RETURNED);CHECK(sched_n==expected);if(expected)CHECK(sched_callback==0x13d9c&&sched_delay==300);
        fixture();put(0x2000c794,0,1);pre=c==69||c==83||c==85||c==87||c==168||c==173||c==174;
        CHECK(run((uint8_t)c,0)==GB_RETURNED);CHECK(sched_n==(pre?0u:1u));if(!pre)CHECK(sched_callback==0x13be8&&last_reply.command==0xa8&&reply_data[0]==255);
    }
}
static void uid_copy_has_flow_boundary(void){++groups;fixture();stop_uid_copy=1;CHECK(run(0xae,14)==GB_HALT);CHECK(model.boundary_va==0x92b4);CHECK(last_reply.length==0&&word(0x200040af,1)==1);}
static void packed_d0_golden(void){
    /* Native14308..144CC field derivation, independent explicit 29-byte vector. */
    static const uint8_t expected[]={0x34,0x12,0x78,0x56,1,2,3,4,5,6,7,8,0x65,0x87,0x21,0x43,0x56,0x34,0x6b,0xdb,0xbc,0xff,0x16,0xa0,0x81,0xc3,0x7b,0xf3,0x6a};
    unsigned i;uint32_t base=0x2000c1b4;++groups;fixture();put(0x2000b9d8,1,1);
    put(base+12+3,0x56781234,4);for(i=0;i<8;i++)put(base+11*12+3+i,i+1,1);
    put(base+5*12+3,0xac,1);put(base+5*12+4,0x2d,1);put(base+5*12+5,0xcd,1);put(base+5*12+6,0xab,1);
    put(base+6*12+5,0x87654321,4);put(base+7*12+5,0x3456,2);put(base+3*12+8,0xa6ff,2);
    CHECK(run(0xd0,1)==GB_RETURNED);CHECK(last_reply.command==0xd0&&last_reply.length==29);
    for(i=0;i<sizeof(expected);i++){CHECK(reply_data[i]==expected[i]);CHECK(reply_known[i]==255);}
}
static void ba_reply_retains_native_source(void){++groups;fixture();put(0x2000b9d8,1,1);rewrite_reply_source=1;CHECK(run(0xba,1)==GB_RETURNED);CHECK(last_reply.source_address==0x2000b9d8&&last_reply.wrapper_va==0x13cac);CHECK(reply_data[0]==9);}
int main(int argc,char **argv){FILE *f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f)return 3;if(fread(image,1,sizeof(image),f)!=sizeof(image)){fclose(f);return 4;}fclose(f);
    auth_mixture();registration_and_eligibility();echo_alias();password_partial_effect();metadata_pre_auth();config_slots_retained();mapping_alias_and_guard();report_sources();status_word();debug_stale_word();explicit_all_commands();missing_backend_is_boundary();stack_alias_and_boundary_state();debug_read_after_reset();all_gate_domains();uid_copy_has_flow_boundary();packed_d0_golden();ba_reply_retains_native_source();
    printf("GENERAL groups=%u checks=%u failures=%u synthetic_helpers=true target_executed=false\n",groups,checks,failures);return failures?1:0;
}
