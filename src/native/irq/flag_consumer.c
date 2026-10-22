#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private consumer only; never execute on the host.
#endif

static __attribute__((always_inline)) inline uintptr_t live_gp(void)
{
    register uintptr_t gp __asm__("gp");
    __asm__ volatile("" : "=r"(gp) : : "memory");
    return gp;
}

/* RA/SP are reserved architectural state owned exclusively by the measured
 * entry/exit ports, not C allocator values. The opaque callee may also change
 * GP; every subsequent GP-relative operation imports the then-live GP. */
static __attribute__((always_inline)) inline void dispatch(uint32_t channel)
{
    register uint32_t a0 __asm__("a0") = channel;
    __asm__ volatile("jal ra, tsl9_receive_entry_16b0a\n"
                     : "+r"(a0) : : "a4", "a5", "memory");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_flag_consumer_entry_17002(void)
{
    /* The first volatile read occurs between allocation and saving RA.
     * The linker must prove immediate fall-through to the body. */
    __asm__ volatile("addi sp, sp, -16\nlbu a5, 360(gp)\nsw ra, 12(sp)\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_flag_consumer_body(void)
{
    register uint32_t first __asm__("a5");
    __asm__ volatile("" : "=r"(first) : : "memory");
    register uint32_t first_bit __asm__("a4") = first & UINT32_C(1);
    __asm__ volatile("" : "+r"(first), "+r"(first_bit) : : "memory");
    if (first_bit != 0u) {
        first = first & UINT32_C(0xfffffffe);
        __asm__ volatile("" : "+r"(first) : : "memory");
        register uint32_t channel __asm__("a0") = 1;
        __asm__ volatile("" : "+r"(first), "+r"(channel) : "r"(first_bit) : "memory");
        *(volatile uint8_t *)(live_gp() + 360u) = (uint8_t)first;
        dispatch(channel);
        *(volatile uint8_t *)(live_gp() + 361u) = 0;
    }

    register uint32_t second __asm__("a5") =
        *(volatile uint8_t *)(live_gp() + 360u);
    register uint32_t second_bit __asm__("a4") = second & UINT32_C(2);
    __asm__ volatile("" : "+r"(second), "+r"(second_bit) : : "memory");
    if (second_bit != 0u) {
        second = second & UINT32_C(0xfffffffd);
        __asm__ volatile("" : "+r"(second) : : "memory");
        register uint32_t channel __asm__("a0") = 2;
        __asm__ volatile("" : "+r"(second), "+r"(channel) : "r"(second_bit) : "memory");
        *(volatile uint8_t *)(live_gp() + 360u) = (uint8_t)second;
        dispatch(channel);
        *(volatile uint8_t *)(live_gp() + 362u) = 0;
    }

    /* Fresh saved-slot read after the last possible callee. A0 is left as
     * inherited on the no-call path or returned by the last taken call. */
    __asm__ volatile("lw ra, 12(sp)\naddi sp, sp, 16\nret\n" : : : "memory");
    __builtin_unreachable();
}
