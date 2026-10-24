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

/* Original1798A..179FC only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Guard35 precedes the32B frame;both mode paths and shared restore are retained.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 1798A..17992 */
REGION void tsl9_record_control_entry_1798a(void)
{
    REGS;
    a5 = UINT32_C(35); LIVE;
    CALL_PORT(".Lrecord_control_edge_1798e:\n.option push\n.option norvc\nbltu a5,a1,.Lrecord_control_edge_1798e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_control_block_179fa\n");
    __builtin_unreachable();
}

/* Original 17992..17998 */
REGION void tsl9_record_control_block_17992(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT(".Lrecord_control_edge_17996:\nc.bnez a0,.Lrecord_control_edge_17996\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_control_block_179e4\n");
    __builtin_unreachable();
}

/* Original 17998..179B2 */
REGION void tsl9_record_control_block_17998(void)
{
    REGS;
    a5 = UINT32_C(7); LIVE;
    a1 = a1 * a5; LIVE;
    CALL_PORT("addi a5, gp, 100");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 76u); LIVE;
    a2 = UINT32_C(7); LIVE;
    CALL_PORT("addi a0, sp, 8");
    a1 = a1 + a4; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 179B2..179C0 */
REGION void tsl9_record_control_block_179b2(void)
{
    REGS;
    CALL_PORT("lw a5, 8(sp)");
    a5 = a5 >> 10u; LIVE;
    a5 = a5 & 0x3fu; LIVE;
    a4 = a5 & 0x1u; LIVE;
    CALL_PORT(".Lrecord_control_edge_179be:\nc.beqz a4,.Lrecord_control_edge_179be\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_control_block_179ca\n");
    __builtin_unreachable();
}

/* Original 179C0..179CA */
REGION void tsl9_record_control_block_179c0(void)
{
    REGS;
    CALL_PORT("lw a4, 12(sp)");
    a4 = a4 >> 23u; LIVE;
    a4 = a4 & 0x1u; LIVE;
    CALL_PORT("sb a4, 367(gp)");
    __builtin_unreachable();
}

/* Original 179CA..179CE */
REGION void tsl9_record_control_block_179ca(void)
{
    REGS;
    a5 = a5 & 0x2u; LIVE;
    CALL_PORT(".Lrecord_control_edge_179cc:\nc.beqz a5,.Lrecord_control_edge_179cc\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_control_block_179d8\n");
    __builtin_unreachable();
}

/* Original 179CE..179D8 */
REGION void tsl9_record_control_block_179ce(void)
{
    REGS;
    CALL_PORT("lw a5, 12(sp)");
    a5 = a5 >> 23u; LIVE;
    a5 = a5 & 0x1u; LIVE;
    CALL_PORT("sb a5, 368(gp)");
    __builtin_unreachable();
}

/* Original 179D8..179DE */
REGION void tsl9_record_control_block_179d8(void)
{
    REGS;
    CALL_PORT("addi a0, sp, 8");
    CALL_PORT(".Lrecord_control_edge_179da:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_179da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_control_provider_1787c\n");
    __builtin_unreachable();
}

/* Original 179DE..179E4 */
REGION void tsl9_record_control_block_179de(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 179E4..179F8 */
REGION void tsl9_record_control_block_179e4(void)
{
    REGS;
    CALL_PORT("sb a1, 376(gp)");
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 88u); LIVE;
    a2 = UINT32_C(2); LIVE;
    a1 = UINT32_C(2); LIVE;
    CALL_PORT("lbu a0, 379(gp)");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 179F8..179FA */
REGION void tsl9_record_control_block_179f8(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_179f8:\nc.j .Lrecord_control_edge_179f8\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_control_block_179de\n");
    __builtin_unreachable();
}

/* Original 179FA..179FC */
REGION void tsl9_record_control_block_179fa(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}
