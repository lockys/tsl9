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

/* Five complete public-SDK callback/LLE/gateway bodies:936B/338i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x65620..0x65634. */
REGION void tsl9_candidate_numeric_callback_65620(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3398\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_65632:\n.option push\n.option rvc\nc.beqz a4,.Lresident_lle_callback_gateway_edge_65632\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_65660\n");
    __builtin_unreachable();
}

/* Original0x65634..0x6563C. */
REGION void tsl9_resident_lle_callback_gateway_block_65634(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)0; LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_65638:\n.option push\n.option norvc\njal ra,.Lresident_lle_callback_gateway_edge_65638\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x6563C..0x6564A. */
REGION void tsl9_resident_lle_callback_gateway_block_6563c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000540)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a5\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_65648:\n.option push\n.option rvc\nc.bnez a4,.Lresident_lle_callback_gateway_edge_65648\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_6568a\n");
    __builtin_unreachable();
}

/* Original0x6564A..0x65658. */
REGION void tsl9_resident_lle_callback_gateway_block_6564a(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000540); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 16(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x65658..0x65660. */
REGION void tsl9_resident_lle_callback_gateway_block_65658(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65660..0x6566C. */
REGION void tsl9_resident_lle_callback_gateway_block_65660(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_6566a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_lle_callback_gateway_edge_6566a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_656ba\n");
    __builtin_unreachable();
}

/* Original0x6566C..0x6567A. */
REGION void tsl9_resident_lle_callback_gateway_block_6566c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000540)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a5\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_65678:\n.option push\n.option rvc\nc.bnez a4,.Lresident_lle_callback_gateway_edge_65678\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_6568a\n");
    __builtin_unreachable();
}

/* Original0x6567A..0x6568A. */
REGION void tsl9_resident_lle_callback_gateway_block_6567a(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000540); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 16(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_65688:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_65688\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_65658\n");
    __builtin_unreachable();
}

/* Original0x6568A..0x6569A. */
REGION void tsl9_resident_lle_callback_gateway_block_6568a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b4\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_65698:\n.option push\n.option rvc\nc.beqz a0,.Lresident_lle_callback_gateway_edge_65698\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_656b4\n");
    __builtin_unreachable();
}

/* Original0x6569A..0x6569E. */
REGION void tsl9_resident_lle_callback_gateway_block_6569a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x310c\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x6569E..0x656A2. */
REGION void tsl9_resident_lle_callback_gateway_block_6569e(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_6569e:\n.option push\n.option norvc\njal ra,.Lresident_lle_callback_gateway_edge_6569e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_64f04\n");
    __builtin_unreachable();
}

/* Original0x656A2..0x656AC. */
REGION void tsl9_resident_lle_callback_gateway_block_656a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1344(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x656AC..0x656B4. */
REGION void tsl9_resident_lle_callback_gateway_block_656ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x656B4..0x656BA. */
REGION void tsl9_resident_lle_callback_gateway_block_656b4(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_656b8:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_656b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_6569e\n");
    __builtin_unreachable();
}

/* Original0x656BA..0x656C6. */
REGION void tsl9_resident_lle_callback_gateway_block_656ba(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_656c4:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_656c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_656ac\n");
    __builtin_unreachable();
}

/* Original0x2000298E..0x200029A0. */
REGION void tsl9_candidate_irq_registers_2000298e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a3 = a4 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_2000299c:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_2000299c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_200029c0\n");
    __builtin_unreachable();
}

/* Original0x200029A0..0x200029AA. */
REGION void tsl9_resident_lle_callback_gateway_block_200029a0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a4 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_200029a6:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_200029a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_200029c0\n");
    __builtin_unreachable();
}

/* Original0x200029AA..0x200029C0. */
REGION void tsl9_resident_lle_callback_gateway_block_200029aa(void)
{
    REGS;
    a4 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000068)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x0000019c); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000001c)); LIVE;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000001c)) = (uint32_t)a3; LIVE;
    a4 = UINT32_C(0x00004000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x200029C0..0x200029C8. */
REGION void tsl9_resident_lle_callback_gateway_block_200029c0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 >> UINT32_C(0x00000003); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_200029c6:\n.option push\n.option rvc\nc.beqz a4,.Lresident_lle_callback_gateway_edge_200029c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_200029e2\n");
    __builtin_unreachable();
}

