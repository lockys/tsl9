#ifndef TSL9_TARGET_BUS_INIT_H
#define TSL9_TARGET_BUS_INIT_H
#ifdef __cplusplus
extern "C" {
#endif
/* Register-level entries; actual ROM/MMIO/IRQ and hardware behavior are unverified. */
void tsl9_can_initialize(void) __asm__("tsl9_runtime_unported_12b9c");
void tsl9_spi_peripheral_initialize(void) __asm__("tsl9_runtime_unported_16dac");
#ifdef __cplusplus
}
#endif
#endif
