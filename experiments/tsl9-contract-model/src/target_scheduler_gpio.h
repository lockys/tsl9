#ifndef TSL9_TARGET_SCHEDULER_GPIO_H
#define TSL9_TARGET_SCHEDULER_GPIO_H
/* Fixed V4.1.00 native ABI. Historical R36 asm names now bind real functions.
 * The original-address names are linkage identity, not physical pin attribution. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_gpio_status_init(void) __asm__("tsl9_runtime_unported_9b2c");
void tsl9_gpio_status_toggle(void) __asm__("tsl9_runtime_unported_9b14");
#ifdef __cplusplus
}
#endif
#endif
