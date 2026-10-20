/* Explicit opt-in host reconstruction of fixed WCH64be955 V1.30 candidate.
   Native bytes and known masks live only in tf_model. No original code, MMIO,
   hardware or wall clock executes here. Evidence: eleventh-round/rom/contracts. */
#include "rom_candidate.h"
#include <string.h>
#include <limits.h>
#define R(x) (TF_RAM_BASE+UINT32_C(x))
#define HOPS (TF_RAM_SIZE+1u)
static void note(rc_adapter *a,unsigned flag,uint32_t va,uint32_t address,int stop){
    a->boundary_flags|=flag;a->unknowns++;a->last_unknown_va=va;a->last_unknown_address=address;
    if(a->memory){a->memory->unknown_effects++;a->memory->last_unknown_va=va;a->memory->last_unknown_address=address;}
    if(stop)a->fault=1;
}
static int begin(rc_adapter *a){
    if(!a||!a->memory)return 0;
    a->operations++;
    if(a->profile!=RC_WCH_64BE955_V130){note(a,RC_BOUND_PROFILE,0,0,1);return 0;}
    return !a->fault;
}
static int range(rc_adapter *a,uint32_t p,unsigned n,uint32_t va){
    if(p<TF_RAM_BASE||n>TF_RAM_SIZE||p-TF_RAM_BASE>TF_RAM_SIZE-n){
        note(a,RC_BOUND_MEMORY,va,p,1);return 0;
    }
    return 1;
}
static int readv(rc_adapter *a,uint32_t p,unsigned n,uint32_t va,uint32_t *out){
    unsigned i;uint32_t v=0;if(!range(a,p,n,va))return 0;
    for(i=0;i<n;i++){
        if(a->memory->known[p-TF_RAM_BASE+i]!=255){note(a,RC_BOUND_OPERAND,va,p+i,1);return 0;}
        v|=(uint32_t)a->memory->ram[p-TF_RAM_BASE+i]<<(8u*i);
    }
    *out=v;return 1;
}
static int r32(rc_adapter *a,uint32_t p,uint32_t va,uint32_t *v){return readv(a,p,4,va,v);}
static int r16(rc_adapter *a,uint32_t p,uint32_t va,uint16_t *v){uint32_t q;if(!readv(a,p,2,va,&q))return 0;*v=(uint16_t)q;return 1;}
static int r8(rc_adapter *a,uint32_t p,uint32_t va,uint8_t *v){uint32_t q;if(!readv(a,p,1,va,&q))return 0;*v=(uint8_t)q;return 1;}
static int writev(rc_adapter *a,uint32_t p,unsigned n,uint32_t v,uint32_t mask,uint32_t va){
    unsigned i;if(!range(a,p,n,va))return 0;
    for(i=0;i<n;i++){a->memory->ram[p-TF_RAM_BASE+i]=(uint8_t)(v>>(8u*i));a->memory->known[p-TF_RAM_BASE+i]=(uint8_t)(mask>>(8u*i));}
    return 1;
}
static int w32(rc_adapter *a,uint32_t p,uint32_t v,uint32_t va){return writev(a,p,4,v,UINT32_MAX,va);}
static int w16(rc_adapter *a,uint32_t p,uint16_t v,uint32_t va){return writev(a,p,2,v,65535,va);}
static int w8(rc_adapter *a,uint32_t p,uint8_t v,uint32_t va){return writev(a,p,1,v,255,va);}
static int zero(rc_adapter *a,uint32_t p,uint32_t n,uint32_t va){
    if(!range(a,p,n,va))return 0;
    memset(a->memory->ram+p-TF_RAM_BASE,0,n);memset(a->memory->known+p-TF_RAM_BASE,255,n);return 1;
}
static int hops(rc_adapter *a,uint32_t *n,uint32_t va,uint32_t p){
    if(++*n>HOPS){note(a,RC_BOUND_CORRUPT_LIST,va,p,1);return 0;}return 1;
}
static int counter(rc_adapter *a,uint32_t amount,int subtract,uint32_t va){
    uint32_t p=R(0x3052);uint16_t old;unsigned known;
    if(!range(a,p,2,va))return 0;
    old=(uint16_t)(a->memory->ram[p-TF_RAM_BASE]|((uint16_t)a->memory->ram[p-TF_RAM_BASE+1]<<8));
    known=a->memory->known[p-TF_RAM_BASE]==255&&a->memory->known[p-TF_RAM_BASE+1]==255;
    if(!known)note(a,RC_BOUND_OPERAND,va,p,0);
    return writev(a,p,2,(uint16_t)(subtract?(uint32_t)old-amount:(uint32_t)old+amount),known?65535u:0u,va);
}
static int status(rc_adapter *a,unsigned code,uint32_t detail,uint32_t va){
    uint32_t token;if(!r32(a,R(0x30d0),va,&token))return 0;
    if(!token)return 1;a->status_calls++;
    if(!a->hooks.status||!a->hooks.status(a->hooks.context,a,code,detail)){
        note(a,RC_BOUND_CALLBACK,va,token,1);return 0;
    }
    return !a->fault;
}
static int raw_now(rc_adapter *a,uint32_t pointer_va,uint32_t va,uint32_t *out){
    uint32_t token;if(!r32(a,pointer_va,va,&token))return 0;a->clock_calls++;
    if(!token||!a->hooks.clock||!a->hooks.clock(a->hooks.context,token,out)){
        note(a,RC_BOUND_CALLBACK,va,token,1);return 0;
    }
    return !a->fault;
}
static uint32_t period(uint16_t f,uint32_t t){return (uint32_t)(((uint64_t)f*t+UINT64_C(800))/UINT64_C(1600));}
static uint32_t wrap(uint32_t n,uint32_t q,uint32_t m){uint32_t s=n+q;if(s<q||s>=m)s-=m;return s;}
int rc_attach(rc_adapter *a,tf_model *m,rc_profile profile,const rc_hooks *hooks){
    if(!a||!m)return 0;memset(a,0,sizeof(*a));a->memory=m;a->profile=profile;if(hooks)a->hooks=*hooks;
    a->boundary_flags=RC_BOUND_MMIO;
    if(profile!=RC_WCH_64BE955_V130){a->boundary_flags|=RC_BOUND_PROFILE;return 0;}return 1;
}
void rc_resume(rc_adapter *a){if(a)a->fault=0;}
int rc_heap_alloc(rc_adapter *a,uint32_t size,uint32_t tag,uint32_t *out){
    uint16_t q=(uint16_t)(size+3u),cap,used;uint32_t p,end,next,count=0,newp;
    if(!begin(a))return 0;
    if(size==0||tag==0){*out=0;return 1;}q=(uint16_t)(q&65532u);
    if(!r32(a,R(q<=52?0x3044:0x3040),0x20000080,&p)||!r32(a,R(0x303c),0x20000088,&end))return 0;
    while(p!=end){
        if(!hops(a,&count,0x2000008c,p)||!r16(a,p+6,0x200000ae,&used))return 0;
        if(!used){
            if(!r16(a,p+4,0x200000b2,&cap))return 0;
            if(cap>=q){
                if((uint32_t)cap-q>8u){
                    if(!r32(a,p,0x200000ca,&next))return 0;newp=p+8u+q;
                    if(!w16(a,newp+4,(uint16_t)(cap-q-8u),0x200000dc)||!w32(a,newp,next,0x200000de)||
                       !w16(a,newp+6,0,0x200000e2)||!w32(a,p,newp,0x200000e6)||!w16(a,p+4,q,0x200000e8)||
                       !counter(a,8,1,0x200000ee))return 0;
                }
                if(!w16(a,p+6,(uint16_t)tag,0x200000f0)||!counter(a,q,1,0x200000fa))return 0;*out=p+8u;return 1;
            }
        }
        if(!r32(a,p,0x2000010c,&p))return 0;
    }
    if(!status(a,1,tag|((uint32_t)q<<16),0x200000a0))return 0;*out=0;return 1;
}
int rc_heap_free_sum(rc_adapter *a,uint32_t *out){
    uint32_t p,end,total=0,count=0;uint16_t tag,cap;
    if(!begin(a)||!r32(a,R(0x3044),0x42f98,&p)||!r32(a,R(0x303c),0x42f9c,&end))return 0;
    while(p!=end){
        if(!hops(a,&count,0x42fa2,p)||!r16(a,p+6,0x42fa8,&tag))return 0;
        if(!tag){if(!r16(a,p+4,0x42fac,&cap))return 0;total+=cap;}
        if(!r32(a,p,0x42fb0,&p))return 0;
    }
    *out=total;return 1;
}
int rc_heap_free(rc_adapter *a,uint32_t pointer){
    uint32_t start,end,large,p,prev=0,next,count=0,after;uint16_t cap,tag,other;
    if(!begin(a))return 0;if(!pointer)return 1;
    if(!r32(a,R(0x3044),0x2000012c,&start)||!r32(a,R(0x303c),0x20000134,&end))return 0;p=start;
    while(p<end){
        if(!hops(a,&count,0x2000013c,p)||!r32(a,p,0x20000140,&next))return 0;
        if(pointer>=p&&pointer<=next){
            if(pointer<p+8u)return 1;
            if(!r16(a,p+6,0x20000154,&tag))return 0;
            if(tag==0x8001){
                uint8_t n;if(!r8(a,R(0x2e54),0x20000162,&n))return 0;
                if(!w8(a,R(0x2e54),(uint8_t)(n+1u),0x20000168))return 0;
            }
            if(!r16(a,p+4,0x20000174,&cap)||!w16(a,p+6,0,0x20000178)||!counter(a,cap,0,0x20000186))return 0;
            if(p!=start){
                if(!r32(a,R(0x3040),0x20000190,&large))return 0;
                if(p!=large){
                    if(!r16(a,prev+6,0x20000198,&tag))return 0;
                    if(!tag){
                        if(!r16(a,prev+4,0x2000019c,&other)||!w32(a,prev,next,0x2000019e)||
                           !w16(a,prev+4,(uint16_t)(other+cap+8u),0x200001a8)||!counter(a,8,0,0x200001aa))return 0;p=prev;
                    }
                }
            }
            if(!r32(a,p,0x200001ae,&next))return 0;
            if(next!=end){
                if(!r32(a,R(0x3040),0x200001b8,&large))return 0;
                if(next!=large){
                    if(!r16(a,next+6,0x200001c0,&tag))return 0;
                    if(!tag){
                        if(!r16(a,p+4,0x200001c4,&cap)||!r16(a,next+4,0x200001c6,&other)||
                           !r32(a,next,0x200001c8,&after)||!w16(a,p+4,(uint16_t)(cap+other+8u),0x200001ce)||
                           !w32(a,p,after,0x200001d0)||!counter(a,8,0,0x200001d6))return 0;
                    }
                }
            }
            return 1;
        }
        prev=p;p=next;
    }
    return 1;
}
int rc_task_register(rc_adapter *a,uint32_t callback,uint8_t *out){
    uint8_t n,max;uint32_t p;if(!begin(a)||!r8(a,R(0x304d),0x43b06,&n)||!r8(a,R(0x304e),0x43b08,&max))return 0;
    if(n>=max){*out=255;return 1;}
    if(!r32(a,R(0x3074),0x43b12,&p)||!w8(a,R(0x304d),(uint8_t)(n+1u),0x43b1a)||!w32(a,p+4u*n,callback,0x43b22))return 0;*out=n;return 1;
}
int rc_prepare(rc_adapter *a,uint32_t P,uint16_t L,uint8_t connect){
    uint32_t S=P+544u,E=P+(uint32_t)L-8u,B=L<=4103u?(uint32_t)L>>3:512u,large=S+B,sum,meta,n;
    uint8_t task;
    if(!begin(a)||!w32(a,R(0x309c),P,0x43b94)||!w16(a,R(0x30a0),L,0x43b94)||
       !w8(a,R(0x30b1),connect,0x43b94)||!w32(a,R(0x3098),0,0x439f2)||!w32(a,R(0x30e0),0,0x43a00)||
       !zero(a,R(0x3078),20,0x43a1e)||!w32(a,R(0x3090),0,0x43a12)||!zero(a,R(0x304c),40,0x43a30))return 0;
    if(!w32(a,R(0x3044),S,0x42fc8)||!w32(a,R(0x303c),E,0x42fdc)||!w32(a,R(0x3040),large,0x42ff8)||
       !w32(a,S,large,0x42ffc)||!w16(a,S+4,(uint16_t)(B-8u),0x43002)||!w16(a,S+6,0,0x43004)||
       !w32(a,large,E,0x43008)||!w16(a,large+4,(uint16_t)(E-large-8u),0x4300e)||!w16(a,large+6,0,0x43010)||
       !rc_heap_free_sum(a,&sum)||!w16(a,R(0x3052),(uint16_t)sum,0x4301c))return 0;
    n=(uint8_t)(14u+3u*((connect>>2)+(connect&3u)));
    if(!w8(a,R(0x304e),(uint8_t)n,0x43a64)||!rc_heap_alloc(a,576u+6u*n,1,&meta)||!w32(a,R(0x30dc),meta,0x43a76))return 0;
    if(!meta)return 1;
    if(!zero(a,meta,576u+6u*n,0x43a8a)||!w32(a,R(0x3074),meta+576u,0x43aa2)||
       !w32(a,R(0x3094),meta+576u+4u*n,0x43aac))return 0;
    if(!rc_task_register(a,0x43154,&task)||!rc_task_register(a,0x431d6,&task)||!rc_task_register(a,0x431d6,&task))return 0;
    return 1;
}
int rc_timer_find(rc_adapter *a,uint32_t task,uint16_t mask,uint32_t *out){
    uint32_t p,count=0;uint16_t e;uint8_t t;
    if(!begin(a)||!r32(a,R(0x3098),0x20000318,&p))return 0;
    while(p){
        if(!hops(a,&count,0x2000031c,p)||!r16(a,p+2,0x20000322,&e))return 0;
        if(e==mask){if(!r8(a,p,0x20000328,&t))return 0;if(t==task){*out=p;return 1;}}
        if(!r32(a,p+12,0x2000032e,&p))return 0;
    }*out=0;return 1;
}
static int event_op(rc_adapter *a,uint32_t task,uint16_t event,uint32_t *out,int clear){
    uint8_t count;uint32_t p;uint16_t old;uint32_t va=clear?0x4343a:0x433fa;
    if(!begin(a)||!r8(a,R(0x304d),va,&count))return 0;
    if(task>=count){*out=3;return 1;}
    if(!r32(a,R(0x3094),va,&p)||!r16(a,p+2u*task,va,&old)||
       !w16(a,p+2u*task,clear?(uint16_t)(old&~event):(uint16_t)(old|event),va))return 0;*out=0;return 1;
}
int rc_set_event(rc_adapter *a,uint32_t task,uint16_t event,uint32_t *out){return event_op(a,task,event,out,0);}
int rc_clear_event(rc_adapter *a,uint32_t task,uint16_t event,uint32_t *out){return event_op(a,task,event,out,1);}
int rc_timer_start(rc_adapter *a,uint32_t task,uint16_t mask,uint32_t ticks,uint32_t *out){
    uint8_t count;uint16_t f;uint32_t token,M,Q,now,D,p,head,next,h=0;
    if(!begin(a)||!r8(a,R(0x304d),0x43600,&count))return 0;
    if(task>=count){*out=0;return 1;}
    if(!r32(a,R(0x3090),0x4360c,&token))return 0;if(!token){*out=0;return 1;}
    if(!r32(a,R(0x30e8),0x43628,&M)||!r16(a,R(0x30ec),0x4362c,&f))return 0;
    Q=period(f,ticks);if(Q>M-UINT32_C(30000000)){*out=0;return 1;}
    if(!raw_now(a,R(0x3090),0x4367a,&now)||!r16(a,R(0x30ec),0x4367c,&f)||!r32(a,R(0x30e8),0x436a4,&M))return 0;
    Q=period(f,ticks);D=wrap(now,Q,M);
    if(!rc_timer_find(a,task,mask,&p))return 0;
    if(p){if(!w32(a,p+8,D,0x436c2))return 0;*out=1;return 1;}
    if(!rc_heap_alloc(a,16,(uint16_t)(0xff00u|task),&p))return 0;
    if(!p){if(!status(a,4,task,0x436f2))return 0;*out=0;return 1;}
    if(!r32(a,R(0x3098),0x436fa,&head))return 0;
    if(!head){if(!w32(a,R(0x3098),p,0x43700))return 0;}
    else{
        for(;;){if(!hops(a,&h,0x4371c,head)||!r32(a,head+12,0x4371c,&next))return 0;if(!next)break;head=next;}
        if(!w32(a,head+12,p,0x43720))return 0;
    }
    if(!w32(a,p+12,0,0x43706)||!w32(a,p+8,D,0x4370a)||!w16(a,p+2,mask,0x4370c)||
       !w8(a,p,(uint8_t)task,0x43710)||!w8(a,p+1,1,0x43712)||!w32(a,p+4,0,0x43714))return 0;*out=1;return 1;
}
int rc_timer_reload(rc_adapter *a,uint32_t task,uint16_t mask,uint32_t ticks,uint32_t *out){
    uint32_t ignored,p;uint16_t f;
    if(!begin(a)||!rc_timer_start(a,task,mask,ticks,&ignored)||!rc_timer_find(a,task,mask,&p))return 0;
    if(!p){*out=8;return 1;}
    if(!r16(a,R(0x30ec),0x4381a,&f)||!w32(a,p+4,period(f,ticks),0x4383a))return 0;*out=0;return 1;
}
int rc_timer_stop(rc_adapter *a,uint32_t task,uint16_t mask,uint32_t *out){
    uint32_t p,ignored;uint8_t cursor;uint16_t suppression;
    if(!begin(a)||!rc_timer_find(a,task,mask,&p))return 0;
    if(p&&!w16(a,p+2,0,0x43884))return 0;
    if(!rc_clear_event(a,task,mask,&ignored)||!r8(a,R(0x304c),0x43892,&cursor))return 0;
    if(cursor==task){if(!r16(a,R(0x308c),0x4389e,&suppression)||!w16(a,R(0x308c),(uint16_t)(suppression|mask),0x438a4))return 0;}
    *out=p?0u:6u;return 1;
}
int rc_timer_remaining(rc_adapter *a,uint32_t task,uint16_t mask,uint32_t *out){
    uint32_t p,D,now,M,diff;uint16_t f;
    if(!begin(a)||!rc_timer_find(a,task,mask,&p))return 0;
    if(!p){*out=0;return 1;}
    if(!r32(a,p+8,0x4397a,&D)||!raw_now(a,R(0x3090),0x4397c,&now)||!r32(a,R(0x30e8),0x4398a,&M))return 0;
    if(D<now)D+=M;diff=D-now;
    if(diff>=M-UINT32_C(30000000)){*out=0;return 1;}
    if(!r16(a,R(0x30ec),0x439a6,&f))return 0;if(!f){note(a,RC_BOUND_OPERAND,0x439ae,R(0x30ec),1);return 0;}
    *out=(uint32_t)(((uint64_t)diff*1600u)/f);return 1;
}
int rc_timer_pump(rc_adapter *a){
    uint32_t p,prev=0,next,now,D,M,e,repeat,ignored,idle,nearest,h=0;uint16_t mask;uint8_t task;
    if(!begin(a)||!r32(a,R(0x3098),0x20000504,&p))return 0;if(!p)return 1;
    while(p){
        if(!hops(a,&h,0x2000053c,p)||!r16(a,p+2,0x2000053c,&mask))return 0;
        if(!mask){
            if(!r32(a,p+12,0x20000540,&next))return 0;
            if(prev){if(!w32(a,prev+12,next,0x20000556))return 0;}else if(!w32(a,R(0x3098),next,0x20000546))return 0;
            if(!rc_heap_free(a,p))return 0;p=next;continue;
        }
        if(!raw_now(a,R(0x3090),0x20000560,&now)||!r32(a,p+8,0x20000562,&D))return 0;
        if(now>=D)e=now-D;
        else{if(!r32(a,R(0x30e8),0x2000056c,&M))return 0;e=M-D+now;}
        if(e<=UINT32_C(29999999)){
            if(!w32(a,R(0x305c),0,0x2000057c)||!r16(a,p+2,0x20000580,&mask)||!r8(a,p,0x20000582,&task)||
               !rc_set_event(a,task,mask,&ignored)||!r32(a,p+4,0x2000058c,&repeat)||!r32(a,p+12,0x2000058e,&next))return 0;
            if(!repeat){
                if(prev){if(!w32(a,prev+12,next,0x200005e6))return 0;}else if(!w32(a,R(0x3098),next,0x200005e0))return 0;
                if(!rc_heap_free(a,p))return 0;p=next;continue;
            }
            if(!r32(a,p+8,0x20000592,&D)||!r32(a,R(0x30e8),0x20000594,&M)||!w32(a,p+8,wrap(D,repeat,M),0x200005a8))return 0;
        }else{
            if(!r32(a,R(0x30c4),0x200005ec,&idle))return 0;
            if(idle){
                uint32_t remain;
                if(D>=now)remain=D-now;
                else{if(!r32(a,R(0x30e8),0x2000060c,&M))return 0;remain=D+M-now;}
                if(!r32(a,R(0x305c),0x200005fa,&nearest))return 0;
                if(remain<nearest&&!w32(a,R(0x305c),remain,0x20000602))return 0;
            }
            if(!r32(a,p+12,0x20000608,&next))return 0;
        }
        prev=p;p=next;
    }
    if(!r32(a,R(0x305c),0x200005b8,&nearest)||!w32(a,R(0x305c),nearest<=1?0:nearest-1,0x200005c2))return 0;return 1;
}
static int clock_delta(rc_adapter *a,uint32_t *out){
    uint32_t raw,old,n,M,maxC;uint16_t f;
    if(!raw_now(a,R(0x30e4),0x43c2a,&raw)||!r16(a,R(0x30ec),0x43c38,&f))return 0;
    if(!f){note(a,RC_BOUND_OPERAND,0x43c44,R(0x30ec),1);return 0;}
    n=(uint32_t)(((uint64_t)raw*1600u)/f);
    if(!r32(a,R(0x3064),0x43c50,&old))return 0;
    if(n==old){*out=0;return 1;}
    if(n>old)*out=n-old;
    else{
        if(!r32(a,R(0x30e8),0x43c66,&M))return 0;
        maxC=(uint32_t)(((uint64_t)M*1600u)/f);*out=maxC-old+n;
    }
    return w32(a,R(0x3064),n,0x43c7e);
}
int rc_clock_configure(rc_adapter *a,int supplied,uint32_t token,uint32_t M,uint16_t f,uint16_t accuracy,uint8_t irq,uint32_t *out){
    uint32_t calibration,delta;uint8_t wait;(void)irq;
    if(!begin(a)||!r32(a,R(0x30cc),0x43e02,&calibration))return 0;
    if(calibration&&(!a->hooks.calibration||!a->hooks.calibration(a->hooks.context,a,calibration))){
        note(a,RC_BOUND_CALLBACK,0x43e12,calibration,1);return 0;
    }
    if(supplied&&(!token||!M||!f||!accuracy)){*out=1;return 1;}
    if(!supplied){token=R(0x986);M=UINT32_MAX;f=31250;accuracy=50;if(!w32(a,R(0x3068),0,0x43e9a))return 0;}
    if(!w32(a,R(0x30e4),token,0x43e38)||!w32(a,R(0x30e8),M,0x43e38)||!w16(a,R(0x30ec),f,0x43e38)||
       !w16(a,R(0x30ee),accuracy,0x43e38)||!zero(a,R(0x30f0),4,0x43e40)||!w32(a,R(0x3090),token,0x43e50)||
       !r8(a,R(0x30b3),0x43e54,&wait))return 0;
    if(!wait&&!w8(a,R(0x30b3),(uint8_t)(((uint32_t)f*1400u)/1000000u),0x43e76))return 0;
    if(!w32(a,R(0x30e0),0x43c12,0x439c2)||!clock_delta(a,&delta)||!w32(a,R(0x3064),delta,0x439ce))return 0;*out=0;return 1;
}
int rc_clock_init(rc_adapter *a,uint32_t token,uint32_t M,uint16_t f,uint16_t accuracy,uint8_t irq,uint32_t *out){
    return rc_clock_configure(a,token!=0,token,M,f,accuracy,irq,out);
}
int rc_clock_get(rc_adapter *a,uint32_t *out){
    uint32_t callback,total,delta;
    if(!begin(a)||!r32(a,R(0x30e0),0x433d4,&callback))return 0;
    if(callback){
        if(callback!=0x43c12){note(a,RC_BOUND_CALLBACK,0x433e8,callback,1);return 0;}
        if(!clock_delta(a,&delta)||!r32(a,R(0x3060),0x433ea,&total)||!w32(a,R(0x3060),total+delta,0x433ee))return 0;
    }
    return r32(a,R(0x3060),0x433f0,out);
}
int rc_take_event(rc_adapter *a,uint8_t task,uint16_t *out){
    uint32_t p;if(!begin(a)||!r32(a,R(0x3094),0x200008e6,&p)||!r16(a,p+2u*task,0x200008e8,out)||
       !w16(a,p+2u*task,0,0x200008ea)||!w8(a,R(0x304c),task,0x200008ee)||!w16(a,R(0x308c),0,0x20000906))return 0;return 1;
}
int rc_return_event(rc_adapter *a,uint8_t task,uint16_t returned){
    uint32_t p,oneshot;uint16_t current,suppression;uint8_t cursor;(void)task;
    if(!begin(a)||!r16(a,R(0x308c),0x2000090c,&suppression)||!r8(a,R(0x304c),0x20000910,&cursor)||
       !r32(a,R(0x3094),0x2000091e,&p)||!r16(a,p+2u*cursor,0x20000924,&current)||
       !w16(a,p+2u*cursor,(uint16_t)((returned&~suppression)|current),0x20000928))return 0;
    if(cursor&&!w8(a,R(0x304c),(uint8_t)(cursor+1u),0x20000932))return 0;
    if(!r32(a,R(0x3078),0x20000936,&oneshot))return 0;
    if(oneshot){note(a,RC_BOUND_CALLBACK,0x2000093c,oneshot,1);return 0;}return 1;
}
int rc_rom_status(void *context,unsigned offset,uint8_t task,uint16_t mask,uint32_t ticks){
    rc_adapter *a=(rc_adapter *)context;uint32_t out;int known=0;
    switch(offset){
    case 80:known=rc_set_event(a,task,mask,&out);break;
    case 84:known=rc_clear_event(a,task,mask,&out);break;
    case 88:known=rc_timer_start(a,task,mask,ticks,&out);break;
    case 92:known=rc_timer_stop(a,task,mask,&out);break;
    case 556:known=rc_timer_reload(a,task,mask,ticks,&out);break;
    default:if(a)note(a,RC_BOUND_CALLBACK,0,UINT32_C(0x40000)+offset,0);return TF_UNKNOWN;
    }
    return known?(int)out:TF_UNKNOWN;
}
int rc_msg_allocate_register(rc_adapter *a,uint32_t n,uint32_t *out){
    uint32_t p;if(!begin(a))return 0;if(!n){*out=0;return 1;}
    if(!rc_heap_alloc(a,(uint16_t)(n+8u),UINT32_C(0xf000)|n,&p))return 0;
    if(!p){*out=0;return 1;}
    if(!w32(a,p,0,0x20000274)||!w16(a,p+4,(uint16_t)n,0x20000278)||!w8(a,p+6,255,0x2000027a))return 0;
    *out=p+8u;return 1;
}
int rc_msg_allocate(rc_adapter *a,uint16_t n,uint32_t *out){return rc_msg_allocate_register(a,n,out);}
int rc_msg_deallocate(rc_adapter *a,uint32_t p,uint32_t *out){
    uint8_t owner;if(!begin(a))return 0;if(!p){*out=5;return 1;}
    if(!r8(a,p-2u,0x43094,&owner))return 0;if(owner!=255){*out=4;return 1;}
    if(!rc_heap_free(a,p))return 0;*out=0;return 1;
}
