/* Independent named-effect fixtures derived from sealed original TX contracts.
 * Numeric addresses are keys in sparse synthetic byte memory, never pointers.
 * This is an algorithm/effect oracle, not an RV32 instruction interpreter. */
#include "tx_native.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define B UINT32_C(0x2000b18c)
#define GP UINT32_C(0x21000000)
#define SP UINT32_C(0x22001000)
#define SRC UINT32_C(0x23000000)
#define CAP 12000u
typedef struct cell {uint32_t a;unsigned char v;} cell;
typedef struct mem {cell c[CAP];unsigned n;} mem;
typedef struct fixture {
    uint32_t context,command,length,source,n,live_source,live_command,live_context,live_gp,live_sp;
    uint32_t g1,g2,handle0,handle1,budget,stop_site,unknown_site;
    int mutate,overlap,frame_alias,frame_edit,register_edit,gate_halt,tail_transfer;
} fixture;
typedef struct state {
    fixture f;mem memory;tx_event expected[CAP];unsigned count,pos,gate_count;
    uint32_t expected_sp,expected_ra,expected_s0,expected_a2,expected_value;
    tx_flow expected_flow;int tail,budget;
} state;
static unsigned checks,cases;
static void check(int v,int line){++checks;if(!v){fprintf(stderr,"independent failure line %d case %u\n",line,cases);exit(1);}}
#define OK(v) check((v),__LINE__)
static unsigned char get8(const mem *m,uint32_t a){unsigned i;for(i=m->n;i>0u;--i)if(m->c[i-1u].a==a)return m->c[i-1u].v;return (unsigned char)(a^(a>>8)^0xa7u);}
static void put8(mem *m,uint32_t a,uint32_t v){unsigned i;for(i=0;i<m->n;++i)if(m->c[i].a==a){m->c[i].v=(unsigned char)v;return;}OK(m->n<CAP);m->c[m->n].a=a;m->c[m->n++].v=(unsigned char)v;}
static uint32_t get(const mem *m,uint32_t a,unsigned w){uint32_t v=0;unsigned i;for(i=0;i<w;++i)v|=(uint32_t)get8(m,a+i)<<(i*8u);return v;}
static void put(mem *m,uint32_t a,unsigned w,uint32_t v){unsigned i;for(i=0;i<w;++i)put8(m,a+i,v>>(8u*i));}
static uint32_t mask(unsigned w){return w==1u?255u:w==2u?65535u:UINT32_MAX;}
static tx_event *event(state *s,tx_kind k,uint32_t site,uint32_t a,unsigned w,uint32_t v){tx_event *e;OK(s->count<CAP);e=&s->expected[s->count++];memset(e,0,sizeof(*e));e->kind=k;e->site=site;e->address=a;e->width=w;e->value=v&mask(w);e->value_known=1;return e;}
static uint32_t rd(state *s,mem *m,uint32_t site,uint32_t a,unsigned w){uint32_t v=get(m,a,w);event(s,TX_READ,site,a,w,v);return v;}
static void wr(state *s,mem *m,uint32_t site,uint32_t a,unsigned w,uint32_t v){event(s,TX_WRITE,site,a,w,v);put(m,a,w,v);}
static void newframe(mem *m,uint32_t sp){put(m,sp+28u,4u,0x70000001u);put(m,sp+24u,4u,0x89abcdefu);put(m,sp+20u,4u,0x10203040u);put(m,sp+16u,4u,0x50607080u);put(m,sp+12u,4u,0x90a0b0c0u);}
static void gate_memory(state *s,mem *m,unsigned gate){if(gate==1u&&s->f.mutate){put(m,s->f.live_gp+0x9au,2u,s->f.live_context);put(m,0x4013cu,4u,0x60000003u);if(s->f.live_sp!=SP-32u)newframe(m,s->f.live_sp);}}
static void read_memory_change(state *s,mem *m,uint32_t site){if(s->f.frame_edit&&site==0x8b56u){put(m,SP-4u,4u,0x71111113u);put(m,SP-8u,4u,0xfedcba98u);}}
static void call(state *s,uint32_t site,uint32_t raw,uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3){tx_event *e=event(s,TX_GATE_CALL,site,0u,0u,0u);e->raw_target=raw;e->target=raw&~1u;e->args[0]=a0;e->args[1]=a1;e->args[2]=a2;e->args[3]=a3;e->args_known=15u;}
static void restore_failure(state *s,mem *m,uint32_t sp){s->expected_ra=rd(s,m,0x8abeu,sp+28u,4u);s->expected_s0=rd(s,m,0x8ac0u,sp+24u,4u);(void)rd(s,m,0x8ac2u,sp+20u,4u);(void)rd(s,m,0x8ac4u,sp+16u,4u);(void)rd(s,m,0x8ac6u,sp+12u,4u);s->expected_sp=sp+32u;s->expected_flow=TX_RETURNED;}
static void expected(state *s){
    mem *m=(mem *)malloc(sizeof(mem));fixture *f=&s->f;uint32_t gp=GP,sp=SP-32u,context=f->context,n=f->length,src=f->source,cmd=f->command,a2=src,a3=n,result=context,lane=0u,handle,raw,base,p,checksum,i,value,slot;
    OK(m!=NULL);*m=s->memory;s->expected_flow=TX_RETURNED;s->expected_value=context;s->expected_a2=src;s->expected_sp=SP;s->expected_ra=0x70000001u;s->expected_s0=0x89abcdefu;
    if(f->length>1039u){free(m);return;}
    wr(s,m,0x8a60u,sp+24u,4u,0x89abcdefu);wr(s,m,0x8a62u,sp+20u,4u,0x10203040u);wr(s,m,0x8a64u,sp+16u,4u,0x50607080u);wr(s,m,0x8a66u,sp+12u,4u,0x90a0b0c0u);wr(s,m,0x8a68u,sp+28u,4u,0x70000001u);
    handle=rd(s,m,0x8a6au,gp+0x96u,2u);
    if(f->register_edit){s->expected_flow=TX_UNKNOWN;free(m);return;}
    if(handle==context&&handle!=0xfffeu){
        raw=rd(s,m,0x8a86u,0x4013cu,4u);call(s,0x8a8eu,raw,context,gp+128u,a2,a3);
        if(f->gate_halt){s->expected_flow=TX_HALT;s->expected_sp=sp;free(m);return;}
        result=f->g1;
        if(f->mutate){gate_memory(s,m,1u);gp=f->live_gp;sp=f->live_sp;n=f->n;src=f->live_source;cmd=f->live_command;context=f->live_context;a2=0x11223344u;a3=0x55667788u;}
        if(result==1u)goto selected;
    }
    handle=rd(s,m,0x8a96u,gp+0x9au,2u);
    if(handle!=context||context==0xfffeu){s->expected_value=result;s->expected_a2=a2;restore_failure(s,m,sp);free(m);return;}
    raw=rd(s,m,0x8aaau,0x4013cu,4u);call(s,0x8ab4u,raw,context,gp+128u,a2,a3);result=f->g2;lane=1u;
    if(result!=1u){s->expected_value=result;s->expected_a2=1u;restore_failure(s,m,sp);free(m);return;}
selected:
    base=B+1062u*lane;p=base+6u;checksum=(n&255u)+(n>>8)+cmd;
    wr(s,m,0x8aecu,p,2u,0x7f55u);wr(s,m,0x8af0u,p+4u,1u,n);wr(s,m,0x8afau,p+3u,1u,n>>8);wr(s,m,0x8b00u,p+2u,1u,cmd);checksum&=255u;
    for(i=0u;(i&65535u)<n;++i){
        if(i>=f->budget){s->expected_flow=TX_UNKNOWN;s->budget=1;s->expected_sp=sp;free(m);return;}
        value=rd(s,m,0x8b56u,src+i,1u);read_memory_change(s,m,0x8b56u);
        if(f->unknown_site==0x8b56u&&i==1u){s->expected[s->count-1u].value_known=0;s->expected_flow=TX_UNKNOWN;s->expected_sp=sp;free(m);return;}
        checksum=(checksum+value)&255u;wr(s,m,0x8b62u,p+5u+i,1u,value);
    }
    wr(s,m,0x8b16u,p+n+5u,1u,checksum);
    s->expected_ra=rd(s,m,0x8b26u,sp+28u,4u);(void)rd(s,m,0x8b28u,sp+20u,4u);(void)rd(s,m,0x8b2au,sp+16u,4u);(void)rd(s,m,0x8b2cu,sp+12u,4u);
    wr(s,m,0x8b32u,base+2u,2u,n+6u);wr(s,m,0x8b36u,base+4u,2u,0u);
    s->expected_s0=rd(s,m,0x8b40u,sp+24u,4u);slot=rd(s,m,0x8b46u,0x40050u,4u);value=rd(s,m,0x8b4au,gp+0x94u+4u*lane,1u);
    {tx_event *e=event(s,TX_TAIL_CALL,0x8b50u,0u,0u,0u);e->raw_target=slot;e->target=slot&~1u;e->args[0]=value;e->args[1]=1u;e->args[2]=gp+0x94u+4u*lane;e->args[3]=B;e->args_known=15u;}
    s->tail=1;s->expected_sp=sp+32u;s->expected_value=0xcafebabeu;s->expected_a2=gp+0x94u+4u*lane;s->expected_flow=f->tail_transfer?TX_TRANSFER:TX_RETURNED;free(m);
}
static tx_flow provide(tx_host *h,tx_event *e,void *user){
    state *s=(state *)user;tx_event *x;unsigned i;uint32_t value;
    OK(s->pos<s->count);x=&s->expected[s->pos++];OK(e->kind==x->kind);OK(e->site==x->site);OK(e->address==x->address);OK(e->width==x->width);
    if(e->kind==TX_READ){value=get(&s->memory,e->address,e->width);OK(value==x->value);e->value=value;e->value_known=x->value_known;read_memory_change(s,&s->memory,e->site);if(s->f.register_edit&&e->site==0x8a6au)h->regs[3]^=4u;}
    else if(e->kind==TX_WRITE){OK(e->value_known==1);OK(e->value==x->value);put(&s->memory,e->address,e->width,e->value);}
    else {
        OK(e->raw_target==x->raw_target);OK(e->target==x->target);OK(e->args_known==15u);for(i=0;i<4u;++i)OK(e->args[i]==x->args[i]);
        if(e->kind==TX_GATE_CALL){++s->gate_count;OK(h->regs[1]==e->site+2u);if(s->f.gate_halt)return TX_HALT;
            if(e->site==0x8a8eu&&s->f.mutate){tx_set(h,3,s->f.live_gp);tx_set(h,2,s->f.live_sp);tx_set(h,8,s->f.n);tx_set(h,9,s->f.live_source);tx_set(h,18,s->f.live_context);tx_set(h,19,s->f.live_command);tx_set(h,12,0x11223344u);tx_set(h,13,0x55667788u);gate_memory(s,&s->memory,1u);}
            tx_set(h,10,e->site==0x8a8eu?s->f.g1:s->f.g2);
        }else{OK(h->regs[1]==s->expected_ra);OK(h->regs[2]==s->expected_sp);OK(h->regs[8]==s->expected_s0);tx_set(h,10,0xcafebabeu);if(s->f.tail_transfer)return TX_TRANSFER;}
    }
    return TX_CONTINUE;
}
static fixture normal(uint32_t n){fixture f;memset(&f,0,sizeof(f));f.context=0x1234u;f.command=0xfedcbaa5u;f.length=n;f.source=SRC;f.n=n;f.live_source=SRC;f.live_command=f.command;f.live_context=f.context;f.live_gp=GP;f.live_sp=SP-32u;f.g1=1u;f.g2=1u;f.handle0=f.context;f.handle1=f.context;f.budget=2048u;return f;}
static void run(fixture f){
    state *s=(state *)calloc(1u,sizeof(state));tx_host h;tx_result r;unsigned i;
    OK(s!=NULL);++cases;s->f=f;put(&s->memory,GP+0x96u,2u,f.handle0);put(&s->memory,GP+0x9au,2u,f.handle1);put(&s->memory,0x4013cu,4u,0x60000001u);put(&s->memory,0x40050u,4u,0x60001003u);put(&s->memory,GP+0x94u,1u,0xe5u);put(&s->memory,GP+0x98u,1u,0xacu);
    expected(s);tx_host_init(&h,provide,s);h.known=UINT32_MAX;for(i=0;i<32u;++i)h.regs[i]=0x55000000u+i;h.regs[0]=0u;h.regs[1]=0x70000001u;h.regs[2]=SP;h.regs[3]=GP;h.regs[8]=0x89abcdefu;h.regs[9]=0x10203040u;h.regs[18]=0x50607080u;h.regs[19]=0x90a0b0c0u;h.loop_budget=f.budget;
    r=tsl9_ota_tx_8a56(&h,f.context,f.command,f.source,f.length);OK(s->pos==s->count);OK(r.flow==s->expected_flow);OK(r.tail_delegated==s->tail);OK(r.budget_exhausted==s->budget);
    if(r.flow==TX_RETURNED||r.flow==TX_TRANSFER){OK(r.value_known);OK(r.value==s->expected_value);OK(h.regs[2]==s->expected_sp);OK(h.regs[8]==s->expected_s0);OK(h.regs[12]==s->expected_a2);OK(r.link_known);OK(r.raw_link==s->expected_ra);OK(r.link==(s->expected_ra&~1u));}
    if(s->tail){OK(r.raw_target==0x60001003u);OK(r.target==0x60001002u);}
    if(f.register_edit)OK(r.unsupported_memory_register_mutation);
    if(f.length>1039u){OK(h.event_count==0u);OK(h.regs[15]==1039u);}
    free(s);
}
int main(void){fixture f;unsigned i;const uint32_t lengths[]={0u,1u,2u,7u,255u,256u,1039u};
    for(i=0u;i<sizeof(lengths)/sizeof(lengths[0]);++i){f=normal(lengths[i]);run(f);f.handle0=9u;run(f);}
    f=normal(1040u);run(f);f=normal(65536u);run(f);f=normal(UINT32_MAX);run(f);
    f=normal(4u);f.handle0=9u;f.handle1=10u;run(f);
    f=normal(4u);f.context=0xfffeu;f.handle0=f.context;f.handle1=f.context;run(f);
    f=normal(4u);f.g1=7u;f.mutate=1;f.live_gp=GP+0x1000u;f.live_context=0x4567u;f.n=5u;f.live_source=SRC+0x100u;f.live_command=0x876543e1u;run(f);f.g2=9u;run(f);
    f=normal(4u);f.g1=7u;f.handle1=9u;run(f);
    f=normal(1u);f.mutate=1;f.n=1041u;run(f);f.n=65536u;f.budget=3u;run(f);
    f=normal(5u);f.mutate=1;f.live_source=B+10u;run(f);
    f=normal(5u);f.mutate=1;f.live_sp=B-22u;run(f);
    f=normal(5u);f.frame_edit=1;run(f);
    f=normal(5u);f.unknown_site=0x8b56u;run(f);
    f=normal(5u);f.register_edit=1;run(f);
    f=normal(5u);f.gate_halt=1;run(f);
    f=normal(5u);f.tail_transfer=1;run(f);
    printf("{\"passed\":true,\"groups\":4,\"cases\":%u,\"checks\":%u,\"target_execution\":false}\n",cases,checks);return 0;
}
