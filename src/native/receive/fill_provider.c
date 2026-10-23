#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private fill regions only; never execute on a host or device.
#endif

/* Original [0x8520,0x85C8). Explicit AUIPC/JALR/RA ports retain computed
 * jumps into the descending byte-store table. C owns arithmetic and volatile
 * word/byte stores. Link all regions at their original PCs before interpreting
 * computed targets. No libc substitution or separately callable C ABI is used.
 * A0 stays unchanged; SP/S/GP are untouched by this bounded instruction body.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))
#define REGS \
    register uint32_t t0 __asm__("t0"); \
    register uint32_t t1 __asm__("t1"); \
    register uint32_t a0 __asm__("a0"); \
    register uint32_t a1 __asm__("a1"); \
    register uint32_t a2 __asm__("a2"); \
    register uint32_t a3 __asm__("a3"); \
    register uint32_t a4 __asm__("a4"); \
    register uint32_t a5 __asm__("a5"); \
    __asm__ volatile("" : "=r"(t0), "=r"(t1), "=r"(a0), "=r"(a1), "=r"(a2), "=r"(a3), "=r"(a4), "=r"(a5) : : "memory")
#define LIVE __asm__ volatile("" : "+r"(t0), "+r"(t1), "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) : : "memory")
REGION void tsl9_tagged_external_8520(void)
{
    REGS;
    t1 = 15; LIVE;
    a4 = a0; LIVE;
    __asm__ volatile(".Lfill_short:\nbgeu t1, a2, .Lfill_short\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_fill_tail_dispatch_854a\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_alignment_8528(void)
{
    REGS;
    a5 = a4 & 15u; LIVE;
    __asm__ volatile(".Lfill_unaligned:\nc.bnez a5, .Lfill_unaligned\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_fill_align_dispatch_85aa\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_pattern_guard_852e(void)
{
    REGS;
    __asm__ volatile(".Lfill_nonzero:\nc.bnez a1, .Lfill_nonzero\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_fill_pattern_8598\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_word_setup_8530(void)
{
    REGS;
    a3 = a2 & UINT32_C(0xfffffff0); LIVE;
    a2 &= 15u; LIVE;
    a3 += a4; LIVE;
    __builtin_unreachable();
}

REGION void tsl9_fill_words_8538(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + 0u) = a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 4u) = a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 8u) = a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 12u) = a1; LIVE;
    a4 += 16u; LIVE;
    __asm__ volatile(".Lfill_words:\nbltu a4, a3, .Lfill_words\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_fill_words_8538\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_tail_guard_8546(void)
{
    REGS;
    __asm__ volatile(".Lfill_remainder:\nc.bnez a2, .Lfill_remainder\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_fill_tail_dispatch_854a\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_fill_word_return_8548(void)
{
    __asm__ volatile("ret\n");
}

REGION void tsl9_fill_tail_dispatch_854a(void)
{
    REGS;
    a3 = t1 - a2; LIVE;
    a3 <<= 2; LIVE;
    __asm__ volatile("auipc t0, 0\n" : "=r"(t0) : : "memory");
    LIVE;
    a3 += t0; LIVE;
    __asm__ volatile("jalr zero, 10(a3)\n" : : "r"(a3) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_bytes_855a(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a4 + 14u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 13u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 12u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 11u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 10u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 9u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 8u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 7u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 6u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 5u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 4u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 3u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 2u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 1u) = (uint8_t)a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 0u) = (uint8_t)a1; LIVE;
    __builtin_unreachable();
}

FRAME void tsl9_fill_byte_return_8596(void)
{
    __asm__ volatile("ret\n");
}

REGION void tsl9_fill_pattern_8598(void)
{
    REGS;
    a1 &= 255u; LIVE;
    a3 = a1 << 8; LIVE;
    a1 |= a3; LIVE;
    a3 = a1 << 16; LIVE;
    a1 |= a3; LIVE;
    __asm__ volatile(".Lfill_pattern_done:\nc.j .Lfill_pattern_done\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_fill_word_setup_8530\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_align_dispatch_85aa(void)
{
    REGS;
    a3 = a5 << 2; LIVE;
    __asm__ volatile("auipc t0, 0\n" : "=r"(t0) : : "memory");
    LIVE;
    a3 += t0; LIVE;
    __asm__ volatile("mv t0, ra\njalr ra, -88(a3)\n" : "+r"(t0) : "r"(a3) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_fill_align_resume_85ba(void)
{
    REGS;
    __asm__ volatile("mv ra, t0\n" : : "r"(t0) : "memory");
    LIVE;
    a5 -= 16u; LIVE;
    a4 -= a5; LIVE;
    a2 += a5; LIVE;
    __asm__ volatile(".Lfill_aligned_short:\nbgeu t1, a2, .Lfill_aligned_short\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_fill_tail_dispatch_854a\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __asm__ volatile(".Lfill_align_done:\nc.j .Lfill_align_done\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_fill_pattern_guard_852e\n"
                     : : "r"(t1), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}
