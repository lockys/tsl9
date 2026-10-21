#include "system_clock_query.h"
#include <string.h>
static ri_value word(uint32_t n){ri_value v={n,UINT32_MAX};return v;}
static ri_value normalized(ri_value v){v.value&=~UINT32_C(1);v.known|=1;return v;}
static int equal(ri_value a,ri_value b){uint32_t known=a.known&b.known;if((a.value^b.value)&known)return 0;return known==UINT32_MAX?1:-1;}
static ri_value mask(ri_value a,uint32_t n){a.value&=n;a.known=(a.known&n)|~n;return a;}
/* Conservative bit knowledge for wrapping numeric addition. No host pointers. */
static ri_value add(ri_value a,ri_value b){
    ri_value r={0,0};unsigned bit,carry=1;
    for(bit=0;bit<32;bit++){
        unsigned values=0,next=0,x,y,c;
        unsigned xs=(a.known&(UINT32_C(1)<<bit))?(1u<<((a.value>>bit)&1u)):3u;
        unsigned ys=(b.known&(UINT32_C(1)<<bit))?(1u<<((b.value>>bit)&1u)):3u;
        for(x=0;x<2;x++)for(y=0;y<2;y++)for(c=0;c<2;c++)if((xs&(1u<<x))&&(ys&(1u<<y))&&(carry&(1u<<c))){
            unsigned sum=x+y+c;values|=1u<<(sum&1u);next|=1u<<(sum>>1);
        }
        if(values!=3){r.known|=UINT32_C(1)<<bit;if(values==2)r.value|=UINT32_C(1)<<bit;}carry=next;
    }return r;
}
static ri_value plus(ri_value a,uint32_t n){return add(a,word(n));}
static ri_value right(ri_value a,unsigned n){ri_value r;if(n==0)return a;r.value=a.value>>n;r.known=(a.known>>n)|(UINT32_MAX<<(32-n));return r;}
static ri_value left(ri_value a,unsigned n){ri_value r;if(n==0)return a;r.value=a.value<<n;r.known=(a.known<<n)|((UINT32_C(1)<<n)-1);return r;}
static ri_value variable_right(ri_value a,ri_value shift){
    uint32_t ones=UINT32_MAX,zeros=UINT32_MAX;unsigned n;ri_value v,r;
    for(n=0;n<32;n++)if(!((n^shift.value)&shift.known&31u)){
        v=right(a,n);ones&=v.value&v.known;zeros&=~v.value&v.known;
    }r.value=ones;r.known=ones|zeros;return r;
}
/* Only the selected source's multiplication-by-known-base/1000 operation.
 * Enumerate at most12 unknown bits; wider sets conservatively retain only the
 * low zeros guaranteed by the factor. Unknown bits are never substituted zero. */
static ri_value multiply(ri_value a,uint32_t factor){
    unsigned pos[32],count=0,i,n;uint32_t ones=UINT32_MAX,any=0;ri_value r={0,0};
    if(!factor)return word(0);
    for(i=0;i<32;i++)if(!(a.known&(UINT32_C(1)<<i)))pos[count++]=i;
    if(count>12){unsigned z=0;while(z<32&&!(factor&(UINT32_C(1)<<z)))++z;r.known=z==32?UINT32_MAX:(UINT32_C(1)<<z)-1;return r;}
    for(n=0;n<(1u<<count);n++){
        uint32_t v=a.value&a.known;
        for(i=0;i<count;i++)if(n&(1u<<i))v|=UINT32_C(1)<<pos[i];
        v*=factor;ones&=v;any|=v;
    }r.value=ones;r.known=ones|~any;return r;
}
/* Unsigned DIVU by8M. Quotient intervals contain at most537 values. Partial
 * inputs may widen the set; only bits common to all candidates become known. */
