#include "irq_frames.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define CHECK(x) do {checks++;if(!(x)){fprintf(stderr,"line%d:%s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks,groups;
static const unsigned regs[29]={1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31};
typedef struct {uint32_t address;iq_scalar word;} cell;
typedef struct {
    cell memory[256];unsigned cells,events,calls; iq_request log[128];
    unsigned action;uint32_t fail_pc;int fail_after_effect;
} fixture;
static iq_scalar scalar(uint32_t value){iq_scalar s={value,UINT32_MAX};return s;}
static iq_scalar *at(fixture *f,uint32_t address){
    unsigned i;for(i=0;i<f->cells;i++)if(f->memory[i].address==address)return &f->memory[i].word;
    CHECK(f->cells<256);f->memory[f->cells].address=address;
    f->memory[f->cells].word=scalar(UINT32_C(0xfeedface));return &f->memory[f->cells++].word;
}
static iq_flow effect(void *ctx,const iq_request *q,iq_scalar *out){
    fixture *f=(fixture *)ctx;CHECK(f->events<128);f->log[f->events++]=*q;
    if(q->pc==f->fail_pc&&!f->fail_after_effect)return IQ_HALT;
    if(q->kind==IQ_READ32)*out=*at(f,q->address);
    if(q->kind==IQ_WRITE32)*at(f,q->address)=q->value;
    if(q->pc==f->fail_pc)return IQ_HALT;
    return IQ_RETURNED;
}
static iq_flow callback(void *ctx,iq_model *m,const iq_request *q){
    fixture *f=(fixture *)ctx;unsigned i;f->calls++;
    CHECK(q->kind==IQ_CALLBACK&&q->pc==0x84da&&q->target.known==UINT32_MAX);
    CHECK(q->target.value==(m->gpr[10].value&~UINT32_C(1)));
    CHECK(m->gpr[1].value==0x84de&&m->gpr[11].value==0x2180);
    if(f->action==1){*at(f,m->gpr[2].value+32)=scalar(0xabc123);m->gpr[3]=scalar(0x77770000);m->gpr[30]=scalar(12);}
    if(f->action==2){m->gpr[2]=scalar(m->gpr[2].value+256);for(i=0;i<29;i++)*at(f,m->gpr[2].value+4+4*i)=scalar(0xd000+i);}
    if(f->action==3)return IQ_TRANSFER;
    if(f->action==4){*at(f,m->gpr[2].value+4)=scalar(0xdead);return IQ_HALT;}
    if(f->action==5){m->mepc=scalar(0x98765432);*at(f,m->gpr[2].value)=scalar(0xdeadbeef);}
    return IQ_RETURNED;
}
static void setup(iq_model *m,fixture *f){
    iq_backend b;unsigned i;memset(f,0,sizeof(*f));b.context=f;b.effect=effect;b.callback=callback;iq_init(m,&b);
    for(i=0;i<32;i++)m->gpr[i]=scalar(0x10000+i);
    m->gpr[0]=scalar(0);m->gpr[2]=scalar(0x1080);m->gpr[3]=scalar(0x2000);m->mepc=scalar(0x9008);
    m->csr804.value=0x80;m->csr804.known=0x80;*at(f,0x2180)=scalar(0x1235);
}
static void restore_case(void){
    iq_model m;fixture f;unsigned i;setup(&m,&f);m.gpr[2]=scalar(0x1000);
    *at(&f,0x1000)=scalar(0xaabbccdd);for(i=0;i<29;i++)*at(&f,0x1004+4*i)=scalar(0x4000+i);
    CHECK(iq_restore_8448(&m)==IQ_TRANSFER&&m.boundary==IQ_MRET_BOUNDARY);
    CHECK(m.operations==33&&m.restored_words==29&&m.saved_words==0&&f.calls==0);
    CHECK(m.mepc.value==0xaabbccdd&&m.gpr[2].value==0x1080&&m.gpr[3].value==0x2000);
    CHECK(m.csr804.value==0xa0&&m.csr804.known==0xa0);
    for(i=0;i<29;i++)CHECK(m.gpr[regs[i]].value==0x4000+i);
    CHECK(f.log[0].kind==IQ_CSR_SET&&f.log[0].csr==0x804&&f.log[0].value.value==32);
    CHECK(f.log[1].kind==IQ_READ32&&f.log[1].address==0x1000&&f.log[2].kind==IQ_CSR_WRITE&&f.log[2].csr==0x341);
    CHECK(f.log[32].kind==IQ_MRET&&f.log[32].pc==0x8492);groups++;
}
static void frame_case(unsigned action){
    iq_model m;fixture f;unsigned i;setup(&m,&f);f.action=action;
    CHECK(iq_irq_8498(&m)==IQ_TRANSFER&&m.boundary==IQ_MRET_BOUNDARY);
    CHECK(m.saved_words==29&&m.restored_words==29&&f.calls==1&&m.operations==61);
    CHECK(m.mepc.value==0x9008&&m.csr804.value==0x80);
    for(i=0;i<29;i++){
        uint32_t expected=action==2?0xd000+i:(action==1&&regs[i]==10?0xabc123:0x10000+regs[i]);
        CHECK(m.gpr[regs[i]].value==expected);
        CHECK(f.log[i].kind==IQ_WRITE32&&f.log[i].address==0x1004+4*i&&f.log[i].value.value==0x10000+regs[i]);
    }
    CHECK(m.gpr[2].value==(action==2?0x1180U:0x1080U));
    CHECK(m.gpr[3].value==(action==1?0x77770000U:0x2000U));
    CHECK(f.log[29].kind==IQ_READ32&&f.log[29].address==0x2180);
    CHECK(f.events==60&&f.log[59].kind==IQ_MRET&&f.log[59].pc==0x851a);
    for(i=0;i<f.events;i++)if(f.log[i].kind==IQ_WRITE32)CHECK(f.log[i].address!=0x1000&&f.log[i].address!=0x1078&&f.log[i].address!=0x107c);
    groups++;
}
static void boundaries(void){
    iq_model m;fixture f;unsigned i;
    setup(&m,&f);f.action=3;CHECK(iq_irq_8498(&m)==IQ_TRANSFER&&m.boundary==IQ_CALLBACK_BOUNDARY);
    CHECK(m.gpr[2].value==0x1000&&m.saved_words==29&&!m.restored_words&&m.operations==31);groups++;
    setup(&m,&f);f.action=4;CHECK(iq_irq_8498(&m)==IQ_HALT&&m.boundary==IQ_PROVIDER_UNKNOWN);
    CHECK(at(&f,0x1004)->value==0xdead&&!m.restored_words&&m.gpr[2].value==0x1000);groups++;
    setup(&m,&f);m.max_operations=3;CHECK(iq_irq_8498(&m)==IQ_OBSERVATION_LIMIT&&m.boundary==IQ_BUDGET);
    CHECK(m.saved_words==3&&m.gpr[2].value==0x1000&&f.events==3);groups++;
    setup(&m,&f);f.fail_pc=0x84a0;f.fail_after_effect=1;CHECK(iq_irq_8498(&m)==IQ_HALT);
    CHECK(m.saved_words==3&&at(&f,0x1010)->value==0x10006&&f.events==4);groups++;
    setup(&m,&f);m.gpr[2].known=0;CHECK(iq_restore_8448(&m)==IQ_HALT&&m.boundary==IQ_UNKNOWN_ADDRESS);
    CHECK(f.events==1&&m.gpr[11].value==32&&m.csr804.value==0xa0);groups++;
    setup(&m,&f);at(&f,0x2180)->known=0;CHECK(iq_irq_8498(&m)==IQ_HALT&&m.boundary==IQ_UNKNOWN_TARGET);
    CHECK(f.calls==0&&m.saved_words==29&&m.gpr[2].value==0x1000);groups++;
    setup(&m,&f);*at(&f,0x2180)=scalar(0);CHECK(iq_irq_8498(&m)==IQ_TRANSFER&&f.calls==1);groups++;
    setup(&m,&f);m.gpr[2]=scalar(0x1000);*at(&f,0x1000)=scalar(0x9008);
    for(i=0;i<29;i++)*at(&f,0x1004+4*i)=scalar(0x5000+i);
    at(&f,0x100c)->known=0;f.fail_pc=0x845c;CHECK(iq_restore_8448(&m)==IQ_HALT&&m.restored_words==3);
    CHECK(m.gpr[1].value==0x5000&&m.gpr[5].known==0&&m.mepc.value==0x9008&&m.gpr[2].value==0x1000);groups++;
    setup(&m,&f);m.gpr[2]=scalar(0x40);f.fail_pc=0x849a;CHECK(iq_irq_8498(&m)==IQ_HALT);
    CHECK(m.gpr[2].value==0xffffffc0&&f.log[0].address==0xffffffc4);groups++;
    setup(&m,&f);at(&f,0x2180)->known=UINT32_C(0xfffffffe);CHECK(iq_irq_8498(&m)==IQ_TRANSFER&&f.calls==1);groups++;
    setup(&m,&f);m.gpr[3].known=0;CHECK(iq_irq_8498(&m)==IQ_HALT&&m.boundary==IQ_UNKNOWN_ADDRESS);
    CHECK(m.saved_words==29&&f.calls==0&&f.events==29);groups++;
    setup(&m,&f);f.action=5;CHECK(iq_irq_8498(&m)==IQ_TRANSFER&&m.mepc.value==0x98765432);
    CHECK(f.log[f.events-1].target.value==0x98765432&&at(&f,0x1000)->value==0xdeadbeef);groups++;
}
int main(void){restore_case();frame_case(0);frame_case(1);frame_case(2);boundaries();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"original_executed\":false,\"hardware\":false}\n",groups,checks);return 0;}
