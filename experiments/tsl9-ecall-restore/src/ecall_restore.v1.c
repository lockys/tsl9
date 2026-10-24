#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error Private RV32 context regions only; never execute on the host.
#endif

#ifdef __cplusplus
#define TSL9_ENTRY extern "C"
#else
#define TSL9_ENTRY
#endif

/* Restore an existing architectural frame. This entry does not allocate one.
 * CSRS preserves the other CSR bits; mask32 is not a complete CSR value.
 * The physical SP+0 load supplies MEPC. Ordinary trap ABI is not established.
 */
TSL9_ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
void tsl9_ecall_restore_entry_8448(void)
{
    register uint32_t mask __asm__("a1") = 32u;
    __asm__ volatile("" : "+r"(mask) : : "memory");
    __asm__ volatile("csrs 0x804, a1\nlw a1, 0(sp)\ncsrw mepc, a1\n"
                     : "+r"(mask) : : "memory");
    __builtin_unreachable();
}

TSL9_ENTRY __attribute__((naked, used, aligned(2)))
void tsl9_ecall_restore_finish_8456(void)
{
    /* Then-live SP;29 original register loads. No explicit GP frame load. */
    __asm__ volatile(
        "lw ra, 4(sp)\n"
        "lw tp, 8(sp)\n"
        "lw t0, 12(sp)\n"
        "lw t1, 16(sp)\n"
        "lw t2, 20(sp)\n"
        "lw s0, 24(sp)\n"
        "lw s1, 28(sp)\n"
        "lw a0, 32(sp)\n"
        "lw a1, 36(sp)\n"
        "lw a2, 40(sp)\n"
        "lw a3, 44(sp)\n"
        "lw a4, 48(sp)\n"
        "lw a5, 52(sp)\n"
        "lw a6, 56(sp)\n"
        "lw a7, 60(sp)\n"
        "lw s2, 64(sp)\n"
        "lw s3, 68(sp)\n"
        "lw s4, 72(sp)\n"
        "lw s5, 76(sp)\n"
        "lw s6, 80(sp)\n"
        "lw s7, 84(sp)\n"
        "lw s8, 88(sp)\n"
        "lw s9, 92(sp)\n"
        "lw s10, 96(sp)\n"
        "lw s11, 100(sp)\n"
        "lw t3, 104(sp)\n"
        "lw t4, 108(sp)\n"
        "lw t5, 112(sp)\n"
        "lw t6, 116(sp)\n"
        "addi sp, sp, 128\n"
        "mret\n"
    );
}
