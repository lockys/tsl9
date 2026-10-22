#include "general_ble.h"
#include <string.h>
#define GP UINT32_C(0x20004000)
#define AUTH UINT32_C(0x2000c790)
#define FULL UINT32_MAX
static int halt_at(gb_model *m,uint32_t va,uint32_t address) {
    m->flow=GB_HALT;m->boundary_va=va;m->boundary_address=address;return 0;
}
static int returned(gb_model *m,gb_flow flow,uint32_t va,uint32_t address){
    if(flow==GB_RETURNED)return 1;
    if(flow==GB_TRANSFER){m->flow=flow;m->transfer_va=va;m->transfer_address=address;return 0;}
    return halt_at(m,va,address);
}
static int in_ram(uint32_t a,size_t n) {
    return a>=TF_RAM_BASE&&a<=TF_RAM_BASE+TF_RAM_SIZE&&n<=TF_RAM_BASE+TF_RAM_SIZE-a;
}
static int bytes(gb_model *m,uint32_t a,uint8_t *d,uint8_t *k,size_t n,uint32_t va) {
    if(in_ram(a,n)){memcpy(d,m->memory->ram+a-TF_RAM_BASE,n);memcpy(k,m->memory->known+a-TF_RAM_BASE,n);return 1;}
    memset(d,0,n);memset(k,0,n);
    if(m->backend.read)m->backend.read(m->backend.context,a,d,k,n);
    /* Outside-SRAM byte results may remain symbolic until actually used. */
    (void)va;return 1;
}
static int scalar(gb_model *m,uint32_t a,unsigned n,uint32_t need,uint32_t *v,uint32_t va) {
    uint8_t d[4],k[4];uint32_t known=0;unsigned i;
    if(n>4)return halt_at(m,va,a);bytes(m,a,d,k,n,va);*v=0;
    for(i=0;i<n;i++){*v|=(uint32_t)d[i]<<(8*i);known|=(uint32_t)k[i]<<(8*i);}
    if((known&need)!=need)return halt_at(m,va,a);return 1;
}
static int write_value(gb_model *m,uint32_t a,uint32_t v,unsigned n,uint32_t va) {
    unsigned i;if(!in_ram(a,n))return halt_at(m,va,a);
    for(i=0;i<n;i++){m->memory->ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));m->memory->known[a-TF_RAM_BASE+i]=255;}
    return 1;
}
static int set_bit(gb_model *m,uint32_t a,uint8_t bit,int value,uint32_t va) {
    size_t i;if(!in_ram(a,1))return halt_at(m,va,a);i=a-TF_RAM_BASE;
    m->memory->ram[i]=(uint8_t)((m->memory->ram[i]&~bit)|(value?bit:0));
    m->memory->known[i]|=bit;return 1;
}
static int config(gb_model *m,uint32_t *a,uint32_t va) {return scalar(m,GP+84,4,FULL,a,va);}
static int payload(gb_model *m,unsigned offset,uint32_t *v,uint32_t va) {
    return scalar(m,m->payload_address+offset,1,255,v,va);
}
static void remember(gb_model *m,const gb_request *r) {
    m->last_request=*r;
    if(r->buffer&&r->buffer_length<=sizeof(m->boundary_buffer)) {
        memmove(m->boundary_buffer,r->buffer,r->buffer_length);
        memmove(m->boundary_known,r->buffer_known,r->buffer_length);
        m->last_request.buffer=m->boundary_buffer;m->last_request.buffer_known=m->boundary_known;
    } else {m->last_request.buffer=NULL;m->last_request.buffer_known=NULL;}
}
static int call(gb_model *m,gb_call_kind kind,uint32_t target,uint32_t site,
                const uint32_t *args,unsigned count,unsigned abstract_pointer,
                uint8_t *buffer,uint8_t *known,size_t n,gb_scalar *result) {
    gb_request r;unsigned i;gb_scalar discarded={0,0};gb_flow flow;
    if(m->flow==GB_TRANSFER)return 0;
    memset(&r,0,sizeof(r));r.kind=kind;r.target=target;r.callsite=site;r.argument_count=count;
    for(i=0;i<count;i++){r.arguments[i]=args[i];r.known[i]=FULL;}
    if(abstract_pointer<count)r.known[abstract_pointer]=0;
    r.buffer=buffer;r.buffer_known=known;r.buffer_length=n;
    if(!result)result=&discarded;result->value=0;result->known=0;
    remember(m,&r);++m->helper_calls;
    flow=m->backend.invoke?m->backend.invoke(m->backend.context,m,&r,result):GB_HALT;
    remember(m,&r); /* Preserve partial abstract-stack writes at an external boundary. */
    return returned(m,flow,kind==GB_NATIVE_HELPER?target:site,0);
}
static int native(gb_model *m,uint32_t target,uint32_t site,
                  uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3,unsigned argc,gb_scalar *result) {
    const uint32_t args[4]={a0,a1,a2,a3};
    return call(m,GB_NATIVE_HELPER,target,site,args,argc,4,NULL,NULL,0,result);
}
static int need_result(gb_model *m,const gb_scalar *r,uint32_t mask,uint32_t target) {
    if((r->known&mask)==mask)return 1;
    return halt_at(m,m->last_request.kind!=GB_NATIVE_HELPER&&m->last_request.target==target?m->last_request.callsite:target,0);
}
static int allocate(gb_model *m,size_t n,uint32_t site,uint32_t *address) {
    uint32_t args[1];gb_scalar r;args[0]=(uint32_t)n;
    if(!call(m,GB_ROM_ALLOC,112,site,args,1,4,NULL,NULL,0,&r)||!need_result(m,&r,FULL,112))return 0;
    *address=r.value;return 1;
}
static int release(gb_model *m,uint32_t address,uint32_t site) {
    uint32_t args[1];args[0]=address;return call(m,GB_ROM_FREE,104,site,args,1,4,NULL,NULL,0,NULL);
}
static int copy(gb_model *m,uint32_t destination,uint32_t source,size_t n,uint32_t site) {
    const uint32_t args[3]={destination,source,(uint32_t)n};
    return call(m,GB_ROM_COPY,76,site,args,3,4,NULL,NULL,0,NULL);
}
static int zero_local(gb_model *m,uint8_t *d,uint8_t *k,size_t n,uint32_t site) {
    const uint32_t args[3]={0,0,(uint32_t)n};memset(d,0,n);memset(k,0,n);
    return call(m,GB_ROM_ZERO,72,site,args,3,0,d,k,n,NULL);
}
static int cache(gb_model *m,unsigned index,uint8_t *d,uint8_t *k,uint32_t site) {
    const uint32_t args[3]={1,index,0};memset(d,0,12);memset(k,0,12);
    return call(m,GB_NATIVE_HELPER,0x829e,site,args,3,2,d,k,12,NULL);
}
static int schedule(gb_model *m,uint32_t callback,uint32_t delay,uint32_t site) {
    gb_scalar r={0,0};gb_flow flow;if(m->flow==GB_TRANSFER)return 0;++m->schedule_calls;
    flow=m->backend.schedule?m->backend.schedule(m->backend.context,m,callback,0,delay,0,&r):GB_HALT;
    return returned(m,flow,site,callback); /* Native ignores scalar, not flow. */
}
static int reply_local(gb_model *m,uint32_t wrapper,uint8_t command,const uint8_t *d,const uint8_t *k,size_t n) {
    gb_reply_request r;gb_flow flow;if(m->flow==GB_TRANSFER)return 0;memset(&r,0,sizeof(r));r.wrapper_va=wrapper;r.source_address=0;r.handle=m->handle;r.command=command;
    r.data=d;r.known=k;r.length=n;++m->reply_calls;
    flow=m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT;
    return returned(m,flow,wrapper,0);
}
static int reply_byte(gb_model *m,uint8_t command,uint8_t value) {
    const uint8_t known=255;return reply_local(m,0x13d7a,command,&value,&known,1);
}
static int reply_ram(gb_model *m,uint32_t wrapper,uint8_t command,uint32_t address,size_t n) {
    gb_reply_request r;gb_flow flow;if(m->flow==GB_TRANSFER)return 0;if(!in_ram(address,n))return halt_at(m,wrapper,address);memset(&r,0,sizeof(r));
    r.wrapper_va=wrapper;r.source_address=address;r.handle=m->handle;r.command=command;
    r.data=m->memory->ram+address-TF_RAM_BASE;r.known=m->memory->known+address-TF_RAM_BASE;r.length=n;
    ++m->reply_calls;
    flow=m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT;
    return returned(m,flow,wrapper,address);
}
static int auth_slot(gb_model *m,uint16_t handle,unsigned *index,uint32_t va) {
    uint32_t h;
    if(!scalar(m,AUTH+2,2,65535,&h,va))return -1;
    if(h==handle){*index=0;return 1;}
    if(!scalar(m,AUTH+6,2,65535,&h,va))return -1;
    if(h==handle){*index=1;return 1;}return 0;
}
gb_flow gb_registration(gb_model *m,uint16_t h,uint32_t action) {
    if(m->flow==GB_TRANSFER)return m->flow;
    uint32_t v;unsigned index=0;int found;
    m->flow=GB_RETURNED;m->boundary_va=0;m->boundary_address=0;
    if(action==2) {
        if(!scalar(m,AUTH+2,2,65535,&v,0x13c4e))return GB_HALT;
        if(v!=65534){index=1;if(!scalar(m,AUTH+6,2,65535,&v,0x13c5a))return GB_HALT;}
        if(v!=65534)return m->flow;
        if(!write_value(m,AUTH+2+4*index,h,2,0x13c68))return GB_HALT;
    } else {
        found=auth_slot(m,h,&index,0x13c36);if(found<0)return GB_HALT;if(!found)return m->flow;
        if(action==1) {
            if(!write_value(m,AUTH+4+4*index,1,1,0x13c8c))return GB_HALT;
            if(!write_value(m,AUTH+5+4*index,0,1,0x13c90))return GB_HALT;
            return m->flow;
        }
        if(!write_value(m,AUTH+2+4*index,65534,2,0x13ca6))return GB_HALT;
    }
    if(!write_value(m,AUTH+4+4*index,0,1,0x13c6c))return GB_HALT;
    if(!write_value(m,AUTH+5+4*index,0,1,0x13c90))return GB_HALT;
    return m->flow;
}
gb_flow gb_report_mode(gb_model *m,uint16_t h,uint8_t mode) {
    if(m->flow==GB_TRANSFER)return m->flow;
    unsigned i;int found;m->flow=GB_RETURNED;m->boundary_va=0;m->boundary_address=0;
    found=auth_slot(m,h,&i,0x139ba);
    if(found<0)return GB_HALT;if(found&&!write_value(m,AUTH+5+4*i,mode,1,0x139dc))return GB_HALT;
    return m->flow;
}
static int uid_equal(gb_model *m,uint32_t address,uint32_t length,int *equal,uint32_t site) {
    uint8_t uid[14],uk[14],d,k;unsigned i;
    uint32_t args[3]={0,0x1ffff7ec,8};
    *equal=0;if(length!=14)return 1;
    /* Constructor9298 byte path; each ROM call must actually return in the
       supplied backend. OUT buffers represent caller stack, never a fake UID RAM. */
    memset(uid,0,sizeof(uid));memset(uk,0,sizeof(uk));
    if(!call(m,GB_ROM_COPY,76,0x92b4,args,3,0,uid,uk,8,NULL))return 0;
    args[1]=0x1ffff7e8;args[2]=6;
    if(!call(m,GB_ROM_COPY,76,0x92ce,args,3,0,uid+8,uk+8,6,NULL))return 0;
    for(i=0;i<14;i++) {
        bytes(m,address+i,&d,&k,1,site);
        if(((d^uid[i])&(k&uk[i]))!=0)return 1;
        if(k!=255||uk[i]!=255)return halt_at(m,0x92d0,address+i);
    }
    *equal=1;return 1;
}
static int bad_config(gb_model *m) {
    if(!native(m,0x94cc,0x14762,0x94e6,0,1,0,3,NULL))return 0;
    return reply_byte(m,0xbd,0);
}
static int factory(gb_model *m,uint8_t command) {
    if(!native(m,0x13124,0x13e2c,0,0,0,0,0,NULL))return 0;
    if(!schedule(m,0x8e12,100,0x13e40)||!schedule(m,0x99c6,200,0x13e54))return 0;
    return reply_byte(m,command,1);
}
static int command_a3(gb_model *m) {
    uint32_t temp,cfg,v,w;unsigned i;int equal;
    if(m->length!=76)return bad_config(m);
    if(!allocate(m,76,0x140b4,&temp))return 0;if(temp==0)return bad_config(m);
    if(!copy(m,temp,m->payload_address,76,0x140c8))return 0;
    if(!uid_equal(m,temp+4,14,&equal,0x140d0))return 0;
    for(i=36;i<40;i++){if(!scalar(m,temp+i,1,255,&v,0x140e4))return 0;if(v<32||v>126){equal=0;break;}}
    if(!release(m,temp,0x14100))return 0;if(!equal)return bad_config(m);
    if(!config(m,&cfg,0x1410a)||!payload(m,27,&v,0x1410c)||!scalar(m,cfg+3,1,16,&w,0x14110))return 0;
    if(((v^w)&16)!=0&&!native(m,0x9ae0,0x14120,(v>>4)&1,0,0,0,1,NULL))return 0;
    if(!config(m,&cfg,0x14124)||!payload(m,24,&v,0x14126)||!scalar(m,cfg,1,7,&w,0x1412a))return 0;
    if(((v^w)&7)!=0&&!native(m,0xf8f2,0x14134,0,0,0,0,0,NULL))return 0;
    if(!config(m,&cfg,0x14140)||!copy(m,cfg,m->payload_address+24,16,0x14148))return 0;
    if(!config(m,&cfg,0x1414a)||!copy(m,cfg+96,m->payload_address+59,16,0x1415a))return 0;
    if(!native(m,0x12f58,0x1415c,0,0,0,0,0,NULL)||!schedule(m,0x95ec,100,0x14170))return 0;
    if(!native(m,0x13be8,0x14176,0,0,0,0,0,NULL)||!config(m,&cfg,0x1417a)||!scalar(m,cfg+4,1,8,&v,0x1417c))return 0;
    if(v&8)return native(m,0xe096,0x14186,0,0,0,0,0,NULL);return 1;
}
static int command_a8(gb_model *m) {
    static const uint8_t fallback[4]={0x41,0x61,0x42,0x62};uint32_t cfg,v,w;unsigned i;
    if(m->length!=4)return 1;if(!config(m,&cfg,0x13f0a))return 0;
    for(i=0;i<4;i++){
        if(!payload(m,i,&v,0x13f18))return 0;
        if(v==fallback[i])continue;
        if(!scalar(m,cfg+12+i,1,255,&w,0x13f1c))return 0;
        if(v!=w)return reply_byte(m,0xa8,0);
    }
    if(gb_registration(m,m->handle,1)==GB_HALT)return 0;
    return native(m,0x13be8,0x13f48,0,0,0,0,0,NULL);
}
static int command_a9(gb_model *m) {
    uint32_t cfg,v,w;unsigned i;
    if(m->length<=25)return reply_byte(m,0xa9,2);
    if(!config(m,&cfg,0x147d2))return 0;
    for(i=0;i<4;i++){
        if(!payload(m,18+i,&v,0x147e0)||!scalar(m,cfg+12+i,1,255,&w,0x147e4))return 0;
        if(v!=w)return reply_byte(m,0xa9,0);
    }
    if(!copy(m,cfg+12,m->payload_address+22,4,0x14806)||!native(m,0x12f58,0x14808,0,0,0,0,0,NULL))return 0;
    if(gb_registration(m,m->handle,0)==GB_HALT||!reply_byte(m,0xa9,1))return 0;
    return schedule(m,0x8e12,100,0x14830);
}
static int protected_command(gb_model *m) {
    uint32_t eligible;int equal;
    if(!uid_equal(m,m->payload_address,(uint8_t)m->length,&equal,m->leaf))return 0;if(!equal)return 1;
    if(m->command==0xa4)return factory(m,0xa4);
    if(m->command==0xa5) {
        if(!schedule(m,0x8e12,100,0x147a6)||!schedule(m,0x99c6,200,0x147ba))return 0;
        return reply_byte(m,0xa5,1);
    }
    if(!native(m,0x908e,m->command==0xad?0x13f62:0x13f92,0x13d9c,0,0,0,1,NULL))return 0;
    if(!scalar(m,GP+175,1,255,&eligible,m->command==0xad?0x13f66:0x13f96))return 0;
    if(eligible) {
        if(!native(m,0x9e0a,m->command==0xad?0x13f6e:0x13f9e,0,0,0,0,1,NULL))return 0;
        if(m->command==0xae&&!native(m,0xe096,0x13fa2,0,0,0,0,0,NULL))return 0;
    }
    return m->command==0xad?factory(m,0xad):reply_byte(m,0xae,1);
}
static int command_af(gb_model *m) {
    uint32_t h,l,value,cfg,flag;gb_scalar computed;int match;
    if(m->length!=2)return 1;
    if(!native(m,0x908e,0x149fa,0x13d9c,0,0,0,1,NULL)||!payload(m,0,&h,0x149fe)||!payload(m,1,&l,0x14a02))return 0;
    value=(h<<8)|l;
    if(!native(m,0x9312,0x14a0a,0,0,0,0,0,&computed)||!need_result(m,&computed,FULL,0x9312))return 0;
    match=computed.value==value;
    if(match) {
        if(!native(m,0x9e0a,0x14a1a,computed.value,0,0,0,1,NULL)||!config(m,&cfg,0x14a22)||!scalar(m,cfg+4,1,8,&flag,0x14a24))return 0;
        if(flag&8){if(!set_bit(m,cfg+4,8,0,0x14a30)||!native(m,0x12f58,0x14a34,0,0,0,0,0,NULL))return 0;}
        if(!write_value(m,GP+193,0,1,0x820e))return 0;
    }
    return reply_byte(m,0xaf,(uint8_t)match);
}
static int map_command(gb_model *m) {
    uint32_t sub,marker,pointer,v;gb_scalar ready;
    if(m->command==0xab) {
        if(m->length==1){if(!payload(m,0,&sub,0x141cc))return 0;return sub==2?native(m,0x13474,0x141d8,m->handle,0,0,0,1,NULL):1;}
        if(m->length!=256)return 1;
        if(!payload(m,255,&marker,0x14840))return 0;
        if(marker!=90)return reply_byte(m,0xbd,0);
        if(!scalar(m,GP+96,4,FULL,&pointer,0x14854)||!copy(m,pointer,m->payload_address,256,0x1485e))return 0;
        if(!native(m,0x12c5e,0x14860,0,0,0,0,0,NULL)||!native(m,0x13474,0x14866,m->handle,0,0,0,1,NULL))return 0;
        return schedule(m,0x95ec,100,0x1487a);
    }
    if(m->command==0xba) {
        if(m->length==1) {
            if(!payload(m,0,&sub,0x14884))return 0;
            if(sub==1) {
                if(!native(m,0x124e2,0x148a4,0,0,0,0,0,NULL))return 0;
                /* 148AA passes the native source pointer to13CAC. Allocation
                   precedes its actual copy; never freeze the source prematurely. */
                return reply_ram(m,0x13cac,0xba,m->payload_address,1);
            }
            if(sub!=2)return 1;
        } else {
            if(m->length!=256)return 1;if(!payload(m,255,&marker,0x148c2))return 0;
            if(marker!=90)return reply_byte(m,0xbd,0);
            if(!scalar(m,GP+88,4,FULL,&pointer,0x148d6)||!copy(m,pointer,m->payload_address,256,0x148e0)||!native(m,0x12d06,0x148e2,0,0,0,0,0,NULL))return 0;
        }
        if(!native(m,0x124d0,0x148ea,1,0,0,0,2,NULL)||!native(m,0x134e4,0x148f0,m->handle,0,0,0,1,NULL))return 0;
        return m->length==256?schedule(m,0x95ec,100,0x1487a):1;
    }
    if(m->length<=1)return 1;if(!payload(m,0,&sub,0x148fc))return 0;
    if(sub>3)return 1;
    if(!native(m,0x17966,0x14912,0,0,0,0,0,&ready))return 0;
    if(sub==0) {
        if(!payload(m,1,&v,0x149ae))return 0;
        return native(m,0x13554,0x149b4,m->handle,v,0,0,3,NULL);
    }
    if(sub==3) {
        if(!payload(m,1,&v,0x14916)||!native(m,v?0x12ea4:0x12d9a,v?0x1491e:0x149e6,0,0,0,0,0,NULL)||!schedule(m,0x95ec,100,0x14976))return 0;
        if(!payload(m,1,&v,0x149ae))return 0;
        return native(m,0x13554,0x149b4,m->handle,v,0,0,3,NULL);
    }
    if(!need_result(m,&ready,FULL,0x17966))return 0;
    if(ready.value==0) {
        if(!reply_byte(m,0xb9,255))return 0;
        if(sub==2)return 1;
        if(!payload(m,1,&v,0x149ae))return 0;
        return native(m,0x13554,0x149b4,m->handle,v,1,0,3,NULL);
    }
    if(sub==2) {
        uint32_t second;if(!payload(m,2,&second,0x149c2))return 0;
        if(second>35)return 1;if(!payload(m,1,&v,0x149ce)||!native(m,0x1775e,0x149d2,v,second,0,0,2,NULL))return 0;
        return reply_byte(m,0xbb,1);
    }
    if(m->length!=258)return 1;if(!payload(m,257,&marker,0x1493a))return 0;
    if(marker==90) {
        if(!payload(m,1,&v,0x14946)||!scalar(m,GP+(v?104:100),4,FULL,&pointer,0x1495a)||!copy(m,pointer,m->payload_address+2,256,0x14960))return 0;
        if(!native(m,v?0x12e72:0x12d68,v?0x14962:0x1498e,0,0,0,0,0,NULL))return 0;
    } else if(!reply_byte(m,0xbd,0))return 0;
    if(!schedule(m,0x95ec,100,0x14976)||!payload(m,1,&v,0x149ae))return 0;
    return native(m,0x13554,0x149b4,m->handle,v,0,0,3,NULL);
}
static int tx_gate(gb_model *m,unsigned channel,uint32_t *v) {
    uint32_t cfg,flag,count;if(!config(m,&cfg,0x8218)||!scalar(m,cfg+4,1,8,&flag,0x821a))return 0;
    if(flag&8){*v=0;return 1;}if(!scalar(m,GP+193+channel,1,255,&count,0x8232))return 0;*v=count<3;return 1;
}
static int command_c1(gb_model *m) {
    uint32_t g0,g1,g2,type,b0,b1,b2,b3,b4,w;uint8_t d[4],k[4];unsigned i;
    if(!tx_gate(m,0,&g0)||!tx_gate(m,1,&g1)||!tx_gate(m,2,&g2)||
       !scalar(m,0x2000bfb1,1,255,&type,0x8294)||
       !scalar(m,GP+356,1,255,&b4,0x14abe)||!scalar(m,GP+354,1,255,&b2,0x14ac2)||
       !scalar(m,GP+355,1,255,&b3,0x14ace)||!scalar(m,GP+352,1,255,&b0,0x14ad6)||
       !scalar(m,GP+353,1,255,&b1,0x14ada))return 0;
    w=(g0<<31)|(g1<<30)|(g2<<29)|(type<<16)|(b4<<8)|(b2<<3)|b3|(b0<<2)|(b1<<1);
    for(i=0;i<4;i++){d[i]=(uint8_t)(w>>(8*i));k[i]=255;}
    return reply_local(m,0x13960,0xc1,d,k,4);
}
static int local_u(gb_model *m,const uint8_t *d,const uint8_t *k,unsigned offset,unsigned n,uint32_t need,uint32_t *v,uint32_t site) {
    uint32_t known=0;unsigned i;*v=0;
    for(i=0;i<n;i++){*v|=(uint32_t)d[offset+i]<<(8*i);known|=(uint32_t)k[offset+i]<<(8*i);}
    return (known&need)==need?1:halt_at(m,site,offset);
}
static void local_put(uint8_t *d,uint8_t *k,unsigned offset,uint32_t v,unsigned n) {
    unsigned i;for(i=0;i<n;i++){d[offset+i]=(uint8_t)(v>>(8*i));k[offset+i]=255;}
}
static int command_battery(gb_model *m) {
    uint32_t first,pause,v,a,b,w;uint8_t d[29],k[29],c[12],ck[12];gb_scalar r;
    if(!payload(m,0,&first,m->leaf))return 0;if(first!=1)return 1;
    if(gb_report_mode(m,m->handle,m->command==0xd1?4:3)==GB_HALT)return 0;
    if(m->command==0xd1)return 1;
    if(!scalar(m,AUTH,1,255,&pause,0x1426a))return 0;if(pause)return 1;
    if(!zero_local(m,d,k,m->command==0xd2?8:29,m->command==0xd2?0x14286:0x1430e))return 0;
    if(m->command==0xd2) {
        if(!cache(m,4,c,ck,0x1428e))return 0;memcpy(d,c+3,6);memcpy(k,ck+3,6);
        return reply_local(m,0x8cfa,0xd2,d,k,8);
    }
    if(!cache(m,1,c,ck,0x14316))return 0;memcpy(d,c+3,4);memcpy(k,ck+3,4);
    if(!cache(m,11,c,ck,0x14340))return 0;memcpy(d+4,c+3,8);memcpy(k+4,ck+3,8);
    if(!cache(m,5,c,ck,0x14386)||
       !local_u(m,c,ck,0,4,0xfc000000u,&a,0x14394)||!local_u(m,c,ck,4,4,0x000fff3fu,&b,0x14398)||
       !local_u(m,d,k,16,4,FULL,&w,0x143a6))return 0;
    v=((a>>26)|((b&63)<<6))&4095;w=(w&0xf000ffffu)|(v<<16);
    v=(b>>8)&4095;w=(w&0x0fffffffu)|(v<<28);local_put(d,k,16,w,4);local_put(d,k,20,v>>4,1);
    if(!cache(m,6,c,ck,0x143d6))return 0;memcpy(d+12,c+7,2);memcpy(k+12,ck+7,2);memcpy(d+14,c+5,2);memcpy(k+14,ck+5,2);
    if(!cache(m,7,c,ck,0x14400))return 0;memcpy(d+16,c+5,2);memcpy(k+16,ck+5,2);
    if(!cache(m,3,c,ck,0x1441a)||!local_u(m,c,ck,8,2,1023,&v,0x14434)||!local_u(m,d,k,20,4,FULL,&w,0x1442e))return 0;
    w=(w&0xfffc00ffu)|((v&1023)<<8);local_put(d,k,20,w,4);
    if(!native(m,0xd392,0x14440,0,0,0,0,0,&r)||!need_result(m,&r,1023,0xd392))return 0;
    w=(w&0xf003ffffu)|((r.value&1023)<<18);local_put(d,k,20,w,4);
    if(!native(m,0xd31a,0x1445a,0,0,0,0,0,&r)||!need_result(m,&r,511,0xd31a))return 0;
    w=(w&0x3fffffffu)|(r.value<<30);local_put(d,k,20,w,4);
    if(!local_u(m,d,k,24,4,FULL,&a,0x1446e))return 0;
    a=(a&~127u)|((r.value>>2)&127);local_put(d,k,24,a,4);
    if(!native(m,0xd17c,0x1447c,0,0,0,0,0,&r)||!need_result(m,&r,3,0xd17c))return 0;
    w=(w&0xcfffffffu)|((r.value&3)<<28);local_put(d,k,20,w,4);
    if(!native(m,0xd388,0x14494,0,0,0,0,0,&r)||!need_result(m,&r,127,0xd388))return 0;
    a=(a&0xffffc07fu)|((r.value&127)<<7);local_put(d,k,24,a,4);
    if(!native(m,0xff3c,0x144ae,0,0,0,0,0,&r)||!need_result(m,&r,0x03ffffffu,0xff3c))return 0;
    a=(a&0x3fffu)|(r.value<<14);local_put(d,k,24,a,4);local_put(d,k,28,r.value>>18,1);
    return reply_local(m,0x8cfa,0xd0,d,k,29);
}
static int debug_filters(gb_model *m) {
    /* Native arrays alias within [sp+8,sp+144): channel1@8,2@20,0@32.
       Appending past a channel's declared size can overwrite another array. */
    uint8_t data[136],known[136];unsigned offsets[3]={24,0,12},sizes[3]={112,12,12},count[3]={0,0,0},i,channel;
    uint32_t lo,hi,word_count,word;uint8_t counter=0;
    if(!native(m,0x10586,0x1455e,0,0,0,0,0,NULL))return 0;
    if(!scalar(m,m->payload_address+2,2,65535,&word,0x14562))return 0;
    if(word==0||word==4096||word==8192) {
        unsigned selected=word==0?0u:(word==4096?1u:2u);
        if(!native(m,0x128ba,selected==0?0x14576:(selected==1?0x14590:0x1459a),selected,0,0,0,1,NULL))return 0;
        /* Exact selected1 sequence: all1, pause0, pause2; selected2: all2,pause0,pause1. */
        for(i=0;i<3;i++)if(i!=selected) {
            uint32_t site=(i==2||(selected==2&&i==1))?0x14582:(selected==2?0x145a0:0x1457c);
            if(!native(m,0x128ec,site,i,0,0,0,1,NULL))return 0;
        }
        return reply_byte(m,0xbc,1);
    }
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    for(i=0;i<3;i++)if(!zero_local(m,data+offsets[i],known+offsets[i],sizes[i],i==0?0x145b6:(i==1?0x145c0:0x145ce)))return 0;
    word_count=(uint16_t)(m->length-2);word_count>>=1;
    while(counter<word_count) {
        counter=(uint8_t)(counter+1);
        if(!payload(m,2u*counter,&lo,0x14616)||!payload(m,2u*counter+1,&hi,0x14616))return 0;
        word=lo|(hi<<8);
        if(word<=2047)channel=0;
        else if(word&4096)channel=1;
        else if(word&8192)channel=2;
        else continue;
        if(offsets[channel]+count[channel]*2+2>sizeof(data)) {
            const uint32_t args[2]={channel,8+offsets[channel]+count[channel]*2};
            call(m,GB_STACK_BOUNDARY,0,channel==0?0x14628:(channel==1?0x14648:0x14664),args,2,4,NULL,NULL,0,NULL);
            return halt_at(m,channel==0?0x14628:(channel==1?0x14648:0x14664),8+offsets[channel]+count[channel]*2);
        }
        local_put(data,known,offsets[channel]+2*count[channel],word,2);count[channel]=(uint8_t)(count[channel]+1);
    }
    for(i=0;i<3;i++) {
        const uint32_t args[3]={i,0,sizes[i]};
        if(!call(m,GB_NATIVE_HELPER,0x1290a,i==0?0x145f4:(i==1?0x145fe:0x14608),args,3,1,data+offsets[i],known+offsets[i],sizes[i],NULL))return 0;
    }
    return reply_byte(m,0xbc,1);
}
static int command_c0(gb_model *m) {
    uint32_t first,second,v,channel=0;uint16_t n;uint8_t d[12],k[12];unsigned i;
    if(!payload(m,0,&first,0x144e4))return 0;
    if(m->length==1) {
        if(first>2)return 1;
        if(gb_report_mode(m,m->handle,first==0?0:2)==GB_HALT)return 0;
        if(first==0) {
            if(!write_value(m,GP+193,0,1,0x820e))return 0;
            return native(m,0x105c8,0x14524,0,0,0,0,1,NULL);
        }
        for(i=0;i<3;i++)if(!native(m,first==1?0x128ba:0x128ec,(first==1?0x14534:0x14502)+i*6,i,0,0,0,1,NULL))return 0;
        return 1;
    }
    if(first==255) {
        if(!payload(m,1,&second,0x1454e))return 0;
        if(second==255) {
            if(gb_report_mode(m,m->handle,2)==GB_HALT)return 0;
            return debug_filters(m);
        }
    }
    n=(uint16_t)(m->length-2);if(n>8)return 1;
    if(gb_report_mode(m,m->handle,2)==GB_HALT||!native(m,0x10586,0x14684,0,0,0,0,0,NULL))return 0;
    /* Native rereads prefix after10586, allowing shared source aliases. */
    if(!payload(m,0,&first,0x14688)||!payload(m,1,&second,0x1468c))return 0;
    memset(d,0,sizeof(d));memset(k,0,sizeof(k));v=(first<<8)|second;
    local_put(d,k,0,v,2);local_put(d,k,2,n,1);
    {const uint32_t args[3]={0,m->payload_address+2,n};
     if(!call(m,GB_ROM_COPY,76,0x146ae,args,3,0,d+3,k+3,n,NULL))return 0;}
    if(v<=2047){channel=0;local_put(d,k,11,0,1);}
    else {
        if(v&4096){channel=1;local_put(d,k,11,1,1);}
        if(v&8192){channel=2;local_put(d,k,11,2,1);}
        if(!(v&12288)) {
            const uint32_t args[1]={0};gb_request r;
            memset(&r,0,sizeof(r));r.kind=GB_NATIVE_HELPER;r.target=0x8202;r.callsite=0x146c4;
            r.argument_count=1;r.arguments[0]=args[0];r.known[0]=0;remember(m,&r);
            return halt_at(m,0x8202,0);
        }
    }
    if(!write_value(m,GP+193+channel,0,1,0x820e))return 0;
    {const uint32_t args[1]={0};if(!call(m,GB_NATIVE_HELPER,0x12864,0x146ca,args,1,0,d,k,12,NULL))return 0;}
    return reply_byte(m,0xbc,1);
}
static uint32_t leaf_for(uint8_t c) {
    switch(c) {
    case 69:case 83:case 85:case 87:return 0x13ea2;
    case 160:return 0x14032;case 161:return 0x14704;case 162:return 0x14730;
    case 163:return 0x140a2;case 164:return 0x14772;case 165:return 0x14788;
    case 166:return 0x141a8;case 167:return 0x1471e;case 168:return 0x13ef6;
    case 169:return 0x147c8;case 171:return 0x141c6;case 173:return 0x13f4e;
    case 174:return 0x13f7e;case 175:return 0x149ec;case 176:return 0x141fe;
    case 185:return 0x148f6;case 186:return 0x1487e;case 187:return 0x14228;
    case 192:return 0x144e2;case 193:return 0x146ee;case 208:case 210:return 0x14254;
    case 209:return 0x144ce;case 240:return 0x142e2;default:return 0;
    }
}
static int eligibility_command(uint8_t c) {
    return c==161||(c>=163&&c<=167)||c==170||c==171||c==176||
        (c>=185&&c<=187)||c==192||c==193||(c>=208&&c<=210)||c==240;
}
void gb_init(gb_model *m,tf_model *ram,const gb_backend *io) {
    memset(m,0,sizeof(*m));m->memory=ram;if(io)m->backend=*io;m->flow=GB_RETURNED;
}
gb_flow gb_dispatch(gb_model *m,uint16_t handle,uint8_t command,uint32_t address,uint16_t length) {
    if(m->flow==GB_TRANSFER)return m->flow;
    uint32_t v;unsigned index;int found,equal;
    m->flow=GB_RETURNED;m->boundary_va=0;m->boundary_address=0;
    m->handle=handle;m->command=command;m->payload_address=address;m->length=length;
    m->leaf=leaf_for(command);m->recognized=(uint8_t)(m->leaf!=0);
    if(!m->memory){halt_at(m,0x13e6a,0);return m->flow;}
    /* A length outside the proved parser ABI is a host analysis boundary. */
    if(length>1040){halt_at(m,0x13e6a,address);return m->flow;}
    if(command==69||command==83||command==85||command==87) {
        native(m,0x9bac,0x13eaa,handle,command,address,length,4,NULL);return m->flow;
    }
    if(command==168){command_a8(m);return m->flow;}
    if(command==173||command==174){protected_command(m);return m->flow;}
    found=auth_slot(m,handle,&index,0x13ee6);if(found<0)return m->flow;
    if(!found) {
        if(gb_registration(m,handle,2)==GB_HALT)return m->flow;
        v=0;
    } else if(!scalar(m,AUTH+4+4*index,1,255,&v,0x13fba))return m->flow;
    if(!v) {
        if(schedule(m,0x13be8,300,0x13fd4))reply_byte(m,0xa8,255);
        return m->flow;
    }
    if(eligibility_command(command)) {
        if(!scalar(m,GP+175,1,255,&v,0x81aa))return m->flow;
        if(!v){schedule(m,0x13d9c,300,0x14086);return m->flow;}
    }
    switch(command) {
    case 160:
        if(gb_report_mode(m,handle,0)!=GB_HALT)native(m,0x13be8,0x13f48,0,0,0,0,0,NULL);break;
    case 161:if(payload(m,0,&v,0x14704))native(m,0x17048,0x1470e,v!=0,1,0,0,2,NULL);break;
    case 162:
        if(!payload(m,0,&v,0x14730))break;
        if(v>=1&&v<=5&&!native(m,0xb57e,0x14742,v,0,0,0,1,NULL))break;
        if(payload(m,0,&v,0x14746))reply_byte(m,0xa2,(uint8_t)v);break;
    case 163:command_a3(m);break;
    case 164:case 165:protected_command(m);break;
    case 166:if(payload(m,0,&v,0x141a8))native(m,v?0xa58a:0xa5d0,v?0x141b0:0x14716,0,0,0,0,0,NULL);break;
    case 167:if(payload(m,0,&v,0x1471e))native(m,0x1611e,0x14728,handle,167,v,0,3,NULL);break;
    case 169:command_a9(m);break;
    case 171:case 185:case 186:map_command(m);break;
    case 175:command_af(m);break;
    case 176:
        if(!payload(m,0,&v,0x141fe))break;
        if(gb_report_mode(m,handle,(uint8_t)(v==1))==GB_HALT)break;
        if(v==1)native(m,0x13a62,0x14212,0,0,0,0,0,NULL);break;
    case 187:
        if(!payload(m,0,&v,0x14228)||!native(m,0x15378,0x1422c,v,0,0,0,1,NULL))break;
        reply_byte(m,0xbb,1);break;
    case 192:command_c0(m);break;
    case 193:command_c1(m);break;
    case 208:case 209:case 210:
        if(m->backend.report_command)m->flow=m->backend.report_command(m->backend.context,m,handle,command,address,length);
        else command_battery(m);break;
    case 240:
        if(length<14)break;
        if(!uid_equal(m,address,14,&equal,0x142ec)||!equal)break;
        native(m,0x12522,0x14302,handle,address+14,(uint16_t)(length-14),0,3,NULL);break;
    default:break;
    }
    return m->flow;
}
