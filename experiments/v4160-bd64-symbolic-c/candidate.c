#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char record_flag_bd64;
__attribute__((section(".leaf"), used))
unsigned char tsl9_get_bd64(void)
{
    return record_flag_bd64;
}
#ifdef __cplusplus
}
#endif
