#ifndef TSL9_RUNTIME_MAIN_PORTS_H
#define TSL9_RUNTIME_MAIN_PORTS_H

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private entry only; never execute on the host.
#endif

/* The original wrapper uses a compressed JAL, then a full JAL.
 * Both providers remain undefined here; declarations are not providers.
 * The clobbers describe the compiler boundary, not a proved callee ABI. */
#define TSL9_MAIN_CALL_CLOBBERS \
    "ra", "t0", "t1", "t2", "t3", "t4", "t5", "t6", \
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "memory"

static __attribute__((always_inline)) inline void tsl9_main_first_call(void)
{
    __asm__ volatile("c.jal tsl9_runtime_entry_9250\n" : : : TSL9_MAIN_CALL_CLOBBERS);
}

static __attribute__((always_inline)) inline void tsl9_main_second_call(void)
{
    __asm__ volatile("jal ra, tsl9_runtime_entry_8180\n" : : : TSL9_MAIN_CALL_CLOBBERS);
}

#endif
