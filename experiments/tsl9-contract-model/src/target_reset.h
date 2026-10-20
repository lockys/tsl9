#ifndef TSL9_TARGET_RESET_H
#define TSL9_TARGET_RESET_H
#ifdef __cplusplus
extern "C" {
#endif
/* Genuine RV32 reset component, not a linked firmware or physical ROM proof.
   The first instructions establish gp20004000/sp20010000 before any C call.
   Final linker must provide aligned data_load/data_start/data_end,bss_start/end,
   vector_table,runtime_entry and absolute rom_entry40000. No default addresses,
   replacement main, vector stubs or final image are supplied here.
   data_start must equal gp and data/bss must respect ROM low16KB, heap/stack
   obligations and actual flash layout. mtvec mode3 and ROM handoff retain
   fixed-target evidence; physical core/ROM ABI remains unverified. */
#if defined(__riscv) && __riscv_xlen == 32
void tsl9_reset_entry(void) __attribute__((noreturn));
#endif
#ifdef __cplusplus
}
#endif
#endif
