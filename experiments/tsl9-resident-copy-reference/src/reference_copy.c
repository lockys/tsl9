#include "reference_copy.h"
#include <string.h>
static bc_value word(uint32_t v){bc_value x;x.value=v;x.known=UINT32_MAX;return x;}
static bc_value target(bc_value v){v.value&=~UINT32_C(1);v.known|=1;return v;}
static int equal(bc_value a,bc_value b){
    uint32_t known=a.known&b.known;
    if((a.value^b.value)&known)return 0;return known==UINT32_MAX?1:-1;
}
/* Bit knowledge for numeric u32 addition, without turning addresses into host
 * pointers or substituting zeros for unknown bits. Unsigned wrap is preserved. */
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
static bc_flow stop(rp_model *m,rp_boundary why,uint32_t pc){m->flow=BC_HALT;m->boundary=why;m->boundary_pc=pc;return m->flow;}
static rp_request request(rp_model *m,rp_kind kind,uint32_t pc){
    rp_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;q.index=m->index;return q;
}
static int invoke(rp_model *m,const rp_request *q,bc_value *out){
    bc_value result={0,0};bc_flow flow;m->last_request=*q;
    if(m->operations>=m->budget){(void)stop(m,RP_BUDGET,q->pc);return 0;}++m->operations;
    if(!m->backend.effect){(void)stop(m,RP_PROVIDER_MISSING,q->pc);return 0;}
    flow=m->backend.effect(m->backend.context,q,&result);
    if(flow==BC_TRANSFER){m->flow=flow;m->boundary_pc=q->pc;return 0;}
    if(flow!=BC_RETURNED){(void)stop(m,RP_PROVIDER_STOP,q->pc);return 0;}
    if(out)*out=result;return 1;
}
static int condition(rp_model *m,bc_value a,uint32_t b,uint32_t pc){
    int same=equal(a,word(b));if(same<0)(void)stop(m,RP_CONDITION_UNKNOWN,pc);return same;
}
static void restore_and_return(rp_model *m){
    rp_request q=request(m,RP_WRITE32,0x2000034e);q.address=word(0x4002420c);q.data=m->saved_mmio;
    if(!invoke(m,&q,0))return;
    q=request(m,RP_RETURN,0x20000352);q.raw_target=m->ra;q.target=target(m->ra);m->return_target=q.target;
    (void)invoke(m,&q,0);
}
void rp_new_activation(rp_model *m){
    m->flow=BC_RETURNED;m->boundary=RP_NONE;m->boundary_pc=0;
    m->index=m->index_set=m->operations=m->stores_returned=0;
    m->saved_mmio.value=m->saved_mmio.known=m->return_target.value=m->return_target.known=0;
    memset(&m->last_request,0,sizeof m->last_request);
}
void rp_init(rp_model *m,rp_profile profile,const rp_backend *b){
    memset(m,0,sizeof *m);m->profile=profile;if(b)m->backend=*b;m->budget=4096;
}
bc_flow rp_copy(rp_model *m,bc_value dst,bc_value src,bc_value n,bc_value ra){
    rp_request q;bc_value byte,destination;int same;
    if(m->flow!=BC_RETURNED)return m->flow;rp_new_activation(m);
    if(m->profile!=RP_DEC2023_133D3705)return stop(m,RP_BINDING,0x20000332);
    m->destination=dst;m->source=src;m->length=n;m->ra=ra;m->result=dst;
    q=request(m,RP_READ32,0x20000336);q.address=word(0x4002420c);
    if(!invoke(m,&q,&m->saved_mmio))return m->flow;
    q=request(m,RP_WRITE32,0x2000033a);q.address=word(0x4002420c);q.data=word(0);
    if(!invoke(m,&q,0))return m->flow;
    q=request(m,RP_FENCE_I,0x2000033e);if(!invoke(m,&q,0))return m->flow;
    /* Source guards come AFTER MMIO clear/FENCE, even for null/n==0. */
    same=condition(m,dst,0,0x20000342);if(same<0)return m->flow;if(same){restore_and_return(m);return m->flow;}
    same=condition(m,src,0,0x20000344);if(same<0)return m->flow;if(same){restore_and_return(m);return m->flow;}
    m->index=0;m->index_set=1;
    same=condition(m,n,0,0x20000348);if(same<0)return m->flow;if(same){restore_and_return(m);return m->flow;}
    for(;;){
        q=request(m,RP_READ8,0x20000358);q.address=add(src,m->index);
        if(!invoke(m,&q,&byte))return m->flow;
        byte.value&=255;byte.known=(byte.known&255)|UINT32_C(0xffffff00); /* LBU. */
        destination=add(dst,m->index); /* ADD before increment, SB after it. */
        ++m->index;
        q=request(m,RP_WRITE8,0x20000362);q.address=destination;q.data=byte;
        if(!invoke(m,&q,0))return m->flow;++m->stores_returned;
        same=condition(m,n,m->index,0x20000366);if(same<0)return m->flow;
        if(same){restore_and_return(m);return m->flow;}
    }
}
static int bound_target(bc_value raw,bc_value normalized){
    return equal(normalized,word(0x20000332))==1&&equal(target(raw),normalized)==1;
}
bc_flow rp_uid_copy(rp_model *m,ub_model *caller,const ub_request *q,bc_value *out){
    bc_flow flow;
    if(!m||!caller||!q||!out)return BC_HALT;
    if(m->flow!=BC_RETURNED)return m->flow;
    if(q->kind!=UB_COPY||q->argc!=3||!bound_target(q->raw_target,q->target)||
       !((q->pc==0x1c66&&q->tail==0)||(q->pc==0x1c80&&q->tail==1))||
       q->continuation.known!=target(caller->ra).known||
       ((q->continuation.value^target(caller->ra).value)&q->continuation.known))return stop(m,RP_BINDING,q->pc);
    flow=rp_copy(m,q->args[0],q->args[1],q->args[2],caller->ra);
    if(flow==BC_RETURNED)*out=m->result;return flow;
}
bc_flow rp_boot_copy(rp_model *m,const bc_request *q,bc_value *out){
    bc_flow flow;
    if(!m||!q||!out)return BC_HALT;if(m->flow!=BC_RETURNED)return m->flow;
    if(q->kind!=BC_INDIRECT_COPY||q->pc!=0x225e||q->argc!=3||!bound_target(q->raw_target,q->target))return stop(m,RP_BINDING,q->pc);
    flow=rp_copy(m,q->args[0],q->args[1],q->args[2],word(0x2260));
    if(flow==BC_RETURNED)*out=m->result;return flow;
}
