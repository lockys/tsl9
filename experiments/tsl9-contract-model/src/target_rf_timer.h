#ifndef TSL9_TARGET_RF_TIMER_H
#define TSL9_TARGET_RF_TIMER_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original register-level entries; not host-callable typed APIs or hardware ABI proof. */
void tsl9_timer_schedule(void) __asm__("tsl9_runtime_unported_9432");
void tsl9_timer_initialize(void) __asm__("tsl9_runtime_unported_9936");
void tsl9_rf_initialize(void) __asm__("tsl9_runtime_unported_17176");
#ifdef __cplusplus
}
#endif
#endif
