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

/* Five complete public-SDK registration/callback/RF-config bodies:1546B/540i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x58C52..0x58C94. */
REGION void tsl9_candidate_numeric_callback_58c52(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1100(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nli s6, 178\n.option pop\n");
    PORT(".option push\n.option norvc\nli s7, 180\n.option pop\n");
    PORT(".option push\n.option norvc\nli s8, 182\n.option pop\n");
    PORT(".option push\n.option norvc\nli s9, 179\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s2, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s5, 564\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58C94..0x58C9A. */
REGION void tsl9_resident_callback_registration_block_58c94(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x207c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58c96:\n.option push\n.option norvc\nbne a5,s6,.Lresident_callback_registration_edge_58c96\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58cb0\n");
    __builtin_unreachable();
}

/* Original0x58C9A..0x58CA2. */
REGION void tsl9_resident_callback_registration_block_58c9a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_58ca0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_58ca0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58CA2..0x58CAC. */
REGION void tsl9_resident_callback_registration_block_58ca2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s2)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58ca8:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58ca8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58988\n");
    __builtin_unreachable();
}

/* Original0x58CAC..0x58CAE. */
REGION void tsl9_resident_callback_registration_block_58cac(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58cac:\n.option push\n.option rvc\nc.beqz a0,.Lresident_callback_registration_edge_58cac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58c94\n");
    __builtin_unreachable();
}

/* Original0x58CAE..0x58CB0. */
REGION void tsl9_resident_callback_registration_block_58cae(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58cae:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58cae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58CB0..0x58CB4. */
REGION void tsl9_resident_callback_registration_block_58cb0(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58cb0:\n.option push\n.option norvc\nbne a5,s7,.Lresident_callback_registration_edge_58cb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58d40\n");
    __builtin_unreachable();
}

/* Original0x58CB4..0x58CC2. */
REGION void tsl9_resident_callback_registration_block_58cb4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3398\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_58cc0:\n.option push\n.option rvc\nc.beqz a4,.Lresident_callback_registration_edge_58cc0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58CC2..0x58CEA. */
REGION void tsl9_resident_callback_registration_block_58cc2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s3, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 8(s2)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x000000f8); LIVE;
    a0 = a0 * a5; LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_callback_registration_edge_58ce6:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58ce6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x58CEA..0x58CF4. */
REGION void tsl9_resident_callback_registration_block_58cea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 564(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58CF4..0x58D08. */
REGION void tsl9_resident_callback_registration_block_58cf4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nadd a5, a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, a5, a0\n.option pop\n");
    a0 = a0 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 4(s2)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d06:\n.option push\n.option rvc\nc.bnez a0,.Lresident_callback_registration_edge_58d06\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d0c\n");
    __builtin_unreachable();
}

/* Original0x58D08..0x58D0C. */
REGION void tsl9_resident_callback_registration_block_58d08(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58d08:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_callback_registration_edge_58d08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58d10\n");
    __builtin_unreachable();
}

/* Original0x58D0C..0x58D10. */
REGION void tsl9_resident_callback_registration_block_58d0c(void)
{
    REGS;
    a4 = a5 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x58D10..0x58D16. */
REGION void tsl9_resident_callback_registration_block_58d10(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a4, 96(s0)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d12:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58d12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x58D16..0x58D1C. */
REGION void tsl9_resident_callback_registration_block_58d16(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d18:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58d18\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58498\n");
    __builtin_unreachable();
}

/* Original0x58D1C..0x58D22. */
REGION void tsl9_resident_callback_registration_block_58d1c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 4(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x205c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d1e:\n.option push\n.option norvc\nbeqz a5,.Lresident_callback_registration_edge_58d1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58e5e\n");
    __builtin_unreachable();
}

/* Original0x58D22..0x58D40. */
REGION void tsl9_resident_callback_registration_block_58d22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d3c:\n.option push\n.option norvc\njal zero,.Lresident_callback_registration_edge_58d3c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57dae\n");
    __builtin_unreachable();
}

/* Original0x58D40..0x58D44. */
REGION void tsl9_resident_callback_registration_block_58d40(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58d40:\n.option push\n.option norvc\nbne a5,s8,.Lresident_callback_registration_edge_58d40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58dcc\n");
    __builtin_unreachable();
}

/* Original0x58D44..0x58D80. */
REGION void tsl9_resident_callback_registration_block_58d44(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a2 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s1, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_58d7e:\n.option push\n.option rvc\nc.bnez a4,.Lresident_callback_registration_edge_58d7e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58db4\n");
    __builtin_unreachable();
}

/* Original0x58D80..0x58D84. */
REGION void tsl9_resident_callback_registration_block_58d80(void)
{
    REGS;
    a4 = UINT32_C(0x00000196); LIVE;
    __builtin_unreachable();
}

/* Original0x58D84..0x58D90. */
REGION void tsl9_resident_callback_registration_block_58d84(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_callback_registration_literal_58d88:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_58d88\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58D90..0x58D98. */
REGION void tsl9_resident_callback_registration_block_58d90(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_58d96:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_58d96\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58da8\n");
    __builtin_unreachable();
}

/* Original0x58D98..0x58DA0. */
REGION void tsl9_resident_callback_registration_block_58d98(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58d9c:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58d9c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x58DA0..0x58DA6. */
REGION void tsl9_resident_callback_registration_block_58da0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58da2:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58da2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_588b4\n");
    __builtin_unreachable();
}

/* Original0x58DA6..0x58DA8. */
REGION void tsl9_resident_callback_registration_block_58da6(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58da6:\n.option push\n.option rvc\nc.beqz a0,.Lresident_callback_registration_edge_58da6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58DA8..0x58DB4. */
REGION void tsl9_resident_callback_registration_block_58da8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 62(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 62(s0)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58db2:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58db2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58DB4..0x58DC0. */
REGION void tsl9_resident_callback_registration_block_58db4(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_58dbc:\n.option push\n.option norvc\nbne a4,a2,.Lresident_callback_registration_edge_58dbc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58dc6\n");
    __builtin_unreachable();
}

/* Original0x58DC0..0x58DC6. */
REGION void tsl9_resident_callback_registration_block_58dc0(void)
{
    REGS;
    a4 = UINT32_C(0x0000043e); LIVE;
    PORT(".Lresident_callback_registration_edge_58dc4:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58dc4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58d84\n");
    __builtin_unreachable();
}

/* Original0x58DC6..0x58DCC. */
REGION void tsl9_resident_callback_registration_block_58dc6(void)
{
    REGS;
    a4 = UINT32_C(0x000001be); LIVE;
    PORT(".Lresident_callback_registration_edge_58dca:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58dca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58d84\n");
    __builtin_unreachable();
}

/* Original0x58DCC..0x58DD0. */
REGION void tsl9_resident_callback_registration_block_58dcc(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58dcc:\n.option push\n.option norvc\nbne a5,s9,.Lresident_callback_registration_edge_58dcc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58de4\n");
    __builtin_unreachable();
}

/* Original0x58DD0..0x58DD8. */
REGION void tsl9_resident_callback_registration_block_58dd0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_58dd6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_58dd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58DD8..0x58DE2. */
REGION void tsl9_resident_callback_registration_block_58dd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s2)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58dde:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58dde\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58788\n");
    __builtin_unreachable();
}

/* Original0x58DE2..0x58DE4. */
REGION void tsl9_resident_callback_registration_block_58de2(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58de2:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58de2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58cac\n");
    __builtin_unreachable();
}

/* Original0x58DE4..0x58DEC. */
REGION void tsl9_resident_callback_registration_block_58de4(void)
{
    REGS;
    a4 = UINT32_C(0x000000b5); LIVE;
    PORT(".Lresident_callback_registration_edge_58de8:\n.option push\n.option norvc\nbne a5,a4,.Lresident_callback_registration_edge_58de8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58DEC..0x58DF4. */
REGION void tsl9_resident_callback_registration_block_58dec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s4)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_58df2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_58df2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58d1c\n");
    __builtin_unreachable();
}

/* Original0x58DF4..0x58E0A. */
REGION void tsl9_resident_callback_registration_block_58df4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 60(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s4)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 564(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s10, 8(s3)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58e06:\n.option push\n.option norvc\nbleu a3,a4,.Lresident_callback_registration_edge_58e06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58e4a\n");
    __builtin_unreachable();
}

/* Original0x58E0A..0x58E0C. */
REGION void tsl9_resident_callback_registration_block_58e0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58E0C..0x58E1C. */
REGION void tsl9_resident_callback_registration_block_58e0c(void)
{
    REGS;
    a2 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000004d8); LIVE;
    __builtin_unreachable();
}

/* Original0x58E1C..0x58E26. */
REGION void tsl9_resident_callback_registration_block_58e1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a0, s10, a0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_callback_registration_edge_58e22:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_58e22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x58E26..0x58E38. */
REGION void tsl9_resident_callback_registration_block_58e26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a5, a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, a5, a0\n.option pop\n");
    a0 = a0 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 4(s3)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58e36:\n.option push\n.option rvc\nc.bnez a0,.Lresident_callback_registration_edge_58e36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_58e3c\n");
    __builtin_unreachable();
}

/* Original0x58E38..0x58E3C. */
REGION void tsl9_resident_callback_registration_block_58e38(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_58e38:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_callback_registration_edge_58e38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_58e40\n");
    __builtin_unreachable();
}

/* Original0x58E3C..0x58E40. */
REGION void tsl9_resident_callback_registration_block_58e3c(void)
{
    REGS;
    a4 = a5 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x58E40..0x58E4A. */
REGION void tsl9_resident_callback_registration_block_58e40(void)
{
    REGS;
    a5 = UINT32_C(0xffffffb6); LIVE;
    PORT(".option push\n.option rvc\nsw a4, 96(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa07c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_58e48:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58e48\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58c94\n");
    __builtin_unreachable();
}

/* Original0x58E4A..0x58E4C. */
REGION void tsl9_resident_callback_registration_block_58e4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58E4C..0x58E5E. */
REGION void tsl9_resident_callback_registration_block_58e4c(void)
{
    REGS;
    a2 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000f8); LIVE;
    PORT(".Lresident_callback_registration_edge_58e5c:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_58e5c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_58e1c\n");
    __builtin_unreachable();
}

/* Original0x58E5E..0x58E7A. */
REGION void tsl9_resident_callback_registration_block_58e5e(void)
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
    PORT(".option push\n.option rvc\nlw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58EF2..0x58F14. */
REGION void tsl9_candidate_callback_registration_58ef2(void)
{
    REGS;
    a5 = UINT32_C(0x00058000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xfffffcbe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000450)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00059000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc52); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000004f0)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60516..0x60548. */
REGION void tsl9_candidate_numeric_callback_60516(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1080(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 162\n.option pop\n");
    PORT(".option push\n.option norvc\nli s3, 161\n.option pop\n");
    PORT(".option push\n.option norvc\nli s2, 166\n.option pop\n");
    PORT(".option push\n.option norvc\nli s6, 164\n.option pop\n");
    PORT(".option push\n.option norvc\nli s4, 165\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60548..0x6054E. */
REGION void tsl9_resident_callback_registration_block_60548(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_6054a:\n.option push\n.option norvc\nbne a5,s5,.Lresident_callback_registration_edge_6054a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_6060e\n");
    __builtin_unreachable();
}

/* Original0x6054E..0x6058A. */
REGION void tsl9_resident_callback_registration_block_6054e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a2 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s1, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_60588:\n.option push\n.option rvc\nc.bnez a4,.Lresident_callback_registration_edge_60588\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_605e4\n");
    __builtin_unreachable();
}

/* Original0x6058A..0x6058E. */
REGION void tsl9_resident_callback_registration_block_6058a(void)
{
    REGS;
    a4 = UINT32_C(0x00000196); LIVE;
    __builtin_unreachable();
}

/* Original0x6058E..0x6059A. */
REGION void tsl9_resident_callback_registration_block_6058e(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_callback_registration_literal_60592:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_60592\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6059A..0x605A2. */
REGION void tsl9_resident_callback_registration_block_6059a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_605a0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_605a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x605A2..0x605AA. */
REGION void tsl9_resident_callback_registration_block_605a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_605a6:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_605a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x605AA..0x605B0. */
REGION void tsl9_resident_callback_registration_block_605aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_605ac:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_605ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6014e\n");
    __builtin_unreachable();
}

/* Original0x605B0..0x605B2. */
REGION void tsl9_resident_callback_registration_block_605b0(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_605b0:\n.option push\n.option rvc\nc.beqz a0,.Lresident_callback_registration_edge_605b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x605B2..0x605BA. */
REGION void tsl9_resident_callback_registration_block_605b2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 20(s0)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_605b6:\n.option push\n.option norvc\nbltz a5,.Lresident_callback_registration_edge_605b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_605fc\n");
    __builtin_unreachable();
}

/* Original0x605BA..0x605BE. */
REGION void tsl9_resident_callback_registration_block_605ba(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x605BE..0x605C6. */
REGION void tsl9_resident_callback_registration_block_605be(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x382c\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_605c2:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_605c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e6a\n");
    __builtin_unreachable();
}

/* Original0x605C6..0x605C8. */
REGION void tsl9_resident_callback_registration_block_605c6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a0, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb808\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x605C8..0x605CE. */
REGION void tsl9_resident_callback_registration_block_605c8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x241c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_605ca:\n.option push\n.option norvc\nbeqz a5,.Lresident_callback_registration_edge_605ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_6071a\n");
    __builtin_unreachable();
}

/* Original0x605CE..0x605E4. */
REGION void tsl9_resident_callback_registration_block_605ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_605e0:\n.option push\n.option norvc\njal zero,.Lresident_callback_registration_edge_605e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6020a\n");
    __builtin_unreachable();
}

/* Original0x605E4..0x605F0. */
REGION void tsl9_resident_callback_registration_block_605e4(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_605ec:\n.option push\n.option norvc\nbne a4,a2,.Lresident_callback_registration_edge_605ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_605f6\n");
    __builtin_unreachable();
}

/* Original0x605F0..0x605F6. */
REGION void tsl9_resident_callback_registration_block_605f0(void)
{
    REGS;
    a4 = UINT32_C(0x0000043e); LIVE;
    PORT(".Lresident_callback_registration_edge_605f4:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_605f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_6058e\n");
    __builtin_unreachable();
}

/* Original0x605F6..0x605FC. */
REGION void tsl9_resident_callback_registration_block_605f6(void)
{
    REGS;
    a4 = UINT32_C(0x000001be); LIVE;
    PORT(".Lresident_callback_registration_edge_605fa:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_605fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_6058e\n");
    __builtin_unreachable();
}

/* Original0x605FC..0x60606. */
REGION void tsl9_resident_callback_registration_block_605fc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x383c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_callback_registration_edge_60604:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_60604\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_6060a\n");
    __builtin_unreachable();
}

/* Original0x60606..0x6060A. */
REGION void tsl9_resident_callback_registration_block_60606(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb83c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60608:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_60608\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_605be\n");
    __builtin_unreachable();
}

/* Original0x6060A..0x6060E. */
REGION void tsl9_resident_callback_registration_block_6060a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_callback_registration_edge_6060c:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_6060c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_60606\n");
    __builtin_unreachable();
}

