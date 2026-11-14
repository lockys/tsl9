#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
#ifdef _WIN32
__declspec(dllexport)
#endif
/* Bounded 0xb2aa path: two earlier calls returned zero; clock provider
 * returns clock and does not alter supplied synthetic stack or gp. No actual
 * memory access or provider execution. Input data_byte must be <=255. */
void scheduler_data_delay(uint32_t data_byte, uint32_t clock, uint32_t gp,
                          uint32_t pointer, uint32_t sp, uint32_t ra,
                          uint32_t out[17])
{
    static const uint32_t table[4]={0,1,5,10};
    uint32_t index=data_byte >> 6;
    uint32_t delay=table[index]*UINT32_C(60000);
    out[0]=UINT32_C(0xb254); out[1]=0; out[2]=delay; out[3]=0;
    out[4]=(uint32_t)(sp+UINT32_C(48)); out[5]=ra;
    out[6]=(uint32_t)(sp+UINT32_C(28)); out[7]=UINT32_C(0x0a050100);
    out[8]=(uint32_t)(gp+UINT32_C(84)); out[9]=pointer;
    out[10]=(uint32_t)(pointer+UINT32_C(96)); out[11]=data_byte;
    out[12]=(uint32_t)(sp+UINT32_C(28)+index); out[13]=table[index];
    out[14]=(uint32_t)(sp+UINT32_C(12)); out[15]=UINT32_C(0x2000bef0);
    out[16]=(uint32_t)(clock+delay);
}
