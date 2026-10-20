#ifndef TSL9_TARGET_BLE_PLATFORM_H
#define TSL9_TARGET_BLE_PLATFORM_H
/* V4.1.00 native ABI only; no ROM, radio or physical-hardware proof. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_ble_platform_init(void) __asm__("tsl9_runtime_unported_8e82");
#ifdef __cplusplus
}
#endif
#endif
