#ifndef TSL9_TARGET_CAN_TRANSMIT_H
#define TSL9_TARGET_CAN_TRANSMIT_H
#ifdef __cplusplus
extern "C" {
#endif
/* Register-level entries only; physical ROM/MMIO/IRQ and typed host ABI are unverified. */
void tsl9_can_gate_reset(void) __asm__("tsl9_runtime_unported_8202");
void tsl9_rf_status_receive(void) __asm__("tsl9_runtime_unported_c612");
void tsl9_can_transmit(void) __asm__("tsl9_runtime_unported_12864");
void tsl9_spi_receive_task(void) __asm__("tsl9_runtime_unported_1687e");
#ifdef __cplusplus
}
#endif
#endif
