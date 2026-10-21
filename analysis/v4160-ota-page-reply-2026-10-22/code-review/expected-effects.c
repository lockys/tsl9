/* Independent finite source-derived effect oracle. Not an instruction interpreter. */
#include "page_reply.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned checks, cases;
#define CHECK(v) do { ++checks; if (!(v)) {fprintf(stderr,"independent failure line %d: %s\n",__LINE__,#v);exit(1);} } while (0)
typedef struct cell { uint32_t address,value,known; } cell;
typedef struct fixture {
    op_host h;cell memory[80];unsigned used,count;
    uint32_t index;unsigned null_result,change_calls,unknown_alloc,unknown_s1,unknown_sp,unknown_a1;
    unsigned unknown_read,stop,memory_regs,memory_known;op_flow stop_flow;
} fixture;
static const uint32_t normal_sites[]={0x9b90u,0x9b96u,0x9b9au,0x9b9cu,0x9b9eu,0x9ba0u,0x9ba2u,0x9baeu,0x9bb6u,0x9bbau,0x9bc2u,0x9bd4u,0x9be0u,0x9be6u,0x9be8u,0x9becu,0x9beeu,0x9bf0u,0x9bf2u,0x9bf4u,0x9bf8u};
static const uint32_t null_sites[]={0x9b90u,0x9b96u,0x9b9au,0x9b9cu,0x9b9eu,0x9ba0u,0x9ba2u,0x9baeu,0x9bfau,0x9bfcu,0x9bfeu,0x9c00u,0x9c02u,0x9c04u};
static void setreg(op_host *h,unsigned r,uint32_t v){h->regs[r]=v;h->known|=(uint32_t)1u<<r;}
static void put(fixture *f,uint32_t a,uint32_t v,uint32_t k){unsigned i;for(i=0;i<f->used;i++)if(f->memory[i].address==a){f->memory[i].value=v;f->memory[i].known=k;return;}CHECK(f->used<80u);f->memory[f->used].address=a;f->memory[f->used].value=v;f->memory[f->used++].known=k;}
static cell get(fixture *f,uint32_t a){unsigned i;cell missing={a,0u,0u};for(i=0;i<f->used;i++)if(f->memory[i].address==a)return f->memory[i];return missing;}
static void synthetic_frame(fixture *f,uint32_t sp,uint32_t tag){static const uint32_t offsets[]={8u,12u,16u,20u,24u,28u};unsigned i;for(i=0;i<6u;i++)put(f,sp+offsets[i],tag+offsets[i],1u);}
static uint32_t original(unsigned reg){return reg==1u?0x123457u:0xa1100000u+reg;}
static int provide(op_host *h,op_event *e){
    fixture *f=(fixture *)h->user;unsigned at=f->count++;uint32_t idx=f->change_calls?0xfedcba98u:f->index;
    uint32_t frame=f->change_calls?0x21005000u:0x21002000u;cell c;
    CHECK(at<(f->null_result?14u:21u));CHECK(e->site==(f->null_result?null_sites[at]:normal_sites[at]));
    if(e->kind==OP_WRITE){
        if(at<=6u){static const unsigned regs[]={18u,0u,9u,19u,20u,1u,8u};static const uint32_t off[]={16u,0u,20u,12u,8u,28u,24u};CHECK(at!=1u);CHECK(e->width==4u&&e->address==0x21002000u+off[at]&&e->value==original(regs[at])&&e->value_known);}
        else {CHECK(at==8u||at==9u);CHECK(e->width==1u);CHECK(e->address==(at==8u?0x3201u:0x3200u));CHECK(e->value==((idx>>(at==8u?0u:8u))&255u)&&e->value_known);}
        put(f,e->address,e->value,e->value_known);
        if(f->memory_regs)setreg(h,9u,0xbadf00du);
        if(f->memory_known)h->known^=1u<<7;
    }else if(e->kind==OP_READ){
        uint32_t expected=0u;CHECK(e->width==4u);
        switch(e->site){
        case 0x9b96u:expected=0x40070u;break;
        case 0x9bc2u:expected=f->change_calls?0x5004cu:0x4004cu;break;
        case 0x9be8u:expected=f->change_calls?0x70068u:0x40068u;break;
        case 0x9be6u:case 0x9bfcu:expected=frame+24u;break;
        case 0x9becu:case 0x9bfau:expected=frame+28u;break;
        case 0x9beeu:case 0x9bfeu:expected=frame+20u;break;
        case 0x9bf0u:case 0x9c00u:expected=frame+16u;break;
        case 0x9bf2u:case 0x9c02u:expected=frame+12u;break;
        case 0x9bf4u:case 0x9c04u:expected=frame+8u;break;
        default:CHECK(0);break;}
        CHECK(e->address==expected);c=get(f,e->address);CHECK(c.known);e->value=c.value;e->value_known=f->unknown_read==at+1u?0u:c.known;
    }else if(e->kind==OP_ALLOCATE){
        CHECK(at==7u&&e->raw_target==0xa003u&&e->target==0xa002u);CHECK(e->args_known==7u);CHECK(e->args[0]==1026u&&e->args[1]==0x91u&&e->args[2]==f->index);CHECK(h->regs[1]==0x9bb0u&&h->regs[15]==0xa003u);e->value=f->null_result?0u:0x3200u;e->value_known=f->unknown_alloc?0u:1u;
        if(f->null_result){put(f,0x2100201cu,0x765433u,1u);setreg(h,11u,0xcafebabeu);setreg(h,12u,0x87878787u);setreg(h,13u,0x34343434u);}
        if(f->change_calls){setreg(h,9u,0xfedcba98u);setreg(h,18u,0x50000u);setreg(h,2u,0x21003000u);synthetic_frame(f,0x21003000u,0xc0000001u);}
        if(f->unknown_s1)h->known&=~(1u<<9);
    }else if(e->kind==OP_COPY_BYTES){
        uint32_t source=(uint32_t)(((uint64_t)0x20004u+idx)*1024u);
        CHECK(at==11u&&e->raw_target==(f->change_calls?0xc003u:0xc001u)&&e->target==(e->raw_target&~1u));CHECK(e->args_known==7u);CHECK(e->args[0]==0x3202u&&e->args[1]==source&&e->args[2]==1024u);CHECK(h->regs[1]==0x9bd6u);CHECK(get(f,0x3201u).value==(idx&255u)&&get(f,0x3200u).value==((idx>>8)&255u));e->value=0x22222222u;e->value_known=1u;
        if(f->change_calls){setreg(h,8u,0x4100u);setreg(h,19u,0x7788u);setreg(h,20u,0x1122u);setreg(h,18u,0x60000u);setreg(h,2u,0x21004000u);synthetic_frame(f,0x21004000u,0xd0000001u);}
    }else if(e->kind==OP_TRANSMIT){
        CHECK(at==12u&&e->raw_target==0x8a56u&&e->target==0x8a56u&&e->args_known==15u);CHECK(e->args[0]==(f->change_calls?0x7788u:0x82u)&&e->args[1]==(f->change_calls?0x1122u:0x91u)&&e->args[2]==(f->change_calls?0x4100u:0x3200u)&&e->args[3]==1026u);CHECK(h->regs[1]==0x9be4u);setreg(h,11u,0xabcd1234u);setreg(h,12u,0xdcba4321u);setreg(h,13u,0xdead0003u);e->value=0xffffffffu;e->value_known=1u;
        if(f->change_calls){setreg(h,8u,0x5200u);setreg(h,18u,0x70000u);setreg(h,2u,0x21005000u);synthetic_frame(f,0x21005000u,0xe0000001u);}
        if(f->unknown_sp)h->known&=~(1u<<2);
        if(f->unknown_a1)h->known&=~(1u<<11);
    }else if(e->kind==OP_RELEASE_TAIL){
        CHECK(at==20u&&e->raw_target==(f->change_calls?0xf007u:0xf001u)&&e->target==(e->raw_target&~1u));CHECK(e->args[0]==(f->change_calls?0x5200u:0x3200u)&&e->args[1]==0xabcd1234u&&e->args[2]==0xdcba4321u&&e->args[3]==0xdead0003u);CHECK(e->args_known==(f->unknown_a1?13u:15u));CHECK(h->regs[2]==frame+32u);CHECK(h->regs[8]==(f->change_calls?0xe0000019u:original(8u)));CHECK(h->regs[1]==(f->change_calls?0xe000001du:original(1u)));e->value=0x44556677u;e->value_known=1u;
        /* Caller link is captured before this opaque tail provider changes RA. */
        setreg(h,1u,0xeeeeeeefu);
    }else CHECK(0);
    if(f->stop==at+1u)e->flow=f->stop_flow;
    return 1;
}
static void init(fixture *f,uint32_t index){unsigned r;memset(f,0,sizeof(*f));f->index=index;f->h.known=0xffffffffu;f->h.provider=provide;f->h.user=f;for(r=0;r<32u;r++)f->h.regs[r]=original(r);f->h.regs[2]=0x21002020u;put(f,0x40070u,0xa003u,1u);put(f,0x4004cu,0xc001u,1u);put(f,0x40068u,0xf001u,1u);put(f,0x5004cu,0xc003u,1u);put(f,0x70068u,0xf007u,1u);}
static op_result run(fixture *f){++cases;return tsl9_ota_page_reply_9b8e(&f->h,0x82u,0x91u,f->index);}
static void full_cases(void){static const uint32_t indexes[]={0u,1u,255u,256u,65535u,65536u,0x12345678u,0x80000000u,0xffffffffu,0xfffdfffcu};unsigned i;fixture f;op_result r;
    for(i=0;i<sizeof(indexes)/sizeof(indexes[0]);i++){init(&f,indexes[i]);r=run(&f);CHECK(r.flow==OP_RETURNED&&r.value_known&&r.value==0x44556677u&&r.tail_delegated&&f.count==21u);CHECK(r.caller_link_known&&r.caller_link_raw==0x123457u&&r.caller_link_target==0x123456u);CHECK(f.h.regs[9]==original(9u)&&f.h.regs[18]==original(18u)&&f.h.regs[19]==original(19u)&&f.h.regs[20]==original(20u));}
    init(&f,0x76543210u);f.null_result=1u;r=run(&f);CHECK(r.flow==OP_RETURNED&&r.value_known&&r.value==0u&&!r.tail_delegated&&f.count==14u);CHECK(r.caller_link_raw==0x765433u&&r.caller_link_target==0x765432u&&f.h.regs[11]==0xcafebabeu&&f.h.regs[12]==0x87878787u&&f.h.regs[13]==0x34343434u);
    init(&f,0x12345678u);f.change_calls=1u;r=run(&f);CHECK(r.flow==OP_RETURNED&&r.value_known&&r.value==0x44556677u&&f.count==21u);CHECK(r.caller_link_raw==0xe000001du&&r.caller_link_target==0xe000001cu);CHECK(f.h.regs[9]==0xe0000015u&&f.h.regs[18]==0xe0000011u&&f.h.regs[19]==0xe000000du&&f.h.regs[20]==0xe0000009u);
    init(&f,0x10000u);f.unknown_a1=1u;r=run(&f);CHECK(r.flow==OP_RETURNED&&r.value_known&&f.count==21u&&!(f.h.known&(1u<<11)));
}
static void unavailable_cases(void){fixture f;op_result r;unsigned i;
    init(&f,0u);f.unknown_alloc=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==8u);
    init(&f,0u);f.unknown_s1=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==8u);
    init(&f,0u);f.unknown_sp=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==13u);
    for(i=1u;i<=21u;i++)if(i==2u||i==11u||(i>=14u&&i<=20u)){init(&f,0u);f.unknown_read=i;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==i);}
    init(&f,0u);f.memory_regs=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==1u&&f.h.unsupported_memory_register_mutation);
    init(&f,0u);f.memory_known=1u;r=run(&f);CHECK(r.flow==OP_UNKNOWN&&!r.value_known&&f.count==1u&&f.h.unsupported_memory_register_mutation);
}
static void stopped_cases(void){unsigned at,k;fixture f;op_result r;for(at=1u;at<=21u;at++)for(k=OP_UNKNOWN;k<=OP_TRANSFER;k++){init(&f,0x12345678u);f.stop=at;f.stop_flow=(op_flow)k;r=run(&f);CHECK(r.flow==(op_flow)k&&!r.value_known&&f.count==at);CHECK(r.tail_delegated==(uint32_t)(at==21u));}}
int main(void){full_cases();unavailable_cases();stopped_cases();printf("{\"passed\":true,\"groups\":3,\"cases\":%u,\"checks\":%u,\"ordered_effects\":21,\"target_execution\":false}\n",cases,checks);return 0;}
