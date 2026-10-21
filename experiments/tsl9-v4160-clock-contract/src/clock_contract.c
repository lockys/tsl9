#include "clock_contract.h"
#include <stddef.h>
/* Clear only our own state/request storage. Volatile byte stores prevent a
 * freestanding build from silently acquiring a libc memset dependency. */
static void clear(void *ptr,size_t n){volatile unsigned char *p=(volatile unsigned char *)ptr;while(n--)*p++=0;}
void vc_init(vc_model *m,const vc_backend *b){clear(m,sizeof(*m));if(b)m->backend=*b;m->max_operations=100000;}
static int stop(vc_model *m,vc_boundary b,uint32_t pc){m->boundary=b;m->boundary_pc=pc;m->flow=b==VC_BUDGET?VC_OBSERVATION_LIMIT:VC_HALT;return 0;}
static int invoke(vc_model *m,const vc_request *q,vc_word *out){
    vc_word result;vc_flow flow;clear(&result,sizeof(result));
    if(m->operations>=m->max_operations)return stop(m,VC_BUDGET,q->pc);
    m->operations++;m->last_request=*q;
    if(!m->backend.invoke)return stop(m,VC_BACKEND_UNKNOWN,q->pc);
    flow=m->backend.invoke(m->backend.context,q,&result);
    if(flow==VC_TRANSFER){m->flow=flow;m->boundary=VC_BACKEND_UNKNOWN;m->boundary_pc=q->pc;return 0;}
    if(flow!=VC_RETURNED)return stop(m,VC_BACKEND_UNKNOWN,q->pc);
    if(out)*out=result;
    return 1;
}
static int get(vc_model *m,uint32_t pc,uint32_t address,vc_word *out){vc_request q;clear(&q,sizeof(q));q.kind=VC_READ32;q.pc=pc;q.address=address;return invoke(m,&q,out);}
static int put(vc_model *m,uint32_t pc,uint32_t address,vc_word word){vc_request q;clear(&q,sizeof(q));q.kind=VC_WRITE32;q.pc=pc;q.address=address;q.value=word.value;q.known=word.known;return invoke(m,&q,NULL);}
static vc_word constant(uint32_t value){vc_word w;w.value=value;w.known=UINT32_MAX;return w;}
static vc_word band(vc_word a,uint32_t mask){a.value&=mask;a.known|=~mask;return a;}
static vc_word bor(vc_word a,uint32_t mask){a.value|=mask;a.known|=mask;return a;}
static vc_word increment(vc_word a){
    vc_word out;unsigned i,b,c,carry=2;out.value=a.value+1u;out.known=0;
    /* Possible carry sets preserve partial knowledge without trusting an
     * arbitrary representative value in unknown input bits. */
    for(i=0;i<32;i++){
        uint32_t bit=UINT32_C(1)<<i;
        unsigned bits=(a.known&bit)?(1u<<((a.value>>i)&1u)):3u,values=0,next=0;
        for(b=0;b<2;b++)if(bits&(1u<<b))for(c=0;c<2;c++)if(carry&(1u<<c)){
            unsigned sum=b+c;values|=1u<<(sum&1u);next|=1u<<(sum>>1);
        }
        if(values==1 || values==2)out.known|=bit;
        carry=next;
    }
    return out;
}
static int equal(vc_model *m,vc_word a,uint32_t value,uint32_t pc){
    if((a.value^value)&a.known)return 0;
    if(a.known==UINT32_MAX)return 1;
    stop(m,VC_BRANCH_UNKNOWN,pc);return -1;
}
static int nonzero(vc_model *m,vc_word a,uint32_t pc){
    if(a.value&a.known)return 1;
    if(a.known==UINT32_MAX)return 0;
    stop(m,VC_BRANCH_UNKNOWN,pc);return -1;
}
static int bit_set(vc_model *m,vc_word a,uint32_t mask,uint32_t pc){
    if(!(a.known&mask)){stop(m,VC_BRANCH_UNKNOWN,pc);return -1;}
    return (a.value&mask)!=0;
}
static int modify(vc_model *m,uint32_t read_pc,uint32_t write_pc,uint32_t address,uint32_t keep,uint32_t set){
    vc_word a;if(!get(m,read_pc,address,&a))return 0;
    return put(m,write_pc,address,bor(band(a,keep),set));
}
vc_flow vc_clock(vc_model *m,uint32_t sp){
    const uint32_t reg=UINT32_C(0x40021000);uint32_t sp8=sp-8u,sp12=sp-4u;
    vc_word a;int test;
    m->flow=VC_RETURNED;m->boundary=VC_NONE;
    m->operations=m->boundary_pc=m->hse_samples=m->pll_samples=m->switch_samples=0;
    m->entry_sp=sp;m->frame_sp=sp-16u;m->frame_entered=m->frame_restored=0;
    clear(&m->last_request,sizeof(m->last_request));
    if(!get(m,0x1874e,reg,&a))return m->flow;
    m->frame_entered=1; /* Source SP decrement18754 follows this first read. */
    if(!put(m,0x1875a,reg,bor(a,1)) ||
       !modify(m,0x1875c,0x18764,reg+4,0xf8ff0000,0) ||
       !modify(m,0x18766,0x18770,reg,0xfef6ffff,0) ||
       !modify(m,0x18772,0x1877c,reg,0xfffbffff,0) ||
       !modify(m,0x1877e,0x18788,reg+4,0xff80ffff,0) ||
       !put(m,0x1878e,reg+8,constant(0x009f0000)) ||
       !put(m,0x18790,sp8,constant(0)) || !put(m,0x18792,sp12,constant(0)) ||
       !modify(m,0x18794,0x1879a,reg,UINT32_MAX,0x10000))return m->flow;
    for(;;){
        if(!get(m,0x187a2,reg,&a))return m->flow;
        m->hse_samples++;
        if(!put(m,0x187a6,sp12,band(a,0x20000)) || !get(m,0x187a8,sp8,&a) ||
           !put(m,0x187ac,sp8,increment(a)) || !get(m,0x187ae,sp12,&a))return m->flow;
        test=nonzero(m,a,0x187b0);if(test<0)return m->flow;if(test)break;
        if(!get(m,0x187b2,sp8,&a))return m->flow;
        test=equal(m,a,0x1000,0x187b4);if(test<0)return m->flow;if(test)break;
    }
    if(!get(m,0x187bc,reg,&a))return m->flow;
    test=bit_set(m,a,0x20000,0x187c2);if(test<0)return m->flow;
    if(!put(m,test?0x187c8:0x18830,sp12,constant(test?1u:0u)) || !get(m,0x187ca,sp12,&a))return m->flow;
    test=equal(m,a,1,0x187ce);if(test<0)return m->flow;
    if(test){
        /* Original same-value writes are observable transactions too. */
        if(!modify(m,0x187d6,0x187de,reg+4,UINT32_MAX,0) ||
           !modify(m,0x187e0,0x187e2,reg+4,UINT32_MAX,0) ||
           !modify(m,0x187e4,0x187ea,reg+4,UINT32_MAX,0x400) ||
           !modify(m,0x187ec,0x187f0,reg+4,0xffc0ffff,0) ||
           !modify(m,0x187f2,0x187fa,reg+4,UINT32_MAX,0x00290000) ||
           !modify(m,0x187fc,0x18804,reg,UINT32_MAX,0x01000000))return m->flow;
        for(;;){
            if(!get(m,0x18806,reg,&a))return m->flow;
            m->pll_samples++;test=bit_set(m,a,0x02000000,0x1880c);if(test<0)return m->flow;if(test)break;
        }
        if(!modify(m,0x18810,0x18818,reg+4,0xfffffffc,0) ||
           !modify(m,0x1881a,0x18820,reg+4,UINT32_MAX,2))return m->flow;
        for(;;){
            if(!get(m,0x18824,reg+4,&a))return m->flow;
            m->switch_samples++;test=equal(m,band(a,12),8,0x18828);if(test<0)return m->flow;if(test)break;
        }
    }
    m->frame_restored=1; /* Source1882C adds16, then1882E RET. */
    return m->flow;
}
