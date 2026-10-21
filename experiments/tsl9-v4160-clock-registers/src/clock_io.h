#ifndef TSL9_CLOCK_REGISTER_IO_H
#define TSL9_CLOCK_REGISTER_IO_H
#include <stdint.h>
#if defined(TSL9_CLOCK_REGISTER_HOST_TEST)
#include "register_test_io.h"
#define CA_GP() tsl9_ca_test_gp()
#define CA_READ32(a) tsl9_ca_test_read32(a)
#define CA_READ8(a) tsl9_ca_test_read8(a)
#define CA_WRITE32(a,v) tsl9_ca_test_write32(a,v)
#define CA_WRITE8(a,v) tsl9_ca_test_write8(a,v)
#define CA_WRITE16(a,v) tsl9_ca_test_write16(a,v)
#define CA_EXTERNAL_MASK() (tsl9_ca_test_set_a2(UINT32_C(0xc00000)),UINT32_C(0xc00000))
#define CA_QUERY_OUTPUTS(r3,r4,r5) tsl9_ca_test_query_outputs(r3,r4,r5)
#define CA_FIELD_OUTPUTS(r4,r5) tsl9_ca_test_field_outputs(r4,r5)
#define CA_DIVIDE_8M(v) ((uint32_t)(v)/UINT32_C(8000000))
#define CA_FIELD_FACTOR() UINT32_C(1000)
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 is required unless the explicit host-test adapter is selected.
#endif
/* Empty asm exposes the live physical GP without emitting a GP assignment.
 * Actual ELF checks must verify no GP writes; this is compiler-specific. */
static inline uint32_t ca_live_gp(void)
{
    register uint32_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}
static inline uint32_t ca_divide_8m(uint32_t value)
{
    uint32_t quotient;
    __asm__ volatile("divu %0, %1, %2" : "=r"(quotient)
                     : "r"(value), "r"(UINT32_C(8000000)));
    return quotient;
}
static inline uint32_t ca_field_factor(void)
{
    register uint32_t factor __asm__("a4")=UINT32_C(1000);
    /* The empty barrier changes no physical value. Its read/write operand
     * keeps this A4 available for MUL and the final register commitment. */
    __asm__ volatile("" : "+r"(factor) : : "memory");
    return factor;
}
static inline uint32_t ca_external_mask(void)
{
    register uint32_t mask __asm__("a2")=UINT32_C(0xc00000);
    __asm__ volatile("" : "+r"(mask) : : "memory");
    return mask;
}
#define CA_GP() ca_live_gp()
#define CA_DIVIDE_8M(v) ca_divide_8m(v)
#define CA_FIELD_FACTOR() ca_field_factor()
#define CA_EXTERNAL_MASK() ca_external_mask()
#define CA_READ32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define CA_READ8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define CA_WRITE32(a,v) (*(volatile uint32_t *)(uintptr_t)(a)=(v))
#define CA_WRITE8(a,v) (*(volatile uint8_t *)(uintptr_t)(a)=(uint8_t)(v))
#define CA_WRITE16(a,v) (*(volatile uint16_t *)(uintptr_t)(a)=(uint16_t)(v))
/* Explicit physical-register commitments; reservation flags and full native
 * write-set/extent checks are required. These are not an interrupt ABI proof. */
#define CA_QUERY_OUTPUTS(r3,r4,r5) do { \
    register uint32_t ca_r3 __asm__("a3")=(r3); \
    register uint32_t ca_r4 __asm__("a4")=(r4); \
    register uint32_t ca_r5 __asm__("a5")=(r5); \
    __asm__ volatile("" : : "r"(ca_r3),"r"(ca_r4),"r"(ca_r5) : "memory"); \
} while (0)
#define CA_FIELD_OUTPUTS(r4,r5) do { \
    register uint32_t ca_r4 __asm__("a4")=(r4); \
    register uint32_t ca_r5 __asm__("a5")=(r5); \
    __asm__ volatile("" : : "r"(ca_r4),"r"(ca_r5) : "memory"); \
} while (0)
#endif
#endif
