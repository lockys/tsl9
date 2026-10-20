#include "can_receive.h"
#include <string.h>
#define ALL UINT32_MAX
#define A(x) (TF_RAM_BASE+UINT32_C(x))
#define Q A(0xc034)
#define AUTH A(0xc790)
typedef cr_scalar val;
typedef struct {uint32_t va,constant;unsigned test;uint32_t yes,no;} node;
static const node nodes[]={
 {0x14b30,819u,0,0x14f38,0x14b34},
 {0x14b34,819u,2,0x14c96,0x14b3c},
 {0x14b3c,602u,0,0x14e9a,0x14b40},
 {0x14b40,602u,2,0x14bee,0x14b48},
 {0x14b48,505u,0,0x14e58,0x14b4c},
 {0x14b4c,505u,2,0x14b9c,0x14b54},
 {0x14b54,259u,0,0x14e30,0x14b58},
 {0x14b58,259u,2,0x14b78,0x14b60},
 {0x14b60,130u,0,0x14e0e,0x14b68},
 {0x14b68,258u,0,0x14e1a,0x14b6c},
 {0x14b78,297u,0,0x14e3c,0x14b80},
 {0x14b80,306u,0,0x14e48,0x14b88},
 {0x14b88,280u,1,0x14b6c,0x14b8c},
 {0x14b9c,568u,0,0x14e70,0x14ba0},
 {0x14ba0,568u,2,0x14bca,0x14ba8},
 {0x14ba8,524u,0,0x14e64,0x14bb0},
 {0x14bb0,553u,1,0x14b6c,0x14bb4},
 {0x14bca,585u,0,0x14e7c,0x14bd2},
 {0x14bd2,599u,0,0x14e8e,0x14bda},
 {0x14bda,579u,1,0x14b6c,0x14bde},
 {0x14bee,694u,0,0x14ee2,0x14bf2},
 {0x14bf2,694u,2,0x14c42,0x14bfa},
 {0x14bfa,627u,0,0x14eb2,0x14bfe},
 {0x14bfe,627u,2,0x14c24,0x14c06},
 {0x14c06,605u,0,0x14ea6,0x14c10},
 {0x14c10,614u,1,0x14b6c,0x14c14},
 {0x14c24,659u,0,0x14ed0,0x14c2c},
 {0x14c2c,692u,0,0x14edc,0x14c34},
 {0x14c34,658u,1,0x14b6c,0x14c38},
 {0x14c42,786u,0,0x14efe,0x14c46},
 {0x14c46,786u,2,0x14c72,0x14c4e},
 {0x14c4e,741u,0,0x14eee,0x14c56},
 {0x14c56,755u,0,0x14ef2,0x14c5e},
 {0x14c5e,737u,1,0x14b6c,0x14c62},
 {0x14c72,801u,0,0x14f0a,0x14c7a},
 {0x14c7a,818u,0,0x14f16,0x14c82},
 {0x14c82,799u,1,0x14b6c,0x14c86},
 {0x14c96,991u,0,0x1501e,0x14c9a},
 {0x14c9a,991u,2,0x14d56,0x14ca2},
 {0x14ca2,925u,0,0x14f78,0x14ca6},
 {0x14ca6,925u,2,0x14d04,0x14cae},
 {0x14cae,826u,0,0x14f66,0x14cb2},
 {0x14cb2,826u,2,0x14cd6,0x14cba},
 {0x14cba,820u,0,0x14f44,0x14cc2},
 {0x14cc2,825u,1,0x14b6c,0x14cc6},
 {0x14cd6,880u,0,0x15090,0x14cde},
 {0x14cde,921u,0,0x150aa,0x14ce6},
 {0x14ce6,850u,1,0x14b6c,0x14cea},
 {0x14d04,962u,0,0x14fa0,0x14d08},
 {0x14d08,962u,2,0x14d2c,0x14d10},
 {0x14d10,947u,0,0x14f84,0x14d18},
 {0x14d18,950u,1,0x14b6c,0x14d1c},
 {0x14d2c,978u,0,0x14fde,0x14d34},
 {0x14d34,984u,0,0x14fd2,0x14d3c},
 {0x14d3c,963u,1,0x14b6c,0x14d40},
 {0x14d56,1025u,0,0x15040,0x14d5a},
 {0x14d5a,1025u,2,0x14db8,0x14d62},
 {0x14d62,1001u,0,0x14ff0,0x14d66},
 {0x14d66,1001u,2,0x14d8a,0x14d6e},
 {0x14d6e,994u,0,0x14fe4,0x14d76},
 {0x14d76,995u,1,0x14b6c,0x14d7a},
 {0x14d8a,1021u,0,0x15030,0x14d92},
 {0x14d92,1022u,0,0x15024,0x14d9a},
 {0x14d9a,1013u,1,0x14b6c,0x14d9e},
 {0x14db8,1267u,0,0x15070,0x14dbc},
 {0x14dbc,1267u,2,0x14de8,0x14dc4},
 {0x14dc4,1250u,0,0x1504c,0x14dcc},
 {0x14dcc,1251u,0,0x1505e,0x14dd4},
 {0x14dd4,1029u,1,0x14b6c,0x14dd8},
 {0x14de8,1657u,0,0x1507a,0x14df0},
 {0x14df0,2047u,0,0x150b6,0x14df8},
 {0x14df8,1656u,1,0x14b6c,0x14dfc}
};
static const uint32_t mode_table[7]={0x14b1c,0x14b28,0x15162,0x15182,0x151a2,0x151e2,0x15222};
static const uint32_t leaves[]={0x14e0e,0x14e1a,0x14e30,0x14b8c,0x14e3c,0x14e48,0x14e58,0x14e64,0x14bb4,0x14e70,0x14bde,0x14e7c,0x14e8e,0x14e9a,0x14ea6,0x14c14,0x14eb2,0x14c38,0x14ed0,0x14edc,0x14ee2,0x14c62,0x14eee,0x14ef2,0x14efe,0x14c86,0x14f0a,0x14f16,0x14f38,0x14f44,0x14cc6,0x14f66,0x14cea,0x15090,0x150aa,0x14f78,0x14f84,0x14d1c,0x14fa0,0x14d40,0x14fde,0x14fd2,0x1501e,0x14fe4,0x14d7a,0x14ff0,0x14d9e,0x15030,0x15024,0x15040,0x14dd8,0x1504c,0x1505e,0x15070,0x14dfc,0x1507a,0x150b6};

