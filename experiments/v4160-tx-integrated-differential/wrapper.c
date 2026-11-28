#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void whole_run(unsigned char *ram,unsigned char *low,uint32_t *r,
    const action *actions,uint32_t limit,uint32_t *events,uint32_t capacity,uint32_t *out) {
    memory m={{{0x20000000,196608,ram},{0x40000,512,low}},events,capacity,0,0};
    uint32_t calls=0,domain=0;uint32_t pc=tx_whole(&m,r,actions,limit,&calls,&domain);
    out[0]=pc;out[1]=calls;out[2]=m.count;out[3]=m.fault;out[4]=domain;
}
