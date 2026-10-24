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

/* Twenty-four complete peripheral functions:2020B/677i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x188E2..0x188F2. */
REGION void tsl9_resident_startup_provider_188e2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x40012000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000400); LIVE;
    PORT(".Lperipheral_primitives_edge_188ee:\n.option push\n.option norvc\nbne a0,a5,.Lperipheral_primitives_edge_188ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_1890a\n");
    __builtin_unreachable();
}

/* Original0x188F2..0x188FC. */
REGION void tsl9_peripheral_primitives_block_188f2(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000200); LIVE;
    PORT(".Lperipheral_primitives_edge_188f8:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_188f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19160\n");
    __builtin_unreachable();
}

/* Original0x188FC..0x18902. */
REGION void tsl9_peripheral_primitives_block_188fc(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000200); LIVE;
    __builtin_unreachable();
}

/* Original0x18902..0x1890A. */
REGION void tsl9_peripheral_primitives_block_18902(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_18906:\n.option push\n.option norvc\njal zero,.Lperipheral_primitives_edge_18906\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19160\n");
    __builtin_unreachable();
}

/* Original0x1890A..0x18916. */
REGION void tsl9_peripheral_primitives_block_1890a(void)
{
    REGS;
    a5 = UINT32_C(0x40013000); LIVE;
    a5 = a5 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lperipheral_primitives_edge_18912:\n.option push\n.option norvc\nbne a0,a5,.Lperipheral_primitives_edge_18912\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_18928\n");
    __builtin_unreachable();
}

/* Original0x18916..0x18920. */
REGION void tsl9_peripheral_primitives_block_18916(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000400); LIVE;
    PORT(".Lperipheral_primitives_edge_1891c:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_1891c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19160\n");
    __builtin_unreachable();
}

/* Original0x18920..0x18928. */
REGION void tsl9_peripheral_primitives_block_18920(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000400); LIVE;
    PORT(".Lperipheral_primitives_edge_18926:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_18926\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_18902\n");
    __builtin_unreachable();
}

/* Original0x18928..0x1892E. */
REGION void tsl9_peripheral_primitives_block_18928(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1892E..0x18986. */
REGION void tsl9_resident_startup_provider_1892e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0xe0f10000); LIVE;
    a4 = a4 + UINT32_C(0xfffffeff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000018)); LIVE;
    a4 = a4 & a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000001c)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a4 = UINT32_C(0xfff1f000); LIVE;
    a4 = a4 + UINT32_C(0x000007fd); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000010)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    a3 = a3 << UINT32_C(0x00000001); LIVE;
    a5 = a5 | a3; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)); LIVE;
    a4 = UINT32_C(0xff100000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000014)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 << UINT32_C(0x00000014); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18986..0x1898A. */
REGION void tsl9_resident_startup_provider_18986(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lperipheral_primitives_edge_18988:\n.option push\n.option rvc\nc.beqz a1,.Lperipheral_primitives_edge_18988\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_18992\n");
    __builtin_unreachable();
}

/* Original0x1898A..0x1898E. */
REGION void tsl9_peripheral_primitives_block_1898a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1898E..0x18992. */
REGION void tsl9_peripheral_primitives_block_1898e(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18992..0x18996. */
REGION void tsl9_peripheral_primitives_block_18992(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".Lperipheral_primitives_edge_18994:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_18994\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_1898e\n");
    __builtin_unreachable();
}

/* Original0x18996..0x1899A. */
REGION void tsl9_resident_startup_provider_18996(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lperipheral_primitives_edge_18998:\n.option push\n.option rvc\nc.beqz a1,.Lperipheral_primitives_edge_18998\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_189a4\n");
    __builtin_unreachable();
}

/* Original0x1899A..0x189A0. */
REGION void tsl9_peripheral_primitives_block_1899a(void)
{
    REGS;
    a4 = UINT32_C(0x00500000); LIVE;
    a5 = a5 | a4; LIVE;
    __builtin_unreachable();
}

