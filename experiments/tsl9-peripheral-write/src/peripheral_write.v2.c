#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 static reconstruction only; never execute on host or hardware.
#endif
/* Empty physical-register ports preserve all then-live values at each C step.
 * Arithmetic/reads/writes stay C; explicit symbolic edge/return ports retain layout.
 * The selected fixed compiler profile and exact native proof define the scope. */
#define LIVE() __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), \
    "+r"(a3), "+r"(a4), "+r"(a5), "+r"(a6) : : "memory")
#define WORD(base, off) (*(volatile uint32_t *)(uintptr_t)((base) + (off)))
#define BYTE(base, off) (*(volatile uint8_t *)(uintptr_t)((base) + (off)))
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))

REGION void tsl9_dispatch_external_18ca4(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a5 = WORD(a0, 8u); LIVE();
    a4 = a5 << 5; LIVE();
    __asm__ volatile(".Lperipheral_bit26:\nblt a4, zero, .Lperipheral_bit26\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_peripheral_select0_18d5e\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    a5 = WORD(a0, 8u); LIVE();
    a4 = a5 << 4; LIVE();
    __asm__ volatile(".Lperipheral_bit27:\nblt a4, zero, .Lperipheral_bit27\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_peripheral_select1_18d62\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    a5 = WORD(a0, 8u); LIVE();
    a3 = 4; LIVE();
    a4 = a5 << 3; LIVE();
    __asm__ volatile(".Lperipheral_absent:\nbge a4, zero, .Lperipheral_absent\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_peripheral_finish_18d5a\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    a3 = 2; LIVE();
    __builtin_unreachable();
}

REGION void tsl9_peripheral_selected_18cc6(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a5 = a3 << 4; LIVE();
    a5 += a0; LIVE();
    a4 = WORD(a5, 384u); LIVE();
    a4 &= 1u; LIVE();
    WORD(a5, 384u) = a4; LIVE();
    a2 = BYTE(a1, 8u); LIVE();
    a0 = BYTE(a1, 9u); LIVE();
    __asm__ volatile(".Lperipheral_alternate:\nc.bnez a2, .Lperipheral_alternate\n"
        ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_peripheral_alternate_18d66\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    a4 = WORD(a1, 0u); LIVE();
    a2 = WORD(a5, 384u); LIVE();
    a4 <<= 21; LIVE();
    a4 |= a0; LIVE();
    a4 |= a2; LIVE();
    __builtin_unreachable();
}

REGION void tsl9_peripheral_metadata_18cec(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    WORD(a5, 384u) = a4; LIVE();
    a4 = BYTE(a1, 10u); LIVE();
    a4 &= 15u; LIVE();
    BYTE(a1, 10u) = (uint8_t)a4; LIVE();
    a2 = WORD(a5, 388u); LIVE();
    a2 &= UINT32_C(0xfffffff0); LIVE();
    WORD(a5, 388u) = a2; LIVE();
    a2 = WORD(a5, 388u); LIVE();
    a4 |= a2; LIVE();
    WORD(a5, 388u) = a4; LIVE();
    a2 = BYTE(a1, 12u); LIVE();
    a4 = BYTE(a1, 11u); LIVE();
    a2 <<= 8; LIVE();
    a2 |= a4; LIVE();
    a4 = BYTE(a1, 13u); LIVE();
    a4 <<= 16; LIVE();
    a2 |= a4; LIVE();
    a4 = BYTE(a1, 14u); LIVE();
    a4 <<= 24; LIVE();
    a4 |= a2; LIVE();
    WORD(a5, 392u) = a4; LIVE();
    a2 = BYTE(a1, 16u); LIVE();
    a4 = BYTE(a1, 15u); LIVE();
    a2 <<= 8; LIVE();
    a2 |= a4; LIVE();
    a4 = BYTE(a1, 17u); LIVE();
    a4 <<= 16; LIVE();
    a2 |= a4; LIVE();
    a4 = BYTE(a1, 18u); LIVE();
    a4 <<= 24; LIVE();
    a4 |= a2; LIVE();
    WORD(a5, 396u) = a4; LIVE();
    a4 = WORD(a5, 384u); LIVE();
    a4 |= 1u; LIVE();
    WORD(a5, 384u) = a4; LIVE();
    __builtin_unreachable();
}

REGION void tsl9_peripheral_finish_18d5a(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a0 = a3; LIVE();
    __asm__ volatile("ret\n" : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_peripheral_select0_18d5e(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a3 = 0; LIVE();
    __asm__ volatile(".Lperipheral_select0:\nc.j .Lperipheral_select0\n"
        ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_peripheral_selected_18cc6\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_peripheral_select1_18d62(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a3 = 1; LIVE();
    __asm__ volatile(".Lperipheral_select1:\nc.j .Lperipheral_select1\n"
        ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_peripheral_selected_18cc6\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_peripheral_alternate_18d66(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a4 = WORD(a1, 4u); LIVE();
    a6 = WORD(a5, 384u); LIVE();
    a4 <<= 3; LIVE();
    a4 |= a0; LIVE();
    a4 |= a2; LIVE();
    a4 |= a6; LIVE();
    __asm__ volatile(".Lperipheral_extended_done:\nc.j .Lperipheral_extended_done\n"
        ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_peripheral_metadata_18cec\n"
        : : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5), "r"(a6) : "memory");
    __builtin_unreachable();
}

#undef LIVE
#undef WORD
#undef BYTE
#undef REGION
#undef ENTRY
