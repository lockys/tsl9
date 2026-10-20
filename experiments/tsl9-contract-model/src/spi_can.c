#include "spi_can.h"
#include <string.h>
typedef struct {uint32_t v,k;} sv;
static int mode_cleanup(sc_model *,uint32_t);
static int channel0_filters(sc_model *,sc_buffer,uint32_t);
#define FULL UINT32_MAX
static sv value(uint32_t v){sv x={v,FULL};return x;}
static sv narrow(sv x,unsigned bits){uint32_t mask=bits==32?FULL:((UINT32_C(1)<<bits)-1);x.v&=mask;x.k&=mask;return x;}
static sv zero_extend(sv x,unsigned bits){uint32_t mask=bits==32?FULL:((UINT32_C(1)<<bits)-1);x.v&=mask;x.k=(x.k&mask)|~mask;return x;}
static sv and_bits(sv x,uint32_t mask){x.v&=mask;x.k|=~mask;return x;}
static sv or_bits(sv x,uint32_t mask){x.v|=mask;x.k|=mask;return x;}
static sv merge_or(sv a,sv b){sv x;x.v=a.v|b.v;x.k=(a.k&b.k)|(a.v&a.k)|(b.v&b.k);return x;}
static sv left(sv x,unsigned n){x.v<<=n;x.k=(x.k<<n)|((UINT32_C(1)<<n)-1);return x;}
static sv right(sv x,unsigned n){x.v>>=n;x.k=(x.k>>n)|(FULL<<(32-n));return x;}
static int halt(sc_model *m,uint32_t va,uint32_t address){m->flow=SC_HALT;m->unknown_va=va;m->unknown_address=address;return 0;}
static int need(sc_model *m,sv x,uint32_t bits,uint32_t va,uint32_t address){return (x.k&bits)==bits?1:halt(m,va,address);}
static int any(sc_model *m,sv x,uint32_t bits,uint32_t va,uint32_t address,int *out){if(x.v&x.k&bits){*out=1;return 1;}if(!need(m,x,bits,va,address))return 0;*out=0;return 1;}
static int equal(sc_model *m,sv x,uint32_t expected,uint32_t va,uint32_t address,int *out){if((x.v^expected)&x.k){*out=0;return 1;}if(!need(m,x,FULL,va,address))return 0;*out=1;return 1;}
static void result(sc_model *m,sv x){m->result=x.v;m->result_known=x.k;m->result_defined=1;}
static sc_buffer rb(uint32_t address){sc_buffer b;memset(&b,0,sizeof(b));b.kind=SC_RAM;b.address=address;return b;}
static sc_buffer vb(uint8_t *data,uint8_t *known,uint32_t length){sc_buffer b;memset(&b,0,sizeof(b));b.kind=SC_VIEW;b.data=data;b.known=known;b.available=length;return b;}
static sc_buffer sub(sc_buffer b,uint32_t offset){if(b.kind==SC_RAM)b.address+=offset;else if(b.kind==SC_VIEW){if(offset>b.available){b.data=b.known=NULL;b.available=0;}else{if(b.data)b.data+=offset;if(b.known)b.known+=offset;b.available-=offset;}}return b;}
static uint32_t ba(sc_buffer b,uint32_t offset){return b.kind==SC_RAM?b.address+offset:0;}
static int load(sc_model *m,sc_buffer b,uint32_t offset,unsigned n,uint32_t va,sv *out){
    unsigned i;sv x={0,0};uint32_t index;
    for(i=0;i<n;i++){
        if(b.kind==SC_RAM){uint32_t a=b.address+offset+i;if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE)return halt(m,va,a);index=a-TF_RAM_BASE;x.v|=(uint32_t)m->memory->ram[index]<<(8*i);x.k|=(uint32_t)m->memory->known[index]<<(8*i);}
        else{index=offset+i;if(b.kind!=SC_VIEW||!b.data||!b.known||index>=b.available)return halt(m,va,0);x.v|=(uint32_t)b.data[index]<<(8*i);x.k|=(uint32_t)b.known[index]<<(8*i);}
    }
    *out=zero_extend(x,n*8);return 1;
}
static int store(sc_model *m,sc_buffer b,uint32_t offset,unsigned n,uint32_t va,sv x){
    unsigned i;uint32_t index;
    for(i=0;i<n;i++){
        if(b.kind==SC_RAM){uint32_t a=b.address+offset+i;if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE)return halt(m,va,a);index=a-TF_RAM_BASE;m->memory->ram[index]=(uint8_t)(x.v>>(8*i));m->memory->known[index]=(uint8_t)(x.k>>(8*i));}
        else{index=offset+i;if(b.kind!=SC_VIEW||!b.data||!b.known||index>=b.available)return halt(m,va,0);b.data[index]=(uint8_t)(x.v>>(8*i));b.known[index]=(uint8_t)(x.k>>(8*i));}
    }return 1;
}
static void request(sc_request *q,sc_operation op,uint32_t va,uint32_t target,unsigned width){memset(q,0,sizeof(*q));q->operation=op;q->va=va;q->target=target;q->width=width;q->known=FULL;}
static int invoke(sc_model *m,sc_request *q,sc_result *out){
    sc_result r;sc_flow f;if(m->flow!=SC_RETURNED)return 0;m->last_request=*q;
    if(m->last_request.source.kind==SC_VIEW)m->last_request.source.data=m->last_request.source.known=NULL;
    if(m->last_request.destination.kind==SC_VIEW)m->last_request.destination.data=m->last_request.destination.known=NULL;
    ++m->operations;memset(&r,0,sizeof(r));if(!m->backend.invoke)return halt(m,q->va,q->target);
    f=m->backend.invoke(m->backend.context,m,q,&r);
    if(q->operation==SC_INTERRUPT_RETURN){if(f==SC_TRANSFER){m->flow=f;return 0;}return halt(m,q->va,q->target);}
    if(f!=SC_RETURNED){if(f==SC_TRANSFER)m->flow=f;else halt(m,q->va,q->target);return 0;}
    if((q->operation==SC_ROM_COPY||q->operation==SC_ROM_MEMSET)&&!r.memory_effects)return halt(m,q->va,q->target);
    if(out)*out=r;return 1;
}
static int mmio(sc_model *m,uint32_t va,uint32_t target,unsigned width,sv *out){sc_request q;sc_result r;request(&q,SC_MMIO_READ,va,target,width);if(!invoke(m,&q,&r))return 0;out->v=r.value;out->k=r.known;*out=narrow(*out,width);return 1;}
static int write(sc_model *m,uint32_t va,uint32_t target,unsigned width,sv x){sc_request q;x=narrow(x,width);request(&q,SC_MMIO_WRITE,va,target,width);q.value=x.v;q.known=x.k;return invoke(m,&q,NULL);}
static int rom(sc_model *m,uint32_t va,unsigned slot,unsigned count,const sv *args,sv *out){sc_request q;sc_result r;unsigned i;request(&q,SC_ROM_CALL,va,0x40000u+slot,0);q.slot=slot;q.count=count;for(i=0;i<count;i++){q.arguments[i]=args[i].v;q.argument_known[i]=args[i].k;}if(!invoke(m,&q,&r))return 0;if(out){out->v=r.value;out->k=r.known;}return 1;}
static int memory(sc_model *m,uint32_t va,int fill,sc_buffer source,sc_buffer dest,uint32_t length){
    sc_request q;request(&q,fill?SC_ROM_MEMSET:SC_ROM_COPY,va,fill?0x40048:0x4004c,0);q.slot=fill?72:76;if(!fill)q.source=source;q.destination=dest;q.length=length;q.count=fill?2:1;q.arguments[0]=fill?0:length;q.argument_known[0]=FULL;
    if(fill){q.arguments[1]=length;q.argument_known[1]=FULL;}return invoke(m,&q,NULL);
}
static int interrupt_return(sc_model *m,uint32_t va){sc_request q;request(&q,SC_INTERRUPT_RETURN,va,va,0);return invoke(m,&q,NULL);}
static int cs(sc_model *m,uint32_t channel,uint32_t va1,uint32_t va2){if((channel&1)&&!write(m,va1,0x40010814,32,value(16)))return 0;if((channel&2)&&!write(m,va2,0x40010814,32,value(1)))return 0;return 1;}
static int spi(sc_model *m,sv input,sv *out){
    unsigned n;sv x;int ready;
    for(n=255;n;n--){if(!mmio(m,0x16612,0x40013008,16,&x)||!any(m,x,2,0x16616,0x40013008,&ready))return 0;if(ready)break;}
    if(!n){*out=value(0);return 1;}
    if(!write(m,0x1661e,0x4001300c,16,input))return 0;
    for(n=255;n;n--){if(!mmio(m,0x1662a,0x40013008,16,&x)||!any(m,x,1,0x1662e,0x40013008,&ready))return 0;if(ready)break;}
    if(!n){*out=value(0);return 1;}if(!mmio(m,0x16632,0x4001300c,16,out))return 0;*out=and_bits(zero_extend(*out,16),255);return 1;
}
static int block(sc_model *m,uint32_t channel,sv address,sc_buffer source,uint32_t count){
    sv ignored,x;uint32_t i;if(!cs(m,channel,0x1666a,0x16678)||!spi(m,value(2),&ignored)||!spi(m,address,&ignored))return 0;
    for(i=0;i<count;i++){if(!load(m,source,i,1,0x166a6,&x)||!spi(m,x,&ignored))return 0;}
    return write(m,0x1669c,0x40010810,32,value(17));
}
static int modify(sc_model *m,uint32_t channel,sv address,sv mask,sv data){sv ignored;if(!cs(m,channel,0x166c2,0x166d0)||!spi(m,value(5),&ignored)||!spi(m,address,&ignored)||!spi(m,mask,&ignored)||!spi(m,data,&ignored))return 0;return write(m,0x16700,0x40010810,32,value(17));}
static int read_register(sc_model *m,uint32_t channel,sv address,sv *out){sv ignored;if(!cs(m,channel,0x16718,0x16726)||!spi(m,value(3),&ignored)||!spi(m,address,&ignored)||!spi(m,value(0),out))return 0;return write(m,0x16748,0x40010810,32,value(17));}
static int write_register(sc_model *m,uint32_t channel,sv address,sv data){sv ignored;if(!cs(m,channel,0x167b4,0x167c2)||!spi(m,value(2),&ignored)||!spi(m,address,&ignored)||!spi(m,data,&ignored))return 0;return write(m,0x167e8,0x40010810,32,value(17));}
static int time_ms(sc_model *m,uint32_t *out){sv raw;if(!rom(m,0x81ba,124,0,NULL,&raw)||!need(m,raw,FULL,0x81be,0x4007c))return 0;*out=(raw.v*UINT32_C(10))>>4;return 1;}
static int mode(sc_model *m,uint32_t channel,uint32_t desired,sv *out){
    uint32_t start,now,n=0;sv x;int same;
    if(!modify(m,channel,value(15),value(224),value(desired))||!time_ms(m,&start))return 0;
    for(;;){if(n++>=m->spin_budget)return halt(m,0x16774,0x81b0);if(!time_ms(m,&now))return 0;if((uint32_t)(now-start)>5){*out=value(1);return 1;}if(!read_register(m,channel,value(14),&x))return 0;x=and_bits(zero_extend(x,8),224);if(!equal(m,x,desired,0x1679c,0x4001300c,&same))return 0;if(same){*out=value(0);return 1;}}
}
static int reset(sc_model *m,uint32_t channel,sv *out){
    uint32_t start,now,n=0;sv x;int same;
    if(!cs(m,channel,0x16b92,0x16ba2)||!spi(m,value(192),&x)||!write(m,0x16bb4,0x40010810,32,value(17))||!time_ms(m,&start))return 0;
    for(;;){if(n++>=m->spin_budget)return halt(m,0x16bc4,0x81b0);if(!time_ms(m,&now))return 0;if((uint32_t)(now-start)>2){*out=value(1);return 1;}if(!read_register(m,channel,value(14),&x))return 0;x=and_bits(zero_extend(x,8),224);if(!equal(m,x,128,0x16bec,0x4001300c,&same))return 0;if(same){*out=value(0);return 1;}}
}
static int queue(sc_model *m,sv id,sc_buffer source,sv count,sv channel){
    uint32_t i,a;sv old;int occupied;
    for(i=0;i<32;i++){
        a=SC_QUEUE_ADDRESS+i*12;if(!load(m,rb(a),0,2,0x129f8,&old)||!any(m,old,65535,0x12a02,a,&occupied))return 0;if(occupied)continue;
        if(!store(m,rb(a),0,2,0x12a06,id)||!store(m,rb(a),2,1,0x12a0a,count)||!need(m,count,FULL,0x12a1c,0x4004c)||!memory(m,0x12a1c,0,source,rb(a+3),count.v)||!store(m,rb(a),11,1,0x12a1e,channel))return 0;
        ++m->queued;return 1;
    }++m->queue_full;return 1;
}
static int receive(sc_model *m,uint32_t channel,uint32_t address){
    uint8_t data[13],known[13];sc_buffer b=vb(data,known,13);sv x,sidl,dlc,id;unsigned i,c;int rejected,has_good=0,has_bad=0;
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!write(m,0x1680c,0x40010814,32,value(channel==1?16:1))||!spi(m,value(3),&x)||!spi(m,value(address),&x))return 0;
    for(i=0;i<13;i++){if(!spi(m,value(0),&x)||!store(m,b,i,1,0x1682c,x))return 0;}
    if(!write(m,0x1683c,0x40010810,32,value(17)))return 0;
    memcpy(m->received,data,13);memcpy(m->received_known,known,13);m->received_length=13;
    if(!load(m,b,1,1,0x16840,&sidl)||!any(m,sidl,24,0x16848,0,&rejected))return 0;
    if(rejected){++m->rx_rejected;return 1;}
    if(!load(m,b,4,1,0x1684a,&dlc))return 0;dlc=and_bits(dlc,15);
    for(c=0;c<16;c++)if(!((c^dlc.v)&dlc.k&15)){if(c>=1&&c<=8)has_good=1;else has_bad=1;}
    if(has_good&&has_bad)return halt(m,0x1685a,0);
    if(!has_good){++m->rx_rejected;return 1;}
    if(!load(m,b,0,1,0x1685e,&id))return 0;id=merge_or(left(id,3),right(sidl,5));
    return queue(m,id,sub(b,5),dlc,value(channel));
}
static int pending(sc_model *m,uint32_t channel){
    sv flags;int set;if(!read_register(m,channel,value(44),&flags)||!any(m,flags,1,0x16896,0x4001300c,&set))return 0;if(set&&!receive(m,channel,97))return 0;
    if(!any(m,flags,2,0x168a4,0x4001300c,&set))return 0;if(set&&!receive(m,channel,113))return 0;
    return write_register(m,channel,value(44),value(0));
}
static int mask_filter(sc_model *m,uint32_t channel,uint32_t index){uint8_t local[8]={32,36,0,0,255,224,0,0},known[8]={255,255,0,0,255,255,255,255};sv address;if(!load(m,vb(local,known,8),index,1,0x168de,&address))return 0;return block(m,channel,address,vb(local+4,known+4,4),4);}
static int disabled(sc_model *m,uint32_t loadva,uint32_t branchva,int *yes){sv pointer,flags;if(!load(m,rb(TF_GP+84),0,4,loadva,&pointer)||!need(m,pointer,FULL,loadva,TF_GP+84)||!load(m,rb(pointer.v),4,1,loadva+2,&flags))return 0;return any(m,flags,8,branchva,pointer.v+4,yes);}
static int gate(sc_model *m,uint32_t channel,sv *out){sv x;int off;if(!disabled(m,0x8218,0x8222,&off))return 0;if(off||channel>2){*out=value(0);return 1;}if(!load(m,rb(TF_GP+192),channel+1,1,0x8232,&x)||!need(m,x,255,0x8236,TF_GP+193+channel))return 0;*out=value(x.v<3);return 1;}
static int clear11(sc_model *m,sc_buffer dest){unsigned n;for(n=11;n;n--)if(!store(m,dest,n-1,1,0x8562+(11-n)*4,value(0)))return 0;return 1;}
static int send(sc_model *m,sc_buffer frame,sv *out){
    static const uint8_t controls[3]={48,64,80};uint8_t data[48],known[48];sc_buffer payload=vb(data,known,48);sv channel,dlc,id,status,live;unsigned i;int off,busy;
    if(!load(m,frame,11,1,0x168f0,&channel)||!need(m,channel,255,0x168fc,ba(frame,11)))return 0;
    if(((channel.v-1)&255)>1){*out=value(4);return 1;}
    if(!disabled(m,0x16904,0x1690e,&off))return 0;if(off){*out=value(4);return 1;}
    if(!load(m,frame,2,1,0x1691c,&dlc)||!need(m,dlc,255,0x16922,ba(frame,2)))return 0;if(dlc.v>8){*out=value(4);return 1;}
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!clear11(m,sub(payload,2))||!load(m,frame,0,2,0x16946,&id)||
       !store(m,payload,0,1,0x1695a,right(id,3))||!store(m,payload,1,1,0x16956,left(id,5))||
       !store(m,payload,4,1,0x1694a,dlc)||!memory(m,0x1696c,0,sub(frame,3),sub(payload,5),dlc.v))return 0;
    for(i=0;i<3;i++){
        if(!load(m,frame,11,1,0x1697a,&channel)||!need(m,channel,255,0x16980,ba(frame,11))||!read_register(m,channel.v,value(controls[i]),&status)||!any(m,status,8,0x16986,0x4001300c,&busy))return 0;if(busy)continue;
        if(!load(m,frame,2,1,0x16988,&live)||!need(m,live,255,0x16996,ba(frame,2))||!load(m,frame,11,1,0x1698c,&channel)||!need(m,channel,255,0x169a0,ba(frame,11))||
           !block(m,channel.v,value(controls[i]+1),payload,(live.v+5)&255))return 0;
        if(!load(m,frame,11,1,0x169a4,&channel)||!need(m,channel,255,0x169ae,ba(frame,11))||!modify(m,channel.v,value(controls[i]),value(8),value(8)))return 0;
        if(!load(m,frame,11,1,0x169b2,&channel)||!need(m,channel,255,0x169b8,ba(frame,11))||!read_register(m,channel.v,value(controls[i]),&status)||!any(m,status,112,0x169c0,0x4001300c,&busy))return 0;*out=value(busy?4:0);return 1;
    }*out=value(4);return 1;
}
static int reload(sc_model *m,uint32_t channel,uint32_t enable,sv *out){
    uint8_t data[8]={0,0,2,0,4,0,0,0},known[8]={255,255,255,255,255,255,0,0};sv event,task,args[3];uint32_t offset=channel*2;
    if(!load(m,vb(data,known,8),offset,2,enable?0x165ea:0x165fc,&event)||!need(m,event,65535,enable?0x165ea:0x165fc,0)||!load(m,rb(SC_TASK_ADDRESS),0,1,0x165e0,&task))return 0;
    args[0]=task;args[1]=event;args[2]=value(1600);return rom(m,enable?0x165fa:0x16608,enable?556:92,enable?3:2,args,out);
}
static int filters(sc_model *m,uint32_t channel,sc_buffer source,uint32_t count,uint32_t schedule){
    static const uint8_t addresses[6]={0,4,8,16,20,24};uint8_t ids[12],idknown[12],data[4],known[4];sc_buffer ib=vb(ids,idknown,12),packet=vb(data,known,4);sv id,x;unsigned i;
    if(((channel-1)&255)>1)return 1;
    memset(ids,0,sizeof(ids));memset(idknown,0,sizeof(idknown));
    if(!memory(m,0x16a6c,1,rb(0),ib,12)||!memory(m,0x16a84,0,source,ib,count>12?12:(count&255))||!mode(m,channel,128,&x)||
       !write_register(m,channel,value(96),value(32))||!write_register(m,channel,value(112),value(32)))return 0;
    for(i=0;i<6;i++){if(!load(m,ib,i*2,2,0x16ac0,&id))return 0;id=and_bits(id,2047);memset(data,0,sizeof(data));memset(known,255,sizeof(known));
        if(!store(m,packet,0,1,0x16ae8,right(id,3))||!store(m,packet,1,1,0x16ad4,left(id,5))||!block(m,channel,value(addresses[i]),packet,4))return 0;}
    if(!mode(m,channel,0,&x))return 0;return reload(m,channel,schedule,&x);
}
static int clear_filters(sc_model *m,uint32_t channel){uint8_t v[2]={0,0},k[2]={255,255};if(((channel-1)&255)>1)return 1;return filters(m,channel,vb(v,k,2),2,0);}
static int special_filters(sc_model *m,uint32_t channel){uint8_t v[4]={0,0,0,0},k[4]={255,255,255,255};uint32_t id=channel==1?921:(channel==2?880:0);v[0]=(uint8_t)id;v[1]=(uint8_t)(id>>8);return filters(m,channel,vb(v,k,4),4,1);}
static int accept_all(sc_model *m,uint32_t channel){sv x;if(((channel-1)&255)>1)return 1;if(!reload(m,channel,0,&x)||!mode(m,channel,128,&x)||!write_register(m,channel,value(96),value(96))||!write_register(m,channel,value(112),value(96)))return 0;return mode(m,channel,0,&x);}
static int controller_init(sc_model *m,uint32_t channel,sv *out){
    sv cached,ignored;if(!reset(m,channel,&cached))return 0;if(cached.v){*out=cached;return 1;}
    if(!mode(m,channel,128,&ignored)||!write_register(m,channel,value(42),value(0))||!write_register(m,channel,value(41),value(144))||!write_register(m,channel,value(40),value(130))||
       !mask_filter(m,channel,0)||!mask_filter(m,channel,1)||!write_register(m,channel,value(44),value(0))||!write_register(m,channel,value(43),value(3)))return 0;*out=cached;return 1;
}
static int power_after_init(sc_model *m){sv x;int set;if(!load(m,rb(TF_GP+176),0,1,0x9ace,&x)||!any(m,x,255,0x9ad2,TF_GP+176,&set))return 0;if(set)return 1;return write(m,0x9ada,0x40010810,32,value(2));}
static int task(sc_model *m,uint32_t task_id,uint32_t events,sv *out){
    sv count,x,args[3];uint32_t bit,offset;int ok;
    if(events&2){bit=2;offset=361;}else if(events&4){bit=4;offset=362;}else if(events&1){bit=1;offset=0;}else{*out=value(0);return 1;}
    if(bit!=1){
        if(!load(m,rb(TF_GP+offset),0,1,bit==2?0x16c7c:0x16cb8,&count)||!need(m,count,255,bit==2?0x16c80:0x16cbc,TF_GP+offset))return 0;
        count=value((count.v+1)&255);
        if(count.v<=2){if(!store(m,rb(TF_GP+offset),0,1,bit==2?0x16c8c:0x16cc8,count))return 0;*out=value(events^bit);return 1;}
        if(!store(m,rb(TF_GP+offset),0,1,bit==2?0x16ca0:0x16cd4,value(0))||!controller_init(m,bit==2?1:2,&x))return 0;
        if(!x.v&&!special_filters(m,bit==2?1:2))return 0;*out=value(events^bit);return 1;
    }
    if(!controller_init(m,1,&x))return 0;ok=x.v==0;
    if(ok){if(!controller_init(m,2,&x))return 0;ok=x.v==0;}
    if(ok){if(!power_after_init(m)||!mode_cleanup(m,0))return 0;*out=value(events^1u);return 1;}
    args[0]=value(task_id);args[1]=value(1);args[2]=value(48);if(!rom(m,0x16d1e,88,3,args,NULL))return 0;*out=value(events^1u);return 1;
}
static int exti_irq(sc_model *m){
    sv pending,flags;int set;
    if(!mmio(m,0x16d26,0x40010414,32,&pending)||!any(m,pending,64,0x16d32,0x40010414,&set))return 0;
    if(set){if(!write(m,0x16d38,0x40010414,32,value(64))||!load(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d3a,&flags)||!store(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d42,or_bits(flags,1)))return 0;}
    if(!mmio(m,0x16d4a,0x40010414,32,&pending)||!any(m,pending,128,0x16d56,0x40010414,&set))return 0;
    if(set){if(!write(m,0x16d5c,0x40010414,32,value(128))||!load(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d5e,&flags)||!store(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d66,or_bits(flags,2)))return 0;}
    return interrupt_return(m,0x16d6a);
}
static int drain(sc_model *m){
    sv flags;int set;
    if(!load(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d70,&flags)||!any(m,flags,1,0x16d7a,SC_FLAGS_ADDRESS,&set))return 0;
    if(set){if(!store(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d80,and_bits(flags,~1u))||!pending(m,1)||!store(m,rb(SC_FLAGS_ADDRESS+1),0,1,0x16d88,value(0)))return 0;}
    if(!load(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d8c,&flags)||!any(m,flags,2,0x16d94,SC_FLAGS_ADDRESS,&set))return 0;
    if(set){if(!store(m,rb(SC_FLAGS_ADDRESS),0,1,0x16d9a,and_bits(flags,~2u))||!pending(m,2)||!store(m,rb(SC_FLAGS_ADDRESS+2),0,1,0x16da2,value(0)))return 0;}
    return 1;
}
static int gpio(sc_model *m,uint32_t base,uint32_t pins,uint32_t mode_value){
    sv control;uint32_t configuration=(mode_value&15u)|((mode_value&16u)?3u:0u),bits;unsigned half,i;
    for(half=0;half<2;half++){
        if((!half&&!(pins&255))||(half&&pins<=255))continue;
        if(!mmio(m,half?0x18d44:0x18cf8,base+half*4,32,&control))return 0;
        for(i=half*8;i<half*8+8;i++)if(pins&(UINT32_C(1)<<i)){
            bits=15u<<((i%8)*4);control=and_bits(control,~bits);control=or_bits(control,configuration<<((i%8)*4));
            if(mode_value==40&&!write(m,half?0x18d7e:0x18d32,base+20,32,value(UINT32_C(1)<<i)))return 0;
            if(mode_value==72&&!write(m,half?0x18d98:0x18d90,base+16,32,value(UINT32_C(1)<<i)))return 0;
        }
        if(!write(m,half?0x18d88:0x18d3a,base+half*4,32,control))return 0;
    }return 1;
}
static int exti_route(sc_model *m,uint32_t port,uint32_t pin){
    sv x;uint32_t a=0x40010008u+(pin&252u),shift=(pin&3u)*4,clear=~(15u<<shift);
    if(!mmio(m,0x18dac,a,32,&x)||!write(m,0x18dbc,a,32,and_bits(x,clear))||!mmio(m,0x18dbe,a,32,&x))return 0;return write(m,0x18dc6,a,32,or_bits(x,port<<shift));
}
static int exti_init(sc_model *m,uint32_t pins){
    sv x;const uint32_t base=0x40010400;
    if(!mmio(m,0x18b88,base,32,&x)||!write(m,0x18b8e,base,32,and_bits(x,~pins))||
       !mmio(m,0x18b92,base+4,32,&x)||!write(m,0x18b96,base+4,32,and_bits(x,~pins))||
       !mmio(m,0x18b98,base,32,&x)||!write(m,0x18b9e,base,32,or_bits(x,pins))||
       !mmio(m,0x18ba2,base+8,32,&x)||!write(m,0x18baa,base+8,32,and_bits(x,~pins))||
       !mmio(m,0x18bac,base+12,32,&x)||!write(m,0x18bb0,base+12,32,and_bits(x,~pins))||
       !mmio(m,0x18bca,base+12,32,&x)||!write(m,0x18bce,base+12,32,or_bits(x,pins)))return 0;return 1;
}
static int spi_init(sc_model *m){
    sv x;const uint32_t base=0x40013000;
    if(!mmio(m,0x19418,base,16,&x)||!write(m,0x19454,base,16,or_bits(and_bits(zero_extend(x,16),0x3040),0x314))||
       !mmio(m,0x19458,base+28,16,&x)||!write(m,0x19464,base+28,16,and_bits(zero_extend(x,16),0xf7ff))||
       !write(m,0x1946c,base+16,16,value(7))||!mmio(m,0x19472,base,16,&x)||!write(m,0x1947c,base,16,or_bits(x,64)))return 0;return 1;
}
static int peripheral_init(sc_model *m){
    sv x,task,args[2];uint32_t divider;
    if(!memory(m,0x16dc4,1,rb(0),rb(SC_FLAGS_ADDRESS),3))return 0;
    args[0]=value(0x16c6c);if(!rom(m,0x16dd6,128,1,args,&task)||!store(m,rb(SC_TASK_ADDRESS),0,1,0x16ddc,task)||!gpio(m,0x40010c00,256,24))return 0;
    if(!write(m,0x16df2,0x40000828,16,value(0))||
       !mmio(m,0x16df6,0x4000081c,16,&x)||!write(m,0x16e06,0x4000081c,16,or_bits(x,96))||
       !mmio(m,0x16e0a,0x40000820,16,&x)||!write(m,0x16e1a,0x40000820,16,or_bits(x,256))||
       !load(m,rb(TF_GP+112),0,4,0x16e22,&x)||!need(m,x,FULL,0x16e28,TF_GP+112))return 0;
    divider=(x.v/UINT32_C(8000000)-1u)&65535u;
    if(!write(m,0x16e36,0x4000082c,16,value(divider))||!mmio(m,0x16e3a,0x4000082c,16,&x)||!write(m,0x16e40,0x4000083c,16,right(zero_extend(x,16),1))||
       !mmio(m,0x16e44,0x40000800,16,&x)||!write(m,0x16e4c,0x40000800,16,or_bits(x,1))||
       !gpio(m,0x40011000,64,72)||!gpio(m,0x40011000,128,72)||!exti_route(m,2,6)||!exti_route(m,2,7)||!exti_init(m,192)||
       !write(m,0x16e9c,0x40010810,32,value(17))||!gpio(m,0x40010800,16,16)||!gpio(m,0x40010800,1,16)||
       !gpio(m,0x40010800,32,24)||!gpio(m,0x40010800,64,72)||!gpio(m,0x40010800,128,24)||!spi_init(m)||
       !load(m,rb(SC_TASK_ADDRESS),0,1,0x16f12,&task))return 0;
    args[0]=task;args[1]=value(1);return rom(m,0x16f18,80,2,args,NULL);
}
static int can_transmit(sc_model *m,uint32_t base,sc_buffer tx,sv *out){
    static const unsigned lo_offset[4]={12,11,13,14},hi_offset[4]={16,15,17,18};
    static const uint32_t lo_va[4]={0x18a62,0x18a66,0x18a6e,0x18a76},hi_va[4]={0x18a82,0x18a86,0x18a8e,0x18a96};
    sv status,id,ide,rtr,dlc,x,word,byte;unsigned i,mailbox=4;uint32_t a;int set,extended;
    for(i=0;i<3;i++){
        if(!mmio(m,i==0?0x189f8:(i==1?0x18a02:0x18a0c),base+8,32,&status)||!any(m,status,UINT32_C(1)<<(26+i),i==0?0x189fe:(i==1?0x18a08:0x18a14),base+8,&set))return 0;
        if(set){mailbox=i;break;}
    }
    if(mailbox==4){*out=value(4);return 1;}a=base+0x180u+mailbox*16;
    if(!mmio(m,0x18a20,a,32,&x)||!write(m,0x18a26,a,32,and_bits(x,1))||
       !load(m,tx,8,1,0x18a2a,&ide)||!load(m,tx,9,1,0x18a2e,&rtr)||!any(m,ide,255,0x18a32,ba(tx,8),&extended))return 0;
    if(!load(m,tx,extended?4:0,4,extended?0x18aba:0x18a34,&id)||!mmio(m,extended?0x18abc:0x18a36,a,32,&x))return 0;
    id=left(id,extended?3:21);id=merge_or(id,rtr);if(extended)id=merge_or(id,ide);id=merge_or(id,x);
    if(!write(m,0x18a40,a,32,id)||!load(m,tx,10,1,0x18a44,&dlc))return 0;dlc=and_bits(dlc,15);
    if(!store(m,tx,10,1,0x18a4a,dlc)||!mmio(m,0x18a4e,a+4,32,&x)||!write(m,0x18a54,a+4,32,and_bits(x,~15u))||
       !mmio(m,0x18a58,a+4,32,&x)||!write(m,0x18a5e,a+4,32,merge_or(x,dlc)))return 0;
    word=value(0);for(i=0;i<4;i++){if(!load(m,tx,lo_offset[i],1,lo_va[i],&byte))return 0;word=merge_or(word,left(byte,(lo_offset[i]-11)*8));}
    if(!write(m,0x18a7e,a+8,32,word))return 0;
    word=value(0);for(i=0;i<4;i++){if(!load(m,tx,hi_offset[i],1,hi_va[i],&byte))return 0;word=merge_or(word,left(byte,(hi_offset[i]-15)*8));}
    if(!write(m,0x18a9e,a+12,32,word)||!mmio(m,0x18aa2,a,32,&x)||!write(m,0x18aaa,a,32,or_bits(x,1)))return 0;*out=value(mailbox);return 1;
}
static int route_send(sc_model *m,sc_buffer frame){
    uint8_t data[32],known[32];sc_buffer b=vb(data,known,32);sv admitted,channel,id,len,out;
    if(!gate(m,0,&admitted))return 0;if(!admitted.v)return 1;
    if(!load(m,frame,11,1,0x12874,&channel)||!need(m,channel,255,0x12878,ba(frame,11)))return 0;if(channel.v)return send(m,frame,&out);
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!load(m,frame,0,2,0x1287a,&id)||!load(m,frame,2,1,0x1287e,&len)||!store(m,b,8,2,0x12882,value(0))||!store(m,b,0,4,0x12886,id)||
       !store(m,b,10,1,0x12888,len)||!need(m,len,255,0x1289a,ba(frame,2))||!memory(m,0x1289a,0,sub(frame,3),sub(b,11),len.v))return 0;
    return can_transmit(m,0x40006400,b,&out);
}
static int can_receive(sc_model *m,uint32_t base,uint32_t fifo,sc_buffer dest){
    uint32_t a=base+0x1b0u+fifo*16;sv x,ide;unsigned i;int ext;static const uint32_t lo_va[4]={0x18b04,0x18b0c,0x18b16,0x18b20},hi_va[4]={0x18b2a,0x18b32,0x18b3c,0x18b46},lo_store[4]={0x18b08,0x18b12,0x18b1c,0x18b26},hi_store[4]={0x18b2e,0x18b38,0x18b42,0x18b4c};
    if(!mmio(m,0x18ad2,a,32,&ide))return 0;ide=and_bits(ide,4);
    if(!store(m,dest,8,1,0x18ad8,ide)||!any(m,ide,4,0x18adc,a,&ext)||!mmio(m,ext?0x18b5c:0x18ade,a,32,&x)||!store(m,dest,ext?4:0,4,ext?0x18b62:0x18ae4,right(x,ext?3:21))||
       !mmio(m,0x18ae6,a,32,&x)||!store(m,dest,9,1,0x18aec,and_bits(x,2))||
       !mmio(m,0x18af0,a+4,32,&x)||!store(m,dest,10,1,0x18af6,and_bits(x,15))||
       !mmio(m,0x18afa,a+4,32,&x)||!store(m,dest,19,1,0x18b00,right(x,8)))return 0;
    for(i=0;i<4;i++){if(!mmio(m,lo_va[i],a+8,32,&x)||!store(m,dest,11+i,1,lo_store[i],i?right(x,i*8):x))return 0;}
    for(i=0;i<4;i++){if(!mmio(m,hi_va[i],a+12,32,&x)||!store(m,dest,15+i,1,hi_store[i],i?right(x,i*8):x))return 0;}
    if(!mmio(m,fifo?0x18b66:0x18b52,base+(fifo?16:12),32,&x))return 0;return write(m,fifo?0x18b6c:0x18b58,base+(fifo?16:12),32,or_bits(x,32));
}
static int can_irq(sc_model *m){
    uint8_t data[20],known[20];sc_buffer b=vb(data,known,20);sv status,id,len;int pending_flag;
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!mmio(m,0x12a3c,0x4000640c,32,&status)||!any(m,status,3,0x12a40,0x4000640c,&pending_flag))return 0;if(!pending_flag)return interrupt_return(m,0x12a64);
    if(!can_receive(m,0x40006400,0,b))return 0;memcpy(m->received,data,20);memcpy(m->received_known,known,20);m->received_length=20;
    if(!load(m,b,0,2,0x12a50,&id)||!load(m,b,10,1,0x12a4c,&len)||!queue(m,id,sub(b,11),len,value(0)))return 0;
    return interrupt_return(m,0x12a60);
}

