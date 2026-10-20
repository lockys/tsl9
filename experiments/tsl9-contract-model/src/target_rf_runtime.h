#ifndef TSL9_TARGET_RF_RUNTIME_H
#define TSL9_TARGET_RF_RUNTIME_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original register-level entries. Typed host-call and resident ROM ABI are unverified. */
void tsl9_rf_transmit(void) __asm__("tsl9_runtime_unported_1730e");
void tsl9_rf_init(void) __asm__("tsl9_runtime_unported_173bc");
#ifdef __cplusplus
}
#endif
#endif
