/* Offline RX payload-path model. Numeric addresses resolve only into harness arrays. */
#include <stdint.h>
typedef struct { uint32_t base,size; volatile unsigned char *bytes; } region;
typedef struct {
    region regions[1]; uint32_t *events,capacity,count,fault;
} memory;
static void event(memory *m,uint32_t kind,uint32_t address,uint32_t width,uint32_t value) {
    if(m->count>=m->capacity) {m->fault=2;return;}
    uint32_t i=4*m->count++;
    m->events[i]=kind;m->events[i+1]=address;m->events[i+2]=width;m->events[i+3]=value;
}
static uint32_t access_le(memory *m,uint32_t address,uint32_t width,uint32_t value,uint32_t store) {
    if((width!=1 && width!=2 && width!=4) || address%width) {m->fault=5;return 0;}
    for(uint32_t i=0;i<1;i++) {
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
/* Slice entry: the incoming byte is already in A5; S1 is a live pointer. */
static uint32_t rx_payload(memory *m,uint32_t r[32]) {
    r[12]=load(m,r[3]+138,2);r[14]=1039;
    if(r[14]<r[12]) {
        store(m,r[3]+156,1,0);return 0x897e;
    }
    r[14]=(r[12]+1)&65535u;
    store(m,r[3]+138,2,r[14]);
    r[13]=0x2000b9d8;r[13]+=r[12];
    store(m,r[13],1,r[15]);
    r[13]=load(m,r[3]+142,2);
    if(r[14]>=r[13]) {r[14]=6;store(m,r[3]+156,1,r[14]);}
    r[14]=load(m,r[9],1);r[15]+=r[14];
    store(m,r[3]+165,1,r[15]);
    return 0x897e;
}
