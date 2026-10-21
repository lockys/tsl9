#include "gatt_ingress.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define RB UINT32_C(0x20000000)
#define GP UINT32_C(0x20004000)
#define ATTR (RB+0x1000u)
#define UUID (RB+0x1100u)
#define EXPECTED (RB+0x1200u)
#define CHUNK (RB+0x2000u)
#define BUFFER UINT32_C(0x2000b9d8)
#define STATE (GP+156u)
#define LAST (GP+160u)
#define CMD (GP+164u)
#define SUM (GP+165u)
#define COUNT (GP+138u)
#define LENGTH (GP+142u)
static unsigned checks,groups;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
typedef struct {uint8_t mem[65536],known[65536];gi_request trace[20000];unsigned count,cut,dispatches,ccc;gi_flow cut_flow;uint32_t now,now_known;int change_after_dispatch,change_length_after_store;} fixture;
static fixture f,g;
static void put(fixture *x,uint32_t a,unsigned n,uint32_t v){unsigned i;CHECK(a>=RB && a-RB<=sizeof(x->mem)-n);for(i=0;i<n;i++){x->mem[a-RB+i]=(uint8_t)(v>>(8*i));x->known[a-RB+i]=255;}}
static uint32_t get(const fixture *x,uint32_t a,unsigned n){uint32_t v=0;unsigned i;for(i=0;i<n;i++)v|=(uint32_t)x->mem[a-RB+i]<<(8*i);return v;}
static gi_flow provider(void *ctx,const gi_request *q,gi_scalar *out){
    fixture *x=(fixture *)ctx;unsigned i;CHECK(x->count<20000);x->trace[x->count++]=*q;if(x->cut && x->count==x->cut)return x->cut_flow;
    out->value=0;out->known=UINT32_MAX;
    if(q->kind==GI_READ || q->kind==GI_WRITE){
        if(q->address<RB || q->address-RB>sizeof(x->mem)-q->width)return GI_HALT;
        if(q->kind==GI_READ){out->value=out->known=0;for(i=0;i<q->width;i++){out->value|=(uint32_t)x->mem[q->address-RB+i]<<(8*i);out->known|=(uint32_t)x->known[q->address-RB+i]<<(8*i);}}
        else{for(i=0;i<q->width;i++){x->mem[q->address-RB+i]=(uint8_t)(q->value>>(8*i));x->known[q->address-RB+i]=(uint8_t)(q->known>>(8*i));}if(x->change_length_after_store && q->address==BUFFER)put(x,LENGTH,2,1);}
    }else if(q->kind==GI_CLOCK){CHECK(q->target==0x81b0);out->value=x->now;out->known=x->now_known;}
    else if(q->kind==GI_CCC){x->ccc++;CHECK(q->target==0x40144 && q->args[5]==1);out->value=7;}
    else if(q->kind==GI_DISPATCH){x->dispatches++;CHECK(q->target==0x14056 && q->args[2]==BUFFER);if(x->change_after_dispatch){put(x,STATE,1,1);put(x,SUM,1,88);}}
    else CHECK(0);
    return GI_RETURNED;
}
static void reset(fixture *x,gi_model *m){gi_backend b;memset(x,0,sizeof(*x));memset(x->known,255,sizeof(x->known));x->now_known=UINT32_MAX;b.context=x;b.invoke=provider;gi_init(m,&b);m->gp=GP;m->gp_known=UINT32_MAX;put(x,ATTR,1,2);put(x,ATTR+4,4,UUID);put(x,UUID,2,0xabcd);put(x,EXPECTED,2,0xabcd);put(x,GP+36,4,EXPECTED);put(x,ATTR+10,2,42);put(x,GP+42,2,42);}
static gi_flow receive(gi_model *m,uint32_t c,unsigned n){return gi_receive(m,c,ATTR,CHUNK,n,37,99);}
static const gi_request *last_dispatch(const fixture *x){unsigned i=x->count;while(i){--i;if(x->trace[i].kind==GI_DISPATCH)return &x->trace[i];}CHECK(0);return NULL;}
static unsigned frame(fixture *x,uint8_t command,unsigned n){unsigned i;uint8_t sum=command;put(x,CHUNK,1,0x55);put(x,CHUNK+1,1,0x7f);put(x,CHUNK+2,1,command);put(x,CHUNK+3,1,n>>8);put(x,CHUNK+4,1,n&255);sum=(uint8_t)(sum+(n>>8)+(n&255));for(i=0;i<n;i++){uint8_t v=(uint8_t)(i*7u+3u);put(x,CHUNK+5+i,1,v);sum=(uint8_t)(sum+v);}put(x,CHUNK+5+n,1,sum);return n+6;}
static void guards(void){gi_model m;reset(&f,&m);put(&f,ATTR+8,1,32);CHECK(receive(&m,1,0)==GI_RETURNED && m.result.value==8 && f.count==1);reset(&f,&m);put(&f,ATTR,1,3);CHECK(receive(&m,1,0)==GI_RETURNED && m.result.value==0 && f.count==2);reset(&f,&m);put(&f,UUID,2,0x2902);CHECK(receive(&m,0x1234,17)==GI_RETURNED && f.ccc==1 && m.result.value==7);CHECK(f.trace[f.count-1].args[0]==0x1234 && f.trace[f.count-1].args[1]==ATTR && f.trace[f.count-1].args[2]==CHUNK && f.trace[f.count-1].args[3]==17 && f.trace[f.count-1].args[4]==37);reset(&f,&m);put(&f,UUID,2,0xabce);CHECK(receive(&m,1,0)==GI_RETURNED && !f.dispatches);reset(&f,&m);put(&f,ATTR+10,2,43);CHECK(receive(&m,1,0)==GI_RETURNED && !f.dispatches);groups++;}
static void fragments(void){gi_model m;unsigned n,i;reset(&f,&m);n=frame(&f,0x19,3);for(i=0;i<n;i++){CHECK(gi_receive(&m,100+i,ATTR,CHUNK+i,1,0,0)==GI_RETURNED);CHECK(f.dispatches==(i+1==n?1u:0u));}CHECK(last_dispatch(&f)->args[0]==100+n-1 && last_dispatch(&f)->args[1]==0x19 && last_dispatch(&f)->args[3]==3);CHECK(get(&f,STATE,1)==0 && get(&f,LENGTH,2)==3 && get(&f,COUNT,2)==3);CHECK(!memcmp(f.mem+BUFFER-RB,f.mem+CHUNK+5-RB,3));reset(&f,&m);n=frame(&f,0x19,0);memcpy(f.mem+CHUNK+n-RB,f.mem+CHUNK-RB,n);CHECK(receive(&m,1,n*2)==GI_RETURNED && f.dispatches==2);reset(&f,&m);n=frame(&f,0x19,2);f.mem[CHUNK+n-1-RB]^=1;CHECK(receive(&m,1,n)==GI_RETURNED && !f.dispatches && get(&f,STATE,1)==0);groups++;}
static void timeout_cases(void){gi_model m;reset(&f,&m);put(&f,STATE,1,3);put(&f,LAST,4,UINT32_MAX-100u);f.now=198;CHECK(receive(&m,1,0)==GI_RETURNED && get(&f,STATE,1)==3 && get(&f,LAST,4)==198);reset(&f,&m);put(&f,STATE,1,3);put(&f,LAST,4,UINT32_MAX-100u);f.now=199;CHECK(receive(&m,1,0)==GI_RETURNED && get(&f,STATE,1)==0 && get(&f,LAST,4)==199);groups++;}
static void bounds(void){gi_model m;unsigned n;reset(&f,&m);n=frame(&f,0x19,1040);CHECK(receive(&m,1,n)==GI_RETURNED && f.dispatches==1 && get(&f,COUNT,2)==1040);reset(&f,&m);put(&f,STATE,1,4);put(&f,LENGTH,2,0x400);put(&f,SUM,1,9);put(&f,COUNT,2,22);put(&f,CHUNK,1,0x11);CHECK(receive(&m,1,1)==GI_RETURNED && !f.dispatches && get(&f,STATE,1)==0 && get(&f,COUNT,2)==0 && get(&f,SUM,1)==26);reset(&f,&m);put(&f,STATE,1,5);put(&f,COUNT,2,1040);put(&f,SUM,1,9);put(&f,CHUNK,1,3);CHECK(receive(&m,1,1)==GI_RETURNED && get(&f,STATE,1)==0 && get(&f,COUNT,2)==1040 && get(&f,SUM,1)==9);reset(&f,&m);m.max_operations=15;CHECK(receive(&m,1,65536)==GI_OBSERVATION_LIMIT && m.boundary==GI_BUDGET && m.operations==15);groups++;}
static void live_effects(void){gi_model m;unsigned n;reset(&f,&m);n=frame(&f,0x19,0);f.change_after_dispatch=1;CHECK(receive(&m,1,n)==GI_RETURNED && f.dispatches==1 && get(&f,STATE,1)==0 && get(&f,SUM,1)==88);reset(&f,&m);put(&f,STATE,1,5);put(&f,LENGTH,2,2);put(&f,CHUNK,1,3);f.change_length_after_store=1;CHECK(receive(&m,1,1)==GI_RETURNED && get(&f,STATE,1)==6 && get(&f,COUNT,2)==1);reset(&f,&m);put(&f,STATE,1,1);put(&f,CHUNK,1,0x55);CHECK(receive(&m,1,1)==GI_RETURNED && get(&f,STATE,1)==0);groups++;}
static void unknowns(void){gi_model m;reset(&f,&m);f.known[ATTR+8-RB]=0;CHECK(receive(&m,1,0)==GI_HALT && f.count==1);reset(&f,&m);m.gp_known=0;CHECK(receive(&m,1,0)==GI_HALT);reset(&f,&m);f.now_known=0;CHECK(receive(&m,1,0)==GI_HALT && get(&f,LAST,4)==0);reset(&f,&m);put(&f,STATE,1,2);f.known[CHUNK-RB]=0;CHECK(receive(&m,1,1)==GI_HALT && get(&f,STATE,1)==3 && f.known[CMD-RB]==0);reset(&f,&m);f.known[ATTR+8-RB]=32;CHECK(receive(&m,1,0)==GI_RETURNED);reset(&f,&m);put(&f,ATTR,1,3);f.known[ATTR-RB]=1;CHECK(receive(&m,1,0)==GI_RETURNED && f.count==2);reset(&f,&m);m.gp_known=0;put(&f,UUID,2,0x2902);CHECK(receive(&m,1,0)==GI_RETURNED && f.ccc==1);reset(&f,&m);put(&f,STATE,1,7);put(&f,COUNT,2,8);put(&f,SUM,1,9);CHECK(receive(&m,1,1)==GI_RETURNED && get(&f,STATE,1)==0 && get(&f,COUNT,2)==8 && get(&f,SUM,1)==9);groups++;}
static void cuts(void){gi_model m;unsigned n,end,i,mode;reset(&g,&m);n=frame(&g,0x19,2);CHECK(receive(&m,1,n)==GI_RETURNED);end=g.count;for(mode=0;mode<2;mode++)for(i=1;i<=end;i++){reset(&f,&m);n=frame(&f,0x19,2);f.cut=i;f.cut_flow=mode?GI_TRANSFER:GI_HALT;CHECK(receive(&m,1,n)==f.cut_flow && f.count==i);CHECK(!memcmp(f.trace,g.trace,i*sizeof(gi_request)));if(i==end)CHECK(f.dispatches==1 && get(&f,STATE,1)==6);}reset(&f,&m);put(&f,UUID,2,0x2902);f.cut=5;f.cut_flow=GI_TRANSFER;CHECK(receive(&m,1,0)==GI_TRANSFER && m.result.known==0);groups++;}
int main(void){guards();fragments();timeout_cases();bounds();live_effects();unknowns();cuts();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u,\"synthetic_backend_only\":true}\n",groups,checks);return 0;}
