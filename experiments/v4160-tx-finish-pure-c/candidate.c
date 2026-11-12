#include <stdint.h>
#include <limits.h>

/* Independent fragments, not a callable replacement for the original ABI.
 * Each address must designate a valid, suitably aligned volatile C object of
 * the accessed type. Integer-to-pointer mapping is implementation-defined. */
_Static_assert(CHAR_BIT == 8, "8-bit byte required");

static uint32_t add32(uint32_t a, uint32_t b)
{
    return (uint32_t)((uint64_t)a + (uint64_t)b);
}

/* 8b14..8b1a: a5 is the incoming D, s0 is the live length. */
void finish_checksum(uint32_t d, uint32_t s0, uint32_t a4)
{
    uint32_t address = add32(add32(d, s0), 5);
    *(volatile unsigned char *)(uintptr_t)address = (unsigned char)a4;
}

struct restored { uint32_t ra, s1, s2, s3; };
/* 8b26..8b2e: four independent, sequenced fresh word reads. */
struct restored finish_restore(uint32_t sp)
{
    struct restored r;
    r.ra = *(volatile uint32_t *)(uintptr_t)add32(sp, 28);
    r.s1 = *(volatile uint32_t *)(uintptr_t)add32(sp, 20);
    r.s2 = *(volatile uint32_t *)(uintptr_t)add32(sp, 16);
    r.s3 = *(volatile uint32_t *)(uintptr_t)add32(sp, 12);
    return r;
}

/* 8b30..8b3a: single halfword accesses, never two byte stores. */
void finish_metadata(uint32_t bank_base, uint32_t length)
{
    *(volatile uint16_t *)(uintptr_t)add32(bank_base, 2) = (uint16_t)add32(length, 6);
    *(volatile uint16_t *)(uintptr_t)add32(bank_base, 4) = 0;
}

struct tail_values { uint32_t s0, t1, a0, a1, a2, a5, sp; };
/* 8b3a..8b50: no tail call. byte may alias either fresh word read. */
struct tail_values finish_tail(uint32_t gp, uint32_t bank, uint32_t sp)
{
    struct tail_values r;
    r.a2 = add32(add32(gp, 148), (uint32_t)((uint64_t)bank * 4));
    r.s0 = *(volatile uint32_t *)(uintptr_t)add32(sp, 24);
    r.a5 = UINT32_C(0x40000);
    r.t1 = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x40050);
    r.a0 = *(volatile unsigned char *)(uintptr_t)r.a2;
    r.a1 = 1;
    r.sp = add32(sp, 32);
    return r;
}

/* 8b1a..8b26 and 8b30: value-only arithmetic, independent of memory. */
uint32_t finish_bank_base(uint32_t a3, uint32_t bank)
{
    return add32(a3, (uint32_t)((uint64_t)bank * 1062));
}
