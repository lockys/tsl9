#include "model.c"
#ifdef __cplusplus
extern "C"
#endif
__declspec(dllexport) void tx_run(volatile unsigned char *ram,
    uint32_t origin, uint32_t base_index, uint32_t source_index,
    uint32_t bank, uint32_t length, uint32_t command, uint32_t entry_a6,
    uint32_t *out)
{
    struct tx_composed_result r = tx_composed(ram, origin, base_index, source_index,
                                             bank, length, command, entry_a6);
    out[0]=r.a0; out[1]=r.a1; out[2]=r.a2; out[3]=r.a3; out[4]=r.a4;
    out[5]=r.a5; out[6]=r.a6; out[7]=r.s0; out[8]=r.s1; out[9]=r.s3;
}
