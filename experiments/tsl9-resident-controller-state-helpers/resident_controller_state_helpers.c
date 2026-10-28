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

/* Four complete conditional controller-state bodies:780B/273i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x55C6E..0x55C84. */
REGION void tsl9_candidate_unprovided_flash_55c6e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000026)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_55c80:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_controller_state_helpers_edge_55c80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_55c92\n");
    __builtin_unreachable();
}

/* Original0x55C84..0x55C8A. */
REGION void tsl9_resident_controller_state_helpers_block_55c84(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_controller_state_helpers_edge_55c86:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_55c86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x55C8A..0x55C92. */
REGION void tsl9_resident_controller_state_helpers_block_55c8a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 38(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55C92..0x55CC4. */
REGION void tsl9_resident_controller_state_helpers_block_55c92(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 72(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, s0, 38\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000060); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 70(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a0 = UINT32_C(0x00056000); LIVE;
    a0 = a0 + UINT32_C(0xfffffc32); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_55cc0:\n.option push\n.option norvc\njal zero,.Lresident_controller_state_helpers_edge_55cc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x55CC4..0x55CDA. */
REGION void tsl9_candidate_unprovided_flash_55cc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000027)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_55cd6:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_controller_state_helpers_edge_55cd6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_55ce8\n");
    __builtin_unreachable();
}

/* Original0x55CDA..0x55CE0. */
REGION void tsl9_resident_controller_state_helpers_block_55cda(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_controller_state_helpers_edge_55cdc:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_55cdc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x55CE0..0x55CE8. */
REGION void tsl9_resident_controller_state_helpers_block_55ce0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 39(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55CE8..0x55D00. */
REGION void tsl9_resident_controller_state_helpers_block_55ce8(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, s0, 39\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a0 = UINT32_C(0x00057000); LIVE;
    a0 = a0 + UINT32_C(0xfffffcb2); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_55cfc:\n.option push\n.option norvc\njal zero,.Lresident_controller_state_helpers_edge_55cfc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x5649C..0x564AE. */
REGION void tsl9_candidate_unprovided_flash_5649c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000000b4)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_564aa:\n.option push\n.option norvc\nbleu a3,a4,.Lresident_controller_state_helpers_edge_564aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5656e\n");
    __builtin_unreachable();
}

/* Original0x564AE..0x564BC. */
REGION void tsl9_resident_controller_state_helpers_block_564ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 156(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x564BC..0x564BE. */
REGION void tsl9_resident_controller_state_helpers_block_564bc(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_564bc:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_564bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_564ce\n");
    __builtin_unreachable();
}

/* Original0x564BE..0x564C0. */
REGION void tsl9_resident_controller_state_helpers_block_564be(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_564be:\n.option push\n.option rvc\nc.bnez s0,.Lresident_controller_state_helpers_edge_564be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_564d6\n");
    __builtin_unreachable();
}

/* Original0x564C0..0x564C4. */
REGION void tsl9_resident_controller_state_helpers_block_564c0(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x564C4..0x564CE. */
REGION void tsl9_resident_controller_state_helpers_block_564c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x564CE..0x564D2. */
REGION void tsl9_resident_controller_state_helpers_block_564ce(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 29(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3fd8\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_564d0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_controller_state_helpers_edge_564d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_564c4\n");
    __builtin_unreachable();
}

/* Original0x564D2..0x564D6. */
REGION void tsl9_resident_controller_state_helpers_block_564d2(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_564d4:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_564d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_564bc\n");
    __builtin_unreachable();
}

/* Original0x564D6..0x564DA. */
REGION void tsl9_resident_controller_state_helpers_block_564d6(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_564d6:\n.option push\n.option norvc\nbne s0,a0,.Lresident_controller_state_helpers_edge_564d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_564de\n");
    __builtin_unreachable();
}

/* Original0x564DA..0x564DE. */
REGION void tsl9_resident_controller_state_helpers_block_564da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 0(s0)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_564dc:\n.option push\n.option rvc\nc.beqz s0,.Lresident_controller_state_helpers_edge_564dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_564c0\n");
    __builtin_unreachable();
}

/* Original0x564DE..0x564E2. */
REGION void tsl9_resident_controller_state_helpers_block_564de(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x343c\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_564e0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_564e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_5656a\n");
    __builtin_unreachable();
}

/* Original0x564E2..0x564EE. */
REGION void tsl9_resident_controller_state_helpers_block_564e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 140(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000008c)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_564ea:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_controller_state_helpers_edge_564ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5656a\n");
    __builtin_unreachable();
}

/* Original0x564EE..0x564FA. */
REGION void tsl9_resident_controller_state_helpers_block_564ee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 28(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2d58\n.option pop\n");
    a5 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_564f6:\n.option push\n.option norvc\nbne a4,a5,.Lresident_controller_state_helpers_edge_564f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56542\n");
    __builtin_unreachable();
}

/* Original0x564FA..0x5651C. */
REGION void tsl9_resident_controller_state_helpers_block_564fa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3e\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5e\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005a)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005c)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a0, 8(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x250a\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56518:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_56518\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x5651C..0x56528. */
REGION void tsl9_resident_controller_state_helpers_block_5651c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xbcdc\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 28(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2cdc\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 28(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xacdc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56528..0x56542. */
REGION void tsl9_resident_controller_state_helpers_block_56528(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 104\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_literal_5653a:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_controller_state_helpers_literal_5653a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56542..0x56564. */
REGION void tsl9_resident_controller_state_helpers_block_56542(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d3e\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 116(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 118(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 60(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d5e\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 90(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 62(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d7e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 92(s0)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56560:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_56560\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56564..0x5656A. */
REGION void tsl9_resident_controller_state_helpers_block_56564(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5c\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56568:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_56568\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_56528\n");
    __builtin_unreachable();
}

/* Original0x5656A..0x5656E. */
REGION void tsl9_resident_controller_state_helpers_block_5656a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 0(s0)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_5656c:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_5656c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_564be\n");
    __builtin_unreachable();
}

/* Original0x5656E..0x56574. */
REGION void tsl9_resident_controller_state_helpers_block_5656e(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56574..0x56590. */
REGION void tsl9_candidate_unprovided_flash_56574(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000000b4)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_5658c:\n.option push\n.option norvc\nbleu a3,a4,.Lresident_controller_state_helpers_edge_5658c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56710\n");
    __builtin_unreachable();
}

/* Original0x56590..0x5659A. */
REGION void tsl9_resident_controller_state_helpers_block_56590(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000108)); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_56596:\n.option push\n.option norvc\nbeqz a4,.Lresident_controller_state_helpers_edge_56596\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56710\n");
    __builtin_unreachable();
}

/* Original0x5659A..0x565A0. */
REGION void tsl9_resident_controller_state_helpers_block_5659a(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000009c)); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x565A0..0x565A2. */
REGION void tsl9_resident_controller_state_helpers_block_565a0(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_565a0:\n.option push\n.option rvc\nc.bnez a1,.Lresident_controller_state_helpers_edge_565a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_5660e\n");
    __builtin_unreachable();
}

/* Original0x565A2..0x565B4. */
REGION void tsl9_resident_controller_state_helpers_block_565a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a2, 484(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli a6, -1\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000022); LIVE;
    PORT(".option push\n.option rvc\nsrai a2, a2, 0x1\n.option pop\n");
    a2 = a2 + UINT32_C(0x0000000b); LIVE;
    a0 = UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x565B4..0x565B6. */
REGION void tsl9_resident_controller_state_helpers_block_565b4(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_565b4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_565b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56616\n");
    __builtin_unreachable();
}

/* Original0x565B6..0x565BA. */
REGION void tsl9_resident_controller_state_helpers_block_565b6(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_565b6:\n.option push\n.option norvc\nbeqz s0,.Lresident_controller_state_helpers_edge_565b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_566ba\n");
    __builtin_unreachable();
}

/* Original0x565BA..0x565C0. */
REGION void tsl9_resident_controller_state_helpers_block_565ba(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x343c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3a\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_565be:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_565be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56668\n");
    __builtin_unreachable();
}

/* Original0x565C0..0x565F0. */
REGION void tsl9_resident_controller_state_helpers_block_565c0(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsh a4, 88(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 96(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    a5 = a5 - a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 94(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5e\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 90(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 92(s0)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_565ec:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_565ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_561b8\n");
    __builtin_unreachable();
}

/* Original0x565F0..0x56604. */
REGION void tsl9_resident_controller_state_helpers_block_565f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56604..0x5660E. */
REGION void tsl9_resident_controller_state_helpers_block_56604(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5660E..0x56612. */
REGION void tsl9_resident_controller_state_helpers_block_5660e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 29(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3dd8\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56610:\n.option push\n.option rvc\nc.bnez a4,.Lresident_controller_state_helpers_edge_56610\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56604\n");
    __builtin_unreachable();
}

/* Original0x56612..0x56616. */
REGION void tsl9_resident_controller_state_helpers_block_56612(void)
{
    REGS;
    a1 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_56614:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_56614\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_565a0\n");
    __builtin_unreachable();
}

/* Original0x56616..0x5661C. */
REGION void tsl9_resident_controller_state_helpers_block_56616(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_56618:\n.option push\n.option norvc\nbne a5,s1,.Lresident_controller_state_helpers_edge_56618\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56620\n");
    __builtin_unreachable();
}

/* Original0x5661C..0x5661E. */
REGION void tsl9_resident_controller_state_helpers_block_5661c(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_5661c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_controller_state_helpers_edge_5661c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_565b6\n");
    __builtin_unreachable();
}

/* Original0x5661E..0x56620. */
REGION void tsl9_resident_controller_state_helpers_block_5661e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56620..0x5662C. */
REGION void tsl9_resident_controller_state_helpers_block_56620(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000090)); LIVE;
    PORT(".option push\n.option norvc\nlw a4, 144(s1)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56628:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_controller_state_helpers_edge_56628\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5664c\n");
    __builtin_unreachable();
}

/* Original0x5662C..0x56638. */
REGION void tsl9_resident_controller_state_helpers_block_5662c(void)
{
    REGS;
    a4 = a3 - a4; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 140(s1)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56634:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_controller_state_helpers_edge_56634\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5663c\n");
    __builtin_unreachable();
}

/* Original0x56638..0x5663C. */
REGION void tsl9_resident_controller_state_helpers_block_56638(void)
{
    REGS;
    PORT(".option push\n.option norvc\nremu a4, a4, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5663C..0x56640. */
REGION void tsl9_resident_controller_state_helpers_block_5663c(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_5663c:\n.option push\n.option norvc\nbleu a0,a4,.Lresident_controller_state_helpers_edge_5663c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56648\n");
    __builtin_unreachable();
}

/* Original0x56640..0x56646. */
REGION void tsl9_resident_controller_state_helpers_block_56640(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56642:\n.option push\n.option norvc\nbleu a2,a4,.Lresident_controller_state_helpers_edge_56642\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56648\n");
    __builtin_unreachable();
}

/* Original0x56646..0x56648. */
REGION void tsl9_resident_controller_state_helpers_block_56646(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56648..0x5664C. */
REGION void tsl9_resident_controller_state_helpers_block_56648(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_5664a:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_5664a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_565b4\n");
    __builtin_unreachable();
}

/* Original0x5664C..0x56656. */
REGION void tsl9_resident_controller_state_helpers_block_5664c(void)
{
    REGS;
    a4 = a4 - a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000008c)); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_56652:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_controller_state_helpers_edge_56652\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5665a\n");
    __builtin_unreachable();
}

/* Original0x56656..0x5665A. */
REGION void tsl9_resident_controller_state_helpers_block_56656(void)
{
    REGS;
    PORT(".option push\n.option norvc\nremu a4, a4, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5665A..0x5665E. */
REGION void tsl9_resident_controller_state_helpers_block_5665a(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_5665a:\n.option push\n.option norvc\nbleu a6,a4,.Lresident_controller_state_helpers_edge_5665a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56648\n");
    __builtin_unreachable();
}

/* Original0x5665E..0x56664. */
REGION void tsl9_resident_controller_state_helpers_block_5665e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a6, a4\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56660:\n.option push\n.option norvc\nbleu a2,a4,.Lresident_controller_state_helpers_edge_56660\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56648\n");
    __builtin_unreachable();
}

/* Original0x56664..0x56668. */
REGION void tsl9_resident_controller_state_helpers_block_56664(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a5\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56666:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_56666\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_56648\n");
    __builtin_unreachable();
}

/* Original0x56668..0x56670. */
REGION void tsl9_resident_controller_state_helpers_block_56668(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3cbe\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a4\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_5666e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_5666e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56604\n");
    __builtin_unreachable();
}

/* Original0x56670..0x56678. */
REGION void tsl9_resident_controller_state_helpers_block_56670(void)
{
    REGS;
    a3 = UINT32_C(0x00000007); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_56674:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_controller_state_helpers_edge_56674\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_5667e\n");
    __builtin_unreachable();
}

/* Original0x56678..0x5667E. */
REGION void tsl9_resident_controller_state_helpers_block_56678(void)
{
    REGS;
    a5 = a4 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x5667E..0x5668E. */
REGION void tsl9_resident_controller_state_helpers_block_5667e(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 116(s0)\n.option pop\n");
    a4 = a4 + UINT32_C(0xfffffc80); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_5668a:\n.option push\n.option norvc\nble a5,a4,.Lresident_controller_state_helpers_edge_5668a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56690\n");
    __builtin_unreachable();
}

/* Original0x5668E..0x56690. */
REGION void tsl9_resident_controller_state_helpers_block_5668e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56690..0x566BA. */
REGION void tsl9_resident_controller_state_helpers_block_56690(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a5, 118(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x0000002c); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 90(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 92(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000012); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_566b6:\n.option push\n.option norvc\njal zero,.Lresident_controller_state_helpers_edge_566b6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x566BA..0x566BC. */
REGION void tsl9_resident_controller_state_helpers_block_566ba(void)
{
    REGS;
    PORT(".Lresident_controller_state_helpers_edge_566ba:\n.option push\n.option rvc\nc.beqz a1,.Lresident_controller_state_helpers_edge_566ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56710\n");
    __builtin_unreachable();
}

/* Original0x566BC..0x566C6. */
REGION void tsl9_resident_controller_state_helpers_block_566bc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 58(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3cba\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 58(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3dbe\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a4\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_566c4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_state_helpers_edge_566c4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_state_helpers_block_56710\n");
    __builtin_unreachable();
}

/* Original0x566C6..0x566CE. */
REGION void tsl9_resident_controller_state_helpers_block_566c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 28(s1)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_566ca:\n.option push\n.option norvc\nbgez a5,.Lresident_controller_state_helpers_edge_566ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_56710\n");
    __builtin_unreachable();
}

/* Original0x566CE..0x566D6. */
REGION void tsl9_resident_controller_state_helpers_block_566ce(void)
{
    REGS;
    a3 = UINT32_C(0x00000007); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_566d2:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_controller_state_helpers_edge_566d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_566dc\n");
    __builtin_unreachable();
}

/* Original0x566D6..0x566DC. */
REGION void tsl9_resident_controller_state_helpers_block_566d6(void)
{
    REGS;
    a5 = a4 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x566DC..0x566EC. */
REGION void tsl9_resident_controller_state_helpers_block_566dc(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 116(s1)\n.option pop\n");
    a4 = a4 + UINT32_C(0xfffffc80); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_controller_state_helpers_edge_566e8:\n.option push\n.option norvc\nble a5,a4,.Lresident_controller_state_helpers_edge_566e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_state_helpers_block_566ee\n");
    __builtin_unreachable();
}

/* Original0x566EC..0x566EE. */
REGION void tsl9_resident_controller_state_helpers_block_566ec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x566EE..0x56710. */
REGION void tsl9_resident_controller_state_helpers_block_566ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a5, 118(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 60(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3cde\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x248a\n.option pop\n");
    a2 = UINT32_C(0x0000002c); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 90(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 62(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3cfe\n.option pop\n");
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 92(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000013); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xbcdc\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_5670c:\n.option push\n.option norvc\njal ra,.Lresident_controller_state_helpers_edge_5670c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56710..0x56716. */
REGION void tsl9_resident_controller_state_helpers_block_56710(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 28(s1)\n.option pop\n");
    PORT(".Lresident_controller_state_helpers_edge_56714:\n.option push\n.option rvc\nc.j .Lresident_controller_state_helpers_edge_56714\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_state_helpers_block_56604\n");
    __builtin_unreachable();
}
