/* Host-only adapter for reference_copy.c; addresses are synthetic. */
#include "reference_copy.h"
#include <stdio.h>
#include <stdlib.h>
#define RAM 0x20001000u
#define MMIO 0x4002420cu
static unsigned char data[64];
static uint32_t mmio = 0x12345678u, fail_read, fail_write;
static bc_value word(uint32_t x) { bc_value v; v.value=x; v.known=UINT32_MAX; return v; }
static bc_flow effect(void *ctx, const rp_request *q, bc_value *out) {
    uint32_t a=q->address.value, v=0; const char *name=0; (void)ctx;
    switch(q->kind) {
    case RP_READ32: if(a!=MMIO) return BC_HALT; v=mmio; *out=word(v); name="read32"; break;
    case RP_WRITE32: if(a!=MMIO) return BC_HALT; v=q->data.value; mmio=v; name="write32"; break;
    case RP_READ8: if(a<RAM || a-RAM>=64 || a==fail_read) return BC_HALT;
        v=data[a-RAM]; *out=word(v); name="read8"; break;
    case RP_WRITE8: if(a<RAM || a-RAM>=64 || a==fail_write) return BC_HALT;
        v=q->data.value & 255; data[a-RAM]=(unsigned char)v; name="write8"; break;
    case RP_FENCE_I: puts("fence.i"); return BC_RETURNED;
    case RP_RETURN: return BC_RETURNED; /* RET is a host termination in the interpreter. */
    default: return BC_HALT;
    }
    printf("%s %u %u\n",name,(unsigned)a,(unsigned)v); return BC_RETURNED;
}
int main(int argc, char **argv) {
    uint32_t d,s,n; unsigned j; rp_model model; rp_backend backend; bc_flow flow;
    if(argc!=6) return 2;
    d=(uint32_t)strtoul(argv[1],0,0); s=(uint32_t)strtoul(argv[2],0,0);
    n=(uint32_t)strtoul(argv[3],0,0); fail_read=(uint32_t)strtoul(argv[4],0,0);
    fail_write=(uint32_t)strtoul(argv[5],0,0);
    for(j=0;j<64;j++) data[j]=(unsigned char)j;
    backend.context=0; backend.effect=effect;
    rp_init(&model,RP_DEC2023_133D3705,&backend);
    flow=rp_copy(&model,word(d),word(s),word(n),word(0));
    printf("status %s %u %u\n",flow==BC_RETURNED?"returned":"halt",(unsigned)model.boundary,(unsigned)model.boundary_pc);
    printf("mmio %u\ndata ",(unsigned)mmio);
    for(j=0;j<64;j++) printf("%02x",data[j]);
    puts(""); return 0;
}