static val constant(uint32_t x){val r={x,ALL};return r;}
static val truncn(val x,unsigned n){uint32_t mask=n==32?ALL:((1u<<n)-1u);x.value&=mask;x.known=(x.known&mask)|~mask;return x;}
static val masked(val x,uint32_t mask){x.value&=mask;x.known|=~mask;return x;}
static val logical_or(val a,val b){val r={a.value|b.value,(a.known&b.known)|(a.value&a.known)|(b.value&b.known)};return r;}
static val shl(val a,unsigned n){val r={a.value<<n,(a.known<<n)|((1u<<n)-1u)};return r;}
static val shr(val a,unsigned n){val r={a.value>>n,(a.known>>n)|(ALL<<(32-n))};return r;}
static val add(val a,val b){
 val r={a.value+b.value,0};unsigned i,carries=1;
 for(i=0;i<32;i++){unsigned av=((a.known>>i)&1)?(1u<<((a.value>>i)&1)):3u,bv=((b.known>>i)&1)?(1u<<((b.value>>i)&1)):3u,aa,bb,cc,sums=0,next=0;
  for(aa=0;aa<2;aa++)for(bb=0;bb<2;bb++)for(cc=0;cc<2;cc++)if((av&(1u<<aa))&&(bv&(1u<<bb))&&(carries&(1u<<cc))){unsigned s=aa+bb+cc;sums|=1u<<(s&1);next|=1u<<(s>>1);}
  if(sums==1||sums==2)r.known|=1u<<i;carries=next;
 }return r;
}
static int halt(cr_model*m,uint32_t va,uint32_t a,uint32_t need){m->flow=CR_HALT;m->boundary_va=va;m->boundary_address=a;m->needed_mask=need;return 0;}
static int full(cr_model*m,val x,uint32_t va,uint32_t a){return x.known==ALL?1:halt(m,va,a,~x.known);}
static cr_buffer rb(uint32_t a){cr_buffer b;memset(&b,0,sizeof(b));b.kind=CR_RAM;b.address=a;return b;}
static cr_buffer vb(uint8_t*d,uint8_t*k,uint32_t n){cr_buffer b;memset(&b,0,sizeof(b));b.kind=CR_VIEW;b.data=d;b.known=k;b.available=n;return b;}
static cr_buffer sub(cr_buffer b,uint32_t n){if(b.kind==CR_RAM)b.address+=n;else if(b.kind==CR_VIEW){if(n>b.available){b.data=b.known=NULL;b.available=0;}else{if(b.data)b.data+=n;if(b.known)b.known+=n;b.available-=n;}}return b;}
static uint32_t address(cr_buffer b,uint32_t n){return b.kind==CR_RAM?b.address+n:0;}
static int span(cr_model*m,cr_buffer b,uint32_t off,unsigned n,uint32_t va){
 if(b.kind==CR_RAM){uint32_t a=b.address+off;if(a<TF_RAM_BASE||n>TF_RAM_SIZE||a-TF_RAM_BASE>TF_RAM_SIZE-n||(n>1&&a%n))return halt(m,va,a,ALL);}
 else if(b.kind!=CR_VIEW||!b.data||!b.known||off>b.available||n>b.available-off)return halt(m,va,0,ALL);return 1;
}
static int load(cr_model*m,cr_buffer b,uint32_t off,unsigned n,uint32_t va,val*out){
 unsigned i;val r={0,0};if(!span(m,b,off,n,va))return 0;
 for(i=0;i<n;i++){uint32_t ix=b.kind==CR_RAM?b.address+off+i-TF_RAM_BASE:off+i;uint8_t v=b.kind==CR_RAM?m->memory->ram[ix]:b.data[ix],k=b.kind==CR_RAM?m->memory->known[ix]:b.known[ix];r.value|=(uint32_t)v<<(8*i);r.known|=(uint32_t)k<<(8*i);}*out=truncn(r,n*8);return 1;
}
static int store(cr_model*m,cr_buffer b,uint32_t off,unsigned n,uint32_t va,val x){
 unsigned i;if(!span(m,b,off,n,va))return 0;
 for(i=0;i<n;i++){uint32_t ix=b.kind==CR_RAM?b.address+off+i-TF_RAM_BASE:off+i;uint8_t v=(uint8_t)(x.value>>(8*i)),k=(uint8_t)(x.known>>(8*i));if(b.kind==CR_RAM){m->memory->ram[ix]=v;m->memory->known[ix]=k;}else{b.data[ix]=v;b.known[ix]=k;}}return 1;
}
static int nz(cr_model*m,val x,uint32_t va,uint32_t a,int*out){if(x.value&x.known){*out=1;return 1;}if(!full(m,x,va,a))return 0;*out=0;return 1;}
static int eq(cr_model*m,val x,uint32_t expected,uint32_t va,uint32_t a,int*out){if((x.value^expected)&x.known){*out=0;return 1;}if(!full(m,x,va,a))return 0;*out=1;return 1;}
static int gt(cr_model*m,val x,uint32_t bound,uint32_t va,uint32_t a,int*out){uint32_t lo=x.value&x.known,hi=lo|~x.known;if(lo>bound){*out=1;return 1;}if(hi<=bound){*out=0;return 1;}return halt(m,va,a,~x.known);}
static void request(cr_request*q,cr_operation op,uint32_t va,uint32_t target){memset(q,0,sizeof(*q));q->operation=op;q->va=va;q->target=target;q->known=ALL;}
static void arg(cr_request*q,unsigned i,val v){q->arguments[i]=v.value;q->argument_known[i]=v.known;}
static int invoke(cr_model*m,cr_request*q,val*out){
 cr_result r;cr_flow f;m->last_request=*q;if(q->source.kind==CR_VIEW)m->last_request.source.data=m->last_request.source.known=NULL;if(q->destination.kind==CR_VIEW)m->last_request.destination.data=m->last_request.destination.known=NULL;
 ++m->operations;if(!m->backend.invoke)return halt(m,q->va,q->target,0);memset(&r,0,sizeof(r));f=m->backend.invoke(m->backend.context,m,q,&r);
 if(f!=CR_RETURNED){if(f==CR_TRANSFER)m->flow=CR_TRANSFER;else halt(m,q->va,q->target,0);return 0;}
 if(q->operation==CR_COPY&&!r.memory_effects)return halt(m,q->va,q->target,0);if(out){out->value=r.value;out->known=r.known;}return 1;
}
static int copy(cr_model*m,uint32_t va,cr_buffer source,cr_buffer dest,val n){cr_request q;request(&q,CR_COPY,va,0x4004c);q.slot=76;q.count=3;q.source=source;q.destination=dest;q.length=n.value;arg(&q,0,dest.kind==CR_RAM?constant(dest.address):constant(0));q.argument_known[0]=dest.kind==CR_RAM?ALL:0;arg(&q,1,source.kind==CR_RAM?constant(source.address):constant(0));q.argument_known[1]=source.kind==CR_RAM?ALL:0;arg(&q,2,n);return invoke(m,&q,NULL);}
static int cache(cr_model*m,val direction,val index,cr_buffer record){
 val at=add(constant(A(0xc1b4)),add(shl(index,2),shl(index,3)));int out;
 if(!nz(m,direction,0x82ba,0,&out)||!full(m,at,0x82c0,at.value))return 0;
 return copy(m,0x82c0,out?rb(at.value):record,out?record:rb(at.value),constant(12));
}
static int mmio(cr_model*m,uint32_t va,uint32_t target,unsigned width,val*out){cr_request q;request(&q,CR_MMIO_READ,va,target);q.width=width;if(!invoke(m,&q,out))return 0;*out=truncn(*out,width);return 1;}
static int io_write(cr_model*m,uint32_t va,uint32_t target,unsigned width,val x){cr_request q;uint32_t mask=width==32?ALL:(1u<<width)-1;request(&q,CR_MMIO_WRITE,va,target);q.width=width;q.value=x.value&mask;q.known=x.known&mask;return invoke(m,&q,NULL);}
static int csr(cr_model*m,int set){cr_request q;request(&q,set?CR_CSR_SET:CR_CSR_CLEAR,set?0x12aba:0x12aa6,0x800);q.value=136;return invoke(m,&q,NULL);}
static int stop_pulse(cr_model*m){val x;if(!io_write(m,0x93d2,0x4000042c,16,constant(65535))||!io_write(m,0x93d6,0x4000043c,16,constant(0))||!mmio(m,0x93da,0x40000400,16,&x))return 0;x.value&=~1u;x.known|=1;return io_write(m,0x93e8,0x40000400,16,x);}
static int start_pulse(cr_model*m){
 val pointer,c,f,x;int active;
 if(!load(m,rb(TF_GP+84),0,4,0x938c,&pointer)||!full(m,pointer,0x938e,TF_GP+84)||!load(m,rb(pointer.value),2,1,0x938e,&c)||!load(m,rb(A(0xbec0)),0,1,0x9396,&f)||!nz(m,logical_or(c,f),0x939c,A(0xbec0),&active))return 0;if(!active)return 1;
 if(!store(m,rb(A(0xbec2)),0,1,0x93a2,constant(0))||!store(m,rb(A(0xbec1)),0,1,0x93aa,constant(0))||!store(m,rb(A(0xbebc)),0,4,0x93b2,constant(0))||!io_write(m,0x93ba,0x40000424,16,constant(0))||!mmio(m,0x93be,0x40000400,16,&x))return 0;x.value|=1;x.known|=1;return io_write(m,0x93c6,0x40000400,16,x);
}
static int allocate_pulse(cr_model*m,val n,val*out){
 val old,len;int exists;cr_request q;
 if(!load(m,rb(A(0xbecc)),0,4,0x93fc,&old)||!nz(m,old,0x9400,A(0xbecc),&exists))return 0;
 if(exists){request(&q,CR_FREE,0x9408,0x40068);q.slot=104;q.count=1;arg(&q,0,old);if(!invoke(m,&q,NULL)||!store(m,rb(A(0xbecc)),0,4,0x940e,constant(0))||!store(m,rb(A(0xbec8)),0,4,0x9416,constant(0))||!stop_pulse(m))return 0;}
 len=add(shl(n,2),shl(n,1));request(&q,CR_ALLOC,0x9430,0x40070);q.slot=112;q.count=1;arg(&q,0,len);return invoke(m,&q,out);
}
static int build_pulse(cr_model*m,val input){
 val ptr,count,n;int large,has,same;uint32_t i=0;cr_buffer b;
 if(!gt(m,input,19,0x943e,0,&large))return 0;
 count=truncn(input,8);n=large?constant(2):truncn(add(count,constant(1)),8);
 if(!allocate_pulse(m,n,&ptr)||!store(m,rb(A(0xbecc)),0,4,large?0x94a4:0x9454,ptr)||!nz(m,ptr,large?0x94a8:0x9458,A(0xbecc),&has))return 0;if(!has)return 1;
 b=rb(ptr.value);
 if(large){if(!full(m,ptr,0x94b0,A(0xbecc))||!store(m,b,0,2,0x94b0,constant(3000))||!store(m,b,2,2,0x94b4,input)||!store(m,b,4,2,0x94b8,constant(0))||!store(m,b,6,2,0x94bc,constant(0)))return 0;}
 else{for(;;){if(!eq(m,count,i,0x946c,0,&same))return 0;if(same)break;if(!full(m,ptr,0x9488,A(0xbecc))||!store(m,b,i*6,2,0x9488,constant(3000))||!store(m,b,i*6+2,2,0x948c,constant(40))||!store(m,b,i*6+4,2,0x9490,constant(80)))return 0;i=(i+1)&255;}if(!full(m,ptr,0x9478,A(0xbecc))||!store(m,b,input.value*6u,2,0x9478,constant(0)))return 0;}
 return start_pulse(m);
}
static int clear_counter(cr_model*m,val channel){int skip;if(!gt(m,channel,2,0x8204,0,&skip))return 0;if(skip)return 1;if(!full(m,channel,0x820e,TF_GP+193))return 0;return store(m,rb(TF_GP+193+channel.value),0,1,0x820e,constant(0));}
static int toggle(cr_model*m){val flag,x;int disabled;if(!load(m,rb(TF_GP+176),0,1,0x9b14,&flag)||!nz(m,flag,0x9b18,TF_GP+176,&disabled))return 0;if(disabled)return 1;if(!mmio(m,0x9b1e,0x4001080c,32,&x))return 0;x.value^=2;return io_write(m,0x9b26,0x4001080c,32,x);}
static int native_sc(cr_model*m,uint32_t va,uint32_t target,cr_buffer source,val channel){cr_request q;request(&q,CR_NATIVE_CALL,va,target);q.source=source;if(target==0x1290a){q.count=3;arg(&q,0,channel);q.argument_known[1]=source.kind==CR_RAM?ALL:0;q.arguments[1]=source.address;arg(&q,2,constant(2));}else{q.count=1;q.arguments[0]=source.address;q.argument_known[0]=source.kind==CR_RAM?ALL:0;}return invoke(m,&q,NULL);}
/* R18 selected real observer bodies. RAM loads are deliberately repeated at
   each native load: borrowed records can alias configuration and shared state. */
