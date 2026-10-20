#ifndef TSL9_TARGET_INIT_CHECK_H
#define TSL9_TARGET_INIT_CHECK_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original RV32 startup check. Preserves the actual false outcome and ROM
 * dependency; no host execution, provisioning utility, or activation bypass. */
void tsl9_init_check_native(void) __asm__("tsl9_runtime_unported_935c");
#ifdef __cplusplus
}
#endif
#endif
