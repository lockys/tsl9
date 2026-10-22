#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 interrupt regions only; never execute on the host.
#endif

/* Private interrupt regions, not ordinary C ABI functions. C expresses the
 * word-sized status read/mask and the zero tag. Explicit
 * ports preserve the conditional frame, true JALs and both MRET exits.
 * v2 uses physical SP load/address ports: importing SP as a C value in v1
 * let LLVM cache it in A1 and emit an extra write back to SP.
 * Provider 18D78 and complete interrupt/silicon contracts remain unknown.
 */
#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_ring_irq_entry_12c24(void)
{
    register uintptr_t base __asm__("a0") = UINT32_C(0x40006000);
    __asm__ volatile("" : "+r"(base) : : "memory");
    base += 1024u;
    __asm__ volatile("" : "+r"(base) : : "memory");
    register uint32_t status __asm__("a5") = *(volatile uint32_t *)(base + 12u);
    status &= 3u;
    __asm__ volatile(".Lirq_empty:\nc.beqz a5, .Lirq_empty\n"
                     ".reloc .Lirq_empty, R_RISCV_RVC_BRANCH, tsl9_ring_irq_empty_12c54\n"
                     : : "r"(status), "r"(base) : "memory");
    __builtin_unreachable();
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_ring_irq_frame_12c32(void)
{
    __asm__ volatile("addi sp, sp, -32\naddi a2, sp, 12\nli a1, 0\n"
                     "jal ra, tsl9_irq_provider_18d78\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_ring_irq_dispatch_12c3c(void)
{
    /* Each access uses the then-live physical SP after the opaque provider.
     * Do not import/cache SP as an ordinary compiler SSA address value. */
    register uint32_t length __asm__("a2");
    register uint32_t identifier __asm__("a0");
    register uintptr_t payload __asm__("a1");
    __asm__ volatile("lbu a2, 22(sp)\nlhu a0, 12(sp)\naddi a1, sp, 23\n"
                     : "=r"(length), "=r"(identifier), "=r"(payload) : : "memory");
    register uint32_t tag __asm__("a3") = 0;
    __asm__ volatile("jal ra, tsl9_ring_insert_entry_12bc8\n"
                     : "+r"(identifier), "+r"(payload), "+r"(length), "+r"(tag)
                     : : "a4", "a5", "memory");
    __builtin_unreachable();
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_ring_irq_finish_12c4e(void)
{
    /* Then-live SP after ring, followed by MRET, never an ordinary RET. */
    __asm__ volatile("addi sp, sp, 32\nmret\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_ring_irq_empty_12c54(void)
{
    __asm__ volatile("mret\n");
}
