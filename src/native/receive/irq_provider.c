#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private provider regions only; never execute on the host.
#endif

/* C owns fresh volatile word reads, shifts, masks and byte/word stores.
 * Explicit region edges preserve original cold-block layout and physical
 * register values. These are private regions, not ordinary C ABI entries.
 * v2 fixes each bank read in A5 before OR32; v1 used A1 as an extra scratch.
 * Peripheral identity, IRQ context and complete firmware remain unproved. */
#ifdef __cplusplus
#define TSL9_ENTRY extern "C"
#else
#define TSL9_ENTRY
#endif
#define TSL9_REGION TSL9_ENTRY __attribute__((used, noinline, noreturn, aligned(2)))

TSL9_REGION void tsl9_irq_provider_18d78(void)
{
    register uintptr_t base __asm__("a0");
    register uint32_t selector __asm__("a1");
    register uintptr_t output __asm__("a2");
    __asm__ volatile("" : "=r"(base), "=r"(selector), "=r"(output) : : "memory");
    register uintptr_t bank __asm__("a5") = selector << 4;
    __asm__ volatile("" : "+r"(bank) : "r"(base), "r"(selector), "r"(output) : "memory");
    bank += base;
    __asm__ volatile("" : "+r"(bank) : "r"(base), "r"(selector), "r"(output) : "memory");
    register uint32_t value __asm__("a4") = *(volatile uint32_t *)(bank + 432u);
    value &= 4u;
    *(volatile uint8_t *)(output + 8u) = (uint8_t)value;
    __asm__ volatile(".Lprovider_extended:\nc.bnez a4, .Lprovider_extended\n"
                     ".reloc .Lprovider_extended, R_RISCV_RVC_BRANCH, tsl9_irq_provider_extended_18e08\n"
                     : : "r"(value), "r"(bank), "r"(base), "r"(selector), "r"(output) : "memory");
    __builtin_unreachable();
}

TSL9_REGION void tsl9_irq_provider_standard_18d8a(void)
{
    register uintptr_t bank __asm__("a5");
    register uintptr_t output __asm__("a2");
    __asm__ volatile("" : "=r"(bank), "=r"(output) : : "memory");
    register uint32_t value __asm__("a4") = *(volatile uint32_t *)(bank + 432u);
    value >>= 21;
    *(volatile uint32_t *)output = value;
    __asm__ volatile("" : : "r"(bank), "r"(output), "r"(value) : "memory");
    __builtin_unreachable();
}

TSL9_REGION void tsl9_irq_provider_common_18d92(void)
{
    register uintptr_t base __asm__("a0");
    register uint32_t selector __asm__("a1");
    register uintptr_t output __asm__("a2");
    register uintptr_t bank __asm__("a5");
    __asm__ volatile("" : "=r"(base), "=r"(selector), "=r"(output), "=r"(bank) : : "memory");
    register uint32_t value __asm__("a4") = *(volatile uint32_t *)(bank + 432u);
    value &= 2u;
    *(volatile uint8_t *)(output + 9u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 436u);
    value &= 15u;
    *(volatile uint8_t *)(output + 10u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 436u);
    value >>= 8;
    *(volatile uint8_t *)(output + 19u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 440u);
    *(volatile uint8_t *)(output + 11u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 440u);
    value >>= 8;
    *(volatile uint8_t *)(output + 12u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 440u);
    value >>= 16;
    *(volatile uint8_t *)(output + 13u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 440u);
    value >>= 24;
    *(volatile uint8_t *)(output + 14u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 444u);
    *(volatile uint8_t *)(output + 15u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 444u);
    value >>= 8;
    *(volatile uint8_t *)(output + 16u) = (uint8_t)value;
    value = *(volatile uint32_t *)(bank + 444u);
    value >>= 16;
    *(volatile uint8_t *)(output + 17u) = (uint8_t)value;
    /* The final read consumes the old bank address and overwrites A5,
     * while A4 retains the previous shifted word until the branch. */
    __asm__ volatile("" : "+r"(value), "+r"(bank) : "r"(base), "r"(selector), "r"(output) : "memory");
    bank = *(volatile uint32_t *)(bank + 444u);
    bank >>= 24;
    *(volatile uint8_t *)(output + 18u) = (uint8_t)bank;
    __asm__ volatile(".Lprovider_bank1:\nc.bnez a1, .Lprovider_bank1\n"
                     ".reloc .Lprovider_bank1, R_RISCV_RVC_BRANCH, tsl9_irq_provider_bank1_18e12\n"
                     : : "r"(base), "r"(selector), "r"(output), "r"(value), "r"(bank) : "memory");
    __builtin_unreachable();
}

TSL9_REGION void tsl9_irq_provider_bank0_18dfe(void)
{
    register uintptr_t base __asm__("a0");
    __asm__ volatile("" : "=r"(base) : : "memory");
    register uint32_t value __asm__("a5") = *(volatile uint32_t *)(base + 12u);
    __asm__ volatile("" : "+r"(value) : "r"(base) : "memory");
    value |= 32u;
    *(volatile uint32_t *)(base + 12u) = value;
    __asm__ volatile("ret\n" : : "r"(base), "r"(value) : "memory");
    __builtin_unreachable();
}

TSL9_REGION void tsl9_irq_provider_extended_18e08(void)
{
    register uintptr_t bank __asm__("a5");
    register uintptr_t output __asm__("a2");
    __asm__ volatile("" : "=r"(bank), "=r"(output) : : "memory");
    register uint32_t value __asm__("a4") = *(volatile uint32_t *)(bank + 432u);
    value >>= 3;
    *(volatile uint32_t *)(output + 4u) = value;
    __asm__ volatile(".Lprovider_common:\nc.j .Lprovider_common\n"
                     ".reloc .Lprovider_common, R_RISCV_RVC_JUMP, tsl9_irq_provider_common_18d92\n"
                     : : "r"(bank), "r"(output), "r"(value) : "memory");
    __builtin_unreachable();
}

TSL9_REGION void tsl9_irq_provider_bank1_18e12(void)
{
    register uintptr_t base __asm__("a0");
    __asm__ volatile("" : "=r"(base) : : "memory");
    register uint32_t value __asm__("a5") = *(volatile uint32_t *)(base + 16u);
    __asm__ volatile("" : "+r"(value) : "r"(base) : "memory");
    value |= 32u;
    *(volatile uint32_t *)(base + 16u) = value;
    __asm__ volatile("ret\n" : : "r"(base), "r"(value) : "memory");
    __builtin_unreachable();
}
