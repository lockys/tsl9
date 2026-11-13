#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char tsl9_81ee_byte;
__attribute__((section(".leaf"), used))
unsigned int tsl9_81ee(void)
{
    return tsl9_81ee_byte;
}
#ifdef __cplusplus
}
#endif
