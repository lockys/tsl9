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

/* Two complete conditional SDK record-transition bodies:918B/322i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x580A4..0x5810A. */
REGION void tsl9_candidate_external_flash_580a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 1288(s2)\n.option pop\n");
    a4 = UINT32_C(0x8e89c000); LIVE;
    a4 = a4 + UINT32_C(0xfffffed6); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00555000); LIVE;
    a4 = a4 + UINT32_C(0x00000555); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000ff); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a5 = UINT32_C(0xffffffb3); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000003c)); LIVE;
    PORT(".option push\n.option norvc\naddi s1, a5, 1300\n.option pop\n");
    a4 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb0f8\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000514)) = (uint8_t)0; LIVE;
    PORT(".Lresident_record_transition_edge_58106:\n.option push\n.option norvc\njal ra,.Lresident_record_transition_edge_58106\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x5810A..0x58170. */
REGION void tsl9_resident_record_transition_block_5810a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a2, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1288(s2)\n.option pop\n");
    a1 = UINT32_C(0x00330000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a3 = a3 | a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000050)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a3 = a3 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 59(s0)\n.option pop\n");
    a3 = a4 & UINT32_C(0x0000007f); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffff80); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58988..0x589AA. */
REGION void tsl9_candidate_external_flash_58988(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000098)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".Lresident_record_transition_literal_589a2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_transition_literal_589a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x589AA..0x589AE. */
REGION void tsl9_resident_record_transition_block_589aa(void)
{
    REGS;
    PORT(".Lresident_record_transition_edge_589aa:\n.option push\n.option norvc\nbnez a0,.Lresident_record_transition_edge_589aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c32\n");
    __builtin_unreachable();
}

/* Original0x589AE..0x589C8. */
REGION void tsl9_resident_record_transition_block_589ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s1, 152(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2098\n.option pop\n");
    a3 = a4 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb414\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x309c\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    PORT(".Lresident_record_transition_edge_589c4:\n.option push\n.option norvc\nbne a3,a2,.Lresident_record_transition_edge_589c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58bae\n");
    __builtin_unreachable();
}

/* Original0x589C8..0x589DE. */
REGION void tsl9_resident_record_transition_block_589c8(void)
{
    REGS;
    a4 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 58(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20b8\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a3 = a4 >> UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nsb a3, 61(s0)\n.option pop\n");
    PORT(".Lresident_record_transition_edge_589da:\n.option push\n.option norvc\nbne a3,a2,.Lresident_record_transition_edge_589da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c36\n");
    __builtin_unreachable();
}

/* Original0x589DE..0x589E8. */
REGION void tsl9_resident_record_transition_block_589de(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_transition_edge_589e4:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_transition_edge_589e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c3a\n");
    __builtin_unreachable();
}

/* Original0x589E8..0x589F4. */
REGION void tsl9_resident_record_transition_block_589e8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30b8\n.option pop\n");
    a5 = UINT32_C(0x00000018); LIVE;
    a3 = a4 & UINT32_C(0xffffffbf); LIVE;
    PORT(".Lresident_record_transition_edge_589f0:\n.option push\n.option norvc\nbne a3,a5,.Lresident_record_transition_edge_589f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c3e\n");
    __builtin_unreachable();
}

/* Original0x589F4..0x58A00. */
REGION void tsl9_resident_record_transition_block_589f4(void)
{
    REGS;
    a5 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s1, 4\n.option pop\n");
    PORT(".Lresident_record_transition_edge_589fe:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_transition_edge_589fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58a20\n");
    __builtin_unreachable();
}

