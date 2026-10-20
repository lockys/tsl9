#include "general_reports.h"
#include <string.h>
#define FULL UINT32_MAX
#define A(x) (TF_RAM_BASE+UINT32_C(x))
#define AUTH A(0xc790)
#define CACHE A(0xc1b4)
static int stop(gr_model*m,uint32_t va,uint32_t address,uint32_t needed){m->flow=GB_HALT;m->boundary_va=va;m->boundary_address=address;m->needed_mask=needed;return 0;}
static int returned(gr_model*m,gb_flow flow,uint32_t va,uint32_t address){
    if(flow==GB_RETURNED)return 1;
    if(flow==GB_TRANSFER){m->flow=flow;m->transfer_va=va;m->transfer_address=address;return 0;}
    return stop(m,va,address,0);
}
static int span(uint32_t address,size_t n){return address>=TF_RAM_BASE&&n<=TF_RAM_SIZE&&address-TF_RAM_BASE<=TF_RAM_SIZE-n;}
static int ram_value(gr_model*m,uint32_t address,unsigned n,uint32_t site,gb_scalar*out){
    unsigned i;uint32_t widthmask=n==4?FULL:(UINT32_C(1)<<(8*n))-1;out->value=0;out->known=~widthmask;
    if(!m->memory||!span(address,n))return stop(m,site,address,widthmask);
    for(i=0;i<n;i++){out->value|=(uint32_t)m->memory->ram[address-TF_RAM_BASE+i]<<(8*i);out->known|=(uint32_t)m->memory->known[address-TF_RAM_BASE+i]<<(8*i);}return 1;
}
static int scalar(gr_model*m,uint32_t address,unsigned n,uint32_t site,uint32_t*out){
    gb_scalar r;if(!ram_value(m,address,n,site,&r))return 0;if(r.known!=FULL)return stop(m,site,address,FULL);*out=r.value;return 1;
}
/* Native equality/nonzero may be decided from a proper subset of loaded bits.
   Keep the original raw32 compare and LHU/LBU zero extension. Ambiguous control
   remains at the load supplying the branch; scalar sinks still require FULL. */