/* Original0x200029C8..0x200029E2. */
REGION void tsl9_resident_lle_callback_gateway_block_200029c8(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2334\n.option pop\n");
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa334\n.option pop\n");
    a3 = UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa354\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x200029E2..0x200029E8. */
REGION void tsl9_resident_lle_callback_gateway_block_200029e2(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_200029e6:\n.option push\n.option rvc\nc.beqz a4,.Lresident_lle_callback_gateway_edge_200029e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_200029fc\n");
    __builtin_unreachable();
}

/* Original0x200029E8..0x200029FC. */
REGION void tsl9_resident_lle_callback_gateway_block_200029e8(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3314\n.option pop\n");
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb314\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x200029FC..0x20002A04. */
REGION void tsl9_resident_lle_callback_gateway_block_200029fc(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 >> UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a02:\n.option push\n.option rvc\nc.bnez a4,.Lresident_lle_callback_gateway_edge_20002a02\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002a0c\n");
    __builtin_unreachable();
}

/* Original0x20002A04..0x20002A0C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a04(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 >> UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a0a:\n.option push\n.option rvc\nc.beqz a4,.Lresident_lle_callback_gateway_edge_20002a0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002a5e\n");
    __builtin_unreachable();
}

/* Original0x20002A0C..0x20002A28. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a0c(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = a4 + UINT32_C(0x00000514); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a1 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000508)); LIVE;
    a3 = a3 >> UINT32_C(0x00000002); LIVE;
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a26:\n.option push\n.option rvc\nc.beqz a3,.Lresident_lle_callback_gateway_edge_20002a26\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b0e\n");
    __builtin_unreachable();
}

/* Original0x20002A28..0x20002A30. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a28(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 >> UINT32_C(0x0000000c); LIVE;
    a3 = a3 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a2e:\n.option push\n.option rvc\nc.bnez a3,.Lresident_lle_callback_gateway_edge_20002a2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b08\n");
    __builtin_unreachable();
}

/* Original0x20002A30..0x20002A3C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a30(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000024)); LIVE;
    a2 = a0 & UINT32_C(0x00000020); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 1(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x3294\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002a3a:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002a3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002adc\n");
    __builtin_unreachable();
}

/* Original0x20002A3C..0x20002A3E. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a3c(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_20002a3c:\n.option push\n.option rvc\nc.bnez a3,.Lresident_lle_callback_gateway_edge_20002a3c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b02\n");
    __builtin_unreachable();
}

/* Original0x20002A3E..0x20002A42. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a3e(void)
{
    REGS;
    a3 = UINT32_C(0x0000005d); LIVE;
    __builtin_unreachable();
}

/* Original0x20002A42..0x20002A52. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a42(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000514)); LIVE;
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000514)) = (uint8_t)a3; LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x20002A52..0x20002A5E. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a52(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002A5E..0x20002A68. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a5e(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a4 << UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a64:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002a64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002a8c\n");
    __builtin_unreachable();
}

/* Original0x20002A68..0x20002A7C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a68(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = a4 + UINT32_C(0x000003b8); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000007c)); LIVE;
    a4 = a4 + UINT32_C(0x000003b8); LIVE;
    a2 = a2 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a7a:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002a7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b1a\n");
    __builtin_unreachable();
}

/* Original0x20002A7C..0x20002A88. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a7c(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000007c)); LIVE;
    a4 = a4 | UINT32_C(0x00000020); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000007c)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002A88..0x20002A8C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a88(void)
{
    REGS;
    a4 = UINT32_C(0x00001000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002A8C..0x20002A96. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a8c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a4 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002a92:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002a92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002ab0\n");
    __builtin_unreachable();
}

/* Original0x20002A96..0x20002AA8. */
REGION void tsl9_resident_lle_callback_gateway_block_20002a96(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2354\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a3, a3, 0x18\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002aa4:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002aa4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002aac\n");
    __builtin_unreachable();
}

/* Original0x20002AA8..0x20002AAC. */
REGION void tsl9_resident_lle_callback_gateway_block_20002aa8(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa354\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002AAC..0x20002AB0. */
REGION void tsl9_resident_lle_callback_gateway_block_20002aac(void)
{
    REGS;
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002AB0..0x20002ABA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ab0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002ab6:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002ab6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002ada\n");
    __builtin_unreachable();
}

/* Original0x20002ABA..0x20002ACA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002aba(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x000003b8); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007d)); LIVE;
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002ac8:\n.option push\n.option rvc\nc.beqz a3,.Lresident_lle_callback_gateway_edge_20002ac8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b3a\n");
    __builtin_unreachable();
}

/* Original0x20002ACA..0x20002AD2. */
REGION void tsl9_resident_lle_callback_gateway_block_20002aca(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007d)); LIVE;
    a3 = a3 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x20002AD2..0x20002AD6. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ad2(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007d)) = (uint8_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0x20002AD6..0x20002ADA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ad6(void)
{
    REGS;
    a4 = UINT32_C(0x00008000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002ADA..0x20002ADC. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ada(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002ADC..0x20002ADE. */
REGION void tsl9_resident_lle_callback_gateway_block_20002adc(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_20002adc:\n.option push\n.option rvc\nc.beqz a3,.Lresident_lle_callback_gateway_edge_20002adc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002a3e\n");
    __builtin_unreachable();
}

/* Original0x20002ADE..0x20002AE4. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ade(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002ae0:\n.option push\n.option norvc\nbne a3,a2,.Lresident_lle_callback_gateway_edge_20002ae0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002aea\n");
    __builtin_unreachable();
}

/* Original0x20002AE4..0x20002AEA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002ae4(void)
{
    REGS;
    a3 = UINT32_C(0x00000061); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002ae8:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002ae8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a42\n");
    __builtin_unreachable();
}

/* Original0x20002AEA..0x20002AF0. */
REGION void tsl9_resident_lle_callback_gateway_block_20002aea(void)
{
    REGS;
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002aec:\n.option push\n.option norvc\nbne a3,a2,.Lresident_lle_callback_gateway_edge_20002aec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002af6\n");
    __builtin_unreachable();
}

/* Original0x20002AF0..0x20002AF6. */
REGION void tsl9_resident_lle_callback_gateway_block_20002af0(void)
{
    REGS;
    a3 = UINT32_C(0x00000065); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002af4:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002af4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a42\n");
    __builtin_unreachable();
}

/* Original0x20002AF6..0x20002AFC. */
REGION void tsl9_resident_lle_callback_gateway_block_20002af6(void)
{
    REGS;
    a2 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002af8:\n.option push\n.option norvc\nbne a3,a2,.Lresident_lle_callback_gateway_edge_20002af8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b02\n");
    __builtin_unreachable();
}

/* Original0x20002AFC..0x20002B02. */
REGION void tsl9_resident_lle_callback_gateway_block_20002afc(void)
{
    REGS;
    a3 = UINT32_C(0x00000069); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b00:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b00\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a42\n");
    __builtin_unreachable();
}

/* Original0x20002B02..0x20002B08. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b02(void)
{
    REGS;
    a3 = UINT32_C(0x0000006b); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b06:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b06\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a42\n");
    __builtin_unreachable();
}

/* Original0x20002B08..0x20002B0E. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b08(void)
{
    REGS;
    a3 = UINT32_C(0x0000006c); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b0c:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b0c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a42\n");
    __builtin_unreachable();
}

/* Original0x20002B0E..0x20002B1A. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b0e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 3(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3238\n.option pop\n");
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb238\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b18:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a52\n");
    __builtin_unreachable();
}

/* Original0x20002B1A..0x20002B26. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b1a(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007c)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b22:\n.option push\n.option norvc\nbeq a3,a2,.Lresident_lle_callback_gateway_edge_20002b22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b32\n");
    __builtin_unreachable();
}

/* Original0x20002B26..0x20002B32. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b26(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007c)); LIVE;
    a2 = UINT32_C(0x00000003); LIVE;
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b2e:\n.option push\n.option norvc\nbne a3,a2,.Lresident_lle_callback_gateway_edge_20002b2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002a88\n");
    __builtin_unreachable();
}

/* Original0x20002B32..0x20002B3A. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b32(void)
{
    REGS;
    a3 = UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007c)) = (uint8_t)a3; LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b38:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002a88\n");
    __builtin_unreachable();
}

/* Original0x20002B3A..0x20002B42. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b3a(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007d)); LIVE;
    a3 = a3 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b40:\n.option push\n.option rvc\nc.beqz a3,.Lresident_lle_callback_gateway_edge_20002b40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002ad6\n");
    __builtin_unreachable();
}

/* Original0x20002B42..0x20002B4C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b42(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000007d)); LIVE;
    a3 = a3 | UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b4a:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002b4a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002ad2\n");
    __builtin_unreachable();
}

/* Original0x20002B4C..0x20002B68. */
REGION void tsl9_candidate_irq_registers_20002b4c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a4 = a3 + UINT32_C(0x00000514); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000018)) = (uint32_t)a2; LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a2 = a2 >> UINT32_C(0x00000003); LIVE;
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b66:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002b66\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b7a\n");
    __builtin_unreachable();
}

/* Original0x20002B68..0x20002B7A. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b68(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2330\n.option pop\n");
    a2 = a2 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa330\n.option pop\n");
    a2 = UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x20002B7A..0x20002B80. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b7a(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b7e:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002b7e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b8c\n");
    __builtin_unreachable();
}

/* Original0x20002B80..0x20002B8C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b80(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3310\n.option pop\n");
    a2 = a2 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb310\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x20002B8C..0x20002B94. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b8c(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a2 = a2 >> UINT32_C(0x00000002); LIVE;
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b92:\n.option push\n.option rvc\nc.bnez a2,.Lresident_lle_callback_gateway_edge_20002b92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002b9c\n");
    __builtin_unreachable();
}

/* Original0x20002B94..0x20002B9C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b94(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a2 = a2 >> UINT32_C(0x00000001); LIVE;
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002b9a:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002b9a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002be6\n");
    __builtin_unreachable();
}

/* Original0x20002B9C..0x20002BB0. */
REGION void tsl9_resident_lle_callback_gateway_block_20002b9c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a1 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000508)); LIVE;
    a2 = a2 >> UINT32_C(0x00000002); LIVE;
    a2 = a2 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002bae:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002bae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c44\n");
    __builtin_unreachable();
}