/* Original0x189A0..0x189A4. */
REGION void tsl9_peripheral_primitives_block_189a0(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x189A4..0x189AE. */
REGION void tsl9_peripheral_primitives_block_189a4(void)
{
    REGS;
    a4 = UINT32_C(0xffb00000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".Lperipheral_primitives_edge_189ac:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_189ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_189a0\n");
    __builtin_unreachable();
}

/* Original0x189AE..0x189B4. */
REGION void tsl9_resident_startup_provider_189ae(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lperipheral_primitives_edge_189b0:\n.option push\n.option norvc\nbleu a1,a5,.Lperipheral_primitives_edge_189b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_189fe\n");
    __builtin_unreachable();
}

/* Original0x189B4..0x189D8. */
REGION void tsl9_peripheral_primitives_block_189b4(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    a4 = a1 + UINT32_C(0xfffffff6); LIVE;
    a4 = a4 * a5; LIVE;
    PORT(".option push\n.option norvc\nlw a6, 12(a0)\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nand a5, a5, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a3, a3, a4\n.option pop\n");
    a3 = a3 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0x189D8..0x189DE. */
REGION void tsl9_peripheral_primitives_block_189d8(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lperipheral_primitives_edge_189da:\n.option push\n.option norvc\nbltu a5,a2,.Lperipheral_primitives_edge_189da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_18a20\n");
    __builtin_unreachable();
}

/* Original0x189DE..0x189FE. */
REGION void tsl9_peripheral_primitives_block_189de(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    a2 = a2 + UINT32_C(0xffffffff); LIVE;
    a2 = a2 * a5; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000034)); LIVE;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsll a2, a1, a2\n.option pop\n");
    a2 = a2 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000034)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x189FE..0x18A20. */
REGION void tsl9_peripheral_primitives_block_189fe(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    a4 = a1 * a4; LIVE;
    PORT(".option push\n.option norvc\nlw a6, 16(a0)\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nand a5, a5, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a3, a3, a4\n.option pop\n");
    a3 = a3 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint32_t)a3; LIVE;
    PORT(".Lperipheral_primitives_edge_18a1e:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_18a1e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_189d8\n");
    __builtin_unreachable();
}

/* Original0x18A20..0x18A26. */
REGION void tsl9_peripheral_primitives_block_18a20(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lperipheral_primitives_edge_18a22:\n.option push\n.option norvc\nbltu a5,a2,.Lperipheral_primitives_edge_18a22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_18a46\n");
    __builtin_unreachable();
}

/* Original0x18A26..0x18A46. */
REGION void tsl9_peripheral_primitives_block_18a26(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    a2 = a2 + UINT32_C(0xfffffff9); LIVE;
    a2 = a2 * a5; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000030)); LIVE;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsll a2, a1, a2\n.option pop\n");
    a2 = a2 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000030)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18A46..0x18A66. */
REGION void tsl9_peripheral_primitives_block_18a46(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    a2 = a2 + UINT32_C(0xfffffff3); LIVE;
    a2 = a2 * a5; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)); LIVE;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsll a1, a1, a2\n.option pop\n");
    a1 = a1 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18A66..0x18A6E. */
REGION void tsl9_resident_startup_provider_18a66(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000004c)); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18A6E..0x18A7A. */
REGION void tsl9_resident_startup_provider_18a6e(void)
{
    REGS;
    a5 = UINT32_C(0x40012000); LIVE;
    a5 = a5 + UINT32_C(0x00000400); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lperipheral_primitives_edge_18a78:\n.option push\n.option rvc\nc.beqz a0,.Lperipheral_primitives_edge_18a78\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_18a84\n");
    __builtin_unreachable();
}

/* Original0x18A7A..0x18A80. */
REGION void tsl9_peripheral_primitives_block_18a7a(void)
{
    REGS;
    a3 = UINT32_C(0x00800000); LIVE;
    a4 = a4 | a3; LIVE;
    __builtin_unreachable();
}

