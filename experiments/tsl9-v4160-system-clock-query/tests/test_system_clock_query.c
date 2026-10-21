#include "system_clock_query.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {ri_value ram[16384],cfgr,mult,source,ext,source2,source3,prescale;
    sf_request trace[128];unsigned count;uint32_t stop_pc,move_gp_pc,new_gp,replace_clock;
    ri_flow stop_flow;unsigned ml_calls,sf_calls;int middle_mutate;
} fixture;
static fixture f;static sf_model s;static ml_model m;static unsigned groups,checks;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"check %u line %d: %s\n",checks,__LINE__,#x);exit(1);}}while(0)
static ri_value w(uint32_t n){ri_value v={n,UINT32_MAX};return v;}
static ri_value *mem(uint32_t a){CHECK(a>=0x20000000&&a<=0x2000fffc&&(a&3)==0);return &f.ram[(a-0x20000000)/4];}
static void put_byte(uint32_t addr,uint32_t value){ri_value *v=mem(addr&~3u);unsigned shift=(addr&3)*8;v->value=(v->value&~(255u<<shift))|((value&255u)<<shift);v->known|=255u<<shift;}
static ri_flow effect(void *ctx,sf_model *model,const sf_request *q,ri_value *out){
    ri_value *v;unsigned width,shift;uint32_t mask;CHECK(ctx==&f&&model==&s);CHECK(f.count<128);f.trace[f.count++]=*q;
    if(f.stop_pc==q->pc)return f.stop_flow;
    if(q->kind!=SF_RETURN)CHECK(q->address.known==UINT32_MAX);
    if(q->kind==SF_READ32){
        if(q->pc==0x18838)*out=f.cfgr;else if(q->pc==0x18882)*out=f.mult;else if(q->pc==0x18884)*out=f.source;
        else if(q->pc==0x1889e)*out=f.ext;else if(q->pc==0x188b4)*out=f.source2;
        else if(q->pc==0x188ce)*out=f.source3;else if(q->pc==0x18858)*out=f.prescale;
        else *out=*mem(q->address.value);
    }else if(q->kind==SF_READ8){v=mem(q->address.value&~3u);shift=(q->address.value&3)*8;out->value=v->value>>shift;out->known=v->known>>shift;}
    else if(q->kind!=SF_RETURN){
        width=q->kind==SF_WRITE8?8u:q->kind==SF_WRITE16?16u:32u;shift=(q->address.value&3)*8;
        CHECK(shift+width<=32);mask=width==32?UINT32_MAX:((UINT32_C(1)<<width)-1);v=mem(q->address.value&~3u);
        v->value=(v->value&~(mask<<shift))|((q->data.value&mask)<<shift);v->known=(v->known&~(mask<<shift))|((q->data.known&mask)<<shift);
    }
    if(q->pc==0x18864&&f.replace_clock)*mem(model->r.gp.value+108)=w(f.replace_clock);
    if(q->pc==f.move_gp_pc)model->r.gp=w(f.new_gp);
    return RI_RETURNED;
}
static ri_flow ml_effect(void *ctx,const ml_request *q,ri_value *out){
    CHECK(ctx==&f);if(q->kind==ML_WRITE32)*mem(q->address.value)=q->data;
    else if(q->kind==ML_READ32)*out=*mem(q->address.value);else CHECK(0);return RI_RETURNED;
}
static ri_flow ml_call(void *ctx,ml_model *model,const ml_request *q,ml_call_result *out){
    CHECK(ctx==&f&&model==&m);++f.ml_calls;
    if(q->pc==0x9254||q->pc==0x925c){++f.sf_calls;return sf_ml_init_call(&s,model,q,out);}
    if(f.middle_mutate&&q->pc==0x9258){model->r.gp=w(0x20005000);*mem(0x2000506c)=w(120000000);model->r.a[0]=w(0x7654);}
    out->returned_to=q->continuation;return RI_RETURNED;
}
static void fresh(void){sf_backend b;ml_backend mb;unsigned i;static const unsigned char table[]={0,0,0,0,0,0,0,0,1,2,3,4,6,7,8,9};
    memset(&f,0,sizeof f);b.context=&f;b.effect=effect;sf_init(&s,SF_ID2966_0EE64183,&b);
    s.r.gp=w(0x20004000);s.r.sp=w(0x20010000);s.r.ra=w(0x9258);s.r.a[0]=w(0x1122);s.r.s[0]=w(0x7788);
    f.cfgr=f.mult=f.source=f.ext=f.source2=f.source3=f.prescale=w(0);
    for(i=0;i<16;i++)put_byte(0x20004040+i,table[i]);
    mb.context=&f;mb.effect=ml_effect;mb.call=ml_call;ml_init(&m,ML_ID2966_0EE64183,&mb);m.r=s.r;
}
static void selection(void){
    ++groups;fresh();CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==8000000&&s.r.a[0].value==0x1122&&s.r.sp.value==0x20010000&&s.return_target.value==0x9258);
    CHECK(f.count==7&&f.trace[0].pc==0x18838&&f.trace[1].pc==0x18850&&f.trace[2].pc==0x18858&&f.trace[3].pc==0x18864&&f.trace[4].pc==0x1886c&&f.trace[5].pc==0x18872&&f.trace[6].pc==0x18876);
    fresh();f.cfgr=w(4);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==32000000);
    fresh();f.cfgr=w(12);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==8000000);
    fresh();f.cfgr=w(8);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==8000000); /* 4M*2 */
    fresh();f.cfgr=w(8);f.ext=w(16);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==16000000); /* 8M*2 */
    fresh();f.cfgr=w(8);f.source=w(0x10000);f.source2=w(0xc00000);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==32000000); /* 16M*2 */
    fresh();f.cfgr=w(8);f.source=w(0x10000);f.source2=w(0);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==16000000);
    fresh();f.cfgr=w(8);f.source=w(0x10000);f.source2=w(0);f.source3=w(0x20000);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==8000000);
    fresh();f.cfgr=w(8);f.mult=w(15u<<18);f.ext=w(16);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==144000000);
}
static void live_values(void){
    ++groups;fresh();f.cfgr=w(4);f.prescale=w(8u<<4);f.replace_clock=100;CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==50);
    fresh();f.prescale=w(15u<<4);put_byte(0x2000404f,33);CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==4000000); /* shift low5 */
    fresh();f.move_gp_pc=0x18850;f.new_gp=0x20005000;put_byte(0x20005040,0);*mem(0x2000506c)=w(77);
    CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==8000000&&mem(0x2000506c)->value==77&&s.r.gp.value==0x20005000);
}
static void derived(void){
    static const uint32_t values[]={0,7999999,8000000,144000000,2048000000u,UINT32_MAX};unsigned i;
    ++groups;for(i=0;i<sizeof values/sizeof values[0];i++){
        uint32_t quotient=(values[i]/8000000)&255u;fresh();*mem(0x2000406c)=w(values[i]);s.r.ra=w(0x9260);
        CHECK(sf_derive_1973c(&s)==RI_RETURNED&&f.count==4&&s.r.a[0].value==0x1122&&s.return_target.value==0x9260);
        CHECK(f.trace[1].pc==0x19752&&f.trace[1].kind==SF_WRITE8&&f.trace[1].data.value==quotient);
        CHECK(f.trace[2].pc==0x1975e&&f.trace[2].kind==SF_WRITE16&&f.trace[2].data.value==((quotient*1000)&65535u));
    }
    fresh();mem(0x2000406c)->known=0;CHECK(sf_derive_1973c(&s)==RI_RETURNED&&f.trace[1].data.known==UINT32_C(0xffffff00)&&((f.trace[2].data.known&7u)==7u));
}
static void stops(void){
    ++groups;fresh();f.cfgr.known=0;CHECK(sf_query_18834(&s)==RI_HALT&&s.boundary_pc==0x1883e&&f.count==1);
    fresh();f.cfgr=w(8);f.mult.known=0;CHECK(sf_query_18834(&s)==RI_HALT&&s.boundary_pc==0x18892&&f.count==3);
    fresh();f.stop_pc=0x1886c;f.stop_flow=RI_TRANSFER;CHECK(sf_query_18834(&s)==RI_TRANSFER&&mem(0x2000406c)->value==8000000&&f.trace[f.count-1].pc==0x1886c);
    fresh();s.budget=2;CHECK(sf_query_18834(&s)==RI_LIMIT&&s.boundary==SF_BUDGET&&s.last_request.pc==0x18858&&f.count==2);
    fresh();s.backend.effect=0;CHECK(sf_query_18834(&s)==RI_HALT&&s.boundary==SF_MISSING_PROVIDER&&f.count==0);
    fresh();s.profile=SF_UNKNOWN_IMAGE;CHECK(sf_query_18834(&s)==RI_HALT&&s.operations==0);
}
static void composition(void){
    unsigned count;++groups;fresh();f.cfgr=w(4);f.middle_mutate=1;
    CHECK(ml_initialize_9250(&m)==RI_RETURNED&&f.ml_calls==15&&f.sf_calls==2&&m.r.gp.value==0x20005000&&m.r.a[0].value==0x7654);
    CHECK(mem(0x2000406c)->value==32000000&&((mem(0x2000517c)->value>>16)&255u)==15u&&(mem(0x2000517c)->value&65535u)==15000u);
    fresh();s.budget=2;CHECK(ml_initialize_9250(&m)==RI_LIMIT&&m.boundary==ML_PROVIDER_STOP&&s.boundary==SF_BUDGET&&m.r.sp.value==0x2000fff0&&f.sf_calls==1);
    count=f.count;CHECK(sf_query_18834(&s)==RI_LIMIT&&f.count==count);
}
static void partial_knowledge(void){
    ++groups;fresh();f.cfgr.value=8;f.cfgr.known=12;f.mult.value=15u<<18;f.mult.known=15u<<18;f.source.value=0;f.source.known=0x10000;f.ext.value=16;f.ext.known=16;
    CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==144000000&&mem(0x2000406c)->known==UINT32_MAX);
    fresh();f.cfgr=w(8);f.mult.known=~(1u<<18); /* multiplier2or3: neither17 */
    CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==(8000000u&12000000u)&&mem(0x2000406c)->known==~(8000000u^12000000u));
    fresh();mem(0x20004040)->known&=~1u;CHECK(sf_query_18834(&s)==RI_RETURNED&&mem(0x2000406c)->value==(8000000u&4000000u)&&mem(0x2000406c)->known==~(8000000u^4000000u));
    fresh();mem(0x2000406c)->value=8000000;mem(0x2000406c)->known=UINT32_C(0xfffffffe);
    CHECK(sf_derive_1973c(&s)==RI_RETURNED&&f.trace[1].data.value==1&&f.trace[1].data.known==UINT32_MAX);
    fresh();f.cfgr=w(8);f.source=w(0x10000);f.source2.known=~(1u<<23);f.source3.known=~(1u<<17);
    CHECK(sf_query_18834(&s)==RI_HALT&&s.boundary_pc==0x188d4&&f.trace[f.count-1].pc==0x188ce);
    fresh();f.cfgr=w(8);f.source=w(0x10000);f.source2.value=0x400000;f.source2.known=0x400000;
    CHECK(sf_query_18834(&s)==RI_HALT&&s.boundary_pc==0x188bc&&f.trace[f.count-1].pc==0x188b4);
}
static void bridge_binding(void){
    ml_request q;ml_call_result out;++groups;memset(&q,0,sizeof q);memset(&out,0,sizeof out);q.kind=ML_CALL;q.pc=0x9254;q.raw_target=q.target=w(0x18834);q.continuation=w(0x9258);
    fresh();q.tail=1;CHECK(sf_ml_init_call(&s,&m,&q,&out)==RI_HALT&&s.boundary==SF_BINDING&&s.operations==0);
    fresh();q.tail=0;q.raw_target.known=0;CHECK(sf_ml_init_call(&s,&m,&q,&out)==RI_HALT&&s.operations==0);
    fresh();q.raw_target=w(0x18834);m.flow=RI_TRANSFER;CHECK(sf_ml_init_call(&s,&m,&q,&out)==RI_HALT&&s.operations==0);
    fresh();q.pc=0x9258;CHECK(sf_ml_init_call(&s,&m,&q,&out)==RI_HALT&&s.operations==0);
}
int main(void){selection();live_values();derived();stops();composition();partial_knowledge();bridge_binding();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;}
