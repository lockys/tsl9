#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char record_flag_bd46;
__attribute__((section(".leaf"), used))
volatile unsigned char *tsl9_record_helpers_provider_bd46(void)
{
    return &record_flag_bd46;
}
#ifdef __cplusplus
}
#endif
