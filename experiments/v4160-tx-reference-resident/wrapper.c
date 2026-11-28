#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void reference_run(unsigned char *ram,unsigned char *low,unsigned char *mmio,
    uint32_t *r,const uint32_t *cfg,uint32_t *events,uint32_t capacity,uint32_t *out) {
    memory m={{{0x20000000,65536,ram},{0x40000,512,low},{0x4002420c,4,mmio}},events,capacity,0,0};
    uint32_t calls=0;out[0]=tx_reference(&m,r,cfg,&calls);
    out[1]=calls;out[2]=m.count;out[3]=m.fault;
}
