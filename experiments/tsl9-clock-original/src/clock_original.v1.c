#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; not a host clock model.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Complete18834..188E2 query and1973C..19764 field-update scopes:214B/69i.
 * C arithmetic/volatile access plus explicit GP and local-control ports.
 * Preserve fresh peripheral reads,GP+64 byte lookup,and GP+108 readback/stores.
 * A2 is written only in the external-source branch; no entry snapshot/restore.
 * Fields preserve unsigned DIVU,8-bit quotient and GP+382/GP+380 store widths.
 * These16 regions require original adjacency and are not normal C ABI functions.
 * No physical clock,MCU,resident,GP/table ownership,IRQ or OTA proof. */

/* Original 18834..18842 */
REGION void tsl9_main_provider_18834(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a3 = UINT32_C(4); LIVE;
    a5 = a5 & 0xcu; LIVE;
    PORT(".Lclock_original_edge_1883e:\n.option push\n.option norvc\nbeq a5,a3,.Lclock_original_edge_1883e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_clock_original_block_18878\n");
    __builtin_unreachable();
}

/* Original 18842..18848 */
REGION void tsl9_clock_original_block_18842(void)
{
    REGS;
    a3 = UINT32_C(8); LIVE;
    PORT(".Lclock_original_edge_18844:\n.option push\n.option norvc\nbeq a5,a3,.Lclock_original_edge_18844\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_clock_original_block_18882\n");
    __builtin_unreachable();
}

/* Original 18848..18850 */
REGION void tsl9_clock_original_block_18848(void)
{
    REGS;
    a5 = UINT32_C(0x7a1000); LIVE;
    a5 = a5 + 0x200u; LIVE;
    __builtin_unreachable();
}

/* Original 18850..18878 */
REGION void tsl9_clock_original_block_18850(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 108(gp)\n.option pop\n");
    a5 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 4u); LIVE;
    PORT(".option push\n.option norvc\naddi a4, gp, 64\n.option pop\n");
    a5 = a5 >> 4u; LIVE;
    a5 = a5 & 0xfu; LIVE;
    a5 = a5 + a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 0u); LIVE;
    PORT(".option push\n.option norvc\naddi a5, gp, 108\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a5 = a5 >> (a4 & 31u); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 108(gp)\n.option pop\n");
    PORT("ret");
    __builtin_unreachable();
}

/* Original 18878..18882 */
REGION void tsl9_clock_original_block_18878(void)
{
    REGS;
    a5 = UINT32_C(0x1e85000); LIVE;
    a5 = a5 + 0xfffff800u; LIVE;
    PORT(".Lclock_original_edge_18880:\n.option push\n.option rvc\nc.j .Lclock_original_edge_18880\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_clock_original_block_18850\n");
    __builtin_unreachable();
}

/* Original 18882..18896 */
REGION void tsl9_clock_original_block_18882(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a3 = UINT32_C(0x10000); LIVE;
    a5 = a5 >> 18u; LIVE;
    a5 = a5 & 0xfu; LIVE;
    a4 = a4 & a3; LIVE;
    a5 = a5 + 0x2u; LIVE;
    a3 = UINT32_C(17); LIVE;
    PORT(".Lclock_original_edge_18892:\n.option push\n.option norvc\nbne a5,a3,.Lclock_original_edge_18892\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_clock_original_block_18898\n");
    __builtin_unreachable();
}

/* Original 18896..18898 */
REGION void tsl9_clock_original_block_18896(void)
{
    REGS;
    a5 = UINT32_C(18); LIVE;
    __builtin_unreachable();
}

/* Original 18898..1889A */
REGION void tsl9_clock_original_block_18898(void)
{
    REGS;
    PORT(".Lclock_original_edge_18898:\n.option push\n.option rvc\nc.bnez a4,.Lclock_original_edge_18898\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_clock_original_block_188b0\n");
    __builtin_unreachable();
}

/* Original 1889A..188A6 */
REGION void tsl9_clock_original_block_1889a(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 - 2048u); LIVE;
    a4 = a4 & 0x10u; LIVE;
    PORT(".Lclock_original_edge_188a4:\n.option push\n.option rvc\nc.beqz a4,.Lclock_original_edge_188a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_clock_original_block_188d8\n");
    __builtin_unreachable();
}

/* Original 188A6..188B0 */
REGION void tsl9_clock_original_block_188a6(void)
{
    REGS;
    a4 = UINT32_C(0x7a1000); LIVE;
    a4 = a4 + 0x200u; LIVE;
    PORT(".Lclock_original_edge_188ae:\n.option push\n.option rvc\nc.j .Lclock_original_edge_188ae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_clock_original_block_188c8\n");
    __builtin_unreachable();
}

/* Original 188B0..188C0 */
REGION void tsl9_clock_original_block_188b0(void)
{
    REGS;
    a3 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + 4u); LIVE;
    a2 = UINT32_C(0xc00000); LIVE;
    a4 = a4 & a2; LIVE;
    PORT(".Lclock_original_edge_188bc:\n.option push\n.option norvc\nbne a4,a2,.Lclock_original_edge_188bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_clock_original_block_188ce\n");
    __builtin_unreachable();
}

/* Original 188C0..188C8 */
REGION void tsl9_clock_original_block_188c0(void)
{
    REGS;
    a4 = UINT32_C(0xf42000); LIVE;
    a4 = a4 + 0x400u; LIVE;
    __builtin_unreachable();
}

/* Original 188C8..188CE */
REGION void tsl9_clock_original_block_188c8(void)
{
    REGS;
    a5 = a5 * a4; LIVE;
    PORT(".Lclock_original_edge_188cc:\n.option push\n.option rvc\nc.j .Lclock_original_edge_188cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_clock_original_block_18850\n");
    __builtin_unreachable();
}

/* Original 188CE..188D8 */
REGION void tsl9_clock_original_block_188ce(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + 4u); LIVE;
    a3 = a4 << 14u; LIVE;
    PORT(".Lclock_original_edge_188d4:\n.option push\n.option norvc\nbgez a3,.Lclock_original_edge_188d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_clock_original_block_188a6\n");
    __builtin_unreachable();
}

/* Original 188D8..188E2 */
REGION void tsl9_clock_original_block_188d8(void)
{
    REGS;
    a4 = UINT32_C(0x3d1000); LIVE;
    a4 = a4 + 0xfffff900u; LIVE;
    PORT(".Lclock_original_edge_188e0:\n.option push\n.option rvc\nc.j .Lclock_original_edge_188e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_clock_original_block_188c8\n");
    __builtin_unreachable();
}

/* Original 1973C..19764 */
REGION void tsl9_main_provider_1973c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, gp, 108\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a4 = UINT32_C(0x7a1000); LIVE;
    a4 = a4 + 0x200u; LIVE;
    a5 = a5 / a4; LIVE;
    a5 = a5 & 0xffu; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 382(gp)\n.option pop\n");
    a4 = UINT32_C(1000); LIVE;
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 380(gp)\n.option pop\n");
    PORT("ret");
    __builtin_unreachable();
}
