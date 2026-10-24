#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; never execute this experiment.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define CALL_PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Original17B92..17BC4 and17BF6..17C4E only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * SP/S registers, calls, RA returns and no-link tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 17B92..17B98 */
REGION void tsl9_init_tail_entry_17b92(void)
{
    REGS;
    __asm__ volatile("lbu a5, 378(gp)":"=r"(a5)::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_17b96:\nc.bnez a5,.Ltimer_edge_17b96\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_init_tail_block_17bbe\n");
    __builtin_unreachable();
}

/* Original 17B98..17BB4 */
REGION void tsl9_init_tail_block_17b98(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(100); LIVE;
    a1 = UINT32_C(0); LIVE;
    __asm__ volatile("auipc a0, 0x0":"=r"(a0)::"memory"); LIVE;
    a0 = a0 + 0xfffffafeu; LIVE;
    __asm__ volatile("sw ra, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("sb zero, 377(gp)":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_17bb0:\n.option push\n.option norvc\njal ra,.Ltimer_edge_17bb0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original 17BB4..17BBE */
REGION void tsl9_init_tail_block_17bb4(void)
{
    REGS;
    __asm__ volatile("lw ra, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("lbu a0, 378(gp)":"=r"(a0)::"memory"); LIVE;
    __asm__ volatile("addi sp, sp, 16":::"memory"); LIVE;
    __asm__ volatile("ret":::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 17BBE..17BC4 */
REGION void tsl9_init_tail_block_17bbe(void)
{
    REGS;
    __asm__ volatile("lbu a0, 378(gp)":"=r"(a0)::"memory"); LIVE;
    __asm__ volatile("ret":::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 17BF6..17C0C */
REGION void tsl9_init_tail_entry_17bf6(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    __asm__ volatile("sw s0, 8(sp)":::"memory"); LIVE;
    __asm__ volatile("lui s0, 0x40":::"memory"); LIVE;
    __asm__ volatile("lw a5, 72(s0)":"=r"(a5)::"memory"); LIVE;
    __asm__ volatile("sw ra, 12(sp)":::"memory"); LIVE;
    a2 = UINT32_C(3); LIVE;
    a1 = UINT32_C(0); LIVE;
    __asm__ volatile("addi a0, gp, 376":"=r"(a0)::"memory"); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17C0C..17C1E */
REGION void tsl9_init_tail_block_17c0c(void)
{
    REGS;
    __asm__ volatile("lw a5, 72(s0)":"=r"(a5)::"memory"); LIVE;
    a2 = UINT32_C(115); LIVE;
    a1 = UINT32_C(0); LIVE;
    __asm__ volatile("auipc a0, 0x1fff5":"=r"(a0)::"memory"); LIVE;
    a0 = a0 + 0xfffffc98u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17C1E..17C2C */
REGION void tsl9_init_tail_block_17c1e(void)
{
    REGS;
    __asm__ volatile("lw a5, 128(s0)":"=r"(a5)::"memory"); LIVE;
    __asm__ volatile("auipc a0, 0x0":"=r"(a0)::"memory"); LIVE;
    a0 = a0 + 0xfffffad6u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17C2C..17C3C */
REGION void tsl9_init_tail_block_17c2c(void)
{
    REGS;
    __asm__ volatile("sb a0, 379(gp)"::"r"(a0):"memory"); LIVE;
    __asm__ volatile("auipc a0, 0x0":"=r"(a0)::"memory"); LIVE;
    a0 = a0 + 0xfffffcc8u; LIVE;
    CALL_PORT(".Ltimer_edge_17c38:\n.option push\n.option norvc\njal ra,.Ltimer_edge_17c38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_90b0\n");
    __builtin_unreachable();
}

/* Original 17C3C..17C44 */
REGION void tsl9_init_tail_block_17c3c(void)
{
    REGS;
    a1 = UINT32_C(0); LIVE;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Ltimer_edge_17c40:\n.option push\n.option norvc\njal ra,.Ltimer_edge_17c40\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_1798a\n");
    __builtin_unreachable();
}

/* Original 17C44..17C4E */
REGION void tsl9_init_tail_block_17c44(void)
{
    REGS;
    __asm__ volatile("lw s0, 8(sp)":::"memory"); LIVE;
    __asm__ volatile("lw ra, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("addi sp, sp, 16":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_17c4a:\n.option push\n.option norvc\njal zero,.Ltimer_edge_17c4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_init_tail_entry_17b92\n");
    __builtin_unreachable();
}
