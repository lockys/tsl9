#ifndef TSL9_TARGET_RUNTIME_ENTRY_H
#define TSL9_TARGET_RUNTIME_ENTRY_H
#ifdef __cplusplus
extern "C" {
#endif
/* RV32 original Runtime entry, not a complete initialized application.
 * Native helpers preserve raw register/MMIO/CSR behavior. Unknown init/feature
 * callees and shared data/ROM/IRQ contracts remain explicit obligations.
 * Never call these native bodies from a host test or execute an ET_REL. */
#if defined(__riscv) && __riscv_xlen == 32
void __tsl9_runtime_entry(void);
#endif
#ifdef __cplusplus
}
#endif
#endif

