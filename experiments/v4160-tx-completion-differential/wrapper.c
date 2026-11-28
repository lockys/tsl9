#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void tx_run(unsigned char *ram, uint32_t origin, uint32_t size,
    unsigned char *gp, unsigned char *low, uint32_t *registers,
    uint32_t *events, uint32_t capacity, uint32_t *count, uint32_t *fault)
{
    struct memory m;
    m.region[0].base=origin; m.region[0].size=size; m.region[0].bytes=ram;
    m.region[1].base=UINT32_C(0x20004000); m.region[1].size=512; m.region[1].bytes=gp;
    m.region[2].base=UINT32_C(0x40000); m.region[2].size=128; m.region[2].bytes=low;
    m.events=events; m.capacity=capacity; m.count=0; m.fault=0;
    tx_completed_slice(&m,registers);
    *count=m.count; *fault=m.fault;
}
