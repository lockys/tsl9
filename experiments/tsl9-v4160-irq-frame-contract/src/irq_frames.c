#include "irq_frames.h"
#include <string.h>
static const unsigned frame_regs[29]={1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31};
static iq_scalar known(uint32_t value){iq_scalar s={value,UINT32_MAX};return s;}
static iq_scalar plus(iq_scalar s,uint32_t delta){
    s.value+=delta;if(s.known!=UINT32_MAX)s.known=0;return s;
}
void iq_init(iq_model *m,const iq_backend *backend){
    memset(m,0,sizeof(*m));if(backend)m->backend=*backend;
    m->gpr[0]=known(0);m->max_operations=96;
}
static void begin(iq_model *m){
    m->flow=IQ_RETURNED;m->boundary=IQ_NONE;m->boundary_pc=0;
    m->operations=m->saved_words=m->restored_words=0;memset(&m->last_request,0,sizeof(m->last_request));
}
static int stop(iq_model *m,iq_flow flow,iq_boundary boundary,uint32_t pc){
    m->flow=flow;m->boundary=boundary;m->boundary_pc=pc;return 0;
}
static iq_request request(iq_kind kind,uint32_t pc){iq_request q;memset(&q,0,sizeof(q));q.kind=kind;q.pc=pc;return q;}
static int invoke(iq_model *m,const iq_request *q,iq_scalar *out){
    iq_scalar result={0,0};iq_flow flow;
    if(m->operations>=m->max_operations)return stop(m,IQ_OBSERVATION_LIMIT,IQ_BUDGET,q->pc);
    m->operations++;m->last_request=*q;
    if(q->kind==IQ_CALLBACK){
        if(!m->backend.callback)return stop(m,IQ_HALT,IQ_PROVIDER_UNKNOWN,q->pc);
        flow=m->backend.callback(m->backend.context,m,q);
    }else{
        if(!m->backend.effect)return stop(m,IQ_HALT,IQ_PROVIDER_UNKNOWN,q->pc);
        flow=m->backend.effect(m->backend.context,q,&result);
    }
    if(flow==IQ_TRANSFER)return stop(m,flow,q->kind==IQ_MRET?IQ_MRET_BOUNDARY:
        (q->kind==IQ_CALLBACK?IQ_CALLBACK_BOUNDARY:IQ_PROVIDER_TRANSFER),q->pc);
    if(flow!=IQ_RETURNED)return stop(m,flow==IQ_OBSERVATION_LIMIT?flow:IQ_HALT,
        flow==IQ_OBSERVATION_LIMIT?IQ_BUDGET:IQ_PROVIDER_UNKNOWN,q->pc);
    if(out)*out=result;return 1;
}
static int access(iq_model *m,iq_kind kind,uint32_t pc,iq_scalar address,iq_scalar value,iq_scalar *out){
    iq_request q=request(kind,pc);q.value=value;
    if(address.known!=UINT32_MAX)return stop(m,IQ_HALT,IQ_UNKNOWN_ADDRESS,pc);
    q.address=address.value;return invoke(m,&q,out);
}
static int csr(iq_model *m,iq_kind kind,uint32_t pc,uint32_t number,iq_scalar value){
    iq_request q=request(kind,pc);q.csr=number;q.value=value;return invoke(m,&q,0);
}
static int restore(iq_model *m,uint32_t first_pc){
    unsigned i;for(i=0;i<29;i++){
        iq_scalar word;
        if(!access(m,IQ_READ32,first_pc+2*i,plus(m->gpr[2],4+4*i),known(0),&word))return 0;
        m->gpr[frame_regs[i]]=word;m->restored_words++;
    }
    return 1;
}
static iq_flow mret_boundary(iq_model *m,uint32_t pc){
    iq_request q=request(IQ_MRET,pc);q.target=m->mepc;
    if(!invoke(m,&q,0))return m->flow;
    /* The own model ends at this obligation. No privilege/IRQ/hardware return
     * is performed, and a normal synthetic acknowledgment is not a CPU RET. */
    stop(m,IQ_TRANSFER,IQ_MRET_BOUNDARY,pc);return m->flow;
}
iq_flow iq_restore_8448(iq_model *m){
    iq_scalar word;begin(m);
    m->gpr[11]=known(32);
    if(!csr(m,IQ_CSR_SET,0x844c,0x804,m->gpr[11]))return m->flow;
    m->csr804.value|=32;m->csr804.known|=32;
    if(!access(m,IQ_READ32,0x8450,m->gpr[2],known(0),&word))return m->flow;
    m->gpr[11]=word;
    if(!csr(m,IQ_CSR_WRITE,0x8452,0x341,m->gpr[11]))return m->flow;
    m->mepc=m->gpr[11];
    if(!restore(m,0x8456))return m->flow;
    m->gpr[2]=plus(m->gpr[2],128);return mret_boundary(m,0x8492);
}
iq_flow iq_irq_8498(iq_model *m){
    unsigned i;iq_scalar target;iq_request q;begin(m);
    m->gpr[2]=plus(m->gpr[2],UINT32_C(0xffffff80));
    for(i=0;i<29;i++){
        if(!access(m,IQ_WRITE32,0x849a+2*i,plus(m->gpr[2],4+4*i),m->gpr[frame_regs[i]],0))return m->flow;
        m->saved_words++;
    }
    m->gpr[11]=plus(m->gpr[3],384);
    if(!access(m,IQ_READ32,0x84d8,m->gpr[11],known(0),&target))return m->flow;
    m->gpr[10]=target;
    q=request(IQ_CALLBACK,0x84da);q.target.value=target.value&~UINT32_C(1);q.target.known=target.known|1;
    if(q.target.known!=UINT32_MAX)return (iq_flow)(stop(m,IQ_HALT,IQ_UNKNOWN_TARGET,q.pc),m->flow);
    m->gpr[1]=known(0x84de);
    if(!invoke(m,&q,0))return m->flow;
    if(!restore(m,0x84de))return m->flow;
    m->gpr[2]=plus(m->gpr[2],128);return mret_boundary(m,0x851a);
}
