/* Offline interpretation of ninth-round source contracts. No hardware access.
   Address checks model missing evidence; they do not add native validation. */
#include "feature.h"
#include <string.h>
#define RA(x) (TF_RAM_BASE+UINT32_C(x))
static void unknown(tf_model *m,uint32_t va,uint32_t address){m->unknown_effects++;m->last_unknown_va=va;m->last_unknown_address=address;}
static int read8(tf_model *m,uint32_t a,uint32_t va,uint8_t *v){
    if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE||m->known[a-TF_RAM_BASE]!=255){unknown(m,va,a);return 0;}
    *v=m->ram[a-TF_RAM_BASE];return 1;
}
static void put8(tf_model *m,uint32_t a,uint8_t v){if(a>=TF_RAM_BASE&&a-TF_RAM_BASE<TF_RAM_SIZE){m->ram[a-TF_RAM_BASE]=v;m->known[a-TF_RAM_BASE]=255;}else unknown(m,0,a);}
static int read32(tf_model *m,uint32_t a,uint32_t va,uint32_t *v){unsigned i;uint8_t b;uint32_t n=0;for(i=0;i<4;i++){if(!read8(m,a+i,va,&b))return 0;n|=(uint32_t)b<<(i*8);}*v=n;return 1;}
static void put32(tf_model *m,uint32_t a,uint32_t v){unsigned i;for(i=0;i<4;i++)put8(m,a+i,(uint8_t)(v>>(i*8)));}
static int config(tf_model *m,unsigned i,uint32_t va,uint8_t *v){uint32_t p;if(!read32(m,TF_GP+84,va,&p))return 0;return read8(m,p+i,va,v);}
static void replace_known(tf_frame *f,unsigned i,uint8_t keep,uint8_t force,uint8_t force_known){
    uint8_t old=(uint8_t)(f->value[i]&keep),old_known=(uint8_t)((f->known[i]&keep)|(uint8_t)~keep);
    f->value[i]=(uint8_t)(old|force);
    f->known[i]=(uint8_t)((old_known&force_known)|(old_known&old)|(force_known&force));
}
static void replace(tf_frame *f,unsigned i,uint8_t keep,uint8_t force){replace_known(f,i,keep,force,255);}
static int frame_bits(tf_model *m,const tf_frame *f,unsigned i,uint8_t mask,uint32_t va){if(i>=f->available||(f->known[i]&mask)!=mask){unknown(m,va,i);return 0;}return 1;}
static uint8_t image_byte(tf_model *m,uint32_t va,uint32_t source,uint8_t *mask){
    if(va>=0x8000&&va-0x8000<m->runtime_length){*mask=255;return m->runtime[va-0x8000];}
    *mask=0;unknown(m,source,va);return 0;
}
static void cached(tf_model *m,unsigned slot,tf_frame *f){unsigned i;uint32_t a=RA(0xc1b4)+12u*slot;memset(f,0,sizeof(*f));f->available=12;for(i=0;i<12;i++){f->value[i]=m->ram[a-TF_RAM_BASE+i];f->known[i]=m->known[a-TF_RAM_BASE+i];}}
static void transmit(tf_model *m,const tf_frame *f){
    uint8_t cfg,n;int result;m->tx_requests++;m->last_tx=*f;
    if(!config(m,4,0x12864,&cfg)||!read8(m,TF_GP+193,0x12864,&n))return;
    if((cfg&8)||n>=3){m->tx_gate_refused++;return;}
    if(!frame_bits(m,f,11,255,0x12864))return;
    result=m->backend.tx?m->backend.tx(m->backend.context,f):TF_UNKNOWN;
    if(result==1)m->tx_accepted++;else if(result==TF_UNKNOWN)unknown(m,0x12864,0);
}
static int rom_request(tf_model *m,unsigned off,unsigned slot,uint32_t ticks){
    uint8_t task;int result;m->schedule_requests++;m->last_ticks=ticks;m->last_rom_offset=off;
    if(!read8(m,TF_GP+174,0x9102,&task))return TF_UNKNOWN;
    result=m->backend.rom_status?m->backend.rom_status(m->backend.context,off,task,(uint16_t)(1u<<slot),ticks):TF_UNKNOWN;
    if(result==TF_UNKNOWN)unknown(m,0x9102,0x40000u+off);return result;
}
void tf_init(tf_model *m,const uint8_t *runtime,size_t length,const tf_backend *backend){
    memset(m,0,sizeof(*m));m->runtime=runtime;m->runtime_length=length;if(backend)m->backend=*backend;
    if(runtime&&length>=0x12868){memcpy(m->ram+0x4000,runtime+0x127e0,136);memset(m->known+0x4000,255,136);}
    else unknown(m,0x18422,0x1a7e0);
    memset(m->ram+0x4088,0,0xc950-0x4088);memset(m->known+0x4088,255,0xc950-0x4088);
}
int tf_schedule(tf_model *m,uint32_t cb,uint32_t mode,uint32_t delay,uint32_t argument){
    unsigned i,chosen=15;uint32_t old,a;int matched=0;
    if(delay==0){
        for(i=0;i<15;i++){a=TF_REGISTRY+12u*i;if(!read32(m,a+4,0x9120,&old))return TF_UNKNOWN;if(old==0){put32(m,a+4,cb);put8(m,a,0);put32(m,a+8,argument);return rom_request(m,80,i,0);}}
    }
    for(i=0;i<15;i++){a=TF_REGISTRY+12u*i;if(!read32(m,a+4,0x917a,&old))return TF_UNKNOWN;if(old==cb){chosen=i;matched=1;break;}}
    if(chosen==15)for(i=0;i<15;i++){a=TF_REGISTRY+12u*i;if(!read32(m,a+4,0x91e0,&old))return TF_UNKNOWN;if(old==0){chosen=i;put32(m,a+4,cb);break;}}
    if(chosen==15)return 1;
    a=TF_REGISTRY+12u*chosen;
    if(matched){if(!read32(m,a+8,0x9188,&old))return TF_UNKNOWN;if(old!=0){m->free_requests++;if(m->backend.free_argument&&m->backend.free_argument(m->backend.context,old)!=1){unknown(m,0x9192,old);return TF_UNKNOWN;}}}
    put8(m,a,(uint8_t)mode);put32(m,a+8,argument);
    {uint32_t ticks=(delay*UINT32_C(1000))/625u;int result=rom_request(m,mode?556u:88u,chosen,ticks);return result==TF_UNKNOWN?TF_UNKNOWN:(mode?result:(result==0));}
}
int tf_cancel(tf_model *m,uint32_t cb){
    unsigned i;uint32_t a,old;uint8_t task;int result;
    for(i=0;i<15;i++){
        a=TF_REGISTRY+12u*i;if(!read32(m,a+4,0x90a4,&old))return TF_UNKNOWN;
        if(old==cb){if(!read32(m,a+8,0x90b0,&old))return TF_UNKNOWN;if(old){m->free_requests++;if(m->backend.free_argument&&m->backend.free_argument(m->backend.context,old)!=1){unknown(m,0x90bc,old);return TF_UNKNOWN;}}put32(m,a+4,0);put32(m,a+8,0);
            if(!read8(m,TF_GP+174,0x90d0,&task))return TF_UNKNOWN;
            result=m->backend.rom_status?m->backend.rom_status(m->backend.context,92,task,(uint16_t)(1u<<i),0):TF_UNKNOWN;
            if(result==TF_UNKNOWN)unknown(m,0x90ec,0x4005c);return result;}
    }return 1;
}
static void deliver(tf_model *m,uint32_t cb,uint32_t argument);
uint16_t tf_dispatch(tf_model *m,uint16_t events){
    unsigned i;uint32_t a,cb,arg;uint8_t mode;
    for(i=0;i<15;i++)if(events&(1u<<i)){
        a=TF_REGISTRY+12u*i;
        if(read32(m,a+4,0x901a,&cb)&&cb!=0&&read32(m,a+8,0x9028,&arg)&&read8(m,a,0x9024,&mode)){
            if(mode==0){put32(m,a+4,0);put32(m,a+8,0);}deliver(m,cb,arg);
        }return (uint16_t)(events^(1u<<i));
    }return 0; /* 9054: no dispatchable slot bit returns zero, including bit15-only input. */
}
int64_t tf_hold(tf_model *m,uint32_t threshold,uint32_t active,uint32_t latch,uint32_t started,uint32_t now){
    uint8_t state;uint32_t start;if(threshold==0)return 0;
    if(!read8(m,latch,0xd6f2,&state))return TF_UNKNOWN;
    if(state==0){if(active){put32(m,started,now);put8(m,latch,1);}return 0;}
    if(state==1){if(!active){put8(m,latch,0);return 0;}if(!read32(m,started,0xd72e,&start))return TF_UNKNOWN;
        if((uint32_t)(now-start)<threshold*UINT32_C(1000))return 0;put8(m,latch,2);return active;}
    if(state==2&&active==0)put8(m,latch,0);return 0;
}
int tf_admit(tf_model *m,uint8_t selector,uint16_t rawspeed,uint8_t locked){
    if(rawspeed!=0&&rawspeed!=511)return 0;put8(m,RA(0xbf7c),selector);
    if(locked)tf_bridge(m);else put8(m,RA(0xbf8d),2);return 1;
}
void tf_bridge(tf_model *m){
    uint8_t q;tf_frame f;if(!read8(m,RA(0xbf7c),0xd69a,&q))return;
    if(q>=1&&q<=19)put8(m,RA(0xbf6a),q);
    else if(q==25)put8(m,RA(0xbf96),1);
    else if(q==24||q==26){cached(m,8,&f);if(frame_bits(m,&f,2,255,0xd65e)&&f.value[2]!=0){replace(&f,3,255,q==24?2:1);transmit(m,&f);transmit(m,&f);}}
    put8(m,RA(0xbf7c),0);
}
void tf_delay_bridge(tf_model *m,uint32_t delay){uint8_t p;if(read8(m,RA(0xbf7c),0xdd0c,&p)&&p)(void)tf_schedule(m,0xd69a,0,delay,0);}
static uint8_t door_enum(uint8_t n){return n==1?6:(n==0?3:((n==3||n==4)?2:3));}
void tf_door_consume(tf_model *m,tf_frame *f,uint8_t cls){
    uint8_t p,v=0,raw,vm=255;unsigned i;uint32_t callback;
    if(!read8(m,RA(0xbf6a),0xda56,&p)||p==0)return;
    if(p<=12){
        i=(unsigned)(p-1)/3u;callback=0xd62eu+12u*i;
        if(p%3u==1){if(cls==7||cls==8){if(!read8(m,RA(0xbf6b)+i,0xd798,&raw)){v=2;vm=0xfa;}else v=door_enum(raw);}else{v=3;(void)tf_schedule(m,callback,0,250,0);}}
        else if(p%3u==2)v=6;else{v=3;if(cls!=7&&cls!=8)(void)tf_schedule(m,callback,0,250,0);}
        if(i==0)replace_known(f,3,0x1f,(uint8_t)(v<<5),(uint8_t)((vm<<5)|0x1f));
        else if(i==1)replace_known(f,4,0xf8,(uint8_t)(v&7),(uint8_t)((vm&7)|0xf8));
        else if(i==2)replace_known(f,4,0xc7,(uint8_t)((v&7)<<3),(uint8_t)(((vm&7)<<3)|0xc7));
        else{replace_known(f,4,0x3f,(uint8_t)((v&3)<<6),(uint8_t)(((vm&3)<<6)|0x3f));replace_known(f,5,0xfe,(uint8_t)(v>>2),(uint8_t)((vm>>2)|0xfe));}
    }else switch(p){
        case 13:replace(f,3,0x1f,0xc0);replace(f,4,0,0xb6);replace(f,5,0xf0,13);break;
        case 14:replace(f,3,0x1f,0x60);replace(f,4,0,0xdb);replace(f,5,0xfe,0);break;
        case 15:replace(f,3,0x1f,0x40);replace(f,4,0,0x92);replace(f,5,0xf0,4);break;
        case 16:case 17:
            if(cls==7||cls==8){if(!read8(m,RA(0xbf6d),0xdc68,&raw)){v=2;vm=0xfa;}else v=door_enum(raw);}else v=3;
            replace_known(f,4,p==16?0:7,(uint8_t)((p==16?(v&7):0)|((v&7)<<3)|((v&3)<<6)),(uint8_t)((p==16?(vm&7):7)|((vm&7)<<3)|((vm&3)<<6)));replace_known(f,5,0xfe,(uint8_t)(v>>2),(uint8_t)((vm>>2)|0xfe));break;
        case 18:replace(f,4,7,0xb0);replace(f,5,255,1);break;
        case 19:replace(f,4,0xc7,0xd8);replace(f,5,0xfe,0);break;
        case 20:replace(f,3,0x1f,0x60);break;case 21:replace(f,4,0xf8,3);break;
        case 22:replace(f,4,0xc7,0x18);break;case 23:replace(f,4,255,0xc0);replace(f,5,0xfe,0);break;
        case 24:if(!read8(m,RA(0xbf6f),0xdbc2,&raw)){v=2;vm=0xfa;}else v=door_enum(raw);replace_known(f,5,0xf1,(uint8_t)(v<<1),(uint8_t)((vm<<1)|1));break;
        default:break;
    }
    put8(m,RA(0xbf6a),0);transmit(m,f);
}
static void observe_raw(tf_model *m,uint32_t raw,uint32_t confirmed,uint8_t n){
    uint8_t v,cs[4],agg;unsigned i;int all=1,one=0;
    put8(m,raw,n);if(n!=1&&n!=2)return;
    if(!read8(m,confirmed,0xd7e0,&v)||v!=n)put8(m,confirmed,n);
    for(i=0;i<4;i++){if(!read8(m,RA(0xbf66)+i,0xd7e0,&cs[i]))return;if(cs[i]!=2)all=0;if(cs[i]==1)one=1;}
    if(!read8(m,TF_GP+257,0xd7e0,&agg))return;
    if(all&&agg)put8(m,TF_GP+257,0);
    else if(!all&&one&&agg==0){put8(m,TF_GP+257,1);unknown(m,0xb0ba,0);}
    /* Event/notification, hazard predicates and per-ID EB32 remain outside this slice. */
}
void tf_observe_pair(tf_model *m,unsigned id,uint8_t d0,uint8_t d7){
    if(id==0x102){observe_raw(m,RA(0xbf6b),RA(0xbf66),(uint8_t)(d0&15));observe_raw(m,RA(0xbf6d),RA(0xbf68),(uint8_t)(d0>>4));}
    else if(id==0x103){observe_raw(m,RA(0xbf6c),RA(0xbf67),(uint8_t)(d0&15));observe_raw(m,RA(0xbf6e),RA(0xbf69),(uint8_t)(d0>>4));put8(m,RA(0xbf6f),(uint8_t)(d7&15));}
    else unknown(m,0xd7e0,id);
}
void tf_body273(tf_model *m,tf_frame *f,uint32_t force){
    uint8_t a,b,cfg,gear;int changed=0,selected=0;unsigned i;
    const uint32_t ff[4]={RA(0xbf99),RA(0xbf93),RA(0xbf9e),RA(0xbf97)};
    for(i=0;i<4;i++){if(!read8(m,ff[i],0xf076,&a))return;if(a){b=1;if((i==0||i==2)&&!read8(m,i==0?RA(0xbf9a):RA(0xbf9f),0xf076,&b))return;replace(f,3,0xf7,(uint8_t)((b&1)<<3));changed=1;break;}}
    if(!read8(m,RA(0xbf9b),0xf076,&a))return;
    if(a){if(!read8(m,RA(0xbf9c),0xf076,&b))return;replace(f,5,0x7f,(uint8_t)((b&1)<<7));selected=1;}
    else{if(!config(m,0,0xf076,&cfg))return;gear=0;if((cfg&8)&&!read8(m,RA(0xbf40),0xf076,&gear))return;
        if((cfg&8)&&gear==2){replace(f,5,0x7f,0x80);selected=1;}
        else if(!read8(m,RA(0xbfa0),0xf076,&a))return;
        else if(a){if(!read8(m,RA(0xbfa1),0xf076,&b))return;replace(f,5,0x7f,(uint8_t)((b&1)<<7));selected=1;}
        else if(!read8(m,RA(0xbf98),0xf076,&a))return;
        else if(a){replace(f,5,0x7f,0x80);selected=1;}}
    changed|=selected;
    if(!read8(m,RA(0xbf94),0xf076,&a))return;if(a){replace(f,10,0xe7,8);changed=1;}
    if(!read8(m,RA(0xbf96),0xf076,&a))return;if(a){put8(m,RA(0xbf96),0);replace(f,3,255,0x20);changed=1;}
    if(!read8(m,RA(0xbf95),0xf076,&a))return;if(a){put8(m,RA(0xbf95),0);replace(f,6,255,0x80);changed=1;}
    if(!read8(m,RA(0xbf8e),0xf076,&a))return;if(a){put8(m,RA(0xbf8e),0);replace(f,6,0xfc,(uint8_t)(a&3));changed=1;}
    if(!read8(m,RA(0xbf8c),0xf076,&a))return;if(a){put8(m,RA(0xbf8c),0);replace(f,6,0xc7,8);changed=1;}
    if(!read8(m,RA(0xbf90),0xf076,&a)||!read8(m,RA(0xbf8f),0xf076,&b))return;
    if(a!=b){if(!read8(m,RA(0xbf40),0xf076,&gear))return;if(gear==2){replace(f,9,0xdf,(uint8_t)((a&1)<<5));changed=1;}}
    if(!read8(m,RA(0xbf8d),0xf076,&a))return;
    if(a){if(a==2)tf_delay_bridge(m,1000);replace(f,5,0xf1,(uint8_t)((a&7)<<1));put8(m,RA(0xbf8d),0);changed=1;}
    if(!read8(m,RA(0xbf92),0xf076,&a))return;
    if(a){int take=0,unresolved=0;const unsigned indices[3]={5,3,10};const uint8_t bits[3]={1,4,0x80};
        for(i=0;i<3;i++){if(indices[i]>=f->available||(f->known[indices[i]]&bits[i])==0)unresolved=1;
            else if(f->value[indices[i]]&bits[i]){take=1;break;}}
        /* Both native branches leave these three bits zero. Only TX selection can remain unknown. */
        replace(f,5,0xfe,0);replace(f,3,0xfb,0);replace(f,10,0x7f,0);
        if(take)changed=1;else if(unresolved)unknown(m,0xf252,0);}
    if(changed||force)transmit(m,f);
}
static void fog_callback(tf_model *m,uint32_t cb){
    uint8_t p,flag;tf_frame f;cached(m,2,&f);
    if(cb==0xf384){if(!read8(m,RA(0xbf9d),cb,&p))return;p=(uint8_t)(p==0);put8(m,RA(0xbf9d),p);(void)tf_schedule(m,cb,0,50,0);}
    else{if(!read8(m,RA(0xbfa2),cb,&p))return;flag=(uint8_t)((~p)&1);p=(uint8_t)(p+1);put8(m,RA(0xbfa2),p);if(p<=3)(void)tf_schedule(m,cb,0,135,0);else{put8(m,RA(0xbfa2),0);(void)tf_schedule(m,cb,0,1500,0);}p=flag;}
    if(!read8(m,cb==0xf384?RA(0xbf99):RA(0xbf9e),cb,&flag))return;if(flag)replace(&f,3,0xf7,(uint8_t)((p&1)<<3));
    if(frame_bits(m,&f,3,8,cb))put8(m,cb==0xf384?RA(0xbf9a):RA(0xbf9f),(uint8_t)((f.value[3]>>3)&1));
    if(!read8(m,cb==0xf384?RA(0xbf9b):RA(0xbfa0),cb,&flag))return;if(flag)replace(&f,5,0x7f,(uint8_t)((p&1)<<7));
    if(frame_bits(m,&f,5,0x80,cb))put8(m,cb==0xf384?RA(0xbf9c):RA(0xbfa1),(uint8_t)(f.value[5]>>7));
    tf_body273(m,&f,1);
}
void tf_fog_set(tf_model *m,uint32_t wrapper,uint32_t enabled){
    uint32_t flag,paired,phase,cb;uint8_t p;tf_frame f;
    switch(wrapper){case 0xf53c:flag=RA(0xbf99);paired=RA(0xbf9b);break;case 0xf56e:flag=RA(0xbf9b);paired=RA(0xbf99);break;case 0xf5a0:flag=RA(0xbf9e);paired=RA(0xbfa0);break;case 0xf5d2:flag=RA(0xbfa0);paired=RA(0xbf9e);break;default:unknown(m,0xf332,wrapper);return;}
    cb=wrapper==0xf53c||wrapper==0xf56e?0xf384u:0xf42cu;phase=cb==0xf384?RA(0xbf9d):RA(0xbfa2);
    put8(m,flag,(uint8_t)enabled);if(!read8(m,paired,0xf332,&p))return;
    if(enabled&&p==0){put8(m,phase,0);fog_callback(m,cb);}
    else if(!enabled){cached(m,2,&f);tf_body273(m,&f,1);if(p==0)(void)tf_cancel(m,cb);}
}
void tf_ceba(tf_model *m,uint32_t q,uint32_t budget,uint32_t phase){put8(m,RA(0xbf34),1);put8(m,RA(0xbf35),(uint8_t)q);put8(m,RA(0xbf36),(uint8_t)(0u-phase));put8(m,RA(0xbf37),(uint8_t)budget);}
void tf_fed4(tf_model *m,uint32_t q,uint32_t repeat){put8(m,TF_GP+300,(uint8_t)q);put8(m,TF_GP+301,repeat?10:1);}
void tf_ceda(tf_model *m,uint32_t q,uint16_t rawspeed){
    uint8_t gear,alt;if(!read8(m,RA(0xbf40),0xceda,&gear)||q==gear)return;if(rawspeed!=511&&rawspeed>8)return;
    if(!read8(m,TF_GP+354,0xceda,&alt))return;if(alt){tf_fed4(m,q,0);return;}
    if(q==1)put32(m,RA(0xbf34),0x01000501);else if(q==2)put32(m,RA(0xbf34),0x01000201);else if(q==4)put32(m,RA(0xbf34),0x01000401);
}
void tf_229(tf_model *m,tf_frame *f){
    uint8_t active,p,q,b,counter,mask;if(!read8(m,RA(0xbf34),0xcd3a,&active)||!active)return;
    if(!read8(m,RA(0xbf36),0xcd3a,&p))return;if(p!=255)put8(m,RA(0xbf36),(uint8_t)(((unsigned)p+1u)%3u));
    if(p==0||p==255){if(!read8(m,RA(0xbf35),0xcd3a,&q))return;
        if(read8(m,RA(0xbf37),0xcd3a,&b)){b=(uint8_t)(b-1);put8(m,RA(0xbf37),b);if(b==0)put8(m,RA(0xbf34),0);}
        else{m->known[0xbf37]=0;m->known[0xbf34]=(uint8_t)~active;}}
    else q=0;
    if(q==5){replace(f,5,0xfc,1);replace(f,4,0x8f,0);}else replace(f,4,0x8f,(uint8_t)((q&7)<<4));
    if(frame_bits(m,f,4,15,0xcd3a)){counter=(uint8_t)((f->value[4]+1)&15);replace(f,4,0xf0,counter);f->value[3]=image_byte(m,0x19d10u+16u*q+counter,0xcdac,&mask);f->known[3]=mask;}
    else{f->known[4]&=0xf0;f->known[3]=0;}
    transmit(m,f);
}
int tf_checksum(const tf_frame *f,uint8_t *sum){
    unsigned i,n;uint8_t s;if(f->available<3||f->known[0]!=255||f->known[1]!=255||f->known[2]!=255)return TF_UNKNOWN;
    s=(uint8_t)(f->value[0]+f->value[1]);n=f->value[2];for(i=1;i<n;i++){unsigned a=3+i;if(a>=f->available||f->known[a]!=255)return TF_UNKNOWN;s=(uint8_t)(s+f->value[a]);}*sum=s;return 1;
}
void tf_678_observe(tf_model *m,const tf_frame *f){
    uint8_t alt,n,sum;if(!read8(m,TF_GP+354,0xfe0c,&alt)||alt)return;if(!frame_bits(m,f,4,255,0xfe0c))return;if(f->value[4]>15)return;
    if(tf_checksum(f,&sum)==TF_UNKNOWN||!frame_bits(m,f,3,255,0xfe0c)){unknown(m,0xfe0c,0);return;}if(f->value[3]!=sum)return;
    if(!read8(m,TF_GP+302,0xfe0c,&n))return;n=(uint8_t)(n+1);if(n>4){put8(m,TF_GP+302,0);put8(m,TF_GP+354,1);}else put8(m,TF_GP+302,n);
}
void tf_678_consume(tf_model *m,tf_frame *f){
    uint8_t alt,b,q,n,mask=0,sum;if(!read8(m,TF_GP+301,0xfe58,&b)||b==0)return;if(!read8(m,TF_GP+354,0xfe58,&alt)||alt==0)return;
    if(!read8(m,TF_GP+300,0xfe58,&q))return;
    n=0;{int counter_known=frame_bits(m,f,4,15,0xfe58);if(counter_known)n=(uint8_t)((f->value[4]+1)&15);
        switch(q){case 1:mask=0x10;break;case 2:mask=0x20;break;case 3:mask=0x80;break;case 4:mask=0x40;break;default:break;}replace(f,4,0,(uint8_t)(n|mask));if(!counter_known)f->known[4]=0xf0;}
    {int sum_known=tf_checksum(f,&sum);if(sum_known!=1)unknown(m,0xeb8a,0);
        /* FE94 loads budget before FE98 stores d0. Frame/RAM aliasing is not represented here. */
        if(!read8(m,TF_GP+301,0xfe94,&b))return;
        if(sum_known==1){f->value[3]=sum;f->known[3]=255;}else f->known[3]=0;
        put8(m,TF_GP+301,(uint8_t)(b-1));transmit(m,f);}
}
void tf_threshold118(tf_model *m,uint8_t raw){
    uint8_t cfg,threshold,mask,old,n;if(!config(m,0,0xf8a2,&cfg))return;cfg&=7;if(cfg==0)return;
    threshold=image_byte(m,0x1a7d8u+cfg,0xf8a2,&mask);if(mask==0)return;n=(uint8_t)(raw>=threshold);
    if(!read8(m,TF_GP+277,0xf8a2,&old)||old!=n)put8(m,TF_GP+277,n);
}
void tf_reset_scope(tf_model *m,uint32_t va){
    uint32_t a;size_t n;switch(va){case 0xcf4c:a=RA(0xbf34);n=16;break;case 0xfee4:a=TF_GP+300;n=3;break;case 0xf906:a=TF_GP+276;n=5;break;case 0xa2a0:a=TF_GP+180;n=5;break;case 0xdf2e:a=RA(0xbf64);n=28;break;case 0xf6fe:a=RA(0xbf8c);n=24;break;default:unknown(m,va,0);return;}
    if(m->backend.memory_contracts==1){memset(m->ram+a-TF_RAM_BASE,0,n);memset(m->known+a-TF_RAM_BASE,255,n);}
    else{memset(m->known+a-TF_RAM_BASE,0,n);unknown(m,va,a);}
}
static void deliver(tf_model *m,uint32_t cb,uint32_t argument){
    uint8_t gear,alt;m->callback_calls++;m->last_callback=cb;m->last_argument=argument;
    if(cb==0xd69a)tf_bridge(m);
    else if(cb==0xd62e||cb==0xd63a||cb==0xd646||cb==0xd652)put8(m,RA(0xbf6a),(uint8_t)(20+(cb-0xd62e)/12));
    else if(cb==0xf384||cb==0xf42c)fog_callback(m,cb);
    else if(cb==0xd3b2){if(read8(m,RA(0xbf40),cb,&gear)&&gear==1&&read8(m,TF_GP+354,cb,&alt)){if(alt)tf_fed4(m,1,1);else tf_ceba(m,5,10,1);}}
    else unknown(m,cb,argument);
    if(m->backend.delivery)m->backend.delivery(m->backend.context,m,cb,argument);
}
