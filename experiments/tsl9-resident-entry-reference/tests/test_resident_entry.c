#include "resident_entry.h"
#include "reset_entry_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {ri_value ram[16384];uint32_t reads,writes,returns,mrets,binds,missing_reads;
    uint32_t fail_pc,fail_address,mutate_ra,wrong_code;ri_flow fail_flow;int strict,unknown_last,unknown_ra;
    ri_request last;ri_value last_missing_write;uint32_t last_restore_seen;
} fixture;
static fixture f;static ri_model m;static unsigned checks,groups;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"check %u line %d: %s\n",checks,__LINE__,#x);exit(1);}}while(0)
static ri_value w(uint32_t n){ri_value v={n,UINT32_MAX};return v;}
static ri_value *ram(uint32_t a){CHECK(a>=0x20000000&&a<=0x2000fffc&&(a&3)==0);return &f.ram[(a-0x20000000)/4];}
static ri_flow effect(void *context,const ri_request *q,ri_value *out){
    fixture *s=(fixture *)context;CHECK(s==&f);s->last=*q;
    if(s->fail_pc==q->pc&&(!s->fail_address||s->fail_address==q->address.value))return s->fail_flow;
    if(q->kind==RI_READ32){
        ++s->reads;CHECK(q->address.known==UINT32_MAX);
        if(q->address.value==0x6eb2c){++s->missing_reads;if(s->strict)return RI_HALT;if(s->unknown_last){out->value=0;out->known=0;return RI_RETURNED;}}
        if(q->address.value>=0x20000000){*out=*ram(q->address.value);if(q->pc==0x6de72)s->last_restore_seen=q->address.value;}
        else *out=w(q->address.value^0xabcddcba);
    }else if(q->kind==RI_WRITE32){
        ++s->writes;CHECK(q->address.known==UINT32_MAX);*ram(q->address.value)=q->data;
        if(q->stage==RI_COPY2&&q->address.value==0x20002ef8)s->last_missing_write=q->data;
        if(q->stage==RI_COPY1&&s->mutate_ra)*ram(0x2000fffc)=w(s->mutate_ra);
        if(q->stage==RI_COPY1&&s->unknown_ra){ram(0x2000fffc)->value=0;ram(0x2000fffc)->known=1;}
    }else if(q->kind==RI_RETURN)++s->returns;
    else if(q->kind==RI_MRET){++s->mrets;*out=w(0x9008);}
    else CHECK(0);
    return RI_RETURNED;
}
static ri_flow bind(void *context,const ri_request *q){
    fixture *s=(fixture *)context;CHECK(s==&f);++s->binds;
    CHECK(q->target.known==UINT32_MAX);
    if(s->wrong_code)return RI_HALT;
    CHECK((q->kind==RI_BIND_COPY&&q->target.value==0x20000010&&q->argc==3)||
          (q->kind==RI_BIND_ZERO&&q->target.value==0x20000022&&q->argc==0));
    return RI_RETURNED;
}
static void fresh(void){ri_backend b;memset(&f,0,sizeof f);b.context=&f;b.effect=effect;b.bind=bind;ri_init(&m,RI_DEC2023_133D3705,&b);}
static void full_synthetic(void){
    ++groups;fresh();CHECK(ri_enter(&m)==RI_TRANSFER);
    CHECK(m.boundary==RI_MRET_BOUNDARY&&m.boundary_pc==0x6debe&&m.return_target.value==0x9008);
    CHECK(m.gp.value==0x20004000&&m.sp.value==0x20010000&&m.ra.value==0x6debe);
    CHECK(m.seed_words==12&&m.first_words==2957&&m.second_words==35&&m.zero_words==456);
    CHECK(f.binds==3&&f.returns==3&&f.mrets==1&&f.missing_reads==1);
    CHECK(ram(0x20000000)->value==0x200007d0&&ram(0x20000004)->value==0x2000251c&&ram(0x20000008)->value==0x20002e34);
    CHECK(m.a0.value==0x6eb30&&m.a1.value==0x20002efc&&m.a2.value==0x20002ef8&&m.a5.value==0x20003618);
}
static void strict_missing_prefix(void){
    ++groups;fresh();f.strict=1;CHECK(ri_enter(&m)==RI_HALT);
    CHECK(m.boundary==RI_PROVIDER_STOP&&m.boundary_pc==0x20000016);
    CHECK(m.seed_words==12&&m.first_words==2957&&m.second_words==34&&m.zero_words==0);
    CHECK(f.binds==2&&f.returns==1&&f.mrets==0&&f.missing_reads==1&&f.last_restore_seen==0);
    CHECK(m.sp.value==0x2000fff0&&m.ra.value==0x6de72);
    CHECK(m.a0.value==0x6eb2c&&m.a1.value==0x20002ef8&&m.a2.value==0x20002ef8);
    CHECK(f.last.kind==RI_READ32&&f.last.address.value==0x6eb2c);
    CHECK(ram(0x20002ef8)->known==0); /* no pending store or zero fill. */
    CHECK(ri_enter(&m)==RI_HALT&&f.mrets==0);
}
static void unknown_data_and_routes(void){
    ++groups;fresh();f.unknown_last=1;CHECK(ri_enter(&m)==RI_TRANSFER);
    CHECK(f.last_missing_write.known==0&&ram(0x20002ef8)->known==UINT32_MAX&&ram(0x20002ef8)->value==0);
    CHECK(f.last_restore_seen==0x2000fffc&&m.zero_words==456);
    fresh();f.mutate_ra=0x1235;CHECK(ri_enter(&m)==RI_TRANSFER);
    CHECK(m.boundary==RI_OTHER_RETURN&&m.return_target.value==0x1234&&f.mrets==0&&m.zero_words==456);
    CHECK(m.sp.value==0x20010000&&m.ra.value==0x1235);
    fresh();f.unknown_ra=1;CHECK(ri_enter(&m)==RI_HALT);
    CHECK(m.boundary==RI_UNKNOWN_CONTROL&&f.mrets==0&&m.zero_words==456);
}
static void boundaries(void){
    unsigned i;++groups;
    for(i=0;i<2;i++){
        fresh();f.fail_pc=0x2000001c;f.fail_address=0x20000040;f.fail_flow=i?RI_TRANSFER:RI_HALT;
        CHECK(ri_enter(&m)==f.fail_flow);
        CHECK(m.a0.value==0x402b4&&m.a1.value==0x20000044&&m.first_words==0&&m.zero_words==0);
        CHECK(m.sp.value==0x2000fff0&&f.mrets==0&&f.binds==1);
    }
    fresh();m.budget=25;CHECK(ri_enter(&m)==RI_LIMIT&&m.boundary==RI_BUDGET);
    CHECK(m.seed_words==12&&m.sp.value==0x2000fff0&&m.first_words==0&&f.mrets==0);
    fresh();f.wrong_code=1;CHECK(ri_enter(&m)==RI_HALT&&m.first_words==0&&f.binds==1&&m.zero_words==0);
    fresh();m.backend.bind=0;CHECK(ri_enter(&m)==RI_HALT&&m.boundary==RI_MISSING_PROVIDER&&m.first_words==0);
    fresh();m.profile=RI_UNKNOWN_PROFILE;CHECK(ri_enter(&m)==RI_HALT&&m.boundary==RI_PROFILE&&m.operations==0);
}
static void bridge(void){
    rc_request q;rc_scalar out;uint32_t old;++groups;fresh();memset(&q,0,sizeof q);
    q.kind=RC_HANDOFF;q.pc=0x18730;q.target=0x40000;f.strict=1;
    CHECK(ri_reset_handoff(&m,&q,&out)==RC_HALT&&m.second_words==34&&m.zero_words==0);
    old=m.operations;CHECK(ri_reset_handoff(&m,&q,&out)==RC_HALT&&m.operations==old);
    fresh();CHECK(ri_reset_handoff(&m,&q,&out)==RC_TRANSFER&&out.value==0x9008&&out.known==UINT32_MAX&&f.mrets==1);
    fresh();q.pc=0x18734;CHECK(ri_reset_handoff(&m,&q,&out)==RC_HALT&&m.operations==0);
    fresh();q.pc=0x18730;q.target=0x40004;CHECK(ri_reset_handoff(&m,&q,&out)==RC_HALT&&m.operations==0);
    fresh();q.target=0x40000;m.budget=25;CHECK(ri_reset_handoff(&m,&q,&out)==RC_OBSERVATION_LIMIT&&f.mrets==0);
}
int main(void){full_synthetic();strict_missing_prefix();unknown_data_and_routes();boundaries();bridge();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;}
