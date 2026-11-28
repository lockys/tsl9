/* Offline entry model. Numeric addresses resolve only into harness arrays. */
#include <stdint.h>
typedef struct { uint32_t base,size; volatile unsigned char *bytes; } region;
typedef struct {
    region regions[2]; uint32_t *events,capacity,count,fault;
} memory;
typedef struct { uint32_t address,width,value; } write_action;
typedef struct {
    uint32_t target,result,mask,registers[32],write_count;
    write_action writes[4];
} action;
static void event(memory *m,uint32_t kind,uint32_t address,uint32_t width,uint32_t value) {
    if(m->count>=m->capacity) {m->fault=2;return;}
    uint32_t i=4*m->count++;
    m->events[i]=kind;m->events[i+1]=address;m->events[i+2]=width;m->events[i+3]=value;
}
static uint32_t access_le(memory *m,uint32_t address,uint32_t width,uint32_t value,uint32_t store) {
    if((width!=1 && width!=2 && width!=4) || address%width) {m->fault=5;return 0;}
    for(uint32_t i=0;i<2;i++) {
        region *p=&m->regions[i]; uint32_t offset=address-p->base;
        if(address>=p->base && offset<=p->size && width<=p->size-offset) {
            uint32_t result=0;
            for(uint32_t j=0;j<width;j++) {
                if(store) p->bytes[offset+j]=(unsigned char)(value>>(8*j));
                result|=(uint32_t)p->bytes[offset+j]<<(8*j);
            }
            event(m,store?2:1,address,width,result);return result;
        }
    }
    m->fault=1;return 0;
}
static uint32_t load(memory *m,uint32_t a,uint32_t w) {return access_le(m,a,w,0,0);}
static void store(memory *m,uint32_t a,uint32_t w,uint32_t v) {(void)access_le(m,a,w,v,1);}
static void opaque_return(memory *m,uint32_t r[32],const action actions[2],uint32_t limit,
                          uint32_t *calls,uint32_t continuation) {
    uint32_t target=r[15]&~(uint32_t)1;
    r[1]=continuation;
    event(m,3,target,continuation,*calls);
    for(uint32_t j=0;j<32;j++) event(m,4,j,4,r[j]);
    if(*calls>=limit) {m->fault=3;return;}
    const action *a=&actions[(*calls)++];
    if(target!=a->target || a->write_count>4 || (a->mask&1025u)) {m->fault=4;return;}
    for(uint32_t j=0;j<a->write_count;j++) store(m,a->writes[j].address,a->writes[j].width,a->writes[j].value);
    r[10]=a->result;
    for(uint32_t j=1;j<32;j++) if(a->mask&((uint32_t)1<<j)) r[j]=a->registers[j];
}
/* Return the original PC at a boundary, before its next instruction executes. */
static uint32_t tx_entry(memory *m,uint32_t r[32],const action actions[2],uint32_t limit,uint32_t *calls) {
    r[15]=1039;
    if(r[13]>r[15]) return 0x8b6c;
    r[2]-=32;
    store(m,r[2]+24,4,r[8]);store(m,r[2]+20,4,r[9]);
    store(m,r[2]+16,4,r[18]);store(m,r[2]+12,4,r[19]);store(m,r[2]+28,4,r[1]);
    r[14]=load(m,r[3]+150,2);
    r[18]=r[10];r[8]=r[13];r[9]=r[12];r[19]=r[11];
    if(r[14]==r[10]) {
        r[15]=65536;r[15]-=2;
        if(r[14]!=r[15]) {
            r[15]=0x40000;r[15]=load(m,r[15]+316,4);
            r[11]=r[3]+128;
            opaque_return(m,r,actions,limit,calls,0x8a90);
            if(m->fault) return 0;
            r[15]=1;
            if(r[10]==r[15]) {r[12]=0;return 0x8ace;}
        }
    }
    r[15]=load(m,r[3]+154,2);
    if(r[15]==r[18]) {
        r[15]=65536;r[15]-=2;
        if(r[18]!=r[15]) {
            r[15]=0x40000;r[15]=load(m,r[15]+316,4);
            r[11]=r[3]+128;r[10]=r[18];
            opaque_return(m,r,actions,limit,calls,0x8ab6);
            if(m->fault) return 0;
            r[15]=1;r[12]=1;
            if(r[10]==r[15]) return 0x8ace;
        }
    }
    r[1]=load(m,r[2]+28,4);r[8]=load(m,r[2]+24,4);r[9]=load(m,r[2]+20,4);
    r[18]=load(m,r[2]+16,4);r[19]=load(m,r[2]+12,4);r[2]+=32;
    return 0x8aca;
}

static uint32_t add32(uint32_t a,uint32_t b) {return (uint32_t)((uint64_t)a+b);}
static void tx_complete(memory *m, uint32_t r[32])
{
    const uint32_t b = UINT32_C(0x2000b18c);
    uint32_t bank=r[12], length=r[8], source=r[9], command=r[19];
    uint32_t sp=r[2], gp=r[3], i=0, a6=r[16];
    uint32_t d=add32(add32(b,(uint32_t)((uint64_t)bank*1062)),6);
    uint32_t sum=(uint32_t)((uint64_t)(length>>8)+(length&255u)+command);

    store(m,d,2,0x7f55);
    store(m,add32(d,4),1,length);
    store(m,add32(d,3),1,length>>8);
    store(m,add32(d,2),1,command);
    sum &= 255u;
    while ((i&65535u)<length) {
        uint32_t value=load(m,add32(source,i),1);
        a6=add32(d,i);
        sum=add32(sum,value);
        store(m,add32(add32(d,i),5),1,value);
        sum &= 255u;
        i=add32(i,1);
    }
    r[10]=i&65535u; r[11]=i; r[13]=b; r[14]=sum; r[15]=d; r[16]=a6;

    store(m,add32(add32(d,length),5),1,sum);
    r[15]=(uint32_t)((uint64_t)bank*1062);
    r[8]=add32(length,6); r[12]=bank<<2;
    r[1]=load(m,add32(sp,28),4);
    r[9]=load(m,add32(sp,20),4);
    r[18]=load(m,add32(sp,16),4);
    r[19]=load(m,add32(sp,12),4);
    r[11]=1; r[15]=add32(r[15],b);
    store(m,add32(r[15],2),2,r[8]);
    store(m,add32(r[15],4),2,0);
    r[15]=add32(gp,148); r[12]=add32(r[12],r[15]);
    r[8]=load(m,add32(sp,24),4);
    r[15]=UINT32_C(0x40000);
    r[6]=load(m,UINT32_C(0x40050),4);
    r[10]=load(m,r[12],1);
    r[2]=add32(sp,32);
    /* Stop before JR T1. No function-pointer conversion or tail execution. */
}

static uint32_t tx_whole(memory *m,uint32_t r[32],const action actions[2],uint32_t limit,uint32_t *calls,uint32_t *domain) {
    uint32_t pc=tx_entry(m,r,actions,limit,calls);
    if(m->fault || pc!=0x8ace) return pc;
    event(m,5,pc,4,0);
    for(uint32_t j=0;j<32;j++) event(m,6,j,4,r[j]);
    if(r[8]>65535) {*domain=6;return pc;}
    tx_complete(m,r);
    return 0x8b50;
}
