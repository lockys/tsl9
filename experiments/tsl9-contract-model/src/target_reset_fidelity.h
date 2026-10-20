#ifndef TSL9_TARGET_RESET_FIDELITY_H
#define TSL9_TARGET_RESET_FIDELITY_H
#ifdef __cplusplus
extern "C" {
#endif
/* Register-level RV32 reset entry. No C ABI, physical ROM or final layout proof.
 * GP/SP use true PC-relative linker contracts before any stack access/call.
 * data_end and bss_start are original GP+136 observations, not allocations. */
#if defined(__riscv) && __riscv_xlen == 32
void tsl9_reset_entry(void) __attribute__((noreturn));
#endif
#ifdef __cplusplus
}
#endif
#endif