/* Original0x18A80..0x18A84. */
REGION void tsl9_peripheral_primitives_block_18a80(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18A84..0x18A8E. */
REGION void tsl9_peripheral_primitives_block_18a84(void)
{
    REGS;
    a3 = UINT32_C(0xff800000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a3; LIVE;
    PORT(".Lperipheral_primitives_edge_18a8c:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_18a8c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_18a80\n");
    __builtin_unreachable();
}

/* Original0x18A8E..0x18A98. */
REGION void tsl9_resident_startup_provider_18a8e(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a0 = a0 & a1; LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18A98..0x18A9C. */
REGION void tsl9_resident_startup_provider_18a98(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lperipheral_primitives_edge_18a9a:\n.option push\n.option rvc\nc.beqz a1,.Lperipheral_primitives_edge_18a9a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_18aa6\n");
    __builtin_unreachable();
}

/* Original0x18A9C..0x18AA2. */
REGION void tsl9_peripheral_primitives_block_18a9c(void)
{
    REGS;
    a4 = UINT32_C(0x04000000); LIVE;
    a5 = a5 | a4; LIVE;
    __builtin_unreachable();
}

/* Original0x18AA2..0x18AA6. */
REGION void tsl9_peripheral_primitives_block_18aa2(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18AA6..0x18AB0. */
REGION void tsl9_peripheral_primitives_block_18aa6(void)
{
    REGS;
    a4 = UINT32_C(0xfc000000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".Lperipheral_primitives_edge_18aae:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_18aae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_18aa2\n");
    __builtin_unreachable();
}

/* Original0x18F56..0x18F88. */
REGION void tsl9_resident_startup_provider_18f56(void)
{
    REGS;
    a4 = UINT32_C(0x1ffff000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000007e8)); LIVE;
    a3 = a5 >> UINT32_C(0x00000008); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000001)) = (uint8_t)a3; LIVE;
    a3 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000018); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)a3; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000007ec)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19076..0x1907E. */
