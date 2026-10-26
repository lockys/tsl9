#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; no host ROM or radio model.
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

/* One complete public-SDK RAM-JT0 scheduler:438B/150i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x200007D0..0x200007F8. */
REGION void tsl9_candidate_TMOS_SystemProcess_200007d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 564\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 564\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s2, 456\n.option pop\n");
    PORT(".Lresident_scheduler_edge_200007f6:\n.option push\n.option rvc\nc.bnez a5,.Lresident_scheduler_edge_200007f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000081a\n");
    __builtin_unreachable();
}

/* Original0x200007F8..0x20000806. */
REGION void tsl9_resident_scheduler_block_200007f8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33d8\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_scheduler_edge_20000804:\n.option push\n.option rvc\nc.beqz a4,.Lresident_scheduler_edge_20000804\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000081a\n");
    __builtin_unreachable();
}

/* Original0x20000806..0x2000080E. */
REGION void tsl9_resident_scheduler_block_20000806(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_scheduler_edge_2000080a:\n.option push\n.option norvc\nbne a3,a4,.Lresident_scheduler_edge_2000080a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_200008c0\n");
    __builtin_unreachable();
}

/* Original0x2000080E..0x20000816. */
REGION void tsl9_resident_scheduler_block_2000080e(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    PORT(".Lresident_scheduler_edge_20000812:\n.option push\n.option norvc\njal ra,.Lresident_scheduler_edge_20000812\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20002610\n");
    __builtin_unreachable();
}

