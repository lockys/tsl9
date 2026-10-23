#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 SDK-candidate private regions only; do not execute on a host/device.
#endif

/* Public WCH V1.31 candidate [0x405A2,0x405DC), conditionally copied to
 * [0x20000332,0x2000036C). This is NOT installed TSL9 resident identity.
 * C owns unsigned arithmetic and volatile memory requests. Explicit control
 * ports retain branch layout and live-register boundaries. Link all regions
 * together at the conditional RAM address; no ordinary standalone C ABI.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define REGS \
    register uint32_t a0 __asm__("a0"); \
    register uint32_t a1 __asm__("a1"); \
    register uint32_t a2 __asm__("a2"); \
    register uint32_t a3 __asm__("a3"); \
    register uint32_t a4 __asm__("a4"); \
    register uint32_t a5 __asm__("a5"); \
    register uint32_t a6 __asm__("a6"); \
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2), "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory")
#define LIVE __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5), "+r"(a6) : : "memory")

REGION void tsl9_candidate_copy_arch_20000332(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 524u); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 524u) = 0; LIVE;
    __asm__ volatile("fence.i" : : : "memory");
    __asm__ volatile(".Lcopy_null_dst:\nc.beqz a0, .Lcopy_null_dst\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_candidate_copy_restore_2000034a\n"
                     : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_candidate_copy_source_guard_20000344(void)
{
    REGS;
    __asm__ volatile(".Lcopy_null_src:\nc.beqz a1, .Lcopy_null_src\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_candidate_copy_restore_2000034a\n"
                     : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_candidate_copy_count_20000346(void)
{
    REGS;
    a5 = 0; LIVE;
    __asm__ volatile(".Lcopy_count:\nc.bnez a2, .Lcopy_count\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_candidate_copy_loop_20000354\n"
                     : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_candidate_copy_restore_2000034a(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 524u) = a4; LIVE;
    __asm__ volatile("ret" : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_candidate_copy_loop_20000354(void)
{
    REGS;
    a3 = a1 + a5; LIVE;
    a6 = *(volatile uint8_t *)(uintptr_t)a3; LIVE;
    a3 = a0 + a5; LIVE;
    a5 += 1u; LIVE;
    *(volatile uint8_t *)(uintptr_t)a3 = (uint8_t)a6; LIVE;
    __asm__ volatile(".Lcopy_loop:\nbne a2, a5, .Lcopy_loop\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_candidate_copy_loop_20000354\n"
                     : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_candidate_copy_finish_2000036a(void)
{
    REGS;
    __asm__ volatile(".Lcopy_finish:\nc.j .Lcopy_finish\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_candidate_copy_restore_2000034a\n"
                     : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}