/* Original0x6060E..0x60612. */
REGION void tsl9_resident_callback_registration_block_6060e(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_6060e:\n.option push\n.option norvc\nbne a5,s3,.Lresident_callback_registration_edge_6060e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_6062c\n");
    __builtin_unreachable();
}

/* Original0x60612..0x6061A. */
REGION void tsl9_resident_callback_registration_block_60612(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_60618:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_60618\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x6061A..0x60624. */
REGION void tsl9_resident_callback_registration_block_6061a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60620:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_60620\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5fcdc\n");
    __builtin_unreachable();
}

/* Original0x60624..0x6062A. */
REGION void tsl9_resident_callback_registration_block_60624(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60626:\n.option push\n.option norvc\nbne a5,s3,.Lresident_callback_registration_edge_60626\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_60548\n");
    __builtin_unreachable();
}

/* Original0x6062A..0x6062C. */
REGION void tsl9_resident_callback_registration_block_6062a(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_6062a:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_6062a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x6062C..0x60630. */
REGION void tsl9_resident_callback_registration_block_6062c(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_6062c:\n.option push\n.option norvc\nbne a5,s2,.Lresident_callback_registration_edge_6062c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_606e4\n");
    __builtin_unreachable();
}

/* Original0x60630..0x6066C. */
REGION void tsl9_resident_callback_registration_block_60630(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a2 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s1, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_6066a:\n.option push\n.option rvc\nc.bnez a4,.Lresident_callback_registration_edge_6066a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_606ba\n");
    __builtin_unreachable();
}

/* Original0x6066C..0x60670. */
REGION void tsl9_resident_callback_registration_block_6066c(void)
{
    REGS;
    a4 = UINT32_C(0x00000196); LIVE;
    __builtin_unreachable();
}

/* Original0x60670..0x6067C. */
REGION void tsl9_resident_callback_registration_block_60670(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_callback_registration_literal_60674:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_60674\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6067C..0x60684. */
REGION void tsl9_resident_callback_registration_block_6067c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_60682:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_60682\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_60694\n");
    __builtin_unreachable();
}

/* Original0x60684..0x6068C. */
REGION void tsl9_resident_callback_registration_block_60684(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60688:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_60688\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x6068C..0x60692. */
REGION void tsl9_resident_callback_registration_block_6068c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_6068e:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_6068e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5f98e\n");
    __builtin_unreachable();
}

/* Original0x60692..0x60694. */
REGION void tsl9_resident_callback_registration_block_60692(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60692:\n.option push\n.option rvc\nc.beqz a0,.Lresident_callback_registration_edge_60692\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_606aa\n");
    __builtin_unreachable();
}

/* Original0x60694..0x6069C. */
REGION void tsl9_resident_callback_registration_block_60694(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 20(s0)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60698:\n.option push\n.option norvc\nbltz a5,.Lresident_callback_registration_edge_60698\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_606d2\n");
    __builtin_unreachable();
}

/* Original0x6069C..0x606A0. */
REGION void tsl9_resident_callback_registration_block_6069c(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x606A0..0x606A8. */
REGION void tsl9_resident_callback_registration_block_606a0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x382c\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_606a4:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_606a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e6a\n");
    __builtin_unreachable();
}

/* Original0x606A8..0x606AA. */
REGION void tsl9_resident_callback_registration_block_606a8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a0, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb808\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x606AA..0x606B4. */
REGION void tsl9_resident_callback_registration_block_606aa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2438\n.option pop\n");
    a5 = UINT32_C(0x000000a5); LIVE;
    PORT(".Lresident_callback_registration_edge_606b0:\n.option push\n.option norvc\nbne a4,a5,.Lresident_callback_registration_edge_606b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x606B4..0x606B8. */
REGION void tsl9_resident_callback_registration_block_606b4(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_606b4:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_606b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5f0d2\n");
    __builtin_unreachable();
}

/* Original0x606B8..0x606BA. */
REGION void tsl9_resident_callback_registration_block_606b8(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_606b8:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_606b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x606BA..0x606C6. */
REGION void tsl9_resident_callback_registration_block_606ba(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_callback_registration_edge_606c2:\n.option push\n.option norvc\nbne a4,a2,.Lresident_callback_registration_edge_606c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_606cc\n");
    __builtin_unreachable();
}

/* Original0x606C6..0x606CC. */
REGION void tsl9_resident_callback_registration_block_606c6(void)
{
    REGS;
    a4 = UINT32_C(0x0000043e); LIVE;
    PORT(".Lresident_callback_registration_edge_606ca:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_606ca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_60670\n");
    __builtin_unreachable();
}

/* Original0x606CC..0x606D2. */
REGION void tsl9_resident_callback_registration_block_606cc(void)
{
    REGS;
    a4 = UINT32_C(0x000001be); LIVE;
    PORT(".Lresident_callback_registration_edge_606d0:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_606d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_60670\n");
    __builtin_unreachable();
}

/* Original0x606D2..0x606DC. */
REGION void tsl9_resident_callback_registration_block_606d2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x383c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_callback_registration_edge_606da:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_606da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_606e0\n");
    __builtin_unreachable();
}

/* Original0x606DC..0x606E0. */
REGION void tsl9_resident_callback_registration_block_606dc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb83c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_606de:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_606de\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_606a0\n");
    __builtin_unreachable();
}

/* Original0x606E0..0x606E4. */
REGION void tsl9_resident_callback_registration_block_606e0(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_callback_registration_edge_606e2:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_606e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_606dc\n");
    __builtin_unreachable();
}

/* Original0x606E4..0x606E8. */
REGION void tsl9_resident_callback_registration_block_606e4(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_606e4:\n.option push\n.option norvc\nbne a5,s6,.Lresident_callback_registration_edge_606e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_60714\n");
    __builtin_unreachable();
}

/* Original0x606E8..0x606F0. */
REGION void tsl9_resident_callback_registration_block_606e8(void)
{
    REGS;
    PORT(".Lresident_callback_registration_literal_606e8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_606e8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x606F0..0x606F8. */
REGION void tsl9_resident_callback_registration_block_606f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_606f6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_606f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_60702\n");
    __builtin_unreachable();
}

/* Original0x606F8..0x60702. */
REGION void tsl9_resident_callback_registration_block_606f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s1)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_606fe:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_606fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5f234\n");
    __builtin_unreachable();
}

