#include "reset_contract.h"
#include <string.h>
void rc_init(rc_model *m,const rc_backend *b){memset(m,0,sizeof(*m));if(b)m->backend=*b;m->max_operations=10000;}
static int stop(rc_model *m,rc_boundary boundary,uint32_t pc){
    m->flow=boundary==RC_BUDGET?RC_OBSERVATION_LIMIT:RC_HALT;
    m->boundary=boundary;m->boundary_pc=pc;return 0;
}
static rc_request request(rc_kind kind,uint32_t pc){
    rc_request q;memset(&q,0,sizeof(q));q.kind=kind;q.pc=pc;return q;
}
static int invoke(rc_model *m,const rc_request *q,rc_scalar *out){
    rc_scalar result;rc_flow flow;memset(&result,0,sizeof(result));
    if(m->operations>=m->max_operations)return stop(m,RC_BUDGET,q->pc);
    m->operations++;m->last_request=*q;
    if(!m->backend.invoke)return stop(m,RC_PROVIDER_UNKNOWN,q->pc);
    flow=m->backend.invoke(m->backend.context,q,&result);
    if(flow==RC_TRANSFER){
        m->flow=RC_TRANSFER;m->boundary=q->kind==RC_HANDOFF?RC_ROM_BOUNDARY:RC_CALLEE_TRANSFER;
        m->boundary_pc=q->pc;return 0;
    }
    if(flow!=RC_RETURNED)return stop(m,RC_PROVIDER_UNKNOWN,q->pc);
    if(out)*out=result;
    return 1;
}
static int csr(rc_model *m,rc_kind kind,uint32_t pc,uint32_t number,uint32_t value){
    rc_request q=request(kind,pc);q.csr=number;q.value=value;q.known=UINT32_MAX;
    return invoke(m,&q,NULL);
}
rc_flow rc_reset(rc_model *m){
    uint32_t offset;rc_scalar word;rc_request q;
    m->flow=RC_RETURNED;m->boundary=RC_NO_BOUNDARY;
    m->operations=m->boundary_pc=m->copied_words=m->zero_words=m->handoff_target=0;
    memset(&m->last_request,0,sizeof(m->last_request));
    /* Initial numeric values decoded from the original own-anchor pairs.
     * They describe this prefix, not callee-preserved registers or real RAM. */
    m->initial_gp=UINT32_C(0x20004000);m->initial_sp=UINT32_C(0x20010000);
    for(offset=0;offset<128;offset+=4){
        q=request(RC_READ32,0x186ce);q.address=UINT32_C(0x1ab60)+offset;
        if(!invoke(m,&q,&word))return m->flow;
        q=request(RC_WRITE32,0x186d2);q.address=m->initial_gp+offset;
        q.value=word.value;q.known=word.known;
        if(!invoke(m,&q,NULL))return m->flow;
        m->copied_words++;
    }
    for(offset=128;offset<35160;offset+=4){
        q=request(RC_WRITE32,0x186ee);q.address=m->initial_gp+offset;
        q.value=0;q.known=UINT32_MAX;
        if(!invoke(m,&q,NULL))return m->flow;
        m->zero_words++;
    }
    if(!csr(m,RC_CSR_WRITE,0x186fa,0xbc0,31) ||
       !csr(m,RC_CSR_WRITE,0x18700,0x804,3) ||
       !csr(m,RC_CSR_SET,0x1870c,0x300,0x1888) ||
       !csr(m,RC_CSR_WRITE,0x1871c,0x305,0x803b))return m->flow;
    q=request(RC_CLOCK,0x18720);q.target=0x1874a;
    if(!invoke(m,&q,NULL))return m->flow;
    if(!csr(m,RC_CSR_WRITE,0x1872c,0x341,0x9008))return m->flow;
    q=request(RC_HANDOFF,0x18730);q.target=0x40000;m->handoff_target=q.target;
    if(!invoke(m,&q,NULL))return m->flow;
    /* No local fallthrough/return is invented after the original JAL x0.
     * This records a known source control boundary, not ROM acceptance. */
    m->flow=RC_TRANSFER;m->boundary=RC_ROM_BOUNDARY;m->boundary_pc=q.pc;
    return m->flow;
}
