#ifndef TSL9_TARGET_CAN_FILTERS_H
#define TSL9_TARGET_CAN_FILTERS_H
#ifdef __cplusplus
extern "C" {
#endif
/* Original register-level entry; no host-callable typed API or proven device ABI. */
void tsl9_can_route_filters(void) __asm__("tsl9_runtime_unported_1290a");
#ifdef __cplusplus
}
#endif
#endif