/* Original0x60702..0x60708. */
REGION void tsl9_resident_callback_registration_block_60702(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60704:\n.option push\n.option norvc\nbne a5,s4,.Lresident_callback_registration_edge_60704\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_6070c\n");
    __builtin_unreachable();
}

/* Original0x60708..0x6070C. */
REGION void tsl9_resident_callback_registration_block_60708(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60708:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_60708\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5f0d2\n");
    __builtin_unreachable();
}

/* Original0x6070C..0x60712. */
REGION void tsl9_resident_callback_registration_block_6070c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_6070e:\n.option push\n.option norvc\nbeq a5,s2,.Lresident_callback_registration_edge_6070e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_60548\n");
    __builtin_unreachable();
}

/* Original0x60712..0x60714. */
REGION void tsl9_resident_callback_registration_block_60712(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60712:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_60712\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x60714..0x60718. */
REGION void tsl9_resident_callback_registration_block_60714(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60714:\n.option push\n.option norvc\nbeq a5,s4,.Lresident_callback_registration_edge_60714\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_60708\n");
    __builtin_unreachable();
}

/* Original0x60718..0x6071A. */
REGION void tsl9_resident_callback_registration_block_60718(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60718:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_60718\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_605c8\n");
    __builtin_unreachable();
}

/* Original0x6071A..0x60724. */
REGION void tsl9_resident_callback_registration_block_6071a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_callback_registration_edge_60722:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_60722\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_60740\n");
    __builtin_unreachable();
}

