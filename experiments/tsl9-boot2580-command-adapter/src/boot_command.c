#include "boot_command.h"
#include <string.h>

static bc_value word(uint32_t v) { bc_value x; x.value=v; x.known=UINT32_MAX; return x; }
/* Bit-known addition of a constant, retaining uncertain carry. This is data
 * arithmetic for numeric requests, not instruction execution. */
static bc_value add(bc_value a,uint32_t constant) {
    bc_value r={0,0}; unsigned bit,carry=1;
    for(bit=0;bit<32;bit++) {
        unsigned possible=0,next=0,av,cv,b=(constant>>bit)&1u;
        unsigned abits=(a.known&(UINT32_C(1)<<bit))?(1u<<((a.value>>bit)&1u)):3u;
        for(av=0;av<2;av++) for(cv=0;cv<2;cv++) if((abits&(1u<<av))&&(carry&(1u<<cv))) {
            unsigned sum=av+b+cv; possible|=1u<<(sum&1u);next|=1u<<(sum>>1);
        }
        if(possible!=3u) {r.known|=UINT32_C(1)<<bit;if(possible==2u)r.value|=UINT32_C(1)<<bit;}
        carry=next;
    }
    return r;
}
static int equal(bc_value a,bc_value b,uint32_t mask) {
    uint32_t common=a.known&b.known&mask;
    if((a.value^b.value)&common)return 0;
    return common==mask?1:-1;
}
static int stop(bc_model *m,bc_boundary boundary,uint32_t pc) {
    m->flow=BC_HALT;m->boundary=boundary;m->boundary_pc=pc;return 0;
}
static bc_request request(bc_kind kind,uint32_t pc,uint32_t target,unsigned argc) {
    bc_request q;memset(&q,0,sizeof q);q.kind=kind;q.pc=pc;q.argc=argc;
    q.target=q.raw_target=word(target);return q;
}
static int invoke(bc_model *m,const bc_request *q,bc_value *out) {
    bc_flow flow;bc_value value={0,0};m->last_request=*q;
    if(m->operations>=m->observation_budget)return stop(m,BC_OBSERVATION_BUDGET,q->pc);
    ++m->operations;
    if(!m->backend.invoke)return stop(m,BC_MISSING_PROVIDER,q->pc);
    flow=m->backend.invoke(m->backend.context,m,q,&value);
    if(flow==BC_TRANSFER){m->flow=flow;m->boundary_pc=q->pc;return 0;}
    if(flow!=BC_RETURNED)return stop(m,BC_PROVIDER_STOP,q->pc);
    if(out)*out=value;return 1;
}
static int read_value(bc_model *m,uint32_t pc,bc_value address,unsigned width,bc_value *out) {
    bc_request q=request(width==1?BC_READ8:BC_READ32,pc,0,1);q.args[0]=address;
    if(!invoke(m,&q,out))return 0;
    if(width==1){out->value&=255;out->known&=255;}return 1;
}
static int write_value(bc_model *m,uint32_t pc,bc_value address,bc_value value,unsigned width) {
    bc_request q=request(width==1?BC_WRITE8:BC_WRITE32,pc,0,2);
    q.args[0]=address;q.args[1]=value;
    if(width==1){q.args[1].value&=255;q.args[1].known&=255;}return invoke(m,&q,0);
}
static int set_active(bc_model *m,uint32_t pc,uint32_t value) {
    return write_value(m,pc,add(m->gp,139),word(value),1);
}
static int active(bc_model *m,uint32_t pc,uint32_t branch_pc,int *yes) {
    bc_value value;int z;
    if(!read_value(m,pc,add(m->gp,139),1,&value))return 0;
    z=equal(value,word(0),255);
    if(z<0)return stop(m,BC_CONDITION_UNKNOWN,branch_pc);*yes=!z;return 1;
}
static int identity(bc_model *m,uint32_t pc,uint32_t payload,uint32_t length,bc_value *out) {
    bc_request q=request(BC_IDENTITY,pc,0x1c82,2);
    q.args[0]=word(payload+1u);q.args[1]=word((length-1u)&255u);return invoke(m,&q,out);
}
static int reply(bc_model *m,uint32_t pc,uint32_t target,uint32_t connection,
                  uint32_t command,bc_value pointer,bc_value length) {
    bc_request q=request(BC_REPLY,pc,target,target==0x2aba?3u:4u);
    q.args[0]=word(connection);q.args[1]=word(command);q.args[2]=pointer;
    if(q.argc==4)q.args[3]=length;
    ++m->reply_attempts;return invoke(m,&q,0);
}
static int saved_payload(bc_model *m,uint32_t ptr_pc,uint32_t len_pc,
                          bc_value *pointer,bc_value *length) {
    return read_value(m,ptr_pc,add(m->body_sp,8),4,pointer)&&
           read_value(m,len_pc,add(m->body_sp,12),4,length);
}
static int start(bc_model *m,uint32_t connection,uint32_t payload,uint32_t length) {
    bc_value uid,pointer,count,mode;bc_request q;int match;
    if(!write_value(m,0x22d6,add(m->body_sp,12),word(length),4)||
       !write_value(m,0x22d8,add(m->body_sp,8),word(payload),4)||
       !identity(m,0x22da,payload,length,&uid)||
       !saved_payload(m,0x22dc,0x22de,&pointer,&count))return 0;
    match=equal(uid,word(0),UINT32_MAX);
    if(match<0)return stop(m,BC_CONDITION_UNKNOWN,0x22e0);
    if(match){
        if(!read_value(m,0x22e2,pointer,1,&mode))return 0;
        match=equal(mode,word(1),255);
        if(match<0)return stop(m,BC_CONDITION_UNKNOWN,0x22e8);
    }
    if(!match){
        if(!set_active(m,0x2312,0)||!write_value(m,0x2318,pointer,word(255),1))return 0;
    } else {
        if(!set_active(m,0x22ec,1))return 0;
        q=request(BC_CANCEL_STARTUP,0x22f0,0x250e,0);if(!invoke(m,&q,0))return 0;
        q=request(BC_METADATA,0x22f4,0x2184,1);q.args[0]=word(2);
        /* Numeric return value is ignored even if not known. Nonreturn isn't. */
        if(!invoke(m,&q,0)||!saved_payload(m,0x22f6,0x22f8,&pointer,&count))return 0;
    }
    return reply(m,0x230e,0x2aa0,connection,'S',pointer,count);
}
static int write_page(bc_model *m,uint32_t connection,uint32_t payload,uint32_t length) {
    bc_value low,high,page,address,slot,flash,source_value;
    bc_request q;uint32_t minimum,maximum,source,offset;int yes,match;
    if(!active(m,0x2202,0x2206,&yes))return 0;
    if(!yes||length!=1026)return 1;
    if(!read_value(m,0x2210,word(payload+1u),1,&low)||
       !read_value(m,0x2214,word(payload),1,&high))return 0;
    page.value=(high.value<<8)|low.value;
    page.known=UINT32_C(0xffff0000)|(high.known<<8)|low.known;m->page=page;
    minimum=page.value&page.known&65535u;maximum=minimum|(~page.known&65535u);
    if(minimum>95)return 1;
    if(maximum>95)return stop(m,BC_CONDITION_UNKNOWN,0x2240);
    address.value=page.value<<10;address.known=(page.known<<10)|1023u;
    address=add(address,UINT32_C(0x08008000));m->destination=address;
    source=(payload+2u)&~UINT32_C(3);
    if((payload+2u)&3u){
        if(!read_value(m,0x2256,word(0x4004c),4,&slot))return 0;
        q=request(BC_INDIRECT_COPY,0x225e,0,3);q.nominal_slot=0x4004c;q.raw_target=slot;
        q.target.value=slot.value&~UINT32_C(1);q.target.known=slot.known|1u;
        q.args[0]=word(source);q.args[1]=word(payload+2u);q.args[2]=word(1024);
        if(!invoke(m,&q,0))return 0;
    }
    for(offset=0;offset<1024;offset+=256){
        q=request(BC_PROGRAM256,0x2272,0x20e6,2);
        q.args[0]=add(address,offset);q.args[1]=word(source+offset);
        ++m->program_attempts;if(!invoke(m,&q,0))return 0;
    }
    for(offset=0;offset<1024;offset+=4){
        if(!read_value(m,0x2282,add(address,offset),4,&flash)||
           !read_value(m,0x2288,word(source+offset),4,&source_value))return 0;
        match=equal(flash,source_value,UINT32_MAX);
        if(!match)return 1; /* Original silent mismatch, no Runtime FF reply. */
        if(match<0)return stop(m,BC_CONDITION_UNKNOWN,0x228a);
    }
    return reply(m,0x230e,0x2aa0,connection,'W',word(0),word(0));
}
static int finish(bc_model *m,uint32_t connection) {
    int yes;bc_request q;
    if(!active(m,0x231e,0x2322,&yes))return 0;if(!yes)return 1;
    if(!set_active(m,0x2336,0))return 0;
    q=request(BC_SCHEDULE,0x233a,0x1afa,4);
    q.args[0]=word(0x192c);q.args[1]=word(0);q.args[2]=word(200);q.args[3]=word(0);
    if(!invoke(m,&q,0))return 0;
    q.pc=0x234e;q.args[0]=word(0x20e2);q.args[2]=word(400);if(!invoke(m,&q,0))return 0;
    return reply(m,0x230e,0x2aa0,connection,'E',word(0),word(0));
}
void bc_new_activation(bc_model *m) {
    m->flow=BC_RETURNED;m->boundary=BC_NONE;m->boundary_pc=0;
    m->operations=m->program_attempts=m->reply_attempts=0;
    m->page.value=m->page.known=m->destination.value=m->destination.known=0;
    memset(&m->last_request,0,sizeof m->last_request);
}
void bc_init(bc_model *m,const bc_backend *backend) {
    memset(m,0,sizeof *m);if(backend)m->backend=*backend;m->observation_budget=4096;
}
bc_flow bc_dispatch(bc_model *m,uint32_t connection,uint32_t command,
                    uint32_t payload,uint32_t length) {
    bc_value uid;int match;
    if(m->flow!=BC_RETURNED)return m->flow;bc_new_activation(m);
    if(command=='S') (void)start(m,connection,payload,length);
    else if(command=='W') (void)write_page(m,connection,payload,length);
    else if(command=='E') (void)finish(m,connection);
    else if(command=='U') {
        if(!set_active(m,0x22a8,0)||!identity(m,0x22ac,payload,length,&uid))return m->flow;
        match=equal(uid,word(0),UINT32_MAX);
        if(match<0)(void)stop(m,BC_CONDITION_UNKNOWN,0x22ae);
        else if(match)(void)reply(m,0x22c6,0x2aba,connection,'U',word(0),word(0));
    }
    /* Other commands return in21BE. This says nothing about outer GATT routes. */
    return m->flow;
}
