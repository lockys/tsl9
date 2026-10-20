#ifndef TSL9_TARGET_BOARD_INIT_H
#define TSL9_TARGET_BOARD_INIT_H
/* V4.1.00 original-address linkage names preserve the R36 caller boundary.
 * These three historical "unported" asm symbols now have actual function bodies.
 * Native RV32 only; CSR/MMIO routines must not be invoked on the analysis host. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_board_clock_irq_init(void) __asm__("tsl9_runtime_unported_9a20");
void tsl9_board_delay_calibrate(void) __asm__("tsl9_runtime_unported_19490");
void tsl9_board_watchdog_init(void) __asm__("tsl9_runtime_unported_9e66");
#ifdef __cplusplus
}
#endif
#endif