static ri_value divide_8m(ri_value a){
    uint32_t lo=(a.value&a.known)/8000000u,hi=((a.value&a.known)|~a.known)/8000000u;
    uint32_t q,ones=UINT32_MAX,any=0;ri_value r;
    for(q=lo;q<=hi;q++){ones&=q;any|=q;}r.value=ones;r.known=ones|~any;return r;
}
static ri_flow stop(sf_model *m,sf_boundary why,uint32_t pc){m->flow=RI_HALT;m->boundary=why;m->boundary_pc=pc;return m->flow;}
static int admit(sf_model *m,uint32_t pc){
    if(m->flow!=RI_RETURNED)return 0;if(m->profile!=SF_ID2966_0EE64183){(void)stop(m,SF_BINDING,pc);return 0;}return 1;
}
static sf_request request(sf_model *m,sf_kind kind,uint32_t pc){sf_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;q.registers=m->r;return q;}
static int effect(sf_model *m,sf_request *q,ri_value *out){
    ri_flow flow;ri_value v={0,0};m->last_request=*q;
    if(m->operations>=m->budget){m->flow=RI_LIMIT;m->boundary=SF_BUDGET;m->boundary_pc=q->pc;return 0;}++m->operations;
    if(!m->backend.effect){(void)stop(m,SF_MISSING_PROVIDER,q->pc);return 0;}
    flow=m->backend.effect(m->backend.context,m,q,&v);
    if(flow!=RI_RETURNED){m->flow=flow;m->boundary=flow==RI_TRANSFER?SF_PROVIDER_TRANSFER:SF_PROVIDER_STOP;m->boundary_pc=q->pc;return 0;}
    if(out)*out=v;return 1;
}
static int load(sf_model *m,uint32_t pc,ri_value address,ri_value *out,int byte){
    sf_request q=request(m,byte?SF_READ8:SF_READ32,pc);ri_value v;q.address=address;
    if(!effect(m,&q,&v))return 0;*out=byte?mask(v,255):v;return 1;
}
static int store(sf_model *m,uint32_t pc,ri_value address,ri_value data,sf_kind kind){
    sf_request q=request(m,kind,pc);q.address=address;q.data=kind==SF_WRITE8?mask(data,255):kind==SF_WRITE16?mask(data,65535):data;return effect(m,&q,0);
}
static int condition(sf_model *m,ri_value a,uint32_t b,uint32_t pc){int n=equal(a,word(b));if(n<0)(void)stop(m,SF_UNKNOWN_CONDITION,pc);return n;}
static void ret(sf_model *m,uint32_t pc){sf_request q=request(m,SF_RETURN,pc);q.raw_target=m->r.ra;q.target=normalized(m->r.ra);m->return_target=q.target;(void)effect(m,&q,0);}
void sf_new_activation(sf_model *m){m->flow=RI_RETURNED;m->boundary=SF_NONE;m->boundary_pc=m->operations=0;memset(&m->return_target,0,sizeof m->return_target);memset(&m->last_request,0,sizeof m->last_request);}
void sf_init(sf_model *m,sf_profile profile,const sf_backend *backend){memset(m,0,sizeof *m);m->profile=profile;if(backend)m->backend=*backend;m->budget=128;}
ri_flow sf_query_18834(sf_model *m){
    int same;uint32_t base=0;if(!admit(m,0x18834))return m->flow;
    m->r.a[4]=word(0x40021000);
    if(!load(m,0x18838,plus(m->r.a[4],4),&m->r.a[5],0))return m->flow;
    m->r.a[3]=word(4);m->r.a[5]=mask(m->r.a[5],12);same=condition(m,m->r.a[5],4,0x1883e);if(same<0)return m->flow;
    if(same)m->r.a[5]=word(32000000);
    else{
        m->r.a[3]=word(8);same=condition(m,m->r.a[5],8,0x18844);if(same<0)return m->flow;
        if(!same)m->r.a[5]=word(8000000);
        else{
            if(!load(m,0x18882,plus(m->r.a[4],4),&m->r.a[5],0))return m->flow;
            if(!load(m,0x18884,plus(m->r.a[4],4),&m->r.a[4],0))return m->flow;
            m->r.a[3]=word(0x10000);m->r.a[5]=mask(right(m->r.a[5],18),15);m->r.a[4]=mask(m->r.a[4],0x10000);
            m->r.a[5]=plus(m->r.a[5],2);m->r.a[3]=word(17);same=condition(m,m->r.a[5],17,0x18892);if(same<0)return m->flow;
            if(same)m->r.a[5]=word(18);
            same=condition(m,m->r.a[4],0,0x18898);if(same<0)return m->flow;
            if(same){
                m->r.a[4]=word(0x40024000);
                if(!load(m,0x1889e,plus(m->r.a[4],UINT32_C(0xfffff800)),&m->r.a[4],0))return m->flow;
                m->r.a[4]=mask(m->r.a[4],16);same=condition(m,m->r.a[4],0,0x188a4);if(same<0)return m->flow;base=same?4000000:8000000;
            }else{
                m->r.a[3]=word(0x40021000);
                if(!load(m,0x188b4,plus(m->r.a[3],4),&m->r.a[4],0))return m->flow;
                m->r.a[2]=word(0xc00000);m->r.a[4]=mask(m->r.a[4],0xc00000);same=condition(m,m->r.a[4],0xc00000,0x188bc);if(same<0)return m->flow;
                if(same)base=16000000;
                else{
                    if(!load(m,0x188ce,plus(m->r.a[3],4),&m->r.a[4],0))return m->flow;
                    m->r.a[3]=left(m->r.a[4],14);
                    if(!(m->r.a[3].known&UINT32_C(0x80000000)))return stop(m,SF_UNKNOWN_CONDITION,0x188d4);
                    base=(m->r.a[3].value&UINT32_C(0x80000000))?4000000:8000000;
                }
            }
            m->r.a[4]=word(base);m->r.a[5]=multiply(m->r.a[5],base);
        }
    }
    if(!store(m,0x18850,plus(m->r.gp,108),m->r.a[5],SF_WRITE32))return m->flow;
    m->r.a[5]=word(0x40021000);
    if(!load(m,0x18858,plus(m->r.a[5],4),&m->r.a[5],0))return m->flow;
    m->r.a[4]=plus(m->r.gp,64);m->r.a[5]=mask(right(m->r.a[5],4),15);m->r.a[5]=add(m->r.a[5],m->r.a[4]);
    if(!load(m,0x18864,m->r.a[5],&m->r.a[4],1))return m->flow;
    m->r.a[5]=plus(m->r.gp,108);
    if(!load(m,0x1886c,m->r.a[5],&m->r.a[5],0))return m->flow;
    m->r.a[5]=variable_right(m->r.a[5],m->r.a[4]);
    if(!store(m,0x18872,plus(m->r.gp,108),m->r.a[5],SF_WRITE32))return m->flow;
    ret(m,0x18876);return m->flow;
}
ri_flow sf_derive_1973c(sf_model *m){
    if(!admit(m,0x1973c))return m->flow;m->r.a[5]=plus(m->r.gp,108);
    if(!load(m,0x19740,m->r.a[5],&m->r.a[5],0))return m->flow;
    m->r.a[4]=word(8000000);m->r.a[5]=divide_8m(m->r.a[5]);m->r.a[5]=mask(m->r.a[5],255);
    if(!store(m,0x19752,plus(m->r.gp,382),m->r.a[5],SF_WRITE8))return m->flow;
    m->r.a[4]=word(1000);m->r.a[5]=multiply(m->r.a[5],1000);
    if(!store(m,0x1975e,plus(m->r.gp,380),m->r.a[5],SF_WRITE16))return m->flow;
    ret(m,0x19762);return m->flow;
}
ri_flow sf_ml_init_call(sf_model *m,ml_model *caller,const ml_request *q,ml_call_result *out){
    uint32_t entry,continuation;ri_flow flow;
    if(!m||!caller||!q||!out)return RI_HALT;if(m->flow!=RI_RETURNED)return m->flow;
    entry=q->pc==0x9254?0x18834:q->pc==0x925c?0x1973c:0;continuation=q->pc==0x9254?0x9258:0x9260;
    if(!entry||m->profile!=SF_ID2966_0EE64183||caller->profile!=ML_ID2966_0EE64183||caller->flow!=RI_RETURNED||q->kind!=ML_CALL||q->tail||equal(q->target,word(entry))!=1||equal(normalized(q->raw_target),word(entry))!=1||equal(q->continuation,word(continuation))!=1||equal(caller->r.ra,word(continuation))!=1)return stop(m,SF_BINDING,q->pc);
    sf_new_activation(m);m->r=caller->r;
    flow=entry==0x18834?sf_query_18834(m):sf_derive_1973c(m);caller->r=m->r;
    if(flow==RI_RETURNED)out->returned_to=m->return_target;return flow;
}
