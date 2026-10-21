#include "resident_entry.h"
#include <string.h>
static ri_value word(uint32_t v){ri_value x;x.value=v;x.known=UINT32_MAX;return x;}
static ri_value target(ri_value v){v.value&=~UINT32_C(1);v.known|=1;return v;}
static ri_flow stop(ri_model *m,ri_boundary why,uint32_t pc){m->flow=RI_HALT;m->boundary=why;m->boundary_pc=pc;return m->flow;}
static ri_request request(ri_model *m,ri_kind kind,uint32_t pc){
    ri_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;q.stage=m->stage;return q;
}
static int invoke(ri_model *m,const ri_request *q,ri_value *out){
    ri_flow flow;ri_value v={0,0};int binding=q->kind==RI_BIND_COPY||q->kind==RI_BIND_ZERO;
    m->last_request=*q;
    if(m->operations>=m->budget){m->flow=RI_LIMIT;m->boundary=RI_BUDGET;m->boundary_pc=q->pc;return 0;}
    ++m->operations;
    if(binding){
        if(!m->backend.bind){(void)stop(m,RI_MISSING_PROVIDER,q->pc);return 0;}
        ++m->bindings;flow=m->backend.bind(m->backend.context,q);
    }else{
        if(!m->backend.effect){(void)stop(m,RI_MISSING_PROVIDER,q->pc);return 0;}
        flow=m->backend.effect(m->backend.context,q,&v);
    }
    if(flow==RI_TRANSFER){
        m->flow=flow;m->boundary=RI_PROVIDER_TRANSFER;m->boundary_pc=q->pc;
        if(out&&q->kind==RI_MRET)*out=v;return 0;
    }
    if(flow!=RI_RETURNED){
        (void)stop(m,RI_PROVIDER_STOP,q->pc);if(flow==RI_LIMIT)m->flow=RI_LIMIT;return 0;
    }
    if(out)*out=v;return 1;
}
static int read_word(ri_model *m,uint32_t pc,ri_value address,ri_value *out){
    ri_request q=request(m,RI_READ32,pc);q.address=address;return invoke(m,&q,out);
}
static int store_word(ri_model *m,uint32_t pc,ri_value address,ri_value value){
    ri_request q=request(m,RI_WRITE32,pc);q.address=address;q.data=value;return invoke(m,&q,0);
}
static int expected_return(ri_model *m,uint32_t pc,uint32_t expected){
    ri_value t=m->return_target;
    if((t.value^expected)&t.known){m->flow=RI_TRANSFER;m->boundary=RI_OTHER_RETURN;m->boundary_pc=pc;return 0;}
    if(t.known!=UINT32_MAX){(void)stop(m,RI_UNKNOWN_CONTROL,pc);return 0;}return 1;
}
static int observe_return(ri_model *m,uint32_t pc,uint32_t expected){
    ri_request q=request(m,RI_RETURN,pc);q.raw_target=m->ra;q.target=target(m->ra);m->return_target=q.target;
    return invoke(m,&q,0)&&expected_return(m,pc,expected);
}
/* Source-specific RAM helper18B. Its installation/unchanged identity is an
 * explicit binding premise, never inferred from target address alone. */
