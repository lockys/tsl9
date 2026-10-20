#ifndef TSL9_TARGET_CONFIG_STORAGE_H
#define TSL9_TARGET_CONFIG_STORAGE_H
/* V4.1.00 native ABI, static compilation only. No physical Flash/ROM proof.
 * Historical caller names bind actual functions; 935C remains opaque. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_config_init(void) __asm__("tsl9_runtime_unported_9e2c");
void tsl9_records_init(void) __asm__("tsl9_runtime_unported_14a54");
#ifdef __cplusplus
}
#endif
#endif
