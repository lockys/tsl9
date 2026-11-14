#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Projection at 0x9234; supplied a0, stack words s0/ra/s1/s2/s3/s4.
 * Records ordered reads and restored values, no physical memory operation. */
void scheduler_full_exit(uint32_t a0, uint32_t sp, const uint32_t saved[6],
                         uint32_t out[16])
{
    uint32_t i;
    out[0]=a0; out[1]=saved[1]; out[2]=sp+UINT32_C(32);
    for (i=0;i<6;++i) out[3+i]=saved[i];
    out[9]=sp+UINT32_C(28); out[10]=sp+UINT32_C(24);
    out[11]=sp+UINT32_C(20); out[12]=sp+UINT32_C(16);
    out[13]=sp+UINT32_C(12); out[14]=sp+UINT32_C(8);
    out[15]=4;
}