/* Original0x20002BB0..0x20002BB8. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bb0(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a2 = a2 >> UINT32_C(0x0000000c); LIVE;
    a2 = a2 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002bb6:\n.option push\n.option rvc\nc.bnez a2,.Lresident_lle_callback_gateway_edge_20002bb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c3e\n");
    __builtin_unreachable();
}

/* Original0x20002BB8..0x20002BC4. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bb8(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000024)); LIVE;
    a0 = a0 & UINT32_C(0x00000020); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3210\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002bc2:\n.option push\n.option rvc\nc.beqz a0,.Lresident_lle_callback_gateway_edge_20002bc2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c12\n");
    __builtin_unreachable();
}

/* Original0x20002BC4..0x20002BC6. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bc4(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_20002bc4:\n.option push\n.option rvc\nc.bnez a2,.Lresident_lle_callback_gateway_edge_20002bc4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c38\n");
    __builtin_unreachable();
}

/* Original0x20002BC6..0x20002BCA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bc6(void)
{
    REGS;
    a2 = UINT32_C(0x0000005d); LIVE;
    __builtin_unreachable();
}

/* Original0x20002BCA..0x20002BDA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bca(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)a2; LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000514)); LIVE;
    a2 = a2 | UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000514)) = (uint8_t)a2; LIVE;
    a3 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x20002BDA..0x20002BE6. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bda(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000002c)); LIVE;
    a3 = a3 & UINT32_C(0xfffffffc); LIVE;
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000002c)) = (uint32_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0x20002BE6..0x20002BF0. */
REGION void tsl9_resident_lle_callback_gateway_block_20002be6(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a2 = a3 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002bec:\n.option push\n.option norvc\nbgez a2,.Lresident_lle_callback_gateway_edge_20002bec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c02\n");
    __builtin_unreachable();
}

