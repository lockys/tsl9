#include "reference_copy.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct {uint32_t address;bc_value byte;} cell;
typedef struct {
    cell cells[512];unsigned used,count,fail_at;bc_flow fail_flow;int apply_failure;
    bc_value mmio;rp_request trace[4096];
} fixture;
static fixture f;static rp_model m;static unsigned checks,groups;
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"check %u line %d: %s\n",checks,__LINE__,#x);exit(1);}}while(0)
static bc_value w(uint32_t v){bc_value x={v,UINT32_MAX};return x;}
static bc_value unknown(void){bc_value x={0,0};return x;}
static cell *at(uint32_t a){unsigned i;for(i=0;i<f.used;i++)if(f.cells[i].address==a)return &f.cells[i];CHECK(f.used<512);f.cells[f.used].address=a;f.cells[f.used].byte=w(0);return &f.cells[f.used++];}
static bc_flow effect(void *context,const rp_request *q,bc_value *out){
    fixture *s=(fixture *)context;bc_flow flow=BC_RETURNED;
    CHECK(s==&f);CHECK(s->count<4096);s->trace[s->count++]=*q;
    if(s->fail_at==s->count){flow=s->fail_flow;if(!s->apply_failure)return flow;}
    if(q->kind==RP_READ32||q->kind==RP_WRITE32){
        CHECK(q->address.known==UINT32_MAX&&q->address.value==0x4002420c);
        if(q->kind==RP_READ32)*out=s->mmio;else s->mmio=q->data;
    }else if(q->kind==RP_READ8||q->kind==RP_WRITE8){
        if(q->address.known!=UINT32_MAX)return BC_HALT;
        if(q->kind==RP_READ8)*out=at(q->address.value)->byte;
        else{at(q->address.value)->byte.value=q->data.value&255;at(q->address.value)->byte.known=q->data.known&255;}
    }else CHECK(q->kind==RP_FENCE_I||q->kind==RP_RETURN);
    return flow;
}
static void fresh(void){rp_backend b;memset(&f,0,sizeof f);f.mmio=w(0xa5b6c7d8);b.context=&f;b.effect=effect;rp_init(&m,RP_DEC2023_133D3705,&b);}
static void fill(uint32_t a,unsigned n){unsigned i;for(i=0;i<n;i++)at(a+i)->byte=w(i+1);}
static void normal_and_guards(void){
    unsigned i;++groups;fresh();fill(0x1000,3);
    CHECK(rp_copy(&m,w(0x2000),w(0x1000),w(3),w(0x1235))==BC_RETURNED);
    CHECK(f.count==11&&m.operations==11&&m.stores_returned==3&&m.index==3&&m.index_set);
    CHECK(f.trace[0].kind==RP_READ32&&f.trace[0].pc==0x20000336);
    CHECK(f.trace[1].kind==RP_WRITE32&&f.trace[1].data.value==0&&f.trace[1].pc==0x2000033a);
    CHECK(f.trace[2].kind==RP_FENCE_I&&f.trace[2].pc==0x2000033e);
    for(i=0;i<3;i++){CHECK(at(0x2000+i)->byte.value==i+1);CHECK(f.trace[3+2*i].index==i);CHECK(f.trace[4+2*i].index==i+1);}
    CHECK(f.trace[9].pc==0x2000034e&&f.trace[10].pc==0x20000352);
    CHECK(f.mmio.value==0xa5b6c7d8&&m.result.value==0x2000&&m.return_target.value==0x1234);
    CHECK(f.trace[10].raw_target.value==0x1235&&f.trace[10].target.value==0x1234);
    fresh();CHECK(rp_copy(&m,w(0),unknown(),unknown(),w(4))==BC_RETURNED);CHECK(f.count==5&&!m.index_set&&m.result.value==0);
    fresh();CHECK(rp_copy(&m,w(1),w(0),unknown(),w(4))==BC_RETURNED);CHECK(f.count==5&&!m.index_set);
    fresh();CHECK(rp_copy(&m,w(1),w(2),w(0),w(4))==BC_RETURNED);CHECK(f.count==5&&m.index_set&&m.index==0);
    fresh();f.mmio.value=0xa0;f.mmio.known=0xf0;
    CHECK(rp_copy(&m,w(0),unknown(),unknown(),unknown())==BC_RETURNED);
    CHECK(f.mmio.value==0xa0&&f.mmio.known==0xf0&&f.trace[4].target.known==1);
}
static void forward_overlap_and_wrap(void){
    unsigned i;++groups;fresh();fill(0x1000,5);
    CHECK(rp_copy(&m,w(0x1001),w(0x1000),w(4),w(4))==BC_RETURNED);
    for(i=0;i<5;i++)CHECK(at(0x1000+i)->byte.value==1);
    fresh();fill(0x1000,5);CHECK(rp_copy(&m,w(0x1000),w(0x1001),w(4),w(4))==BC_RETURNED);
    for(i=0;i<4;i++)CHECK(at(0x1000+i)->byte.value==i+2);
    fresh();fill(0x1000,2);CHECK(rp_copy(&m,w(UINT32_MAX),w(0x1000),w(2),w(4))==BC_RETURNED);
    CHECK(at(UINT32_MAX)->byte.value==1&&at(0)->byte.value==2);
    CHECK(f.trace[6].address.value==0&&f.trace[6].index==2);
    fresh();at(UINT32_MAX)->byte=w(8);at(0)->byte=w(9);
    CHECK(rp_copy(&m,w(0x1000),w(UINT32_MAX),w(2),w(4))==BC_RETURNED);
    CHECK(at(0x1000)->byte.value==8&&at(0x1001)->byte.value==9);
}
static void knowledge(void){
    bc_value n;++groups;fresh();CHECK(rp_copy(&m,unknown(),w(2),w(0),w(4))==BC_HALT);
    CHECK(m.boundary==RP_CONDITION_UNKNOWN&&m.boundary_pc==0x20000342&&f.count==3&&f.mmio.value==0);
    fresh();CHECK(rp_copy(&m,w(1),unknown(),w(0),w(4))==BC_HALT);
    CHECK(m.boundary_pc==0x20000344&&f.count==3&&!m.index_set);
    fresh();CHECK(rp_copy(&m,w(1),w(2),unknown(),w(4))==BC_HALT);
    CHECK(m.boundary_pc==0x20000348&&f.count==3&&m.index_set);
    fresh();n.value=1;n.known=1;at(2)->byte.value=0x0a;at(2)->byte.known=0x0f;
    CHECK(rp_copy(&m,w(1),w(2),n,w(4))==BC_HALT);
    CHECK(m.boundary_pc==0x20000366&&f.count==5&&m.index==1&&m.stores_returned==1&&f.mmio.value==0);
    CHECK(at(1)->byte.value==0x0a&&at(1)->byte.known==0x0f);
    CHECK(f.trace[4].data.known==0xffffff0f);
    fresh();n.value=0x1000;n.known=0xfffffff0;
    CHECK(rp_copy(&m,n,w(2),w(1),w(4))==BC_HALT);
    CHECK(m.boundary==RP_PROVIDER_STOP&&m.last_request.kind==RP_WRITE8&&m.index==1&&m.stores_returned==0);
}
static void nonreturn_and_budget(void){
    unsigned fail,transfer;++groups;
    for(transfer=0;transfer<2;transfer++)for(fail=1;fail<=9;fail++){
        fresh();fill(0x1000,2);f.fail_at=fail;f.fail_flow=transfer?BC_TRANSFER:BC_HALT;
        CHECK(rp_copy(&m,w(0x2000),w(0x1000),w(2),w(4))==f.fail_flow);
        CHECK(f.count==fail&&m.operations==fail);
        CHECK(f.mmio.value==(fail<=2?0xa5b6c7d8u:(fail<=8?0u:0xa5b6c7d8u)));
        if(fail==5)CHECK(m.index==1&&m.stores_returned==0&&f.trace[4].kind==RP_WRITE8);
        CHECK(rp_copy(&m,w(0),w(0),w(0),w(4))==f.fail_flow&&f.count==fail);
    }
    fresh();fill(0x1000,2);f.fail_at=5;f.fail_flow=BC_TRANSFER;f.apply_failure=1;
    CHECK(rp_copy(&m,w(0x2000),w(0x1000),w(2),w(4))==BC_TRANSFER);
    CHECK(at(0x2000)->byte.value==1&&m.stores_returned==0&&f.mmio.value==0);
    rp_new_activation(&m);CHECK(f.mmio.value==0&&m.flow==BC_RETURNED);
    fresh();m.budget=7;fill(0x1000,3);
    CHECK(rp_copy(&m,w(0x2000),w(0x1000),w(65536),w(4))==BC_HALT);
    CHECK(m.boundary==RP_BUDGET&&m.boundary_pc==0x20000358&&f.count==7&&m.index==2&&m.stores_returned==2&&f.mmio.value==0);
    fresh();m.backend.effect=0;CHECK(rp_copy(&m,w(0),w(0),w(0),w(4))==BC_HALT);
    CHECK(m.boundary==RP_PROVIDER_MISSING&&m.operations==1&&f.count==0);
}
static void bindings(void){
    ub_model u;ub_request q;bc_request b;bc_value out;++groups;
    fresh();m.profile=RP_PHYSICAL_UNKNOWN;CHECK(rp_copy(&m,w(0),w(0),w(0),w(4))==BC_HALT&&f.count==0&&m.boundary==RP_BINDING);
    fresh();memset(&u,0,sizeof u);memset(&q,0,sizeof q);q.kind=UB_COPY;q.argc=3;q.pc=0x1c66;q.target=q.raw_target=w(0x20000332);q.continuation=w(0x1c68);u.ra=w(0x1c68);
    q.args[0]=w(0);q.args[1]=unknown();q.args[2]=unknown();u.sp=w(0x4000);u.s0=w(3);u.s1=w(5);u.s2=w(7);
    CHECK(rp_uid_copy(&m,&u,&q,&out)==BC_RETURNED&&out.value==0&&f.count==5);
    CHECK(u.sp.value==0x4000&&u.s0.value==3&&u.s1.value==5&&u.s2.value==7&&u.ra.value==0x1c68);
    fresh();q.raw_target=w(0x20000331);CHECK(rp_uid_copy(&m,&u,&q,&out)==BC_HALT&&f.count==0);
    fresh();q.raw_target=w(0x20000333);CHECK(rp_uid_copy(&m,&u,&q,&out)==BC_RETURNED&&f.count==5);
    fresh();q.continuation=w(0xdead);CHECK(rp_uid_copy(&m,&u,&q,&out)==BC_HALT&&f.count==0);
    fresh();memset(&b,0,sizeof b);b.kind=BC_INDIRECT_COPY;b.pc=0x225e;b.argc=3;b.target=b.raw_target=w(0x20000332);b.args[0]=w(0);b.args[1]=unknown();b.args[2]=unknown();
    CHECK(rp_boot_copy(&m,&b,&out)==BC_RETURNED&&f.trace[4].raw_target.value==0x2260);
    fresh();b.pc=0x225c;CHECK(rp_boot_copy(&m,&b,&out)==BC_HALT&&f.count==0);
}
int main(void){normal_and_guards();forward_overlap_and_wrap();knowledge();nonreturn_and_budget();bindings();printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;}