static int eqv(cr_model*m,val a,val b,uint32_t va,uint32_t where,int*out){
 if((a.value^b.value)&a.known&b.known){*out=0;return 1;}
 if((a.known&b.known)!=ALL)return halt(m,va,where,~(a.known&b.known));
 *out=1;return 1;
}
static val mul10(val a){return add(shl(a,3),shl(a,1));}
static int general_13a62(cr_model*m,cr_buffer record){
 cr_request q;request(&q,CR_GENERAL_CALL,0xd2a0,0x13a62);q.source=record;
 q.count=1;q.arguments[0]=record.address;q.argument_known[0]=record.kind==CR_RAM?ALL:0;
 return invoke(m,&q,NULL);
}
static int observer_fc22(cr_model*m,val input){
 val x;int yes;
 if(!eq(m,input,3,0xfc24,0,&yes))return 0;
 if(!yes)return store(m,rb(TF_GP+290),0,1,0xfc52,input);
 if(!load(m,rb(TF_GP+290),0,1,0xfc28,&x)||!nz(m,x,0xfc2c,TF_GP+290,&yes))return 0;
 if(yes){
  if(!eq(m,x,1,0xfc32,TF_GP+290,&yes))return 0;
  return store(m,rb(TF_GP+290),0,1,0xfc38,constant(yes?2:1));
 }
 if(!load(m,rb(A(0xc253)),0,1,0xfc42,&x)||!eq(m,masked(x,3),1,0xfc4a,A(0xc253),&yes))return 0;
 return store(m,rb(TF_GP+290),0,1,0xfc38,constant(yes?2:1));
}
static int observer_d25a(cr_model*m,cr_buffer record){
 val x,y,z,old;int yes;
 if(!load(m,record,3,1,0xd25a,&x)||!eq(m,masked(x,3),1,0xd262,address(record,3),&yes))return 0;if(!yes)return 1;
 if(!load(m,record,6,1,0xd266,&x)||!load(m,record,5,1,0xd26a,&y))return 0;
 z=logical_or(shl(masked(x,15),8),y);
 if(!load(m,record,3,1,0xd274,&x))return 0;y=shr(x,2);
 if(!load(m,record,4,1,0xd27c,&x))return 0;
 z=shr(add(z,logical_or(shl(masked(x,63),6),y)),1);
 if(!load(m,rb(A(0xbf5c)),0,2,0xd290,&old)||!eqv(m,old,z,0xd294,A(0xbf5c),&yes))return 0;if(yes)return 1;
 if(!store(m,rb(A(0xbf5c)),0,2,0xd29c,z))return 0;
 return general_13a62(m,record);
}
static int observer_f918(cr_model*m,cr_buffer record){
 val x,old;int yes;
 if(!load(m,record,4,1,0xf918,&x)||!load(m,rb(TF_GP+281),0,1,0xf91c,&old))return 0;
 x=masked(shr(x,1),7);
 if(!eqv(m,old,x,0xf924,TF_GP+281,&yes))return 0;if(yes)return 1;
 if(!store(m,rb(TF_GP+281),0,1,0xf928,x))return 0;
 return observer_fc22(m,constant(0));
}
static int observer_f932(cr_model*m,cr_buffer record){
 val mode,x,y;int yes,force=0;
 if(!load(m,rb(TF_GP+284),0,1,0xf932,&mode)||!eq(m,mode,1,0xf938,TF_GP+284,&yes))return 0;
 if(yes){
  if(!load(m,record,4,1,0xf97a,&x)||!store(m,record,4,1,0xf984,logical_or(masked(x,~14u),constant(2))))return 0;force=1;
 }else{
  if(!eq(m,mode,2,0xf93e,TF_GP+284,&yes))return 0;
  if(yes){if(!load(m,record,4,1,0xf98c,&x)||!store(m,record,4,1,0xf984,logical_or(masked(x,~14u),constant(6))))return 0;force=1;}
 }
 if(!load(m,record,4,1,0xf944,&x)||!load(m,rb(TF_GP+285),0,1,0xf948,&y))return 0;
 x=masked(x,1);
 if(!eqv(m,y,x,0xf94e,TF_GP+285,&yes))return 0;
 if(!yes){if(!store(m,rb(TF_GP+285),0,1,0xf952,x)||!store(m,rb(TF_GP+286),0,1,0xf956,x))return 0;}
 if(!load(m,rb(TF_GP+286),0,1,0xf95a,&x)||!load(m,rb(TF_GP+285),0,1,0xf95e,&y)||!eqv(m,y,x,0xf962,TF_GP+285,&yes))return 0;
 if(!yes){
  y=masked(x,1);if(!load(m,record,4,1,0xf96a,&x)||!store(m,record,4,1,0xf972,logical_or(masked(x,~1u),y)))return 0;
 }else if(!force)return 1;
 return native_sc(m,0xf976,0x12864,record,constant(0));
}
static int observer_c544(cr_model*m,cr_buffer record){
 val x,y,z,n;int yes,modified=0,clamp=1;
 if(!load(m,rb(TF_GP+220),0,4,0xc548,&x)||!nz(m,masked(shr(x,9),1),0xc54e,TF_GP+220,&yes))return 0;if(!yes)return 1;
 if(!load(m,rb(TF_GP+220),0,4,0xc550,&x)||!nz(m,masked(shr(x,10),63),0xc55a,TF_GP+220,&yes))return 0;
 if(yes){
  if(!load(m,rb(TF_GP+220),0,4,0xc55c,&x)||!load(m,rb(TF_GP+224),0,4,0xc562,&y))return 0;
  z=logical_or(shl(masked(y,255),16),shr(x,16));
  if(!store(m,record,4,1,0xc570,z)||!store(m,record,5,1,0xc576,shr(z,8))||!store(m,record,6,1,0xc57a,shr(z,16)))return 0;modified=1;
 }
 if(!load(m,rb(TF_GP+224),0,4,0xc580,&x)||!nz(m,masked(shr(x,8),31),0xc586,TF_GP+224,&yes))return 0;
 if(!yes){if(!modified)return 1;}else{
  if(!load(m,rb(TF_GP+224),0,4,0xc588,&x)||!gt(m,masked(shr(x,8),31),10,0xc590,TF_GP+224,&yes))return 0;
  if(!yes){
   if(!load(m,rb(TF_GP+224),0,4,0xc594,&x)||!load(m,record,7,1,0xc598,&y))return 0;
   n=truncn(add(masked(y,127),mul10(masked(shr(x,8),31))),8);
  }else{
   if(!load(m,rb(TF_GP+224),0,4,0xc5f0,&x)||!gt(m,masked(shr(x,8),31),20,0xc5fa,TF_GP+224,&yes))return 0;
   if(yes){n=constant(0);clamp=0;}
   else{
    if(!load(m,rb(TF_GP+224),0,4,0xc5fe,&x))return 0;
    n=truncn(mul10(add(masked(shr(x,8),31),constant(UINT32_C(0xfffffff6)))),8);
   }
  }
  /* Native >20 jumps directly to C5C0 without evaluating C5B4. */
  if(clamp){if(!gt(m,n,100,0xc5b4,0,&yes))return 0;if(yes)n=constant(100);}
  if(!load(m,record,7,1,0xc5c0,&x)||!store(m,record,7,1,0xc5ce,logical_or(masked(n,127),masked(x,~127u))))return 0;
 }
 if(!load(m,record,2,1,0xc5d2,&x)||!nz(m,x,0xc5d6,address(record,2),&yes))return 0;if(!yes)return 1;
 if(!load(m,rb(TF_GP+224),0,4,0xc5d8,&x)||!load(m,record,8,1,0xc5e0,&y)||!store(m,record,8,1,0xc5e8,logical_or(masked(y,~3u),masked(shr(x,13),3))))return 0;
 return native_sc(m,0xc5ec,0x12864,record,constant(0));
}
static int debug(cr_model*m,cr_buffer record,val*out){
 unsigned i;val h,mode,auth,dlc,id,channel,last=constant(0),header,live;int yes;cr_request q;cr_buffer local=vb(m->debug_value,m->debug_known,60);
 ++m->debug_calls;memset(m->debug_value,0,60);memset(m->debug_known,0,60);
 for(i=0;i<2;i++){uint32_t a=AUTH+4*i;
  if(!load(m,rb(a),2,2,0x8304,&h)||!eq(m,h,65534,0x8308,a+2,&yes))return 0;if(yes)continue;
  if(!load(m,rb(a),5,1,0x830c,&mode)||!eq(m,mode,2,0x8310,a+5,&yes))return 0;if(!yes)continue;
  if(!load(m,rb(a),4,1,0x8314,&auth)||!nz(m,auth,0x831c,a+4,&yes))return 0;if(!yes)continue;
  if(!load(m,record,2,1,0x831e,&dlc))return 0;last=auth;if(!gt(m,dlc,8,0x8324,address(record,2),&yes))return 0;if(yes)continue;
  if(!load(m,record,0,2,0x8328,&id)||!load(m,record,11,1,0x832c,&channel)||!store(m,local,1,1,0x8332,id))return 0;header=logical_or(shr(id,8),shl(channel,4));if(!store(m,local,0,1,0x8340,header)||!copy(m,0x834c,sub(record,3),sub(local,2),dlc))return 0;
  if(!load(m,record,2,1,0x834e,&live)||!load(m,rb(a),2,2,0x8352,&h))return 0;
  request(&q,CR_REPLY,0x835e,0x8cfa);q.count=4;q.source=local;arg(&q,0,h);arg(&q,1,constant(192));q.argument_known[2]=0;arg(&q,3,add(live,constant(2)));q.length=q.arguments[3];++m->debug_replies;if(!invoke(m,&q,NULL))return 0;
 }*out=last;return 1;
}
/* R19 actual EBBC/1051C/106B8 bodies. The byte counter is native uint8;
   LBU DLC bounds it at254 iterations, even for malformed CAN lengths. */
