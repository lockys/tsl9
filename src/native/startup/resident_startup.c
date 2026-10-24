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

/* Eight complete resident startup functions:1082B/385i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x1979A..0x197B0. */
REGION void tsl9_resident_startup_provider_1979a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a2 = a1 << UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x197B0..0x197B8. */
REGION void tsl9_resident_startup_block_197b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x197B8..0x197BE. */
REGION void tsl9_resident_startup_provider_197b8(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_startup_edge_197ba:\n.option push\n.option norvc\njal zero,.Lresident_startup_edge_197ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_1929a\n");
    __builtin_unreachable();
}

/* Original0x197BE..0x197CC. */
REGION void tsl9_resident_startup_provider_197be(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_startup_edge_197c8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_197c8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18e98\n");
    __builtin_unreachable();
}

/* Original0x197CC..0x197D2. */
REGION void tsl9_resident_startup_block_197cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_startup_edge_197ce:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_197ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18ec4\n");
    __builtin_unreachable();
}

/* Original0x197D2..0x197DC. */
REGION void tsl9_resident_startup_block_197d2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a2\n.option pop\n");
    PORT(".Lresident_startup_edge_197d8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_197d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18ef2\n");
    __builtin_unreachable();
}

/* Original0x197DC..0x197E0. */
REGION void tsl9_resident_startup_block_197dc(void)
{
    REGS;
    PORT(".Lresident_startup_edge_197dc:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_197dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18eb6\n");
    __builtin_unreachable();
}

/* Original0x197E0..0x197E6. */
REGION void tsl9_resident_startup_block_197e0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_197e2:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_197e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_19764\n");
    __builtin_unreachable();
}

/* Original0x197E6..0x197F0. */
REGION void tsl9_resident_startup_block_197e6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x197F0..0x19818. */
REGION void tsl9_resident_startup_provider_197f0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -128\n.option pop\n");
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 124(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 116(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 120(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 112(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 108(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 104(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 100(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 96(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 76(sp)\n.option pop\n");
    PORT(".Lresident_startup_edge_19814:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19814\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_tagged_external_8520\n");
    __builtin_unreachable();
}

/* Original0x19818..0x19872. */
REGION void tsl9_resident_startup_block_19818(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    PORT(".option push\n.option norvc\nlw s11, 24(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s10, 4(a5)\n.option pop\n");
    a5 = UINT32_C(0x40012000); LIVE;
    PORT(".option push\n.option norvc\naddi s1, a5, 1024\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s9, 4(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s8, 8(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s7, 44(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s6, 48(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 52(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s4, 12(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 16(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 20(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 24(s1)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000200); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 28(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40012\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 32(s1)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 36(s1)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 40(s1)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 56(s1)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_startup_edge_1986e:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_1986e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19124\n");
    __builtin_unreachable();
}

/* Original0x19872..0x19878. */
REGION void tsl9_resident_startup_block_19872(void)
{
    REGS;
    a0 = UINT32_C(0x0000c000); LIVE;
    PORT(".Lresident_startup_edge_19874:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19874\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_1908c\n");
    __builtin_unreachable();
}

/* Original0x19878..0x1987E. */
REGION void tsl9_resident_startup_block_19878(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_startup_edge_1987a:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_1987a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_188e2\n");
    __builtin_unreachable();
}

/* Original0x1987E..0x1989A. */
REGION void tsl9_resident_startup_block_1987e(void)
{
    REGS;
    a4 = UINT32_C(0x000e0000); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 32\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000034)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000020)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000024)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000028)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000030)) = (uint32_t)0; LIVE;
    PORT(".Lresident_startup_edge_19896:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19896\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_1892e\n");
    __builtin_unreachable();
}

/* Original0x1989A..0x198A2. */
REGION void tsl9_resident_startup_block_1989a(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_startup_edge_1989e:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_1989e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18986\n");
    __builtin_unreachable();
}

/* Original0x198A2..0x198AA. */
REGION void tsl9_resident_startup_block_198a2(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_startup_edge_198a6:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18a98\n");
    __builtin_unreachable();
}

/* Original0x198AA..0x198B0. */
REGION void tsl9_resident_startup_block_198aa(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_198ac:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18a6e\n");
    __builtin_unreachable();
}

/* Original0x198B0..0x198BC. */
REGION void tsl9_resident_startup_block_198b0(void)
{
    REGS;
    a3 = UINT32_C(0x00000007); LIVE;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_startup_edge_198b8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_189ae\n");
    __builtin_unreachable();
}

/* Original0x198BC..0x198C4. */
REGION void tsl9_resident_startup_block_198bc(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_startup_edge_198c0:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18996\n");
    __builtin_unreachable();
}

/* Original0x198C4..0x198C6. */
REGION void tsl9_resident_startup_block_198c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x198C6..0x198CE. */
REGION void tsl9_resident_startup_block_198c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_startup_edge_198ca:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18a8e\n");
    __builtin_unreachable();
}

