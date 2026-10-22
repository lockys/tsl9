#include "callback.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct fixture {unsigned char memory[65536];uint32_t recv,gate,capacity,allocated,sent;cb_effect calls[16];unsigned count,checks;} fixture;
static void check(fixture *f,int ok){f->checks++;if(!ok){fprintf(stderr,"check failed at %u\n",f->checks);exit(1);}}
static uint32_t get(fixture *f,uint32_t a,unsigned w){uint32_t v=0;unsigned i;if(a>=0x40000u && a<0x40200u)return a+0x100000u;for(i=0;i<w/8u;i++)v|=(uint32_t)f->memory[(a+i)&65535u]<<(8u*i);return v;}
static void put(fixture *f,uint32_t a,unsigned w,uint32_t v){unsigned i;for(i=0;i<w/8u;i++)f->memory[(a+i)&65535u]=(unsigned char)(v>>(8u*i));}
static cb_flow provider(void *u,cb_host *h,cb_effect *e){fixture *f=(fixture *)u;if(e->kind==CB_READ)e->value=get(f,e->address,e->width);else if(e->kind==CB_WRITE)put(f,e->address,e->width,e->value);else{check(f,f->count<16u);f->calls[f->count++]=*e;switch(e->source_site){case 0x8640u:h->args[0]=f->recv;break;case 0x86e0u:case 0x87c6u:h->args[0]=f->gate;break;case 0x8704u:h->args[0]=f->capacity;break;case 0x87a2u:h->args[0]=f->allocated;break;case 0x8812u:h->args[0]=f->sent;break;default:h->args[0]=0x66778899u;break;}}return CB_CONTINUE;}
static void setup(fixture *f,cb_host *h){memset(f,0,sizeof(*f));memset(h,0,sizeof(*h));h->values.gp=0x20001000u;h->values.sp=0x2000f000u;h->values.return_address=0x12345679u;h->values.events=0x77777777u;h->provider=provider;h->user=f;h->diagnostic_budget=200u;f->gate=1u;f->capacity=20u;put(f,h->values.gp+0x94u,8,5u);put(f,h->values.gp+0x96u,16,0x3344u);put(f,0x2000b18eu,16,10u);put(f,0x2000b190u,16,3u);put(f,0x2000bdfau,16,7u);}
int main(void){fixture f;cb_host h;unsigned cases=0,total=0;
    setup(&f,&h);tsl9_callback_host_8614(&h,5u,0xabcd800fu);check(&f,h.result==0xabcd000fu && f.count==1u && h.values.sp==0x2000f000u && h.values.return_address==0x12345679u);total+=f.checks;cases++;
    setup(&f,&h);f.recv=0x20002000u;put(&f,f.recv,8,0x42u);tsl9_callback_host_8614(&h,5u,0x8000u);check(&f,f.count==2u && f.calls[1].source_site==0x8666u && f.calls[1].args[4]==0x42u && f.calls[1].args[0]==f.recv);total+=f.checks;cases++;
    setup(&f,&h);f.recv=0x20002000u;put(&f,f.recv,8,0xb0u);put(&f,f.recv+4u,8,9u);tsl9_callback_host_8614(&h,5u,0x8000u);check(&f,f.count==3u && f.calls[1].args[0]==f.recv+8u && f.calls[1].args[1]==9u);total+=f.checks;cases++;
    setup(&f,&h);tsl9_callback_host_8614(&h,0x12345678u,0x10008u);check(&f,h.result==0x10000u && f.count==1u && f.calls[0].args[0]==0x12345678u && f.calls[0].args[1]==0u && f.calls[0].args[2]==0x19de0u);total+=f.checks;cases++;
    setup(&f,&h);tsl9_callback_host_8614(&h,0x105u,1u);check(&f,h.result==0u && f.count==0u);total+=f.checks;cases++;
    setup(&f,&h);tsl9_callback_host_8614(&h,5u,0x80000001u);check(&f,h.result==0x80000000u && f.count==3u && get(&f,0x2000bdfau,16)==7u && get(&f,0x2000b18cu,8)==10u);total+=f.checks;cases++;
    setup(&f,&h);f.gate=3u;tsl9_callback_host_8614(&h,5u,1u);check(&f,f.count==1u && get(&f,0x2000b18eu,16)==0u);total+=f.checks;cases++;
    setup(&f,&h);f.capacity=2u;tsl9_callback_host_8614(&h,5u,1u);check(&f,get(&f,0x2000bdfau,16)==7u);total+=f.checks;cases++;
    setup(&f,&h);put(&f,0x2000b18cu,8,1u);tsl9_callback_host_8614(&h,5u,2u);check(&f,f.count==2u && f.calls[1].args[2]==2u && get(&f,0x2000b18cu,8)==0u);total+=f.checks;cases++;
    setup(&f,&h);put(&f,0x2000b18cu,8,1u);f.allocated=0x20003000u;f.gate=3u;tsl9_callback_host_8614(&h,5u,2u);check(&f,f.count==5u && get(&f,0x2000b190u,16)==10u && get(&f,0x2000b18cu,8)==1u && f.calls[4].args[1]==1u && f.calls[4].args[4]==7u);total+=f.checks;cases++;
    setup(&f,&h);tsl9_callback_host_8614(&h,5u,4u);check(&f,f.count==1u && f.calls[0].target_register==6u && f.calls[0].args[0]==0x3344u && f.calls[0].args[1]==12u && f.calls[0].args[2]==24u && f.calls[0].args[4]==200u && f.calls[0].args[5]==5u);total+=f.checks;cases++;
    setup(&f,&h);h.diagnostic_budget=1u;tsl9_callback_host_8614(&h,5u,1u);check(&f,h.flow==CB_UNKNOWN && h.effects==1u && f.count==0u);total+=f.checks;cases++;
    printf("{\"groups\":1,\"cases\":%u,\"checks\":%u}\n",cases,total);return 0;}
