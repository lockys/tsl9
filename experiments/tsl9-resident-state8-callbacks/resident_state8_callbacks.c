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

/* Eight complete public-SDK callback/provider bodies:2118B/755i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x63B0E..0x63B18. */
REGION void tsl9_candidate_register_config_63b0e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000050c)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_63b16:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_63b16\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_63b2c\n");
    __builtin_unreachable();
}

/* Original0x63B18..0x63B2C. */
REGION void tsl9_resident_state8_callbacks_block_63b18(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x63B2C..0x63B4C. */
REGION void tsl9_resident_state8_callbacks_block_63b2c(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = a2 + UINT32_C(0x00000514); LIVE;
    PORT(".option push\n.option norvc\nlui a6, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nli a7, 1\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 10(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x2638\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 1340(a6)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_63b48:\n.option push\n.option norvc\nbne a0,a7,.Lresident_state8_callbacks_edge_63b48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_63b88\n");
    __builtin_unreachable();
}

/* Original0x63B4C..0x63B88. */
REGION void tsl9_resident_state8_callbacks_block_63b4c(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nlui a7, 0xffffd\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a7, a7, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nand a0, a0, a7\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 1340(a6)\n.option pop\n");
    a5 = UINT32_C(0x00002000); LIVE;
    a1 = a1 + UINT32_C(0x0000000b); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa25c\n.option pop\n");
    a5 = a1 << UINT32_C(0x00000002); LIVE;
    a1 = a4 + UINT32_C(0x0000009e); LIVE;
    a1 = a1 + a5; LIVE;
    a1 = a1 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000064)) = (uint32_t)a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63B88..0x63B96. */
REGION void tsl9_resident_state8_callbacks_block_63b88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlui a7, 0xffffd\n.option pop\n");
    PORT(".option push\n.option norvc\nandi t3, a0, 2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi t1, a7, -1\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_63b92:\n.option push\n.option norvc\nbeqz t3,.Lresident_state8_callbacks_edge_63b92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_63c20\n");
    __builtin_unreachable();
}

/* Original0x63B96..0x63BBA. */
REGION void tsl9_resident_state8_callbacks_block_63b96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a7, 0(a5)\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nli t3, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nand a7, a7, t1\n.option pop\n");
    PORT(".option push\n.option rvc\nlui t1, 0x2\n.option pop\n");
    PORT(".option push\n.option norvc\nor a7, a7, t1\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a7, 0(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui a7, 0xffff4\n.option pop\n");
    a4 = a4 + UINT32_C(0x000000be); LIVE;
    a1 = a1 << UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi a7, a7, -1\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_63bb6:\n.option push\n.option norvc\nbne a0,t3,.Lresident_state8_callbacks_edge_63bb6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_63bf4\n");
    __builtin_unreachable();
}

