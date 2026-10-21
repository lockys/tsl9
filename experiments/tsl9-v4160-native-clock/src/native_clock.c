#include "native_clock.h"
#include <stdint.h>

#if defined(TSL9_CLOCK_HOST_TEST)
#include "test_io.h"
#define current_gp tsl9_nc_test_gp
#define read32 tsl9_nc_test_read32
#define read8 tsl9_nc_test_read8
#define write32 tsl9_nc_test_write32
#define write8 tsl9_nc_test_write8
#define write16 tsl9_nc_test_write16
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error This component requires RV32 or the explicit host-test adapter.
#endif
static uint32_t current_gp(void)
{
    uint32_t value;
    __asm__ volatile("mv %0, gp" : "=r"(value) : : "memory");
    return value;
}
static uint32_t read32(uint32_t address)
{
    return *(volatile uint32_t *)(uintptr_t)address;
}
static uint8_t read8(uint32_t address)
{
    return *(volatile uint8_t *)(uintptr_t)address;
}
static void write32(uint32_t address, uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)address = value;
}
static void write8(uint32_t address, uint8_t value)
{
    *(volatile uint8_t *)(uintptr_t)address = value;
}
static void write16(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)(uintptr_t)address = value;
}
#endif

/* Source contract: ID2966 V4.1.60 [0x18834,0x188e2).
 * Each read is a separate live observation. These ordinary C interfaces do
 * not preserve the original function's complete register/interrupt ABI. */
void tsl9_rebuild_clock_query_18834(void)
{
    const uint32_t rcc = UINT32_C(0x40021004);
    const uint32_t selector = read32(rcc) & UINT32_C(12);
    uint32_t frequency;
    if (selector == 4u) {
        frequency = UINT32_C(32000000);
    } else if (selector == 8u) {
        const uint32_t multiplier_sample = read32(rcc);
        const uint32_t source_sample = read32(rcc);
        uint32_t multiplier = ((multiplier_sample >> 18) & 15u) + 2u;
        uint32_t base;
        if (multiplier == 17u) multiplier = 18u;
        if ((source_sample & UINT32_C(0x10000)) == 0u) {
            const uint32_t control = read32(UINT32_C(0x40023800));
            base = (control & 16u) != 0u ? UINT32_C(8000000) : UINT32_C(4000000);
        } else {
            const uint32_t external_sample = read32(rcc);
            if ((external_sample & UINT32_C(0xc00000)) == UINT32_C(0xc00000)) {
                base = UINT32_C(16000000);
            } else {
                const uint32_t fallback_sample = read32(rcc);
                base = (fallback_sample & UINT32_C(0x20000)) != 0u
                    ? UINT32_C(4000000) : UINT32_C(8000000);
            }
        }
        frequency = multiplier * base;
    } else {
        frequency = UINT32_C(8000000);
    }
    write32(current_gp() + 108u, frequency);
    {
        const uint32_t prescaler_sample = read32(rcc);
        const uint32_t index = (prescaler_sample >> 4) & 15u;
        const uint8_t shift = read8(current_gp() + 64u + index);
        const uint32_t live_frequency = read32(current_gp() + 108u);
        write32(current_gp() + 108u, live_frequency >> (shift & 31u));
    }
}

/* Source contract: ID2966 V4.1.60 [0x1973c,0x19764).
 * Truncate the unsigned quotient before multiplying; never reload the byte. */
void tsl9_rebuild_clock_fields_1973c(void)
{
    const uint32_t frequency = read32(current_gp() + 108u);
    const uint32_t quotient = (frequency / UINT32_C(8000000)) & 255u;
    write8(current_gp() + 382u, (uint8_t)quotient);
    write16(current_gp() + 380u, (uint16_t)(quotient * 1000u));
}
