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

/* Five complete conditional SDK task-handler/scheduler bodies:2254B/801i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43874..0x438A0. */
REGION void tsl9_candidate_external_flash_43874(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_4389e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_final_handlers_edge_4389e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_438fe\n");
    __builtin_unreachable();
}

/* Original0x438A0..0x438B6. */
REGION void tsl9_resident_task_final_handlers_block_438a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s9, 12\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nli s10, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nli s8, 48\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x438B6..0x438C4. */
REGION void tsl9_resident_task_final_handlers_block_438b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul s7, s0, s9\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 556(s6)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s7\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_final_handlers_edge_438c2:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_final_handlers_edge_438c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_43920\n");
    __builtin_unreachable();
}

/* Original0x438C4..0x438DC. */
REGION void tsl9_resident_task_final_handlers_block_438c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a1, s0, 15\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a1, s10, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a0, s0, 0x4\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_final_handlers_edge_438da:\n.option push\n.option rvc\nc.jal .Lresident_task_final_handlers_edge_438da\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x438DC..0x438DE. */
REGION void tsl9_resident_task_final_handlers_block_438dc(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_438dc:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_final_handlers_edge_438dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_43920\n");
    __builtin_unreachable();
}

/* Original0x438DE..0x438EE. */
REGION void tsl9_resident_task_final_handlers_block_438de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 556(s6)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s7\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 0(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s4, 4(a5)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_438ea:\n.option push\n.option norvc\nbeqz s2,.Lresident_task_final_handlers_edge_438ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_438f2\n");
    __builtin_unreachable();
}

