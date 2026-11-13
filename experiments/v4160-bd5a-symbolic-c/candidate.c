#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char record_flag_bd5a;
__attribute__((section(".leaf"), used))
void candidate(unsigned char value)
{
    record_flag_bd5a = value;
}
#ifdef __cplusplus
}
#endif
