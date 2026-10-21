#include "ota_contract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned groups,checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
#define RB UINT32_C(0x20004000)
#define FB UINT32_C(0x08001000)
#define PAY UINT32_C(0x20005002)
#define ALLOC UINT32_C(0x20006000)
typedef struct {
    uint8_t ram[12288],mask[12288],flash[32768],flash_mask[32768];
    oc_request trace[1024];unsigned count,cut,tx,small,release,programs,id_calls,schedules;
    oc_flow cut_flow;int id_failure,id_unknown,alloc_fail,alloc_unknown,copy_halt,word_unknown,mismatch;
    int mutate_mode,mutate_source,mutate_during_flash_read;uint32_t program_status;
} fixture;
static fixture f,g;
static void bytes(fixture *x,uint32_t address,uint8_t **v,uint8_t **k,unsigned width) {
    if(address>=RB && address-RB<=sizeof(x->ram)-width){*v=x->ram+(address-RB);*k=x->mask+(address-RB);return;}
    CHECK(address>=FB && address-FB<=sizeof(x->flash)-width);*v=x->flash+(address-FB);*k=x->flash_mask+(address-FB);
}
static oc_flow backend(void *context,const oc_request *q,oc_scalar *out) {
    fixture *x=(fixture *)context;uint8_t *v,*k,*sv,*sk;unsigned i;
    CHECK(x->count<1024);x->trace[x->count++]=*q;
    if(x->cut && x->count==x->cut)return x->cut_flow;
    out->value=0;out->known=UINT32_MAX;
    switch(q->kind){
    case OC_READ8:bytes(x,q->address,&v,&k,1);out->value=*v;out->known=*k;break;
    case OC_READ32:
        bytes(x,q->address,&v,&k,4);out->value=out->known=0;
        for(i=0;i<4;i++){out->value|=(uint32_t)v[i]<<(8*i);out->known|=(uint32_t)k[i]<<(8*i);}
        if(x->word_unknown)out->known=x->word_unknown==2?1u:0u;
        if(x->mismatch && q->pc==0x9d10)out->value^=1;
        if(x->mutate_during_flash_read && q->pc==0x9d10)x->ram[(PAY+2)-RB]^=1;
        break;
    case OC_WRITE8:bytes(x,q->address,&v,&k,1);*v=(uint8_t)q->value;*k=(uint8_t)q->known;break;
    case OC_IDENTITY:
        x->id_calls++;CHECK(q->target==0x92f2);out->value=(q->length!=14 || x->id_failure)?1u:0u;
        if(x->id_unknown)out->known=0;
        if(x->mutate_mode){x->ram[PAY-RB]=0;x->mask[PAY-RB]=255;}break;
    case OC_COPY:
        CHECK(q->target==0x4004c && q->length==1024);if(x->copy_halt)return OC_HALT;
        if(q->source>=FB && (q->source-FB>sizeof(x->flash)-1024))return OC_HALT;
        bytes(x,q->address,&v,&k,1024);bytes(x,q->source,&sv,&sk,1024);memmove(v,sv,1024);memmove(k,sk,1024);break;
    case OC_PROGRAM256:
        CHECK(q->target==0x9c0a && q->length==256);bytes(x,q->address,&v,&k,256);bytes(x,q->source,&sv,&sk,256);memcpy(v,sv,256);memcpy(k,sk,256);x->programs++;
        out->value=x->program_status;
        if(x->mutate_source && x->programs==4)x->ram[(PAY+2)-RB]^=1;
        break;
    case OC_ALLOC:x->release=0;out->value=x->alloc_fail?0:ALLOC;if(x->alloc_unknown)out->known=0;break;
    case OC_TX:CHECK(q->target==0x8a56 && q->length==1026 && q->address==ALLOC);x->tx++;break;
    case OC_RELEASE:CHECK(q->target==0x40068 && q->address==ALLOC);x->release++;break;
    case OC_SCHEDULE:CHECK(q->target==0x9124);x->schedules++;out->value=255;break;
    case OC_SMALL_REPLY:CHECK(q->target==0x13e98 || q->target==0x13f66);x->small++;break;
    default:CHECK(0);
    }
    return OC_RETURNED;
}
static void reset(fixture *x,oc_model *m){unsigned i;oc_backend b;memset(x,0,sizeof(*x));memset(x->mask,255,sizeof(x->mask));memset(x->flash_mask,255,sizeof(x->flash_mask));for(i=0;i<1024;i++)x->ram[(PAY+2)-RB+i]=(uint8_t)(i*17u);b.context=x;b.invoke=backend;oc_init(m,&b);m->gp=RB;m->gp_known=UINT32_MAX;x->ram[169]=1;x->ram[PAY-RB]=0;x->ram[PAY+1-RB]=0;}
static const oc_request *last_kind(const fixture *x,oc_kind kind){unsigned i=x->count;while(i){--i;if(x->trace[i].kind==kind)return &x->trace[i];}return NULL;}
static void write_echo(void){oc_model m;const oc_request *q;unsigned i,words=0;reset(&f,&m);CHECK(oc_dispatch(&m,7,'W',PAY,1026)==OC_RETURNED);CHECK(f.programs==4 && f.tx==1 && f.release==1 && f.small==0);CHECK(f.ram[ALLOC-RB]==0 && f.ram[ALLOC+1-RB]==0);CHECK(memcmp(f.ram+ALLOC+2-RB,f.flash,1024)==0);for(i=0;i<f.count;i++)if(f.trace[i].pc==0x9d10){CHECK(i+1<f.count && f.trace[i+1].pc==0x9d16);words++;}CHECK(words==256);q=last_kind(&f,OC_TX);CHECK(q && q->command=='W' && q->connection==7);CHECK(last_kind(&f,OC_COPY)->source==FB);groups++;}
static void guards_and_errors(void){oc_model m;const oc_request *q;reset(&f,&m);f.ram[169]=0;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.count==1);reset(&f,&m);CHECK(oc_dispatch(&m,0,'W',PAY,1025)==OC_RETURNED && !f.programs);reset(&f,&m);f.ram[PAY+1-RB]=28;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && !f.programs);reset(&f,&m);f.mismatch=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && !f.tx);q=last_kind(&f,OC_SMALL_REPLY);CHECK(q && q->command=='W' && q->length==1 && q->payload[0]==255);reset(&f,&m);f.word_unknown=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT && !f.tx && !f.small);reset(&f,&m);f.alloc_fail=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.programs==4 && !f.tx && !f.release);reset(&f,&m);f.alloc_unknown=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT && !f.tx);reset(&f,&m);f.mutate_source=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.small==1 && !f.tx);reset(&f,&m);f.program_status=255;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.tx==1);groups++;}
static void controls(void){oc_model m;const oc_request *q;reset(&f,&m);CHECK(oc_dispatch(&m,9,'E',PAY,0)==OC_RETURNED && f.ram[169]==1 && !f.id_calls);reset(&f,&m);CHECK(oc_dispatch(&m,9,'E',PAY,271)==OC_RETURNED && !f.schedules);reset(&f,&m);f.ram[PAY-RB]=1;CHECK(oc_dispatch(&m,9,'E',PAY,15)==OC_RETURNED && !f.id_calls && f.ram[169]==1);reset(&f,&m);f.id_failure=1;CHECK(oc_dispatch(&m,9,'E',PAY,15)==OC_RETURNED && !f.schedules && f.ram[169]==1);reset(&f,&m);CHECK(oc_dispatch(&m,9,'E',PAY,15)==OC_RETURNED && f.schedules==2 && f.ram[169]==0);q=last_kind(&f,OC_SMALL_REPLY);CHECK(q && q->command=='E' && q->length==0);CHECK(last_kind(&f,OC_SCHEDULE)->address==0x99e8);reset(&f,&m);CHECK(oc_dispatch(&m,9,'U',PAY,15)==OC_RETURNED && f.ram[169]==0 && f.schedules==0);q=last_kind(&f,OC_SMALL_REPLY);CHECK(q && q->payload[0]==1);reset(&f,&m);f.ram[PAY-RB]=1;CHECK(oc_dispatch(&m,9,'U',PAY,15)==OC_RETURNED && f.schedules==2);CHECK(last_kind(&f,OC_SCHEDULE)->address==0x9ee0);reset(&f,&m);CHECK(oc_dispatch(&m,9,'S',PAY,15)==OC_RETURNED && f.ram[169]==1);q=last_kind(&f,OC_SMALL_REPLY);CHECK(q && q->length==2 && q->payload[0]==0 && q->payload[1]==1);reset(&f,&m);f.id_failure=1;CHECK(oc_dispatch(&m,9,'S',PAY,15)==OC_RETURNED && f.ram[169]==0);CHECK(last_kind(&f,OC_SMALL_REPLY)->payload[0]==255);reset(&f,&m);f.ram[PAY-RB]=5;f.mutate_mode=1;CHECK(oc_dispatch(&m,9,'S',PAY,15)==OC_RETURNED && f.ram[169]==1);CHECK(last_kind(&f,OC_SMALL_REPLY)->payload[0]==5);groups++;}
static void read_and_overlap(void){oc_model m;reset(&f,&m);CHECK(oc_dispatch(&m,0,'R',PAY,16)==OC_RETURNED && !f.programs && f.tx==1 && f.id_calls==1);CHECK(last_kind(&f,OC_TX)->command=='R');reset(&f,&m);f.ram[PAY+1-RB]=28;CHECK(oc_dispatch(&m,0,'R',PAY,16)==OC_RETURNED && f.tx==1);CHECK(last_kind(&f,OC_COPY)->source==FB+28u*1024u);reset(&f,&m);CHECK(oc_dispatch(&m,0,'R',PAY,15)==OC_RETURNED && !f.id_calls);reset(&f,&m);f.copy_halt=1;CHECK(oc_dispatch(&m,0,'W',PAY-1,1026)==OC_HALT && !f.programs);CHECK(last_kind(&f,OC_COPY)->address==((PAY+1)&~3u) && last_kind(&f,OC_COPY)->source==PAY+1);reset(&f,&m);CHECK(oc_dispatch(&m,0,0x10057,PAY,1026)==OC_RETURNED && f.count==0);groups++;}
static void unknown_controls(void){oc_model m;unsigned end;reset(&f,&m);m.gp_known=0;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT && !f.count);reset(&f,&m);f.mask[169]=0;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT && !f.programs);reset(&f,&m);f.id_unknown=1;CHECK(oc_dispatch(&m,0,'E',PAY,15)==OC_HALT && f.ram[169]==1 && !f.schedules);reset(&f,&m);f.id_failure=1;CHECK(oc_dispatch(&m,0,'U',PAY,15)==OC_RETURNED && f.ram[169]==0 && !f.small);reset(&f,&m);f.mask[PAY-RB]=0;f.id_failure=1;CHECK(oc_dispatch(&m,0,'S',PAY,15)==OC_RETURNED && f.small==1 && last_kind(&f,OC_SMALL_REPLY)->payload[0]==255);reset(&g,&m);CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED);end=g.count;reset(&f,&m);f.cut=end;f.cut_flow=OC_TRANSFER;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_TRANSFER && f.tx==1 && !f.release);oc_init(&m,NULL);m.gp=RB;m.gp_known=UINT32_MAX;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT);reset(&f,&m);f.mask[PAY-RB]=0;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_HALT && !f.programs);reset(&f,&m);f.id_failure=1;CHECK(oc_dispatch(&m,0,'U',PAY,271)==OC_RETURNED);CHECK(last_kind(&f,OC_IDENTITY)->length==14);reset(&f,&m);f.id_failure=1;CHECK(oc_dispatch(&m,0,'U',UINT32_MAX,15)==OC_RETURNED);CHECK(last_kind(&f,OC_IDENTITY)->address==0);reset(&f,&m);f.ram[PAY-RB]=255;f.ram[PAY+1-RB]=255;CHECK(oc_dispatch(&m,0,'R',PAY,16)==OC_HALT && !f.tx);CHECK(last_kind(&f,OC_COPY)->source==((UINT32_C(0x20004)+65535u)<<10));reset(&f,&m);f.mutate_during_flash_read=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.small==1 && !f.tx);CHECK(last_kind(&f,OC_SMALL_REPLY)->payload[0]==255);reset(&f,&m);f.word_unknown=2;f.mismatch=1;CHECK(oc_dispatch(&m,0,'W',PAY,1026)==OC_RETURNED && f.small==1);groups++;}
static void interruptions(void){oc_model m;unsigned i,j,k;const unsigned commands[5]={'W','S','E','U','R'};for(k=0;k<5;k++){unsigned n=commands[k]=='W'?1026u:(commands[k]=='R'?16u:15u);reset(&g,&m);if(commands[k]=='U')g.ram[PAY-RB]=1;CHECK(oc_dispatch(&m,3,commands[k],PAY,n)==OC_RETURNED);for(j=0;j<2;j++)for(i=1;i<=g.count;i++){reset(&f,&m);if(commands[k]=='U')f.ram[PAY-RB]=1;f.cut=i;f.cut_flow=j?OC_TRANSFER:OC_HALT;CHECK(oc_dispatch(&m,3,commands[k],PAY,n)==f.cut_flow);CHECK(f.count==i && memcmp(f.trace,g.trace,sizeof(oc_request)*i)==0);}}groups++;}
int main(void){write_echo();guards_and_errors();controls();read_and_overlap();unknown_controls();interruptions();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"synthetic_backend_only\":true}\n",groups,checks);return 0;}
