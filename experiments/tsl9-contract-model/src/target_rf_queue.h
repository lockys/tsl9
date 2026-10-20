#ifndef TSL9_TARGET_RF_QUEUE_H
#define TSL9_TARGET_RF_QUEUE_H
#ifdef __cplusplus
extern "C" {
#endif
/* Register-level entries; resident ROM ABI and typed host-call ABI are unverified. */
void tsl9_rf_queue_enqueue(void) __asm__("tsl9_runtime_unported_17650");
void tsl9_rf_queue_init(void) __asm__("tsl9_runtime_unported_179ca");
#ifdef __cplusplus
}
#endif
#endif
