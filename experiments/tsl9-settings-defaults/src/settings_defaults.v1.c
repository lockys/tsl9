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

/* Twelve complete original settings functions:878B/297i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x12E54..0x12E70. */
REGION void tsl9_settings_writer_12e54(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x0000062e); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12E70..0x12E7E. */
REGION void tsl9_settings_defaults_block_12e70(void)
{
    REGS;
    a0 = UINT32_C(0x08078000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff900); LIVE;
    PORT(".Lsettings_defaults_edge_12e7a:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_12e7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x12E7E..0x12E86. */
REGION void tsl9_settings_defaults_block_12e7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12E86..0x12EA4. */
REGION void tsl9_main_init_external_12e86(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1540\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12EA4..0x12EE6. */
REGION void tsl9_settings_defaults_block_12ea4(void)
{
    REGS;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 255(s0)\n.option pop\n");
    a5 = UINT32_C(0x0b431000); LIVE;
    a5 = a5 + UINT32_C(0x00000402); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x0d451000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc44); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0x2b0c3000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc0a); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 8(s0)\n.option pop\n");
    a5 = UINT32_C(0x5f1f5000); LIVE;
    a5 = a5 + UINT32_C(0x0000001e); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 12(s0)\n.option pop\n");
    a5 = UINT32_C(0x2a212000); LIVE;
    a5 = a5 + UINT32_C(0xfffffe20); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 16(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_12ee2:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_12ee2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_12e54\n");
    __builtin_unreachable();
}

/* Original0x12EE6..0x12F02. */
REGION void tsl9_settings_writer_12ee6(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000414); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F02..0x12F10. */
REGION void tsl9_settings_defaults_block_12f02(void)
{
    REGS;
    a0 = UINT32_C(0x08078000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lsettings_defaults_edge_12f0c:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_12f0c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x12F10..0x12F18. */
REGION void tsl9_settings_defaults_block_12f10(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F18..0x12F36. */
REGION void tsl9_main_init_external_12f18(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1002\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F36..0x12F48. */
REGION void tsl9_settings_defaults_block_12f36(void)
{
    REGS;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 255(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_12f44:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_12f44\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_12ee6\n");
    __builtin_unreachable();
}

/* Original0x12F48..0x12F64. */
REGION void tsl9_settings_writer_12f48(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x0000063a); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F64..0x12F72. */
REGION void tsl9_settings_defaults_block_12f64(void)
{
    REGS;
    a0 = UINT32_C(0x08077000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000700); LIVE;
    PORT(".Lsettings_defaults_edge_12f6e:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_12f6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x12F72..0x12F7A. */
REGION void tsl9_settings_defaults_block_12f72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F7A..0x12F98. */
REGION void tsl9_main_init_external_12f7a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1552\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12F98..0x13052. */
REGION void tsl9_settings_defaults_block_12f98(void)
{
    REGS;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 255(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a4 = UINT32_C(0xff000000); LIVE;
    a3 = UINT32_C(0x049aa000); LIVE;
    a5 = a5 & UINT32_C(0x00000200); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x99800000); LIVE;
    a5 = a5 + UINT32_C(0x00000300); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    a4 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + UINT32_C(0xffffff04); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\nlw a4, 12(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a5, 8(s0)\n.option pop\n");
    a5 = UINT32_C(0x02000000); LIVE;
    a4 = a4 & a5; LIVE;
    a3 = a3 + UINT32_C(0x00000023); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option rvc\nsw a4, 12(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a3, 20(s0)\n.option pop\n");
    a4 = UINT32_C(0x03000000); LIVE;
    a4 = a4 + UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nsw a4, 16(s0)\n.option pop\n");
    a4 = UINT32_C(0x00020000); LIVE;
    a4 = a4 & a3; LIVE;
    a3 = UINT32_C(0xff08a000); LIVE;
    a3 = a3 + UINT32_C(0xfffffb00); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option rvc\nsw a4, 20(s0)\n.option pop\n");
    a4 = UINT32_C(0xa0230000); LIVE;
    PORT(".option push\n.option rvc\nsw a4, 24(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 28(s0)\n.option pop\n");
    a3 = UINT32_C(0x00ff1000); LIVE;
    a3 = a3 + UINT32_C(0xfffff89c); LIVE;
    a4 = a4 & UINT32_C(0x00000200); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option rvc\nsw a4, 28(s0)\n.option pop\n");
    a4 = UINT32_C(0x9f000000); LIVE;
    a4 = a4 + UINT32_C(0x00000300); LIVE;
    PORT(".option push\n.option rvc\nsw a4, 32(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 36(s0)\n.option pop\n");
    a3 = UINT32_C(0xff010000); LIVE;
    a3 = a3 + UINT32_C(0xffffff0c); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option rvc\nsw a4, 36(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 48(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 & a4; LIVE;
    a4 = UINT32_C(0x0c9ea000); LIVE;
    a4 = a4 + UINT32_C(0xfffff803); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 40(s0)\n.option pop\n");
    a5 = UINT32_C(0x03ff0000); LIVE;
    a5 = a5 + UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 44(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_1304e:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_1304e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_12f48\n");
    __builtin_unreachable();
}

/* Original0x13052..0x1306E. */
REGION void tsl9_settings_writer_13052(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000630); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1306E..0x1307C. */
REGION void tsl9_settings_defaults_block_1306e(void)
{
    REGS;
    a0 = UINT32_C(0x08077000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000600); LIVE;
    PORT(".Lsettings_defaults_edge_13078:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_13078\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x1307C..0x13084. */
REGION void tsl9_settings_defaults_block_1307c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13084..0x130A2. */
REGION void tsl9_main_init_external_13084(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1542\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x130A2..0x130D6. */
REGION void tsl9_settings_defaults_block_130a2(void)
{
    REGS;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 255(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a4 = UINT32_C(0x00ff1000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 & UINT32_C(0x00000200); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x00006000); LIVE;
    a5 = a5 + UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_130d2:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_130d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13052\n");
    __builtin_unreachable();
}

/* Original0x130D6..0x130F2. */
REGION void tsl9_settings_writer_130d6(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000085); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000324); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x130F2..0x13100. */
REGION void tsl9_settings_defaults_block_130f2(void)
{
    REGS;
    a0 = UINT32_C(0x08077000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000500); LIVE;
    PORT(".Lsettings_defaults_edge_130fc:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_130fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x13100..0x13108. */
REGION void tsl9_settings_defaults_block_13100(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13108..0x13126. */
REGION void tsl9_main_init_external_13108(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 762\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000085); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13126..0x13138. */
REGION void tsl9_settings_defaults_block_13126(void)
{
    REGS;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 132(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_13134:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_13134\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_130d6\n");
    __builtin_unreachable();
}

/* Original0x13138..0x13154. */
REGION void tsl9_settings_writer_13138(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a2 = UINT32_C(0x00000070); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff9\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000152); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13154..0x13162. */
REGION void tsl9_settings_defaults_block_13154(void)
{
    REGS;
    a0 = UINT32_C(0x08078000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffa00); LIVE;
    PORT(".Lsettings_defaults_edge_1315e:\n.option push\n.option norvc\njal ra,.Lsettings_defaults_edge_1315e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x13162..0x1316A. */
REGION void tsl9_settings_defaults_block_13162(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1316A..0x1318A. */
REGION void tsl9_main_init_external_1316a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 294\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000070); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1318A..0x131B6. */
REGION void tsl9_settings_defaults_block_1318a(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 2(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000101); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 8(s0)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nlw a5, 76(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsettings_defaults_literal_131aa:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_settings_default_data_1a69c\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsettings_defaults_literal_131aa\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x131B6..0x131C2. */
REGION void tsl9_settings_defaults_block_131b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_defaults_edge_131be:\n.option push\n.option norvc\njal zero,.Lsettings_defaults_edge_131be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13138\n");
    __builtin_unreachable();
}
