/* Pure C leaf models only the store, not the BD46 transfer. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_record_helpers_block_f030(volatile unsigned char *base, unsigned value)
{
    base[10] = (unsigned char)value;
}
#ifdef __cplusplus
}
#endif
