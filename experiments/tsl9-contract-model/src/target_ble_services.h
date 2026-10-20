#ifndef TSL9_TARGET_BLE_SERVICES_H
#define TSL9_TARGET_BLE_SERVICES_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original register-level entry contracts; ROM ABI remains opaque. */
void tsl9_ble_services_init(void) __asm__("tsl9_runtime_unported_12388");
void tsl9_rtc_startup_init(void) __asm__("tsl9_runtime_unported_1986a");
#ifdef __cplusplus
}
#endif
#endif