static int checksum_ebbc(cr_model*m,cr_buffer record,val*out){
 val id,dlc,sum,x;uint32_t i,count,maximum;
 if(!load(m,record,0,2,0xebbc,&id)||!load(m,record,2,1,0xebc0,&dlc))return 0;
 sum=truncn(add(shr(id,8),id),8);
 maximum=(dlc.value&dlc.known)|~dlc.known;
 if(maximum<=1){*out=sum;return 1;}
 if(!full(m,dlc,0xebd2,address(record,2)))return 0;
 count=dlc.value?dlc.value-1:0;
 for(i=0;i<count;i++){if(!load(m,record,3+i,1,0xebde,&x))return 0;sum=truncn(add(sum,x),8);}
 *out=sum;return 1;
}
static int predicate_1051c(cr_model*m,cr_buffer record,val*out){
 val sum,last;uint32_t known;
 if(!checksum_ebbc(m,record,&sum)||!load(m,record,10,1,0x10528,&last))return 0;
 known=sum.known&last.known;
 if((sum.value^last.value)&known){*out=constant(0);return 1;}
 out->value=sum.value==last.value?1u:0u;out->known=known==ALL?ALL:~1u;return 1;
}
static int gate_106b8(cr_model*m,val predicate,cr_buffer record,val*out){
 val target=masked(predicate,~1u),result;cr_request q;int yes;
 if(!full(m,target,0x106c2,target.value))return 0;
 if(target.value!=0x1051c)return halt(m,0x106c2,target.value,0);
 if(!predicate_1051c(m,record,&result)||!nz(m,result,0x106c6,0,&yes))return 0;
 if(yes){
  if(!clear_counter(m,constant(0)))return 0;
  request(&q,CR_SCHEDULE,0x106de,0x9102);q.count=4;
  arg(&q,0,constant(0x1063c));arg(&q,1,constant(0));arg(&q,2,constant(2000));arg(&q,3,constant(0));
  if(!invoke(m,&q,NULL))return 0;
 }
 *out=result;return 1;
}
static int cache_leaf(cr_model*m,uint32_t pc,cr_buffer record,int*handled){
 val gate;int yes;uint32_t index=0,va=0,target=0;*handled=1;
 switch(pc){
 case 0x14e48:index=1;break;
 case 0x14c38:index=3;break;
 case 0x14edc:index=4;break;
 case 0x14fde:index=11;break;
 case 0x1501e:index=12;break;
 case 0x14cea:
  if(!load(m,record,3,1,0x14cea,&gate)||!nz(m,masked(gate,3),0x14cf0,address(record,3),&yes))return 0;
  if(!yes){index=6;break;}if(!eq(m,masked(gate,3),1,0x14cf6,address(record,3),&yes))return 0;if(!yes)return 1;index=7;break;
 case 0x15030:
  if(!load(m,record,3,1,0x15030,&gate)||!nz(m,masked(gate,7),0x15036,address(record,3),&yes))return 0;if(yes)return 1;index=14;break;
 case 0x1504c:case 0x1505e:
  if(!load(m,record,3,1,pc,&gate)||!eq(m,masked(gate,7),5,pc==0x1504c?0x15054:0x15066,address(record,3),&yes))return 0;if(!yes)return 1;index=pc==0x1504c?16:17;break;
 case 0x14e1a:index=0;va=0x14e2c;target=0xdd7c;break;
 case 0x14eb2:index=2;va=0x14ebe;target=0xeffe;break;
 case 0x14f16:
  if(!load(m,record,3,1,0x14f16,&gate)||!eq(m,masked(gate,3),1,0x14f1e,address(record,3),&yes))return 0;
  if(yes&&!cache(m,constant(0),constant(5),record))return 0;return observer_d25a(m,record);
 case 0x14f84:
  if(!cache(m,constant(0),constant(8),record)||!observer_f918(m,record))return 0;return observer_f932(m,record);
 case 0x14fa0:
  if(!load(m,record,3,1,0x14fa0,&gate)||!nz(m,masked(gate,3),0x14fa6,address(record,3),&yes))return 0;
  if(!yes){if(!cache(m,constant(0),constant(9),record))return 0;}
  else{if(!eq(m,masked(gate,3),1,0x14faa,address(record,3),&yes))return 0;if(yes&&!cache(m,constant(0),constant(10),record))return 0;}
  return halt(m,0x14fb0,0xb5ba,0);
 case 0x14ff0:{val result;
  if(!cache(m,constant(0),constant(13),record)||!gate_106b8(m,constant(0x1051c),record,&result)||!nz(m,result,0x15008,0,&yes))return 0;
  return yes?halt(m,0x1500e,0xad16,0):1;
 }
 case 0x14d9e:index=15;va=0x14db0;target=0xa5fe;break;
 case 0x1507a:
  if(!cache(m,constant(0),constant(18),record))return 0;return observer_c544(m,record);
 default:*handled=0;return 0;
 }
 if(!cache(m,constant(0),constant(index),record))return 0;return target?halt(m,va,target,0):1;
}
static int dispatch(cr_model*m,cr_buffer record){
 val mode,id;int yes;uint32_t pc,from=0x14b1a;unsigned i,n;
 ++m->dispatch_calls;if(!load(m,rb(A(0xbfb1)),0,1,0x8298,&mode)||!gt(m,mode,6,0x14b06,A(0xbfb1),&yes))return 0;
 if(yes)return halt(m,0x1524a,0x105c8,0);if(!full(m,mode,0x14b1a,0x1a33c))return 0;if(mode.value!=1)return halt(m,0x14b1a,mode_table[mode.value],0);
 if(!load(m,record,0,2,0x14b28,&id))return 0;pc=0x14b30;
 for(n=0;n<80;n++){
  if(pc==0x14b6c)return 1;if(pc==0x15040){cr_request q;request(&q,CR_D1_TAIL,0x15048,0x139e6);q.source=record;q.count=1;q.arguments[0]=record.address;q.argument_known[0]=record.kind==CR_RAM?ALL:0;++m->d1_calls;return invoke(m,&q,NULL);}
  for(i=0;i<sizeof(leaves)/sizeof(leaves[0]);i++)if(pc==leaves[i]){int handled,ok=cache_leaf(m,pc,record,&handled);return handled?ok:halt(m,from,pc,0);}
  for(i=0;i<sizeof(nodes)/sizeof(nodes[0]);i++)if(nodes[i].va==pc)break;if(i==sizeof(nodes)/sizeof(nodes[0]))return halt(m,pc,pc,0);
  if(nodes[i].test==2){if(!gt(m,id,nodes[i].constant,pc,address(record,0),&yes))return 0;}
  else{if(!eq(m,id,nodes[i].constant,pc,address(record,0),&yes))return 0;if(nodes[i].test==1)yes=!yes;}
  from=pc;pc=yes?nodes[i].yes:nodes[i].no;
 }return halt(m,pc,pc,0);
}
static int queue(cr_model*m){
 unsigned i;int yes;val id,value,pointer,dummy,channel;cr_buffer record=vb(m->record_value,m->record_known,12),control=vb(m->control_value,m->control_known,12);
 memset(m->record_value,0,12);memset(m->record_known,0,12);memset(m->control_value,0,12);memset(m->control_known,0,12);
 for(i=0;i<32;i++){uint32_t a=Q+i*12;
  if(!load(m,rb(a),0,2,0x12a9c,&id)||!nz(m,id,0x12aa4,a,&yes))return 0;if(!yes)continue;
  if(!csr(m,0)||!copy(m,0x12ab4,rb(a),record,constant(12))||!store(m,rb(a),0,2,0x12ab6,constant(0)))return 0;++m->consumed;
  if(!csr(m,1)||!debug(m,record,&dummy)||!nz(m,dummy,0x12ac4,0,&yes))return 0;if(yes)continue;
  if(!load(m,record,0,2,0x12ac6,&id)||!eq(m,id,1,0x12aca,0,&yes))return 0;
  if(!yes){if(!load(m,rb(TF_GP+84),0,4,0x12b88,&pointer)||!full(m,pointer,0x12b8c,TF_GP+84)||!load(m,rb(pointer.value),4,1,0x12b8c,&value))return 0;value.value&=8;value.known|=~8u;if(!nz(m,value,0x12b92,pointer.value+4,&yes))return 0;if(!yes&&!dispatch(m,record))return 0;continue;}
  if(!load(m,record,2,1,0x12ace,&value)||!eq(m,value,4,0x12ad4,0,&yes))return 0;if(!yes)continue;
  if(!load(m,record,3,1,0x12ad8,&value)||!eq(m,value,181,0x12ae0,0,&yes))return 0;if(!yes)continue;
  if(!load(m,record,4,1,0x12ae4,&value)||!eq(m,value,98,0x12aec,0,&yes))return 0;if(!yes)continue;
  if(!load(m,record,5,1,0x12af0,&value)||!eq(m,value,0,0x12af4,0,&yes))return 0;
  if(yes){
   if(!clear_counter(m,constant(0))||!load(m,record,6,1,0x12b22,&value)||!build_pulse(m,value)||!toggle(m)||!load(m,record,11,1,0x12b30,&channel)||!store(m,control,0,2,0x12b38,constant(0))||!native_sc(m,0x12b3c,0x1290a,sub(control,0),channel))return 0;
   if(!load(m,record,11,1,0x12b40,&channel)||!store(m,control,0,2,0x12b44,constant(1))||!eq(m,channel,2,0x12b4c,0,&yes))return 0;
   if(!native_sc(m,0x12b56,0x1290a,vb(m->control_value,m->control_known,2),constant(yes?1:2)))return 0;continue;
  }
  if(!eq(m,value,90,0x12afa,0,&yes))return 0;if(!yes)continue;
  if(!load(m,record,6,1,0x12b5c,&value)||!eq(m,value,85,0x12b64,0,&yes))return 0;if(!yes)continue;
  if(!copy(m,0x12b72,record,control,constant(12))||!store(m,control,6,1,0x12b7a,constant(86))||!store(m,control,11,1,0x12b7e,constant(0))||!native_sc(m,0x12b82,0x12864,control,constant(0)))return 0;
 }return 1;
}
void cr_init(cr_model*m,tf_model*ram,const cr_backend*b){memset(m,0,sizeof(*m));m->memory=ram;if(b)m->backend=*b;}
void cr_resume(cr_model*m){m->flow=CR_RETURNED;m->result_defined=0;m->boundary_va=m->boundary_address=m->needed_mask=0;}
cr_flow cr_run(cr_model*m,uint32_t entry,const cr_arguments*input){
 cr_arguments empty;const cr_arguments*a=input;val out={0,0};int ok=0,defined=0;
 if(m->flow!=CR_RETURNED)return m->flow;m->result_defined=0;m->boundary_va=m->boundary_address=m->needed_mask=0;if(!m->memory){halt(m,entry,0,ALL);return m->flow;}
 if(!a){memset(&empty,0,sizeof(empty));a=&empty;}
 switch(entry){case CR_QUEUE:ok=queue(m);break;case CR_DEBUG:ok=debug(m,a->record,&out);defined=1;break;case CR_DISPATCH:ok=dispatch(m,a->record);break;case CR_CACHE:ok=cache(m,a->argument,a->cache_index,a->record);break;case CR_OBSERVE_D25A:ok=observer_d25a(m,a->record);break;case CR_OBSERVE_F918:ok=observer_f918(m,a->record);break;case CR_OBSERVE_F932:ok=observer_f932(m,a->record);break;case CR_OBSERVE_FC22:ok=observer_fc22(m,a->argument);break;case CR_OBSERVE_C544:ok=observer_c544(m,a->record);break;case CR_CHECKSUM:ok=checksum_ebbc(m,a->record,&out);defined=1;break;case CR_PREDICATE:ok=predicate_1051c(m,a->record,&out);defined=1;break;case CR_GATE:ok=gate_106b8(m,a->argument,a->record,&out);defined=1;break;case CR_CLEAR_COUNTER:ok=clear_counter(m,a->argument);break;case CR_PULSE_ALLOC:ok=allocate_pulse(m,a->argument,&out);defined=1;break;case CR_PULSE_BUILD:ok=build_pulse(m,a->argument);break;case CR_PULSE_START:ok=start_pulse(m);break;case CR_PULSE_STOP:ok=stop_pulse(m);break;case CR_TOGGLE:ok=toggle(m);break;default:ok=halt(m,entry,entry,0);break;}
 if(ok&&defined&&m->flow==CR_RETURNED){m->result=out.value;m->result_known=out.known;m->result_defined=1;}return m->flow;
}
