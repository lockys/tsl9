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

/* Three complete conditional completion-chain bodies:3204B/1011i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x567BE..0x567DE. */
REGION void tsl9_candidate_unprovided_flash_567be(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e8)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 564\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_567dc:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_567dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5685a\n");
    __builtin_unreachable();
}

/* Original0x567DE..0x567EE. */
REGION void tsl9_resident_completion_chain_block_567de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s3, a5\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000046c)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_567ea:\n.option push\n.option norvc\nbne a4,a5,.Lresident_completion_chain_edge_567ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5685a\n");
    __builtin_unreachable();
}

/* Original0x567EE..0x56812. */
REGION void tsl9_resident_completion_chain_block_567ee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s0, 134(s2)\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000090)); LIVE;
    PORT(".option push\n.option norvc\nmul s0, s0, a5\n.option pop\n");
    a5 = UINT32_C(0x000f4000); LIVE;
    a4 = a5 + UINT32_C(0x0000023f); LIVE;
    a5 = a5 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option rvc\nadd s0, s0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s0, s0, a5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5680e:\n.option push\n.option norvc\nbltu a0,s0,.Lresident_completion_chain_edge_5680e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5689e\n");
    __builtin_unreachable();
}

/* Original0x56812..0x56820. */
REGION void tsl9_resident_completion_chain_block_56812(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option norvc\nsub s0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56820..0x56824. */
REGION void tsl9_resident_completion_chain_block_56820(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_56820:\n.option push\n.option norvc\nbltu s0,a0,.Lresident_completion_chain_edge_56820\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_568a4\n");
    __builtin_unreachable();
}

/* Original0x56824..0x56828. */
REGION void tsl9_resident_completion_chain_block_56824(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a5, s0, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56828..0x5683C. */
REGION void tsl9_resident_completion_chain_block_56828(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu s0, 515(a4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 1256(s3)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nc.srli s0,0x1\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56838:\n.option push\n.option norvc\nbleu a5,s0,.Lresident_completion_chain_edge_56838\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56858\n");
    __builtin_unreachable();
}

/* Original0x5683C..0x56858. */
REGION void tsl9_resident_completion_chain_block_5683c(void)
{
    REGS;
    a0 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option norvc\nsub s0, a5, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, s0, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2492\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s0, a0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56854:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56854\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x56858..0x5685A. */
REGION void tsl9_resident_completion_chain_block_56858(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr s3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5685A..0x56866. */
REGION void tsl9_resident_completion_chain_block_5685a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffb0); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 14(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56864:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_56864\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_568b4\n");
    __builtin_unreachable();
}

/* Original0x56866..0x56870. */
REGION void tsl9_resident_completion_chain_block_56866(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_completion_chain_literal_56868:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_completion_chain_literal_56868\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56870..0x56884. */
REGION void tsl9_resident_completion_chain_block_56870(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000045c)) = (uint32_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004ec)); LIVE;
    PORT(".Lresident_completion_chain_edge_56880:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56880\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43ed2\n");
    __builtin_unreachable();
}

/* Original0x56884..0x5689E. */
REGION void tsl9_resident_completion_chain_block_56884(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0xe000e000); LIVE;
    a4 = UINT32_C(0x02000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000204)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5689E..0x568A4. */
REGION void tsl9_resident_completion_chain_block_5689e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    a0 = a0 + a5; LIVE;
    PORT(".Lresident_completion_chain_edge_568a2:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_568a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_56812\n");
    __builtin_unreachable();
}

/* Original0x568A4..0x568AE. */
REGION void tsl9_resident_completion_chain_block_568a4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a4, a0, s0\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_completion_chain_edge_568aa:\n.option push\n.option norvc\nbgez a4,.Lresident_completion_chain_edge_568aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56828\n");
    __builtin_unreachable();
}

/* Original0x568AE..0x568B4. */
REGION void tsl9_resident_completion_chain_block_568ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_568b2:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_568b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_56824\n");
    __builtin_unreachable();
}

/* Original0x568B4..0x568D4. */
REGION void tsl9_resident_completion_chain_block_568b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 41(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a1, a1, a5\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_568d0:\n.option push\n.option norvc\njal zero,.Lresident_completion_chain_edge_568d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x56D0E..0x56D28. */
REGION void tsl9_candidate_unprovided_flash_56d0e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56d24:\n.option push\n.option norvc\nbeqz a5,.Lresident_completion_chain_edge_56d24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_571c4\n");
    __builtin_unreachable();
}

/* Original0x56D28..0x56D2E. */
REGION void tsl9_resident_completion_chain_block_56d28(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_56d2c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56d2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56d40\n");
    __builtin_unreachable();
}

/* Original0x56D2E..0x56D40. */
REGION void tsl9_resident_completion_chain_block_56d2e(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a0, 8(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x250a\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56d3c:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56d3c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56D40..0x56D4A. */
REGION void tsl9_resident_completion_chain_block_56d40(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_completion_chain_edge_56d48:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56d48\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56de0\n");
    __builtin_unreachable();
}

/* Original0x56D4A..0x56D5A. */
REGION void tsl9_resident_completion_chain_block_56d4a(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_completion_chain_edge_56d58:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_56d58\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56d6c\n");
    __builtin_unreachable();
}

/* Original0x56D5A..0x56D6C. */
REGION void tsl9_resident_completion_chain_block_56d5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000400); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56d68:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56d68\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5605c\n");
    __builtin_unreachable();
}

/* Original0x56D6C..0x56D7A. */
REGION void tsl9_resident_completion_chain_block_56d6c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3438\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2850\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a3, 98(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56d76:\n.option push\n.option norvc\nbne a4,a5,.Lresident_completion_chain_edge_56d76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5755e\n");
    __builtin_unreachable();
}