REGION void tsl9_resident_startup_provider_19076(void)
{
    REGS;
    a4 = UINT32_C(0x40007000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lperipheral_primitives_edge_1907c:\n.option push\n.option rvc\nc.beqz a0,.Lperipheral_primitives_edge_1907c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_19086\n");
    __builtin_unreachable();
}

/* Original0x1907E..0x19082. */
REGION void tsl9_peripheral_primitives_block_1907e(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    __builtin_unreachable();
}

/* Original0x19082..0x19086. */
REGION void tsl9_peripheral_primitives_block_19082(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19086..0x1908C. */
REGION void tsl9_peripheral_primitives_block_19086(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffeff); LIVE;
    PORT(".Lperipheral_primitives_edge_1908a:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_1908a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_19082\n");
    __builtin_unreachable();
}

/* Original0x1908C..0x1909E. */
REGION void tsl9_resident_startup_provider_1908c(void)
{
    REGS;
    a3 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0xffff4000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1909E..0x190B0. */
REGION void tsl9_resident_startup_provider_1909e(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint8_t)0; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_primitives_edge_190ac:\n.option push\n.option norvc\nbeq a0,a4,.Lperipheral_primitives_edge_190ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_190b8\n");
    __builtin_unreachable();
}

/* Original0x190B0..0x190B6. */
REGION void tsl9_peripheral_primitives_block_190b0(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lperipheral_primitives_edge_190b2:\n.option push\n.option norvc\nbeq a0,a4,.Lperipheral_primitives_edge_190b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_190be\n");
    __builtin_unreachable();
}

/* Original0x190B6..0x190B8. */
REGION void tsl9_peripheral_primitives_block_190b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190B8..0x190BE. */
REGION void tsl9_peripheral_primitives_block_190b8(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190BE..0x190C6. */
REGION void tsl9_peripheral_primitives_block_190be(void)
{
    REGS;
    a4 = UINT32_C(0x00000005); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190C6..0x190CE. */
REGION void tsl9_resident_startup_provider_190c6(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000024)); LIVE;
    PORT(".Lperipheral_primitives_edge_190cc:\n.option push\n.option rvc\nc.beqz a0,.Lperipheral_primitives_edge_190cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_190d6\n");
    __builtin_unreachable();
}

/* Original0x190CE..0x190D2. */
REGION void tsl9_peripheral_primitives_block_190ce(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x190D2..0x190D6. */
REGION void tsl9_peripheral_primitives_block_190d2(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000024)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190D6..0x190DA. */
REGION void tsl9_peripheral_primitives_block_190d6(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".Lperipheral_primitives_edge_190d8:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_190d8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_190d2\n");
    __builtin_unreachable();
}

/* Original0x190DA..0x190E6. */
REGION void tsl9_resident_startup_provider_190da(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190E6..0x190E8. */
REGION void tsl9_resident_startup_provider_190e6(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_190e6:\n.option push\n.option rvc\nc.beqz a0,.Lperipheral_primitives_edge_190e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_190f6\n");
    __builtin_unreachable();
}

/* Original0x190E8..0x190F6. */
REGION void tsl9_peripheral_primitives_block_190e8(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x190F6..0x19106. */
REGION void tsl9_peripheral_primitives_block_190f6(void)
{
    REGS;
    a3 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000020)); LIVE;
    a4 = UINT32_C(0xffff8000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000020)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19106..0x19108. */
REGION void tsl9_resident_startup_provider_19106(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_19106:\n.option push\n.option rvc\nc.beqz a1,.Lperipheral_primitives_edge_19106\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_19114\n");
    __builtin_unreachable();
}

/* Original0x19108..0x19114. */
REGION void tsl9_peripheral_primitives_block_19108(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000014)); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000014)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19114..0x19124. */
REGION void tsl9_peripheral_primitives_block_19114(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)); LIVE;
    PORT(".option push\n.option norvc\nnot a0, a0\n.option pop\n");
    a0 = a0 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1919C..0x191AE. */
REGION void tsl9_peripheral_primitives_provider_1919c(void)
{
    REGS;
    a5 = UINT32_C(0x40003000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff804)); LIVE;
    a4 = a4 | UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff804)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x191AE..0x191C6. */
REGION void tsl9_peripheral_primitives_provider_191ae(void)
{
    REGS;
    a4 = UINT32_C(0x40003000); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffff804)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffff804)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x191C6..0x191CA. */
REGION void tsl9_resident_startup_provider_191c6(void)
{
    REGS;
    a2 = UINT32_C(0x40003000); LIVE;
    __builtin_unreachable();
}

/* Original0x191CA..0x191DA. */
REGION void tsl9_peripheral_primitives_block_191ca(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0xfffff818)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0xfffff818)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lperipheral_primitives_edge_191d6:\n.option push\n.option norvc\nbne a4,a3,.Lperipheral_primitives_edge_191d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_191ca\n");
    __builtin_unreachable();
}

/* Original0x191DA..0x191DE. */
REGION void tsl9_peripheral_primitives_block_191da(void)
{
    REGS;
    a2 = UINT32_C(0x40003000); LIVE;
    __builtin_unreachable();
}

/* Original0x191DE..0x191EE. */
REGION void tsl9_peripheral_primitives_block_191de(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0xfffff81c)); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0xfffff81c)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lperipheral_primitives_edge_191ea:\n.option push\n.option norvc\nbne a5,a3,.Lperipheral_primitives_edge_191ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_191de\n");
    __builtin_unreachable();
}

/* Original0x191EE..0x191F2. */
REGION void tsl9_peripheral_primitives_block_191ee(void)
{
    REGS;
    a1 = UINT32_C(0x40003000); LIVE;
    __builtin_unreachable();
}

