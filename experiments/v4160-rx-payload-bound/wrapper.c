#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void rx_run(unsigned char *ram,uint32_t *r,uint32_t *events,uint32_t capacity,uint32_t *out) {
    memory m={{{0x20000000,65536,ram}},events,capacity,0,0};
    out[0]=rx_payload(&m,r);out[1]=m.count;out[2]=m.fault;
}