/* Original0x20002BF0..0x20002BFA. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bf0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2354\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a3, a3, 0x18\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002bf6:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002bf6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002bfe\n");
    __builtin_unreachable();
}

/* Original0x20002BFA..0x20002BFE. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bfa(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa354\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002BFE..0x20002C02. */
REGION void tsl9_resident_lle_callback_gateway_block_20002bfe(void)
{
    REGS;
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002C02..0x20002C0C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c02(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c08:\n.option push\n.option norvc\nbgez a3,.Lresident_lle_callback_gateway_edge_20002c08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c10\n");
    __builtin_unreachable();
}

/* Original0x20002C0C..0x20002C10. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c0c(void)
{
    REGS;
    a4 = UINT32_C(0x00008000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20002C10..0x20002C12. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c10(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002C12..0x20002C14. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c12(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_20002c12:\n.option push\n.option rvc\nc.beqz a2,.Lresident_lle_callback_gateway_edge_20002c12\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_lle_callback_gateway_block_20002bc6\n");
    __builtin_unreachable();
}

/* Original0x20002C14..0x20002C1A. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c14(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c16:\n.option push\n.option norvc\nbne a2,a0,.Lresident_lle_callback_gateway_edge_20002c16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c20\n");
    __builtin_unreachable();
}

/* Original0x20002C1A..0x20002C20. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c1a(void)
{
    REGS;
    a2 = UINT32_C(0x00000061); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c1e:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c1e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bca\n");
    __builtin_unreachable();
}

/* Original0x20002C20..0x20002C26. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c20(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c22:\n.option push\n.option norvc\nbne a2,a0,.Lresident_lle_callback_gateway_edge_20002c22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c2c\n");
    __builtin_unreachable();
}

/* Original0x20002C26..0x20002C2C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c26(void)
{
    REGS;
    a2 = UINT32_C(0x00000065); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c2a:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c2a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bca\n");
    __builtin_unreachable();
}

/* Original0x20002C2C..0x20002C32. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c2c(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c2e:\n.option push\n.option norvc\nbne a2,a0,.Lresident_lle_callback_gateway_edge_20002c2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002c38\n");
    __builtin_unreachable();
}

/* Original0x20002C32..0x20002C38. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c32(void)
{
    REGS;
    a2 = UINT32_C(0x00000069); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c36:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c36\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bca\n");
    __builtin_unreachable();
}

/* Original0x20002C38..0x20002C3E. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c38(void)
{
    REGS;
    a2 = UINT32_C(0x0000006b); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c3c:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bca\n");
    __builtin_unreachable();
}

/* Original0x20002C3E..0x20002C44. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c3e(void)
{
    REGS;
    a2 = UINT32_C(0x0000006c); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c42:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bca\n");
    __builtin_unreachable();
}

/* Original0x20002C44..0x20002C50. */
REGION void tsl9_resident_lle_callback_gateway_block_20002c44(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3334\n.option pop\n");
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb334\n.option pop\n");
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_lle_callback_gateway_edge_20002c4e:\n.option push\n.option rvc\nc.j .Lresident_lle_callback_gateway_edge_20002c4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_lle_callback_gateway_block_20002bda\n");
    __builtin_unreachable();
}

/* Original0x20002E28..0x20002E2C. */
REGION void tsl9_candidate_callback_gateway_20002e28(void)
{
    REGS;
    PORT(".Lresident_lle_callback_gateway_edge_20002e28:\n.option push\n.option norvc\njal ra,.Lresident_lle_callback_gateway_edge_20002e28\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_callback_runner_200007a0\n");
    __builtin_unreachable();
}

/* Original0x20002E2C..0x20002E30. */
REGION void tsl9_resident_lle_callback_gateway_block_20002e2c(void)
{
    REGS;
    PORT(".option push\n.option norvc\necall\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002E34..0x20002E48. */
REGION void tsl9_candidate_LLE_IRQLibHandler_20002e34(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc t0, 0x0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi t0, t0, 200\n.option pop\n");
    PORT(".option push\n.option norvc\nlb t1, 0(t0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 0(t0)\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002e44:\n.option push\n.option norvc\nbeqz t1,.Lresident_lle_callback_gateway_edge_20002e44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_lle_callback_gateway_block_20002e62\n");
    __builtin_unreachable();
}

/* Original0x20002E48..0x20002E5E. */
REGION void tsl9_resident_lle_callback_gateway_block_20002e48(void)
{
    REGS;
    PORT(".option push\n.option norvc\ncsrr a1, mepc\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x0\n.option pop\n");
    a1 = a1 + UINT32_C(0xffffffda); LIVE;
    PORT(".option push\n.option norvc\ncsrw mepc, a1\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002e5a:\n.option push\n.option norvc\njal ra,.Lresident_lle_callback_gateway_edge_20002e5a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_irq_registers_20002b4c\n");
    __builtin_unreachable();
}

/* Original0x20002E5E..0x20002E62. */
REGION void tsl9_resident_lle_callback_gateway_block_20002e5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002E62..0x20002E68. */
REGION void tsl9_resident_lle_callback_gateway_block_20002e62(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw ra, 120(sp)\n.option pop\n");
    PORT(".Lresident_lle_callback_gateway_edge_20002e64:\n.option push\n.option norvc\njal ra,.Lresident_lle_callback_gateway_edge_20002e64\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_irq_registers_2000298e\n");
    __builtin_unreachable();
}

/* Original0x20002E68..0x20002E6C. */
REGION void tsl9_resident_lle_callback_gateway_block_20002e68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 120(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