/* Original0x56D7A..0x56DB2. */
REGION void tsl9_resident_completion_chain_block_56d7a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3e\n.option pop\n");
    a4 = UINT32_C(0x000004e2); LIVE;
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 148(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000202)); LIVE;
    a4 = a4 + UINT32_C(0x00000050); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 43(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 132(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 130(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56db0:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56db0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56db6\n");
    __builtin_unreachable();
}

/* Original0x56DB2..0x56DB6. */
REGION void tsl9_resident_completion_chain_block_56db2(void)
{
    REGS;
    a5 = UINT32_C(0x00000040); LIVE;
    __builtin_unreachable();
}

/* Original0x56DB6..0x56DBA. */
REGION void tsl9_resident_completion_chain_block_56db6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac5c\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56db8:\n.option push\n.option rvc\nc.bnez a2,.Lresident_completion_chain_edge_56db8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56dc6\n");
    __builtin_unreachable();
}

/* Original0x56DBA..0x56DC6. */
REGION void tsl9_resident_completion_chain_block_56dba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56DC6..0x56DC8. */
REGION void tsl9_resident_completion_chain_block_56dc6(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_56dc6:\n.option push\n.option rvc\nc.bnez a3,.Lresident_completion_chain_edge_56dc6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56dd4\n");
    __builtin_unreachable();
}

/* Original0x56DC8..0x56DD4. */
REGION void tsl9_resident_completion_chain_block_56dc8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56dd0:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56dd0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56DD4..0x56DD8. */
REGION void tsl9_resident_completion_chain_block_56dd4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 98(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56DD8..0x56DE0. */
REGION void tsl9_resident_completion_chain_block_56dd8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 20(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 29(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56DE0..0x56DEA. */
REGION void tsl9_resident_completion_chain_block_56de0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_completion_chain_edge_56de8:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56de8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e08\n");
    __builtin_unreachable();
}

/* Original0x56DEA..0x56DFC. */
REGION void tsl9_resident_completion_chain_block_56dea(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56df8:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56df8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56DFC..0x56E08. */
REGION void tsl9_resident_completion_chain_block_56dfc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56E08..0x56E12. */
REGION void tsl9_resident_completion_chain_block_56e08(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_56e10:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56e10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e5c\n");
    __builtin_unreachable();
}

/* Original0x56E12..0x56E22. */
REGION void tsl9_resident_completion_chain_block_56e12(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 77(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_completion_chain_edge_56e20:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_56e20\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e2a\n");
    __builtin_unreachable();
}

/* Original0x56E22..0x56E2A. */
REGION void tsl9_resident_completion_chain_block_56e22(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 77(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000030); LIVE;
    __builtin_unreachable();
}

/* Original0x56E2A..0x56E32. */
REGION void tsl9_resident_completion_chain_block_56e2a(void)
{
    REGS;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_completion_chain_edge_56e2e:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56e2e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56E32..0x56E38. */
REGION void tsl9_resident_completion_chain_block_56e32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56e36:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_56e36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e50\n");
    __builtin_unreachable();
}

/* Original0x56E38..0x56E40. */
REGION void tsl9_resident_completion_chain_block_56e38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 264(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_56e3e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_56e3e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e50\n");
    __builtin_unreachable();
}

/* Original0x56E40..0x56E50. */
REGION void tsl9_resident_completion_chain_block_56e40(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 74(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_56e4c:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56e4c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_55c6e\n");
    __builtin_unreachable();
}

/* Original0x56E50..0x56E5C. */
REGION void tsl9_resident_completion_chain_block_56e50(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56E5C..0x56E66. */
REGION void tsl9_resident_completion_chain_block_56e5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_completion_chain_edge_56e64:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56e64\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e94\n");
    __builtin_unreachable();
}

/* Original0x56E66..0x56E78. */
REGION void tsl9_resident_completion_chain_block_56e66(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 79(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffbf); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_completion_chain_edge_56e74:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_completion_chain_edge_56e74\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56e88\n");
    __builtin_unreachable();
}

/* Original0x56E78..0x56E7C. */
REGION void tsl9_resident_completion_chain_block_56e78(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x343c\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56e7a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_56e7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56e88\n");
    __builtin_unreachable();
}

/* Original0x56E7C..0x56E88. */
REGION void tsl9_resident_completion_chain_block_56e7c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56E88..0x56E94. */
REGION void tsl9_resident_completion_chain_block_56e88(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_completion_chain_edge_56e90:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56e90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56E94..0x56E9E. */
REGION void tsl9_resident_completion_chain_block_56e94(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_completion_chain_edge_56e9c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56e9c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56f48\n");
    __builtin_unreachable();
}

/* Original0x56E9E..0x56EB2. */
REGION void tsl9_resident_completion_chain_block_56e9e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3434\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 268(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 264(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56eb0:\n.option push\n.option rvc\nc.bnez a3,.Lresident_completion_chain_edge_56eb0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56ec6\n");
    __builtin_unreachable();
}

/* Original0x56EB2..0x56EB8. */
REGION void tsl9_resident_completion_chain_block_56eb2(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56eb6:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56eb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56ec6\n");
    __builtin_unreachable();
}

/* Original0x56EB8..0x56EC6. */
REGION void tsl9_resident_completion_chain_block_56eb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 164(s0)\n.option pop\n");
    a2 = UINT32_C(0x00400000); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".option push\n.option norvc\nsw a4, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56EC6..0x56ECE. */
REGION void tsl9_resident_completion_chain_block_56ec6(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_completion_chain_edge_56eca:\n.option push\n.option norvc\nbeqz a5,.Lresident_completion_chain_edge_56eca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57592\n");
    __builtin_unreachable();
}

/* Original0x56ECE..0x56ED0. */
REGION void tsl9_resident_completion_chain_block_56ece(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_56ece:\n.option push\n.option rvc\nc.bnez a3,.Lresident_completion_chain_edge_56ece\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56f30\n");
    __builtin_unreachable();
}

/* Original0x56ED0..0x56EDC. */
REGION void tsl9_resident_completion_chain_block_56ed0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 466(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 482(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56ed8:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_completion_chain_edge_56ed8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56f00\n");
    __builtin_unreachable();
}

/* Original0x56EDC..0x56EE6. */
REGION void tsl9_resident_completion_chain_block_56edc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 327(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_56ee2:\n.option push\n.option norvc\nbne a3,a4,.Lresident_completion_chain_edge_56ee2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57586\n");
    __builtin_unreachable();
}

/* Original0x56EE6..0x56EEC. */
REGION void tsl9_resident_completion_chain_block_56ee6(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffffa90); LIVE;
    __builtin_unreachable();
}

/* Original0x56EEC..0x56EF0. */
REGION void tsl9_resident_completion_chain_block_56eec(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_56eec:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_completion_chain_edge_56eec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56f00\n");
    __builtin_unreachable();
}

/* Original0x56EF0..0x56F00. */
REGION void tsl9_resident_completion_chain_block_56ef0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56F00..0x56F0C. */
REGION void tsl9_resident_completion_chain_block_56f00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 470(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 486(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56f08:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_completion_chain_edge_56f08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56f30\n");
    __builtin_unreachable();
}

/* Original0x56F0C..0x56F16. */
REGION void tsl9_resident_completion_chain_block_56f0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 326(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_56f12:\n.option push\n.option norvc\nbne a3,a4,.Lresident_completion_chain_edge_56f12\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5758c\n");
    __builtin_unreachable();
}

/* Original0x56F16..0x56F1C. */
REGION void tsl9_resident_completion_chain_block_56f16(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffffa90); LIVE;
    __builtin_unreachable();
}

/* Original0x56F1C..0x56F20. */
REGION void tsl9_resident_completion_chain_block_56f1c(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_56f1c:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_completion_chain_edge_56f1c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56f30\n");
    __builtin_unreachable();
}

/* Original0x56F20..0x56F2C. */
REGION void tsl9_resident_completion_chain_block_56f20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 | a4; LIVE;
    __builtin_unreachable();
}

/* Original0x56F2C..0x56F30. */
REGION void tsl9_resident_completion_chain_block_56f2c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56F30..0x56F3C. */
REGION void tsl9_resident_completion_chain_block_56f30(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56f38:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56f38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56F3C..0x56F48. */
REGION void tsl9_resident_completion_chain_block_56f3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56F48..0x56F52. */
REGION void tsl9_resident_completion_chain_block_56f48(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000100); LIVE;
    PORT(".Lresident_completion_chain_edge_56f50:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56f50\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56f76\n");
    __builtin_unreachable();
}

/* Original0x56F52..0x56F6A. */
REGION void tsl9_resident_completion_chain_block_56f52(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffeff); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 124(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56f66:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56f66\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56F6A..0x56F76. */
REGION void tsl9_resident_completion_chain_block_56f6a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56F76..0x56F80. */
REGION void tsl9_resident_completion_chain_block_56f76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56f7e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56f7e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56f96\n");
    __builtin_unreachable();
}

/* Original0x56F80..0x56F96. */
REGION void tsl9_resident_completion_chain_block_56f80(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffff7f); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000057); LIVE;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_completion_chain_edge_56f92:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56f92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56F96..0x56FA0. */
REGION void tsl9_resident_completion_chain_block_56f96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000200); LIVE;
    PORT(".Lresident_completion_chain_edge_56f9e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_56f9e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_56fe0\n");
    __builtin_unreachable();
}

/* Original0x56FA0..0x56FBE. */
REGION void tsl9_resident_completion_chain_block_56fa0(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffdff); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 326(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 30(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    a0 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000180)); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 323(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56fba:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56fba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_639ca\n");
    __builtin_unreachable();
}

/* Original0x56FBE..0x56FC8. */
REGION void tsl9_resident_completion_chain_block_56fbe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 322(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56fc4:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56fc4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55dea\n");
    __builtin_unreachable();
}

/* Original0x56FC8..0x56FD4. */
REGION void tsl9_resident_completion_chain_block_56fc8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_56fd0:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_56fd0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56FD4..0x56FE0. */
REGION void tsl9_resident_completion_chain_block_56fd4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56FE0..0x56FEC. */
REGION void tsl9_resident_completion_chain_block_56fe0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_completion_chain_edge_56fe8:\n.option push\n.option norvc\nbgez a4,.Lresident_completion_chain_edge_56fe8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57122\n");
    __builtin_unreachable();
}

/* Original0x56FEC..0x57002. */
REGION void tsl9_resident_completion_chain_block_56fec(void)
{
    REGS;
    a4 = UINT32_C(0xffffc000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s4, 1080(a5)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_56ffe:\n.option push\n.option norvc\nbeqz s4,.Lresident_completion_chain_edge_56ffe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5754c\n");
    __builtin_unreachable();
}

/* Original0x57002..0x57014. */
REGION void tsl9_resident_completion_chain_block_57002(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 340(s0)\n.option pop\n");
    a0 = a5 << UINT32_C(0x00000013); LIVE;
    a4 = a5 << UINT32_C(0x00000011); LIVE;
    a0 = a0 >> UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_completion_chain_edge_57010:\n.option push\n.option norvc\nbgez a4,.Lresident_completion_chain_edge_57010\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575a0\n");
    __builtin_unreachable();
}

/* Original0x57014..0x57024. */
REGION void tsl9_resident_completion_chain_block_57014(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x0000012c); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    a1 = a0 * a1; LIVE;
    PORT(".Lresident_completion_chain_edge_57020:\n.option push\n.option norvc\nbgez a5,.Lresident_completion_chain_edge_57020\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5702a\n");
    __builtin_unreachable();
}

/* Original0x57024..0x5702A. */
REGION void tsl9_resident_completion_chain_block_57024(void)
{
    REGS;
    a5 = UINT32_C(0x00258000); LIVE;
    a1 = a1 + a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5702A..0x57054. */
REGION void tsl9_resident_completion_chain_block_5702a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a6, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 344(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, s2, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 144(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 140(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 4(a3)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 132(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57050:\n.option push\n.option norvc\nbne a6,a4,.Lresident_completion_chain_edge_57050\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575ac\n");
    __builtin_unreachable();
}

/* Original0x57054..0x57058. */
REGION void tsl9_resident_completion_chain_block_57054(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57054:\n.option push\n.option norvc\nbltu a5,a2,.Lresident_completion_chain_edge_57054\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575a8\n");
    __builtin_unreachable();
}

/* Original0x57058..0x5705C. */
REGION void tsl9_resident_completion_chain_block_57058(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a5, a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5705C..0x57078. */
REGION void tsl9_resident_completion_chain_block_5705c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 8(s2)\n.option pop\n");
    a0 = a0 + a1; LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, a0, a5\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 * a5; LIVE;
    PORT(".Lresident_completion_chain_edge_57074:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57074\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x57078..0x57088. */
REGION void tsl9_resident_completion_chain_block_57078(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a5, a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, a5, a0\n.option pop\n");
    a0 = a0 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv s1, a5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57084:\n.option push\n.option norvc\nbne s3,a0,.Lresident_completion_chain_edge_57084\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5708c\n");
    __builtin_unreachable();
}

/* Original0x57088..0x5708C. */
REGION void tsl9_resident_completion_chain_block_57088(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57088:\n.option push\n.option norvc\nbltu a5,s5,.Lresident_completion_chain_edge_57088\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57090\n");
    __builtin_unreachable();
}

/* Original0x5708C..0x57090. */
REGION void tsl9_resident_completion_chain_block_5708c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a5, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57090..0x5709A. */
REGION void tsl9_resident_completion_chain_block_57090(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 480(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5709A..0x570A0. */
REGION void tsl9_resident_completion_chain_block_5709a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, s3\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5709c:\n.option push\n.option norvc\nbltu s1,a0,.Lresident_completion_chain_edge_5709c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575e2\n");
    __builtin_unreachable();
}

/* Original0x570A0..0x570A4. */
REGION void tsl9_resident_completion_chain_block_570a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s1, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x570A4..0x570B6. */
REGION void tsl9_resident_completion_chain_block_570a4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 492\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 23(s3)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_570b2:\n.option push\n.option norvc\nbleu a4,a0,.Lresident_completion_chain_edge_570b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575ee\n");
    __builtin_unreachable();
}

/* Original0x570B6..0x570EC. */
REGION void tsl9_resident_completion_chain_block_570b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 220(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a3, 8(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 342(s0)\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 * a3; LIVE;
    a3 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nlw a2, 4(s2)\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a4, a4, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a3, a4, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_570e8:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_completion_chain_edge_570e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57660\n");
    __builtin_unreachable();
}

/* Original0x570EC..0x570F0. */
REGION void tsl9_resident_completion_chain_block_570ec(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_570ec:\n.option push\n.option norvc\nbleu a2,a3,.Lresident_completion_chain_edge_570ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57660\n");
    __builtin_unreachable();
}

/* Original0x570F0..0x57106. */
REGION void tsl9_resident_completion_chain_block_570f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a5, 136(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s1, 160(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 334(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 130(s4)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57102:\n.option push\n.option norvc\nbne a4,a3,.Lresident_completion_chain_edge_57102\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_576de\n");
    __builtin_unreachable();
}

/* Original0x57106..0x5710A. */
REGION void tsl9_resident_completion_chain_block_57106(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x5710A..0x57114. */
REGION void tsl9_resident_completion_chain_block_5710a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 130(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57110:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57110\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_633aa\n");
    __builtin_unreachable();
}

/* Original0x57114..0x57122. */
REGION void tsl9_resident_completion_chain_block_57114(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000026); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_5711e:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_5711e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x57122..0x5712E. */
REGION void tsl9_resident_completion_chain_block_57122(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_completion_chain_edge_5712a:\n.option push\n.option norvc\nbgez a4,.Lresident_completion_chain_edge_5712a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57138\n");
    __builtin_unreachable();
}

/* Original0x5712E..0x57138. */
REGION void tsl9_resident_completion_chain_block_5712e(void)
{
    REGS;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57138..0x57144. */
REGION void tsl9_resident_completion_chain_block_57138(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_57140:\n.option push\n.option norvc\nbgez a4,.Lresident_completion_chain_edge_57140\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57192\n");
    __builtin_unreachable();
}

/* Original0x57144..0x57154. */
REGION void tsl9_resident_completion_chain_block_57144(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003bb)); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 48(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57150:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57150\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_43de4\n");
    __builtin_unreachable();
}

/* Original0x57154..0x57192. */
REGION void tsl9_resident_completion_chain_block_57154(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3e\n.option pop\n");
    a4 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option norvc\nsw a0, 148(s0)\n.option pop\n");
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000202)); LIVE;
    a4 = UINT32_C(0xffff8000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a0 = a0 + UINT32_C(0x00000050); LIVE;
    a5 = a5 + a0; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 132(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57192..0x5719A. */
REGION void tsl9_resident_completion_chain_block_57192(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_57198:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57198\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_571b4\n");
    __builtin_unreachable();
}

/* Original0x5719A..0x571B0. */
REGION void tsl9_resident_completion_chain_block_5719a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 84(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_571ac:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_571ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x571B0..0x571B4. */
REGION void tsl9_resident_completion_chain_block_571b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x571B4..0x571BC. */
REGION void tsl9_resident_completion_chain_block_571b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_571b8:\n.option push\n.option norvc\nbgez a5,.Lresident_completion_chain_edge_571b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_571c4\n");
    __builtin_unreachable();
}

/* Original0x571BC..0x571C4. */
REGION void tsl9_resident_completion_chain_block_571bc(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x571C4..0x571CA. */
REGION void tsl9_resident_completion_chain_block_571c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 379(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_571c8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_571c8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_571f0\n");
    __builtin_unreachable();
}

/* Original0x571CA..0x571D8. */
REGION void tsl9_resident_completion_chain_block_571ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a4, 52(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000006); LIVE;
    a2 = a4 - a5; LIVE;
    PORT(".Lresident_completion_chain_edge_571d4:\n.option push\n.option norvc\nble a2,a3,.Lresident_completion_chain_edge_571d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_576f0\n");
    __builtin_unreachable();
}

/* Original0x571D8..0x571E8. */
REGION void tsl9_resident_completion_chain_block_571d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a3 = UINT32_C(0x00100000); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    a5 = UINT32_C(0xfffffffb); LIVE;
    __builtin_unreachable();
}

/* Original0x571E8..0x571F0. */
REGION void tsl9_resident_completion_chain_block_571e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 383(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a4, 379(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x571F0..0x571FA. */
REGION void tsl9_resident_completion_chain_block_571f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 388(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_571f8:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_571f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57296\n");
    __builtin_unreachable();
}

/* Original0x571FA..0x57206. */
REGION void tsl9_resident_completion_chain_block_571fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a3, 52(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a4, 380(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57202:\n.option push\n.option norvc\nble a4,a3,.Lresident_completion_chain_edge_57202\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5721a\n");
    __builtin_unreachable();
}

/* Original0x57206..0x5721A. */
REGION void tsl9_resident_completion_chain_block_57206(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 164(s0)\n.option pop\n");
    a2 = UINT32_C(0x00100000); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".option push\n.option norvc\nsw a4, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 383(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5721A..0x57222. */
REGION void tsl9_resident_completion_chain_block_5721a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a4, 381(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5721e:\n.option push\n.option norvc\nble a3,a4,.Lresident_completion_chain_edge_5721e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57236\n");
    __builtin_unreachable();
}

/* Original0x57222..0x57236. */
REGION void tsl9_resident_completion_chain_block_57222(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 164(s0)\n.option pop\n");
    a2 = UINT32_C(0x00100000); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".option push\n.option norvc\nsw a4, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0xfffffffc); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 383(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57236..0x57242. */
REGION void tsl9_resident_completion_chain_block_57236(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a4, 378(s0)\n.option pop\n");
    a2 = UINT32_C(0x0000007f); LIVE;
    PORT(".Lresident_completion_chain_edge_5723e:\n.option push\n.option norvc\nbeq a4,a2,.Lresident_completion_chain_edge_5723e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57276\n");
    __builtin_unreachable();
}

/* Original0x57242..0x57258. */
REGION void tsl9_resident_completion_chain_block_57242(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 391(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 392(s0)\n.option pop\n");
    a4 = a4 - a3; LIVE;
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x18\n.option pop\n");
    a3 = a2 - a0; LIVE;
    PORT(".Lresident_completion_chain_edge_57254:\n.option push\n.option norvc\nble a3,a4,.Lresident_completion_chain_edge_57254\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57708\n");
    __builtin_unreachable();
}

/* Original0x57258..0x57260. */
REGION void tsl9_resident_completion_chain_block_57258(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_5725c:\n.option push\n.option norvc\nbnez a3,.Lresident_completion_chain_edge_5725c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57708\n");
    __builtin_unreachable();
}

/* Original0x57260..0x57268. */
REGION void tsl9_resident_completion_chain_block_57260(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x57268..0x57276. */
REGION void tsl9_resident_completion_chain_block_57268(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 388(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 394(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 396(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57276..0x5727C. */
REGION void tsl9_resident_completion_chain_block_57276(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 396(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5727a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_5727a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57296\n");
    __builtin_unreachable();
}

/* Original0x5727C..0x57288. */
REGION void tsl9_resident_completion_chain_block_5727c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 396(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57286:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_57286\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57296\n");
    __builtin_unreachable();
}

/* Original0x57288..0x57296. */
REGION void tsl9_resident_completion_chain_block_57288(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_57292:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57292\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x57296..0x5729A. */
REGION void tsl9_resident_completion_chain_block_57296(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57298:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57298\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572d6\n");
    __builtin_unreachable();
}

/* Original0x5729A..0x572A0. */
REGION void tsl9_resident_completion_chain_block_5729a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5729e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_5729e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572b6\n");
    __builtin_unreachable();
}

/* Original0x572A0..0x572A4. */
REGION void tsl9_resident_completion_chain_block_572a0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c3c\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_572a2:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_572a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572b6\n");
    __builtin_unreachable();
}

/* Original0x572A4..0x572B0. */
REGION void tsl9_resident_completion_chain_block_572a4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_572ac:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_572ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x572B0..0x572B2. */
REGION void tsl9_resident_completion_chain_block_572b0(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_572b0:\n.option push\n.option rvc\nc.bnez a0,.Lresident_completion_chain_edge_572b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572b6\n");
    __builtin_unreachable();
}

/* Original0x572B2..0x572B6. */
REGION void tsl9_resident_completion_chain_block_572b2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x572B6..0x572BC. */
REGION void tsl9_resident_completion_chain_block_572b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 68(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_572ba:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_572ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572d6\n");
    __builtin_unreachable();
}

/* Original0x572BC..0x572C2. */
REGION void tsl9_resident_completion_chain_block_572bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 49(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_572c0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_572c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572d6\n");
    __builtin_unreachable();
}

/* Original0x572C2..0x572CE. */
REGION void tsl9_resident_completion_chain_block_572c2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000013); LIVE;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_completion_chain_edge_572ca:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_572ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x572CE..0x572D0. */
REGION void tsl9_resident_completion_chain_block_572ce(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_572ce:\n.option push\n.option rvc\nc.bnez a0,.Lresident_completion_chain_edge_572ce\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_572d6\n");
    __builtin_unreachable();
}

/* Original0x572D0..0x572D6. */
REGION void tsl9_resident_completion_chain_block_572d0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 49(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x572D6..0x572E0. */
REGION void tsl9_resident_completion_chain_block_572d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 398(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_572de:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_572de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_573ac\n");
    __builtin_unreachable();
}

/* Original0x572E0..0x572EE. */
REGION void tsl9_resident_completion_chain_block_572e0(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 398(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_572ec:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_572ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_573ac\n");
    __builtin_unreachable();
}

/* Original0x572EE..0x572F6. */
REGION void tsl9_resident_completion_chain_block_572ee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2818\n.option pop\n");
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".Lresident_completion_chain_edge_572f2:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_completion_chain_edge_572f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_573ac\n");
    __builtin_unreachable();
}

/* Original0x572F6..0x572FC. */
REGION void tsl9_resident_completion_chain_block_572f6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_572fa:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_572fa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_573ac\n");
    __builtin_unreachable();
}

/* Original0x572FC..0x57308. */
REGION void tsl9_resident_completion_chain_block_572fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s5, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nli s4, 37\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57308..0x57326. */
REGION void tsl9_resident_completion_chain_block_57308(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a4, s1, 0x18\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x18\n.option pop\n");
    a5 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s0\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000197)); LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a5, s5, a5\n.option pop\n");
    a4 = a4 & a5; LIVE;
    PORT(".Lresident_completion_chain_edge_57322:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_completion_chain_edge_57322\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57338\n");
    __builtin_unreachable();
}

/* Original0x57326..0x57330. */
REGION void tsl9_resident_completion_chain_block_57326(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_completion_chain_edge_5732c:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_5732c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_6deee\n");
    __builtin_unreachable();
}

/* Original0x57330..0x57338. */
REGION void tsl9_resident_completion_chain_block_57330(void)
{
    REGS;
    PORT(".option push\n.option norvc\nor s3, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nor s2, s2, a1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57338..0x5733E. */
REGION void tsl9_resident_completion_chain_block_57338(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, 1\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5733a:\n.option push\n.option norvc\nbne s1,s4,.Lresident_completion_chain_edge_5733a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57308\n");
    __builtin_unreachable();
}

/* Original0x5733E..0x57358. */
REGION void tsl9_resident_completion_chain_block_5733e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 312(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 316(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nand a0, a0, s3\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nand a1, a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_completion_chain_edge_57354:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57354\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ad8\n");
    __builtin_unreachable();
}

/* Original0x57358..0x57360. */
REGION void tsl9_resident_completion_chain_block_57358(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 309(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5735c:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_completion_chain_edge_5735c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5737c\n");
    __builtin_unreachable();
}

/* Original0x57360..0x5737C. */
REGION void tsl9_resident_completion_chain_block_57360(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 52(s0)\n.option pop\n");
    a4 = UINT32_C(0xffffffff); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = a0 + UINT32_C(0xfffffff6); LIVE;
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x18\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_completion_chain_literal_57374:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_200027b4\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_completion_chain_literal_57374\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5737C..0x57386. */
REGION void tsl9_resident_completion_chain_block_5737c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 312(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".Lresident_completion_chain_edge_57382:\n.option push\n.option norvc\nbne a4,a5,.Lresident_completion_chain_edge_57382\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57390\n");
    __builtin_unreachable();
}

/* Original0x57386..0x57390. */
REGION void tsl9_resident_completion_chain_block_57386(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 316(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_completion_chain_edge_5738c:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_completion_chain_edge_5738c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_573ac\n");
    __builtin_unreachable();
}

/* Original0x57390..0x573A0. */
REGION void tsl9_resident_completion_chain_block_57390(void)
{
    REGS;
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 8\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 296\n.option pop\n");
    PORT(".Lresident_completion_chain_literal_57398:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_completion_chain_literal_57398\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x573A0..0x573AC. */
REGION void tsl9_resident_completion_chain_block_573a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x573AC..0x573BA. */
REGION void tsl9_resident_completion_chain_block_573ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 398(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000009); LIVE;
    a4 = a3 & UINT32_C(0x00000009); LIVE;
    PORT(".Lresident_completion_chain_edge_573b6:\n.option push\n.option norvc\nbne a4,a5,.Lresident_completion_chain_edge_573b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57400\n");
    __builtin_unreachable();
}

/* Original0x573BA..0x573C6. */
REGION void tsl9_resident_completion_chain_block_573ba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 400(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_573c2:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_completion_chain_edge_573c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57400\n");
    __builtin_unreachable();
}

/* Original0x573C6..0x573D2. */
REGION void tsl9_resident_completion_chain_block_573c6(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    a2 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_573ce:\n.option push\n.option norvc\nbltz a2,.Lresident_completion_chain_edge_573ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57400\n");
    __builtin_unreachable();
}

/* Original0x573D2..0x57400. */
REGION void tsl9_resident_completion_chain_block_573d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 399(s0)\n.option pop\n");
    a2 = UINT32_C(0x000000a0); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    a5 = a5 * a2; LIVE;
    /* Conditional Xwchc: qk.c.lhu a2, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c32\n.option pop\n");
    a3 = a3 & UINT32_C(0xfffffff7); LIVE;
    PORT(".option push\n.option norvc\nsb a3, 398(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a5, a5, a2\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 400(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00800000); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57400..0x57406. */
REGION void tsl9_resident_completion_chain_block_57400(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57404:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57404\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_574ce\n");
    __builtin_unreachable();
}

/* Original0x57406..0x5740A. */
REGION void tsl9_resident_completion_chain_block_57406(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_completion_chain_edge_57408:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57408\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57422\n");
    __builtin_unreachable();
}

/* Original0x5740A..0x57418. */
REGION void tsl9_resident_completion_chain_block_5740a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2810\n.option pop\n");
    a1 = UINT32_C(0x00010000); LIVE;
    a1 = a1 + UINT32_C(0xfffffa00); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57414:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57414\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_55cc4\n");
    __builtin_unreachable();
}

/* Original0x57418..0x57422. */
REGION void tsl9_resident_completion_chain_block_57418(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57422..0x5742A. */
REGION void tsl9_resident_completion_chain_block_57422(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_57428:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57428\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5744a\n");
    __builtin_unreachable();
}

/* Original0x5742A..0x57436. */
REGION void tsl9_resident_completion_chain_block_5742a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 39(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_completion_chain_edge_57432:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_completion_chain_edge_57432\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57440\n");
    __builtin_unreachable();
}

/* Original0x57436..0x5743A. */
REGION void tsl9_resident_completion_chain_block_57436(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57436:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57436\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x5743A..0x57440. */
REGION void tsl9_resident_completion_chain_block_5743a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 39(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57440..0x5744A. */
REGION void tsl9_resident_completion_chain_block_57440(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5744A..0x57452. */
REGION void tsl9_resident_completion_chain_block_5744a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_57450:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57450\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5746a\n");
    __builtin_unreachable();
}

/* Original0x57452..0x57460. */
REGION void tsl9_resident_completion_chain_block_57452(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c6e\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 40(s0)\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    a1 = a1 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_completion_chain_edge_5745c:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_5745c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_435ce\n");
    __builtin_unreachable();
}

/* Original0x57460..0x5746A. */
REGION void tsl9_resident_completion_chain_block_57460(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5746A..0x57472. */
REGION void tsl9_resident_completion_chain_block_5746a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_completion_chain_edge_57470:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57470\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5748e\n");
    __builtin_unreachable();
}

/* Original0x57472..0x57484. */
REGION void tsl9_resident_completion_chain_block_57472(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c6e\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    a1 = a1 + UINT32_C(0xfffffffe); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_57480:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57480\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_55cc4\n");
    __builtin_unreachable();
}

/* Original0x57484..0x5748E. */
REGION void tsl9_resident_completion_chain_block_57484(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5748E..0x57498. */
REGION void tsl9_resident_completion_chain_block_5748e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_completion_chain_edge_57496:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_57496\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_574ae\n");
    __builtin_unreachable();
}

/* Original0x57498..0x574A8. */
REGION void tsl9_resident_completion_chain_block_57498(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 38(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_574a4:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_574a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x574A8..0x574AE. */
REGION void tsl9_resident_completion_chain_block_574a8(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 38(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x574AE..0x574B8. */
REGION void tsl9_resident_completion_chain_block_574ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_completion_chain_edge_574b6:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_574b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_574ce\n");
    __builtin_unreachable();
}

/* Original0x574B8..0x574CE. */
REGION void tsl9_resident_completion_chain_block_574b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 74(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 38(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_completion_chain_edge_574ca:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_574ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_435ce\n");
    __builtin_unreachable();
}

/* Original0x574CE..0x574D6. */
REGION void tsl9_resident_completion_chain_block_574ce(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c5c\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_completion_chain_edge_574d4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_574d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_574e4\n");
    __builtin_unreachable();
}

/* Original0x574D6..0x574E0. */
REGION void tsl9_resident_completion_chain_block_574d6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3438\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_574dc:\n.option push\n.option norvc\nbne a4,a5,.Lresident_completion_chain_edge_574dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57748\n");
    __builtin_unreachable();
}

/* Original0x574E0..0x574E4. */
REGION void tsl9_resident_completion_chain_block_574e0(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_574e0:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_574e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_56574\n");
    __builtin_unreachable();
}

/* Original0x574E4..0x574EA. */
REGION void tsl9_resident_completion_chain_block_574e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_574e8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_574e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5754c\n");
    __builtin_unreachable();
}

/* Original0x574EA..0x574F4. */
REGION void tsl9_resident_completion_chain_block_574ea(void)
{
    REGS;
    a4 = UINT32_C(0x00000064); LIVE;
    PORT(".option push\n.option norvc\nremu a5, a5, a4\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_574f2:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_574f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_5754c\n");
    __builtin_unreachable();
}

/* Original0x574F4..0x57508. */
REGION void tsl9_resident_completion_chain_block_574f4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e4)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_57506:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_57506\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57544\n");
    __builtin_unreachable();
}

/* Original0x57508..0x57516. */
REGION void tsl9_resident_completion_chain_block_57508(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 492\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 52(s2)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57514:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_chain_edge_57514\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57544\n");
    __builtin_unreachable();
}

/* Original0x57516..0x57522. */
REGION void tsl9_resident_completion_chain_block_57516(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 16(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x289e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 18(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28ae\n.option pop\n");
    a0 = UINT32_C(0x00000009); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a1 = a1 | a5; LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57522..0x5752C. */
REGION void tsl9_resident_completion_chain_block_57522(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 52(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 14(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24ee\n.option pop\n");
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5752C..0x57538. */
REGION void tsl9_resident_completion_chain_block_5752c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 52(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlh a1, 50(s0)\n.option pop\n");
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57538..0x57544. */
REGION void tsl9_resident_completion_chain_block_57538(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 52(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a1, 52(s0)\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57544..0x5754C. */
REGION void tsl9_resident_completion_chain_block_57544(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 14(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 16(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5754C..0x5755E. */
REGION void tsl9_resident_completion_chain_block_5754c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5755E..0x57566. */
REGION void tsl9_resident_completion_chain_block_5755e(void)
{
    REGS;
    a5 = UINT32_C(0x00000040); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac5c\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57564:\n.option push\n.option rvc\nc.bnez a2,.Lresident_completion_chain_edge_57564\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_57572\n");
    __builtin_unreachable();
}

/* Original0x57566..0x57572. */
REGION void tsl9_resident_completion_chain_block_57566(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57572..0x57576. */
REGION void tsl9_resident_completion_chain_block_57572(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57572:\n.option push\n.option norvc\nbnez a3,.Lresident_completion_chain_edge_57572\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_56dd8\n");
    __builtin_unreachable();
}

/* Original0x57576..0x57582. */
REGION void tsl9_resident_completion_chain_block_57576(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_5757e:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_5757e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x57582..0x57586. */
REGION void tsl9_resident_completion_chain_block_57582(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57582:\n.option push\n.option norvc\njal zero,.Lresident_completion_chain_edge_57582\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_completion_chain_block_56dd8\n");
    __builtin_unreachable();
}

/* Original0x57586..0x5758C. */
REGION void tsl9_resident_completion_chain_block_57586(void)
{
    REGS;
    a4 = UINT32_C(0x00000148); LIVE;
    PORT(".Lresident_completion_chain_edge_5758a:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_5758a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_56eec\n");
    __builtin_unreachable();
}

/* Original0x5758C..0x57592. */
REGION void tsl9_resident_completion_chain_block_5758c(void)
{
    REGS;
    a4 = UINT32_C(0x00000148); LIVE;
    PORT(".Lresident_completion_chain_edge_57590:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_57590\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_56f1c\n");
    __builtin_unreachable();
}

/* Original0x57592..0x575A0. */
REGION void tsl9_resident_completion_chain_block_57592(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0xfffff000); LIVE;
    a4 = a4 + UINT32_C(0x000007ff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".Lresident_completion_chain_edge_5759e:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_5759e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_56f2c\n");
    __builtin_unreachable();
}

/* Original0x575A0..0x575A8. */
REGION void tsl9_resident_completion_chain_block_575a0(void)
{
    REGS;
    a1 = UINT32_C(0x0000001e); LIVE;
    a1 = a0 * a1; LIVE;
    PORT(".Lresident_completion_chain_edge_575a6:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5702a\n");
    __builtin_unreachable();
}

/* Original0x575A8..0x575AC. */
REGION void tsl9_resident_completion_chain_block_575a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a5, a5, s5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575aa:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575aa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_57058\n");
    __builtin_unreachable();
}

/* Original0x575AC..0x575B4. */
REGION void tsl9_resident_completion_chain_block_575ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, a6, 1\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575b0:\n.option push\n.option norvc\nbleu a6,a4,.Lresident_completion_chain_edge_575b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575ca\n");
    __builtin_unreachable();
}

/* Original0x575B4..0x575C0. */
REGION void tsl9_resident_completion_chain_block_575b4(void)
{
    REGS;
    a4 = a3 - a4; LIVE;
    a4 = a4 * a2; LIVE;
    PORT(".Lresident_completion_chain_edge_575bc:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_completion_chain_edge_575bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575c6\n");
    __builtin_unreachable();
}

/* Original0x575C0..0x575C6. */
REGION void tsl9_resident_completion_chain_block_575c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a5, a4\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575c4:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5705c\n");
    __builtin_unreachable();
}

/* Original0x575C6..0x575CA. */
REGION void tsl9_resident_completion_chain_block_575c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a5, a5, s5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575c8:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_575c0\n");
    __builtin_unreachable();
}

/* Original0x575CA..0x575D8. */
REGION void tsl9_resident_completion_chain_block_575ca(void)
{
    REGS;
    a4 = a4 - a3; LIVE;
    a4 = a4 * a2; LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv s1, a5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575d4:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_completion_chain_edge_575d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_575dc\n");
    __builtin_unreachable();
}

/* Original0x575D8..0x575DC. */
REGION void tsl9_resident_completion_chain_block_575d8(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_575d8:\n.option push\n.option norvc\nbltu a5,s5,.Lresident_completion_chain_edge_575d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5705c\n");
    __builtin_unreachable();
}

/* Original0x575DC..0x575E2. */
REGION void tsl9_resident_completion_chain_block_575dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a5, s5\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_575e0:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5705c\n");
    __builtin_unreachable();
}

/* Original0x575E2..0x575EE. */
REGION void tsl9_resident_completion_chain_block_575e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 4(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s1\n.option pop\n");
    a0 = a4 - a0; LIVE;
    PORT(".Lresident_completion_chain_edge_575ec:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_575ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_570a4\n");
    __builtin_unreachable();
}

/* Original0x575EE..0x575F6. */
REGION void tsl9_resident_completion_chain_block_575ee(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".Lresident_completion_chain_edge_575f2:\n.option push\n.option norvc\nbgez a0,.Lresident_completion_chain_edge_575f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5766e\n");
    __builtin_unreachable();
}

/* Original0x575F6..0x575F8. */
REGION void tsl9_resident_completion_chain_block_575f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x575F8..0x5760C. */
REGION void tsl9_resident_completion_chain_block_575f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 23(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 4(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    a0 = a0 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57608:\n.option push\n.option norvc\nbltu a0,a4,.Lresident_completion_chain_edge_57608\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57610\n");
    __builtin_unreachable();
}

/* Original0x5760C..0x57610. */
REGION void tsl9_resident_completion_chain_block_5760c(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_5760c:\n.option push\n.option norvc\nbltu a0,a2,.Lresident_completion_chain_edge_5760c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57614\n");
    __builtin_unreachable();
}

/* Original0x57610..0x57614. */
REGION void tsl9_resident_completion_chain_block_57610(void)
{
    REGS;
    a5 = a0 - a2; LIVE;
    __builtin_unreachable();
}

/* Original0x57614..0x57618. */
REGION void tsl9_resident_completion_chain_block_57614(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57614:\n.option push\n.option norvc\nbltu a5,s1,.Lresident_completion_chain_edge_57614\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57666\n");
    __builtin_unreachable();
}

/* Original0x57618..0x5761A. */
REGION void tsl9_resident_completion_chain_block_57618(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsub a5, a5, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5761A..0x57660. */
REGION void tsl9_resident_completion_chain_block_5761a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 220(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 8(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a3, 342(s0)\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 * a0; LIVE;
    a0 = UINT32_C(0x00000320); LIVE;
    a4 = a4 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a4, a4, a0\n.option pop\n");
    a0 = a3 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    a5 = a5 + a0; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a3 = a5 - a3; LIVE;
    a4 = a3 * a4; LIVE;
    PORT(".option push\n.option norvc\nadd a3, a4, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a4, a3, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5765c:\n.option push\n.option norvc\nbeq a1,a4,.Lresident_completion_chain_edge_5765c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_570ec\n");
    __builtin_unreachable();
}

/* Original0x57660..0x57666. */
REGION void tsl9_resident_completion_chain_block_57660(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a3, a2\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57664:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_57664\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_570f0\n");
    __builtin_unreachable();
}

/* Original0x57666..0x5766E. */
REGION void tsl9_resident_completion_chain_block_57666(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a4, a2, s1\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".Lresident_completion_chain_edge_5766c:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_5766c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5761a\n");
    __builtin_unreachable();
}

/* Original0x5766E..0x57670. */
REGION void tsl9_resident_completion_chain_block_5766e(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57670..0x57682. */
REGION void tsl9_resident_completion_chain_block_57670(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 23(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 4(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    a0 = a0 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5767e:\n.option push\n.option norvc\nbltu a0,a4,.Lresident_completion_chain_edge_5767e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57686\n");
    __builtin_unreachable();
}

/* Original0x57682..0x57686. */
REGION void tsl9_resident_completion_chain_block_57682(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57682:\n.option push\n.option norvc\nbltu a0,a1,.Lresident_completion_chain_edge_57682\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5768a\n");
    __builtin_unreachable();
}

/* Original0x57686..0x5768A. */
REGION void tsl9_resident_completion_chain_block_57686(void)
{
    REGS;
    a5 = a0 - a1; LIVE;
    __builtin_unreachable();
}

/* Original0x5768A..0x5768E. */
REGION void tsl9_resident_completion_chain_block_5768a(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_5768a:\n.option push\n.option norvc\nbltu s1,a5,.Lresident_completion_chain_edge_5768a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_576d0\n");
    __builtin_unreachable();
}

/* Original0x5768E..0x57692. */
REGION void tsl9_resident_completion_chain_block_5768e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a5, s1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57692..0x576CC. */
REGION void tsl9_resident_completion_chain_block_57692(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 220(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a2, 8(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a3, 342(s0)\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 * a2; LIVE;
    a2 = UINT32_C(0x00000320); LIVE;
    a4 = a4 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a4, a2\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a5, a5, a2\n.option pop\n");
    a5 = a3 - a5; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a4 = a3 - a5; LIVE;
    a4 = a4 * a2; LIVE;
    PORT(".Lresident_completion_chain_edge_576c8:\n.option push\n.option norvc\nbltu s1,a4,.Lresident_completion_chain_edge_576c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_576da\n");
    __builtin_unreachable();
}

/* Original0x576CC..0x576D0. */
REGION void tsl9_resident_completion_chain_block_576cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsub s1, s1, a4\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_576ce:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_576ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_570f0\n");
    __builtin_unreachable();
}

/* Original0x576D0..0x576DA. */
REGION void tsl9_resident_completion_chain_block_576d0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a4, s1, a1\n.option pop\n");
    a5 = a4 - a5; LIVE;
    PORT(".Lresident_completion_chain_edge_576d8:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_576d8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_57692\n");
    __builtin_unreachable();
}

/* Original0x576DA..0x576DE. */
REGION void tsl9_resident_completion_chain_block_576da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s1, s1, a1\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_576dc:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_576dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_576cc\n");
    __builtin_unreachable();
}

/* Original0x576DE..0x576E4. */
REGION void tsl9_resident_completion_chain_block_576de(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_576e0:\n.option push\n.option norvc\nbne a4,a3,.Lresident_completion_chain_edge_576e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_576e8\n");
    __builtin_unreachable();
}

/* Original0x576E4..0x576E8. */
REGION void tsl9_resident_completion_chain_block_576e4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffff9); LIVE;
    PORT(".Lresident_completion_chain_edge_576e6:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_576e6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5710a\n");
    __builtin_unreachable();
}

/* Original0x576E8..0x576F0. */
REGION void tsl9_resident_completion_chain_block_576e8(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_completion_chain_edge_576ee:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_576ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_5710a\n");
    __builtin_unreachable();
}

/* Original0x576F0..0x576F6. */
REGION void tsl9_resident_completion_chain_block_576f0(void)
{
    REGS;
    a5 = a5 - a4; LIVE;
    PORT(".Lresident_completion_chain_edge_576f2:\n.option push\n.option norvc\nble a5,a3,.Lresident_completion_chain_edge_576f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_571f0\n");
    __builtin_unreachable();
}

/* Original0x576F6..0x57708. */
REGION void tsl9_resident_completion_chain_block_576f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a3 = UINT32_C(0x00100000); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_completion_chain_edge_57706:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_57706\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_571e8\n");
    __builtin_unreachable();
}

/* Original0x57708..0x57718. */
REGION void tsl9_resident_completion_chain_block_57708(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 389(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 390(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a6, a3, a1\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_57714:\n.option push\n.option norvc\nble a4,a6,.Lresident_completion_chain_edge_57714\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5772a\n");
    __builtin_unreachable();
}

/* Original0x57718..0x57720. */
REGION void tsl9_resident_completion_chain_block_57718(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a6, a5, 64\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_5771c:\n.option push\n.option norvc\nbnez a6,.Lresident_completion_chain_edge_5771c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_5772a\n");
    __builtin_unreachable();
}

/* Original0x57720..0x5772A. */
REGION void tsl9_resident_completion_chain_block_57720(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_completion_chain_edge_57728:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_57728\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_57268\n");
    __builtin_unreachable();
}

/* Original0x5772A..0x57730. */
REGION void tsl9_resident_completion_chain_block_5772a(void)
{
    REGS;
    a2 = a2 + a0; LIVE;
    PORT(".Lresident_completion_chain_edge_5772c:\n.option push\n.option norvc\nblt a4,a2,.Lresident_completion_chain_edge_5772c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57276\n");
    __builtin_unreachable();
}

/* Original0x57730..0x57736. */
REGION void tsl9_resident_completion_chain_block_57730(void)
{
    REGS;
    a3 = a3 - a1; LIVE;
    PORT(".Lresident_completion_chain_edge_57732:\n.option push\n.option norvc\nblt a3,a4,.Lresident_completion_chain_edge_57732\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57276\n");
    __builtin_unreachable();
}

/* Original0x57736..0x5773E. */
REGION void tsl9_resident_completion_chain_block_57736(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_completion_chain_edge_5773a:\n.option push\n.option norvc\nbnez a4,.Lresident_completion_chain_edge_5773a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_57276\n");
    __builtin_unreachable();
}

/* Original0x5773E..0x57748. */
REGION void tsl9_resident_completion_chain_block_5773e(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_completion_chain_edge_57746:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_57746\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_57268\n");
    __builtin_unreachable();
}

/* Original0x57748..0x5774C. */
REGION void tsl9_resident_completion_chain_block_57748(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_57748:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_57748\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5649c\n");
    __builtin_unreachable();
}

/* Original0x5774C..0x5774E. */
REGION void tsl9_resident_completion_chain_block_5774c(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_5774c:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_5774c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_574e4\n");
    __builtin_unreachable();
}

/* Original0x58F14..0x58F30. */
REGION void tsl9_candidate_unprovided_flash_58f14(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000136)); LIVE;
    a3 = a5 >> UINT32_C(0x00000003); LIVE;
    a3 = a3 + a0; LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000130)); LIVE;
    a4 = a5 & UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsra a2, a1, a4\n.option pop\n");
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_58f2c:\n.option push\n.option norvc\nbeqz a2,.Lresident_completion_chain_edge_58f2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_59032\n");
    __builtin_unreachable();
}

/* Original0x58F30..0x58F38. */
REGION void tsl9_resident_completion_chain_block_58f30(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x391c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_58f34:\n.option push\n.option norvc\nbnez a5,.Lresident_completion_chain_edge_58f34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_59040\n");
    __builtin_unreachable();
}

/* Original0x58F38..0x58F42. */
REGION void tsl9_resident_completion_chain_block_58f38(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_completion_chain_edge_58f3e:\n.option push\n.option norvc\nbnez a5,.Lresident_completion_chain_edge_58f3e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_59040\n");
    __builtin_unreachable();
}

/* Original0x58F42..0x58F52. */
REGION void tsl9_resident_completion_chain_block_58f42(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000138); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_58f4e:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_58f4e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ad8\n");
    __builtin_unreachable();
}

/* Original0x58F52..0x58F5E. */
REGION void tsl9_resident_completion_chain_block_58f52(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 309(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 52(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_58f5a:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_completion_chain_edge_58f5a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_58ffa\n");
    __builtin_unreachable();
}

/* Original0x58F5E..0x58F78. */
REGION void tsl9_resident_completion_chain_block_58f5e(void)
{
    REGS;
    a0 = a5 + UINT32_C(0xfffffff6); LIVE;
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a2 = UINT32_C(0xffffffff); LIVE;
    a3 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x18\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_completion_chain_literal_58f70:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_200027b4\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_completion_chain_literal_58f70\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58F78..0x58F8C. */
REGION void tsl9_resident_completion_chain_block_58f78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a2, 312(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nlw a3, 316(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & a2; LIVE;
    a5 = a5 & a3; LIVE;
    PORT(".Lresident_completion_chain_edge_58f88:\n.option push\n.option norvc\nbne a2,a4,.Lresident_completion_chain_edge_58f88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_58f90\n");
    __builtin_unreachable();
}

/* Original0x58F8C..0x58F90. */
REGION void tsl9_resident_completion_chain_block_58f8c(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_58f8c:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_completion_chain_edge_58f8c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_58fa0\n");
    __builtin_unreachable();
}

/* Original0x58F90..0x58F96. */
REGION void tsl9_resident_completion_chain_block_58f90(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_58f92:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_58f92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ad8\n");
    __builtin_unreachable();
}

/* Original0x58F96..0x58F9C. */
REGION void tsl9_resident_completion_chain_block_58f96(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lresident_completion_chain_edge_58f98:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_completion_chain_edge_58f98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_chain_block_58fd6\n");
    __builtin_unreachable();
}

/* Original0x58F9C..0x58FA0. */
REGION void tsl9_resident_completion_chain_block_58f9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 309(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58FA0..0x58FA6. */
REGION void tsl9_resident_completion_chain_block_58fa0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 398(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_58fa4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_chain_edge_58fa4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_58fce\n");
    __builtin_unreachable();
}

/* Original0x58FA6..0x58FB2. */
REGION void tsl9_resident_completion_chain_block_58fa6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 310(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_completion_chain_edge_58fae:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_58fae\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6dec2\n");
    __builtin_unreachable();
}

/* Original0x58FB2..0x58FB6. */
REGION void tsl9_resident_completion_chain_block_58fb2(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_chain_edge_58fb4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_completion_chain_edge_58fb4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_58fce\n");
    __builtin_unreachable();
}

/* Original0x58FB6..0x58FC0. */
REGION void tsl9_resident_completion_chain_block_58fb6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 268(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_chain_edge_58fbe:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_chain_edge_58fbe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_58fce\n");
    __builtin_unreachable();
}

/* Original0x58FC0..0x58FCE. */
REGION void tsl9_resident_completion_chain_block_58fc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00400000); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58FCE..0x58FD6. */
REGION void tsl9_resident_completion_chain_block_58fce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58FD6..0x58FDC. */
REGION void tsl9_resident_completion_chain_block_58fd6(void)
{
    REGS;
    a0 = a0 + UINT32_C(0xfffffffb); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 309(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58FDC..0x58FEC. */
REGION void tsl9_resident_completion_chain_block_58fdc(void)
{
    REGS;
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 8\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 296\n.option pop\n");
    PORT(".Lresident_completion_chain_literal_58fe4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_completion_chain_literal_58fe4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58FEC..0x58FFA. */
REGION void tsl9_resident_completion_chain_block_58fec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_58ff8:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_58ff8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_58fa0\n");
    __builtin_unreachable();
}

/* Original0x58FFA..0x5900A. */
REGION void tsl9_resident_completion_chain_block_58ffa(void)
{
    REGS;
    a0 = a5 + UINT32_C(0xfffffff4); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 310(s0)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x18\n.option pop\n");
    PORT(".Lresident_completion_chain_edge_59006:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_59006\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_63a2c\n");
    __builtin_unreachable();
}

/* Original0x5900A..0x5900C. */
REGION void tsl9_resident_completion_chain_block_5900a(void)
{
    REGS;
    PORT(".Lresident_completion_chain_edge_5900a:\n.option push\n.option rvc\nc.bnez a0,.Lresident_completion_chain_edge_5900a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_chain_block_58fa0\n");
    __builtin_unreachable();
}

/* Original0x5900C..0x59018. */
REGION void tsl9_resident_completion_chain_block_5900c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 310(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_completion_chain_edge_59014:\n.option push\n.option norvc\njal ra,.Lresident_completion_chain_edge_59014\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_6deee\n");
    __builtin_unreachable();
}

/* Original0x59018..0x59032. */
REGION void tsl9_resident_completion_chain_block_59018(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 312(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 316(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a1, a1\n.option pop\n");
    a4 = a4 & a0; LIVE;
    a5 = a5 & a1; LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_completion_chain_edge_59030:\n.option push\n.option rvc\nc.j .Lresident_completion_chain_edge_59030\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_completion_chain_block_58fdc\n");
    __builtin_unreachable();
}

/* Original0x59032..0x59040. */
REGION void tsl9_resident_completion_chain_block_59032(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a4\n.option pop\n");
    a5 = a5 | a1; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000130)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59040..0x59042. */
REGION void tsl9_resident_completion_chain_block_59040(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
