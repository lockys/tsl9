#include "flash_contract.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static unsigned checks, groups;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"check failed line %d: %s\n",__LINE__,#x); exit(1); } } while(0)
typedef struct {
    fc_request trace[512]; unsigned count, cut, timer_polls, source_reads, stores;
    fc_flow cut_flow; uint32_t flash_ctrl, timer_ctrl, source_known;
    int unknown_flash_status, unknown_scale, busy, timer_never, unaligned_trap;
} fixture;
static fc_flow backend(void *context,const fc_request *q,fc_scalar *out) {
    fixture *f=(fixture *)context;
    CHECK(f->count<512); f->trace[f->count++]=*q;
    if(f->cut && f->count==f->cut) return f->cut_flow;
    out->known=UINT32_MAX; out->value=0;
    switch(q->kind) {
    case FC_MMIO_READ:
        if(q->address==0x40022010) out->value=f->flash_ctrl;
        else if(q->address==0x4002200c) { out->value=f->busy?3u:0u; if(f->unknown_flash_status)out->known=0; }
        else if(q->address==0xe000f000)out->value=f->timer_ctrl;
        else if(q->address==0xe000f004)out->value=q->pc==0x19768?0xa3u:((++f->timer_polls>=2 && !f->timer_never)?1u:0u);
        else CHECK(0);
        break;
    case FC_MMIO_WRITE:
        CHECK(q->known==UINT32_MAX);
        if(q->address==0x40022010)f->flash_ctrl=q->value;
        if(q->address==0xe000f000)f->timer_ctrl=q->value;
        break;
    case FC_RAM_BYTE_READ: out->value=7;out->known=f->unknown_scale?0:255;break;
    case FC_SOURCE_WORD_READ:
        if(f->unaligned_trap && (q->address&3u))return FC_TRANSFER;
        out->value=q->address^0x9a5aa55a;out->known=f->source_known;f->source_reads++;break;
    case FC_DEST_WORD_STORE: f->stores++;break;
    default:CHECK(0);
    }
    return FC_RETURNED;
}
static void reset(fixture *f,fc_model *m) {
    fc_backend b;memset(f,0,sizeof(*f));f->flash_ctrl=0x60000000;f->timer_ctrl=0x200;f->source_known=UINT32_MAX;
    b.context=f;b.invoke=backend;fc_init(m,&b);m->poll_budget=3;m->gp=0x20004000;m->gp_known=UINT32_MAX;
}
static fc_flow run(fc_model *m,uint32_t ignored,uint32_t source) {return fc_write_registers(m,0x1ab37,ignored,source);}
static void normal(void) {
    fixture f,g;fc_model m,n;unsigned i,keys=0,cmp=0,scale=0;
    reset(&f,&m);CHECK(run(&m,0,0x20005000)==FC_RETURNED);CHECK(m.result_known==UINT32_MAX && m.result==0);CHECK(m.words_written==64 && f.stores==64 && f.source_reads==64);
    CHECK(m.destination==0x1ab00 && m.source==0x20005000);CHECK(f.timer_polls==2);CHECK((f.flash_ctrl&0x8000)!=0 && (f.flash_ctrl&0x30000)==0);CHECK((f.timer_ctrl&0x31)==0x30);
    for(i=0;i<f.count;i++) {
        fc_request *q=&f.trace[i];
        CHECK(q->kind>=FC_MMIO_READ && q->kind<=FC_RAM_BYTE_READ);
        if(q->kind==FC_MMIO_WRITE && (q->address==0x40022004 || q->address==0x40022024)) {CHECK(q->value==((keys&1)?0xcdef89abu:0x45670123u));CHECK(q->address==(keys<2?0x40022004u:0x40022024u));keys++;}
        if(q->kind==FC_SOURCE_WORD_READ) {unsigned j=i+1;CHECK(j<f.count && f.trace[j].kind==FC_DEST_WORD_STORE);CHECK(f.trace[j].address==0x1ab00+(q->address-0x20005000));CHECK(f.trace[j].value==(q->address^0x9a5aa55a));}
        if(q->kind==FC_RAM_BYTE_READ) {CHECK(q->address==0x2000417e && q->pc==0x19770 && q->width==8);scale++;}
        if(q->kind==FC_MMIO_WRITE && q->address==0xe000f010) {CHECK(q->value==7 && q->pc==0x19778);cmp++;}
        CHECK(!(q->kind==FC_MMIO_WRITE && q->address==0x4002200c));
    }
    CHECK(keys==4 && cmp==1 && scale==1);reset(&g,&n);CHECK(run(&n,UINT32_MAX,0x20005000)==FC_RETURNED);CHECK(f.count==g.count && memcmp(f.trace,g.trace,sizeof(fc_request)*f.count)==0);groups++;
}
static void interrupted(void) {
    fixture normal_f,f;fc_model m;unsigned cut,k;reset(&normal_f,&m);CHECK(run(&m,1,0x20005000)==FC_RETURNED);
    for(k=0;k<2;k++) for(cut=1;cut<=normal_f.count;cut++) {
        reset(&f,&m);f.cut=cut;f.cut_flow=k?FC_TRANSFER:FC_HALT;
        CHECK(run(&m,1,0x20005000)==f.cut_flow);CHECK(f.count==cut);CHECK(!m.result_known);CHECK(memcmp(f.trace,normal_f.trace,sizeof(fc_request)*cut)==0);
    }
    groups++;
}
static void unknowns(void) {
    fixture f;fc_model m;reset(&f,&m);f.unknown_flash_status=1;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_CONDITION_UNKNOWN && !m.result_known && f.stores==0);
    reset(&f,&m);f.unknown_scale=1;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_OPERAND_UNKNOWN && f.stores==64 && !m.result_known);
    reset(&f,&m);m.gp_known=0;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_OPERAND_UNKNOWN && m.boundary_pc==0x19770);
    reset(&f,&m);f.busy=1;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_SPIN_BUDGET && !m.result_known && f.stores==0);
    reset(&f,&m);f.timer_never=1;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_SPIN_BUDGET && f.stores==64 && !m.result_known);
    reset(&f,&m);m.poll_budget=0;CHECK(run(&m,0,0x20005000)==FC_HALT);CHECK(m.boundary==FC_SPIN_BUDGET && !m.result_known);
    reset(&f,&m);f.unaligned_trap=1;CHECK(run(&m,0,0x20005001)==FC_TRANSFER);CHECK(f.stores==0 && !m.result_known);
    fc_init(&m,NULL);CHECK(run(&m,0,0)==FC_HALT);CHECK(m.boundary==FC_PROVIDER_UNKNOWN && !m.result_known);groups++;
}
static void partial_and_wrap(void) {
    fixture f;fc_model m;unsigned i,seen=0;reset(&f,&m);f.source_known=0x00ff00ff;CHECK(run(&m,0,0xfffffffc)==FC_RETURNED);
    for(i=0;i<f.count;i++)if(f.trace[i].kind==FC_SOURCE_WORD_READ) {CHECK(f.trace[i].address==UINT32_C(0xfffffffc)+4u*seen);CHECK(f.trace[i+1].known==0x00ff00ff);seen++;}
    CHECK(seen==64 && m.result_known==UINT32_MAX);groups++;
}
int main(void) {normal();interrupted();unknowns();partial_and_wrap();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"synthetic_backend_only\":true}\n",groups,checks);return 0;}
