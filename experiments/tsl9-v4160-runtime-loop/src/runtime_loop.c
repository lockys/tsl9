#include "runtime_loop.h"
#include <string.h>
static ri_value word(uint32_t n){ri_value v={n,UINT32_MAX};return v;}
static ri_value target(ri_value v){v.value&=~UINT32_C(1);v.known|=1;return v;}
static int equal(ri_value a,ri_value b){
    uint32_t k=a.known&b.known;
    if((a.value^b.value)&k)return 0;return k==UINT32_MAX?1:-1;
}
/* Source-specific numeric dataflow only. Unknown bits are sets of possibilities,
 * not zero-filled RAM; all addition is wrapping unsigned arithmetic. */
static ri_value add(ri_value a,uint32_t b){
    ri_value r={0,0};unsigned bit,carry=1;
    for(bit=0;bit<32;bit++){
        unsigned values=0,next=0,x,c,bb=(b>>bit)&1u;
        unsigned xs=(a.known&(UINT32_C(1)<<bit))?(1u<<((a.value>>bit)&1u)):3u;
        for(x=0;x<2;x++)for(c=0;c<2;c++)if((xs&(1u<<x))&&(carry&(1u<<c))){
            unsigned sum=x+bb+c;values|=1u<<(sum&1u);next|=1u<<(sum>>1);
        }
        if(values!=3){r.known|=UINT32_C(1)<<bit;if(values==2)r.value|=UINT32_C(1)<<bit;}
        carry=next;
    }return r;
}
static ri_value and_mask(ri_value a,uint32_t mask){a.value&=mask;a.known=(a.known&mask)|~mask;return a;}
static ri_value xor_value(ri_value a,ri_value b){ri_value r={a.value^b.value,a.known&b.known};r.value&=r.known;return r;}
static ri_value bit_from_events(ri_value events,unsigned index){
    ri_value v={(events.value>>index)&1u,((events.known>>index)&1u)|UINT32_C(0xfffffffe)};return v;
}
static ri_value shifted_one(ri_value shift){
    uint32_t possible=0;unsigned n;ri_value v={0,0};
    for(n=0;n<32;n++)if(!((n^shift.value)&shift.known&31u))possible|=UINT32_C(1)<<n;
    v.known=~possible;if(possible&&!(possible&(possible-1))){v.value=possible;v.known=UINT32_MAX;}return v;
}
static ri_flow stop(ml_model *m,ml_boundary why,uint32_t pc){m->flow=RI_HALT;m->boundary=why;m->boundary_pc=pc;return m->flow;}
static ml_request request(ml_model *m,ml_kind kind,uint32_t pc){
    ml_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;q.registers=m->r;return q;
}
static int ready(ml_model *m,const ml_request *q,int is_call){
    m->last_request=*q;
    if(m->operations>=m->budget){m->flow=RI_LIMIT;m->boundary=ML_BUDGET;m->boundary_pc=q->pc;return 0;}
    ++m->operations;
    if((is_call&&!m->backend.call)||(!is_call&&!m->backend.effect)){(void)stop(m,ML_MISSING_PROVIDER,q->pc);return 0;}
    return 1;
}
static int accepted(ml_model *m,ri_flow flow,uint32_t pc){
    if(flow==RI_RETURNED)return 1;
    m->flow=flow;m->boundary=flow==RI_TRANSFER?ML_PROVIDER_TRANSFER:ML_PROVIDER_STOP;m->boundary_pc=pc;return 0;
}
static int effect(ml_model *m,ml_request *q,ri_value *out){
    ri_value v={0,0};if(!ready(m,q,0))return 0;
    if(!accepted(m,m->backend.effect(m->backend.context,q,&v),q->pc))return 0;
    if(out)*out=v;return 1;
}
static int store(ml_model *m,uint32_t pc,ri_value address,ri_value data){
    ml_request q=request(m,ML_WRITE32,pc);q.address=address;q.data=data;return effect(m,&q,0);
}
static int load(ml_model *m,uint32_t pc,ri_value address,ri_value *out,int byte){
    ml_request q=request(m,byte?ML_READ8:ML_READ32,pc);ri_value v;q.address=address;
    if(!effect(m,&q,&v))return 0;*out=byte?and_mask(v,255):v;return 1;
}
static int route(ml_model *m,ri_value returned,ri_value expected,uint32_t pc){
    int same=equal(returned,expected);m->return_target=returned;
    if(same==0){m->flow=RI_TRANSFER;m->boundary=ML_OTHER_RETURN;m->boundary_pc=pc;return 0;}
    if(same==1)return 1;
    (void)stop(m,ML_UNKNOWN_CONTROL,pc);return 0;
}
static int call(ml_model *m,uint32_t pc,ri_value raw,uint32_t continuation,int tail){
    ml_request q;ml_call_result result;ri_value normalized=target(raw);ri_flow flow;
    /* Observation is at the callee/provider boundary, after the local link
     * assignment, even when its provider/budget/target knowledge is absent. */
    if(!tail)m->r.ra=word(continuation);
    q=request(m,ML_CALL,pc);
    q.raw_target=raw;q.target=normalized;q.tail=(uint32_t)tail;
    q.continuation=tail?target(m->r.ra):word(continuation);
    if(normalized.known!=UINT32_MAX){m->last_request=q;(void)stop(m,ML_UNKNOWN_CONTROL,pc);return 0;}
    if(!ready(m,&q,1))return 0;
    q.registers=m->r;m->last_request=q;memset(&result,0,sizeof result);++m->calls;
    flow=m->backend.call(m->backend.context,m,&q,&result);
    if(!accepted(m,flow,pc))return 0;
    return route(m,result.returned_to,q.continuation,pc);
}
static int return_effect(ml_model *m,uint32_t pc){
    ml_request q=request(m,ML_RETURN,pc);q.raw_target=m->r.ra;q.target=target(m->r.ra);
    m->return_target=q.target;m->result=m->r.a[0];return effect(m,&q,0);
}
static int admit(ml_model *m,uint32_t pc){
    if(m->flow!=RI_RETURNED)return 0;
    if(m->profile!=ML_ID2966_0EE64183){(void)stop(m,ML_BINDING,pc);return 0;}return 1;
}
void ml_new_activation(ml_model *m){
    m->flow=RI_RETURNED;m->boundary=ML_NONE;m->boundary_pc=0;
    m->operations=m->calls=m->iterations=m->slots_examined=0;
    memset(&m->result,0,sizeof m->result);memset(&m->return_target,0,sizeof m->return_target);memset(&m->last_request,0,sizeof m->last_request);
}
void ml_init(ml_model *m,ml_profile profile,const ml_backend *backend){
    memset(m,0,sizeof *m);m->profile=profile;if(backend)m->backend=*backend;m->budget=4096;
}
ri_flow ml_initialize_9250(ml_model *m){
    static const uint32_t pc[]={0x9254,0x9258,0x925c,0x9260,0x9264,0x9268,0x926a,0x926e,0x9270,0x9274,0x9278,0x927c,0x9280,0x9284};
    static const uint32_t dst[]={0x18834,0x9a42,0x1973c,0x9f4c,0x131c2,0x8e88,0x9b4e,0x9958,0x9f12,0x12d92,0x14c8a,0x154a6,0x17040,0x173a2};
    unsigned i;if(!admit(m,0x9250))return m->flow;
    m->r.sp=add(m->r.sp,UINT32_C(0xfffffff0));
    if(!store(m,0x9252,add(m->r.sp,12),m->r.ra))return m->flow;
    for(i=0;i<14;i++)if(!call(m,pc[i],word(dst[i]),i==13?0x9288:pc[i+1],0))return m->flow;
    if(!load(m,0x9288,add(m->r.sp,12),&m->r.ra,0))return m->flow;
    m->r.sp=add(m->r.sp,16);
    (void)call(m,0x928c,word(0x17bf6),0,1);m->result=m->r.a[0];return m->flow;
}
ri_flow ml_loop_8180(ml_model *m){
    if(!admit(m,0x8180))return m->flow;
    m->r.sp=add(m->r.sp,UINT32_C(0xfffffff0));
    if(!store(m,0x8182,add(m->r.sp,8),m->r.s[0]))return m->flow;
    m->r.s[0]=word(0xb000);
    if(!store(m,0x8186,add(m->r.sp,4),m->r.s[1]))return m->flow;
    if(!store(m,0x8188,m->r.sp,m->r.s[2]))return m->flow;
    if(!store(m,0x818a,add(m->r.sp,12),m->r.ra))return m->flow;
    m->r.s[2]=word(0x20000000);m->r.s[1]=word(0x40003000);m->r.s[0]=word(0xaaaa);
    for(;;){
        if(!load(m,0x8198,m->r.s[2],&m->r.a[5],0))return m->flow;
        if(!call(m,0x819c,m->r.a[5],0x819e,0))return m->flow;
        if(!call(m,0x819e,word(0x17002),0x81a2,0))return m->flow;
        if(!call(m,0x81a2,word(0x12c58),0x81a6,0))return m->flow;
        if(!store(m,0x81a6,m->r.s[1],m->r.s[0]))return m->flow;
        ++m->iterations; /* Permanent source81A8 backedge; no epilogue. */
    }
}
ri_flow ml_main_suffix_9012(ml_model *m){
    if(!admit(m,0x9012))return m->flow;
    if(!load(m,0x9012,add(m->r.sp,12),&m->r.ra,0))return m->flow;
    m->r.a[0]=word(0);m->r.sp=add(m->r.sp,16);(void)return_effect(m,0x9018);return m->flow;
}
ri_flow ml_main_9008(ml_model *m){
    if(!admit(m,0x9008))return m->flow;
    m->r.sp=add(m->r.sp,UINT32_C(0xfffffff0));
    if(!store(m,0x900a,add(m->r.sp,12),m->r.ra))return m->flow;
    m->r.ra=word(0x900e);
    if(ml_initialize_9250(m)!=RI_RETURNED)return m->flow;
    if(!route(m,m->return_target,word(0x900e),0x900c))return m->flow;
    m->r.ra=word(0x9012);
    /* A host limit/nonreturn is terminal. Never call the suffix as cleanup. */
    return ml_loop_8180(m);
}
ri_flow ml_dispatch_901a(ml_model *m){
    int same;unsigned index;ri_value record;
    if(!admit(m,0x901a))return m->flow;
    m->r.sp=add(m->r.sp,UINT32_C(0xfffffff0));
    if(!store(m,0x901c,add(m->r.sp,8),m->r.s[0]))return m->flow;
    if(!store(m,0x901e,add(m->r.sp,12),m->r.ra))return m->flow;
    if(!store(m,0x9020,add(m->r.sp,4),m->r.s[1]))return m->flow;
    m->r.s[0]=word(0);m->r.a[4]=word(15);
    for(index=0;index<15;index++){
        ++m->slots_examined;m->r.a[5]=bit_from_events(m->r.a[1],index);
        same=equal(m->r.a[5],word(0));
        if(same<0)return stop(m,ML_UNKNOWN_CONDITION,0x902c);
        if(!same){
            m->r.a[5]=word(12);m->r.a[4]=word(index*12);
            m->r.a[5]=word(0x2000be08);m->r.s[1]=m->r.a[1];
            m->r.a[5]=add(m->r.a[5],index*12);record=m->r.a[5];
            if(!load(m,0x9040,add(record,4),&m->r.a[3],0))return m->flow;
            same=equal(m->r.a[3],word(0));
            if(same<0)return stop(m,ML_UNKNOWN_CONDITION,0x9042);
            if(!same){
                if(!load(m,0x9044,record,&m->r.a[4],1))return m->flow;
                if(!load(m,0x9048,add(record,8),&m->r.a[0],0))return m->flow;
                m->r.a[4]=and_mask(m->r.a[4],255);same=equal(m->r.a[4],word(0));
                if(same<0)return stop(m,ML_UNKNOWN_CONDITION,0x904e);
                if(same){
                    if(!store(m,0x9050,add(record,4),word(0)))return m->flow;
                    if(!store(m,0x9054,add(record,8),word(0)))return m->flow;
                }
                if(!call(m,0x9058,m->r.a[3],0x905a,0))return m->flow;
            }
            m->r.a[0]=and_mask(xor_value(shifted_one(m->r.s[0]),m->r.s[1]),UINT32_C(0xffff));
            break;
        }
        m->r.s[0]=add(m->r.s[0],1);
    }
    if(index==15)m->r.a[0]=word(0);
    if(!load(m,0x9066,add(m->r.sp,12),&m->r.ra,0))return m->flow;
    if(!load(m,0x9068,add(m->r.sp,8),&m->r.s[0],0))return m->flow;
    if(!load(m,0x906a,add(m->r.sp,4),&m->r.s[1],0))return m->flow;
    m->r.sp=add(m->r.sp,16);(void)return_effect(m,0x906e);return m->flow;
}
ri_flow ml_main_from_resident(ml_model *m,const ri_model *resident){
    if(!admit(m,0x9008))return m->flow;
    if(!resident||resident->profile!=RI_DEC2023_133D3705||resident->flow!=RI_TRANSFER||resident->boundary!=RI_MRET_BOUNDARY||equal(resident->return_target,word(0x9008))!=1)return stop(m,ML_BINDING,0x9008);
    m->r.sp=resident->sp;m->r.gp=resident->gp;m->r.ra=resident->ra;
    m->r.a[0]=resident->a0;m->r.a[1]=resident->a1;m->r.a[2]=resident->a2;m->r.a[4]=resident->a4;m->r.a[5]=resident->a5;
    return ml_main_9008(m);
}
