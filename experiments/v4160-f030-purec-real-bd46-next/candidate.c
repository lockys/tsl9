/* State-adapter hypothesis, not the private F030 register ABI. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_record_helpers_provider_bd46(void);
void tsl9_record_helpers_block_f030(volatile unsigned char *base, unsigned value)
{
    base[10] = (unsigned char)value;
    tsl9_record_helpers_provider_bd46();
}
#ifdef __cplusplus
}
#endif