/* Original0x198CE..0x198D8. */
REGION void tsl9_resident_startup_block_198ce(void)
{
    REGS;
    a5 = UINT32_C(0x40012000); LIVE;
    a5 = a5 + UINT32_C(0x00000400); LIVE;
    PORT(".Lresident_startup_edge_198d6:\n.option push\n.option rvc\nc.beqz a0,.Lresident_startup_edge_198d6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_198c6\n");
    __builtin_unreachable();
}

/* Original0x198D8..0x198E0. */
REGION void tsl9_resident_startup_block_198d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 1024\n.option pop\n");
    PORT(".Lresident_startup_edge_198dc:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18a66\n");
    __builtin_unreachable();
}

/* Original0x198E0..0x198EA. */
REGION void tsl9_resident_startup_block_198e0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 1024\n.option pop\n");
    PORT(".Lresident_startup_edge_198e6:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_198e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_188e2\n");
    __builtin_unreachable();
}

/* Original0x198EA..0x1995C. */
REGION void tsl9_resident_startup_block_198ea(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    PORT(".option push\n.option norvc\nsw s11, 24(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s10, 4(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s9, 1028(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s8, 1032(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s7, 1068(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s6, 1072(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s5, 1076(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s4, 1036(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 1040(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s2, 1044(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1048(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 124(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1052(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nlw s1, 116(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 112(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1056(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)); LIVE;
    PORT(".option push\n.option rvc\nlw s3, 108(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 104(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1060(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)); LIVE;
    PORT(".option push\n.option rvc\nlw s5, 100(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 96(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1064(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)); LIVE;
    PORT(".option push\n.option rvc\nlw s7, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 1080(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 120(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 128\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1995C..0x19970. */
REGION void tsl9_resident_startup_provider_1995c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lresident_startup_edge_1996c:\n.option push\n.option norvc\nbgez a5,.Lresident_startup_edge_1996c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_startup_block_1998c\n");
    __builtin_unreachable();
}

/* Original0x19970..0x19978. */
REGION void tsl9_resident_startup_block_19970(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 108(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19978..0x1997A. */
REGION void tsl9_resident_startup_block_19978(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19978:\n.option push\n.option rvc\nc.beqz a0,.Lresident_startup_edge_19978\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_1997e\n");
    __builtin_unreachable();
}

/* Original0x1997A..0x1997E. */
REGION void tsl9_resident_startup_block_1997a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 104(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1997E..0x19980. */
REGION void tsl9_resident_startup_block_1997e(void)
{
    REGS;
    a0 = UINT32_C(0x00008000); LIVE;
    __builtin_unreachable();
}

/* Original0x19980..0x19982. */
REGION void tsl9_resident_startup_block_19980(void)
{
    REGS;
    PORT(".option push\n.option rvc\nxor a0, a0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19982..0x1998C. */
REGION void tsl9_resident_startup_block_19982(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1998C..0x19996. */
REGION void tsl9_resident_startup_block_1998c(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    a0 = a1 ^ UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_19994:\n.option push\n.option rvc\nc.bnez a5,.Lresident_startup_edge_19994\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_19982\n");
    __builtin_unreachable();
}

/* Original0x19996..0x1999E. */
REGION void tsl9_resident_startup_block_19996(void)
{
    REGS;
    a5 = a1 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_startup_edge_1999a:\n.option push\n.option norvc\nbgez a5,.Lresident_startup_edge_1999a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_startup_block_199c2\n");
    __builtin_unreachable();
}

/* Original0x1999E..0x199A8. */
REGION void tsl9_resident_startup_block_1999e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 492(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x199A8..0x199AC. */
REGION void tsl9_resident_startup_block_199a8(void)
{
    REGS;
    PORT(".Lresident_startup_edge_199a8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_199a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_197b8\n");
    __builtin_unreachable();
}

/* Original0x199AC..0x199BE. */
REGION void tsl9_resident_startup_block_199ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 88(s1)\n.option pop\n");
    a2 = UINT32_C(0x0002f000); LIVE;
    a2 = a2 + UINT32_C(0xfffffe00); LIVE;
    a1 = UINT32_C(0x00002000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000184)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x199BE..0x199C2. */
REGION void tsl9_resident_startup_block_199be(void)
{
    REGS;
    a0 = UINT32_C(0x00002000); LIVE;
    PORT(".Lresident_startup_edge_199c0:\n.option push\n.option rvc\nc.j .Lresident_startup_edge_199c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_block_19980\n");
    __builtin_unreachable();
}

/* Original0x199C2..0x199CC. */
REGION void tsl9_resident_startup_block_199c2(void)
{
    REGS;
    a5 = a1 << UINT32_C(0x00000011); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_startup_edge_199c8:\n.option push\n.option norvc\nbgez a5,.Lresident_startup_edge_199c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_startup_block_19982\n");
    __builtin_unreachable();
}

/* Original0x199CC..0x199DE. */
REGION void tsl9_resident_startup_block_199cc(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000640); LIVE;
    a1 = UINT32_C(0x00004000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000184)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x199DE..0x199E2. */
REGION void tsl9_resident_startup_block_199de(void)
{
    REGS;
    a0 = UINT32_C(0x00004000); LIVE;
    PORT(".Lresident_startup_edge_199e0:\n.option push\n.option rvc\nc.j .Lresident_startup_edge_199e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_block_19980\n");
    __builtin_unreachable();
}

/* Original0x199E2..0x19A06. */
REGION void tsl9_main_runtime_external_199e2(void)
{
    REGS;
    a5 = UINT32_C(0x20000000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -96\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 88(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x00000180)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 60(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 52(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 92(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000015); LIVE;
    PORT(".Lresident_startup_literal_199fc:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_version_1ab1c\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_199fc\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19A06..0x19A08. */
REGION void tsl9_resident_startup_block_19a06(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19a06:\n.option push\n.option rvc\nc.bnez a0,.Lresident_startup_edge_19a06\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_19a0a\n");
    __builtin_unreachable();
}

/* Original0x19A08..0x19A0A. */
REGION void tsl9_resident_startup_block_19a08(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19a08:\n.option push\n.option rvc\nc.j .Lresident_startup_edge_19a08\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_block_19a08\n");
    __builtin_unreachable();
}

/* Original0x19A0A..0x19A3A. */
REGION void tsl9_resident_startup_block_19a0a(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a3 = UINT32_C(0x90000000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a3 = UINT32_C(0x30000000); LIVE;
    a2 = UINT32_C(0x00000040); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a3 = UINT32_C(0x03000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19A3A..0x19AB8. */
REGION void tsl9_resident_startup_block_19a3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffea\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000752); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00007000); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x08078000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc00); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00001000); LIVE;
    a4 = a5 + UINT32_C(0xfffff803); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001e)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x000000fb); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    a5 = a5 + UINT32_C(0xfffffe3f); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000022)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000024)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 124(s0)\n.option pop\n");
    PORT(".Lresident_startup_literal_19a76:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_1979a\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19a76\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000048)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_startup_literal_19a80:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_197be\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19a80\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000004c)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00004000); LIVE;
    a4 = a4 + UINT32_C(0xfffffe80); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000034)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_startup_literal_19a92:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_197f0\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19a92\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000002e)) = (uint16_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000003c)) = (uint32_t)a5; LIVE;
    a4 = UINT32_C(0x000003e8); LIVE;
    PORT(".Lresident_startup_literal_19aa4:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_197b8\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19aa4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000030)) = (uint16_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000040)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_startup_edge_19ab4:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19ab4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_18f56\n");
    __builtin_unreachable();
}

/* Original0x19AB8..0x19ABE. */
REGION void tsl9_resident_startup_block_19ab8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a4, sp, 16\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0x19ABE..0x19AD2. */
REGION void tsl9_resident_startup_block_19abe(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    a2 = a2 + a5; LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000017)) = (uint8_t)a2; LIVE;
    PORT(".Lresident_startup_edge_19ace:\n.option push\n.option norvc\nbne a5,a3,.Lresident_startup_edge_19ace\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_startup_block_19abe\n");
    __builtin_unreachable();
}

/* Original0x19AD2..0x19AD6. */
REGION void tsl9_resident_startup_block_19ad2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)); LIVE;
    PORT(".Lresident_startup_edge_19ad4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_startup_edge_19ad4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_19ae0\n");
    __builtin_unreachable();
}

/* Original0x19AD6..0x19AE0. */
REGION void tsl9_resident_startup_block_19ad6(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)); LIVE;
    a5 = UINT32_C(0x00001000); LIVE;
    PORT(".Lresident_startup_edge_19adc:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_startup_edge_19adc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_startup_block_19ae2\n");
    __builtin_unreachable();
}