static int copy_words(ri_model *m,uint32_t pc,uint32_t continuation,uint32_t *completed){
    ri_request q=request(m,RI_BIND_COPY,pc);
    q.target=q.raw_target=word(0x20000010);q.argc=3;q.args[0]=m->a0;q.args[1]=m->a1;q.args[2]=m->a2;
    m->ra=word(continuation);
    if(!invoke(m,&q,0))return 0;
    while(m->a1.value<=m->a2.value){
        if(!read_word(m,0x20000016,m->a0,&m->a5))return 0;
        m->a1.value+=4;m->a0.value+=4; /* Both increments BEFORE SW. */
        if(!store_word(m,0x2000001c,word(m->a1.value-4u),m->a5))return 0;
        ++*completed;
    }
    return observe_return(m,0x20000014,continuation);
}
static int initialize(ri_model *m){
    ri_request q;m->stage=RI_GLOBALS;
    m->sp.value-=16;m->a4=word(0x20000000);
    if(!store_word(m,0x6de12,word(m->sp.value+12u),m->ra))return 0;
    m->a5=word(0x20000000);m->a4=word(0x200007d0);
    if(!store_word(m,0x6de1c,m->a5,m->a4))return 0;
    m->a4=word(0x2000251c);if(!store_word(m,0x6de26,word(m->a5.value+4u),m->a4))return 0;
    m->a4=word(0x20002e34);m->a2=word(0x20003000);m->a1=word(0x20000000);m->a0=word(0x40000);
    if(!store_word(m,0x6de3c,word(m->a5.value+8u),m->a4))return 0;
    m->a2=word(0x20002e70);m->a1=word(0x20000040);m->a0=word(0x402b0);m->stage=RI_COPY1;
    if(!copy_words(m,0x6de4e,0x6de52,&m->first_words))return 0;
    m->a2=word(0x20002ef8);m->a1=word(0x20002e70);m->a0=word(0x6eaa4);m->stage=RI_COPY2;
    if(!copy_words(m,0x6de6e,0x6de72,&m->second_words))return 0;
    m->stage=RI_EPILOGUE;
    if(!read_word(m,0x6de72,word(m->sp.value+12u),&m->ra))return 0;
    m->sp.value+=16;
    /* Tail jump does not assign RA. Source helper30B owns its fixed bounds. */
    q=request(m,RI_BIND_ZERO,0x6de7a);q.raw_target=q.target=word(0x20000022);
    if(!invoke(m,&q,0))return 0;
    m->stage=RI_ZERO;m->a5=word(0x20002ef8);m->a4=word(0x20003614);
    while(m->a5.value<=m->a4.value){
        if(!store_word(m,0x20000038,m->a5,word(0)))return 0;
        m->a5.value+=4;++m->zero_words;
    }
    return observe_return(m,0x20000036,0x6debe);
}
void ri_new_activation(ri_model *m){
    m->flow=RI_RETURNED;m->boundary=RI_NONE;m->boundary_pc=0;m->stage=RI_SEED;
    m->operations=m->seed_words=m->first_words=m->second_words=m->zero_words=m->bindings=0;
    m->return_target.value=m->return_target.known=0;memset(&m->last_request,0,sizeof m->last_request);
}
void ri_init(ri_model *m,ri_profile profile,const ri_backend *backend){
    memset(m,0,sizeof *m);m->profile=profile;if(backend)m->backend=*backend;m->budget=10000;
}
ri_flow ri_enter(ri_model *m){
    ri_request q;ri_value transfer={0,0};
    if(m->flow!=RI_RETURNED)return m->flow;ri_new_activation(m);
    if(m->profile!=RI_DEC2023_133D3705)return stop(m,RI_PROFILE,0x40000);
    m->gp=word(0x20004000);m->sp=word(0x20010000);
    m->a0=word(0x40280);m->a1=word(0x20000010);m->a2=word(0x20000040);
    while(m->a1.value<m->a2.value){
        if(!read_word(m,0x6deaa,m->a0,&m->t0))return m->flow;
        if(!store_word(m,0x6deae,m->a1,m->t0))return m->flow;
        m->a0.value+=4;m->a1.value+=4;++m->seed_words; /* AFTER SW. */
    }
    m->ra=word(0x6debe);
    if(!initialize(m))return m->flow;
    m->stage=RI_FINAL;q=request(m,RI_MRET,0x6debe);
    if(!invoke(m,&q,&transfer)){
        if(m->flow==RI_TRANSFER){m->return_target=transfer;m->boundary=RI_MRET_BOUNDARY;}
        return m->flow;
    }
    /* MRET has no source fallthrough or normal C return, even when its provider
     * acknowledges the declared transition using RETURNED. */
    m->return_target=transfer;m->flow=RI_TRANSFER;m->boundary=RI_MRET_BOUNDARY;m->boundary_pc=q.pc;
    return m->flow;
}
