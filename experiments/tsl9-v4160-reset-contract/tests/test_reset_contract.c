#include "reset_contract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define GP UINT32_C(0x20004000)
#define INIT UINT32_C(0x1ab60)
static unsigned checks,groups;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
typedef struct {
    uint8_t source[128],source_known[128],ram[35160],known[35160];
    rc_request trace[9000];unsigned count,cut,clock,tail,csr_count;
    rc_flow cut_flow;uint32_t csr[5];int mutate_source,mutate_clock;
} fixture;
static fixture f,g;
static rc_flow provider(void *ctx,const rc_request *q,rc_scalar *out){
    fixture *x=(fixture *)ctx;unsigned i;CHECK(x->count<9000);x->trace[x->count++]=*q;if(x->cut && x->count==x->cut)return x->cut_flow;
    out->value=out->known=0;
    if(q->kind==RC_READ32){CHECK(q->address>=INIT && q->address-INIT<=124 && !(q->address&3u));for(i=0;i<4;i++){out->value|=(uint32_t)x->source[q->address-INIT+i]<<(8*i);out->known|=(uint32_t)x->source_known[q->address-INIT+i]<<(8*i);}if(x->mutate_source && q->address==INIT)x->source[4]=77;}
    else if(q->kind==RC_WRITE32){CHECK(q->address>=GP && q->address-GP<=sizeof(x->ram)-4 && !(q->address&3u));for(i=0;i<4;i++){x->ram[q->address-GP+i]=(uint8_t)(q->value>>(8*i));x->known[q->address-GP+i]=(uint8_t)(q->known>>(8*i));}}
    else if(q->kind==RC_CSR_WRITE || q->kind==RC_CSR_SET){CHECK(x->csr_count<5);x->csr[x->csr_count++]=q->value;}
    else if(q->kind==RC_CLOCK){CHECK(q->target==0x1874a);x->clock++;if(x->mutate_clock)x->ram[0]=91;}
    else if(q->kind==RC_HANDOFF){CHECK(q->target==0x40000);x->tail++;}
    else CHECK(0);
    return RC_RETURNED;
}
static void reset(fixture *x,rc_model *m){unsigned i;rc_backend b;memset(x,0,sizeof(*x));memset(x->ram,0xcc,sizeof(x->ram));memset(x->known,255,sizeof(x->known));memset(x->source_known,255,sizeof(x->source_known));for(i=0;i<128;i++)x->source[i]=(uint8_t)(i*11u+5u);b.context=x;b.invoke=provider;rc_init(m,&b);}
static void normal(void){rc_model m;unsigned i;reset(&f,&m);CHECK(rc_reset(&m)==RC_TRANSFER && m.boundary==RC_ROM_BOUNDARY && m.handoff_target==0x40000);CHECK(m.initial_gp==GP && m.initial_sp==0x20010000 && m.copied_words==32 && m.zero_words==8758);CHECK(f.count==8829 && m.operations==8829 && f.clock==1 && f.tail==1 && f.csr_count==5);CHECK(!memcmp(f.ram,f.source,128));for(i=128;i<sizeof(f.ram);i++)CHECK(f.ram[i]==0 && f.known[i]==255);CHECK(f.trace[0].pc==0x186ce && f.trace[0].address==INIT && f.trace[1].pc==0x186d2 && f.trace[1].address==GP);CHECK(f.trace[64].pc==0x186ee && f.trace[64].address==GP+128);CHECK(f.trace[8821].address==0x2000c954);CHECK(f.csr[0]==31 && f.csr[1]==3 && f.csr[2]==0x1888 && f.csr[3]==0x803b && f.csr[4]==0x9008);CHECK(f.trace[8824].kind==RC_CSR_SET && f.trace[8824].csr==0x300);CHECK(f.trace[8825].csr==0x305 && f.trace[8827].csr==0x341);groups++;}
static void ordering(void){rc_model m;reset(&f,&m);f.mutate_source=1;CHECK(rc_reset(&m)==RC_TRANSFER && f.ram[4]==77);reset(&f,&m);f.mutate_clock=1;CHECK(rc_reset(&m)==RC_TRANSFER && f.ram[0]==91);CHECK(f.trace[8826].kind==RC_CLOCK && f.trace[8826].pc==0x18720 && f.trace[8827].kind==RC_CSR_WRITE && f.trace[8827].pc==0x1872c && f.trace[8828].pc==0x18730);groups++;}
static void unknown_data(void){rc_model m;reset(&f,&m);f.source_known[0]=0;f.source_known[7]=0x0f;CHECK(rc_reset(&m)==RC_TRANSFER && f.known[0]==0 && f.known[7]==0x0f);CHECK(f.known[128]==255 && f.ram[128]==0);groups++;}
static void prefix_cuts(void){static const unsigned points[]={1,2,63,64,65,66,8821,8822,8823,8826,8827,8828,8829};rc_model m;unsigned i,j,mode;reset(&g,&m);CHECK(rc_reset(&m)==RC_TRANSFER);for(mode=0;mode<2;mode++)for(i=0;i<sizeof(points)/sizeof(points[0]);i++){reset(&f,&m);f.cut=points[i];f.cut_flow=mode?RC_TRANSFER:RC_HALT;CHECK(rc_reset(&m)==f.cut_flow && f.count==points[i]);CHECK(!memcmp(f.trace,g.trace,points[i]*sizeof(rc_request)));if(points[i]==2)CHECK(f.ram[0]==0xcc);if(points[i]==64)CHECK(!memcmp(f.ram,f.source,124) && f.ram[124]==0xcc);if(points[i]>=65)CHECK(!memcmp(f.ram,f.source,128));if(points[i]==8827)CHECK(f.csr_count==4 && !f.clock && !f.tail);if(points[i]==8828)CHECK(f.clock==1 && f.csr_count==4 && !f.tail);if(points[i]==8829){CHECK(f.csr_count==5 && !f.tail);for(j=128;j<sizeof(f.ram);j++)CHECK(f.ram[j]==0);}}groups++;}
static void budgets(void){rc_model m;reset(&f,&m);m.max_operations=0;CHECK(rc_reset(&m)==RC_OBSERVATION_LIMIT && !f.count && m.boundary==RC_BUDGET);reset(&f,&m);m.max_operations=64;CHECK(rc_reset(&m)==RC_OBSERVATION_LIMIT && m.copied_words==32 && !m.zero_words && !memcmp(f.ram,f.source,128) && f.ram[128]==0xcc);reset(&f,&m);m.max_operations=8828;CHECK(rc_reset(&m)==RC_OBSERVATION_LIMIT && f.clock==1 && f.csr_count==5 && !f.tail);rc_init(&m,NULL);CHECK(rc_reset(&m)==RC_HALT && m.operations==1);groups++;}
int main(void){normal();ordering();unknown_data();prefix_cuts();budgets();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"synthetic_backend_only\":true}\n",groups,checks);return 0;}
