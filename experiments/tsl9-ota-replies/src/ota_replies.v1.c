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

/* Six complete original OTA response functions:334B/127i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x8E18..0x8E24. */
REGION void tsl9_ota_external_8e18(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lota_replies_edge_8e20:\n.option push\n.option norvc\nbeq a0,a5,.Lota_replies_edge_8e20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_replies_block_8e52\n");
    __builtin_unreachable();
}

/* Original0x8E24..0x8E32. */
REGION void tsl9_ota_replies_block_8e24(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000017c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8E32..0x8E3E. */
REGION void tsl9_ota_replies_block_8e32(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lota_replies_edge_8e3a:\n.option push\n.option norvc\nbeq a0,a5,.Lota_replies_edge_8e3a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_replies_block_8e4c\n");
    __builtin_unreachable();
}

/* Original0x8E3E..0x8E4A. */
REGION void tsl9_ota_replies_block_8e3e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 380(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8E4A..0x8E4C. */
REGION void tsl9_ota_replies_block_8e4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8E4C..0x8E52. */
REGION void tsl9_ota_replies_block_8e4c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8E52..0x8E5E. */
REGION void tsl9_ota_replies_block_8e52(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lota_replies_edge_8e5a:\n.option push\n.option norvc\nbeq a0,a5,.Lota_replies_edge_8e5a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_replies_block_8e68\n");
    __builtin_unreachable();
}

/* Original0x8E5E..0x8E68. */
REGION void tsl9_ota_replies_block_8e5e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 380(a5)\n.option pop\n");
    PORT(".Lota_replies_edge_8e66:\n.option push\n.option rvc\nc.j .Lota_replies_edge_8e66\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_replies_block_8e4a\n");
    __builtin_unreachable();
}

/* Original0x8E68..0x8E6A. */
REGION void tsl9_ota_replies_block_8e68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x99E8..0x99F6. */
REGION void tsl9_ota_external_99e8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x02000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lota_replies_edge_99f2:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_99f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_1917e\n");
    __builtin_unreachable();
}

/* Original0x99F6..0x9A00. */
REGION void tsl9_ota_replies_block_99f6(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x02000000); LIVE;
    PORT(".Lota_replies_edge_99fc:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_99fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_1917e\n");
    __builtin_unreachable();
}

/* Original0x9A00..0x9A06. */
REGION void tsl9_ota_replies_block_9a00(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lota_replies_edge_9a02:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_9a02\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_reply_external_16e0c\n");
    __builtin_unreachable();
}

/* Original0x9A06..0x9A0C. */
REGION void tsl9_ota_replies_block_9a06(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lota_replies_edge_9a08:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_9a08\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_reply_external_16e0c\n");
    __builtin_unreachable();
}

/* Original0x9A0C..0x9A22. */
REGION void tsl9_ota_replies_block_9a0c(void)
{
    REGS;
    a5 = UINT32_C(0x00000088); LIVE;
    PORT(".option push\n.option norvc\ncsrc 0x800, a5\n.option pop\n");
    a5 = UINT32_C(0xbeef0000); LIVE;
    a4 = UINT32_C(0xe000e000); LIVE;
    a5 = a5 + UINT32_C(0x00000080); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000048)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x9A22..0x9A24. */
REGION void tsl9_ota_replies_block_9a22(void)
{
    REGS;
    PORT(".Lota_replies_edge_9a22:\n.option push\n.option rvc\nc.j .Lota_replies_edge_9a22\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_replies_block_9a22\n");
    __builtin_unreachable();
}

/* Original0x9B8E..0x9BB0. */
REGION void tsl9_ota_external_9b8e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 112(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    a0 = UINT32_C(0x00000402); LIVE;
    PORT(".option push\n.option rvc\nmv s4, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9BB0..0x9BB2. */
REGION void tsl9_ota_replies_block_9bb0(void)
{
    REGS;
    PORT(".Lota_replies_edge_9bb0:\n.option push\n.option rvc\nc.beqz a0,.Lota_replies_edge_9bb0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_replies_block_9bfa\n");
    __builtin_unreachable();
}

/* Original0x9BB2..0x9BD6. */
REGION void tsl9_ota_replies_block_9bb2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a5, s1, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 1(a0)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    a1 = UINT32_C(0x00020000); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 76(s2)\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nadd a1, a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a2 = UINT32_C(0x00000400); LIVE;
    a1 = a1 << UINT32_C(0x0000000a); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9BD6..0x9BE4. */
REGION void tsl9_ota_replies_block_9bd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s4\n.option pop\n");
    a3 = UINT32_C(0x00000402); LIVE;
    PORT(".Lota_replies_edge_9be0:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_9be0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_filter_external_8a56\n");
    __builtin_unreachable();
}

/* Original0x9BE4..0x9BFA. */
REGION void tsl9_ota_replies_block_9be4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9BFA..0x9C0A. */
REGION void tsl9_ota_replies_block_9bfa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9EE0..0x9EE8. */
REGION void tsl9_ota_external_9ee0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lota_replies_edge_9ee6:\n.option push\n.option rvc\nc.jal .Lota_replies_edge_9ee6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_reply_external_9ea6\n");
    __builtin_unreachable();
}

/* Original0x9EE8..0x9EF0. */
REGION void tsl9_ota_replies_block_9ee8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lota_replies_edge_9eee:\n.option push\n.option rvc\nc.j .Lota_replies_edge_9eee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_external_99e8\n");
    __builtin_unreachable();
}

/* Original0x13E98..0x13EA2. */
REGION void tsl9_ota_external_13e98(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a6, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a7, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    PORT(".Lota_replies_edge_13ea0:\n.option push\n.option rvc\nc.beqz a2,.Lota_replies_edge_13ea0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_replies_block_13ea4\n");
    __builtin_unreachable();
}

/* Original0x13EA2..0x13EA4. */
REGION void tsl9_ota_replies_block_13ea2(void)
{
    REGS;
    PORT(".Lota_replies_edge_13ea2:\n.option push\n.option rvc\nc.bnez a3,.Lota_replies_edge_13ea2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_replies_block_13eb0\n");
    __builtin_unreachable();
}

/* Original0x13EA4..0x13EB0. */
REGION void tsl9_ota_replies_block_13ea4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a7\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a6\n.option pop\n");
    PORT(".Lota_replies_edge_13eac:\n.option push\n.option norvc\njal zero,.Lota_replies_edge_13eac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_filter_external_8a56\n");
    __builtin_unreachable();
}

/* Original0x13EB0..0x13EB4. */
REGION void tsl9_ota_replies_block_13eb0(void)
{
    REGS;
    PORT(".Lota_replies_edge_13eb0:\n.option push\n.option norvc\njal zero,.Lota_replies_edge_13eb0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_events_13b4c\n");
    __builtin_unreachable();
}

/* Original0x13F66..0x13F78. */
REGION void tsl9_ota_external_13f66(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a2; LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\naddi a2, sp, 15\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lota_replies_edge_13f74:\n.option push\n.option norvc\njal ra,.Lota_replies_edge_13f74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_events_13b4c\n");
    __builtin_unreachable();
}

/* Original0x13F78..0x13F7E. */
REGION void tsl9_ota_replies_block_13f78(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
