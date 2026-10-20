#ifndef TSL9_TARGET_SYSTEM_CLOCK_H
#define TSL9_TARGET_SYSTEM_CLOCK_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original1849E..18588 register entry; native RV32 only, never host-run.
 * Exact16B leaf frame, live MMIO/stack reads and unbounded waits retained.
 * Physical clock, IRQ/stack budget, ROM and OTA remain unverified. */
void sc_native_init(void);
#ifdef __cplusplus
}
#endif
#endif