/* R16: native callers are expanded down to the existing primitive provider.
   Internal stack descriptors are views, not invented native addresses. */
static int image_load(sc_model *m,uint32_t address,unsigned n,uint32_t va,sv *out){
    unsigned i;uint32_t at;if(address<0x8000||!m->memory->runtime)return halt(m,va,address);at=address-0x8000;
    for(i=0;i<n;i++)if(at+i>=m->memory->runtime_length)return halt(m,va,address+i);
    *out=value(0);for(i=0;i<n;i++)out->v|=(uint32_t)m->memory->runtime[at+i]<<(i*8);return 1;
}
static int cancel_callback(sc_model *m,uint32_t callback,sv *out){
    const uint32_t base=TF_RAM_BASE+0xbe08;uint32_t i,a;sv found,pointer,args[2];int same,nz;
    for(i=0;i<15;i++){
        a=base+i*12;if(!load(m,rb(a),4,4,0x90a4,&found)||!equal(m,found,callback,0x90a6,a+4,&same))return 0;if(!same)continue;
        if(!load(m,rb(a),8,4,0x90b2,&pointer)||!any(m,pointer,FULL,0x90b4,a+8,&nz))return 0;
        if(nz){args[0]=pointer;if(!rom(m,0x90bc,104,1,args,NULL))return 0;}
        /* gp174 is reread after free, before callback/argument stores. */
        if(!load(m,rb(TF_GP+174),0,1,0x90d0,&args[0])||
           !store(m,rb(a),4,4,0x90dc,value(0))||!store(m,rb(a),8,4,0x90e0,value(0)))return 0;
        args[1]=value((UINT32_C(1)<<i)&65535);return rom(m,0x90ec,92,2,args,out);
    }*out=value(1);return 1;
}
static int state_cleanup(sc_model *m){sv ignored;
    if(!memory(m,0xfef4,1,rb(0),rb(TF_GP+300),3)||
       !store(m,rb(TF_RAM_BASE+0xbfb4),0,1,0x1049e,value(0))||!cancel_callback(m,0x1049a,&ignored)||
       !memory(m,0x105a6,1,rb(0),rb(TF_RAM_BASE+0xbfb4),12)||!power_after_init(m)||
       !cancel_callback(m,0x9b14,&ignored)||!cancel_callback(m,0x1063c,&ignored))return 0;
    return 1;
}
static int native_filter(sc_model *m,sc_buffer d){
    const uint32_t base=0x40006400;uint32_t bits,bank_address;sv x,bank,scale,a,b,c,word,fifo,active;int zero,one,nz;
    if(!mmio(m,0x188fe,base+512,32,&x)||!load(m,d,10,1,0x18902,&bank)||
       !write(m,0x1890c,base+512,32,or_bits(x,1))||!mmio(m,0x18910,base+540,32,&x)||
       !need(m,bank,31,0x18914,ba(d,10)))return 0;
    bits=UINT32_C(1)<<(bank.v&31);
    if(!write(m,0x1891e,base+540,32,and_bits(x,~bits))||!load(m,d,12,1,0x18922,&scale)||
       !equal(m,scale,0,0x18926,ba(d,12),&zero))return 0;
    if(zero){
        if(!mmio(m,0x18928,base+524,32,&x)||!load(m,d,2,2,0x1892c,&a)||
           !write(m,0x18934,base+524,32,and_bits(x,~bits))||!load(m,d,6,2,0x18938,&b)||!load(m,d,4,2,0x1893e,&c)||
           !need(m,bank,255,0x18948,ba(d,10)))return 0;
        bank_address=base+bank.v*8;word=merge_or(a,left(b,16));
        if(!write(m,0x18948,bank_address+576,32,word)||!load(m,d,0,2,0x1894c,&a)||
           !write(m,0x18954,bank_address+580,32,merge_or(left(c,16),a)))return 0;
    }else{
        if(!equal(m,scale,1,0x189ae,ba(d,12),&one))return 0;
        if(one){
            if(!mmio(m,0x189b2,base+524,32,&x)||!load(m,d,2,2,0x189b6,&a)||
               !write(m,0x189be,base+524,32,or_bits(x,bits))||!load(m,d,0,2,0x189c2,&b)||!load(m,d,4,2,0x189c8,&c)||
               !need(m,bank,255,0x189d2,ba(d,10)))return 0;
            bank_address=base+bank.v*8;
            if(!write(m,0x189d2,bank_address+576,32,merge_or(left(b,16),a))||!load(m,d,6,2,0x189d8,&a)||
               !write(m,0x18954,bank_address+580,32,merge_or(left(c,16),a)))return 0;
        }
    }
    if(!load(m,d,11,1,0x18958,&x)||!any(m,x,255,0x18964,ba(d,11),&nz))return 0;
    if(!mmio(m,nz?0x189de:0x18966,base+516,32,&x)||!write(m,0x1896c,base+516,32,nz?or_bits(x,bits):and_bits(x,~bits))||
       !load(m,d,8,2,0x18970,&fifo)||!any(m,fifo,65535,0x1897c,ba(d,8),&nz))return 0;
    if(!nz){if(!mmio(m,0x1897e,base+532,32,&x)||!write(m,0x18984,base+532,32,and_bits(x,~bits)))return 0;}
    else{if(!equal(m,fifo,1,0x189e8,ba(d,8),&one))return 0;if(one&&(!mmio(m,0x189ec,base+532,32,&x)||!write(m,0x189f2,base+532,32,or_bits(x,bits))))return 0;}
    if(!load(m,d,16,4,0x18988,&active)||!equal(m,active,1,0x1898c,ba(d,16),&one))return 0;
    if(one&&(!mmio(m,0x18994,base+540,32,&x)||!write(m,0x1899a,base+540,32,or_bits(x,bits))))return 0;
    if(!mmio(m,0x189a2,base+512,32,&x))return 0;return write(m,0x189a8,base+512,32,and_bits(x,~1u));
}
static int channel0_apply(sc_model *m,sc_buffer ids,int clearing){
    uint8_t descriptor[20],known[20];sc_buffer d=vb(descriptor,known,20);sv id[4];unsigned bank,i;static const uint32_t loadva[4]={0x127c8,0x127cc,0x127d0,0x127d4};
    static const uint32_t storeva[4]={0x127f4,0x127f8,0x127fc,0x12800};
    for(bank=0;bank<14;bank++){
        memset(descriptor,0,sizeof(descriptor));memset(known,0,sizeof(known));
        if(!clearing)for(i=0;i<4;i++)if(!load(m,ids,bank*8+i*2,2,loadva[i],&id[i]))return 0;
        if(!store(m,d,8,4,clearing?0x12834:0x127d8,value(0))||!store(m,d,10,1,clearing?0x12836:0x127da,value(bank))||
           !store(m,d,12,4,clearing?0x12842:0x127ee,value(0))||!store(m,d,11,1,clearing?0x12844:0x127f0,value(1)))return 0;
        if(clearing){if(!store(m,d,0,4,0x12848,value(0))||!store(m,d,4,4,0x1284a,value(0)))return 0;}
        else for(i=0;i<4;i++)if(!store(m,d,i*2,2,storeva[i],left(id[i],5)))return 0;
        if(!store(m,d,16,4,clearing?0x1284c:0x12804,value(1))||!native_filter(m,d))return 0;
    }return 1;
}
static int channel0_filters(sc_model *m,sc_buffer source,uint32_t count){
    uint8_t data[112],known[112];sc_buffer ids=vb(data,known,112);memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!memory(m,0x127a0,1,rb(0),ids,112)||!memory(m,0x127bc,0,source,ids,count>112?112:(count&255)))return 0;
    return channel0_apply(m,ids,0);
}
static int channel0_clear(sc_model *m){sc_buffer none;memset(&none,0,sizeof(none));return channel0_apply(m,none,1);}
static int route_clear(sc_model *m,uint32_t channel){if(!state_cleanup(m))return 0;return channel?clear_filters(m,channel):channel0_clear(m);}
/* Only native19944's actual caller here: SP16 aligned view, immutable ROM199FC,
   count110, no alias. All nine-word batch reads/store order and the two-byte
   tail are explicit. This does not export a guessed general memcpy contract. */