/* Original0x438EE..0x438F2. */
REGION void tsl9_resident_task_final_handlers_block_438ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 0(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x438F2..0x438FE. */
REGION void tsl9_resident_task_final_handlers_block_438f2(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_final_handlers_edge_438fc:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_438fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_43904\n");
    __builtin_unreachable();
}

/* Original0x438FE..0x43904. */
REGION void tsl9_resident_task_final_handlers_block_438fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x43904..0x43920. */
REGION void tsl9_resident_task_final_handlers_block_43904(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43920..0x43926. */
REGION void tsl9_resident_task_final_handlers_block_43920(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_43922:\n.option push\n.option norvc\nbne s0,s8,.Lresident_task_final_handlers_edge_43922\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_438b6\n");
    __builtin_unreachable();
}

/* Original0x43926..0x43932. */
REGION void tsl9_resident_task_final_handlers_block_43926(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_final_handlers_edge_43930:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_43930\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_43904\n");
    __builtin_unreachable();
}

/* Original0x5F98E..0x5F9AA. */
REGION void tsl9_candidate_external_flash_5f98e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a2 = a0 + UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000078)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_5f9a2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_5f9a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F9AA..0x5F9AE. */
REGION void tsl9_resident_task_final_handlers_block_5f9aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5f9ac:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_final_handlers_edge_5f9ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5F9AE..0x5F9C4. */
REGION void tsl9_resident_task_final_handlers_block_5f9ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s1, 120(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    a5 = UINT32_C(0x00000080); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2094\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb454\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3098\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa478\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5f9c0:\n.option push\n.option norvc\nbne a3,a2,.Lresident_task_final_handlers_edge_5f9c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5F9C4..0x5F9DE. */
REGION void tsl9_resident_task_final_handlers_block_5f9c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20bc\n.option pop\n");
    a3 = a5 >> UINT32_C(0x00000006); LIVE;
    a2 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5f9dc:\n.option push\n.option rvc\nc.bnez a3,.Lresident_task_final_handlers_edge_5f9dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5F9DE..0x5F9E8. */
REGION void tsl9_resident_task_final_handlers_block_5f9de(void)
{
    REGS;
    a3 = a2 + UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5f9e4:\n.option push\n.option norvc\nble a4,a3,.Lresident_task_final_handlers_edge_5f9e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5F9E8..0x5F9FA. */
REGION void tsl9_resident_task_final_handlers_block_5f9e8(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 - a2; LIVE;
    PORT(".option push\n.option norvc\nsb a4, 46(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, s1, 4\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5f9f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5f9f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa2e\n");
    __builtin_unreachable();
}

/* Original0x5F9FA..0x5FA06. */
REGION void tsl9_resident_task_final_handlers_block_5f9fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 84(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fa02:\n.option push\n.option norvc\nbne a3,a4,.Lresident_task_final_handlers_edge_5fa02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fb30\n");
    __builtin_unreachable();
}

/* Original0x5FA06..0x5FA0C. */
REGION void tsl9_resident_task_final_handlers_block_5fa06(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa0a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_final_handlers_edge_5fa0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa1a\n");
    __builtin_unreachable();
}

/* Original0x5FA0C..0x5FA0E. */
REGION void tsl9_resident_task_final_handlers_block_5fa0c(void)
{
    REGS;
    a5 = UINT32_C(0x00000011); LIVE;
    __builtin_unreachable();
}

/* Original0x5FA0E..0x5FA1A. */
REGION void tsl9_resident_task_final_handlers_block_5fa0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FA1A..0x5FA20. */
REGION void tsl9_resident_task_final_handlers_block_5fa1a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 100(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a0 = a0 + UINT32_C(0x00000014); LIVE;
    __builtin_unreachable();
}

/* Original0x5FA20..0x5FA28. */
REGION void tsl9_resident_task_final_handlers_block_5fa20(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_literal_5fa20:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_5fa20\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FA28..0x5FA2E. */
REGION void tsl9_resident_task_final_handlers_block_5fa28(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a1, s1, 10\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fa2c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_final_handlers_edge_5fa2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0c\n");
    __builtin_unreachable();
}

/* Original0x5FA2E..0x5FA38. */
REGION void tsl9_resident_task_final_handlers_block_5fa2e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30b8\n.option pop\n");
    a5 = UINT32_C(0x00000012); LIVE;
    a3 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa36:\n.option push\n.option rvc\nc.bnez a3,.Lresident_task_final_handlers_edge_5fa36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FA38..0x5FA44. */
REGION void tsl9_resident_task_final_handlers_block_5fa38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 92(s0)\n.option pop\n");
    a3 = a4 & UINT32_C(0x00000004); LIVE;
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa42:\n.option push\n.option rvc\nc.bnez a3,.Lresident_task_final_handlers_edge_5fa42\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FA44..0x5FA4C. */
REGION void tsl9_resident_task_final_handlers_block_5fa44(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000020); LIVE;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa4a:\n.option push\n.option rvc\nc.bnez a3,.Lresident_task_final_handlers_edge_5fa4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FA4C..0x5FA52. */
REGION void tsl9_resident_task_final_handlers_block_5fa4c(void)
{
    REGS;
    a5 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa50:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5fa50\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fa70\n");
    __builtin_unreachable();
}

/* Original0x5FA52..0x5FA70. */
REGION void tsl9_resident_task_final_handlers_block_5fa52(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x319c\n.option pop\n");
    a3 = UINT32_C(0x00001000); LIVE;
    a3 = a3 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a3; LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x2194\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000002); LIVE;
    a5 = a5 | a3; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 42(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb43e\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xffffffff)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 41(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FA70..0x5FA74. */
REGION void tsl9_resident_task_final_handlers_block_5fa70(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa72:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_final_handlers_edge_5fa72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fae0\n");
    __builtin_unreachable();
}

/* Original0x5FA74..0x5FA9C. */
REGION void tsl9_resident_task_final_handlers_block_5fa74(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a4 = a4 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 36(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21bc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3198\n.option pop\n");
    a5 = a5 | a4; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    a4 = *(volatile int8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fa98:\n.option push\n.option norvc\nbgez a4,.Lresident_task_final_handlers_edge_5fa98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fb44\n");
    __builtin_unreachable();
}

/* Original0x5FA9C..0x5FAA0. */
REGION void tsl9_resident_task_final_handlers_block_5fa9c(void)
{
    REGS;
    a4 = UINT32_C(0x0000012c); LIVE;
    __builtin_unreachable();
}

/* Original0x5FAA0..0x5FAB0. */
REGION void tsl9_resident_task_final_handlers_block_5faa0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 37(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a5 = a5 * a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2478\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5faac:\n.option push\n.option norvc\nbne a3,a2,.Lresident_task_final_handlers_edge_5faac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fb50\n");
    __builtin_unreachable();
}

/* Original0x5FAB0..0x5FABE. */
REGION void tsl9_resident_task_final_handlers_block_5fab0(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000051f)); LIVE;
    a4 = a4 + UINT32_C(0x00000002); LIVE;
    a4 = a4 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fabc:\n.option push\n.option rvc\nc.beqz a3,.Lresident_task_final_handlers_edge_5fabc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fb48\n");
    __builtin_unreachable();
}

/* Original0x5FABE..0x5FAC4. */
REGION void tsl9_resident_task_final_handlers_block_5fabe(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x000000d7); LIVE;
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x5FAC4..0x5FAD2. */
REGION void tsl9_resident_task_final_handlers_block_5fac4(void)
{
    REGS;
    a5 = a5 - a4; LIVE;
    a4 = a5 + UINT32_C(0xfffffed4); LIVE;
    a3 = UINT32_C(0x00000514); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5face:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_task_final_handlers_edge_5face\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fb60\n");
    __builtin_unreachable();
}

/* Original0x5FAD2..0x5FADA. */
REGION void tsl9_resident_task_final_handlers_block_5fad2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    __builtin_unreachable();
}

/* Original0x5FADA..0x5FAE0. */
REGION void tsl9_resident_task_final_handlers_block_5fada(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x5FAE0..0x5FAE8. */
REGION void tsl9_resident_task_final_handlers_block_5fae0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fae6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5fae6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5faee\n");
    __builtin_unreachable();
}

/* Original0x5FAE8..0x5FAEE. */
REGION void tsl9_resident_task_final_handlers_block_5fae8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 35(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FAEE..0x5FAF6. */
REGION void tsl9_resident_task_final_handlers_block_5faee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 20(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5faf2:\n.option push\n.option norvc\nbgtz a5,.Lresident_task_final_handlers_edge_5faf2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fba0\n");
    __builtin_unreachable();
}

/* Original0x5FAF6..0x5FAFA. */
REGION void tsl9_resident_task_final_handlers_block_5faf6(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FAFA..0x5FB02. */
REGION void tsl9_resident_task_final_handlers_block_5fafa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x382c\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fafe:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fafe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e6a\n");
    __builtin_unreachable();
}

/* Original0x5FB02..0x5FB0A. */
REGION void tsl9_resident_task_final_handlers_block_5fb02(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a0, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb808\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fb06:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fb06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x5FB0A..0x5FB12. */
REGION void tsl9_resident_task_final_handlers_block_5fb0a(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb0e:\n.option push\n.option norvc\nbne a0,a4,.Lresident_task_final_handlers_edge_5fb0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FB12..0x5FB22. */
REGION void tsl9_resident_task_final_handlers_block_5fb12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 40(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000020); LIVE;
    a4 = a4 & UINT32_C(0x00000060); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb1e:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_final_handlers_edge_5fb1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FB22..0x5FB30. */
REGION void tsl9_resident_task_final_handlers_block_5fb22(void)
{
    REGS;
    a4 = UINT32_C(0xffffffa5); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa438\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 46(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5a\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fb2e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb2e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fa0e\n");
    __builtin_unreachable();
}

/* Original0x5FB30..0x5FB3C. */
REGION void tsl9_resident_task_final_handlers_block_5fb30(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 85(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb38:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_final_handlers_edge_5fb38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fa0c\n");
    __builtin_unreachable();
}

/* Original0x5FB3C..0x5FB44. */
REGION void tsl9_resident_task_final_handlers_block_5fb3c(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 86\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fb42:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fa20\n");
    __builtin_unreachable();
}

/* Original0x5FB44..0x5FB48. */
REGION void tsl9_resident_task_final_handlers_block_5fb44(void)
{
    REGS;
    a4 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb46:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb46\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5faa0\n");
    __builtin_unreachable();
}

/* Original0x5FB48..0x5FB4C. */
REGION void tsl9_resident_task_final_handlers_block_5fb48(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x0000004a); LIVE;
    __builtin_unreachable();
}

/* Original0x5FB4C..0x5FB50. */
REGION void tsl9_resident_task_final_handlers_block_5fb4c(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb4e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fac4\n");
    __builtin_unreachable();
}

/* Original0x5FB50..0x5FB56. */
REGION void tsl9_resident_task_final_handlers_block_5fb50(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb52:\n.option push\n.option norvc\nbne a3,a2,.Lresident_task_final_handlers_edge_5fb52\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fb5c\n");
    __builtin_unreachable();
}

/* Original0x5FB56..0x5FB5C. */
REGION void tsl9_resident_task_final_handlers_block_5fb56(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x0000000b); LIVE;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb5a:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fac4\n");
    __builtin_unreachable();
}

/* Original0x5FB5C..0x5FB60. */
REGION void tsl9_resident_task_final_handlers_block_5fb5c(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb5e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb5e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fb4c\n");
    __builtin_unreachable();
}

/* Original0x5FB60..0x5FBA0. */
REGION void tsl9_resident_task_final_handlers_block_5fb60(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a3 = UINT32_C(0x00002000); LIVE;
    a0 = UINT32_C(0xffffff80); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = a3 + UINT32_C(0x00000514); LIVE;
    a5 = a5 + UINT32_C(0xfffffed5); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 4(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa2c8\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fb9e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fb9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fada\n");
    __builtin_unreachable();
}

/* Original0x5FBA0..0x5FBA6. */
REGION void tsl9_resident_task_final_handlers_block_5fba0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x383c\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fba4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5fba4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fbaa\n");
    __builtin_unreachable();
}

/* Original0x5FBA6..0x5FBAA. */
REGION void tsl9_resident_task_final_handlers_block_5fba6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb83c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fba8:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fba8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fafa\n");
    __builtin_unreachable();
}

/* Original0x5FBAA..0x5FBAE. */
REGION void tsl9_resident_task_final_handlers_block_5fbaa(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fbac:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fbac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fba6\n");
    __builtin_unreachable();
}

/* Original0x5FBAE..0x5FC26. */
REGION void tsl9_candidate_external_flash_5fbae(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1424(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1288(s2)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000024)); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a3 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a1 = UINT32_C(0x000000ff); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x8e89c000); LIVE;
    a5 = a5 + UINT32_C(0xfffffed6); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00555000); LIVE;
    a5 = a5 + UINT32_C(0x00000555); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1340(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0xffffffa1); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa53c\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000025)); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 1300(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fc22:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fc22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x5FC26..0x5FC70. */
REGION void tsl9_resident_task_final_handlers_block_5fc26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1288(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00330000); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    a5 = a5 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000050)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FCDC..0x5FCFE. */
REGION void tsl9_candidate_external_flash_5fcdc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    a2 = a0 + UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000078)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_5fcf6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_5fcf6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FCFE..0x5FD02. */
REGION void tsl9_resident_task_final_handlers_block_5fcfe(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fcfe:\n.option push\n.option norvc\nbnez a0,.Lresident_task_final_handlers_edge_5fcfe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_6012c\n");
    __builtin_unreachable();
}

/* Original0x5FD02..0x5FD2E. */
REGION void tsl9_resident_task_final_handlers_block_5fd02(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s4, 120(s0)\n.option pop\n");
    a3 = UINT32_C(0x0000007f); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 0(s4)\n.option pop\n");
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb458\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a3, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 84(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 92(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd2a:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_final_handlers_edge_5fd2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60068\n");
    __builtin_unreachable();
}

/* Original0x5FD2E..0x5FD38. */
REGION void tsl9_resident_task_final_handlers_block_5fd2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    a3 = a4 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd34:\n.option push\n.option norvc\nbltz a3,.Lresident_task_final_handlers_edge_5fd34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60130\n");
    __builtin_unreachable();
}

/* Original0x5FD38..0x5FD48. */
REGION void tsl9_resident_task_final_handlers_block_5fd38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s2, 2(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s2, 63\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s1, 1\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fd44:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_task_final_handlers_edge_5fd44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd5c\n");
    __builtin_unreachable();
}

/* Original0x5FD48..0x5FD4A. */
REGION void tsl9_resident_task_final_handlers_block_5fd48(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FD4A..0x5FD5C. */
REGION void tsl9_resident_task_final_handlers_block_5fd4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FD5C..0x5FD72. */
REGION void tsl9_resident_task_final_handlers_block_5fd5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli s2, s2, 0x6\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s4, 4\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd70:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_final_handlers_edge_5fd70\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fe12\n");
    __builtin_unreachable();
}

/* Original0x5FD72..0x5FD74. */
REGION void tsl9_resident_task_final_handlers_block_5fd72(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FD74..0x5FD82. */
REGION void tsl9_resident_task_final_handlers_block_5fd74(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd80:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_final_handlers_edge_5fd80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fdc8\n");
    __builtin_unreachable();
}

/* Original0x5FD82..0x5FD86. */
REGION void tsl9_resident_task_final_handlers_block_5fd82(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fd82:\n.option push\n.option norvc\nbnez s2,.Lresident_task_final_handlers_edge_5fd82\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd48\n");
    __builtin_unreachable();
}

/* Original0x5FD86..0x5FD8A. */
REGION void tsl9_resident_task_final_handlers_block_5fd86(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd88:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5fd88\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fd94\n");
    __builtin_unreachable();
}

/* Original0x5FD8A..0x5FD94. */
REGION void tsl9_resident_task_final_handlers_block_5fd8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 33(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fd90:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_final_handlers_edge_5fd90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd48\n");
    __builtin_unreachable();
}

/* Original0x5FD94..0x5FDB6. */
REGION void tsl9_resident_task_final_handlers_block_5fd94(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 92(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 120(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 94\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -6\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 93(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_5fdae:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_5fdae\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FDB6..0x5FDC8. */
REGION void tsl9_resident_task_final_handlers_block_5fdb6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, 6\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FDC8..0x5FDD4. */
REGION void tsl9_resident_task_final_handlers_block_5fdc8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s4)\n.option pop\n");
    a5 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fdd0:\n.option push\n.option norvc\nbnez a5,.Lresident_task_final_handlers_edge_5fdd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60138\n");
    __builtin_unreachable();
}

/* Original0x5FDD4..0x5FDDA. */
REGION void tsl9_resident_task_final_handlers_block_5fdd4(void)
{
    REGS;
    a2 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fdd8:\n.option push\n.option rvc\nc.beqz a2,.Lresident_task_final_handlers_edge_5fdd8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fe4e\n");
    __builtin_unreachable();
}

/* Original0x5FDDA..0x5FE02. */
REGION void tsl9_resident_task_final_handlers_block_5fdda(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    a3 = UINT32_C(0x00001000); LIVE;
    a3 = a3 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -2\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, 2\n.option pop\n");
    a5 = a5 | a3; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 42(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb43e\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, -1(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 41(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FE02..0x5FE0C. */
REGION void tsl9_resident_task_final_handlers_block_5fe02(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 34(s0)\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fe0a:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_final_handlers_edge_5fe0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fef4\n");
    __builtin_unreachable();
}

/* Original0x5FE0C..0x5FE0E. */
REGION void tsl9_resident_task_final_handlers_block_5fe0c(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fe0c:\n.option push\n.option rvc\nc.bnez a2,.Lresident_task_final_handlers_edge_5fe0c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fe56\n");
    __builtin_unreachable();
}

/* Original0x5FE0E..0x5FE12. */
REGION void tsl9_resident_task_final_handlers_block_5fe0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 21\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fe10:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fe10\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x5FE12..0x5FE16. */
REGION void tsl9_resident_task_final_handlers_block_5fe12(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fe12:\n.option push\n.option norvc\nbnez s2,.Lresident_task_final_handlers_edge_5fe12\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60134\n");
    __builtin_unreachable();
}

/* Original0x5FE16..0x5FE1A. */
REGION void tsl9_resident_task_final_handlers_block_5fe16(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fe18:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5fe18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fe24\n");
    __builtin_unreachable();
}

/* Original0x5FE1A..0x5FE24. */
REGION void tsl9_resident_task_final_handlers_block_5fe1a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 33(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fe20:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_final_handlers_edge_5fe20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60134\n");
    __builtin_unreachable();
}

/* Original0x5FE24..0x5FE46. */
REGION void tsl9_resident_task_final_handlers_block_5fe24(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 86\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_5fe3e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_5fe3e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FE46..0x5FE4E. */
REGION void tsl9_resident_task_final_handlers_block_5fe46(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s3, s4, 10\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -7\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fe4c:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fe4c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd74\n");
    __builtin_unreachable();
}

/* Original0x5FE4E..0x5FE56. */
REGION void tsl9_resident_task_final_handlers_block_5fe4e(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 41(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fe54:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fe54\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fe02\n");
    __builtin_unreachable();
}

/* Original0x5FE56..0x5FE5A. */
REGION void tsl9_resident_task_final_handlers_block_5fe56(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fe56:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fe56\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x5FE5A..0x5FE84. */
REGION void tsl9_resident_task_final_handlers_block_5fe5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a4 = a4 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 36(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 1(s3)\n.option pop\n");
    a5 = a5 | a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a4, 0(s3)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fe80:\n.option push\n.option norvc\nbgez a4,.Lresident_task_final_handlers_edge_5fe80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fe8a\n");
    __builtin_unreachable();
}

/* Original0x5FE84..0x5FE8A. */
REGION void tsl9_resident_task_final_handlers_block_5fe84(void)
{
    REGS;
    a4 = UINT32_C(0xffff8000); LIVE;
    a5 = a5 | a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FE8A..0x5FE9A. */
REGION void tsl9_resident_task_final_handlers_block_5fe8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 37(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fe96:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task_final_handlers_edge_5fe96\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fe0e\n");
    __builtin_unreachable();
}

/* Original0x5FE9A..0x5FEA2. */
REGION void tsl9_resident_task_final_handlers_block_5fe9a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -3\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FEA2..0x5FEAE. */
REGION void tsl9_resident_task_final_handlers_block_5fea2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5feaa:\n.option push\n.option norvc\nbnez a4,.Lresident_task_final_handlers_edge_5feaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_6013c\n");
    __builtin_unreachable();
}

/* Original0x5FEAE..0x5FEB4. */
REGION void tsl9_resident_task_final_handlers_block_5feae(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5feb2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_final_handlers_edge_5feb2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fed0\n");
    __builtin_unreachable();
}

/* Original0x5FEB4..0x5FEB8. */
REGION void tsl9_resident_task_final_handlers_block_5feb4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5feb6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_5feb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fec2\n");
    __builtin_unreachable();
}

/* Original0x5FEB8..0x5FEC2. */
REGION void tsl9_resident_task_final_handlers_block_5feb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 33(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5febe:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_final_handlers_edge_5febe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60140\n");
    __builtin_unreachable();
}

/* Original0x5FEC2..0x5FED0. */
REGION void tsl9_resident_task_final_handlers_block_5fec2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 35(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FED0..0x5FED4. */
REGION void tsl9_resident_task_final_handlers_block_5fed0(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fed0:\n.option push\n.option norvc\nbnez s1,.Lresident_task_final_handlers_edge_5fed0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60144\n");
    __builtin_unreachable();
}

/* Original0x5FED4..0x5FED8. */
REGION void tsl9_resident_task_final_handlers_block_5fed4(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fed4:\n.option push\n.option norvc\nbeqz s2,.Lresident_task_final_handlers_edge_5fed4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fefa\n");
    __builtin_unreachable();
}

/* Original0x5FED8..0x5FEE0. */
REGION void tsl9_resident_task_final_handlers_block_5fed8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5fede:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_final_handlers_edge_5fede\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5ff10\n");
    __builtin_unreachable();
}

/* Original0x5FEE0..0x5FEE4. */
REGION void tsl9_resident_task_final_handlers_block_5fee0(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fee0:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fee0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x5FEE4..0x5FEE8. */
REGION void tsl9_resident_task_final_handlers_block_5fee4(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fee4:\n.option push\n.option norvc\nbnez s2,.Lresident_task_final_handlers_edge_5fee4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fe0e\n");
    __builtin_unreachable();
}

/* Original0x5FEE8..0x5FEF2. */
REGION void tsl9_resident_task_final_handlers_block_5fee8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 46(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5feee:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5feee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x5FEF2..0x5FEF4. */
REGION void tsl9_resident_task_final_handlers_block_5fef2(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5fef2:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fef2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fe0e\n");
    __builtin_unreachable();
}

/* Original0x5FEF4..0x5FEFA. */
REGION void tsl9_resident_task_final_handlers_block_5fef4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 45(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fef8:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5fef8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fea2\n");
    __builtin_unreachable();
}

/* Original0x5FEFA..0x5FF00. */
REGION void tsl9_resident_task_final_handlers_block_5fefa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5fefc:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5fefc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e950\n");
    __builtin_unreachable();
}

/* Original0x5FF00..0x5FF02. */
REGION void tsl9_resident_task_final_handlers_block_5ff00(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5ff00:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_final_handlers_edge_5ff00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5ff06\n");
    __builtin_unreachable();
}

/* Original0x5FF02..0x5FF06. */
REGION void tsl9_resident_task_final_handlers_block_5ff02(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 8\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5ff04:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5ff04\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x5FF06..0x5FF0C. */
REGION void tsl9_resident_task_final_handlers_block_5ff06(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5ff08:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5ff08\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ea9a\n");
    __builtin_unreachable();
}

/* Original0x5FF0C..0x5FF0E. */
REGION void tsl9_resident_task_final_handlers_block_5ff0c(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5ff0c:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_final_handlers_edge_5ff0c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5fed8\n");
    __builtin_unreachable();
}

/* Original0x5FF0E..0x5FF10. */
REGION void tsl9_resident_task_final_handlers_block_5ff0e(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_5ff0e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5ff0e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5ff02\n");
    __builtin_unreachable();
}

/* Original0x5FF10..0x5FF1A. */
REGION void tsl9_resident_task_final_handlers_block_5ff10(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 33(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff16:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_final_handlers_edge_5ff16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5ff1c\n");
    __builtin_unreachable();
}

/* Original0x5FF1A..0x5FF1C. */
REGION void tsl9_resident_task_final_handlers_block_5ff1a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FF1C..0x5FF36. */
REGION void tsl9_resident_task_final_handlers_block_5ff1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 37(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3072\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 44(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 45(s0)\n.option pop\n");
    a5 = a2 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5ff32:\n.option push\n.option norvc\nbgez a5,.Lresident_task_final_handlers_edge_5ff32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5ff50\n");
    __builtin_unreachable();
}

/* Original0x5FF36..0x5FF3E. */
REGION void tsl9_resident_task_final_handlers_block_5ff36(void)
{
    REGS;
    a2 = a2 << UINT32_C(0x00000013); LIVE;
    a2 = a2 >> UINT32_C(0x00000013); LIVE;
    a5 = UINT32_C(0x0000012c); LIVE;
    __builtin_unreachable();
}

/* Original0x5FF3E..0x5FF4A. */
REGION void tsl9_resident_task_final_handlers_block_5ff3e(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    a2 = a2 * a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5ff46:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_final_handlers_edge_5ff46\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5ff54\n");
    __builtin_unreachable();
}

/* Original0x5FF4A..0x5FF4C. */
REGION void tsl9_resident_task_final_handlers_block_5ff4a(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x5FF4C..0x5FF50. */
REGION void tsl9_resident_task_final_handlers_block_5ff4c(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff4e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5ff4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5ff68\n");
    __builtin_unreachable();
}

/* Original0x5FF50..0x5FF54. */
REGION void tsl9_resident_task_final_handlers_block_5ff50(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff52:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_5ff52\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5ff3e\n");
    __builtin_unreachable();
}

/* Original0x5FF54..0x5FF62. */
REGION void tsl9_resident_task_final_handlers_block_5ff54(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff60:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_final_handlers_edge_5ff60\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_6002e\n");
    __builtin_unreachable();
}

/* Original0x5FF62..0x5FF68. */
REGION void tsl9_resident_task_final_handlers_block_5ff62(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x000000d7); LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x5FF68..0x5FF7A. */
REGION void tsl9_resident_task_final_handlers_block_5ff68(void)
{
    REGS;
    a2 = a2 - a5; LIVE;
    a5 = UINT32_C(0x004b0000); LIVE;
    a4 = a2 + UINT32_C(0xfffffed4); LIVE;
    a5 = a5 + UINT32_C(0xfffffda8); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff76:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task_final_handlers_edge_5ff76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60148\n");
    __builtin_unreachable();
}

/* Original0x5FF7A..0x5FF82. */
REGION void tsl9_resident_task_final_handlers_block_5ff7a(void)
{
    REGS;
    a5 = UINT32_C(0x00000500); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ff7e:\n.option push\n.option norvc\nbltu a5,a2,.Lresident_task_final_handlers_edge_5ff7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60034\n");
    __builtin_unreachable();
}

/* Original0x5FF82..0x5FFBE. */
REGION void tsl9_resident_task_final_handlers_block_5ff82(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a1 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a1; LIVE;
    a0 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s2, 1300\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffffed5); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 4(a1). */
    PORT(".option push\n.option rvc\n.2byte 0xa1c8\n.option pop\n");
    a2 = a2 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\naddi s3, s2, 1300\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5FFBE..0x5FFC2. */
REGION void tsl9_resident_task_final_handlers_block_5ffbe(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_task_final_handlers_edge_5ffc0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_final_handlers_edge_5ffc0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_5ffbe\n");
    __builtin_unreachable();
}

/* Original0x5FFC2..0x5FFD6. */
REGION void tsl9_resident_task_final_handlers_block_5ffc2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 33(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 34(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 33(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_5ffd2:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_5ffd2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5fbae\n");
    __builtin_unreachable();
}

/* Original0x5FFD6..0x6000C. */
REGION void tsl9_resident_task_final_handlers_block_5ffd6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 1340(s1)\n.option pop\n");
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s1)\n.option pop\n");
    a3 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nli s1, 32\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a3, 4(s3)\n.option pop\n");
    a3 = UINT32_C(0x000005ba); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_task_final_handlers_literal_60004:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_60004\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6000C..0x60016. */
REGION void tsl9_resident_task_final_handlers_block_6000c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_60012:\n.option push\n.option norvc\nbeqz a5,.Lresident_task_final_handlers_edge_60012\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60016..0x6002E. */
REGION void tsl9_resident_task_final_handlers_block_60016(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6002a:\n.option push\n.option norvc\njal zero,.Lresident_task_final_handlers_edge_6002a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5f234\n");
    __builtin_unreachable();
}

/* Original0x6002E..0x60034. */
REGION void tsl9_resident_task_final_handlers_block_6002e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000004a); LIVE;
    PORT(".Lresident_task_final_handlers_edge_60032:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60032\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5ff4c\n");
    __builtin_unreachable();
}

/* Original0x60034..0x60044. */
REGION void tsl9_resident_task_final_handlers_block_60034(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 48(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nli s1, 33\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60040:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_final_handlers_edge_60040\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60044..0x60066. */
REGION void tsl9_resident_task_final_handlers_block_60044(void)
{
    REGS;
    a5 = UINT32_C(0x00000271); LIVE;
    a2 = a2 + UINT32_C(0xfffffd8f); LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a2, a5\n.option pop\n");
    a0 = UINT32_C(0x00060000); LIVE;
    PORT(".option push\n.option norvc\naddi a3, s0, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffc70); LIVE;
    PORT(".option push\n.option norvc\nli s1, 127\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60062:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_60062\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x60066..0x60068. */
REGION void tsl9_resident_task_final_handlers_block_60066(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_60066:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60066\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60068..0x6006E. */
REGION void tsl9_resident_task_final_handlers_block_60068(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_final_handlers_edge_6006a:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_task_final_handlers_edge_6006a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_60078\n");
    __builtin_unreachable();
}

/* Original0x6006E..0x60078. */
REGION void tsl9_resident_task_final_handlers_block_6006e(void)
{
    REGS;
    a3 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nli s1, 128\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60074:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_final_handlers_edge_60074\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60078..0x60088. */
REGION void tsl9_resident_task_final_handlers_block_60078(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nli s1, 128\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60084:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task_final_handlers_edge_60084\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60088..0x600AC. */
REGION void tsl9_resident_task_final_handlers_block_60088(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s4, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 86\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_600a4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_600a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x600AC..0x600B8. */
REGION void tsl9_resident_task_final_handlers_block_600ac(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x345c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 92(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_600b4:\n.option push\n.option norvc\nbne a5,a4,.Lresident_task_final_handlers_edge_600b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_600d6\n");
    __builtin_unreachable();
}

/* Original0x600B8..0x600D6. */
REGION void tsl9_resident_task_final_handlers_block_600b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a1, 120(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 92(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 94\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000008); LIVE;
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 93(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_600ce:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_600ce\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x600D6..0x600DC. */
REGION void tsl9_resident_task_final_handlers_block_600d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_600d8:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_600d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e950\n");
    __builtin_unreachable();
}

/* Original0x600DC..0x600E4. */
REGION void tsl9_resident_task_final_handlers_block_600dc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_600e0:\n.option push\n.option norvc\nbne a0,a5,.Lresident_task_final_handlers_edge_600e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5ff02\n");
    __builtin_unreachable();
}

/* Original0x600E4..0x600EA. */
REGION void tsl9_resident_task_final_handlers_block_600e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_600e6:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_600e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ea9a\n");
    __builtin_unreachable();
}

/* Original0x600EA..0x600EE. */
REGION void tsl9_resident_task_final_handlers_block_600ea(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_600ea:\n.option push\n.option norvc\nbne a0,s1,.Lresident_task_final_handlers_edge_600ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5ff02\n");
    __builtin_unreachable();
}

/* Original0x600EE..0x600F2. */
REGION void tsl9_resident_task_final_handlers_block_600ee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x345c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_600f0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_600f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_600f8\n");
    __builtin_unreachable();
}

/* Original0x600F2..0x600F8. */
REGION void tsl9_resident_task_final_handlers_block_600f2(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_task_final_handlers_edge_600f4:\n.option push\n.option norvc\nbne a5,a4,.Lresident_task_final_handlers_edge_600f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_6010c\n");
    __builtin_unreachable();
}

/* Original0x600F8..0x600FE. */
REGION void tsl9_resident_task_final_handlers_block_600f8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x347c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_600fc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_600fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_6010c\n");
    __builtin_unreachable();
}

/* Original0x600FE..0x60104. */
REGION void tsl9_resident_task_final_handlers_block_600fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 84(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60102:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_60102\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_6010c\n");
    __builtin_unreachable();
}

/* Original0x60104..0x60108. */
REGION void tsl9_resident_task_final_handlers_block_60104(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60106:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_60106\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_60122\n");
    __builtin_unreachable();
}

/* Original0x60108..0x6010C. */
REGION void tsl9_resident_task_final_handlers_block_60108(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6010C..0x60110. */
REGION void tsl9_resident_task_final_handlers_block_6010c(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_6010c:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_6010c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x60110..0x6011A. */
REGION void tsl9_resident_task_final_handlers_block_60110(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3458\n.option pop\n");
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nli s1, 6\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60116:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_final_handlers_edge_60116\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x6011A..0x60120. */
REGION void tsl9_resident_task_final_handlers_block_6011a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6011c:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_6011c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x60120..0x60122. */
REGION void tsl9_resident_task_final_handlers_block_60120(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_60120:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60120\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60122..0x60128. */
REGION void tsl9_resident_task_final_handlers_block_60122(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60124:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_60124\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ee06\n");
    __builtin_unreachable();
}

/* Original0x60128..0x6012C. */
REGION void tsl9_resident_task_final_handlers_block_60128(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6012a:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_6012a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x6012C..0x60130. */
REGION void tsl9_resident_task_final_handlers_block_6012c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6012e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_6012e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60130..0x60134. */
REGION void tsl9_resident_task_final_handlers_block_60130(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 7\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60132:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60132\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60134..0x60138. */
REGION void tsl9_resident_task_final_handlers_block_60134(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 17\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60136:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60136\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60138..0x6013C. */
REGION void tsl9_resident_task_final_handlers_block_60138(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 19\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6013a:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_6013a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x6013C..0x60140. */
REGION void tsl9_resident_task_final_handlers_block_6013c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 22\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6013e:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_6013e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60140..0x60144. */
REGION void tsl9_resident_task_final_handlers_block_60140(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 23\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60142:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60142\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60144..0x60148. */
REGION void tsl9_resident_task_final_handlers_block_60144(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 24\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60146:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60146\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x60148..0x6014E. */
REGION void tsl9_resident_task_final_handlers_block_60148(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s1, 33\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6014c:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_6014c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_5fd4a\n");
    __builtin_unreachable();
}

/* Original0x6014E..0x60168. */
REGION void tsl9_candidate_external_flash_6014e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a2 = a0 + UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000078)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_literal_60160:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_60160\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60168..0x6016A. */
REGION void tsl9_resident_task_final_handlers_block_60168(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_60168:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_final_handlers_edge_60168\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_60206\n");
    __builtin_unreachable();
}

/* Original0x6016A..0x60186. */
REGION void tsl9_resident_task_final_handlers_block_6016a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a1, 120(s0)\n.option pop\n");
    a4 = UINT32_C(0x0000001f); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x319c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 92(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_final_handlers_edge_60182:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task_final_handlers_edge_60182\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_601a8\n");
    __builtin_unreachable();
}

/* Original0x60186..0x60194. */
REGION void tsl9_resident_task_final_handlers_block_60186(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    a0 = UINT32_C(0x00000007); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb45c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60190:\n.option push\n.option norvc\nbne a5,a4,.Lresident_task_final_handlers_edge_60190\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_601a8\n");
    __builtin_unreachable();
}

/* Original0x60194..0x601A0. */
REGION void tsl9_resident_task_final_handlers_block_60194(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 84(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_6019c:\n.option push\n.option norvc\nbne a3,a4,.Lresident_task_final_handlers_edge_6019c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_601e2\n");
    __builtin_unreachable();
}

/* Original0x601A0..0x601A6. */
REGION void tsl9_resident_task_final_handlers_block_601a0(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_final_handlers_edge_601a4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_final_handlers_edge_601a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_601b0\n");
    __builtin_unreachable();
}

/* Original0x601A6..0x601A8. */
REGION void tsl9_resident_task_final_handlers_block_601a6(void)
{
    REGS;
    a0 = UINT32_C(0x00000011); LIVE;
    __builtin_unreachable();
}

/* Original0x601A8..0x601B0. */
REGION void tsl9_resident_task_final_handlers_block_601a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x601B0..0x601B8. */
REGION void tsl9_resident_task_final_handlers_block_601b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 100(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000002); LIVE;
    a0 = a0 + UINT32_C(0x00000014); LIVE;
    __builtin_unreachable();
}

/* Original0x601B8..0x601C0. */
REGION void tsl9_resident_task_final_handlers_block_601b8(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_literal_601b8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_final_handlers_literal_601b8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x601C0..0x601C2. */
REGION void tsl9_resident_task_final_handlers_block_601c0(void)
{
    REGS;
    PORT(".Lresident_task_final_handlers_edge_601c0:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_final_handlers_edge_601c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_601a6\n");
    __builtin_unreachable();
}

/* Original0x601C2..0x601CA. */
REGION void tsl9_resident_task_final_handlers_block_601c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 20(s0)\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_601c6:\n.option push\n.option norvc\nbgtz a5,.Lresident_task_final_handlers_edge_601c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_601f8\n");
    __builtin_unreachable();
}

/* Original0x601CA..0x601CE. */
REGION void tsl9_resident_task_final_handlers_block_601ca(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x601CE..0x601D6. */
REGION void tsl9_resident_task_final_handlers_block_601ce(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x382c\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_601d2:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_601d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e6a\n");
    __builtin_unreachable();
}

/* Original0x601D6..0x601DE. */
REGION void tsl9_resident_task_final_handlers_block_601d6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a0, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb808\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_601da:\n.option push\n.option norvc\njal ra,.Lresident_task_final_handlers_edge_601da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x601DE..0x601E2. */
REGION void tsl9_resident_task_final_handlers_block_601de(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_final_handlers_edge_601e0:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_601e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_601a8\n");
    __builtin_unreachable();
}

/* Original0x601E2..0x601EE. */
REGION void tsl9_resident_task_final_handlers_block_601e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 85(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_601ea:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_final_handlers_edge_601ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_final_handlers_block_601a6\n");
    __builtin_unreachable();
}

/* Original0x601EE..0x601F8. */
REGION void tsl9_resident_task_final_handlers_block_601ee(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 86\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_601f6:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_601f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_601b8\n");
    __builtin_unreachable();
}

/* Original0x601F8..0x601FE. */
REGION void tsl9_resident_task_final_handlers_block_601f8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x383c\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_601fc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_final_handlers_edge_601fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_final_handlers_block_60202\n");
    __builtin_unreachable();
}

/* Original0x601FE..0x60202. */
REGION void tsl9_resident_task_final_handlers_block_601fe(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb83c\n.option pop\n");
    PORT(".Lresident_task_final_handlers_edge_60200:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60200\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_601ce\n");
    __builtin_unreachable();
}

/* Original0x60202..0x60206. */
REGION void tsl9_resident_task_final_handlers_block_60202(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_60204:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60204\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_601fe\n");
    __builtin_unreachable();
}

/* Original0x60206..0x6020A. */
REGION void tsl9_resident_task_final_handlers_block_60206(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_final_handlers_edge_60208:\n.option push\n.option rvc\nc.j .Lresident_task_final_handlers_edge_60208\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_final_handlers_block_601a8\n");
    __builtin_unreachable();
}
