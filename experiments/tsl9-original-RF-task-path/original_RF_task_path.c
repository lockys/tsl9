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

/* Seven complete required RF task/callback bodies:1586B/576i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43B28..0x43B2E. */
REGION void tsl9_candidate_external_flash_43b28(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_task_path_edge_43b2a:\n.option push\n.option norvc\nbltu a5,a1,.Loriginal_RF_task_path_edge_43b2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_43b3c\n");
    __builtin_unreachable();
}

/* Original0x43B2E..0x43B3C. */
REGION void tsl9_original_RF_task_path_block_43b2e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = a1 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + UINT32_C(0x000001c8); LIVE;
    a1 = a1 + a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x43B3C..0x43B3E. */
REGION void tsl9_original_RF_task_path_block_43b3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43EDC..0x43EE8. */
REGION void tsl9_candidate_external_flash_43edc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x000001ec); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    PORT(".Loriginal_RF_task_path_edge_43ee6:\n.option push\n.option rvc\nc.beqz a4,.Loriginal_RF_task_path_edge_43ee6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_43f44\n");
    __builtin_unreachable();
}

/* Original0x43EE8..0x43EF8. */
REGION void tsl9_original_RF_task_path_block_43ee8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, a5, 492\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43EF8..0x43F0A. */
REGION void tsl9_original_RF_task_path_block_43ef8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x0000019c); LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 8(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x271a\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a5, 412\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_43f08:\n.option push\n.option rvc\nc.beqz a4,.Loriginal_RF_task_path_edge_43f08\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_43f38\n");
    __builtin_unreachable();
}

/* Original0x43F0A..0x43F10. */
REGION void tsl9_original_RF_task_path_block_43f0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_43f0c:\n.option push\n.option norvc\nbleu a0,a4,.Loriginal_RF_task_path_edge_43f0c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_43f12\n");
    __builtin_unreachable();
}

/* Original0x43F10..0x43F12. */
REGION void tsl9_original_RF_task_path_block_43f10(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F12..0x43F1C. */
REGION void tsl9_original_RF_task_path_block_43f12(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_43f18:\n.option push\n.option norvc\nbleu a4,s0,.Loriginal_RF_task_path_edge_43f18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_43f1e\n");
    __builtin_unreachable();
}

/* Original0x43F1C..0x43F1E. */
REGION void tsl9_original_RF_task_path_block_43f1c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F1E..0x43F2A. */
REGION void tsl9_original_RF_task_path_block_43f1e(void)
{
    REGS;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 - a3; LIVE;
    a4 = UINT32_C(0x00000014); LIVE;
    PORT(".Loriginal_RF_task_path_edge_43f26:\n.option push\n.option norvc\nble a5,a4,.Loriginal_RF_task_path_edge_43f26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_43f38\n");
    __builtin_unreachable();
}

/* Original0x43F2A..0x43F30. */
REGION void tsl9_original_RF_task_path_block_43f2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 48(s2)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_43f2e:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_43f2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_43f32\n");
    __builtin_unreachable();
}