/* Original0x19AE0..0x19AE2. */
REGION void tsl9_resident_startup_block_19ae0(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19ae0:\n.option push\n.option rvc\nc.j .Lresident_startup_edge_19ae0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_block_19ae0\n");
    __builtin_unreachable();
}

/* Original0x19AE2..0x19AEE. */
REGION void tsl9_resident_startup_block_19ae2(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a4)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19AEE..0x19AF0. */
REGION void tsl9_resident_startup_block_19aee(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19aee:\n.option push\n.option rvc\nc.beqz a0,.Lresident_startup_edge_19aee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_startup_block_19af2\n");
    __builtin_unreachable();
}

/* Original0x19AF0..0x19AF2. */
REGION void tsl9_resident_startup_block_19af0(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19af0:\n.option push\n.option rvc\nc.j .Lresident_startup_edge_19af0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_block_19af0\n");
    __builtin_unreachable();
}

/* Original0x19AF2..0x19AFC. */
REGION void tsl9_resident_startup_block_19af2(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_startup_edge_19af8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19af8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_19106\n");
    __builtin_unreachable();
}

/* Original0x19AFC..0x19B16. */
REGION void tsl9_resident_startup_block_19afc(void)
{
    REGS;
    a5 = UINT32_C(0xe000e000); LIVE;
    a4 = UINT32_C(0x80000000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 88(sp)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000104)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000108)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 96\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19B16..0x19B30. */
