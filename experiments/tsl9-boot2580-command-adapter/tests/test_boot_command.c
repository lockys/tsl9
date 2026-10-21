#include "boot_command.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned checks, groups;
#define T(x) do { ++checks; if(!(x)){fprintf(stderr,"line%d: %s\n",__LINE__,#x);exit(1);} } while(0)
#define RAM UINT32_C(0x20000000)
#define FLASH UINT32_C(0x08008000)
#define PAYLOAD (RAM+0x202u)
#define STACK (RAM+0x1000u)
#define ACTIVE (RAM+0x18bu)
typedef struct {
    uint8_t ram[65536], known[65536], flash[98304], flash_known[98304];
    bc_request events[1200]; unsigned count, replies, programs;
    unsigned stop_at, transfer_at, uid_match, uid_mutate_mode, uid_unknown;
    unsigned metadata_unknown, metadata_stop, metadata_transfer, mutate_live_source;
    unsigned replace_uid_frame, replace_meta_frame;
    uint32_t new_pointer,new_length; bc_request reply;
} fixture;
static fixture f;
static bc_model m;
static uint8_t *byte_at(uint32_t a,unsigned mask) {
    if(a>=RAM&&a-RAM<sizeof f.ram) return (mask?f.known:f.ram)+(a-RAM);
    if(a>=FLASH&&a-FLASH<sizeof f.flash) return (mask?f.flash_known:f.flash)+(a-FLASH);
    return NULL;
}
static void set(uint32_t a,uint32_t v,uint32_t k,unsigned width) {
    unsigned i; for(i=0;i<width;i++) { uint8_t *p=byte_at(a+i,0),*q=byte_at(a+i,1);
        T(p&&q); *p=(uint8_t)(v>>(8*i));*q=(uint8_t)(k>>(8*i)); }
}
static bc_value get(uint32_t a,unsigned width) {
    bc_value v={0,0}; unsigned i;
    for(i=0;i<width;i++) { uint8_t *p=byte_at(a+i,0),*q=byte_at(a+i,1);
        if(p&&q){v.value|=(uint32_t)*p<<(8*i);v.known|=(uint32_t)*q<<(8*i);} }
    return v;
}
static bc_flow provider(void *context,bc_model *model,const bc_request *q,bc_value *out) {
    unsigned i; (void)context; T(f.count<1200); f.events[f.count++]=*q;
    if(f.count==f.stop_at) return BC_HALT;
    if(f.count==f.transfer_at) return BC_TRANSFER;
    if(q->kind==BC_READ8||q->kind==BC_READ32) {
        if(q->args[0].known!=UINT32_MAX)return BC_HALT;
        if(q->args[0].value==0x4004cu){out->value=0x9001;out->known=UINT32_MAX;return BC_RETURNED;}
        *out=get(q->args[0].value,q->kind==BC_READ8?1u:4u);
        if(f.mutate_live_source&&q->pc==0x2282) {set(PAYLOAD+2,0x11,255,1);f.mutate_live_source=0;}
    } else if(q->kind==BC_WRITE8||q->kind==BC_WRITE32) {
        if(q->args[0].known!=UINT32_MAX)return BC_HALT;
        set(q->args[0].value,q->args[1].value,q->args[1].known,q->kind==BC_WRITE8?1u:4u);
    } else if(q->kind==BC_IDENTITY) {
        out->value=q->args[1].value==14&&f.uid_match?0u:1u;
        out->known=f.uid_unknown?0u:UINT32_MAX;
        if(f.uid_mutate_mode)set(PAYLOAD,0,255,1);
        if(f.replace_uid_frame){set(STACK+8,f.new_pointer,UINT32_MAX,4);set(STACK+12,f.new_length,UINT32_MAX,4);}
    } else if(q->kind==BC_INDIRECT_COPY) {
        T(q->nominal_slot==0x4004c&&q->raw_target.value==0x9001&&q->target.value==0x9000);
        T(q->args[0].known==UINT32_MAX&&q->args[1].known==UINT32_MAX&&q->args[2].value==1024);
        /* Explicit synthetic overlap-copy assumption; not an original ROM ABI. */
        memmove(byte_at(q->args[0].value,0),byte_at(q->args[1].value,0),1024);
        memmove(byte_at(q->args[0].value,1),byte_at(q->args[1].value,1),1024);
    } else if(q->kind==BC_PROGRAM256) {
        if(q->args[0].known!=UINT32_MAX||q->args[1].known!=UINT32_MAX)return BC_HALT;
        ++f.programs;
        for(i=0;i<256;i++){bc_value v=get(q->args[1].value+i,1);set(q->args[0].value+i,v.value,v.known,1);}
    } else if(q->kind==BC_METADATA) {
        T(q->target.value==0x2184&&q->args[0].value==2);
        if(f.metadata_stop)return BC_HALT;
        if(f.metadata_transfer)return BC_TRANSFER;
        out->value=1;out->known=f.metadata_unknown?0u:UINT32_MAX;
        if(f.replace_meta_frame){set(STACK+8,f.new_pointer,UINT32_MAX,4);set(STACK+12,f.new_length,UINT32_MAX,4);}
    } else if(q->kind==BC_REPLY) {++f.replies;f.reply=*q;}
    (void)model; return BC_RETURNED;
}
static void setup(void) {
    bc_backend b; memset(&f,0,sizeof f);memset(f.known,255,sizeof f.known);
    memset(f.flash_known,255,sizeof f.flash_known);f.uid_match=1;
    b.context=&f;b.invoke=provider;bc_init(&m,&b);
    m.gp.value=RAM+0x100;m.gp.known=UINT32_MAX;
    m.body_sp.value=STACK;m.body_sp.known=UINT32_MAX;
    set(ACTIVE,1,255,1);set(PAYLOAD,1,255,1);
}
static unsigned find(bc_kind kind,unsigned after) {
    unsigned i; for(i=after;i<f.count;i++)if(f.events[i].kind==kind)return i;
    return f.count;
}
static void start_success(void) {
    unsigned u,c,d; ++groups;setup();set(ACTIVE,0,255,1);f.metadata_unknown=1;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_RETURNED);
    T(f.replies==1&&get(ACTIVE,1).value==1);
    T(f.events[0].pc==0x22d6&&f.events[0].args[0].value==STACK+12);
    T(f.events[1].pc==0x22d8&&f.events[1].args[0].value==STACK+8);
    u=find(BC_IDENTITY,0);c=find(BC_CANCEL_STARTUP,u);d=find(BC_METADATA,c);
    T(u==2&&f.events[u].args[0].value==PAYLOAD+1&&f.events[u].args[1].value==14);
    T(f.events[u+1].pc==0x22dc&&f.events[u+2].pc==0x22de);
    T(f.events[u+3].pc==0x22e2&&c<d);
    T(f.events[d+1].pc==0x22f6&&f.events[d+2].pc==0x22f8);
    T(f.reply.target.value==0x2aa0&&f.reply.args[0].value==7);
    T(f.reply.args[1].value=='S'&&f.reply.args[2].value==PAYLOAD&&f.reply.args[3].value==15);
}
static void live_start(void) {
    ++groups;setup();f.uid_mutate_mode=1;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_RETURNED);
    T(get(ACTIVE,1).value==0&&get(PAYLOAD,1).value==255&&find(BC_METADATA,0)==f.count);
    setup();f.replace_uid_frame=1;f.new_pointer=RAM+0x800;f.new_length=271;set(f.new_pointer,1,255,1);
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_RETURNED);
    T(f.reply.args[2].value==f.new_pointer&&f.reply.args[3].value==271);
    setup();f.replace_meta_frame=1;f.new_pointer=RAM+0x900;f.new_length=99;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_RETURNED);
    T(f.reply.args[2].value==f.new_pointer&&f.reply.args[3].value==99);
}
static void failed_identity(void) {
    ++groups;setup();f.uid_match=0;
    T(bc_dispatch(&m,7,'S',PAYLOAD,271)==BC_RETURNED);
    T(f.events[2].args[1].value==14&&f.events[3].pc==0x22dc&&f.events[4].pc==0x22de);
    T(get(ACTIVE,1).value==0&&get(PAYLOAD,1).value==255&&f.replies==1);
    setup();f.uid_unknown=1;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_HALT);
    T(m.boundary==BC_CONDITION_UNKNOWN&&m.boundary_pc==0x22e0);
    T(f.count==5&&f.replies==0&&get(ACTIVE,1).value==1);
}
static void metadata_nonreturn(void) {
    ++groups;setup();set(ACTIVE,0,255,1);f.metadata_stop=1;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_HALT);
    T(get(ACTIVE,1).value==1&&f.replies==0&&m.last_request.kind==BC_METADATA);
    T(bc_dispatch(&m,7,'E',0,0)==BC_HALT&&f.replies==0);
    setup();set(ACTIVE,0,255,1);f.metadata_transfer=1;
    T(bc_dispatch(&m,7,'S',PAYLOAD,15)==BC_TRANSFER);
    T(f.replies==0&&get(ACTIVE,1).value==1);
    bc_new_activation(&m);T(bc_dispatch(&m,7,'E',0,0)==BC_RETURNED&&f.replies==1);
}
static void update_prepare(void) {
    ++groups;setup();set(PAYLOAD,0x93,255,1);
    T(bc_dispatch(&m,9,'U',PAYLOAD,271)==BC_RETURNED);
    T(f.events[0].pc==0x22a8&&get(ACTIVE,1).value==0);
    T(f.events[1].kind==BC_IDENTITY&&f.events[1].args[1].value==14);
    T(f.reply.target.value==0x2aba&&f.reply.argc==3&&f.reply.args[2].value==0);
    setup();f.uid_match=0;T(bc_dispatch(&m,9,'U',PAYLOAD,15)==BC_RETURNED);
    T(get(ACTIVE,1).value==0&&f.replies==0);
}
static void end_unguarded(void) {
    ++groups;setup();T(bc_dispatch(&m,9,'E',UINT32_MAX,UINT32_MAX)==BC_RETURNED);
    T(f.count==5&&f.events[0].pc==0x231e&&f.events[1].pc==0x2336);
    T(f.events[2].kind==BC_SCHEDULE&&f.events[2].target.value==0x1afa);
    T(f.events[2].args[0].value==0x192c&&f.events[2].args[2].value==200);
    T(f.events[3].args[0].value==0x20e2&&f.events[3].args[2].value==400);
    T(get(ACTIVE,1).value==0&&f.reply.args[2].value==0&&f.reply.args[3].value==0);
    setup();set(ACTIVE,0,255,1);T(bc_dispatch(&m,9,'E',0,0)==BC_RETURNED&&f.count==1);
    setup();T(bc_dispatch(&m,9,'R',PAYLOAD,16)==BC_RETURNED&&f.count==0);
}
static void write_page(void) {
    unsigned i,p; ++groups;setup();set(PAYLOAD,0,255,1);set(PAYLOAD+1,74,255,1);
    for(i=0;i<1024;i++)set(PAYLOAD+2+i,i&255,255,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_RETURNED);
    T(f.events[1].pc==0x2210&&f.events[1].args[0].value==PAYLOAD+1);
    T(f.events[2].pc==0x2214&&f.events[2].args[0].value==PAYLOAD);
    T(m.page.value==74&&m.destination.value==FLASH+74*1024);
    T(f.programs==4&&f.replies==1&&m.program_attempts==4);
    p=find(BC_PROGRAM256,0);for(i=0;i<4;i++)T(f.events[p+i].args[0].value==FLASH+74*1024+i*256);
    T(f.events[p+4].pc==0x2282&&f.events[p+5].pc==0x2288);
    T(f.reply.target.value==0x2aa0&&f.reply.args[1].value=='W'&&f.reply.args[3].value==0);
}
static void page_guards(void) {
    ++groups;setup();set(PAYLOAD,0,255,1);set(PAYLOAD+1,96,255,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_RETURNED&&f.count==3&&f.programs==0);
    setup();T(bc_dispatch(&m,9,'W',PAYLOAD,1025)==BC_RETURNED&&f.count==1);
    setup();set(ACTIVE,0,255,1);T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_RETURNED&&f.count==1);
    setup();set(ACTIVE,0,0,1);T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_HALT&&m.boundary_pc==0x2206);
}
static void overlap_and_live(void) {
    unsigned c; ++groups;setup();set(PAYLOAD-2,0,65535,2);set(PAYLOAD,0xab,255,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD-2,1026)==BC_RETURNED);
    c=find(BC_INDIRECT_COPY,0);T(c<f.count&&f.events[c-1].pc==0x2256);
    T(f.events[c].pc==0x225e&&f.events[c].args[0].value==PAYLOAD-2&&f.events[c].args[1].value==PAYLOAD);
    T(get(PAYLOAD-2,1).value==0xab&&f.replies==1);
    setup();set(PAYLOAD,0,65535,2);f.mutate_live_source=1;
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_RETURNED);
    T(f.programs==4&&f.replies==0&&f.events[f.count-1].pc==0x2288);
}
static void partial_pages(void) {
    ++groups;setup();set(PAYLOAD,1,1,1);set(PAYLOAD+1,0,0,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_RETURNED&&f.count==3);
    setup();set(PAYLOAD,0,255,1);set(PAYLOAD+1,0x40,0xc0,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_HALT&&m.boundary==BC_CONDITION_UNKNOWN&&m.boundary_pc==0x2240);
    setup();set(PAYLOAD,0,255,1);set(PAYLOAD+1,0,0xf0,1);
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_HALT);
    T(m.last_request.kind==BC_PROGRAM256&&m.last_request.args[0].known==0xffffc3ffu);
}
static void prefix_boundaries(void) {
    unsigned n; ++groups;setup();m.observation_budget=0;
    T(bc_dispatch(&m,9,'W',PAYLOAD,1026)==BC_HALT&&f.count==0&&m.boundary==BC_OBSERVATION_BUDGET);
    setup();f.stop_at=2;T(bc_dispatch(&m,9,'U',PAYLOAD,15)==BC_HALT);
    T(get(ACTIVE,1).value==0&&f.replies==0);
    n=f.count;T(bc_dispatch(&m,9,'S',PAYLOAD,15)==BC_HALT&&f.count==n);
    setup();f.transfer_at=3;T(bc_dispatch(&m,9,'E',0,0)==BC_TRANSFER);
    T(get(ACTIVE,1).value==0&&f.replies==0&&f.count==3);
    setup();m.backend.invoke=NULL;
    T(bc_dispatch(&m,9,'U',PAYLOAD,15)==BC_HALT&&m.boundary==BC_MISSING_PROVIDER);
}
int main(void) {
    start_success();live_start();failed_identity();metadata_nonreturn();update_prepare();
    end_unguarded();write_page();page_guards();overlap_and_live();partial_pages();prefix_boundaries();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"target_executed\":false,\"hardware\":false}\n",groups,checks);
    return 0;
}