/* Original0x60724..0x60740. */
REGION void tsl9_resident_callback_registration_block_60724(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_callback_registration_literal_60738:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_60738\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60740..0x60754. */
REGION void tsl9_resident_callback_registration_block_60740(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60856..0x60864. */
REGION void tsl9_candidate_callback_registration_60856(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019f)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_60862:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_60862\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_60874\n");
    __builtin_unreachable();
}

/* Original0x60864..0x60870. */
REGION void tsl9_resident_callback_registration_block_60864(void)
{
    REGS;
    a0 = UINT32_C(0x00053000); LIVE;
    a0 = a0 + UINT32_C(0x0000052c); LIVE;
    PORT(".Lresident_callback_registration_edge_6086c:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_6086c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_process_event_register_43c4e\n");
    __builtin_unreachable();
}

/* Original0x60870..0x60874. */
REGION void tsl9_resident_callback_registration_block_60870(void)
{
    REGS;
    PORT(".Lresident_callback_registration_edge_60870:\n.option push\n.option norvc\njal ra,.Lresident_callback_registration_edge_60870\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5362e\n");
    __builtin_unreachable();
}

/* Original0x60874..0x6089A. */
REGION void tsl9_resident_callback_registration_block_60874(void)
{
    REGS;
    a5 = UINT32_C(0x0005f000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xfffff8bc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000043c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00060000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000516); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000004f8)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64BAE..0x64BB4. */
REGION void tsl9_candidate_RF_Config_64bae(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)); LIVE;
    PORT(".Lresident_callback_registration_edge_64bb0:\n.option push\n.option norvc\nbeqz a5,.Lresident_callback_registration_edge_64bb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_64ce8\n");
    __builtin_unreachable();
}

