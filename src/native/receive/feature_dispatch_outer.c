#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Private RV32 architectural regions only; never execute as a host model.
#endif

/* Original [14D2E,14D5E), [153BA,154A6), plus the whole 829E getter.
 * C owns free-bank memory, constants, unsigned shifts and additions.
 * Physical SP/S0/RA, fresh S0-relative loads, explicit control and PC-relative
 * bases are architectural ports. Fresh S0 cannot be treated as a saved C local:
 * the reserved-SP compiler profile rejects a C output tied to S0 (trial-v1).
 * Regions fall through at their exact original boundaries, not C ABI calls.
 * The separate mode1/common-return tree and all final tail providers stay open.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((naked,used,aligned(2)))
#define PORT(x) __asm__ volatile("" : "+r"(x) : : "memory")
#define TAIL(name,target) \
    FRAME void name(void) { \
        __asm__ volatile("mv a0, s0\nlw s0, 8(sp)\nlw ra, 12(sp)\n" \
                         "addi sp, sp, 16\nj " #target "\n"); \
    }

FRAME void tsl9_queue_external_14d2e(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw s0, 8(sp)\nsw ra, 12(sp)\n"
                     "mv s0, a0\njal ra, tsl9_feature_mode_getter_829e\n");
}

REGION void tsl9_feature_outer_14d3a(void)
{
    register uint32_t a0 __asm__("a0");
    __asm__ volatile("" : "=r"(a0) : : "memory");
    register uint32_t a5 __asm__("a5")=6; PORT(a5);
    __asm__ volatile(".Louter_default%=:\nbltu a5, a0, .Louter_default%=\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_feature_outer_1549a\n"
                     : : "r"(a0),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_outer_14d40(void)
{
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile(".Louter_table_base%=:\n"
                     "auipc a4, %%pcrel_hi(tsl9_feature_mode_table_1a6b8)\n"
                     "addi a4, a4, %%pcrel_lo(.Louter_table_base%=)\n"
                     : "=r"(a4) : : "memory");
    register uintptr_t a0 __asm__("a0");
    __asm__ volatile("" : "=r"(a0) : "r"(a4) : "memory");
    a0<<=2; PORT(a0);
    a0+=a4; PORT(a0);
    register uintptr_t a5 __asm__("a5")=*(volatile uint32_t *)a0;
    PORT(a5);
    a5+=a4; PORT(a5);
    __asm__ volatile("jr a5\n" : : "r"(a5),"r"(a4),"r"(a0) : "memory");
    __builtin_unreachable();
}

TAIL(tsl9_feature_outer_14d52,tsl9_feature_external_10b60)

#define FRESH_ID() \
    register uint32_t a5 __asm__("a5"); \
    __asm__ volatile("lhu a5, 0(s0)\n" : "=r"(a5) : : "memory"); \
    register uint32_t a4 __asm__("a4")
#define EQ(value,target) \
    a4=(value); PORT(a4); \
    __asm__ volatile(".Louter_equal%=:\nbeq a5, a4, .Louter_equal%=\n" \
                     ".reloc .-4, R_RISCV_BRANCH, " #target "\n" \
                     : : "r"(a5),"r"(a4) : "memory")
#define NE(value,target) \
    a4=(value); PORT(a4); \
    __asm__ volatile(".Louter_other%=:\nbne a5, a4, .Louter_other%=\n" \
                     ".reloc .-4, R_RISCV_BRANCH, " #target "\n" \
                     : : "r"(a5),"r"(a4) : "memory")

REGION void tsl9_feature_outer_153ba(void)
{
    FRESH_ID(); EQ(169,tsl9_feature_outer_15416);
    NE(540,tsl9_feature_return_14da2); __builtin_unreachable();
}
TAIL(tsl9_feature_outer_153ce,tsl9_feature_external_108d8)

REGION void tsl9_feature_outer_153da(void)
{
    FRESH_ID(); EQ(169,tsl9_feature_outer_15416);
    NE(540,tsl9_feature_return_14da2); __builtin_unreachable();
}
TAIL(tsl9_feature_outer_153ee,tsl9_feature_external_10944)

REGION void tsl9_feature_outer_153fa(void)
{
    FRESH_ID(); EQ(393,tsl9_feature_outer_15422);
    EQ(1676,tsl9_feature_outer_1542e);
    NE(169,tsl9_feature_return_14da2); __builtin_unreachable();
}
TAIL(tsl9_feature_outer_15416,tsl9_feature_external_10870)
TAIL(tsl9_feature_outer_15422,tsl9_feature_external_109c4)
TAIL(tsl9_feature_outer_1542e,tsl9_feature_external_10a00)

REGION void tsl9_feature_outer_1543a(void)
{
    FRESH_ID(); EQ(929,tsl9_feature_outer_15462);
    EQ(1002,tsl9_feature_outer_1546e);
    NE(890,tsl9_feature_return_14da2); __builtin_unreachable();
}
TAIL(tsl9_feature_outer_15456,tsl9_feature_external_10ac6)
TAIL(tsl9_feature_outer_15462,tsl9_feature_external_10a16)
TAIL(tsl9_feature_outer_1546e,tsl9_feature_external_10b0a)

REGION void tsl9_feature_outer_1547a(void)
{
    FRESH_ID(); EQ(169,tsl9_feature_outer_15416);
    NE(1176,tsl9_feature_return_14da2); __builtin_unreachable();
}
TAIL(tsl9_feature_outer_1548e,tsl9_feature_external_10936)

FRAME void tsl9_feature_outer_1549a(void)
{
    __asm__ volatile("lw s0, 8(sp)\nlw ra, 12(sp)\n");
}
REGION void tsl9_feature_outer_1549e(void)
{
    register uint32_t a0 __asm__("a0")=0; PORT(a0);
    __asm__ volatile("addi sp, sp, 16\nj tsl9_feature_external_1074c\n"
                     : : "r"(a0) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_mode_getter_829e(void)
{
    register uintptr_t a0 __asm__("a0");
    __asm__ volatile("auipc a0, 0x20004\n" : "=r"(a0) : : "memory");
    a0=*(volatile uint8_t *)(a0-745u); PORT(a0);
    __asm__ volatile("ret\n" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

/* Data only: true ELF ADD32/SUB32 relocations; never ABS target providers. */
__asm__(".pushsection .rodata.tsl9_feature_mode_table_1a6b8,\"a\",@progbits\n"
        ".balign 4\n.globl tsl9_feature_mode_table_1a6b8\n"
        ".type tsl9_feature_mode_table_1a6b8,@object\n"
        "tsl9_feature_mode_table_1a6b8:\n"
        ".word tsl9_feature_outer_14d52-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_mode1_14d5e-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_outer_153ba-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_outer_153da-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_outer_153fa-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_outer_1543a-tsl9_feature_mode_table_1a6b8\n"
        ".word tsl9_feature_outer_1547a-tsl9_feature_mode_table_1a6b8\n"
        ".size tsl9_feature_mode_table_1a6b8,.-tsl9_feature_mode_table_1a6b8\n"
        ".popsection\n");
