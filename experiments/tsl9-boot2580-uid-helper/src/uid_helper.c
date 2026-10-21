#include "uid_helper.h"
#include <string.h>
static bc_value word(uint32_t v){bc_value r;r.value=v;r.known=UINT32_MAX;return r;}
static bc_value add(bc_value a,uint32_t b){
    bc_value r={0,0};unsigned bit,carry=1;
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
static bc_value target(bc_value raw){raw.value&=~UINT32_C(1);raw.known|=1;return raw;}
static int equal(bc_value a,bc_value b,uint32_t mask){
    uint32_t common=a.known&b.known&mask;
    if((a.value^b.value)&common)return 0;return common==mask?1:-1;
}
static int stop(ub_model *m,ub_boundary why,uint32_t pc){m->flow=BC_HALT;m->boundary=why;m->boundary_pc=pc;return 0;}
static ub_request request(ub_kind kind,uint32_t pc){ub_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;return q;}
static int invoke(ub_model *m,const ub_request *q,bc_value *out){
    bc_flow flow;bc_value result={0,0};m->last_request=*q;
    if(m->operations>=m->budget)return stop(m,UB_BUDGET,q->pc);++m->operations;
    if(q->kind==UB_COPY){
        if(!m->backend.copy)return stop(m,UB_PROVIDER_MISSING,q->pc);
        flow=m->backend.copy(m->backend.context,m,q,&result);
    }else{
        if(!m->backend.effect)return stop(m,UB_PROVIDER_MISSING,q->pc);
        flow=m->backend.effect(m->backend.context,q,&result);
    }
    if(flow==BC_TRANSFER){m->flow=flow;m->boundary_pc=q->pc;return 0;}
    if(flow!=BC_RETURNED)return stop(m,UB_PROVIDER_STOP,q->pc);
    if(out)*out=result;return 1;
}
static int read_value(ub_model *m,uint32_t pc,bc_value address,unsigned width,bc_value *out){
    ub_request q=request(width==1?UB_READ8:UB_READ32,pc);q.address=address;
    if(!invoke(m,&q,out))return 0;if(width==1){out->value&=255;out->known&=255;}return 1;
}
static int save(ub_model *m,uint32_t pc,uint32_t offset,bc_value value){
    ub_request q=request(UB_WRITE32,pc);q.address=add(m->sp,offset);q.data=value;return invoke(m,&q,0);
}
static int load(ub_model *m,uint32_t pc,uint32_t offset,bc_value *out){return read_value(m,pc,add(m->sp,offset),4,out);}
static int call_copy(ub_model *m,uint32_t pc,bc_value slot,bc_value raw,
                      bc_value dst,bc_value src,uint32_t n,unsigned tail){
    ub_request q=request(UB_COPY,pc);bc_value result;
    q.argc=3;q.tail=tail;q.slot=slot;q.raw_target=raw;q.target=target(raw);
    q.args[0]=dst;q.args[1]=src;q.args[2]=word(n);
    if(!tail)m->ra=word(0x1c68);
    q.continuation=target(m->ra);++m->copy_attempts;
    if(!invoke(m,&q,&result))return 0;
    m->return_target=q.continuation;
    if(tail)m->result=result;return 1;
}
static int return_control(ub_model *m,uint32_t pc){
    ub_request q=request(UB_RETURN,pc);q.raw_target=m->ra;q.target=target(m->ra);
    q.continuation=q.target;m->return_target=q.target;return invoke(m,&q,0);
}
static int expected_route(ub_model *m,uint32_t pc,uint32_t expected){
    int same=equal(m->return_target,word(expected),UINT32_MAX);
    if(same<0)return stop(m,UB_UNKNOWN_CONTROL,pc);
    if(!same){m->flow=BC_TRANSFER;m->boundary=UB_CONTROL_TRANSFER;m->boundary_pc=pc;return 0;}
    return 1;
}
/* Fixed data effects of the selected1C4A body, not an opcode dispatcher. */
static int build(ub_model *m,bc_value output){
    bc_value first_slot,second_slot,slot_address,source,destination;
    m->sp=add(m->sp,UINT32_C(0xfffffff0));
    if(!save(m,0x1c4c,4,m->s1))return 0;m->s1=word(0x40000);
    slot_address=add(m->s1,76);
    if(!read_value(m,0x1c52,slot_address,4,&first_slot)||!save(m,0x1c54,8,m->s0))return 0;
    m->s0=word(0x1ffff000);
    if(!save(m,0x1c5a,0,m->s2)||!save(m,0x1c5c,12,m->ra))return 0;
    source=add(m->s0,2028);m->s2=output;
    if(!call_copy(m,0x1c66,slot_address,first_slot,output,source,8,0))return 0;
    source=add(m->s0,2024); /* BEFORE restoring S0. */
    if(!load(m,0x1c6c,8,&m->s0))return 0;
    slot_address=add(m->s1,76); /* BEFORE restoring S1; fresh slot value. */
    if(!read_value(m,0x1c6e,slot_address,4,&second_slot)||
       !load(m,0x1c72,12,&m->ra)||!load(m,0x1c74,4,&m->s1))return 0;
    destination=add(m->s2,8); /* BEFORE restoring S2. */
    if(!load(m,0x1c7a,0,&m->s2))return 0;
    m->sp=add(m->sp,16);
    return call_copy(m,0x1c80,slot_address,second_slot,destination,source,6,1);
}
void ub_new_activation(ub_model *m){
    m->flow=BC_RETURNED;m->boundary=UB_NONE;m->boundary_pc=0;
    m->operations=m->compared=m->copy_attempts=0;
    m->result.value=m->result.known=m->return_target.value=m->return_target.known=0;
    memset(&m->last_request,0,sizeof m->last_request);
}
void ub_init(ub_model *m,const ub_backend *backend){memset(m,0,sizeof *m);if(backend)m->backend=*backend;m->budget=1024;}
bc_flow ub_build(ub_model *m,bc_value output){
    if(m->flow!=BC_RETURNED)return m->flow;ub_new_activation(m);(void)build(m,output);return m->flow;
}
bc_flow ub_compare(ub_model *m,bc_value incoming,bc_value length){
    bc_value left,right,output;unsigned i;int same;
    if(m->flow!=BC_RETURNED)return m->flow;ub_new_activation(m);
    same=equal(length,word(14),UINT32_MAX);
    if(same<0){(void)stop(m,UB_UNKNOWN_CONDITION,0x1c84);return m->flow;}
    if(!same){m->result=word(1);(void)return_control(m,0x1cc2);return m->flow;}
    m->sp=add(m->sp,UINT32_C(0xffffffe0));
    if(!save(m,0x1c8a,24,m->s0))return m->flow;m->s0=incoming;output=m->sp;
    if(!save(m,0x1c90,28,m->ra))return m->flow;m->ra=word(0x1c94);
    if(!build(m,output)||!expected_route(m,0x1c80,0x1c94))return m->flow;
    same=1;
    for(i=0;i<14;i++){
        if(!read_value(m,0x1c9c,add(m->s0,i),1,&left)||
           !read_value(m,0x1ca4,add(m->sp,i),1,&right))return m->flow;
        ++m->compared;same=equal(left,right,255);
        if(same<0){(void)stop(m,UB_UNKNOWN_CONDITION,0x1ca8);return m->flow;}
        if(!same)break;
    }
    m->result=word(same?0u:1u);
    if(!load(m,0x1cb4,28,&m->ra)||!load(m,0x1cb6,24,&m->s0))return m->flow;
    m->sp=add(m->sp,32);(void)return_control(m,0x1cba);return m->flow;
}
bc_flow ub_identity_bridge(bc_model *caller,const bc_request *q,ub_model *m,bc_value *out){
    bc_flow flow;
    if(!caller||!q||!m||!out||q->kind!=BC_IDENTITY||q->argc!=2||
       q->target.known!=UINT32_MAX||q->target.value!=0x1c82||
       (q->pc!=0x22ac&&q->pc!=0x22da))return BC_HALT;
    if(m->flow!=BC_RETURNED)return m->flow;
    m->sp=caller->body_sp;m->ra=word(q->pc+2u);
    flow=ub_compare(m,q->args[0],q->args[1]);caller->body_sp=m->sp;
    if(flow!=BC_RETURNED)return flow;
    if(!expected_route(m,m->last_request.pc,q->pc+2u))return m->flow;
    *out=m->result;return BC_RETURNED;
}
