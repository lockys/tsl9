#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error Private RV32 IRQ regions only; never execute on the host.
#endif

/* Import the then-live architectural GP; do not assign GP or snapshot RAM. */
static __attribute__((always_inline)) inline uintptr_t live_gp(void)
{
    register uintptr_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}

#ifdef __cplusplus
#define TSL9_ENTRY extern "C"
#else
#define TSL9_ENTRY
#endif

/* 128B frame and29 original physical register stores. GP is not saved.
 * These are private architecture regions, not ordinary C IRQ ABI functions.
 */
TSL9_ENTRY __attribute__((naked, used, aligned(2)))
void tsl9_lle_irq_entry_8498(void)
{
    __asm__ volatile(
        "addi sp, sp, -128\n"
        "sw ra, 4(sp)\n"
        "sw tp, 8(sp)\n"
        "sw t0, 12(sp)\n"
        "sw t1, 16(sp)\n"
        "sw t2, 20(sp)\n"
        "sw s0, 24(sp)\n"
        "sw s1, 28(sp)\n"
        "sw a0, 32(sp)\n"
        "sw a1, 36(sp)\n"
        "sw a2, 40(sp)\n"
        "sw a3, 44(sp)\n"
        "sw a4, 48(sp)\n"
        "sw a5, 52(sp)\n"
        "sw a6, 56(sp)\n"
        "sw a7, 60(sp)\n"
        "sw s2, 64(sp)\n"
        "sw s3, 68(sp)\n"
        "sw s4, 72(sp)\n"
        "sw s5, 76(sp)\n"
        "sw s6, 80(sp)\n"
        "sw s7, 84(sp)\n"
        "sw s8, 88(sp)\n"
        "sw s9, 92(sp)\n"
        "sw s10, 96(sp)\n"
        "sw s11, 100(sp)\n"
        "sw t3, 104(sp)\n"
        "sw t4, 108(sp)\n"
        "sw t5, 112(sp)\n"
        "sw t6, 116(sp)\n"
    );
}

TSL9_ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
void tsl9_lle_irq_callback_84d4(void)
{
    register uintptr_t address __asm__("a1") = live_gp() + 384u;
    __asm__ volatile("" : "+r"(address) : : "memory");
    register uintptr_t callback __asm__("a0") =
        *(volatile uint32_t *)address;
    /* Preserve the original full-width JALR. Identity and preservation of the
     * installed callback are unknown. The exit reads physical SP afterwards.
     */
    __asm__ volatile(".option push\n.option norvc\njalr a0\n.option pop\n"
                     : "+r"(callback) : "r"(address) : "memory");
    __builtin_unreachable();
}

TSL9_ENTRY __attribute__((naked, used, aligned(2)))
void tsl9_lle_irq_finish_84de(void)
{
    /* Every load uses then-live SP after the opaque call; GP stays inherited. */
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