/* Original0x20000816..0x20000818. */
REGION void tsl9_resident_scheduler_block_20000816(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 12(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000818..0x2000081A. */
REGION void tsl9_resident_scheduler_block_20000818(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000081A..0x2000081E. */
REGION void tsl9_resident_scheduler_block_2000081a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_2000081c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_edge_2000081c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_20000820\n");
    __builtin_unreachable();
}

/* Original0x2000081E..0x20000820. */
REGION void tsl9_resident_scheduler_block_2000081e(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000820..0x20000836. */
REGION void tsl9_resident_scheduler_block_20000820(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 412\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 484(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3390\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s0, 412\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000836..0x20000844. */
REGION void tsl9_resident_scheduler_block_20000836(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 412(s0)\n.option pop\n");
    a3 = a5 << UINT32_C(0x00000001); LIVE;
    a3 = a3 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 0(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x2296\n.option pop\n");
    PORT(".Lresident_scheduler_edge_20000842:\n.option push\n.option rvc\nc.beqz a3,.Lresident_scheduler_edge_20000842\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_200008d4\n");
    __builtin_unreachable();
}

/* Original0x20000844..0x2000084C. */
REGION void tsl9_resident_scheduler_block_20000844(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 412(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_20000848:\n.option push\n.option norvc\nbltu a5,a2,.Lresident_scheduler_edge_20000848\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_200008e4\n");
    __builtin_unreachable();
}

/* Original0x2000084C..0x20000862. */
REGION void tsl9_resident_scheduler_block_2000084c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 412(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x379c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".Lresident_scheduler_edge_2000085e:\n.option push\n.option norvc\nbnez a5,.Lresident_scheduler_edge_2000085e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_20000960\n");
    __builtin_unreachable();
}

/* Original0x20000862..0x2000086C. */
REGION void tsl9_resident_scheduler_block_20000862(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".Lresident_scheduler_edge_2000086a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_edge_2000086a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x2000086C..0x20000874. */
REGION void tsl9_resident_scheduler_block_2000086c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 16(s4)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_20000872:\n.option push\n.option rvc\nc.jal .Lresident_scheduler_edge_20000872\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_200004fa\n");
    __builtin_unreachable();
}

/* Original0x20000874..0x2000087E. */
REGION void tsl9_resident_scheduler_block_20000874(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000214)); LIVE;
    PORT(".Lresident_scheduler_edge_2000087c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_edge_2000087c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x2000087E..0x20000886. */
REGION void tsl9_resident_scheduler_block_2000087e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_scheduler_edge_20000882:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_scheduler_edge_20000882\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x20000886..0x20000894. */
REGION void tsl9_resident_scheduler_block_20000886(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_scheduler_edge_20000892:\n.option push\n.option rvc\nc.bnez a5,.Lresident_scheduler_edge_20000892\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x20000894..0x200008A2. */
REGION void tsl9_resident_scheduler_block_20000894(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_scheduler_edge_200008a0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_scheduler_edge_200008a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x200008A2..0x200008AA. */
REGION void tsl9_resident_scheduler_block_200008a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 1(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 484(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200008AA..0x200008AE. */
REGION void tsl9_resident_scheduler_block_200008aa(void)
{
    REGS;
    PORT(".Lresident_scheduler_edge_200008aa:\n.option push\n.option norvc\nblt a5,a3,.Lresident_scheduler_edge_200008aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_20000978\n");
    __builtin_unreachable();
}

/* Original0x200008AE..0x200008C0. */
REGION void tsl9_resident_scheduler_block_200008ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_scheduler_edge_200008be:\n.option push\n.option rvc\nc.j .Lresident_scheduler_edge_200008be\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_2000061a\n");
    __builtin_unreachable();
}

/* Original0x200008C0..0x200008C8. */
REGION void tsl9_resident_scheduler_block_200008c0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_scheduler_edge_200008c4:\n.option push\n.option norvc\nbne a3,a4,.Lresident_scheduler_edge_200008c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_2000081a\n");
    __builtin_unreachable();
}

/* Original0x200008C8..0x200008D0. */
REGION void tsl9_resident_scheduler_block_200008c8(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    PORT(".Lresident_scheduler_edge_200008cc:\n.option push\n.option norvc\njal ra,.Lresident_scheduler_edge_200008cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20002610\n");
    __builtin_unreachable();
}

/* Original0x200008D0..0x200008D4. */
REGION void tsl9_resident_scheduler_block_200008d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 16(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_200008d2:\n.option push\n.option rvc\nc.j .Lresident_scheduler_edge_200008d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_scheduler_block_20000818\n");
    __builtin_unreachable();
}

/* Original0x200008D4..0x200008E2. */
REGION void tsl9_resident_scheduler_block_200008d4(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 412(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_200008de:\n.option push\n.option norvc\nbltu a5,a2,.Lresident_scheduler_edge_200008de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_20000836\n");
    __builtin_unreachable();
}

/* Original0x200008E2..0x200008E4. */
REGION void tsl9_resident_scheduler_block_200008e2(void)
{
    REGS;
    PORT(".Lresident_scheduler_edge_200008e2:\n.option push\n.option rvc\nc.j .Lresident_scheduler_edge_200008e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_scheduler_block_20000844\n");
    __builtin_unreachable();
}

/* Original0x200008E4..0x2000090C. */
REGION void tsl9_resident_scheduler_block_200008e4(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a4 = a4 + a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a1, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x230e\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 412(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001c4)); LIVE;
    a4 = a0 << UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsh zero, 476(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000090C..0x20000930. */
REGION void tsl9_resident_scheduler_block_2000090c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 476(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 412(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a0 = a0 & a5; LIVE;
    a5 = a4 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlw a4, 484(s3)\n.option pop\n");
    a4 = a4 + a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x231e\n.option pop\n");
    a0 = a0 | a5; LIVE;
    /* Conditional Xwchc: qk.c.sh a0, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa30a\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 412(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_2000092e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_edge_2000092e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_20000936\n");
    __builtin_unreachable();
}

/* Original0x20000930..0x20000936. */
REGION void tsl9_resident_scheduler_block_20000930(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 412(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000936..0x2000093C. */
REGION void tsl9_resident_scheduler_block_20000936(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 456(s2)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_2000093a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_edge_2000093a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_20000942\n");
    __builtin_unreachable();
}

/* Original0x2000093C..0x2000093E. */
REGION void tsl9_resident_scheduler_block_2000093c(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000093E..0x20000942. */
REGION void tsl9_resident_scheduler_block_2000093e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 456(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000942..0x2000094E. */
REGION void tsl9_resident_scheduler_block_20000942(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 412(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1(s4)\n.option pop\n");
    PORT(".Lresident_scheduler_edge_2000094a:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_scheduler_edge_2000094a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_2000084c\n");
    __builtin_unreachable();
}

/* Original0x2000094E..0x20000960. */
REGION void tsl9_resident_scheduler_block_2000094e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000960..0x2000096A. */
REGION void tsl9_resident_scheduler_block_20000960(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_scheduler_edge_20000966:\n.option push\n.option norvc\nbnez a5,.Lresident_scheduler_edge_20000966\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_block_20000862\n");
    __builtin_unreachable();
}

/* Original0x2000096A..0x20000976. */
REGION void tsl9_resident_scheduler_block_2000096a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 9(s0)\n.option pop\n");
    PORT(".Lresident_scheduler_literal_2000096e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_63dd0\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_scheduler_literal_2000096e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000976..0x20000978. */
REGION void tsl9_resident_scheduler_block_20000976(void)
{
    REGS;
    PORT(".Lresident_scheduler_edge_20000976:\n.option push\n.option rvc\nc.j .Lresident_scheduler_edge_20000976\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_scheduler_block_20000862\n");
    __builtin_unreachable();
}

/* Original0x20000978..0x20000982. */
REGION void tsl9_resident_scheduler_block_20000978(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000001); LIVE;
    a4 = a4 + a2; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x231a\n.option pop\n");
    PORT(".Lresident_scheduler_edge_20000980:\n.option push\n.option rvc\nc.bnez a4,.Lresident_scheduler_edge_20000980\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_block_2000094e\n");
    __builtin_unreachable();
}

/* Original0x20000982..0x20000986. */
REGION void tsl9_resident_scheduler_block_20000982(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_scheduler_edge_20000984:\n.option push\n.option rvc\nc.j .Lresident_scheduler_edge_20000984\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_scheduler_block_200008aa\n");
    __builtin_unreachable();
}
