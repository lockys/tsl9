/* Abstract little-endian memory and registers; not a callable firmware ABI. */
#include <stdint.h>
#include <limits.h>
#ifdef __cplusplus
static_assert(CHAR_BIT == 8, "octets required");
#else
_Static_assert(CHAR_BIT == 8, "octets required");
#endif

struct segment { uint32_t base, size; volatile unsigned char *bytes; };
struct memory {
    struct segment region[3];
    uint32_t *events, capacity, count, fault;
};

static uint32_t add32(uint32_t a, uint32_t b)
{ return (uint32_t)((uint64_t)a + b); }

static volatile unsigned char *byte_at(struct memory *m, uint32_t address)
{
    unsigned i;
    for (i=0; i<3; ++i) {
        uint32_t offset = address - m->region[i].base;
        if (address >= m->region[i].base && offset < m->region[i].size)
            return m->region[i].bytes + offset;
    }
    m->fault = 1;
    return 0;
}

/* Events group abstract accesses, not host bus transactions or atomic stores. */
static void event(struct memory *m, uint32_t kind, uint32_t address,
                  uint32_t width, uint32_t value)
{
    if (m->count >= m->capacity) { m->fault = 2; return; }
    m->events[4*m->count] = kind; m->events[4*m->count+1] = address;
    m->events[4*m->count+2] = width; m->events[4*m->count+3] = value;
    ++m->count;
}

static uint32_t read_le(struct memory *m, uint32_t address, uint32_t width)
{
    uint32_t value=0, i;
    for (i=0; i<width; ++i) {
        volatile unsigned char *p = byte_at(m, add32(address,i));
        if (!p) return 0;
        value |= (uint32_t)*p << (8*i);
    }
    event(m,1,address,width,value);
    return value;
}

static void write_le(struct memory *m, uint32_t address, uint32_t width, uint32_t value)
{
    uint32_t i;
    value &= width == 1 ? 255u : 65535u;
    for (i=0; i<width; ++i) {
        volatile unsigned char *p = byte_at(m, add32(address,i));
        if (!p) return;
        *p = (unsigned char)(value >> (8*i));
    }
    event(m,2,address,width,value);
}

void tx_completed_slice(struct memory *m, uint32_t r[32])
{
    const uint32_t b = UINT32_C(0x2000b18c);
    uint32_t bank=r[12], length=r[8], source=r[9], command=r[19];
    uint32_t sp=r[2], gp=r[3], i=0, a6=r[16];
    uint32_t d=add32(add32(b,(uint32_t)((uint64_t)bank*1062)),6);
    uint32_t sum=(uint32_t)((uint64_t)(length>>8)+(length&255u)+command);

    write_le(m,d,2,0x7f55);
    write_le(m,add32(d,4),1,length);
    write_le(m,add32(d,3),1,length>>8);
    write_le(m,add32(d,2),1,command);
    sum &= 255u;
    while ((i&65535u)<length) {
        uint32_t value=read_le(m,add32(source,i),1);
        a6=add32(d,i);
        sum=add32(sum,value);
        write_le(m,add32(add32(d,i),5),1,value);
        sum &= 255u;
        i=add32(i,1);
    }
    r[10]=i&65535u; r[11]=i; r[13]=b; r[14]=sum; r[15]=d; r[16]=a6;

    write_le(m,add32(add32(d,length),5),1,sum);
    r[15]=(uint32_t)((uint64_t)bank*1062);
    r[8]=add32(length,6); r[12]=bank<<2;
    r[1]=read_le(m,add32(sp,28),4);
    r[9]=read_le(m,add32(sp,20),4);
    r[18]=read_le(m,add32(sp,16),4);
    r[19]=read_le(m,add32(sp,12),4);
    r[11]=1; r[15]=add32(r[15],b);
    write_le(m,add32(r[15],2),2,r[8]);
    write_le(m,add32(r[15],4),2,0);
    r[15]=add32(gp,148); r[12]=add32(r[12],r[15]);
    r[8]=read_le(m,add32(sp,24),4);
    r[15]=UINT32_C(0x40000);
    r[6]=read_le(m,UINT32_C(0x40050),4);
    r[10]=read_le(m,r[12],1);
    r[2]=add32(sp,32);
    /* Stop before JR T1. No function-pointer conversion or tail execution. */
}
