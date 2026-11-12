/* Host-only abstract contract tests. No target code is executed. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "../v4160-1316a-default-candidate/model.c"

struct byte { uint32_t a; unsigned char v; };
struct event { uint32_t k, pc, a, b, c, d, e; };
struct state {
    struct byte mem[128]; unsigned n;
    struct event events[32]; unsigned count;
    unsigned stop, mutate, calls, tails, failed;
};
static unsigned char get(struct state *s, uint32_t a) {
    unsigned j; for (j=0;j<s->n;j++) if (s->mem[j].a==a) return s->mem[j].v;
    return 0;
}
static void put(struct state *s, uint32_t a, unsigned char v) {
    unsigned j; for (j=0;j<s->n;j++) if (s->mem[j].a==a) { s->mem[j].v=v; return; }
    if (s->n==128) { s->failed=1; return; }
    s->mem[s->n].a=a; s->mem[s->n++].v=v;
}
static void word(struct state *s, uint32_t a, uint32_t v) {
    unsigned j; for(j=0;j<4;j++) put(s,a+j,(unsigned char)(v>>(8*j)));
}
static uint32_t load(struct state *s, uint32_t a) {
    unsigned j; uint32_t v=0; for(j=0;j<4;j++) v|=(uint32_t)get(s,a+j)<<(8*j); return v;
}
static void logevent(struct state *s, uint32_t k, uint32_t pc, uint32_t a, uint32_t b, uint32_t c, uint32_t d, uint32_t e) {
    struct event *p; if(s->count==32) { s->failed=1; return; }
    p=&s->events[s->count++]; p->k=k;p->pc=pc;p->a=a;p->b=b;p->c=c;p->d=d;p->e=e;
}
static uint32_t rd(void *ctx,uint32_t pc,uint32_t a) {
    struct state *s=ctx; uint32_t v=load(s,a); logevent(s,1,pc,a,v,0,0,0); return v;
}
static void wr(void *ctx,uint32_t pc,uint32_t a,unsigned width,uint32_t v) {
    struct state *s=ctx; unsigned j;
    if(width!=1 && width!=2 && width!=4) { s->failed=1; return; }
    logevent(s,2,pc,a,width,v,0,0);
    for(j=0;j<width;j++) put(s,a+j,(unsigned char)(v>>(8*j)));
}
static int call(void *ctx,uint32_t pc,uint32_t t,uint32_t a,uint32_t b,uint32_t c) {
    struct state *s=ctx; s->calls++; logevent(s,3,pc,t,a,b,c,0);
    if(s->mutate && s->calls==1) { word(s,0x1054,0xfffffffc); word(s,0x4004c,0x3333); }
    return s->calls!=s->stop;
}
static void tail(void *ctx,uint32_t pc,uint32_t t) {
    struct state *s=ctx; s->tails++; logevent(s,4,pc,t,0,0,0,0);
}
#define R(pc,a,v) {1,pc,a,v,0,0,0}
#define W(pc,a,n,v) {2,pc,a,n,v,0,0}
#define C(pc,t,a,b,c) {3,pc,t,a,b,c,0}
#define T(pc,t) {4,pc,t,0,0,0,0}
#define PREFIX R(0x13172,0x40048,0x1111), C(0x13188,0x1110,0x2000c29c,0,112), W(0x1318e,0x2000c29e,2,0xfff), W(0x13194,0x2000c2a0,1,1), W(0x1319c,0x2000c2a4,2,257)
static const struct event normal[]={ PREFIX, R(0x131a4,0x1054,0xfffffffc), R(0x131a6,0x4004c,0x3333), C(0x131b4,0x3332,8,0x1a69c,4), T(0x131be,0x13138) };
static const struct event first[]={ R(0x13172,0x40048,0x1111), C(0x13188,0x1110,0x2000c29c,0,112) };
static const struct event second[]={ PREFIX, R(0x131a4,0x1054,0x8888), R(0x131a6,0x4004c,0x2223), C(0x131b4,0x2222,0x8894,0x1a69c,4) };
static const struct event alias0[]={ PREFIX, R(0x131a4,0x2000c29c,0x0fff0000), R(0x131a6,0x4004c,0x2223), C(0x131b4,0x2222,0x0fff000c,0x1a69c,4), T(0x131be,0x13138) };
static const struct event alias1[]={ PREFIX, R(0x131a4,0x2000c2a0,1), R(0x131a6,0x4004c,0x2223), C(0x131b4,0x2222,13,0x1a69c,4), T(0x131be,0x13138) };
static const struct event alias2[]={ PREFIX, R(0x131a4,0x2000c2a4,257), R(0x131a6,0x4004c,0x2223), C(0x131b4,0x2222,269,0x1a69c,4), T(0x131be,0x13138) };
static const struct event wrap[]={ PREFIX, R(0x131a4,0,0xfffffffc), R(0x131a6,0x4004c,0x2223), C(0x131b4,0x2222,8,0x1a69c,4), T(0x131be,0x13138) };
static int run(const char *name,uint32_t gp,unsigned stop,unsigned mutate,const struct event *want,unsigned count) {
    struct state s; struct interface i; unsigned j=0; volatile unsigned returned=0;
    memset(&s,0,sizeof s); s.stop=stop;s.mutate=mutate;
    word(&s,0x40048,0x1111);word(&s,0x4004c,0x2223);
    if(gp==0x1000) word(&s,0x1054,0x8888);
    if(gp==0xffffffac) word(&s,0,0xfffffffc);
    i.ctx=&s;i.read32=rd;i.store=wr;i.call=call;i.tail=tail;
    model_1316a(&i,gp); returned=1;
    if(!returned || s.failed || s.count!=count || s.calls!=(stop==1?1u:2u) || s.tails!=(stop?0u:1u)) goto fail;
    for(j=0;j<count;j++) {
        const struct event *x=&s.events[j], *y=&want[j];
        if(x->k!=y->k || x->pc!=y->pc || x->a!=y->a || x->b!=y->b || x->c!=y->c || x->d!=y->d || x->e!=y->e) goto fail;
    }
    return 0;
fail: fprintf(stderr,"FAIL %s at event %u (count %u expected %u)\n",name,j,s.count,count); return 1;
}
#define RUN(name,gp,stop,mutate,fixture) run(name,gp,stop,mutate,fixture,(unsigned)(sizeof(fixture)/sizeof((fixture)[0])))
int main(void) {
    int failures=0;
    failures+=RUN("mutate",0x1000,0,1,normal);
    failures+=RUN("first nonreturn",0x1000,1,0,first);
    failures+=RUN("second nonreturn",0x1000,2,0,second);
    failures+=RUN("alias first",0x2000c248,0,0,alias0);
    failures+=RUN("alias second",0x2000c24c,0,0,alias1);
    failures+=RUN("alias third",0x2000c250,0,0,alias2);
    failures+=RUN("wrap",0xffffffac,0,0,wrap);
    if(failures) return 1;
    puts("host model fixtures passed"); return 0;
}