/* Original0x63BBA..0x63BEA. */
REGION void tsl9_resident_state8_callbacks_block_63bba(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nand a0, a0, a7\n.option pop\n");
    PORT(".option push\n.option rvc\nlui a7, 0x4\n.option pop\n");
    PORT(".option push\n.option norvc\nor a0, a0, a7\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(a6)\n.option pop\n");
    a3 = UINT32_C(0xffffff80); LIVE;
    a1 = a1 + UINT32_C(0x000000d7); LIVE;
    PORT(".option push\n.option norvc\nsw t1, 8(a5)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa254\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x63BEA..0x63BF4. */
REGION void tsl9_resident_state8_callbacks_block_63bea(void)
{
    REGS;
    a1 = a1 + a4; LIVE;
    a1 = a1 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63BF4..0x63C20. */
REGION void tsl9_resident_state8_callbacks_block_63bf4(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nand a0, a0, a7\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(a6)\n.option pop\n");
    a3 = UINT32_C(0xffffff80); LIVE;
    a1 = a1 + UINT32_C(0x0000004a); LIVE;
    PORT(".option push\n.option norvc\nsw t1, 8(a5)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa254\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_63c1e:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_63c1e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_63bea\n");
    __builtin_unreachable();
}

/* Original0x63C20..0x63C54. */
REGION void tsl9_resident_state8_callbacks_block_63c20(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nlui a7, 0x1\n.option pop\n");
    PORT(".option push\n.option norvc\nand a0, a0, t1\n.option pop\n");
    PORT(".option push\n.option norvc\nor a0, a0, a7\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(a6)\n.option pop\n");
    a3 = UINT32_C(0x00002000); LIVE;
    a1 = a1 + UINT32_C(0x0000000a); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa254\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000003); LIVE;
    a4 = a4 + UINT32_C(0x0000009e); LIVE;
    PORT(".Lresident_state8_callbacks_edge_63c52:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_63c52\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_63bea\n");
    __builtin_unreachable();
}

/* Original0x63E58..0x63E76. */
REGION void tsl9_candidate_reset_registers_63e58(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a3 = a3 & UINT32_C(0xfffffff8); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 | UINT32_C(0x00000008); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 >> UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_63e74:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_63e74\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_63e7e\n");
    __builtin_unreachable();
}

/* Original0x63E76..0x63E7E. */
REGION void tsl9_resident_state8_callbacks_block_63e76(void)
{
    REGS;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63E7E..0x63EB8. */
REGION void tsl9_resident_state8_callbacks_block_63e7e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a3 = UINT32_C(0xffce0000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000050c)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_63eb6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_63eb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_63ecc\n");
    __builtin_unreachable();
}

/* Original0x63EB8..0x63ECC. */
REGION void tsl9_resident_state8_callbacks_block_63eb8(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x63ECC..0x63EDA. */
REGION void tsl9_resident_state8_callbacks_block_63ecc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6440A..0x6441A. */
REGION void tsl9_candidate_reset_registers_6440a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000056e)) = (uint8_t)0; LIVE;
    PORT(".Lresident_state8_callbacks_edge_64416:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_64416\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x6441A..0x64422. */
REGION void tsl9_resident_state8_callbacks_block_6441a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65164..0x65180. */
REGION void tsl9_candidate_numeric_callback_65164(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x331c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_6517c:\n.option push\n.option norvc\nbeqz a5,.Lresident_state8_callbacks_edge_6517c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6535c\n");
    __builtin_unreachable();
}

/* Original0x65180..0x65198. */
REGION void tsl9_resident_state8_callbacks_block_65180(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlw s3, 36(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65194:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_65194\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x65198..0x651AC. */
REGION void tsl9_resident_state8_callbacks_block_65198(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s1, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_state8_callbacks_edge_651a8:\n.option push\n.option norvc\nbeqz a5,.Lresident_state8_callbacks_edge_651a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652fa\n");
    __builtin_unreachable();
}

/* Original0x651AC..0x651BC. */
REGION void tsl9_resident_state8_callbacks_block_651ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s3\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    a5 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_state8_callbacks_edge_651b8:\n.option push\n.option norvc\nbne a4,a5,.Lresident_state8_callbacks_edge_651b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_651c8\n");
    __builtin_unreachable();
}

/* Original0x651BC..0x651C8. */
REGION void tsl9_resident_state8_callbacks_block_651bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1344(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x651C8..0x651D0. */
REGION void tsl9_resident_state8_callbacks_block_651c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_651cc:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_state8_callbacks_edge_651cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652a4\n");
    __builtin_unreachable();
}

/* Original0x651D0..0x651DC. */
REGION void tsl9_resident_state8_callbacks_block_651d0(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffc); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 28(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 8(s1)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_651d8:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_state8_callbacks_edge_651d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652b0\n");
    __builtin_unreachable();
}

/* Original0x651DC..0x651F4. */
REGION void tsl9_resident_state8_callbacks_block_651dc(void)
{
    REGS;
    a4 = a5 - a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24d4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s3\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339c\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a3, a3, 0x18\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_651f0:\n.option push\n.option norvc\nbgez a3,.Lresident_state8_callbacks_edge_651f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652ce\n");
    __builtin_unreachable();
}

/* Original0x651F4..0x651F8. */
REGION void tsl9_resident_state8_callbacks_block_651f4(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_651f4:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_state8_callbacks_edge_651f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652bc\n");
    __builtin_unreachable();
}

/* Original0x651F8..0x651FA. */
REGION void tsl9_resident_state8_callbacks_block_651f8(void)
{
    REGS;
    a4 = a4 - a5; LIVE;
    __builtin_unreachable();
}

/* Original0x651FA..0x65202. */
REGION void tsl9_resident_state8_callbacks_block_651fa(void)
{
    REGS;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_state8_callbacks_edge_651fe:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_state8_callbacks_edge_651fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6520e\n");
    __builtin_unreachable();
}

/* Original0x65202..0x65208. */
REGION void tsl9_resident_state8_callbacks_block_65202(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65204:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_state8_callbacks_edge_65204\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652c2\n");
    __builtin_unreachable();
}

/* Original0x65208..0x6520E. */
REGION void tsl9_resident_state8_callbacks_block_65208(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 8(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6520E..0x65216. */
REGION void tsl9_resident_state8_callbacks_block_6520e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2888\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65212:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_65212\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x65216..0x6521E. */
REGION void tsl9_resident_state8_callbacks_block_65216(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_state8_callbacks_edge_6521c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_6521c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_652f0\n");
    __builtin_unreachable();
}

/* Original0x6521E..0x6528C. */
REGION void tsl9_resident_state8_callbacks_block_6521e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = UINT32_C(0x000000c8); LIVE;
    a4 = UINT32_C(0x000000ff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 32(s0)\n.option pop\n");
    a2 = UINT32_C(0x00330000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 4(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 1344(s2)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x4\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    a5 = a5 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000050)) = (uint32_t)a5; LIVE;
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_literal_65284:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_work_mode_200026ba\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_callbacks_literal_65284\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6528C..0x6529A. */
REGION void tsl9_resident_state8_callbacks_block_6528c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20b4\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30b0\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1344(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6529A..0x652A2. */
REGION void tsl9_resident_state8_callbacks_block_6529a(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_state8_callbacks_edge_6529e:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_6529e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_64f04\n");
    __builtin_unreachable();
}

/* Original0x652A2..0x652A4. */
REGION void tsl9_resident_state8_callbacks_block_652a2(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_652a2:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6534e\n");
    __builtin_unreachable();
}

/* Original0x652A4..0x652B0. */
REGION void tsl9_resident_state8_callbacks_block_652a4(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_652ae:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652ae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_651d0\n");
    __builtin_unreachable();
}

/* Original0x652B0..0x652BC. */
REGION void tsl9_resident_state8_callbacks_block_652b0(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_652ba:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_651dc\n");
    __builtin_unreachable();
}

/* Original0x652BC..0x652C2. */
REGION void tsl9_resident_state8_callbacks_block_652bc(void)
{
    REGS;
    a4 = a5 - a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_652c0:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_651fa\n");
    __builtin_unreachable();
}

/* Original0x652C2..0x652CE. */
REGION void tsl9_resident_state8_callbacks_block_652c2(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a4 = a4 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_652cc:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65208\n");
    __builtin_unreachable();
}

/* Original0x652CE..0x652D4. */
REGION void tsl9_resident_state8_callbacks_block_652ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_652d0:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_state8_callbacks_edge_652d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_652e4\n");
    __builtin_unreachable();
}

/* Original0x652D4..0x652E4. */
REGION void tsl9_resident_state8_callbacks_block_652d4(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 8(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4dc\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_652e2:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6520e\n");
    __builtin_unreachable();
}

/* Original0x652E4..0x652F0. */
REGION void tsl9_resident_state8_callbacks_block_652e4(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a4 = a4 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_652ee:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_652ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_652d4\n");
    __builtin_unreachable();
}

/* Original0x652F0..0x652FA. */
REGION void tsl9_resident_state8_callbacks_block_652f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x652FA..0x6530C. */
REGION void tsl9_resident_state8_callbacks_block_652fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 36(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi a2, sp, 15\n.option pop\n");
    PORT(".Lresident_state8_callbacks_literal_65304:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_callbacks_literal_65304\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6530C..0x6531E. */
REGION void tsl9_resident_state8_callbacks_block_6530c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 36(s0)\n.option pop\n");
    a1 = a0 << UINT32_C(0x00000018); LIVE;
    a3 = UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x18\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_6531a:\n.option push\n.option norvc\nbeq a4,a3,.Lresident_state8_callbacks_edge_6531a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6532c\n");
    __builtin_unreachable();
}

/* Original0x6531E..0x65324. */
REGION void tsl9_resident_state8_callbacks_block_6531e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65320:\n.option push\n.option norvc\nbeq a5,a3,.Lresident_state8_callbacks_edge_65320\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6532c\n");
    __builtin_unreachable();
}

/* Original0x65324..0x65328. */
REGION void tsl9_resident_state8_callbacks_block_65324(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65324:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_state8_callbacks_edge_65324\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6532c\n");
    __builtin_unreachable();
}

/* Original0x65328..0x6532C. */
REGION void tsl9_resident_state8_callbacks_block_65328(void)
{
    REGS;
    a1 = a1 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x6532C..0x65334. */
REGION void tsl9_resident_state8_callbacks_block_6532c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 1344(s2)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65330:\n.option push\n.option norvc\nbltz a5,.Lresident_state8_callbacks_edge_65330\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6533c\n");
    __builtin_unreachable();
}

/* Original0x65334..0x65336. */
REGION void tsl9_resident_state8_callbacks_block_65334(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65334:\n.option push\n.option rvc\nc.bnez a1,.Lresident_state8_callbacks_edge_65334\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_6533c\n");
    __builtin_unreachable();
}

/* Original0x65336..0x6533C. */
REGION void tsl9_resident_state8_callbacks_block_65336(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbusp a5, 15(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x879c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 0(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6533C..0x6534E. */
REGION void tsl9_resident_state8_callbacks_block_6533c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s2, 1344\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 16(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 36(s0)\n.option pop\n");
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6534E..0x6535C. */
REGION void tsl9_resident_state8_callbacks_block_6534e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6535C..0x65368. */
REGION void tsl9_resident_state8_callbacks_block_6535c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65366:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_callbacks_edge_65366\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_6538c\n");
    __builtin_unreachable();
}

/* Original0x65368..0x6536C. */
REGION void tsl9_resident_state8_callbacks_block_65368(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65368:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_65368\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x6536C..0x65376. */
REGION void tsl9_resident_state8_callbacks_block_6536c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65374:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_65374\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_6537e\n");
    __builtin_unreachable();
}

/* Original0x65376..0x6537E. */
REGION void tsl9_resident_state8_callbacks_block_65376(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000081); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6537E..0x6538C. */
REGION void tsl9_resident_state8_callbacks_block_6537e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b4\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b0\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_6538a:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_6538a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6529a\n");
    __builtin_unreachable();
}

/* Original0x6538C..0x65394. */
REGION void tsl9_resident_state8_callbacks_block_6538c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x337c\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65390:\n.option push\n.option norvc\nbne a4,a5,.Lresident_state8_callbacks_edge_65390\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6534e\n");
    __builtin_unreachable();
}

/* Original0x65394..0x653A0. */
REGION void tsl9_resident_state8_callbacks_block_65394(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_6539e:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_6539e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6534e\n");
    __builtin_unreachable();
}

/* Original0x653A0..0x653BC. */
REGION void tsl9_candidate_numeric_callback_653a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1300(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_653b8:\n.option push\n.option norvc\nbeqz a5,.Lresident_state8_callbacks_edge_653b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_655d6\n");
    __builtin_unreachable();
}

/* Original0x653BC..0x653DE. */
REGION void tsl9_resident_state8_callbacks_block_653bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 36(a5)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi a2, sp, 15\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)0; LIVE;
    PORT(".Lresident_state8_callbacks_literal_653d6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_callbacks_literal_653d6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x653DE..0x653F6. */
REGION void tsl9_resident_state8_callbacks_block_653de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli s4, a0, 0x18\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai s4, s4, 0x18\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_653f2:\n.option push\n.option norvc\nbnez s4,.Lresident_state8_callbacks_edge_653f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6540e\n");
    __builtin_unreachable();
}

/* Original0x653F6..0x65400. */
REGION void tsl9_resident_state8_callbacks_block_653f6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a3 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_state8_callbacks_edge_653fc:\n.option push\n.option norvc\nbeq a5,a3,.Lresident_state8_callbacks_edge_653fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6540e\n");
    __builtin_unreachable();
}

/* Original0x65400..0x65408. */
REGION void tsl9_resident_state8_callbacks_block_65400(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 36(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2318\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65404:\n.option push\n.option norvc\nbeq a4,a3,.Lresident_state8_callbacks_edge_65404\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6540e\n");
    __builtin_unreachable();
}

/* Original0x65408..0x6540C. */
REGION void tsl9_resident_state8_callbacks_block_65408(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65408:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_state8_callbacks_edge_65408\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6540e\n");
    __builtin_unreachable();
}

/* Original0x6540C..0x6540E. */
REGION void tsl9_resident_state8_callbacks_block_6540c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s4, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6540E..0x6541A. */
REGION void tsl9_resident_state8_callbacks_block_6540e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a5, 1344(s2)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65416:\n.option push\n.option norvc\nbltz a5,.Lresident_state8_callbacks_edge_65416\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65542\n");
    __builtin_unreachable();
}

/* Original0x6541A..0x6541E. */
REGION void tsl9_resident_state8_callbacks_block_6541a(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_6541a:\n.option push\n.option norvc\nbnez s4,.Lresident_state8_callbacks_edge_6541a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65546\n");
    __builtin_unreachable();
}

/* Original0x6541E..0x65424. */
REGION void tsl9_resident_state8_callbacks_block_6541e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbusp a5, 15(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x879c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 0(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65424..0x6542A. */
REGION void tsl9_resident_state8_callbacks_block_65424(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65428:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_65428\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_6549e\n");
    __builtin_unreachable();
}

/* Original0x6542A..0x65432. */
REGION void tsl9_resident_state8_callbacks_block_6542a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_6542e:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_state8_callbacks_edge_6542e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65582\n");
    __builtin_unreachable();
}

/* Original0x65432..0x6543E. */
REGION void tsl9_resident_state8_callbacks_block_65432(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffc); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 28(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 8(s1)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_6543a:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_state8_callbacks_edge_6543a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6558e\n");
    __builtin_unreachable();
}

/* Original0x6543E..0x65456. */
REGION void tsl9_resident_state8_callbacks_block_6543e(void)
{
    REGS;
    a4 = a5 - a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24d4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s3\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339c\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a3, a3, 0x18\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65452:\n.option push\n.option norvc\nbgez a3,.Lresident_state8_callbacks_edge_65452\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_655ac\n");
    __builtin_unreachable();
}

/* Original0x65456..0x6545A. */
REGION void tsl9_resident_state8_callbacks_block_65456(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65456:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_state8_callbacks_edge_65456\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_6559a\n");
    __builtin_unreachable();
}

/* Original0x6545A..0x6545C. */
REGION void tsl9_resident_state8_callbacks_block_6545a(void)
{
    REGS;
    a4 = a4 - a5; LIVE;
    __builtin_unreachable();
}

/* Original0x6545C..0x65464. */
REGION void tsl9_resident_state8_callbacks_block_6545c(void)
{
    REGS;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65460:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_state8_callbacks_edge_65460\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65470\n");
    __builtin_unreachable();
}

/* Original0x65464..0x6546A. */
REGION void tsl9_resident_state8_callbacks_block_65464(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65466:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_state8_callbacks_edge_65466\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_655a0\n");
    __builtin_unreachable();
}

/* Original0x6546A..0x65470. */
REGION void tsl9_resident_state8_callbacks_block_6546a(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 8(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65470..0x65478. */
REGION void tsl9_resident_state8_callbacks_block_65470(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2888\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65474:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_65474\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x65478..0x6548A. */
REGION void tsl9_resident_state8_callbacks_block_65478(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a4, s3, a5\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2314\n.option pop\n");
    a4 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65486:\n.option push\n.option norvc\nbne a3,a4,.Lresident_state8_callbacks_edge_65486\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_655ce\n");
    __builtin_unreachable();
}

/* Original0x6548A..0x6549E. */
REGION void tsl9_resident_state8_callbacks_block_6548a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 32(s0)\n.option pop\n");
    a4 = UINT32_C(0x000000ff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1344(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6549E..0x654AE. */
REGION void tsl9_resident_state8_callbacks_block_6549e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_654ac:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_654ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_654f0\n");
    __builtin_unreachable();
}

/* Original0x654AE..0x654F0. */
REGION void tsl9_resident_state8_callbacks_block_654ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s2, 1344\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a1 = UINT32_C(0x00010000); LIVE;
    a1 = a1 + UINT32_C(0xfffffa00); LIVE;
    PORT(".option push\n.option norvc\ndivu a3, a5, a1\n.option pop\n");
    a0 = UINT32_C(0xfe100000); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nremu a5, a5, a1\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000001f); LIVE;
    a2 = a3 << UINT32_C(0x00000014); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    a3 = a3 & a0; LIVE;
    a3 = a3 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x000000fa); LIVE;
    a2 = UINT32_C(0xfffc0000); LIVE;
    a5 = a5 << UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    a3 = a3 & a2; LIVE;
    a5 = a5 << UINT32_C(0x0000000e); LIVE;
    a5 = a5 >> UINT32_C(0x0000000e); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x654F0..0x65500. */
REGION void tsl9_resident_state8_callbacks_block_654f0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 1344(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x338c\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_654fc:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_654fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x65500..0x65510. */
REGION void tsl9_resident_state8_callbacks_block_65500(void)
{
    REGS;
    a0 = UINT32_C(0x00065000); LIVE;
    a0 = a0 + UINT32_C(0x00000620); LIVE;
    PORT(".Lresident_state8_callbacks_literal_65508:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_callbacks_literal_65508\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65510..0x65530. */
REGION void tsl9_resident_state8_callbacks_block_65510(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a3 = UINT32_C(0x00800000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_state8_callbacks_edge_6552e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_callbacks_edge_6552e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_65572\n");
    __builtin_unreachable();
}

/* Original0x65530..0x65540. */
REGION void tsl9_resident_state8_callbacks_block_65530(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s2, 1344\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 16(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 36(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65540..0x65542. */
REGION void tsl9_resident_state8_callbacks_block_65540(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65540:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_65540\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65572\n");
    __builtin_unreachable();
}

/* Original0x65542..0x65546. */
REGION void tsl9_resident_state8_callbacks_block_65542(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65542:\n.option push\n.option norvc\nbeqz s4,.Lresident_state8_callbacks_edge_65542\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65424\n");
    __builtin_unreachable();
}

/* Original0x65546..0x6554A. */
REGION void tsl9_resident_state8_callbacks_block_65546(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65546:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_65546\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x6554A..0x6555C. */
REGION void tsl9_resident_state8_callbacks_block_6554a(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s2, 1344\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 36(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 16(s2)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nandi a1, s4, 255\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6555C..0x65562. */
REGION void tsl9_resident_state8_callbacks_block_6555c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 4(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20b4\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30b0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65562..0x65564. */
REGION void tsl9_resident_state8_callbacks_block_65562(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_65562:\n.option push\n.option rvc\nc.beqz a0,.Lresident_state8_callbacks_edge_65562\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_6556a\n");
    __builtin_unreachable();
}

/* Original0x65564..0x6556A. */
REGION void tsl9_resident_state8_callbacks_block_65564(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x310c\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65568:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_65568\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6556e\n");
    __builtin_unreachable();
}

/* Original0x6556A..0x6556E. */
REGION void tsl9_resident_state8_callbacks_block_6556a(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x6556E..0x65572. */
REGION void tsl9_resident_state8_callbacks_block_6556e(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_6556e:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_6556e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_64f04\n");
    __builtin_unreachable();
}

/* Original0x65572..0x65582. */
REGION void tsl9_resident_state8_callbacks_block_65572(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65582..0x6558E. */
REGION void tsl9_resident_state8_callbacks_block_65582(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_6558c:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_6558c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65432\n");
    __builtin_unreachable();
}

/* Original0x6558E..0x6559A. */
REGION void tsl9_resident_state8_callbacks_block_6558e(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_65598:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_65598\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6543e\n");
    __builtin_unreachable();
}

/* Original0x6559A..0x655A0. */
REGION void tsl9_resident_state8_callbacks_block_6559a(void)
{
    REGS;
    a4 = a5 - a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_6559e:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_6559e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6545c\n");
    __builtin_unreachable();
}

/* Original0x655A0..0x655AC. */
REGION void tsl9_resident_state8_callbacks_block_655a0(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a4 = a4 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_655aa:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_655aa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6546a\n");
    __builtin_unreachable();
}

/* Original0x655AC..0x655B2. */
REGION void tsl9_resident_state8_callbacks_block_655ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_655ae:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_state8_callbacks_edge_655ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_655c2\n");
    __builtin_unreachable();
}

/* Original0x655B2..0x655C2. */
REGION void tsl9_resident_state8_callbacks_block_655b2(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 8(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4dc\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_655c0:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_655c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65470\n");
    __builtin_unreachable();
}

/* Original0x655C2..0x655CE. */
REGION void tsl9_resident_state8_callbacks_block_655c2(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a4 = a4 + a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_655cc:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_655cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_655b2\n");
    __builtin_unreachable();
}

/* Original0x655CE..0x655D6. */
REGION void tsl9_resident_state8_callbacks_block_655ce(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1(s3)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_655d4:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_655d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_6549e\n");
    __builtin_unreachable();
}

/* Original0x655D6..0x655E2. */
REGION void tsl9_resident_state8_callbacks_block_655d6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_655e0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_callbacks_edge_655e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_65608\n");
    __builtin_unreachable();
}

/* Original0x655E2..0x655E6. */
REGION void tsl9_resident_state8_callbacks_block_655e2(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_655e2:\n.option push\n.option norvc\njal ra,.Lresident_state8_callbacks_edge_655e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x655E6..0x655F0. */
REGION void tsl9_resident_state8_callbacks_block_655e6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_655ee:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_655ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_655f8\n");
    __builtin_unreachable();
}

/* Original0x655F0..0x655F8. */
REGION void tsl9_resident_state8_callbacks_block_655f0(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000081); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x655F8..0x65608. */
REGION void tsl9_resident_state8_callbacks_block_655f8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b4\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_65606:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_65606\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65562\n");
    __builtin_unreachable();
}

/* Original0x65608..0x65614. */
REGION void tsl9_resident_state8_callbacks_block_65608(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_state8_callbacks_edge_65610:\n.option push\n.option norvc\nbne a4,a5,.Lresident_state8_callbacks_edge_65610\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_65572\n");
    __builtin_unreachable();
}

/* Original0x65614..0x65620. */
REGION void tsl9_resident_state8_callbacks_block_65614(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_6561e:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_6561e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_65572\n");
    __builtin_unreachable();
}

/* Original0x200007A0..0x200007B4. */
REGION void tsl9_candidate_callback_runner_200007a0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffef8)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, a5, -264\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_200007b2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_state8_callbacks_edge_200007b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200007b6\n");
    __builtin_unreachable();
}

/* Original0x200007B4..0x200007B6. */
REGION void tsl9_resident_state8_callbacks_block_200007b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200007B6..0x200007C4. */
REGION void tsl9_resident_state8_callbacks_block_200007b6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_state8_callbacks_edge_200007c2:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_callbacks_edge_200007c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200007c8\n");
    __builtin_unreachable();
}

/* Original0x200007C4..0x200007C8. */
REGION void tsl9_resident_state8_callbacks_block_200007c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 0(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200007C8..0x200007D0. */
REGION void tsl9_resident_state8_callbacks_block_200007c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000263A..0x2000264A. */
REGION void tsl9_candidate_receive_status_2000263a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui a6, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1288(a6)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000038)); LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002648:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_callbacks_edge_20002648\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200026b6\n");
    __builtin_unreachable();
}

/* Original0x2000264A..0x2000264C. */
REGION void tsl9_resident_state8_callbacks_block_2000264a(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_2000264a:\n.option push\n.option rvc\nc.beqz a2,.Lresident_state8_callbacks_edge_2000264a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_20002652\n");
    __builtin_unreachable();
}

/* Original0x2000264C..0x20002652. */
REGION void tsl9_resident_state8_callbacks_block_2000264c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000030)); LIVE;
    a5 = a5 >> UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa21c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002652..0x20002654. */
REGION void tsl9_resident_state8_callbacks_block_20002652(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_20002652:\n.option push\n.option rvc\nc.beqz a3,.Lresident_state8_callbacks_edge_20002652\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_20002680\n");
    __builtin_unreachable();
}

/* Original0x20002654..0x20002664. */
REGION void tsl9_resident_state8_callbacks_block_20002654(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(a6)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000030)); LIVE;
    a4 = a4 << UINT32_C(0x00000011); LIVE;
    a5 = a4 >> UINT32_C(0x00000016); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002660:\n.option push\n.option norvc\nbgez a4,.Lresident_state8_callbacks_edge_20002660\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_2000266c\n");
    __builtin_unreachable();
}

/* Original0x20002664..0x2000266C. */
REGION void tsl9_resident_state8_callbacks_block_20002664(void)
{
    REGS;
    a5 = a5 | UINT32_C(0xfffffc00); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x2000266C..0x20002676. */
REGION void tsl9_resident_state8_callbacks_block_2000266c(void)
{
    REGS;
    a4 = *(volatile int16_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_20002674:\n.option push\n.option rvc\nc.beqz a4,.Lresident_state8_callbacks_edge_20002674\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_2000267e\n");
    __builtin_unreachable();
}

/* Original0x20002676..0x2000267E. */
REGION void tsl9_resident_state8_callbacks_block_20002676(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000267E..0x20002680. */
REGION void tsl9_resident_state8_callbacks_block_2000267e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a5, 0(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa29e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002680..0x20002682. */
REGION void tsl9_resident_state8_callbacks_block_20002680(void)
{
    REGS;
    PORT(".Lresident_state8_callbacks_edge_20002680:\n.option push\n.option rvc\nc.beqz a1,.Lresident_state8_callbacks_edge_20002680\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200026a0\n");
    __builtin_unreachable();
}

/* Original0x20002682..0x20002686. */
REGION void tsl9_resident_state8_callbacks_block_20002682(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x311c\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_20002684:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_callbacks_edge_20002684\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200026a0\n");
    __builtin_unreachable();
}

/* Original0x20002686..0x20002696. */
REGION void tsl9_resident_state8_callbacks_block_20002686(void)
{
    REGS;
    a0 = a0 + a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x351c\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000006); LIVE;
    a3 = a5 & UINT32_C(0x0000006f); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002692:\n.option push\n.option norvc\nbne a3,a4,.Lresident_state8_callbacks_edge_20002692\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_200026b8\n");
    __builtin_unreachable();
}

/* Original0x20002696..0x200026A0. */
REGION void tsl9_resident_state8_callbacks_block_20002696(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    a0 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lresident_state8_callbacks_edge_2000269c:\n.option push\n.option norvc\nbltz a5,.Lresident_state8_callbacks_edge_2000269c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_200026b8\n");
    __builtin_unreachable();
}

/* Original0x200026A0..0x200026B6. */
REGION void tsl9_resident_state8_callbacks_block_200026a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(a6)\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000038)); LIVE;
    a5 = a5 >> UINT32_C(0x0000001b); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200026B6..0x200026B8. */
REGION void tsl9_resident_state8_callbacks_block_200026b6(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x200026B8..0x200026BA. */
REGION void tsl9_resident_state8_callbacks_block_200026b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200026BA..0x200026CC. */
REGION void tsl9_candidate_register_work_mode_200026ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1340(s0)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_edge_200026ca:\n.option push\n.option rvc\nc.bnez a0,.Lresident_state8_callbacks_edge_200026ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_20002738\n");
    __builtin_unreachable();
}

/* Original0x200026CC..0x200026CE. */
REGION void tsl9_resident_state8_callbacks_block_200026cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200026CE..0x200026D2. */
REGION void tsl9_resident_state8_callbacks_block_200026ce(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_200026d0:\n.option push\n.option rvc\nc.bnez a3,.Lresident_state8_callbacks_edge_200026d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_200026ce\n");
    __builtin_unreachable();
}

/* Original0x200026D2..0x200026EA. */
REGION void tsl9_resident_state8_callbacks_block_200026d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1300\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    PORT(".Lresident_state8_callbacks_literal_200026e2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_config_63b0e\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_callbacks_literal_200026e2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200026EA..0x20002712. */
REGION void tsl9_resident_state8_callbacks_block_200026ea(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a3 = UINT32_C(0x00800000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002712..0x2000271E. */
REGION void tsl9_resident_state8_callbacks_block_20002712(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 1340(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    __builtin_unreachable();
}

/* Original0x2000271E..0x20002724. */
REGION void tsl9_resident_state8_callbacks_block_2000271e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b8\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002722:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_callbacks_edge_20002722\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_2000272e\n");
    __builtin_unreachable();
}

/* Original0x20002724..0x2000272A. */
REGION void tsl9_resident_state8_callbacks_block_20002724(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b8\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002728:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_callbacks_edge_20002728\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_2000272e\n");
    __builtin_unreachable();
}

/* Original0x2000272A..0x2000272E. */
REGION void tsl9_resident_state8_callbacks_block_2000272a(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_state8_callbacks_edge_2000272c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_callbacks_edge_2000272c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_2000271e\n");
    __builtin_unreachable();
}

/* Original0x2000272E..0x20002738. */
REGION void tsl9_resident_state8_callbacks_block_2000272e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002738..0x2000273E. */
REGION void tsl9_resident_state8_callbacks_block_20002738(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_2000273a:\n.option push\n.option norvc\nbne a0,a5,.Lresident_state8_callbacks_edge_2000273a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_20002758\n");
    __builtin_unreachable();
}

/* Original0x2000273E..0x20002758. */
REGION void tsl9_resident_state8_callbacks_block_2000273e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a3 = UINT32_C(0x00800000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002756:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_20002756\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_20002712\n");
    __builtin_unreachable();
}

/* Original0x20002758..0x2000275E. */
REGION void tsl9_resident_state8_callbacks_block_20002758(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_callbacks_edge_2000275a:\n.option push\n.option norvc\nbne a0,a5,.Lresident_state8_callbacks_edge_2000275a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_20002712\n");
    __builtin_unreachable();
}

/* Original0x2000275E..0x20002792. */
REGION void tsl9_resident_state8_callbacks_block_2000275e(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s0)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a2 = UINT32_C(0xffffff80); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_20002790:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_callbacks_edge_20002790\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_callbacks_block_2000279c\n");
    __builtin_unreachable();
}

/* Original0x20002792..0x20002796. */
REGION void tsl9_resident_state8_callbacks_block_20002792(void)
{
    REGS;
    a4 = UINT32_C(0x00000196); LIVE;
    __builtin_unreachable();
}

/* Original0x20002796..0x2000279C. */
REGION void tsl9_resident_state8_callbacks_block_20002796(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_state8_callbacks_edge_2000279a:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_2000279a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_20002712\n");
    __builtin_unreachable();
}

/* Original0x2000279C..0x200027A8. */
REGION void tsl9_resident_state8_callbacks_block_2000279c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_callbacks_edge_200027a4:\n.option push\n.option norvc\nbne a4,a2,.Lresident_state8_callbacks_edge_200027a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_callbacks_block_200027ae\n");
    __builtin_unreachable();
}

/* Original0x200027A8..0x200027AE. */
REGION void tsl9_resident_state8_callbacks_block_200027a8(void)
{
    REGS;
    a4 = UINT32_C(0x0000043e); LIVE;
    PORT(".Lresident_state8_callbacks_edge_200027ac:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_200027ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_20002796\n");
    __builtin_unreachable();
}

/* Original0x200027AE..0x200027B4. */
REGION void tsl9_resident_state8_callbacks_block_200027ae(void)
{
    REGS;
    a4 = UINT32_C(0x000001be); LIVE;
    PORT(".Lresident_state8_callbacks_edge_200027b2:\n.option push\n.option rvc\nc.j .Lresident_state8_callbacks_edge_200027b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_callbacks_block_20002796\n");
    __builtin_unreachable();
}