/* Original0x64BB4..0x64BC8. */
REGION void tsl9_resident_callback_registration_block_64bb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211c\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_callback_registration_edge_64bc6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_64bc6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64bce\n");
    __builtin_unreachable();
}

/* Original0x64BC8..0x64BCE. */
REGION void tsl9_resident_callback_registration_block_64bc8(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_callback_registration_edge_64bcc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_64bcc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c84\n");
    __builtin_unreachable();
}

/* Original0x64BCE..0x64BE4. */
REGION void tsl9_resident_callback_registration_block_64bce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s2, 1344\n.option pop\n");
    PORT(".Lresident_callback_registration_literal_64bdc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_64bdc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64BE4..0x64BF6. */
REGION void tsl9_resident_callback_registration_block_64be4(void)
{
    REGS;
    a2 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s2, 1344\n.option pop\n");
    PORT(".Lresident_callback_registration_literal_64bee:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_64bee\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64BF6..0x64C02. */
REGION void tsl9_resident_callback_registration_block_64bf6(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s2, 1344\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 25(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3f9c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s2, 1344\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c00:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_64c00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c08\n");
    __builtin_unreachable();
}

/* Original0x64C02..0x64C08. */
REGION void tsl9_resident_callback_registration_block_64c02(void)
{
    REGS;
    a5 = UINT32_C(0x00000028); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc1c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C08..0x64C0C. */
REGION void tsl9_resident_callback_registration_block_64c08(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c3c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c0a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_64c0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c10\n");
    __builtin_unreachable();
}

/* Original0x64C0C..0x64C10. */
REGION void tsl9_resident_callback_registration_block_64c0c(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C10..0x64C14. */
REGION void tsl9_resident_callback_registration_block_64c10(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c12:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_64c12\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c18\n");
    __builtin_unreachable();
}

/* Original0x64C14..0x64C18. */
REGION void tsl9_resident_callback_registration_block_64c14(void)
{
    REGS;
    a5 = UINT32_C(0x00000011); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C18..0x64C1C. */
REGION void tsl9_resident_callback_registration_block_64c18(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c5c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c1a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_64c1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c20\n");
    __builtin_unreachable();
}

/* Original0x64C1C..0x64C20. */
REGION void tsl9_resident_callback_registration_block_64c1c(void)
{
    REGS;
    a5 = UINT32_C(0xfffffffb); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac5c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C20..0x64C24. */
REGION void tsl9_resident_callback_registration_block_64c20(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5c\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c22:\n.option push\n.option rvc\nc.bnez a5,.Lresident_callback_registration_edge_64c22\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c28\n");
    __builtin_unreachable();
}

/* Original0x64C24..0x64C28. */
REGION void tsl9_resident_callback_registration_block_64c24(void)
{
    REGS;
    a5 = UINT32_C(0xfffffffb); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C28..0x64C30. */
REGION void tsl9_resident_callback_registration_block_64c28(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_callback_registration_edge_64c2e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_64c2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c44\n");
    __builtin_unreachable();
}

/* Original0x64C30..0x64C3E. */
REGION void tsl9_resident_callback_registration_block_64c30(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    a4 = UINT32_C(0x0024b000); LIVE;
    a4 = a4 + UINT32_C(0xfffffe9f); LIVE;
    PORT(".Lresident_callback_registration_edge_64c3a:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_callback_registration_edge_64c3a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_64c90\n");
    __builtin_unreachable();
}

/* Original0x64C3E..0x64C42. */
REGION void tsl9_resident_callback_registration_block_64c3e(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    __builtin_unreachable();
}

/* Original0x64C42..0x64C44. */
REGION void tsl9_resident_callback_registration_block_64c42(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C44..0x64C54. */
REGION void tsl9_resident_callback_registration_block_64c44(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 1376\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".Lresident_callback_registration_edge_64c52:\n.option push\n.option rvc\nc.beqz a0,.Lresident_callback_registration_edge_64c52\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c5c\n");
    __builtin_unreachable();
}

/* Original0x64C54..0x64C5C. */
REGION void tsl9_resident_callback_registration_block_64c54(void)
{
    REGS;
    PORT(".Lresident_callback_registration_literal_64c54:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_64c54\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C5C..0x64C68. */
REGION void tsl9_resident_callback_registration_block_64c5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 4(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_callback_registration_edge_64c66:\n.option push\n.option rvc\nc.beqz a5,.Lresident_callback_registration_edge_64c66\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_callback_registration_block_64c7a\n");
    __builtin_unreachable();
}

/* Original0x64C68..0x64C78. */
REGION void tsl9_resident_callback_registration_block_64c68(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c48\n.option pop\n");
    a1 = UINT32_C(0x00000049); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_callback_registration_literal_64c70:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_callback_registration_literal_64c70\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C78..0x64C7A. */
REGION void tsl9_resident_callback_registration_block_64c78(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 4(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C7A..0x64C84. */
REGION void tsl9_resident_callback_registration_block_64c7a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x301c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 15(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb4fc\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a5, 20(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64C84..0x64C90. */
REGION void tsl9_resident_callback_registration_block_64c84(void)
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

/* Original0x64C90..0x64C9C. */
REGION void tsl9_resident_callback_registration_block_64c90(void)
{
    REGS;
    a4 = UINT32_C(0x00250000); LIVE;
    a3 = a4 + UINT32_C(0x0000048f); LIVE;
    PORT(".Lresident_callback_registration_edge_64c98:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_callback_registration_edge_64c98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_64cb2\n");
    __builtin_unreachable();
}

/* Original0x64C9C..0x64CB2. */
REGION void tsl9_resident_callback_registration_block_64c9c(void)
{
    REGS;
    a4 = UINT32_C(0xffdb6000); LIVE;
    a4 = a4 + UINT32_C(0xfffff930); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x000007d0); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_callback_registration_edge_64cb0:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_64cb0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_64c42\n");
    __builtin_unreachable();
}

/* Original0x64CB2..0x64CBA. */
REGION void tsl9_resident_callback_registration_block_64cb2(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000490); LIVE;
    PORT(".Lresident_callback_registration_edge_64cb6:\n.option push\n.option norvc\nbne a5,a4,.Lresident_callback_registration_edge_64cb6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_64cc0\n");
    __builtin_unreachable();
}

/* Original0x64CBA..0x64CC0. */
REGION void tsl9_resident_callback_registration_block_64cba(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    PORT(".Lresident_callback_registration_edge_64cbe:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_64cbe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_64c42\n");
    __builtin_unreachable();
}

/* Original0x64CC0..0x64CCC. */
REGION void tsl9_resident_callback_registration_block_64cc0(void)
{
    REGS;
    a4 = UINT32_C(0x0025d000); LIVE;
    a4 = a4 + UINT32_C(0x0000077f); LIVE;
    PORT(".Lresident_callback_registration_edge_64cc8:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_callback_registration_edge_64cc8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_callback_registration_block_64ce2\n");
    __builtin_unreachable();
}

/* Original0x64CCC..0x64CE2. */
REGION void tsl9_resident_callback_registration_block_64ccc(void)
{
    REGS;
    a4 = UINT32_C(0xffdb6000); LIVE;
    a4 = a4 + UINT32_C(0xfffff930); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x000007d0); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_callback_registration_edge_64ce0:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_64ce0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_64c42\n");
    __builtin_unreachable();
}

/* Original0x64CE2..0x64CE8. */
REGION void tsl9_resident_callback_registration_block_64ce2(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lresident_callback_registration_edge_64ce6:\n.option push\n.option rvc\nc.j .Lresident_callback_registration_edge_64ce6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_callback_registration_block_64c42\n");
    __builtin_unreachable();
}

/* Original0x64CE8..0x64CEC. */
REGION void tsl9_resident_callback_registration_block_64ce8(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
