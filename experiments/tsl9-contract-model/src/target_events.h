#ifndef TSL9_TARGET_EVENTS_H
#define TSL9_TARGET_EVENTS_H
#ifdef __cplusplus
extern "C" {
#endif
/* RV32 naked IRQ/context entries. Never invoke as normal C functions.
 * Exact original register/frame/MMIO contracts depend on physical core entry.
 * No host execution, poll timeout or generic compiler interrupt ABI is added. */
#if defined(__riscv) && __riscv_xlen == 32
void tsl9_context_restore_irq(void) __attribute__((noreturn));
void tsl9_exti_5_9_irq(void) __attribute__((noreturn));
void tsl9_rtc_alarm_irq(void) __attribute__((noreturn));
#endif
#ifdef __cplusplus
}
#endif
#endif