REGION void tsl9_main_runtime_external_19b16(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 128(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lresident_startup_literal_19b26:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_1995c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19b26\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19B30..0x19B3A. */
REGION void tsl9_resident_startup_block_19b30(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, gp, 388\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 0(s0)\n.option pop\n");
    PORT(".Lresident_startup_edge_19b38:\n.option push\n.option rvc\nc.jal .Lresident_startup_edge_19b38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_startup_provider_19b56\n");
    __builtin_unreachable();
}

/* Original0x19B3A..0x19B56. */
REGION void tsl9_resident_startup_block_19b3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 0(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a2 = UINT32_C(0x0002f000); LIVE;
    a2 = a2 + UINT32_C(0xfffffe00); LIVE;
    a1 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19B56..0x19B6C. */
REGION void tsl9_resident_startup_provider_19b56(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x18000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    PORT(".Lresident_startup_edge_19b68:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b68\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19142\n");
    __builtin_unreachable();
}

/* Original0x19B6C..0x19B72. */
REGION void tsl9_resident_startup_block_19b6c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_19b6e:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_19076\n");
    __builtin_unreachable();
}

/* Original0x19B72..0x19B78. */
REGION void tsl9_resident_startup_block_19b72(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_19b74:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_190c6\n");
    __builtin_unreachable();
}

/* Original0x19B78..0x19B7E. */
REGION void tsl9_resident_startup_block_19b78(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_startup_edge_19b7a:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_1909e\n");
    __builtin_unreachable();
}

/* Original0x19B7E..0x19B86. */
REGION void tsl9_resident_startup_block_19b7e(void)
{
    REGS;
    a0 = UINT32_C(0x00000200); LIVE;
    PORT(".Lresident_startup_edge_19b82:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b82\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_190da\n");
    __builtin_unreachable();
}

/* Original0x19B86..0x19B8C. */
REGION void tsl9_resident_startup_block_19b86(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_19b88:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_190e6\n");
    __builtin_unreachable();
}

/* Original0x19B8C..0x19B90. */
REGION void tsl9_resident_startup_block_19b8c(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19b8c:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b8c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rtc_wait_19272\n");
    __builtin_unreachable();
}

/* Original0x19B90..0x19B94. */
REGION void tsl9_resident_startup_block_19b90(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19b90:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rtc_wait_19272\n");
    __builtin_unreachable();
}

/* Original0x19B94..0x19B9A. */
REGION void tsl9_resident_startup_block_19b94(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_startup_edge_19b96:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b96\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_19248\n");
    __builtin_unreachable();
}

/* Original0x19B9A..0x19B9E. */
REGION void tsl9_resident_startup_block_19b9a(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19b9a:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19b9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rtc_wait_19272\n");
    __builtin_unreachable();
}

/* Original0x19B9E..0x19BA4. */
REGION void tsl9_resident_startup_block_19b9e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_startup_edge_19ba0:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19ba0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_19220\n");
    __builtin_unreachable();
}

/* Original0x19BA4..0x19BA8. */
REGION void tsl9_resident_startup_block_19ba4(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19ba4:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19ba4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rtc_wait_19272\n");
    __builtin_unreachable();
}

/* Original0x19BA8..0x19BAC. */
REGION void tsl9_resident_startup_block_19ba8(void)
{
    REGS;
    PORT(".Lresident_startup_edge_19ba8:\n.option push\n.option norvc\njal ra,.Lresident_startup_edge_19ba8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_startup_provider_197b8\n");
    __builtin_unreachable();
}

/* Original0x19BAC..0x19BCE. */
REGION void tsl9_resident_startup_block_19bac(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x03e84000); LIVE;
    a5 = a5 + UINT32_C(0xfffffe80); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_startup_literal_19bba:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_resident_startup_provider_191c6\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_startup_literal_19bba\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000074)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19BCE..0x19BD4. */
REGION void tsl9_resident_startup_block_19bce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define VERSION_DATA extern "C" __attribute__((used,section(".rodata.tsl9_resident_version_1ab1c"),aligned(4)))
#else
#define VERSION_DATA __attribute__((used,section(".rodata.tsl9_resident_version_1ab1c"),aligned(4)))
#endif
VERSION_DATA const uint8_t tsl9_resident_version_1ab1c[21] = {0x43, 0x48, 0x33, 0x32, 0x56, 0x32, 0x30, 0x78, 0x5f, 0x42, 0x4c, 0x45, 0x5f, 0x4c, 0x49, 0x42, 0x5f, 0x56, 0x31, 0x2e, 0x33};