static int copy_fixed_ids(sc_model *m,sc_buffer dest){
    static const uint32_t reads[8]={0x19994,0x19998,0x1999c,0x199a0,0x199a4,0x199a8,0x199ac,0x199b0};
    static const uint32_t writes[8]={0x199c0,0x199c4,0x199c8,0x199cc,0x199d0,0x199d4,0x199d8,0x199e0};
    sv words[9],byte;unsigned offset,i;
    for(offset=0;offset<76;offset+=36){
        for(i=0;i<8;i++)if(!image_load(m,0x199fc+offset+i*4,4,reads[i],&words[i]))return 0;
        if(!store(m,dest,offset,4,0x199b8,words[0])||!image_load(m,0x19a1c+offset,4,0x199bc,&words[8]))return 0;
        for(i=1;i<9;i++)if(!store(m,dest,offset+i*4,4,writes[i-1],words[i]))return 0;
    }
    for(;offset<110;offset++)if(!image_load(m,0x199fc+offset,1,0x1995c,&byte)||!store(m,dest,offset,1,0x19964,byte))return 0;
    return 1;
}
static int mode_cleanup(sc_model *m,uint32_t mode_value){
    uint8_t data[112],known[112],external[2]={1,0},external_known[2]={255,255};sc_buffer ids=vb(data,known,112);sv table,word,half;uint32_t target;
    memset(data,0,sizeof(data));memset(known,0,sizeof(known));
    if(!state_cleanup(m)||!channel0_clear(m)||!route_clear(m,1)||!route_clear(m,2))return 0;
    if(mode_value>6)return 1;
    if(!image_load(m,0x1a318+mode_value*4,4,0x1294a,&table))return 0;target=0x1a318+table.v;
    switch(target){
    case 0x12950:
        if(!store(m,ids,0,4,0x1295c,value(0x03e90334))||!channel0_filters(m,ids,4))return 0;
        return filters(m,1,vb(external,external_known,2),2,0);
    case 0x1297a:
        if(!copy_fixed_ids(m,ids)||!channel0_filters(m,ids,110)||!special_filters(m,1)||!special_filters(m,2))return 0;return 1;
    case 0x129a4:word=value(0x049800a9);break;
    case 0x129b8:word=value(0x021c00a9);break;
    case 0x129be:case 0x129d2:
        if(!load(m,rb(TF_GP+(target==0x129be?120:128)),0,4,0x129c2,&word)||
           !load(m,rb(TF_GP+(target==0x129be?120:128)),4,2,0x129c4,&half)||
           !store(m,ids,0,4,0x129ca,word)||!store(m,ids,4,2,0x129cc,half))return 0;
        return channel0_filters(m,ids,6);
    default:return halt(m,0x1294e,target);
    }
    if(!store(m,ids,0,4,0x129ac,word))return 0;return channel0_filters(m,ids,4);
}

