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

/* Original17666..1787C only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Physical16B/32B/48B frames,shared event exits andprivate callback ports remain.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 17666..1767E */
REGION void tsl9_event_consumer_entry_17666(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 88u); LIVE;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("mv s0, a0");
    a2 = UINT32_C(2); LIVE;
    a1 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nlbu a0, 379(gp)\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 1767E..17680 */
REGION void tsl9_event_consumer_block_1767e(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_1767e:\nc.bnez s0,.Lrecord_control_edge_1767e\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17698\n");
    __builtin_unreachable();
}

/* Original 17680..17686 */
REGION void tsl9_event_consumer_block_17680(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 378(gp)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_17684:\nc.bnez a5,.Lrecord_control_edge_17684\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17698\n");
    __builtin_unreachable();
}

/* Original 17686..17692 */
REGION void tsl9_event_consumer_block_17686(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x0\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi a0, a0, 26\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_1768e:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_1768e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_90b0\n");
    __builtin_unreachable();
}

/* Original 17692..17698 */
REGION void tsl9_event_consumer_block_17692(void)
{
    REGS;
    a5 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 378(gp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original 17698..176A0 */
REGION void tsl9_event_consumer_block_17698(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 176A0..176C8 */
REGION void tsl9_event_consumer_entry_176a0(void)
{
    REGS;
    a5 = UINT32_C(0x6000); LIVE;
    CALL_PORT("addi sp, sp, -32");
    a5 = a5 + 0x2b5u; LIVE;
    a0 = UINT32_C(0xb000); LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 12(sp)\n.option pop\n");
    a4 = UINT32_C(2); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x0\n.option pop\n");
    a5 = a5 + 0xffffffb6u; LIVE;
    CALL_PORT("addi a3, sp, 12");
    a2 = UINT32_C(15); LIVE;
    a1 = UINT32_C(21); LIVE;
    a0 = a0 + 0x562u; LIVE;
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT(".Lrecord_control_edge_176c4:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_176c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_event_consumer_provider_1753a\n");
    __builtin_unreachable();
}

/* Original 176C8..176CA */
REGION void tsl9_event_consumer_block_176c8(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_176c8:\nc.bnez a0,.Lrecord_control_edge_176c8\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_176f2\n");
    __builtin_unreachable();
}

/* Original 176CA..176DE */
REGION void tsl9_event_consumer_block_176ca(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 377(gp)\n.option pop\n");
    a5 = a5 + 0x1u; LIVE;
    a5 = a5 & 0xffu; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 377(gp)\n.option pop\n");
    a4 = UINT32_C(4); LIVE;
    CALL_PORT(".Lrecord_control_edge_176da:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_control_edge_176da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_event_consumer_block_176f2\n");
    __builtin_unreachable();
}

/* Original 176DE..176F2 */
REGION void tsl9_event_consumer_block_176de(void)
{
    REGS;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(500); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x0\n.option pop\n");
    a0 = a0 + 0xffffffbau; LIVE;
    CALL_PORT(".Lrecord_control_edge_176ee:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_176ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original 176F2..176F8 */
REGION void tsl9_event_consumer_block_176f2(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 176F8..1770C */
REGION void tsl9_event_consumer_entry_176f8(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -48");
    CALL_PORT("sw s0, 40(sp)");
    CALL_PORT("sw ra, 44(sp)");
    CALL_PORT("sw s1, 36(sp)");
    CALL_PORT("sw s2, 32(sp)");
    CALL_PORT("sw s3, 28(sp)");
    a5 = a1 & 0x1u; LIVE;
    CALL_PORT("mv s0, a1");
    CALL_PORT(".Lrecord_control_edge_1770a:\nc.beqz a5,.Lrecord_control_edge_1770a\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17776\n");
    __builtin_unreachable();
}

/* Original 1770C..1771E */
REGION void tsl9_event_consumer_block_1770c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 418u); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc s1, 0x1fff5\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi s1, s1, 408\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_1771c:\nc.beqz a5,.Lrecord_control_edge_1771c\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17764\n");
    __builtin_unreachable();
}

/* Original 1771E..17744 */
REGION void tsl9_event_consumer_block_1771e(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 0(s1)\n.option pop\n");
    a3 = UINT32_C(7); LIVE;
    a0 = UINT32_C(0xb000); LIVE;
    a3 = a3 * a5; LIVE;
    a4 = UINT32_C(7); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x0\n.option pop\n");
    a5 = a5 + 0xffffff3au; LIVE;
    a2 = UINT32_C(0); LIVE;
    a1 = UINT32_C(21); LIVE;
    a0 = a0 + 0x562u; LIVE;
    a3 = a3 + 0x3u; LIVE;
    CALL_PORT("add a3, a3, s1");
    CALL_PORT(".Lrecord_control_edge_17740:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_17740\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_event_consumer_provider_1753a\n");
    __builtin_unreachable();
}

/* Original 17744..17746 */
REGION void tsl9_event_consumer_block_17744(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_17744:\nc.bnez a0,.Lrecord_control_edge_17744\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17764\n");
    __builtin_unreachable();
}

/* Original 17746..17764 */
REGION void tsl9_event_consumer_block_17746(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 0(s1)\n.option pop\n");
    a5 = a5 + 0x1u; LIVE;
    a5 = a5 & 0xfu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + 350u) = (uint8_t)a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 2(s1)\n.option pop\n");
    a5 = a5 + 0xffffffffu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + 338u) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original 17764..17768 */
REGION void tsl9_event_consumer_block_17764(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original 17768..17776 */
REGION void tsl9_event_consumer_block_17768(void)
{
    REGS;
    CALL_PORT("lw ra, 44(sp)");
    CALL_PORT("lw s0, 40(sp)");
    CALL_PORT("lw s1, 36(sp)");
    CALL_PORT("lw s2, 32(sp)");
    CALL_PORT("lw s3, 28(sp)");
    CALL_PORT("addi sp, sp, 48");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 17776..17780 */
REGION void tsl9_event_consumer_block_17776(void)
{
    REGS;
    a5 = a1 & 0x2u; LIVE;
    CALL_PORT("mv s1, a0");
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lrecord_control_edge_1777e:\nc.beqz a5,.Lrecord_control_edge_1777e\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17768\n");
    __builtin_unreachable();
}

/* Original 17780..177A2 */
REGION void tsl9_event_consumer_block_17780(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 376(gp)\n.option pop\n");
    a1 = UINT32_C(7); LIVE;
    a5 = a5 * a1; LIVE;
    CALL_PORT(".option push\n.option norvc\naddi s2, gp, 104\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a1, 0(s2)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a4, 76(s3)\n.option pop\n");
    a2 = UINT32_C(7); LIVE;
    CALL_PORT("addi a0, sp, 8");
    a1 = a1 + a5; LIVE;
    CALL_PORT("c.jalr a4");
    __builtin_unreachable();
}

/* Original 177A2..177A8 */
REGION void tsl9_event_consumer_block_177a2(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 376(gp)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_177a6:\nc.beqz a5,.Lrecord_control_edge_177a6\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_177c4\n");
    __builtin_unreachable();
}

/* Original 177A8..177B2 */
REGION void tsl9_event_consumer_block_177a8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 9(sp)\n.option pop\n");
    a5 = a5 & 0xfcu; LIVE;
    CALL_PORT(".Lrecord_control_edge_177b0:\nc.bnez a5,.Lrecord_control_edge_177b0\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_177c4\n");
    __builtin_unreachable();
}

/* Original 177B2..177C4 */
REGION void tsl9_event_consumer_block_177b2(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb zero, 376(gp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a5, 76(s3)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a1, 0(s2)\n.option pop\n");
    a2 = UINT32_C(7); LIVE;
    CALL_PORT("addi a0, sp, 8");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 177C4..177CC */
REGION void tsl9_event_consumer_block_177c4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 9(sp)\n.option pop\n");
    a5 = a5 & 0x2u; LIVE;
    CALL_PORT(".Lrecord_control_edge_177ca:\nc.beqz a5,.Lrecord_control_edge_177ca\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_177e2\n");
    __builtin_unreachable();
}

/* Original 177CC..177DC */
REGION void tsl9_event_consumer_block_177cc(void)
{
    REGS;
    CALL_PORT("lw a4, 8(sp)");
    a3 = UINT32_C(1); LIVE;
    a5 = a4 >> 10u; LIVE;
    a5 = a5 & 0x3fu; LIVE;
    CALL_PORT(".Lrecord_control_edge_177d8:\n.option push\n.option norvc\nbeq a5,a3,.Lrecord_control_edge_177d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_event_consumer_block_177ee\n");
    __builtin_unreachable();
}

/* Original 177DC..177E2 */
REGION void tsl9_event_consumer_block_177dc(void)
{
    REGS;
    a3 = UINT32_C(2); LIVE;
    CALL_PORT(".Lrecord_control_edge_177de:\n.option push\n.option norvc\nbeq a5,a3,.Lrecord_control_edge_177de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_event_consumer_block_17832\n");
    __builtin_unreachable();
}

/* Original 177E2..177E8 */
REGION void tsl9_event_consumer_block_177e2(void)
{
    REGS;
    CALL_PORT("addi a0, sp, 8");
    CALL_PORT(".Lrecord_control_edge_177e4:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_177e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_event_consumer_provider_c776\n");
    __builtin_unreachable();
}

/* Original 177E8..177EE */
REGION void tsl9_event_consumer_block_177e8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_177ec:\nc.j .Lrecord_control_edge_177ec\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_event_consumer_block_17768\n");
    __builtin_unreachable();
}

/* Original 177EE..177F8 */
REGION void tsl9_event_consumer_block_177ee(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 14(sp)\n.option pop\n");
    a5 = a5 & 0x7cu; LIVE;
    CALL_PORT(".Lrecord_control_edge_177f6:\nc.beqz a5,.Lrecord_control_edge_177f6\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_177e2\n");
    __builtin_unreachable();
}

/* Original 177F8..17806 */
REGION void tsl9_event_consumer_block_177f8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 369(gp)\n.option pop\n");
    a5 = a5 ^ 0x1u; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 369(gp)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_17804:\nc.beqz a5,.Lrecord_control_edge_17804\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_event_consumer_block_17816\n");
    __builtin_unreachable();
}

/* Original 17806..17816 */
REGION void tsl9_event_consumer_block_17806(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlhu a5, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x2000); LIVE;
    a4 = a4 + 0xffffff00u; LIVE;
    a5 = a5 | a4; LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 12(sp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original 17816..17826 */
REGION void tsl9_event_consumer_block_17816(void)
{
    REGS;
    CALL_PORT("lw a5, 12(sp)");
    a4 = UINT32_C(0x40000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + 88u); LIVE;
    a5 = a5 >> 18u; LIVE;
    a5 = a5 & 0x1fu; LIVE;
    a2 = UINT32_C(160); LIVE;
    __builtin_unreachable();
}

/* Original 17826..17830 */
REGION void tsl9_event_consumer_block_17826(void)
{
    REGS;
    a2 = a5 * a2; LIVE;
    a1 = UINT32_C(2); LIVE;
    CALL_PORT("mv a0, s1");
    CALL_PORT("c.jalr a4");
    __builtin_unreachable();
}

/* Original 17830..17832 */
REGION void tsl9_event_consumer_block_17830(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_17830:\nc.j .Lrecord_control_edge_17830\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_event_consumer_block_177e2\n");
    __builtin_unreachable();
}

/* Original 17832..1787C */
REGION void tsl9_event_consumer_block_17832(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 370(gp)\n.option pop\n");
    a2 = a5 << 2u; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x3\n.option pop\n");
    a3 = a3 + 0x2aeu; LIVE;
    a3 = a3 + a2; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + 0u); LIVE;
    a2 = UINT32_C(0x10000); LIVE;
    a2 = a2 + 0xffffffffu; LIVE;
    a1 = a3 & a2; LIVE;
    a4 = a4 & a2; LIVE;
    a1 = a1 << 16u; LIVE;
    a4 = a4 | a1; LIVE;
    CALL_PORT("sw a4, 8(sp)");
    a5 = a5 + 0x1u; LIVE;
    a4 = UINT32_C(7); LIVE;
    CALL_PORT(".option push\n.option norvc\nrem a5, a5, a4\n.option pop\n");
    a3 = a3 >> 16u; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a3, 12(sp)\n.option pop\n");
    a2 = UINT32_C(800); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 370(gp)\n.option pop\n");
    CALL_PORT("lw a5, 12(sp)");
    a4 = UINT32_C(0x40000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + 88u); LIVE;
    a5 = a5 >> 18u; LIVE;
    a5 = a5 & 0x1fu; LIVE;
    a5 = a5 + 0x1u; LIVE;
    CALL_PORT(".Lrecord_control_edge_1787a:\nc.j .Lrecord_control_edge_1787a\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_event_consumer_block_17826\n");
    __builtin_unreachable();
}