/* Original0x58A00..0x58A20. */
REGION void tsl9_resident_record_transition_block_58a00(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 5(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30dc\n.option pop\n");
    a3 = UINT32_C(0x00001000); LIVE;
    a3 = a3 + UINT32_C(0xffffff00); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 & a3; LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 4(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20d4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s1, 6\n.option pop\n");
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 68(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 5(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30dc\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 63(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58A20..0x58A26. */
REGION void tsl9_resident_record_transition_block_58a20(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000010); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_record_transition_edge_58a24:\n.option push\n.option rvc\nc.beqz a4,.Lresident_record_transition_edge_58a24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58aac\n");
    __builtin_unreachable();
}

/* Original0x58A26..0x58A2A. */
REGION void tsl9_resident_record_transition_block_58a26(void)
{
    REGS;
    PORT(".Lresident_record_transition_edge_58a26:\n.option push\n.option norvc\njal ra,.Lresident_record_transition_edge_58a26\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x58A2A..0x58A64. */
REGION void tsl9_resident_record_transition_block_58a2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 59(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a2, 2(s3)\n.option pop\n");
    a5 = UINT32_C(0x00002000); LIVE;
    a5 = a5 + UINT32_C(0xffffff00); LIVE;
    a2 = a2 << UINT32_C(0x00000008); LIVE;
    a2 = a2 & a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    a2 = a2 | a5; LIVE;
    a2 = a2 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a2, a2, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a2, 66(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 60(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a5, 0(s3)\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58a60:\n.option push\n.option norvc\nbgez a5,.Lresident_record_transition_edge_58a60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58a7e\n");
    __builtin_unreachable();
}

/* Original0x58A64..0x58A68. */
REGION void tsl9_resident_record_transition_block_58a64(void)
{
    REGS;
    a5 = UINT32_C(0x0000012c); LIVE;
    __builtin_unreachable();
}

/* Original0x58A68..0x58A78. */
REGION void tsl9_resident_record_transition_block_58a68(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 57(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    a2 = a2 * a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58a74:\n.option push\n.option norvc\nbne a3,a4,.Lresident_record_transition_edge_58a74\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58a82\n");
    __builtin_unreachable();
}

/* Original0x58A78..0x58A7A. */
REGION void tsl9_resident_record_transition_block_58a78(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x58A7A..0x58A7E. */
REGION void tsl9_resident_record_transition_block_58a7a(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_record_transition_edge_58a7c:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58a7c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58a96\n");
    __builtin_unreachable();
}

/* Original0x58A7E..0x58A82. */
REGION void tsl9_resident_record_transition_block_58a7e(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_record_transition_edge_58a80:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58a80\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58a68\n");
    __builtin_unreachable();
}

/* Original0x58A82..0x58A90. */
REGION void tsl9_resident_record_transition_block_58a82(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_record_transition_edge_58a8e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_record_transition_edge_58a8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58b70\n");
    __builtin_unreachable();
}

/* Original0x58A90..0x58A96. */
REGION void tsl9_resident_record_transition_block_58a90(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x000000d7); LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x58A96..0x58AA8. */
REGION void tsl9_resident_record_transition_block_58a96(void)
{
    REGS;
    a2 = a2 - a5; LIVE;
    a5 = UINT32_C(0x80000000); LIVE;
    a4 = a2 + UINT32_C(0xfffffed4); LIVE;
    a5 = a5 ^ UINT32_C(0xfffffed3); LIVE;
    PORT(".Lresident_record_transition_edge_58aa4:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_record_transition_edge_58aa4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c42\n");
    __builtin_unreachable();
}

/* Original0x58AA8..0x58AAC. */
REGION void tsl9_resident_record_transition_block_58aa8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a3, 58(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58AAC..0x58AB4. */
REGION void tsl9_resident_record_transition_block_58aac(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_record_transition_edge_58ab2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_transition_edge_58ab2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58abe\n");
    __builtin_unreachable();
}

/* Original0x58AB4..0x58ABE. */
REGION void tsl9_resident_record_transition_block_58ab4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 57(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_transition_edge_58aba:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_record_transition_edge_58aba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c48\n");
    __builtin_unreachable();
}

/* Original0x58ABE..0x58ACA. */
REGION void tsl9_resident_record_transition_block_58abe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 58(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_record_transition_edge_58ac6:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_record_transition_edge_58ac6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58ACA..0x58AD2. */
REGION void tsl9_resident_record_transition_block_58aca(void)
{
    REGS;
    a4 = UINT32_C(0x00000500); LIVE;
    PORT(".Lresident_record_transition_edge_58ace:\n.option push\n.option norvc\nbltu a4,a2,.Lresident_record_transition_edge_58ace\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58b76\n");
    __builtin_unreachable();
}

/* Original0x58AD2..0x58B0E. */
REGION void tsl9_resident_record_transition_block_58ad2(void)
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
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a1; LIVE;
    a0 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s1, 1300\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffffed5); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 4(a1). */
    PORT(".option push\n.option rvc\n.2byte 0xa1c8\n.option pop\n");
    a2 = a2 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\naddi s4, s1, 1300\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58B0E..0x58B12. */
REGION void tsl9_resident_record_transition_block_58b0e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_record_transition_edge_58b10:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_transition_edge_58b10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58b0e\n");
    __builtin_unreachable();
}

/* Original0x58B12..0x58B1E. */
REGION void tsl9_resident_record_transition_block_58b12(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 57(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58b1a:\n.option push\n.option norvc\njal ra,.Lresident_record_transition_edge_58b1a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_580a4\n");
    __builtin_unreachable();
}

/* Original0x58B1E..0x58B50. */
REGION void tsl9_resident_record_transition_block_58b1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 1340(s3)\n.option pop\n");
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a3 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a3, 4(s4)\n.option pop\n");
    a3 = UINT32_C(0x00000592); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_record_transition_literal_58b48:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_transition_literal_58b48\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58B50..0x58B58. */
REGION void tsl9_resident_record_transition_block_58b50(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_transition_edge_58b56:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_transition_edge_58b56\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58B58..0x58B70. */
REGION void tsl9_resident_record_transition_block_58b58(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58b6c:\n.option push\n.option norvc\njal zero,.Lresident_record_transition_edge_58b6c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58788\n");
    __builtin_unreachable();
}

/* Original0x58B70..0x58B76. */
REGION void tsl9_resident_record_transition_block_58b70(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000004a); LIVE;
    PORT(".Lresident_record_transition_edge_58b74:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58b74\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58a7a\n");
    __builtin_unreachable();
}

/* Original0x58B76..0x58B7E. */
REGION void tsl9_resident_record_transition_block_58b76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 64(s0)\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58b7a:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_transition_edge_58b7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58B7E..0x58B9C. */
REGION void tsl9_resident_record_transition_block_58b7e(void)
{
    REGS;
    a2 = a2 + UINT32_C(0xfffffd8f); LIVE;
    a5 = UINT32_C(0x00000271); LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a2, a5\n.option pop\n");
    a0 = UINT32_C(0x00058000); LIVE;
    PORT(".option push\n.option norvc\naddi a3, s0, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000170); LIVE;
    PORT(".Lresident_record_transition_edge_58b98:\n.option push\n.option norvc\njal ra,.Lresident_record_transition_edge_58b98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x58B9C..0x58BAE. */
REGION void tsl9_resident_record_transition_block_58b9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58BAE..0x58BB2. */
REGION void tsl9_resident_record_transition_block_58bae(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000000e); LIVE;
    PORT(".Lresident_record_transition_edge_58bb0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_record_transition_edge_58bb0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_transition_block_58c4c\n");
    __builtin_unreachable();
}

/* Original0x58BB2..0x58BC2. */
REGION void tsl9_resident_record_transition_block_58bb2(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nli s2, 128\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58bbe:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_record_transition_edge_58bbe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58BC2..0x58BE4. */
REGION void tsl9_resident_record_transition_block_58bc2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s1, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 117(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 118\n.option pop\n");
    PORT(".Lresident_record_transition_literal_58bdc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_transition_literal_58bdc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58BE4..0x58BF0. */
REGION void tsl9_resident_record_transition_block_58be4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 124(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_transition_edge_58bec:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_transition_edge_58bec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58c10\n");
    __builtin_unreachable();
}

/* Original0x58BF0..0x58C10. */
REGION void tsl9_resident_record_transition_block_58bf0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a1, 152(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 124(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 126\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000008); LIVE;
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 125(s0)\n.option pop\n");
    PORT(".Lresident_record_transition_literal_58c08:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_transition_literal_58c08\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58C10..0x58C16. */
REGION void tsl9_resident_record_transition_block_58c10(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c12:\n.option push\n.option norvc\njal ra,.Lresident_record_transition_edge_58c12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_585c8\n");
    __builtin_unreachable();
}

/* Original0x58C16..0x58C1E. */
REGION void tsl9_resident_record_transition_block_58c16(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nli s2, 8\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c1a:\n.option push\n.option norvc\nbne a0,a5,.Lresident_record_transition_edge_58c1a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C1E..0x58C32. */
REGION void tsl9_resident_record_transition_block_58c1e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c2e:\n.option push\n.option norvc\njal zero,.Lresident_record_transition_edge_58c2e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58744\n");
    __builtin_unreachable();
}

/* Original0x58C32..0x58C36. */
REGION void tsl9_resident_record_transition_block_58c32(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c34:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c34\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C36..0x58C3A. */
REGION void tsl9_resident_record_transition_block_58c36(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 5\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c38:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C3A..0x58C3E. */
REGION void tsl9_resident_record_transition_block_58c3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 3\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c3c:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C3E..0x58C42. */
REGION void tsl9_resident_record_transition_block_58c3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 2\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c40:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C42..0x58C48. */
REGION void tsl9_resident_record_transition_block_58c42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s2, 33\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c46:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c46\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C48..0x58C4C. */
REGION void tsl9_resident_record_transition_block_58c48(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 23\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c4a:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c4a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}

/* Original0x58C4C..0x58C52. */
REGION void tsl9_resident_record_transition_block_58c4c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s2, 128\n.option pop\n");
    PORT(".Lresident_record_transition_edge_58c50:\n.option push\n.option rvc\nc.j .Lresident_record_transition_edge_58c50\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_transition_block_58b9c\n");
    __builtin_unreachable();
}