void sc_init(sc_model *m,tf_model *ram,const sc_backend *b){memset(m,0,sizeof(*m));m->memory=ram;if(b)m->backend=*b;m->spin_budget=65536;}
void sc_resume(sc_model *m){m->flow=SC_RETURNED;m->unknown_va=m->unknown_address=0;m->result_defined=0;}
sc_flow sc_run(sc_model *m,uint32_t entry,const sc_arguments *input){
    sc_arguments empty;const sc_arguments *a=input;sv out={0,0};int ok=0,defined=0;if(m->flow!=SC_RETURNED)return m->flow;
    m->result_defined=0;m->result_known=0;m->received_length=0;m->unknown_va=m->unknown_address=0;if(!m->memory){halt(m,entry,0);return m->flow;}if(!a){memset(&empty,0,sizeof(empty));a=&empty;}
    switch(entry){
    case SC_TIME_MS:{uint32_t now;ok=time_ms(m,&now);out=value(ok?now:0);defined=1;break;}
    case SC_GATE:ok=gate(m,a->registers[0],&out);defined=1;break;
    case SC_SPI_BYTE:ok=spi(m,value(a->registers[0]),&out);defined=1;break;
    case SC_WRITE_BYTES:ok=block(m,a->registers[0],value(a->registers[1]),a->buffer,a->registers[3]);break;
    case SC_MODIFY:ok=modify(m,a->registers[0],value(a->registers[1]),value(a->registers[2]),value(a->registers[3]));break;
    case SC_READ_REGISTER:ok=read_register(m,a->registers[0],value(a->registers[1]),&out);defined=1;break;
    case SC_SET_MODE:ok=mode(m,a->registers[0],a->registers[1],&out);defined=1;break;
    case SC_WRITE_REGISTER:ok=write_register(m,a->registers[0],value(a->registers[1]),value(a->registers[2]));break;
    case SC_RECEIVE_BUFFER:ok=receive(m,a->registers[0],a->registers[1]);break;
    case SC_RECEIVE_PENDING:ok=pending(m,a->registers[0]);break;
    case SC_SET_MASK:ok=mask_filter(m,a->registers[0],a->registers[1]);break;
    case SC_SEND:ok=send(m,a->buffer,&out);defined=1;break;
    case SC_RELOAD:ok=reload(m,a->registers[0],a->registers[1],&out);defined=1;break;
    case SC_ACCEPT_ALL:ok=accept_all(m,a->registers[0]);break;
    case SC_FILTERS:ok=filters(m,a->registers[0],a->buffer,a->registers[2],a->registers[3]);break;
    case SC_CLEAR_FILTERS:ok=clear_filters(m,a->registers[0]);break;
    case SC_SPECIAL_FILTERS:ok=special_filters(m,a->registers[0]);break;
    case SC_RESET:ok=reset(m,a->registers[0],&out);defined=1;break;
    case SC_CONTROLLER_INIT:ok=controller_init(m,a->registers[0],&out);defined=1;break;
    case SC_TASK:ok=task(m,a->registers[0],a->registers[1],&out);defined=1;break;
    case SC_EXTI_IRQ:ok=exti_irq(m);break;
    case SC_DRAIN:ok=drain(m);break;
    case SC_PERIPHERAL_INIT:ok=peripheral_init(m);break;
    case SC_QUEUE:ok=queue(m,value(a->registers[0]),a->buffer,value(a->registers[2]),value(a->registers[3]));break;
    case SC_ROUTE_SEND:ok=route_send(m,a->buffer);break;
    case SC_ROUTE_FILTERS:if(!a->registers[0])ok=channel0_filters(m,a->buffer,a->registers[2]);else ok=filters(m,a->registers[0],a->buffer,a->registers[2],0);break;
    case SC_CAN_TRANSMIT:ok=can_transmit(m,a->registers[0],a->buffer,&out);defined=1;break;
    case SC_CAN_RECEIVE:ok=can_receive(m,a->registers[0],a->registers[1],a->buffer);break;
    case SC_CAN_FIFO0_IRQ:ok=can_irq(m);break;
    case SC_CHANNEL0_FILTERS:ok=channel0_filters(m,a->buffer,a->registers[1]);break;
    case SC_CHANNEL0_CLEAR:ok=channel0_clear(m);break;
    case SC_ROUTE_CLEAR:ok=route_clear(m,a->registers[0]);break;
    case SC_MODE_CLEANUP:ok=mode_cleanup(m,a->registers[0]);break;
    case SC_NATIVE_FILTER_INIT:ok=native_filter(m,a->buffer);break;
    case SC_STATE_CLEANUP:ok=state_cleanup(m);break;
    case SC_CANCEL_CALLBACK:ok=cancel_callback(m,a->registers[0],&out);defined=1;break;
    default:ok=halt(m,entry,entry);break;
    }
    if(ok&&defined&&m->flow==SC_RETURNED)result(m,out);return m->flow;
}


