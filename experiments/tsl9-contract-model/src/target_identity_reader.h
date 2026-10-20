#ifndef TSL9_TARGET_IDENTITY_READER_H
#define TSL9_TARGET_IDENTITY_READER_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* RV32-only original6-byte reader; destination/address validity is a hardware
 * precondition, not checked here. Never execute this entry on the host. */
void tsl9_identity_reader_native(uint8_t *output6) __asm__("tsl9_runtime_unported_18caa");
#ifdef __cplusplus
}
#endif
#endif

