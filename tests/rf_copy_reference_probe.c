/* Synthetic provider for the existing C reference; no target instructions run. */
#include "reference_copy.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define W UINT32_C(0x20003534)
#define BASE (W-16)
static unsigned char mem[64];
static uint32_t mmio=0x12345678;
static bc_value val(uint32_t n){bc_value v={n,UINT32_MAX};return v;}
static bc_flow effect(void *ctx,const rp_request *q,bc_value *out){
    uint32_t a=q->address.value; (void)ctx;
    printf("%u %08x %08x %08x\n",(unsigned)q->kind,q->pc,a,q->data.value);
    switch(q->kind){
    case RP_READ32: if(a!=0x4002420c)exit(3); *out=val(mmio); break;
    case RP_WRITE32: if(a!=0x4002420c || q->data.known!=UINT32_MAX)exit(3); mmio=q->data.value; break;
    case RP_READ8: if(a<BASE || a>=BASE+sizeof mem)exit(3); *out=val(mem[a-BASE]); break;
    case RP_WRITE8: if(a<BASE || a>=BASE+sizeof mem || (q->data.known&255)!=255)exit(3); mem[a-BASE]=(unsigned char)q->data.value; break;
    case RP_FENCE_I: case RP_RETURN: break;
    default: exit(3);
    }
    return BC_RETURNED;
}
int main(int argc,char **argv){
    uint32_t p,src,n,i,loaded; rp_model m; rp_backend b={0,effect};
    if(argc!=4)return 2;
    p=(uint32_t)strtoul(argv[1],0,0);src=(uint32_t)strtoul(argv[2],0,0);n=(uint32_t)strtoul(argv[3],0,0);
    if(p<BASE || p+2+n>BASE+sizeof mem || src<BASE || src+n>BASE+sizeof mem)return 2;
    for(i=0;i<sizeof mem;i++)mem[i]=(unsigned char)i;
    for(i=0;i<4;i++)mem[W-BASE+i]=(unsigned char)(p>>(8*i));
    loaded=(uint32_t)mem[W-BASE]|((uint32_t)mem[W-BASE+1]<<8)|((uint32_t)mem[W-BASE+2]<<16)|((uint32_t)mem[W-BASE+3]<<24);
    mem[loaded-BASE]=0xa5;mem[loaded+1-BASE]=(unsigned char)n;
    rp_init(&m,RP_DEC2023_133D3705,&b);
    if(rp_copy(&m,val(loaded+2),val(src),val(n),val(0x64e28))!=BC_RETURNED || mmio!=0x12345678)return 4;
    printf("memory ");for(i=0;i<sizeof mem;i++)printf("%02x",mem[i]);puts("");
    return 0;
}
