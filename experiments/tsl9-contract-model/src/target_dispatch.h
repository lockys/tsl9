#ifndef TSL9_TARGET_DISPATCH_H
#define TSL9_TARGET_DISPATCH_H
#ifdef __cplusplus
extern "C" {
#endif
/* RV32 original calling convention; argument/return registers preserved in assembly. */
void tsl9_dispatch_native(void) __asm__("tsl9_runtime_unported_14af8");
#ifdef __cplusplus
}
#endif
#endif