static int equals(gr_model*m,uint32_t address,unsigned n,uint32_t site,uint32_t expected,int*out){
    gb_scalar r;if(!ram_value(m,address,n,site,&r))return 0;
    if((r.value^expected)&r.known){*out=0;return 1;}
    if(r.known!=FULL)return stop(m,site,address,FULL);*out=1;return 1;
}
static int nonzero(gr_model*m,uint32_t address,unsigned n,uint32_t site,int*out){
    gb_scalar r;if(!ram_value(m,address,n,site,&r))return 0;
    if(r.value&r.known){*out=1;return 1;}
    if(r.known!=FULL)return stop(m,site,address,FULL);*out=0;return 1;
}
static int predicate(gr_model*m,uint32_t address,unsigned n,uint32_t site,gb_scalar*out){
    gb_scalar r;if(!ram_value(m,address,n,site,&r))return 0;
    out->value=0;out->known=FULL;
    if(r.value&r.known)out->value=1;else if(r.known!=FULL)out->known=FULL^1u;return 1;
}
static void write_ram(gr_model*m,uint32_t address,uint32_t value,unsigned n){
    unsigned i;for(i=0;i<n;i++){m->memory->ram[address-TF_RAM_BASE+i]=(uint8_t)(value>>(8*i));m->memory->known[address-TF_RAM_BASE+i]=255;}
}
static int begin(gr_model*m,uint32_t entry){
    if(m->flow==GB_TRANSFER)return 0;
    m->entry=entry;m->flow=GB_RETURNED;m->recognized=1;m->boundary_va=m->boundary_address=m->needed_mask=0;m->calls=m->replies=0;
    m->frame_offset=m->frame_length=0;m->transfer_va=m->transfer_address=0;memset(m->stack,0,sizeof(m->stack));memset(m->known,0,sizeof(m->known));memset(&m->last_request,0,sizeof(m->last_request));return 1;
}
static int invoke(gr_model*m,gr_request*r){
    gb_scalar ignored;gb_flow flow;if(m->flow==GB_TRANSFER)return 0;m->last_request=*r;++m->calls;ignored.value=ignored.known=0;
    flow=m->backend.invoke?m->backend.invoke(m->backend.context,m,r,&ignored):GB_HALT;
    return returned(m,flow,r->callsite,r->target); /* Scalar is unused, flow is not. */
}
static int zero(gr_model*m,uint32_t site,size_t off,size_t n){
    gr_request r;size_t i;memset(&r,0,sizeof(r));r.callsite=site;r.target=72;r.arguments[2]=(uint32_t)n;r.known[1]=r.known[2]=FULL;
    r.buffer=m->stack+off;r.buffer_known=m->known+off;r.buffer_length=n;if(!invoke(m,&r))return 0;
    for(i=0;i<n;i++)if(r.buffer[i]||r.buffer_known[i]!=255)return stop(m,site,72,255);return 1;
}
static int mode_body(gr_model*m,uint32_t h,uint32_t mode){
    int same;unsigned index=0;if(!equals(m,AUTH+2,2,0x139be,h,&same))return 0;
    if(!same){index=1;if(!equals(m,AUTH+6,2,0x139ce,h,&same))return 0;if(!same)return 1;}
    write_ram(m,AUTH+5+4*index,mode,1);return 1;
}
static int cache_body(gr_model*m,uint32_t direction,uint32_t index,gr_view*view){
    uint32_t cache_address=CACHE+index*UINT32_C(12);gr_request r;
    memset(&r,0,sizeof(r));r.target=76;r.callsite=0x82c0;r.arguments[2]=12;r.known[2]=FULL;r.buffer_length=12;
    if(!view||view->available<12)return stop(m,0x82c0,view?view->address:0,0);
    if(direction){
        r.arguments[1]=cache_address;r.known[1]=FULL;r.arguments[0]=view->address;r.known[0]=view->address?FULL:0;
        if(view->address){if(!span(view->address,12))return stop(m,0x82c0,view->address,0);r.buffer=m->memory->ram+view->address-TF_RAM_BASE;r.buffer_known=m->memory->known+view->address-TF_RAM_BASE;}
        else{r.buffer=view->data;r.buffer_known=view->known;}
    }else{
        r.arguments[0]=cache_address;r.known[0]=FULL;r.arguments[1]=view->address;r.known[1]=view->address?FULL:0;
        if(!span(cache_address,12))return stop(m,0x82c0,cache_address,0);
        r.buffer=m->memory->ram+cache_address-TF_RAM_BASE;r.buffer_known=m->memory->known+cache_address-TF_RAM_BASE;r.input=view->data;r.input_known=view->known;
    }
    if(!r.buffer||!r.buffer_known||(!direction&&!view->address&&(!r.input||!r.input_known)))return stop(m,0x82c0,0,0);
    return invoke(m,&r);
}
static int cache_read(gr_model*m,unsigned index,size_t off){
    gr_view view;memset(&view,0,sizeof(view));view.data=m->stack+off;view.known=m->known+off;view.available=12;return cache_body(m,1,index,&view);
}
static int getter_body(gr_model*m,uint32_t entry,gb_scalar*out){
    gb_scalar condition,p;switch(entry){
    case 0xd392:return ram_value(m,A(0xbf62),2,0xd396,out);
    case 0xd31a:return ram_value(m,A(0xbf5e),2,0xd31e,out);
    case 0xd388:return ram_value(m,A(0xbf61),1,0xd38c,out);
    case 0xff3c:return ram_value(m,A(0xbfa4),4,0xff44,out);
    case 0xd17c:
        if(!predicate(m,A(0xbf60),1,0xd180,&condition))return 0;
        if((condition.known&1)&&(condition.value&1)){out->value=2;out->known=FULL;return 1;}
        if(!predicate(m,A(0xbf58),2,0xd18c,&p))return 0;
        if(condition.known&1)*out=p;
        else{out->value=p.value;out->known=p.known&~(p.value^UINT32_C(2));}
        /* Both possible native paths only read SRAM and RET@D194. Joining their
           scalar knowledge preserves known-return flow without choosing a path. */
        return 1;
    default:m->recognized=0;out->value=out->known=0;return stop(m,entry,entry,0);
    }
}
static gb_scalar local(gr_model*m,size_t off,unsigned n){
    gb_scalar r={0,0};unsigned i;for(i=0;i<n;i++){r.value|=(uint32_t)m->stack[off+i]<<(8*i);r.known|=(uint32_t)m->known[off+i]<<(8*i);}return r;
}
static void bytes(gr_model*m,size_t dest,size_t source,size_t n){
    memmove(m->stack+dest,m->stack+source,n);memmove(m->known+dest,m->known+source,n);
}
static void field(gr_model*m,unsigned framebit,unsigned width,uint32_t value,uint32_t known){
    unsigned i;for(i=0;i<width;i++){unsigned bit=framebit+i,off=(unsigned)m->frame_offset+bit/8;uint8_t mask=(uint8_t)(1u<<(bit%8));
        m->stack[off]=(uint8_t)((m->stack[off]&~mask)|(((value>>i)&1)?mask:0));
        m->known[off]=(uint8_t)((m->known[off]&~mask)|(((known>>i)&1)?mask:0));
    }
}
static int reply(gr_model*m,uint32_t site,uint16_t h,uint8_t command,uint32_t source,const uint8_t*d,const uint8_t*k,size_t n){
    gb_reply_request r;memset(&r,0,sizeof(r));r.wrapper_va=0x8cfa;r.handle=h;r.command=command;r.source_address=source;r.data=d;r.known=k;r.length=n;++m->replies;
    return returned(m,m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT,site,0x8cfa);
}
static int d0_body(gr_model*m){
    gb_scalar a,b,v;m->frame_offset=12;m->frame_length=29;
    if(!zero(m,0x1430e,12,29)||!cache_read(m,1,0))return 0;bytes(m,12,3,4);
    if(!cache_read(m,11,0))return 0;bytes(m,16,3,8);
    if(!cache_read(m,5,0))return 0;a=local(m,0,4);b=local(m,4,4);
    field(m,18*8,12,(a.value>>26)|((b.value&63)<<6),(a.known>>26)|((b.known&63)<<6));
    field(m,19*8+4,12,(b.value>>8)&4095,(b.known>>8)&4095);
    if(!cache_read(m,6,0))return 0;bytes(m,26,5,2);bytes(m,24,7,2);
    if(!cache_read(m,7,0))return 0;bytes(m,28,5,2);
    if(!cache_read(m,3,0))return 0;v=local(m,8,2);field(m,21*8,10,v.value&1023,v.known&1023);
    if(!getter_body(m,0xd392,&v))return 0;field(m,20*8+18,10,v.value&1023,v.known&1023);
    if(!getter_body(m,0xd31a,&v))return 0;field(m,20*8+30,2,v.value&3,v.known&3);field(m,24*8,7,(v.value>>2)&127,(v.known>>2)&127);
    if(!getter_body(m,0xd17c,&v))return 0;field(m,20*8+28,2,v.value&3,v.known&3);
    if(!getter_body(m,0xd388,&v))return 0;field(m,24*8+7,7,v.value&127,v.known&127);
    if(!getter_body(m,0xff3c,&v))return 0;field(m,24*8+14,26,v.value&0x03ffffff,v.known&0x03ffffff);
    return reply(m,0x142cc,m->handle,0xd0,0,m->stack+12,m->known+12,29);
}
static int d2_body(gr_model*m){
    m->frame_offset=0;m->frame_length=8;if(!zero(m,0x14286,0,8)||!cache_read(m,4,12))return 0;
    /* Native SP35..40 after OUT@SP32:cache offsets3..8, not4..9. */
    bytes(m,0,15,6);return reply(m,0x142cc,m->handle,0xd2,0,m->stack,m->known,8);
}
void gr_init(gr_model*m,tf_model*memory,const gr_backend*b){memset(m,0,sizeof(*m));m->memory=memory;if(b)m->backend=*b;}
gb_flow gr_command(gr_model*m,uint16_t h,uint8_t c,uint32_t payload,uint16_t n){
    int first,pause;if(!begin(m,c==0xd1?0x144ce:0x14254))return m->flow;m->handle=h;m->command=c;m->argument=payload;m->length=n;
    if(c!=0xd0&&c!=0xd1&&c!=0xd2){m->recognized=0;stop(m,m->entry,c,0);return m->flow;}
    if(!equals(m,payload,1,m->entry,1,&first)||!first)return m->flow;
    if(!mode_body(m,h,c==0xd1?4:3)||c==0xd1)return m->flow;
    if(!nonzero(m,AUTH,1,0x1426a,&pause)||pause)return m->flow;
    if(c==0xd2)(void)d2_body(m);else(void)d0_body(m);return m->flow;
}
gb_flow gr_mode(gr_model*m,uint32_t handle,uint32_t mode){if(!begin(m,0x139ba))return m->flow;m->argument=handle;(void)mode_body(m,handle,mode);return m->flow;}
gb_flow gr_cache_transfer(gr_model*m,uint32_t direction,uint32_t index,gr_view*view){if(!begin(m,0x829e))return m->flow;m->argument=index;(void)cache_body(m,direction,index,view);return m->flow;}
gb_flow gr_getter(gr_model*m,uint32_t va,gb_scalar*out){if(!begin(m,va))return m->flow;(void)getter_body(m,va,out);return m->flow;}
gb_flow gr_d1_view(gr_model*m,const gr_view*record){
    unsigned i;uint32_t h,source=record&&record->address?record->address+3:0;int pause,gate;if(!begin(m,0x139e6))return m->flow;m->argument=record?record->address:0;m->command=0xd1;
    if(!nonzero(m,AUTH,1,0x139ea,&pause)||pause)return m->flow;
    for(i=0;i<2;i++){uint32_t slot=AUTH+4*i;
        if(!equals(m,slot+2,2,0x13a1c,65534,&gate))return m->flow;if(gate)continue;
        if(!equals(m,slot+5,1,0x13a24,4,&gate))return m->flow;if(!gate)continue;
        if(!nonzero(m,slot+4,1,0x13a2c,&gate))return m->flow;if(!gate)continue;
        if(!scalar(m,slot+2,2,0x13a36,&h))return m->flow;
        {gb_reply_request r;memset(&r,0,sizeof(r));r.wrapper_va=0x8cfa;r.handle=(uint16_t)h;r.command=0xd1;r.length=8;r.source_address=source;r.bounded=1;
            /*139E6 only computes record+3; source bytes are first read by8CFA
              after transport selection and header writes. Avoid host pointer
              arithmetic outside the supplied borrower without pre-reading it. */
            if(record&&record->address&&span(source,8)){r.data=m->memory->ram+source-TF_RAM_BASE;r.known=m->memory->known+source-TF_RAM_BASE;r.available=8;}
            else if(record&&!record->address&&record->data&&record->known&&record->available>=3){r.data=record->data+3;r.known=record->known+3;r.available=record->available-3;}
            ++m->replies;if(!returned(m,m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT,0x13a42,0x8cfa))return m->flow;
        }
    }return m->flow;
}
gb_flow gr_d1(gr_model*m,uint32_t record){gr_view view;memset(&view,0,sizeof(view));view.address=record;return gr_d1_view(m,&view);}