/* Original0x191F2..0x19202. */
REGION void tsl9_peripheral_primitives_block_191f2(void)
{
    REGS;
    a2 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0xfffff818)); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0xfffff818)); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lperipheral_primitives_edge_191fe:\n.option push\n.option norvc\nbne a0,a2,.Lperipheral_primitives_edge_191fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_191f2\n");
    __builtin_unreachable();
}

/* Original0x19202..0x19206. */
REGION void tsl9_peripheral_primitives_block_19202(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_19202:\n.option push\n.option norvc\nbeq a4,a0,.Lperipheral_primitives_edge_19202\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_1921a\n");
    __builtin_unreachable();
}

/* Original0x19206..0x1920A. */
REGION void tsl9_peripheral_primitives_block_19206(void)
{
    REGS;
    a3 = UINT32_C(0x40003000); LIVE;
    __builtin_unreachable();
}

/* Original0x1920A..0x1921A. */
REGION void tsl9_peripheral_primitives_block_1920a(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff81c)); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff81c)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lperipheral_primitives_edge_19216:\n.option push\n.option norvc\nbne a5,a4,.Lperipheral_primitives_edge_19216\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_1920a\n");
    __builtin_unreachable();
}

/* Original0x1921A..0x19220. */
REGION void tsl9_peripheral_primitives_block_1921a(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19220..0x1922A. */
REGION void tsl9_resident_startup_provider_19220(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lperipheral_primitives_edge_19226:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_19226\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_peripheral_primitives_provider_1919c\n");
    __builtin_unreachable();
}

/* Original0x1922A..0x19248. */
REGION void tsl9_peripheral_primitives_block_1922a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0x40003000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a4 = a0 >> UINT32_C(0x00000010); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff818)) = (uint16_t)a4; LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff81c)) = (uint16_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19244:\n.option push\n.option norvc\njal zero,.Lperipheral_primitives_edge_19244\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_peripheral_primitives_provider_191ae\n");
    __builtin_unreachable();
}

/* Original0x19248..0x19252. */
REGION void tsl9_resident_startup_provider_19248(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lperipheral_primitives_edge_1924e:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_1924e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_peripheral_primitives_provider_1919c\n");
    __builtin_unreachable();
}

/* Original0x19252..0x19272. */
REGION void tsl9_peripheral_primitives_block_19252(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0x40003000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a4 = a0 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff808)) = (uint16_t)a4; LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff80c)) = (uint16_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_1926e:\n.option push\n.option norvc\njal zero,.Lperipheral_primitives_edge_1926e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_peripheral_primitives_provider_191ae\n");
    __builtin_unreachable();
}

