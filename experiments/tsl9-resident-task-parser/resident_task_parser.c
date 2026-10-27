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

/* Four complete conditional SDK parser/scheduler/count bodies:2316B/770i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43414..0x4343C. */
REGION void tsl9_candidate_external_flash_43414(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_task_parser_edge_4343a:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_parser_edge_4343a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_4345a\n");
    __builtin_unreachable();
}

/* Original0x4343C..0x43442. */
REGION void tsl9_resident_task_parser_block_4343c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x43442..0x4345A. */
REGION void tsl9_resident_task_parser_block_43442(void)
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
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4345A..0x4346E. */
REGION void tsl9_resident_task_parser_block_4345a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option rvc\nmv s5, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s7, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4346E..0x4347E. */
REGION void tsl9_resident_task_parser_block_4346e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000022c)); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    a3 = UINT32_C(0x0000000c); LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x4347E..0x4348A. */
REGION void tsl9_resident_task_parser_block_4347e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul s8, s0, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a2, a4, s8\n.option pop\n");
    a2 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_parser_edge_43488:\n.option push\n.option rvc\nc.bnez a2,.Lresident_task_parser_edge_43488\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_4350e\n");
    __builtin_unreachable();
}

/* Original0x4348A..0x4349A. */
REGION void tsl9_resident_task_parser_block_4348a(void)
{
    REGS;
    a1 = UINT32_C(0x00010000); LIVE;
    a1 = a1 + UINT32_C(0xffffff00); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_parser_literal_43492:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_43492\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4349A..0x4349C. */
REGION void tsl9_resident_task_parser_block_4349a(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_4349a:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_parser_edge_4349a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_434b8\n");
    __builtin_unreachable();
}

/* Original0x4349C..0x434A6. */
REGION void tsl9_resident_task_parser_block_4349c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_task_parser_edge_434a4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_434a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_434ac\n");
    __builtin_unreachable();
}

/* Original0x434A6..0x434AC. */
REGION void tsl9_resident_task_parser_block_434a6(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x434AC..0x434B8. */
REGION void tsl9_resident_task_parser_block_434ac(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lresident_task_parser_edge_434b6:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_434b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_43442\n");
    __builtin_unreachable();
}

/* Original0x434B8..0x434C2. */
REGION void tsl9_resident_task_parser_block_434b8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e8)); LIVE;
    PORT(".Lresident_task_parser_edge_434c0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_parser_edge_434c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_43506\n");
    __builtin_unreachable();
}

