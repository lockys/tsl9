/* Offline post-copy counter-path model. Numeric addresses resolve only into harness arrays. */
#include <stdint.h>
typedef struct { uint32_t base,size; volatile unsigned char *bytes; } region;
typedef struct {
    region regions[2]; uint32_t *events,capacity,count,fault;
} memory;
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
static void getter(memory *m,uint32_t r[32],uint32_t target,uint32_t continuation,uint32_t *calls) {
    r[1]=continuation;event(m,3,target,continuation,(*calls)++);
    for(uint32_t j=0;j<32;j++) event(m,4,j,4,r[j]);
    if(target==0x81f8) {r[10]=0x2000c1f8;r[10]=load(m,0x2000beea,1);}
    else {r[10]=0x2000c1ee;r[10]=load(m,0x2000bed5,1);}
}
static uint32_t counter_path(memory *m,uint32_t r[32],uint32_t *calls,uint32_t *window) {
    getter(m,r,0x81f8,0xa0e6,calls);
    r[15]=load(m,r[3]+170,1);
    if(r[15]!=r[10]) {
        store(m,r[3]+170,1,r[10]);r[15]=load(m,r[3]+176,1);
        r[15]=(r[15]+1)&3u;store(m,r[3]+176,1,r[15]);
        if(!r[10]) {r[10]=0xa2ea;return 0xa1de;}
        r[13]=0;r[12]=2000;r[11]=1;r[10]=0xa2ea;return 0xa110;
    }
    if(!r[15]) {
        r[15]=load(m,r[3]+175,1);
        if(!r[15]) return 0xa1e8;
    }
    r[15]=load(m,r[2]+8,4);r[14]=load(m,r[2]+10,1);
    r[15]=(r[15]>>8)&15u;r[15]<<=8;r[15]|=r[14];
    r[15]=(r[15]-1961)&65535u;r[14]=178;
    if(r[14]<r[15]) return 0xa1e8;
    getter(m,r,0x81ee,0xa136,calls);
    r[14]=1;r[15]=1960;
    if(r[10]==r[14]) return 0xa168;
    r[15]=2;
    if(r[10]==r[15]) {r[15]=4096;r[15]-=1956;return 0xa168;}
    r[15]=load(m,r[3]+176,1);r[14]=r[15]<<1;
    r[15]=0x1ab48;r[15]+=r[14];
    if(r[15]<0x1ab48 || r[15]+2>0x1ab50) {*window=1;return 0xa158;}
    r[15]=load(m,r[15],2);r[14]=2050;r[15]+=r[14];r[15]&=65535u;
    return 0xa168;
}