/* Original0x1929A..0x19316. */
REGION void tsl9_resident_startup_provider_1929a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -80\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x0000006c); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 0(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0xffe49\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s5, 0x4\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x1b7\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0xdc\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -1856\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s6, s5, -384\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 1856\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, -1120\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s6, s0, s6\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 76(sp)\n.option pop\n");
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s10, 4\n.option pop\n");
    a4 = a4 & UINT32_C(0x000000f0); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)); LIVE;
    PORT(".option push\n.option norvc\nlui s9, 0x40022\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s11, 0x4\n.option pop\n");
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlui s7, 0xffff8\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s5, s5, -1\n.option pop\n");
    PORT(".option push\n.option rvc\nli s8, 2\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s2, s0, s2\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s3, s0, s3\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s4, s0, s4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19316..0x1933E. */
REGION void tsl9_peripheral_primitives_block_19316(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 79(s9)\n.option pop\n");
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 79(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nor a4, a4, s11\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nor a4, a4, s7\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a4, 76(s9)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1933E..0x1934A. */
REGION void tsl9_peripheral_primitives_block_1933e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19346:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_19346\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_1933e\n");
    __builtin_unreachable();
}

/* Original0x1934A..0x19386. */
REGION void tsl9_peripheral_primitives_block_1934a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 79(s9)\n.option pop\n");
    a4 = a4 & UINT32_C(0x000000fd); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 79(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 79(s9)\n.option pop\n");
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 79(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nor a4, a4, s11\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nor a4, a4, s7\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a4, 76(s9)\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19382:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_19382\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x19386..0x19388. */
REGION void tsl9_peripheral_primitives_block_19386(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19388..0x1938E. */
REGION void tsl9_peripheral_primitives_block_19388(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".Lperipheral_primitives_edge_1938a:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_1938a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x1938E..0x19394. */
REGION void tsl9_peripheral_primitives_block_1938e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lperipheral_primitives_edge_19390:\n.option push\n.option norvc\nbeq a0,a5,.Lperipheral_primitives_edge_19390\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19388\n");
    __builtin_unreachable();
}

/* Original0x19394..0x193A0. */
REGION void tsl9_peripheral_primitives_block_19394(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nor a5, a5, s11\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 76(s9)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x193A0..0x193AC. */
REGION void tsl9_peripheral_primitives_block_193a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 76(s9)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_193a8:\n.option push\n.option norvc\nbltz a5,.Lperipheral_primitives_edge_193a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_193a0\n");
    __builtin_unreachable();
}

/* Original0x193AC..0x193B8. */
REGION void tsl9_peripheral_primitives_block_193ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_193b4:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_193b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_193ac\n");
    __builtin_unreachable();
}

/* Original0x193B8..0x193D2. */
REGION void tsl9_peripheral_primitives_block_193b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 76(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 78(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\nand a4, s5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a5, s5, a5\n.option pop\n");
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option norvc\nsub a4, a4, s6\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_193ce:\n.option push\n.option norvc\nble a4,s2,.Lperipheral_primitives_edge_193ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_193d6\n");
    __builtin_unreachable();
}

/* Original0x193D2..0x193D6. */
REGION void tsl9_peripheral_primitives_block_193d2(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_193d2:\n.option push\n.option norvc\nblt a4,s3,.Lperipheral_primitives_edge_193d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19406\n");
    __builtin_unreachable();
}

/* Original0x193D6..0x193E0. */
REGION void tsl9_peripheral_primitives_block_193d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s10, s10, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s10, s10, 255\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_193dc:\n.option push\n.option norvc\nbeqz s10,.Lperipheral_primitives_edge_193dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19406\n");
    __builtin_unreachable();
}

/* Original0x193E0..0x193EC. */
REGION void tsl9_peripheral_primitives_block_193e0(void)
{
    REGS;
    a5 = a4 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, s4\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_193e8:\n.option push\n.option norvc\nblez a4,.Lperipheral_primitives_edge_193e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19402\n");
    __builtin_unreachable();
}

/* Original0x193EC..0x193EE. */
REGION void tsl9_peripheral_primitives_block_193ec(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x193EE..0x19402. */
REGION void tsl9_peripheral_primitives_block_193ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a3, 54(s9)\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a5, a5, s8\n.option pop\n");
    a5 = a5 + a3; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 54(s9)\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19400:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_19400\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_19316\n");
    __builtin_unreachable();
}

/* Original0x19402..0x19406. */
REGION void tsl9_peripheral_primitives_block_19402(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lperipheral_primitives_edge_19404:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_19404\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_193ee\n");
    __builtin_unreachable();
}

/* Original0x19406..0x19456. */
REGION void tsl9_peripheral_primitives_block_19406(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a4 = a4 & UINT32_C(0x000000f0); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)); LIVE;
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000049)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)) = (uint16_t)a4; LIVE;
    a3 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x19456..0x19466. */
REGION void tsl9_peripheral_primitives_block_19456(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a5 = a3 + UINT32_C(0x0000002c); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19462:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_19462\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19456\n");
    __builtin_unreachable();
}