/* Original0x43F30..0x43F32. */
REGION void tsl9_original_RF_task_path_block_43f30(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F32..0x43F36. */
REGION void tsl9_original_RF_task_path_block_43f32(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_43f32:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_43f32\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_common_reset_641b0\n");
    __builtin_unreachable();
}

/* Original0x43F36..0x43F38. */
REGION void tsl9_original_RF_task_path_block_43f36(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh s0, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa482\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F38..0x43F44. */
REGION void tsl9_original_RF_task_path_block_43f38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F44..0x43F46. */
REGION void tsl9_original_RF_task_path_block_43f44(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64794..0x647B6. */
REGION void tsl9_candidate_external_flash_64794(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 36(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv s7, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, a2\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_647b2:\n.option push\n.option norvc\nbne a2,a5,.Loriginal_RF_task_path_edge_647b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_647e4\n");
    __builtin_unreachable();
}

/* Original0x647B6..0x647C0. */
REGION void tsl9_original_RF_task_path_block_647b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 15\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1344\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x647C0..0x647C8. */
REGION void tsl9_original_RF_task_path_block_647c0(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_literal_647c0:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002d4c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_647c0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x647C8..0x647CC. */
REGION void tsl9_original_RF_task_path_block_647c8(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_647c8:\n.option push\n.option norvc\nbleu a0,s2,.Loriginal_RF_task_path_edge_647c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_647c0\n");
    __builtin_unreachable();
}

/* Original0x647CC..0x647D6. */
REGION void tsl9_original_RF_task_path_block_647cc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c3c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 + UINT32_C(0xfffffff0); LIVE;
    PORT(".Loriginal_RF_task_path_edge_647d2:\n.option push\n.option norvc\nbltu a5,a0,.Loriginal_RF_task_path_edge_647d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_647c0\n");
    __builtin_unreachable();
}

/* Original0x647D6..0x647E4. */
REGION void tsl9_original_RF_task_path_block_647d6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0x000000a0); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x647E4..0x6480E. */
REGION void tsl9_original_RF_task_path_block_647e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s5, 1344\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3008\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6480a:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_6480a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_6434a\n");
    __builtin_unreachable();
}

/* Original0x6480E..0x64878. */
REGION void tsl9_original_RF_task_path_block_6480e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s4)\n.option pop\n");
    a2 = UINT32_C(0x00330000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1340(s3)\n.option pop\n");
    a3 = UINT32_C(0x0000005a); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000050)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option rvc\nlw a3, 8(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option rvc\nlw a3, 12(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\naddi a4, s2, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 14(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x277c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 1376\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa77c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s6, -1\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_64874:\n.option push\n.option norvc\nbltu a4,a5,.Loriginal_RF_task_path_edge_64874\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_64920\n");
    __builtin_unreachable();
}

/* Original0x64878..0x6488E. */
REGION void tsl9_original_RF_task_path_block_64878(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 32(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s7\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s6, 0(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb104\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_task_path_literal_64886:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_64886\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6488E..0x648B0. */
REGION void tsl9_original_RF_task_path_block_6488e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 32(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a1, s1, 0x10\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb078\n.option pop\n");
    a4 = UINT32_C(0x00000080); LIVE;
    PORT(".Loriginal_RF_task_path_edge_648ac:\n.option push\n.option norvc\nbne s6,a4,.Loriginal_RF_task_path_edge_648ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_6493a\n");
    __builtin_unreachable();
}

/* Original0x648B0..0x648B4. */
REGION void tsl9_original_RF_task_path_block_648b0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_task_path_edge_648b2:\n.option push\n.option rvc\nc.bnez a4,.Loriginal_RF_task_path_edge_648b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_648b0\n");
    __builtin_unreachable();
}

/* Original0x648B4..0x648C0. */
REGION void tsl9_original_RF_task_path_block_648b4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x648C0..0x648CA. */
REGION void tsl9_original_RF_task_path_block_648c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 8(s2)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Loriginal_RF_task_path_edge_648c6:\n.option push\n.option norvc\nbltu a0,a4,.Loriginal_RF_task_path_edge_648c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_6492c\n");
    __builtin_unreachable();
}

/* Original0x648CA..0x648CC. */
REGION void tsl9_original_RF_task_path_block_648ca(void)
{
    REGS;
    a0 = a0 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x648CC..0x648EA. */
REGION void tsl9_original_RF_task_path_block_648cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 32(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x800\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s1, 767\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a0 = a0 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_edge_648e6:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_648e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x648EA..0x6490A. */
REGION void tsl9_original_RF_task_path_block_648ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s4)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nor a4, a4, s1\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x6490A..0x64920. */
REGION void tsl9_original_RF_task_path_block_6490a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64920..0x64928. */
REGION void tsl9_original_RF_task_path_block_64920(void)
{
    REGS;
    a5 = UINT32_C(0x00000080); LIVE;
    PORT(".Loriginal_RF_task_path_edge_64924:\n.option push\n.option norvc\nbne s6,a5,.Loriginal_RF_task_path_edge_64924\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_6488e\n");
    __builtin_unreachable();
}

/* Original0x64928..0x6492C. */
REGION void tsl9_original_RF_task_path_block_64928(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6492a:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_6492a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_6488e\n");
    __builtin_unreachable();
}

/* Original0x6492C..0x6493A. */
REGION void tsl9_original_RF_task_path_block_6492c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 - a4; LIVE;
    a0 = a0 + a5; LIVE;
    PORT(".Loriginal_RF_task_path_edge_64938:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_64938\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_648cc\n");
    __builtin_unreachable();
}

/* Original0x6493A..0x64946. */
REGION void tsl9_original_RF_task_path_block_6493a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_edge_64942:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_64942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x64946..0x6496A. */
REGION void tsl9_original_RF_task_path_block_64946(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00800000); LIVE;
    a0 = UINT32_C(0x00066000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = a0 + UINT32_C(0xfffffde6); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".Loriginal_RF_task_path_literal_64962:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_64962\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6496A..0x6497E. */
REGION void tsl9_original_RF_task_path_block_6496a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 12(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x6497E..0x64988. */
REGION void tsl9_original_RF_task_path_block_6497e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 12(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Loriginal_RF_task_path_edge_64986:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_64986\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_6497e\n");
    __builtin_unreachable();
}

/* Original0x64988..0x6498A. */
REGION void tsl9_original_RF_task_path_block_64988(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_64988:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_64988\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_6490a\n");
    __builtin_unreachable();
}

/* Original0x6575A..0x6576C. */
REGION void tsl9_candidate_external_flash_6575a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65768:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65768\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_Shut_656c6\n");
    __builtin_unreachable();
}

/* Original0x6576C..0x65792. */
REGION void tsl9_original_RF_task_path_block_6576c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s1, 1376\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 15(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1344\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 16(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 20(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a5, 8(s0)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6578e:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_6578e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x65792..0x6579C. */
REGION void tsl9_original_RF_task_path_block_65792(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 16(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65798:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65798\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x6579C..0x657A4. */
REGION void tsl9_original_RF_task_path_block_6579c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 12(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_task_path_edge_657a2:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_657a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_657c6\n");
    __builtin_unreachable();
}

/* Original0x657A4..0x657AE. */
REGION void tsl9_original_RF_task_path_block_657a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 16(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000022); LIVE;
    __builtin_unreachable();
}

/* Original0x657AE..0x657B0. */
REGION void tsl9_original_RF_task_path_block_657ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x657B0..0x657C6. */
REGION void tsl9_original_RF_task_path_block_657b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 12(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_657c2:\n.option push\n.option norvc\njal zero,.Loriginal_RF_task_path_edge_657c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43b28\n");
    __builtin_unreachable();
}

/* Original0x657C6..0x657CC. */
REGION void tsl9_original_RF_task_path_block_657c6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_task_path_edge_657ca:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_657ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_657b0\n");
    __builtin_unreachable();
}

/* Original0x657CC..0x657D8. */
REGION void tsl9_original_RF_task_path_block_657cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 16(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000024); LIVE;
    PORT(".Loriginal_RF_task_path_edge_657d6:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_657d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_657ae\n");
    __builtin_unreachable();
}

/* Original0x657D8..0x657FE. */
REGION void tsl9_candidate_external_flash_657d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s1, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x275c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_task_path_edge_657fa:\n.option push\n.option norvc\nbeqz a5,.Loriginal_RF_task_path_edge_657fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65908\n");
    __builtin_unreachable();
}

/* Original0x657FE..0x65812. */
REGION void tsl9_original_RF_task_path_block_657fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6580e:\n.option push\n.option norvc\nbne a3,a5,.Loriginal_RF_task_path_edge_6580e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65830\n");
    __builtin_unreachable();
}

/* Original0x65812..0x65816. */
REGION void tsl9_original_RF_task_path_block_65812(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2b08\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x65816..0x65830. */
REGION void tsl9_original_RF_task_path_block_65816(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6582c:\n.option push\n.option norvc\njal zero,.Loriginal_RF_task_path_edge_6582c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x65830..0x6583C. */
REGION void tsl9_original_RF_task_path_block_65830(void)
{
    REGS;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\nlui s4, 0xffffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65838:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65838\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63eda\n");
    __builtin_unreachable();
}

/* Original0x6583C..0x6584A. */
REGION void tsl9_original_RF_task_path_block_6583c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 8\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s4, s4, -1\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s7, 0x2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6584A..0x65858. */
REGION void tsl9_original_RF_task_path_block_6584a(void)
{
    REGS;
    a2 = UINT32_C(0x00000080); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nlui s5, 0x1\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65854:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65854\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_64794\n");
    __builtin_unreachable();
}

/* Original0x65858..0x65860. */
REGION void tsl9_original_RF_task_path_block_65858(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s8, -128\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, s5, -110\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65860..0x65866. */
REGION void tsl9_original_RF_task_path_block_65860(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65864:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_task_path_edge_65864\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_6588e\n");
    __builtin_unreachable();
}

/* Original0x65866..0x6586E. */
REGION void tsl9_original_RF_task_path_block_65866(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_task_path_edge_6586c:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_task_path_edge_6586c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_65860\n");
    __builtin_unreachable();
}

/* Original0x6586E..0x65874. */
REGION void tsl9_original_RF_task_path_block_6586e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s3, s3, -1\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65870:\n.option push\n.option norvc\nbnez s3,.Loriginal_RF_task_path_edge_65870\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_6584a\n");
    __builtin_unreachable();
}

/* Original0x65874..0x6588E. */
REGION void tsl9_original_RF_task_path_block_65874(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_6588a:\n.option push\n.option norvc\njal zero,.Loriginal_RF_task_path_edge_6588a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6575a\n");
    __builtin_unreachable();
}

/* Original0x6588E..0x658A4. */
REGION void tsl9_original_RF_task_path_block_6588e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s0)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_658a0:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_658a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x658A4..0x658BA. */
REGION void tsl9_original_RF_task_path_block_658a4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1344(s6)\n.option pop\n");
    a2 = UINT32_C(0x000000ff); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x4\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_literal_658b2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_work_mode_200026ba\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_658b2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x658BA..0x658C0. */
REGION void tsl9_original_RF_task_path_block_658ba(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x303c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_658be:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_658be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_658d6\n");
    __builtin_unreachable();
}

/* Original0x658C0..0x658C8. */
REGION void tsl9_original_RF_task_path_block_658c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_658c4:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_658c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x658C8..0x658D6. */
REGION void tsl9_original_RF_task_path_block_658c8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2888\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4dc\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_658d4:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_658d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_65816\n");
    __builtin_unreachable();
}

/* Original0x658D6..0x658DA. */
REGION void tsl9_original_RF_task_path_block_658d6(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_658d6:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_658d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x658DA..0x658FC. */
REGION void tsl9_original_RF_task_path_block_658da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nand a3, a4, s4\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s7, 8(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s8, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s5, 100(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x658FC..0x65904. */
REGION void tsl9_original_RF_task_path_block_658fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65902:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_65902\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_65866\n");
    __builtin_unreachable();
}

/* Original0x65904..0x65908. */
REGION void tsl9_original_RF_task_path_block_65904(void)
{
    REGS;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65906:\n.option push\n.option rvc\nc.j .Loriginal_RF_task_path_edge_65906\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_task_path_block_658fc\n");
    __builtin_unreachable();
}

/* Original0x65908..0x65920. */
REGION void tsl9_original_RF_task_path_block_65908(void)
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

/* Original0x65DE6..0x65E0C. */
REGION void tsl9_candidate_registered_callback_65de6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20bc\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s2, 1376\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65e08:\n.option push\n.option norvc\nbeqz a5,.Loriginal_RF_task_path_edge_65e08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65E0C..0x65E26. */
REGION void tsl9_original_RF_task_path_block_65e0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 1344(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65e22:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65e22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x65E26..0x65E3C. */
REGION void tsl9_original_RF_task_path_block_65e26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1344(s3)\n.option pop\n");
    a2 = UINT32_C(0x000000ff); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x4\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_literal_65e34:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_work_mode_200026ba\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_65e34\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65E3C..0x65E44. */
REGION void tsl9_original_RF_task_path_block_65e3c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65e40:\n.option push\n.option norvc\nbeqz a5,.Loriginal_RF_task_path_edge_65e40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65E44..0x65E5C. */
REGION void tsl9_original_RF_task_path_block_65e44(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 36(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 3(s1)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_literal_65e54:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_65e54\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65E5C..0x65E62. */
REGION void tsl9_original_RF_task_path_block_65e5c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s4, a0\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65e5e:\n.option push\n.option norvc\nbnez a0,.Loriginal_RF_task_path_edge_65e5e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65E62..0x65E6C. */
REGION void tsl9_original_RF_task_path_block_65e62(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 36(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2038\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65e68:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_task_path_edge_65e68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65E6C..0x65E82. */
REGION void tsl9_original_RF_task_path_block_65e6c(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000204); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 9\n.option pop\n");
    PORT(".Loriginal_RF_task_path_literal_65e7a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_65e7a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65E82..0x65E88. */
REGION void tsl9_original_RF_task_path_block_65e82(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65e84:\n.option push\n.option norvc\nbne a0,a5,.Loriginal_RF_task_path_edge_65e84\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65E88..0x65E9C. */
REGION void tsl9_original_RF_task_path_block_65e88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 32(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65e98:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65e98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x65E9C..0x65EB0. */
REGION void tsl9_original_RF_task_path_block_65e9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1344(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x4\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_task_path_literal_65ea8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_work_mode_200026ba\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_65ea8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65EB0..0x65EB6. */
REGION void tsl9_original_RF_task_path_block_65eb0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65eb4:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_task_path_edge_65eb4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_65f7a\n");
    __builtin_unreachable();
}

/* Original0x65EB6..0x65EC4. */
REGION void tsl9_original_RF_task_path_block_65eb6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65EC4..0x65ECC. */
REGION void tsl9_original_RF_task_path_block_65ec4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 8(s2)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65ec8:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65ec8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_Shut_656c6\n");
    __builtin_unreachable();
}

/* Original0x65ECC..0x65F20. */
REGION void tsl9_original_RF_task_path_block_65ecc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x383c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s3, 1344\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)) = (uint8_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 25(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xbf1c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x285c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 13(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 26(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xaf3c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x385c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 1344\n.option pop\n");
    a1 = UINT32_C(0x00000020); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 27(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xbf3c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2814\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x347c\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000008); LIVE;
    a3 = a3 | a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a3 = a3 | a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 18(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x283c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3874\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 22(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x287c\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000008); LIVE;
    a3 = a3 | a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 24(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c1c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a3 = a3 | a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c1c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 17(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000014)) = (uint32_t)a5; LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x65F20..0x65F28. */
REGION void tsl9_original_RF_task_path_block_65f20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrl a3, a5, a4\n.option pop\n");
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65f26:\n.option push\n.option rvc\nc.beqz a3,.Loriginal_RF_task_path_edge_65f26\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_65f30\n");
    __builtin_unreachable();
}

/* Original0x65F28..0x65F30. */
REGION void tsl9_original_RF_task_path_block_65f28(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s4, s4, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s4, s4, 255\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x65F30..0x65F36. */
REGION void tsl9_original_RF_task_path_block_65f30(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_65f32:\n.option push\n.option norvc\nbne a4,a1,.Loriginal_RF_task_path_edge_65f32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_65f20\n");
    __builtin_unreachable();
}

/* Original0x65F36..0x65F38. */
REGION void tsl9_original_RF_task_path_block_65f36(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_65f36:\n.option push\n.option rvc\nc.beqz a2,.Loriginal_RF_task_path_edge_65f36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_65f3c\n");
    __builtin_unreachable();
}

/* Original0x65F38..0x65F3C. */
REGION void tsl9_original_RF_task_path_block_65f38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s4, 17(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65F3C..0x65F5E. */
REGION void tsl9_original_RF_task_path_block_65f3c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c3c\n.option pop\n");
    a0 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 24(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    a0 = a0 + UINT32_C(0x0000057c); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 12(s2)\n.option pop\n");
    PORT(".Loriginal_RF_task_path_literal_65f56:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_task_path_literal_65f56\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65F5E..0x65F7A. */
REGION void tsl9_original_RF_task_path_block_65f5e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 16(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000028); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_65f76:\n.option push\n.option norvc\njal zero,.Loriginal_RF_task_path_edge_65f76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x65F7A..0x65F7E. */
REGION void tsl9_original_RF_task_path_block_65f7a(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_65f7a:\n.option push\n.option norvc\njal ra,.Loriginal_RF_task_path_edge_65f7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x65F7E..0x65F94. */
REGION void tsl9_original_RF_task_path_block_65f7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 12(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000442..0x20000454. */
REGION void tsl9_candidate_external_ram_20000442(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_20000452:\n.option push\n.option rvc\nc.beqz a0,.Loriginal_RF_task_path_edge_20000452\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_2000045a\n");
    __builtin_unreachable();
}

/* Original0x20000454..0x20000456. */
REGION void tsl9_original_RF_task_path_block_20000454(void)
{
    REGS;
    PORT(".Loriginal_RF_task_path_edge_20000454:\n.option push\n.option rvc\nc.beqz a1,.Loriginal_RF_task_path_edge_20000454\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_2000045a\n");
    __builtin_unreachable();
}

/* Original0x20000456..0x2000045A. */
REGION void tsl9_original_RF_task_path_block_20000456(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Loriginal_RF_task_path_edge_20000458:\n.option push\n.option rvc\nc.bnez a2,.Loriginal_RF_task_path_edge_20000458\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_task_path_block_2000046c\n");
    __builtin_unreachable();
}

/* Original0x2000045A..0x20000466. */
REGION void tsl9_original_RF_task_path_block_2000045a(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a4; LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000466..0x2000046C. */
REGION void tsl9_original_RF_task_path_block_20000466(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_task_path_edge_20000468:\n.option push\n.option norvc\nbeq a2,a5,.Loriginal_RF_task_path_edge_20000468\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_2000045a\n");
    __builtin_unreachable();
}

/* Original0x2000046C..0x2000047E. */
REGION void tsl9_original_RF_task_path_block_2000046c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a6, a0, a5\n.option pop\n");
    a3 = a1 + a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a6, 0(a6)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 0(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x2294\n.option pop\n");
    PORT(".Loriginal_RF_task_path_edge_2000047a:\n.option push\n.option norvc\nbeq a6,a3,.Loriginal_RF_task_path_edge_2000047a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_task_path_block_20000466\n");
    __builtin_unreachable();
}

/* Original0x2000047E..0x2000048A. */
REGION void tsl9_original_RF_task_path_block_2000047e(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a4; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
