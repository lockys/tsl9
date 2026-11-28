#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void entry_run(unsigned char *ram,unsigned char *low,uint32_t *r,
    const action *actions,uint32_t limit,uint32_t *events,uint32_t capacity,uint32_t *out) {
    memory m={{{0x20000000,65536,ram},{0x40000,512,low}},events,capacity,0,0};
    uint32_t calls=0;uint32_t pc=tx_entry(&m,r,actions,limit,&calls);
    out[0]=pc;out[1]=calls;out[2]=m.count;out[3]=m.fault;
}
