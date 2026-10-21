#include "gatt_ingress.h"
#include <string.h>
void gi_init(gi_model *m,const gi_backend *b){memset(m,0,sizeof(*m));if(b)m->backend=*b;m->max_operations=100000;}
static int stop(gi_model *m,gi_boundary boundary,uint32_t pc){m->flow=boundary==GI_BUDGET?GI_OBSERVATION_LIMIT:GI_HALT;m->boundary=boundary;m->boundary_pc=pc;return 0;}
static gi_request request(gi_kind kind,uint32_t pc,uint32_t target){gi_request q;memset(&q,0,sizeof(q));q.kind=kind;q.pc=pc;q.target=target;return q;}
static int invoke(gi_model *m,const gi_request *q,gi_scalar *out){gi_scalar r;gi_flow flow;memset(&r,0,sizeof(r));if(m->operations>=m->max_operations)return stop(m,GI_BUDGET,q->pc);m->operations++;m->last_request=*q;if(!m->backend.invoke)return stop(m,GI_PROVIDER_UNKNOWN,q->pc);flow=m->backend.invoke(m->backend.context,q,&r);if(flow==GI_TRANSFER){m->flow=GI_TRANSFER;return 0;}if(flow!=GI_RETURNED)return stop(m,GI_PROVIDER_UNKNOWN,q->pc);if(out)*out=r;return 1;}
static uint32_t mask(unsigned width){return width==4?UINT32_MAX:((UINT32_C(1)<<(width*8))-1u);}
static int read_at(gi_model *m,uint32_t pc,uint32_t address,unsigned width,gi_scalar *out){gi_request q=request(GI_READ,pc,0);q.address=address;q.width=width;if(!invoke(m,&q,out))return 0;out->value&=mask(width);out->known&=mask(width);return 1;}
static int write_at(gi_model *m,uint32_t pc,uint32_t address,unsigned width,uint32_t value,uint32_t known){gi_request q=request(GI_WRITE,pc,0);q.address=address;q.width=width;q.value=value&mask(width);q.known=known&mask(width);return invoke(m,&q,NULL);}
static int gp_address(gi_model *m,uint32_t pc,unsigned offset,uint32_t *out){if(m->gp_known!=UINT32_MAX)return stop(m,GI_OPERAND_UNKNOWN,pc);*out=m->gp+offset;return 1;}
static int read_gp(gi_model *m,uint32_t pc,unsigned offset,unsigned width,gi_scalar *out){uint32_t a;return gp_address(m,pc,offset,&a)&&read_at(m,pc,a,width,out);}
static int write_gp(gi_model *m,uint32_t pc,unsigned offset,unsigned width,uint32_t value,uint32_t known){uint32_t a;return gp_address(m,pc,offset,&a)&&write_at(m,pc,a,width,value,known);}
static int full(gi_model *m,uint32_t pc,gi_scalar a,unsigned width){return a.known==mask(width)?1:stop(m,GI_OPERAND_UNKNOWN,pc);}
static int equal(gi_scalar a,gi_scalar b,unsigned width){uint32_t k=a.known&b.known&mask(width);if((a.value^b.value)&k)return 0;return k==mask(width)?1:-1;}
static int equal_constant(gi_model *m,uint32_t pc,gi_scalar a,uint32_t value,unsigned width,int *out){gi_scalar b;b.value=value;b.known=mask(width);*out=equal(a,b,width);return *out<0?stop(m,GI_CONDITION_UNKNOWN,pc):1;}
static gi_flow returned(gi_model *m,uint32_t value){m->result.value=value;m->result.known=UINT32_MAX;return m->flow;}
static int clear_state(gi_model *m){return write_gp(m,0x8a4c,156,1,0,255);}
static int add_sum(gi_model *m,gi_scalar byte){gi_scalar sum;if(!read_gp(m,0x89a8,165,1,&sum)||!full(m,0x89ac,sum,1)||!full(m,0x89ac,byte,1))return 0;return write_gp(m,0x89ae,165,1,sum.value+byte.value,255);}
gi_flow gi_receive(gi_model *m,uint32_t context,uint32_t attribute,uint32_t chunk,uint32_t length,uint32_t offset,uint32_t method){
    gi_scalar a,b,byte,state,clock,last;gi_request q;int eq;uint32_t expected,next,index=0;
    (void)method;m->flow=GI_RETURNED;m->boundary=GI_NONE;m->boundary_pc=m->operations=m->dispatches=m->index=0;m->result.value=m->result.known=0;memset(&m->last_request,0,sizeof(m->last_request));
    if(!read_at(m,0x888c,attribute+8u,1,&a))return m->flow;
    if(!(a.known&32u)){(void)stop(m,GI_CONDITION_UNKNOWN,0x8894);return m->flow;}
    if(a.value&32u)return returned(m,8);
    if(!read_at(m,0x8898,attribute,1,&a)||!equal_constant(m,0x889e,a,2,1,&eq))return m->flow;
    if(!eq)return returned(m,0);
    if(!read_at(m,0x88a6,attribute+4u,4,&a)||!full(m,0x88b0,a,4)||!read_at(m,0x88b0,a.value,2,&b)||!equal_constant(m,0x88ba,b,0x2902,2,&eq))return m->flow;
    if(eq){q=request(GI_CCC,0x88c8,0x40144);q.args[0]=context;q.args[1]=attribute;q.args[2]=chunk;q.args[3]=length;q.args[4]=offset;q.args[5]=1;(void)invoke(m,&q,&m->result);return m->flow;}
    if(!read_gp(m,0x88ce,36,4,&a)||!full(m,0x88d0,a,4)||!read_at(m,0x88d0,a.value,2,&a))return m->flow;
    eq=equal(a,b,2);if(eq<0){(void)stop(m,GI_CONDITION_UNKNOWN,0x88d4);return m->flow;}if(!eq)return returned(m,0);
    if(!read_at(m,0x88d8,attribute+10u,2,&a)||!read_gp(m,0x88dc,42,2,&b))return m->flow;
    eq=equal(a,b,2);if(eq<0){(void)stop(m,GI_CONDITION_UNKNOWN,0x88e0);return m->flow;}if(!eq)return returned(m,0);
    q=request(GI_CLOCK,0x8906,0x81b0);if(!invoke(m,&q,&clock)||!read_gp(m,0x890c,160,4,&last)||!full(m,0x8912,clock,4)||!full(m,0x8912,last,4))return m->flow;
    if(clock.value-last.value>299u && !write_gp(m,0x891a,156,1,0,255))return m->flow;
    if(!write_gp(m,0x891e,160,4,clock.value,UINT32_MAX))return m->flow;
    while((index&65535u)<length){
        m->index=index;
        /* The original reads the global state before reading this input byte. */
        if(!read_gp(m,0x8966,156,1,&state)||!read_at(m,0x896a,chunk+index,1,&byte)||!full(m,0x896e,state,1))return m->flow;
        if(state.value==0 || state.value==1){
            if(!equal_constant(m,state.value?0x898a:0x8974,byte,state.value?0x7f:0x55,1,&eq))return m->flow;
            if(!eq){if(!clear_state(m))return m->flow;}
            else if(state.value==0){if(!write_gp(m,0x897a,156,1,1,255))return m->flow;}
            else if(!write_gp(m,0x8990,156,1,2,255)||!write_gp(m,0x8994,165,1,0,255))return m->flow;
        }else if(state.value==2){
            if(!write_gp(m,0x89a0,156,1,3,255)||!write_gp(m,0x89a4,164,1,byte.value,byte.known)||!add_sum(m,byte))return m->flow;
        }else if(state.value==3){
            if(!write_gp(m,0x89ba,156,1,4,255)||!write_gp(m,0x89c2,142,2,byte.value<<8,(byte.known<<8)|255u)||!add_sum(m,byte))return m->flow;
        }else if(state.value==4){
            if(!write_gp(m,0x89cc,138,2,0,65535)||!read_gp(m,0x89d0,142,2,&a))return m->flow;
            /* LBU proves the upper byte zero when OR-ing into a u16 length. */
            b.value=a.value|byte.value;b.known=((a.value&a.known)|(byte.value&(byte.known|65280u))|(a.known&(byte.known|65280u)))&65535u;
            if(!write_gp(m,0x89d6,142,2,b.value,b.known)||!full(m,0x89da,b,2))return m->flow;
            next=b.value==0?6u:(b.value>1040u?0u:5u);
            if(!write_gp(m,next==0?0x89f0:0x89ea,156,1,next,255)||!add_sum(m,byte))return m->flow;
        }else if(state.value==5){
            if(!read_gp(m,0x89fa,138,2,&a)||!full(m,0x8a02,a,2))return m->flow;
            if(a.value>1039u){if(!clear_state(m))return m->flow;}
            else{
                next=(a.value+1u)&65535u;
                if(!write_gp(m,0x8a0e,138,2,next,65535)||!write_at(m,0x8a1c,UINT32_C(0x2000b9d8)+a.value,1,byte.value,byte.known)||!read_gp(m,0x8a20,142,2,&b)||!full(m,0x8a24,b,2))return m->flow;
                if(next>=b.value && !write_gp(m,0x89ea,156,1,6,255))return m->flow;
                if(!add_sum(m,byte))return m->flow;
            }
        }else if(state.value==6){
            if(!read_gp(m,0x8a2e,165,1,&a))return m->flow;
            eq=equal(a,byte,1);if(eq<0){(void)stop(m,GI_CONDITION_UNKNOWN,0x8a32);return m->flow;}
            if(eq){
                if(!read_gp(m,0x8a36,142,2,&a)||!full(m,0x8a48,a,2))return m->flow;expected=a.value;
                if(!read_gp(m,0x8a42,164,1,&a)||!full(m,0x8a48,a,1))return m->flow;
                q=request(GI_DISPATCH,0x8a48,0x14056);q.args[0]=context;q.args[1]=a.value;q.args[2]=UINT32_C(0x2000b9d8);q.args[3]=expected;m->dispatches++;
                if(!invoke(m,&q,NULL))return m->flow;
            }
            if(!clear_state(m))return m->flow;
        }else if(!clear_state(m))return m->flow;
        index++;m->index=index;
    }
    return returned(m,0);
}