/* Original0x19466..0x1949E. */
REGION void tsl9_peripheral_primitives_block_19466(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    PORT(".Lperipheral_primitives_edge_1949a:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_1949a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x1949E..0x194A0. */
REGION void tsl9_peripheral_primitives_block_1949e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x194A0..0x194A4. */
REGION void tsl9_peripheral_primitives_block_194a0(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_194a0:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_194a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x194A4..0x194A8. */
REGION void tsl9_peripheral_primitives_block_194a4(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_194a4:\n.option push\n.option norvc\nbeq a0,s2,.Lperipheral_primitives_edge_194a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_194a0\n");
    __builtin_unreachable();
}

/* Original0x194A8..0x194BC. */
REGION void tsl9_peripheral_primitives_block_194a8(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x194BC..0x194C8. */
REGION void tsl9_peripheral_primitives_block_194bc(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_194c4:\n.option push\n.option norvc\nbltz a5,.Lperipheral_primitives_edge_194c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_194bc\n");
    __builtin_unreachable();
}

/* Original0x194C8..0x194CC. */
REGION void tsl9_peripheral_primitives_block_194c8(void)
{
    REGS;
    a3 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x194CC..0x194D8. */
REGION void tsl9_peripheral_primitives_block_194cc(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_194d4:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_194d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_194cc\n");
    __builtin_unreachable();
}

/* Original0x194D8..0x19528. */
REGION void tsl9_peripheral_primitives_block_194d8(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004e)); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0xf4\n.option pop\n");
    a5 = UINT32_C(0x00004000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s2, 576\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s2, s0, s2\n.option pop\n");
    a4 = a4 & a5; LIVE;
    a2 = UINT32_C(0x00009000); LIVE;
    a2 = a2 + UINT32_C(0xfffffca0); LIVE;
    a5 = a5 * a3; LIVE;
    a4 = a4 + a5; LIVE;
    a5 = UINT32_C(0x000003e8); LIVE;
    PORT(".option push\n.option norvc\ndiv s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a3, s2, a5\n.option pop\n");
    a5 = UINT32_C(0x000000c8); LIVE;
    a4 = a4 - a3; LIVE;
    a3 = UINT32_C(0x000002ec); LIVE;
    PORT(".option push\n.option norvc\nmul a3, s0, a3\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a3, a3, a2\n.option pop\n");
    a5 = a4 * a5; LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a3\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19524:\n.option push\n.option norvc\nblez a4,.Lperipheral_primitives_edge_19524\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_196bc\n");
    __builtin_unreachable();
}

/* Original0x19528..0x1952A. */
REGION void tsl9_peripheral_primitives_block_19528(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1952A..0x19592. */
REGION void tsl9_peripheral_primitives_block_1952a(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x40022000); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000036)); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 + a3; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000036)) = (uint16_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000049)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a5 = a5 & UINT32_C(0x000000f0); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000049)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000049)); LIVE;
    PORT(".option push\n.option rvc\nor a5, a5, s1\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000049)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000004f)); LIVE;
    a5 = a5 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000004f)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000004f)); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000004f)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)) = (uint16_t)a5; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)) = (uint16_t)a5; LIVE;
    a3 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x19592..0x195A2. */
REGION void tsl9_peripheral_primitives_block_19592(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a5 = a3 + UINT32_C(0x0000002c); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_1959e:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_1959e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19592\n");
    __builtin_unreachable();
}