/* Original0x434C2..0x434C6. */
REGION void tsl9_resident_task_parser_block_434c2(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e8)) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x434C6..0x434F4. */
REGION void tsl9_resident_task_parser_block_434c6(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 556(s2)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a4, a4, s0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsw s7, 8(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa13a\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s5, 4(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s8\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s3, 0(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s6, 4(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s5, 8(a5)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_434f0:\n.option push\n.option norvc\nbeqz s4,.Lresident_task_parser_edge_434f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_434f8\n");
    __builtin_unreachable();
}

/* Original0x434F4..0x434F8. */
REGION void tsl9_resident_task_parser_block_434f4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 0(s4)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x434F8..0x43504. */
REGION void tsl9_resident_task_parser_block_434f8(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_parser_edge_43502:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_43502\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_43442\n");
    __builtin_unreachable();
}

/* Original0x43504..0x43506. */
REGION void tsl9_resident_task_parser_block_43504(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43506..0x4350A. */
REGION void tsl9_resident_task_parser_block_43506(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_task_parser_edge_43508:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_parser_edge_43508\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_43504\n");
    __builtin_unreachable();
}

/* Original0x4350A..0x4350E. */
REGION void tsl9_resident_task_parser_block_4350a(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_task_parser_edge_4350c:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_4350c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_434c6\n");
    __builtin_unreachable();
}

/* Original0x4350E..0x43514. */
REGION void tsl9_resident_task_parser_block_4350e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lresident_task_parser_edge_43510:\n.option push\n.option norvc\nbne s0,a5,.Lresident_task_parser_edge_43510\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_4347e\n");
    __builtin_unreachable();
}

/* Original0x43514..0x43520. */
REGION void tsl9_resident_task_parser_block_43514(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_parser_edge_4351e:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_4351e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_43442\n");
    __builtin_unreachable();
}

/* Original0x43A14..0x43A38. */
REGION void tsl9_candidate_external_flash_43a14(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40024\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x0000002f); LIVE;
    PORT(".Lresident_task_parser_edge_43a34:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task_parser_edge_43a34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_43a80\n");
    __builtin_unreachable();
}

/* Original0x43A38..0x43A4C. */
REGION void tsl9_resident_task_parser_block_43a38(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul s0, a0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 556(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_parser_edge_43a4a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_43a4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_43a80\n");
    __builtin_unreachable();
}

/* Original0x43A4C..0x43A5E. */
REGION void tsl9_resident_task_parser_block_43a4c(void)
{
    REGS;
    a5 = a0 & UINT32_C(0x0000000f); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a1, a1, a5\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task_parser_edge_43a5c:\n.option push\n.option rvc\nc.jal .Lresident_task_parser_edge_43a5c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x43A5E..0x43A72. */
REGION void tsl9_resident_task_parser_block_43a5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 556(s3)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43A72..0x43A80. */
REGION void tsl9_resident_task_parser_block_43a72(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43A80..0x43A8C. */
REGION void tsl9_resident_task_parser_block_43a80(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_parser_edge_43a8a:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_43a8a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_43a72\n");
    __builtin_unreachable();
}

/* Original0x57AD8..0x57AFA. */
REGION void tsl9_candidate_external_flash_57ad8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x311c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2138\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2154\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2118\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option rvc\nli a6, 1\n.option pop\n");
    a5 = a5 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 3(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3138\n.option pop\n");
    a1 = UINT32_C(0x00000020); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x57AFA..0x57B02. */
REGION void tsl9_resident_task_parser_block_57afa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsll a2, a6, a4\n.option pop\n");
    a2 = a2 & a5; LIVE;
    PORT(".Lresident_task_parser_edge_57b00:\n.option push\n.option rvc\nc.beqz a2,.Lresident_task_parser_edge_57b00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_57b08\n");
    __builtin_unreachable();
}

/* Original0x57B02..0x57B08. */
REGION void tsl9_resident_task_parser_block_57b02(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x57B08..0x57B0E. */
REGION void tsl9_resident_task_parser_block_57b08(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_57b0a:\n.option push\n.option norvc\nbne a4,a1,.Lresident_task_parser_edge_57b0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_57afa\n");
    __builtin_unreachable();
}

/* Original0x57B0E..0x57B12. */
REGION void tsl9_resident_task_parser_block_57b0e(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x57B12..0x57B1A. */
REGION void tsl9_resident_task_parser_block_57b12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsra a4, a3, a5\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_57b18:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_parser_edge_57b18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_57b20\n");
    __builtin_unreachable();
}

/* Original0x57B1A..0x57B20. */
REGION void tsl9_resident_task_parser_block_57b1a(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x57B20..0x57B26. */
REGION void tsl9_resident_task_parser_block_57b20(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_57b22:\n.option push\n.option norvc\nbne a5,a2,.Lresident_task_parser_edge_57b22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_57b12\n");
    __builtin_unreachable();
}

/* Original0x57B26..0x57B28. */
REGION void tsl9_resident_task_parser_block_57b26(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F234..0x5F264. */
REGION void tsl9_candidate_external_flash_5f234(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -112\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 104(sp)\n.option pop\n");
    a2 = a0 + UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000078)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 108(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 100(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 96(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 60(sp)\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f25c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f25c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F264..0x5F268. */
REGION void tsl9_resident_task_parser_block_5f264(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f266:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_parser_edge_5f266\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F268..0x5F284. */
REGION void tsl9_resident_task_parser_block_5f268(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s4, 120(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    a4 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s4)\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb454\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1(s4)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f280:\n.option push\n.option norvc\nbne a3,a2,.Lresident_task_parser_edge_5f280\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F284..0x5F29A. */
REGION void tsl9_resident_task_parser_block_5f284(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s1, 2(s4)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsrli s5, s1, 0x6\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 63\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f296:\n.option push\n.option norvc\nbleu a5,s1,.Lresident_task_parser_edge_5f296\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F29A..0x5F2A2. */
REGION void tsl9_resident_task_parser_block_5f29a(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a4, s1, 1\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f29e:\n.option push\n.option norvc\nble a5,a4,.Lresident_task_parser_edge_5f29e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f2aa\n");
    __builtin_unreachable();
}

/* Original0x5F2A2..0x5F2AA. */
REGION void tsl9_resident_task_parser_block_5f2a2(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_task_parser_edge_5f2a6:\n.option push\n.option norvc\nbeq s5,a3,.Lresident_task_parser_edge_5f2a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F2AA..0x5F2BE. */
REGION void tsl9_resident_task_parser_block_5f2aa(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nsub a5, a5, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 46(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s4, 4\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f2bc:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_parser_edge_5f2bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f2ea\n");
    __builtin_unreachable();
}

/* Original0x5F2BE..0x5F2C0. */
REGION void tsl9_resident_task_parser_block_5f2be(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F2C0..0x5F2CC. */
REGION void tsl9_resident_task_parser_block_5f2c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_parser_edge_5f2ca:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f2ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f37a\n");
    __builtin_unreachable();
}

/* Original0x5F2CC..0x5F2D6. */
REGION void tsl9_resident_task_parser_block_5f2cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 92(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 120(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f2d2:\n.option push\n.option norvc\nbeqz a4,.Lresident_task_parser_edge_5f2d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f520\n");
    __builtin_unreachable();
}

/* Original0x5F2D6..0x5F2DE. */
REGION void tsl9_resident_task_parser_block_5f2d6(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f2da:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_parser_edge_5f2da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f34a\n");
    __builtin_unreachable();
}

/* Original0x5F2DE..0x5F2E6. */
REGION void tsl9_resident_task_parser_block_5f2de(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f2e2:\n.option push\n.option norvc\nbltz a5,.Lresident_task_parser_edge_5f2e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f354\n");
    __builtin_unreachable();
}

/* Original0x5F2E6..0x5F2EA. */
REGION void tsl9_resident_task_parser_block_5f2e6(void)
{
    REGS;
    a4 = UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_task_parser_edge_5f2e8:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f2e8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F2EA..0x5F2F4. */
REGION void tsl9_resident_task_parser_block_5f2ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 84(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 86\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f2f2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f2f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f324\n");
    __builtin_unreachable();
}

/* Original0x5F2F4..0x5F300. */
REGION void tsl9_resident_task_parser_block_5f2f4(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f2f8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f2f8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F300..0x5F304. */
REGION void tsl9_resident_task_parser_block_5f300(void)
{
    REGS;
    a4 = UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_task_parser_edge_5f302:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_parser_edge_5f302\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f342\n");
    __builtin_unreachable();
}

/* Original0x5F304..0x5F324. */
REGION void tsl9_resident_task_parser_block_5f304(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 108(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 104(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 100(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 96(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 112\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F324..0x5F342. */
REGION void tsl9_resident_task_parser_block_5f324(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 85(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f33a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f33a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F342..0x5F34A. */
REGION void tsl9_resident_task_parser_block_5f342(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s4, 10\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -7\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f348:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f348\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f2c0\n");
    __builtin_unreachable();
}

/* Original0x5F34A..0x5F354. */
REGION void tsl9_resident_task_parser_block_5f34a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 93(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_task_parser_edge_5f350:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_parser_edge_5f350\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f2e6\n");
    __builtin_unreachable();
}

/* Original0x5F354..0x5F364. */
REGION void tsl9_resident_task_parser_block_5f354(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 94\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f35c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f35c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F364..0x5F366. */
REGION void tsl9_resident_task_parser_block_5f364(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f364:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_parser_edge_5f364\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f2e6\n");
    __builtin_unreachable();
}

/* Original0x5F366..0x5F37A. */
REGION void tsl9_resident_task_parser_block_5f366(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -6\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 6\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F37A..0x5F380. */
REGION void tsl9_resident_task_parser_block_5f37a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f37c:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f37c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e950\n");
    __builtin_unreachable();
}

/* Original0x5F380..0x5F384. */
REGION void tsl9_resident_task_parser_block_5f380(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_parser_edge_5f382:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_parser_edge_5f382\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F384..0x5F38E. */
REGION void tsl9_resident_task_parser_block_5f384(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 3(s4)\n.option pop\n");
    a5 = a3 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task_parser_edge_5f38c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f38c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f396\n");
    __builtin_unreachable();
}

/* Original0x5F38E..0x5F396. */
REGION void tsl9_resident_task_parser_block_5f38e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F396..0x5F39C. */
REGION void tsl9_resident_task_parser_block_5f396(void)
{
    REGS;
    a5 = a3 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_parser_edge_5f39a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f39a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f3ce\n");
    __builtin_unreachable();
}

/* Original0x5F39C..0x5F3AE. */
REGION void tsl9_resident_task_parser_block_5f39c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 41(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000014); LIVE;
    a2 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task_parser_edge_5f3aa:\n.option push\n.option norvc\nbne a1,a2,.Lresident_task_parser_edge_5f3aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F3AE..0x5F3C4. */
REGION void tsl9_resident_task_parser_block_5f3ae(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 0(s2)\n.option pop\n");
    a5 = a5 | a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 42(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x343a\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f3c0:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_parser_edge_5f3c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f3c6\n");
    __builtin_unreachable();
}

/* Original0x5F3C4..0x5F3C6. */
REGION void tsl9_resident_task_parser_block_5f3c4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a5, 42(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb43e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F3C6..0x5F3CE. */
REGION void tsl9_resident_task_parser_block_5f3c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -2\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F3CE..0x5F3D4. */
REGION void tsl9_resident_task_parser_block_5f3ce(void)
{
    REGS;
    a5 = a3 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_parser_edge_5f3d2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f3d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f422\n");
    __builtin_unreachable();
}

/* Original0x5F3D4..0x5F3DA. */
REGION void tsl9_resident_task_parser_block_5f3d4(void)
{
    REGS;
    a4 = UINT32_C(0x00000015); LIVE;
    PORT(".Lresident_task_parser_edge_5f3d6:\n.option push\n.option norvc\nbnez s5,.Lresident_task_parser_edge_5f3d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F3DA..0x5F404. */
REGION void tsl9_resident_task_parser_block_5f3da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s2)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a4 = a4 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 36(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 | a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a4, 0(s2)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f400:\n.option push\n.option norvc\nbgez a4,.Lresident_task_parser_edge_5f400\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f40a\n");
    __builtin_unreachable();
}

/* Original0x5F404..0x5F40A. */
REGION void tsl9_resident_task_parser_block_5f404(void)
{
    REGS;
    a4 = UINT32_C(0xffff8000); LIVE;
    a5 = a5 | a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F40A..0x5F416. */
REGION void tsl9_resident_task_parser_block_5f40a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307e\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -3\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f414:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f414\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f422\n");
    __builtin_unreachable();
}

/* Original0x5F416..0x5F422. */
REGION void tsl9_resident_task_parser_block_5f416(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F422..0x5F42A. */
REGION void tsl9_resident_task_parser_block_5f422(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task_parser_edge_5f426:\n.option push\n.option norvc\nbeqz a3,.Lresident_task_parser_edge_5f426\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f864\n");
    __builtin_unreachable();
}

/* Original0x5F42A..0x5F430. */
REGION void tsl9_resident_task_parser_block_5f42a(void)
{
    REGS;
    a4 = UINT32_C(0x00000016); LIVE;
    PORT(".Lresident_task_parser_edge_5f42c:\n.option push\n.option norvc\nbnez s5,.Lresident_task_parser_edge_5f42c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F430..0x5F43E. */
REGION void tsl9_resident_task_parser_block_5f430(void)
{
    REGS;
    a2 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 28\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f436:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f436\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F43E..0x5F44C. */
REGION void tsl9_resident_task_parser_block_5f43e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhusp a5, 30(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x87bc\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc7e\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000e); LIVE;
    PORT(".Lresident_task_parser_edge_5f448:\n.option push\n.option norvc\nbne a5,a4,.Lresident_task_parser_edge_5f448\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f470\n");
    __builtin_unreachable();
}

/* Original0x5F44C..0x5F456. */
REGION void tsl9_resident_task_parser_block_5f44c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 130(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f452:\n.option push\n.option norvc\nbeqz a5,.Lresident_task_parser_edge_5f452\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f61a\n");
    __builtin_unreachable();
}

/* Original0x5F456..0x5F464. */
REGION void tsl9_resident_task_parser_block_5f456(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s3, 1092(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s6, s0, 86\n.option pop\n");
    PORT(".option push\n.option rvc\nli s7, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F464..0x5F468. */
REGION void tsl9_resident_task_parser_block_5f464(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f464:\n.option push\n.option norvc\nbnez s3,.Lresident_task_parser_edge_5f464\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f540\n");
    __builtin_unreachable();
}

/* Original0x5F468..0x5F470. */
REGION void tsl9_resident_task_parser_block_5f468(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 124(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f46c:\n.option push\n.option norvc\nbnez a5,.Lresident_task_parser_edge_5f46c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f5a0\n");
    __builtin_unreachable();
}

/* Original0x5F470..0x5F478. */
REGION void tsl9_resident_task_parser_block_5f470(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -18\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 18\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F478..0x5F482. */
REGION void tsl9_resident_task_parser_block_5f478(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s4)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_parser_edge_5f480:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f480\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f492\n");
    __builtin_unreachable();
}

/* Original0x5F482..0x5F492. */
REGION void tsl9_resident_task_parser_block_5f482(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F492..0x5F494. */
REGION void tsl9_resident_task_parser_block_5f492(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f492:\n.option push\n.option rvc\nc.beqz s1,.Lresident_task_parser_edge_5f492\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f510\n");
    __builtin_unreachable();
}

/* Original0x5F494..0x5F49E. */
REGION void tsl9_resident_task_parser_block_5f494(void)
{
    REGS;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x00000009); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nli a6, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F49E..0x5F4AA. */
REGION void tsl9_resident_task_parser_block_5f49e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s2)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f4a6:\n.option push\n.option norvc\nbne a4,a2,.Lresident_task_parser_edge_5f4a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f4fa\n");
    __builtin_unreachable();
}

/* Original0x5F4AA..0x5F4AE. */
REGION void tsl9_resident_task_parser_block_5f4aa(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f4aa:\n.option push\n.option norvc\nbne a5,a1,.Lresident_task_parser_edge_5f4aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f4fa\n");
    __builtin_unreachable();
}

/* Original0x5F4AE..0x5F4B6. */
REGION void tsl9_resident_task_parser_block_5f4ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 124(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f4b2:\n.option push\n.option norvc\nbne a4,a0,.Lresident_task_parser_edge_5f4b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f4fa\n");
    __builtin_unreachable();
}

/* Original0x5F4B6..0x5F4FA. */
REGION void tsl9_resident_task_parser_block_5f4b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 3(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 2(s2)\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000008); LIVE;
    a3 = a3 | a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 4(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a3 = a3 | a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 5(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option norvc\nsw a4, 192(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 6(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 224(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 7(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 225(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 8(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 226(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 9(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a6, 124(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 227(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F4FA..0x5F4FE. */
REGION void tsl9_resident_task_parser_block_5f4fa(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f4fa:\n.option push\n.option norvc\nbleu s1,a5,.Lresident_task_parser_edge_5f4fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f510\n");
    __builtin_unreachable();
}

/* Original0x5F4FE..0x5F510. */
REGION void tsl9_resident_task_parser_block_5f4fe(void)
{
    REGS;
    a4 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a4\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f50e:\n.option push\n.option rvc\nc.bnez s1,.Lresident_task_parser_edge_5f50e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f49e\n");
    __builtin_unreachable();
}

/* Original0x5F510..0x5F516. */
REGION void tsl9_resident_task_parser_block_5f510(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f512:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f512\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ea9a\n");
    __builtin_unreachable();
}

/* Original0x5F516..0x5F51C. */
REGION void tsl9_resident_task_parser_block_5f516(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f518:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_task_parser_edge_5f518\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f86a\n");
    __builtin_unreachable();
}

/* Original0x5F51C..0x5F520. */
REGION void tsl9_resident_task_parser_block_5f51c(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_parser_edge_5f51e:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f51e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F520..0x5F53E. */
REGION void tsl9_resident_task_parser_block_5f520(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 92(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 93(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 94\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f536:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f536\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F53E..0x5F540. */
REGION void tsl9_resident_task_parser_block_5f53e(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f53e:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f53e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f366\n");
    __builtin_unreachable();
}

/* Original0x5F540..0x5F54C. */
REGION void tsl9_resident_task_parser_block_5f540(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f548:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_parser_edge_5f548\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f614\n");
    __builtin_unreachable();
}

/* Original0x5F54C..0x5F55A. */
REGION void tsl9_resident_task_parser_block_5f54c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 5(s3)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f556:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_parser_edge_5f556\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f614\n");
    __builtin_unreachable();
}

/* Original0x5F55A..0x5F56A. */
REGION void tsl9_resident_task_parser_block_5f55a(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s6\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s3, 6\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f562:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f562\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F56A..0x5F56E. */
REGION void tsl9_resident_task_parser_block_5f56a(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f56a:\n.option push\n.option norvc\nbne a0,s7,.Lresident_task_parser_edge_5f56a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f614\n");
    __builtin_unreachable();
}

/* Original0x5F56E..0x5F596. */
REGION void tsl9_resident_task_parser_block_5f56e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 209(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s7, 210(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 212(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 213(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 214\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f58e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f58e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F596..0x5F59C. */
REGION void tsl9_resident_task_parser_block_5f596(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw zero, 224(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F59C..0x5F5A0. */
REGION void tsl9_resident_task_parser_block_5f59c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 124(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F5A0..0x5F5F4. */
REGION void tsl9_resident_task_parser_block_5f5a0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000024)); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 176\n.option pop\n");
    a4 = a5 >> UINT32_C(0x00000005); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 223(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 37(s0)\n.option pop\n");
    a2 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 220(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7a\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 180(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 221(s0)\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 222(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000028)); LIVE;
    a3 = a4 << UINT32_C(0x00000018); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsw a4, 152(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000002c)); LIVE;
    a3 = a3 | a2; LIVE;
    PORT(".option push\n.option norvc\nsw a3, 148(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a4, 136(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000020)); LIVE;
    PORT(".option push\n.option norvc\nsw a4, 176(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f5f0:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f5f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ad8\n");
    __builtin_unreachable();
}

/* Original0x5F5F4..0x5F608. */
REGION void tsl9_resident_task_parser_block_5f5f4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001d)); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 143(s0)\n.option pop\n");
    a0 = UINT32_C(0x00002000); LIVE;
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_task_parser_edge_5f606:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_parser_edge_5f606\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f65a\n");
    __builtin_unreachable();
}

/* Original0x5F608..0x5F614. */
REGION void tsl9_resident_task_parser_block_5f608(void)
{
    REGS;
    PORT(".option push\n.option norvc\nand s3, s3, a0\n.option pop\n");
    a0 = UINT32_C(0x0000001e); LIVE;
    PORT(".option push\n.option norvc\nmul s3, s3, a0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f612:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f612\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f672\n");
    __builtin_unreachable();
}

/* Original0x5F614..0x5F61A. */
REGION void tsl9_resident_task_parser_block_5f614(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s3, 0(s3)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f618:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f618\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f464\n");
    __builtin_unreachable();
}

/* Original0x5F61A..0x5F626. */
REGION void tsl9_resident_task_parser_block_5f61a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 212(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f622:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_parser_edge_5f622\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f468\n");
    __builtin_unreachable();
}

/* Original0x5F626..0x5F634. */
REGION void tsl9_resident_task_parser_block_5f626(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 213(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f630:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task_parser_edge_5f630\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f468\n");
    __builtin_unreachable();
}

/* Original0x5F634..0x5F646. */
REGION void tsl9_resident_task_parser_block_5f634(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 86\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 214\n.option pop\n");
    PORT(".Lresident_task_parser_literal_5f63e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_parser_literal_5f63e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F646..0x5F64C. */
REGION void tsl9_resident_task_parser_block_5f646(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f648:\n.option push\n.option norvc\nbne a0,a5,.Lresident_task_parser_edge_5f648\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f468\n");
    __builtin_unreachable();
}

/* Original0x5F64C..0x5F65A. */
REGION void tsl9_resident_task_parser_block_5f64c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 209(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a0, 210(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 224(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f658:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f658\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f59c\n");
    __builtin_unreachable();
}

/* Original0x5F65A..0x5F66C. */
REGION void tsl9_resident_task_parser_block_5f65a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nand s3, s3, a0\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    a0 = UINT32_C(0x0000012c); LIVE;
    PORT(".option push\n.option norvc\nmul s3, s3, a0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f66a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f66a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f672\n");
    __builtin_unreachable();
}

/* Original0x5F66C..0x5F672. */
REGION void tsl9_resident_task_parser_block_5f66c(void)
{
    REGS;
    a5 = UINT32_C(0x00258000); LIVE;
    PORT(".option push\n.option rvc\nadd s3, s3, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F672..0x5F67E. */
REGION void tsl9_resident_task_parser_block_5f672(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 37(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f67a:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_parser_edge_5f67a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f826\n");
    __builtin_unreachable();
}

/* Original0x5F67E..0x5F68E. */
REGION void tsl9_resident_task_parser_block_5f67e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_parser_edge_5f68a:\n.option push\n.option norvc\nbeqz a4,.Lresident_task_parser_edge_5f68a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f81e\n");
    __builtin_unreachable();
}

/* Original0x5F68E..0x5F694. */
REGION void tsl9_resident_task_parser_block_5f68e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x000000d7); LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x5F694..0x5F6A8. */
REGION void tsl9_resident_task_parser_block_5f694(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s3, s3, a5\n.option pop\n");
    a5 = UINT32_C(0x004b0000); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s3, -300\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffda7); LIVE;
    PORT(".Lresident_task_parser_edge_5f6a4:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task_parser_edge_5f6a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f470\n");
    __builtin_unreachable();
}

/* Original0x5F6A8..0x5F6CE. */
REGION void tsl9_resident_task_parser_block_5f6a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s8, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s7, s8, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 8(s7)\n.option pop\n");
    a2 = UINT32_C(0x000f4000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, a0, s3\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 128(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, a0, s3\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f6ca:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f6ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5F6CE..0x5F6D8. */
REGION void tsl9_resident_task_parser_block_5f6ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 564(s8)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F6D8..0x5F6F0. */
REGION void tsl9_resident_task_parser_block_5f6d8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nadd a5, a0, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, a5, a0\n.option pop\n");
    a0 = a0 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 4(s7)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s8, s8, 564\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f6ee:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task_parser_edge_5f6ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f6f4\n");
    __builtin_unreachable();
}

/* Original0x5F6F0..0x5F6F4. */
REGION void tsl9_resident_task_parser_block_5f6f0(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f6f0:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_task_parser_edge_5f6f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f6f8\n");
    __builtin_unreachable();
}

/* Original0x5F6F4..0x5F6F8. */
REGION void tsl9_resident_task_parser_block_5f6f4(void)
{
    REGS;
    a4 = a5 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x5F6F8..0x5F70A. */
REGION void tsl9_resident_task_parser_block_5f6f8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option norvc\nsw a4, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s11, 0xf4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F70A..0x5F750. */
REGION void tsl9_resident_task_parser_block_5f70a(void)
{
    REGS;
    a4 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option norvc\ndiv s7, s3, a4\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000500)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nlhu a0, 10(s8)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s11, s11, 576\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = a0 + UINT32_C(0x000001f4); LIVE;
    PORT(".option push\n.option norvc\nlbu s6, 515(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s10, 8(s8)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s10\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a0, s11, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s9, s7, a4\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s9, s9, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s6, s11\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli s6, s6, 0x1\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f74c:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f74c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5F750..0x5F780. */
REGION void tsl9_resident_task_parser_block_5f750(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a5, s10, s7\n.option pop\n");
    PORT(".option push\n.option norvc\nli s7, 800\n.option pop\n");
    a4 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s9\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s10\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nremu a5, a5, s7\n.option pop\n");
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, s10\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nadd s7, a0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s6, s11\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f77c:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f77c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5F780..0x5F786. */
REGION void tsl9_resident_task_parser_block_5f780(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a0, a0, s7\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f782:\n.option push\n.option norvc\nbleu s3,a0,.Lresident_task_parser_edge_5f782\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f836\n");
    __builtin_unreachable();
}

/* Original0x5F786..0x5F78C. */
REGION void tsl9_resident_task_parser_block_5f786(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s7, 172(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, s6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F78C..0x5F7AA. */
REGION void tsl9_resident_task_parser_block_5f78c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 172(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s6, 160(s0)\n.option pop\n");
    a2 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, s10, a0\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s10, a0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f7a6:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f7a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5F7AA..0x5F7AE. */
REGION void tsl9_resident_task_parser_block_5f7aa(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f7aa:\n.option push\n.option norvc\nbltu s6,a0,.Lresident_task_parser_edge_5f7aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f854\n");
    __builtin_unreachable();
}

/* Original0x5F7AE..0x5F7C2. */
REGION void tsl9_resident_task_parser_block_5f7ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s6, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a0, 164(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 125(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_parser_edge_5f7be:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_task_parser_edge_5f7be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f7c6\n");
    __builtin_unreachable();
}

/* Original0x5F7C2..0x5F7C6. */
REGION void tsl9_resident_task_parser_block_5f7c2(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f7c2:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f7c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x5F7C6..0x5F7D6. */
REGION void tsl9_resident_task_parser_block_5f7c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a2, 164(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000448)); LIVE;
    PORT(".Lresident_task_parser_edge_5f7d2:\n.option push\n.option norvc\nbltu a2,s3,.Lresident_task_parser_edge_5f7d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f85c\n");
    __builtin_unreachable();
}

/* Original0x5F7D6..0x5F802. */
REGION void tsl9_resident_task_parser_block_5f7d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 220(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 8(s8)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a2, a2, s3\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\naddi a3, s0, 125\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a4, a5, a4\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f7fe:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f7fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43414\n");
    __builtin_unreachable();
}

/* Original0x5F802..0x5F80E. */
REGION void tsl9_resident_task_parser_block_5f802(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 125(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_parser_edge_5f80a:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_parser_edge_5f80a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f470\n");
    __builtin_unreachable();
}

/* Original0x5F80E..0x5F81E. */
REGION void tsl9_resident_task_parser_block_5f80e(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 146(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 28(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f81c:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f81c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f470\n");
    __builtin_unreachable();
}

/* Original0x5F81E..0x5F822. */
REGION void tsl9_resident_task_parser_block_5f81e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000004a); LIVE;
    __builtin_unreachable();
}

/* Original0x5F822..0x5F826. */
REGION void tsl9_resident_task_parser_block_5f822(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_parser_edge_5f824:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f824\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f694\n");
    __builtin_unreachable();
}

/* Original0x5F826..0x5F82C. */
REGION void tsl9_resident_task_parser_block_5f826(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f828:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_parser_edge_5f828\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f832\n");
    __builtin_unreachable();
}

/* Original0x5F82C..0x5F832. */
REGION void tsl9_resident_task_parser_block_5f82c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000b); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_parser_edge_5f830:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f830\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f694\n");
    __builtin_unreachable();
}

/* Original0x5F832..0x5F836. */
REGION void tsl9_resident_task_parser_block_5f832(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_task_parser_edge_5f834:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f834\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f822\n");
    __builtin_unreachable();
}

/* Original0x5F836..0x5F848. */
REGION void tsl9_resident_task_parser_block_5f836(void)
{
    REGS;
    a0 = UINT32_C(0x003d1000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s10\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0xfffff900); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_parser_edge_5f844:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f844\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5F848..0x5F854. */
REGION void tsl9_resident_task_parser_block_5f848(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a0, 172(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 3\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f852:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f852\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f78c\n");
    __builtin_unreachable();
}

/* Original0x5F854..0x5F85C. */
REGION void tsl9_resident_task_parser_block_5f854(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s8)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s6, s6, a5\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f85a:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f85a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f7ae\n");
    __builtin_unreachable();
}

/* Original0x5F85C..0x5F864. */
REGION void tsl9_resident_task_parser_block_5f85c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s8)\n.option pop\n");
    a2 = a2 + a5; LIVE;
    PORT(".Lresident_task_parser_edge_5f862:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f862\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f7d6\n");
    __builtin_unreachable();
}

/* Original0x5F864..0x5F86A. */
REGION void tsl9_resident_task_parser_block_5f864(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 62(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f868:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f868\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f478\n");
    __builtin_unreachable();
}

/* Original0x5F86A..0x5F870. */
REGION void tsl9_resident_task_parser_block_5f86a(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_parser_edge_5f86c:\n.option push\n.option norvc\nbne s5,a5,.Lresident_task_parser_edge_5f86c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f884\n");
    __builtin_unreachable();
}

/* Original0x5F870..0x5F876. */
REGION void tsl9_resident_task_parser_block_5f870(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x347c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f874:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f874\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f884\n");
    __builtin_unreachable();
}

/* Original0x5F876..0x5F87C. */
REGION void tsl9_resident_task_parser_block_5f876(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 84(s0)\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f87a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f87a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f884\n");
    __builtin_unreachable();
}

/* Original0x5F87C..0x5F880. */
REGION void tsl9_resident_task_parser_block_5f87c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f87e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_parser_edge_5f87e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f93a\n");
    __builtin_unreachable();
}

/* Original0x5F880..0x5F884. */
REGION void tsl9_resident_task_parser_block_5f880(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F884..0x5F888. */
REGION void tsl9_resident_task_parser_block_5f884(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f884:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f884\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x5F888..0x5F88E. */
REGION void tsl9_resident_task_parser_block_5f888(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f88a:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f88a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x5F88E..0x5F89A. */
REGION void tsl9_resident_task_parser_block_5f88e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task_parser_edge_5f896:\n.option push\n.option norvc\nbeqz a5,.Lresident_task_parser_edge_5f896\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f51c\n");
    __builtin_unreachable();
}

/* Original0x5F89A..0x5F8A8. */
REGION void tsl9_resident_task_parser_block_5f89a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307e\n.option pop\n");
    a1 = UINT32_C(0x0000001e); LIVE;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f8a4:\n.option push\n.option norvc\nbgez a4,.Lresident_task_parser_edge_5f8a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f8b0\n");
    __builtin_unreachable();
}

/* Original0x5F8A8..0x5F8B0. */
REGION void tsl9_resident_task_parser_block_5f8a8(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000013); LIVE;
    a5 = a5 >> UINT32_C(0x00000013); LIVE;
    a1 = UINT32_C(0x0000012c); LIVE;
    __builtin_unreachable();
}

/* Original0x5F8B0..0x5F8C0. */
REGION void tsl9_resident_task_parser_block_5f8b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 37(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000002); LIVE;
    a1 = a5 * a1; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f8bc:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_parser_edge_5f8bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f950\n");
    __builtin_unreachable();
}

/* Original0x5F8C0..0x5F8CE. */
REGION void tsl9_resident_task_parser_block_5f8c0(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_parser_edge_5f8cc:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_parser_edge_5f8cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_parser_block_5f942\n");
    __builtin_unreachable();
}

/* Original0x5F8CE..0x5F8DA. */
REGION void tsl9_resident_task_parser_block_5f8ce(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x000000d7); LIVE;
    a2 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a1 - a2; LIVE;
    __builtin_unreachable();
}

/* Original0x5F8DA..0x5F8EE. */
REGION void tsl9_resident_task_parser_block_5f8da(void)
{
    REGS;
    a3 = UINT32_C(0x004b0000); LIVE;
    a2 = a5 + UINT32_C(0xfffffed4); LIVE;
    a3 = a3 + UINT32_C(0xfffffda8); LIVE;
    a4 = UINT32_C(0x00000021); LIVE;
    PORT(".Lresident_task_parser_edge_5f8ea:\n.option push\n.option norvc\nbltu a3,a2,.Lresident_task_parser_edge_5f8ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f304\n");
    __builtin_unreachable();
}

/* Original0x5F8EE..0x5F8F6. */
REGION void tsl9_resident_task_parser_block_5f8ee(void)
{
    REGS;
    a4 = UINT32_C(0x00000640); LIVE;
    PORT(".Lresident_task_parser_edge_5f8f2:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task_parser_edge_5f8f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f51c\n");
    __builtin_unreachable();
}

/* Original0x5F8F6..0x5F93A. */
REGION void tsl9_resident_task_parser_block_5f8f6(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a3 = UINT32_C(0x00002000); LIVE;
    a1 = UINT32_C(0xffffff80); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = a3 + UINT32_C(0x00000514); LIVE;
    a5 = a5 + UINT32_C(0xfffffed5); LIVE;
    /* Conditional Xwchc: qk.c.sb a1, 4(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa2cc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    a5 = UINT32_C(0xffffffa5); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 46(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5e\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f938:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f938\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f51c\n");
    __builtin_unreachable();
}

/* Original0x5F93A..0x5F940. */
REGION void tsl9_resident_task_parser_block_5f93a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_parser_edge_5f93c:\n.option push\n.option norvc\njal ra,.Lresident_task_parser_edge_5f93c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ee06\n");
    __builtin_unreachable();
}

/* Original0x5F940..0x5F942. */
REGION void tsl9_resident_task_parser_block_5f940(void)
{
    REGS;
    PORT(".Lresident_task_parser_edge_5f940:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f940\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f51c\n");
    __builtin_unreachable();
}

/* Original0x5F942..0x5F950. */
REGION void tsl9_resident_task_parser_block_5f942(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000004a); LIVE;
    a3 = a5 << UINT32_C(0x00000003); LIVE;
    a5 = a1 - a3; LIVE;
    PORT(".Lresident_task_parser_edge_5f94e:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f94e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f8da\n");
    __builtin_unreachable();
}

/* Original0x5F950..0x5F956. */
REGION void tsl9_resident_task_parser_block_5f950(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_parser_edge_5f952:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_parser_edge_5f952\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_parser_block_5f962\n");
    __builtin_unreachable();
}

/* Original0x5F956..0x5F962. */
REGION void tsl9_resident_task_parser_block_5f956(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000b); LIVE;
    a4 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a1 - a4; LIVE;
    PORT(".Lresident_task_parser_edge_5f960:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f960\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f8da\n");
    __builtin_unreachable();
}

/* Original0x5F962..0x5F96C. */
REGION void tsl9_resident_task_parser_block_5f962(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    a5 = a1 - a5; LIVE;
    PORT(".Lresident_task_parser_edge_5f96a:\n.option push\n.option rvc\nc.j .Lresident_task_parser_edge_5f96a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_parser_block_5f8da\n");
    __builtin_unreachable();
}
