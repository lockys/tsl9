#ifndef TSL9_TARGET_PERIPHERALS_H
#define TSL9_TARGET_PERIPHERALS_H
#ifdef __cplusplus
extern "C" {
#endif
/* RV32 naked original CAN/TIM candidate entries: never normal C calls.
 * Two SRAM symbols require final layout; ROM/callback ABI remains unproved.
 * This header authorizes no peripheral execution or physical flashing. */
#if defined(__riscv) && __riscv_xlen == 32
void tsl9_can_rx0_irq(void) __attribute__((noreturn));
void tsl9_timer3_irq(void) __attribute__((noreturn));
#endif
#ifdef __cplusplus
}
#endif
#endif

