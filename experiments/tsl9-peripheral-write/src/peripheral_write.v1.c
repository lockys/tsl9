#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 static reconstruction only; never execute on host or hardware.
#endif
/* Empty physical-register ports preserve all then-live values at each C step.
 * No instruction strings, original opcodes, hidden providers or MMIO execution.
 * The selected fixed compiler profile and exact native proof define the scope. */
#define LIVE() __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), \
    "+r"(a3), "+r"(a4), "+r"(a5), "+r"(a6) : : "memory")
#define WORD(base, off) (*(volatile uint32_t *)(uintptr_t)((base) + (off)))
#define BYTE(base, off) (*(volatile uint8_t *)(uintptr_t)((base) + (off)))
#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_dispatch_external_18ca4(uint32_t base, uint32_t record)
{
    register uint32_t a0 __asm__("a0") = base;
    register uint32_t a1 __asm__("a1") = record;
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    register uint32_t a6 __asm__("a6");
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "=r"(a2),
        "=r"(a3), "=r"(a4), "=r"(a5), "=r"(a6) : : "memory");

    a5 = WORD(a0, 8u); LIVE();
    a4 = a5 << 5; LIVE();
    if ((int32_t)a4 < 0) goto select0;
    a5 = WORD(a0, 8u); LIVE();
    a4 = a5 << 4; LIVE();
    if ((int32_t)a4 < 0) goto select1;
    a5 = WORD(a0, 8u); LIVE();
    a3 = 4; LIVE();
    a4 = a5 << 3; LIVE();
    if ((int32_t)a4 >= 0) goto finish;
    a3 = 2; LIVE();
selected:
    a5 = a3 << 4; LIVE();
    a5 += a0; LIVE();
    a4 = WORD(a5, 384u); LIVE();
    a4 &= 1u; LIVE();
    WORD(a5, 384u) = a4; LIVE();
    a2 = BYTE(a1, 8u); LIVE();
    a0 = BYTE(a1, 9u); LIVE();
    if (a2 != 0) goto alternate;
    a4 = WORD(a1, 0u); LIVE();
    a2 = WORD(a5, 384u); LIVE();
    a4 <<= 21; LIVE();
    a4 |= a0; LIVE();
    a4 |= a2; LIVE();
write_identifier:
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
finish:
    a0 = a3; LIVE();
    return a0;
select0:
    a3 = 0; LIVE();
    goto selected;
select1:
    a3 = 1; LIVE();
    goto selected;
alternate:
    a4 = WORD(a1, 4u); LIVE();
    a6 = WORD(a5, 384u); LIVE();
    a4 <<= 3; LIVE();
    a4 |= a0; LIVE();
    a4 |= a2; LIVE();
    a4 |= a6; LIVE();
    goto write_identifier;
}
#undef LIVE
#undef WORD
#undef BYTE
