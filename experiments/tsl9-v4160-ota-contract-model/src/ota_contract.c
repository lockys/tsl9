#include "ota_contract.h"
#include <string.h>
void oc_init(oc_model *m,const oc_backend *b){memset(m,0,sizeof(*m));if(b)m->backend=*b;}
static int stop(oc_model *m,oc_boundary boundary,uint32_t pc){m->flow=OC_HALT;m->boundary=boundary;m->boundary_pc=pc;return 0;}
static oc_request request(oc_kind kind,uint32_t pc,uint32_t target){oc_request q;memset(&q,0,sizeof(q));q.kind=kind;q.pc=pc;q.target=target;return q;}
static int invoke(oc_model *m,const oc_request *q,oc_scalar *out){
    oc_flow flow;oc_scalar result;memset(&result,0,sizeof(result));m->last_request=*q;m->operations++;
    if(!m->backend.invoke)return stop(m,OC_PROVIDER_UNKNOWN,q->pc);
    flow=m->backend.invoke(m->backend.context,q,&result);
    if(flow==OC_TRANSFER){m->flow=flow;return 0;}
    if(flow!=OC_RETURNED)return stop(m,OC_PROVIDER_UNKNOWN,q->pc);
    if(out)*out=result;return 1;
}
static int read_value(oc_model *m,uint32_t pc,uint32_t address,int word,oc_scalar *out){oc_request q=request(word?OC_READ32:OC_READ8,pc,0);q.address=address;if(!invoke(m,&q,out))return 0;if(!word){out->value&=255;out->known&=255;}return 1;}
static int write_byte(oc_model *m,uint32_t pc,uint32_t address,uint32_t value,uint32_t known){oc_request q=request(OC_WRITE8,pc,0);q.address=address;q.value=value&255;q.known=known&255;return invoke(m,&q,NULL);}
static int active(oc_model *m,uint32_t pc,oc_scalar *out){if(m->gp_known!=UINT32_MAX)return stop(m,OC_OPERAND_UNKNOWN,pc);return read_value(m,pc,m->gp+169u,0,out);}
static int set_active(oc_model *m,uint32_t pc,uint32_t value){if(m->gp_known!=UINT32_MAX)return stop(m,OC_OPERAND_UNKNOWN,pc);return write_byte(m,pc,m->gp+169u,value,255);}
/* -1 unknown; the provider returns the raw helper result: ZERO is a match. */
static int zero(oc_scalar value,uint32_t mask){if(value.value&value.known&mask)return 0;return (value.known&mask)==mask?1:-1;}
static int identity(oc_model *m,uint32_t pc,uint32_t pointer,uint32_t length,int *match){oc_scalar result;oc_request q=request(OC_IDENTITY,pc,0x92f2);q.address=pointer;q.length=length;if(!invoke(m,&q,&result))return 0;*match=zero(result,UINT32_MAX);if(*match<0)return stop(m,OC_CONDITION_UNKNOWN,pc);return 1;}
static int page_index(oc_model *m,uint32_t high_pc,uint32_t low_pc,uint32_t payload,uint32_t *page){oc_scalar h,l;if(!read_value(m,high_pc,payload,0,&h)||!read_value(m,low_pc,payload+1u,0,&l))return 0;if(h.known!=255 || l.known!=255)return stop(m,OC_OPERAND_UNKNOWN,high_pc);*page=(h.value<<8)|l.value;m->page=*page;m->page_known=UINT32_MAX;return 1;}
static int copy(oc_model *m,uint32_t pc,uint32_t dst,uint32_t src){oc_request q=request(OC_COPY,pc,0x4004c);q.address=dst;q.source=src;q.length=1024;return invoke(m,&q,NULL);}
static int small_reply(oc_model *m,uint32_t pc,uint32_t target,uint32_t connection,uint32_t command,unsigned length,oc_scalar first){oc_request q=request(OC_SMALL_REPLY,pc,target);q.connection=connection;q.command=command;q.length=length;q.payload[0]=(uint8_t)first.value;q.payload_known[0]=(uint8_t)first.known;if(length==2){q.payload[1]=1;q.payload_known[1]=255;}m->response_attempts++;return invoke(m,&q,NULL);}
static int schedule(oc_model *m,uint32_t pc,uint32_t callback,uint32_t delay){oc_request q=request(OC_SCHEDULE,pc,0x9124);q.address=callback;q.value=delay;return invoke(m,&q,NULL);}
static int echo_page(oc_model *m,uint32_t connection,uint32_t command,uint32_t page){
    oc_scalar allocation;oc_request q=request(OC_ALLOC,0x9bae,0x40070);uint32_t buffer,source;
    q.length=1026;if(!invoke(m,&q,&allocation))return 0;
    if(allocation.known!=UINT32_MAX)return stop(m,OC_OPERAND_UNKNOWN,0x9bb0);
    buffer=allocation.value;if(!buffer)return 1; /* No TX, no release. */
    if(!write_byte(m,0x9bb6,buffer+1u,page,255)||!write_byte(m,0x9bba,buffer,page>>8,255))return 0;
    source=(UINT32_C(0x20004)+page)<<10;
    if(!copy(m,0x9bd4,buffer+2u,source))return 0;
    q=request(OC_TX,0x9be0,0x8a56);q.address=buffer;q.length=1026;q.connection=connection;q.command=command;m->response_attempts++;
    if(!invoke(m,&q,NULL))return 0;
    /* The original tail delegates to the slot after TX, even if its ordinary
     * result did not indicate delivery. Preserve this unknown return/transfer. */
    q=request(OC_RELEASE,0x9bf8,0x40068);q.address=buffer;return invoke(m,&q,NULL);
}
static int write_page(oc_model *m,uint32_t connection,uint32_t payload,uint32_t length){
    uint32_t page,address,source,offset;oc_scalar state,flash,ram,status;oc_request q;int is_zero;
    if(!active(m,0x9c9c,&state))return 0;is_zero=zero(state,255);
    if(is_zero<0)return stop(m,OC_CONDITION_UNKNOWN,0x9ca0);
    if(is_zero || length!=1026)return 1;
    if(!page_index(m,0x9caa,0x9cae,payload,&page))return 0;
    address=(UINT32_C(0x20004)+page)<<10;
    if(address+UINT32_C(0xf7fff000)>UINT32_C(0x6f00))return 1;
    source=(payload+2u)&~UINT32_C(3);
    if(((payload+2u)&3u) && !copy(m,0x9cec,source,payload+2u))return 0;
    for(offset=0;offset<1024;offset+=256){q=request(OC_PROGRAM256,0x9d00,0x9c0a);q.address=address+offset;q.source=source+offset;q.length=256;if(!invoke(m,&q,NULL))return 0;m->program_calls++;}
    for(offset=0;offset<1024;offset+=4){
        uint32_t common;
        if(!read_value(m,0x9d10,address+offset,1,&flash)||!read_value(m,0x9d16,source+offset,1,&ram))return 0;
        common=flash.known&ram.known;
        if((flash.value^ram.value)&common){status.value=255;status.known=255;return small_reply(m,0x9d7a,0x13f66,connection,'W',1,status);}
        if(common!=UINT32_MAX)return stop(m,OC_CONDITION_UNKNOWN,0x9d18);
    }
    return echo_page(m,connection,'W',page);
}
oc_flow oc_dispatch(oc_model *m,uint32_t connection,uint32_t command,uint32_t payload,uint32_t length){
    oc_scalar state,mode,saved_mode,reply;uint32_t page;int match,z;
    m->flow=OC_RETURNED;m->boundary=OC_NO_BOUNDARY;m->boundary_pc=0;m->operations=m->program_calls=m->response_attempts=m->page=m->page_known=0;memset(&m->last_request,0,sizeof(m->last_request));
    if(command=='W'){(void)write_page(m,connection,payload,length);return m->flow;}
    if(command=='U'){
        if(!set_active(m,0x9d36,0)||!identity(m,0x9d3a,payload+1u,(length-1u)&255u,&match))return m->flow;
        if(!match)return m->flow;
        if(!read_value(m,0x9d40,payload,0,&mode))return m->flow;
        mode.value^=1;z=zero(mode,255);if(z<0){(void)stop(m,OC_CONDITION_UNKNOWN,0x9d46);return m->flow;}
        if(z && (!schedule(m,0x9d5a,0x8e18,200)||!schedule(m,0x9d6e,0x9ee0,400)))return m->flow;
        reply.value=1;reply.known=255;(void)small_reply(m,0x9d7a,0x13f66,connection,'U',1,reply);
    }else if(command=='S'){
        if(!read_value(m,0x9d80,payload,0,&saved_mode)||!identity(m,0x9d9a,payload+1u,(length-1u)&255u,&match))return m->flow;
        if(match){
            /* The source re-reads live mode after UID comparison; the reply's
             * first byte remains the earlier saved value. */
            if(!read_value(m,0x9da0,payload,0,&mode))return m->flow;z=zero(mode,255);
            if(z<0){(void)stop(m,OC_CONDITION_UNKNOWN,0x9da4);return m->flow;}match=z;
        }
        if(!set_active(m,match?0x9da6:0x9dba,match?1u:0u))return m->flow;
        if(!match){saved_mode.value=255;saved_mode.known=255;}
        (void)small_reply(m,0x9db4,0x13e98,connection,'S',2,saved_mode);
    }else if(command=='E' || command=='R'){
        if(!active(m,command=='E'?0x9df8:0x9dc6,&state))return m->flow;z=zero(state,255);
        if(z<0){(void)stop(m,OC_CONDITION_UNKNOWN,command=='E'?0x9dfc:0x9dca);return m->flow;}
        if(z || length!=(command=='E'?15u:16u))return m->flow;
        if(command=='R'){
            if(!identity(m,0x9dda,payload+2u,14,&match)||!match)return m->flow;
            if(!page_index(m,0x9de2,0x9de6,payload,&page))return m->flow;
            /* Unlike W, this original body has no page-number range guard. */
            (void)echo_page(m,connection,'R',page);
        }else{
            if(!read_value(m,0x9e06,payload,0,&mode))return m->flow;z=zero(mode,255);
            if(z<0){(void)stop(m,OC_CONDITION_UNKNOWN,0x9e0a);return m->flow;}
            if(!z || !identity(m,0x9e14,payload+1u,14,&match)||!match)return m->flow;
            if(!set_active(m,0x9e2c,0)||!schedule(m,0x9e30,0x8e18,200)||!schedule(m,0x9e44,0x99e8,400))return m->flow;
            reply.value=reply.known=0;(void)small_reply(m,0x9db4,0x13e98,connection,'E',0,reply);
        }
    }
    return m->flow;
}
