#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void counter_run(unsigned char *ram,unsigned char *flash,uint32_t *r,
    uint32_t *events,uint32_t capacity,uint32_t *out) {
    memory m={{{0x20000000,65536,ram},{0x1ab48,8,flash}},events,capacity,0,0};
    uint32_t calls=0,window=0;out[0]=counter_path(&m,r,&calls,&window);
    out[1]=calls;out[2]=m.count;out[3]=m.fault;out[4]=window;
}