/* Original0x195A2..0x195DA. */
REGION void tsl9_peripheral_primitives_block_195a2(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)); LIVE;
    a4 = a4 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    PORT(".Lperipheral_primitives_edge_195d6:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_195d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x195DA..0x195DC. */
REGION void tsl9_peripheral_primitives_block_195da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x195DC..0x195E0. */
REGION void tsl9_peripheral_primitives_block_195dc(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_195dc:\n.option push\n.option norvc\njal ra,.Lperipheral_primitives_edge_195dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_191c6\n");
    __builtin_unreachable();
}

/* Original0x195E0..0x195E4. */
REGION void tsl9_peripheral_primitives_block_195e0(void)
{
    REGS;
    PORT(".Lperipheral_primitives_edge_195e0:\n.option push\n.option norvc\nbeq a0,s3,.Lperipheral_primitives_edge_195e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_195dc\n");
    __builtin_unreachable();
}

/* Original0x195E4..0x195F8. */
REGION void tsl9_peripheral_primitives_block_195e4(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a3 = UINT32_C(0x00004000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x195F8..0x19604. */
REGION void tsl9_peripheral_primitives_block_195f8(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000004c)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19600:\n.option push\n.option norvc\nbltz a5,.Lperipheral_primitives_edge_19600\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_195f8\n");
    __builtin_unreachable();
}

/* Original0x19604..0x19608. */
REGION void tsl9_peripheral_primitives_block_19604(void)
{
    REGS;
    a3 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x19608..0x19614. */
REGION void tsl9_peripheral_primitives_block_19608(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_19610:\n.option push\n.option norvc\nbgez a4,.Lperipheral_primitives_edge_19610\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_19608\n");
    __builtin_unreachable();
}

/* Original0x19614..0x19682. */
REGION void tsl9_peripheral_primitives_block_19614(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)); LIVE;
    a5 = UINT32_C(0x00004000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004f)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000004c)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000004e)); LIVE;
    a4 = a4 & a5; LIVE;
    a5 = a5 * a3; LIVE;
    a4 = a4 + a5; LIVE;
    a5 = UINT32_C(0x00002000); LIVE;
    a5 = a5 + UINT32_C(0xffffff40); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s2, a5, s2\n.option pop\n");
    a5 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\ndiv s2, s2, a5\n.option pop\n");
    a5 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\nslli s2, s2, 0x3\n.option pop\n");
    PORT(".option push\n.option norvc\nsub s2, a4, s2\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll s1, a4, s1\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\ndiv s1, s1, a4\n.option pop\n");
    a4 = UINT32_C(0x00009000); LIVE;
    a4 = a4 + UINT32_C(0xfffffca0); LIVE;
    PORT(".option push\n.option norvc\nmul s0, s1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nli s1, 748\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s0, s0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv s0, s0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a5, s2, a5\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a5, a5, s0\n.option pop\n");
    PORT(".Lperipheral_primitives_edge_1967e:\n.option push\n.option norvc\nblez s2,.Lperipheral_primitives_edge_1967e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_primitives_block_196c0\n");
    __builtin_unreachable();
}

/* Original0x19682..0x19684. */
REGION void tsl9_peripheral_primitives_block_19682(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x19684..0x196BC. */
REGION void tsl9_peripheral_primitives_block_19684(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x40022000); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000036)); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 + a3; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000036)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 80\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x196BC..0x196C0. */
REGION void tsl9_peripheral_primitives_block_196bc(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lperipheral_primitives_edge_196be:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_196be\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_1952a\n");
    __builtin_unreachable();
}

/* Original0x196C0..0x196C4. */
REGION void tsl9_peripheral_primitives_block_196c0(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lperipheral_primitives_edge_196c2:\n.option push\n.option rvc\nc.j .Lperipheral_primitives_edge_196c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_primitives_block_19684\n");
    __builtin_unreachable();
}

/* Original0x19764..0x1978C. */
REGION void tsl9_resident_startup_provider_19764(void)
{
    REGS;
    a5 = UINT32_C(0xe000f000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a4 = a4 & UINT32_C(0xfffffffe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000017e)); LIVE;
    a2 = a4 * a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000010); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000021); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x1978C..0x19792. */
REGION void tsl9_peripheral_primitives_block_1978c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_primitives_edge_19790:\n.option push\n.option rvc\nc.beqz a4,.Lperipheral_primitives_edge_19790\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_primitives_block_1978c\n");
    __builtin_unreachable();
}

/* Original0x19792..0x1979A. */
REGION void tsl9_peripheral_primitives_block_19792(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
