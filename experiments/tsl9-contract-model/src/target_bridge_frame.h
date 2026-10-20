#ifndef TSL9_TARGET_BRIDGE_FRAME_H
#define TSL9_TARGET_BRIDGE_FRAME_H
/* Original register-level RV32 entry: a0 points at the source record.
 * Does not establish a host ABI, valid device pointers, ROM effects or OTA readiness. */
#ifdef __cplusplus
extern "C" {
#endif
void tsl9_bridge_route_frame(void) __asm__("tsl9_runtime_unported_82c8");
#ifdef __cplusplus
}
#endif
#endif
