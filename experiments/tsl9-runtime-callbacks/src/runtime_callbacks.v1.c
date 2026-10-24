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

/* Three complete original dependency functions:1072B/369i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x8614..0x8638. */
REGION void tsl9_main_runtime_external_8614(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    a5 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8634:\n.option push\n.option norvc\nbgez a5,.Lruntime_callbacks_edge_8634\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8686\n");
    __builtin_unreachable();
}

/* Original0x8638..0x8642. */
REGION void tsl9_runtime_callbacks_block_8638(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 108(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8642..0x8646. */
REGION void tsl9_runtime_callbacks_block_8642(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8644:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_callbacks_edge_8644\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8668\n");
    __builtin_unreachable();
}

/* Original0x8646..0x8652. */
REGION void tsl9_runtime_callbacks_block_8646(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x000000b0); LIVE;
    PORT(".Lruntime_callbacks_edge_864e:\n.option push\n.option norvc\nbne a4,a5,.Lruntime_callbacks_edge_864e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_865e\n");
    __builtin_unreachable();
}

/* Original0x8652..0x865E. */
REGION void tsl9_runtime_callbacks_block_8652(void)
{
    REGS;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 300(s2)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x865E..0x8668. */
REGION void tsl9_runtime_callbacks_block_865e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000068)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8668..0x866C. */
REGION void tsl9_runtime_callbacks_block_8668(void)
{
    REGS;
    a0 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nxor a0, a0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x866C..0x8686. */
REGION void tsl9_runtime_callbacks_block_866c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8686..0x868E. */
REGION void tsl9_runtime_callbacks_block_8686(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Lruntime_callbacks_edge_868a:\n.option push\n.option norvc\nbnez a5,.Lruntime_callbacks_edge_868a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8872\n");
    __builtin_unreachable();
}

/* Original0x868E..0x8698. */
REGION void tsl9_runtime_callbacks_block_868e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000094)); LIVE;
    PORT(".option push\n.option rvc\nmv s4, a0\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8694:\n.option push\n.option norvc\nbeq a5,a0,.Lruntime_callbacks_edge_8694\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8744\n");
    __builtin_unreachable();
}

/* Original0x8698..0x86A4. */
REGION void tsl9_runtime_callbacks_block_8698(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000098)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_86a0:\n.option push\n.option norvc\nbne a5,s4,.Lruntime_callbacks_edge_86a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x86A4..0x86B8. */
REGION void tsl9_runtime_callbacks_block_86a4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a4, s2, 0x2\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000094); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nlhu s5, 2(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a5, s0, 1\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_86b6:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_86b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_875e\n");
    __builtin_unreachable();
}

/* Original0x86B8..0x86E2. */
REGION void tsl9_runtime_callbacks_block_86b8(void)
{
    REGS;
    a5 = UINT32_C(0x00000426); LIVE;
    PORT(".option push\n.option norvc\nmul a5, s2, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, -1332\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s7, 0x40\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = original_gp + UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s3, 2(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s6, 4(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 316(s7)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x86E2..0x86E8. */
REGION void tsl9_runtime_callbacks_block_86e2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lruntime_callbacks_edge_86e4:\n.option push\n.option norvc\nbne a0,a5,.Lruntime_callbacks_edge_86e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_874e\n");
    __builtin_unreachable();
}

/* Original0x86E8..0x86FE. */
REGION void tsl9_runtime_callbacks_block_86e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s3, s3, s6\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s3, s3, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli s3, s3, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s6, s3, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai s6, s6, 0x10\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_86fa:\n.option push\n.option norvc\nblez s6,.Lruntime_callbacks_edge_86fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_874e\n");
    __builtin_unreachable();
}

/* Original0x86FE..0x8706. */
REGION void tsl9_runtime_callbacks_block_86fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 184(s7)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8706..0x871E. */
REGION void tsl9_runtime_callbacks_block_8706(void)
{
    REGS;
    a0 = a0 + UINT32_C(0xfffffffd); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    a5 = a5 + UINT32_C(0x000006ee); LIVE;
    PORT(".option push\n.option norvc\nslli a4, s2, 0x3\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".Lruntime_callbacks_edge_871a:\n.option push\n.option norvc\nblt s6,a0,.Lruntime_callbacks_edge_871a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8748\n");
    __builtin_unreachable();
}

/* Original0x871E..0x8722. */
REGION void tsl9_runtime_callbacks_block_871e(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint16_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x8722..0x873E. */
REGION void tsl9_runtime_callbacks_block_8722(void)
{
    REGS;
    a5 = UINT32_C(0x00000426); LIVE;
    PORT(".option push\n.option norvc\nmul s2, s2, a5\n.option pop\n");
    a5 = UINT32_C(0x0000000a); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 0(s1)\n.option pop\n");
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x873E..0x8744. */
REGION void tsl9_runtime_callbacks_block_873e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8742:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8742\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x8744..0x8748. */
REGION void tsl9_runtime_callbacks_block_8744(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8746:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8746\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_86a4\n");
    __builtin_unreachable();
}

/* Original0x8748..0x874E. */
REGION void tsl9_runtime_callbacks_block_8748(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh s3, 2(a5)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_874c:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_874c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8722\n");
    __builtin_unreachable();
}

/* Original0x874E..0x875E. */
REGION void tsl9_runtime_callbacks_block_874e(void)
{
    REGS;
    a5 = UINT32_C(0x00000426); LIVE;
    PORT(".option push\n.option norvc\nmul s2, s2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 2(s1)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_875c:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_875c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_873e\n");
    __builtin_unreachable();
}

/* Original0x875E..0x8764. */
REGION void tsl9_runtime_callbacks_block_875e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a5, s0, 2\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8762:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8762\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_884a\n");
    __builtin_unreachable();
}

/* Original0x8764..0x8780. */
REGION void tsl9_runtime_callbacks_block_8764(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s3, 1062\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s3, s2, s3\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s9, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s9, s9, -1504\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s8, s9\n.option pop\n");
    PORT(".option push\n.option norvc\nadd s6, s9, s3\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s6)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_877e:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_877e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8844\n");
    __builtin_unreachable();
}

/* Original0x8780..0x87A4. */
REGION void tsl9_runtime_callbacks_block_8780(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a5, s2, 0x3\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1652\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s7, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 296(s7)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a2, 2(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000001b); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87A4..0x87A8. */
REGION void tsl9_runtime_callbacks_block_87a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 4(s1)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_87a6:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_callbacks_edge_87a6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8834\n");
    __builtin_unreachable();
}

/* Original0x87A8..0x87BC. */
REGION void tsl9_runtime_callbacks_block_87a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 4(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 76(s7)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a2, 2(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, 6\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a1, a1, s3\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a1, a1, s9\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87BC..0x87C8. */
REGION void tsl9_runtime_callbacks_block_87bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 316(s7)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = original_gp + UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87C8..0x87CC. */
REGION void tsl9_runtime_callbacks_block_87c8(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lruntime_callbacks_edge_87ca:\n.option push\n.option rvc\nc.bnez a0,.Lruntime_callbacks_edge_87ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_87fc\n");
    __builtin_unreachable();
}

/* Original0x87CC..0x87DA. */
REGION void tsl9_runtime_callbacks_block_87cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 300(s3)\n.option pop\n");
    a1 = UINT32_C(0x0000001b); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87DA..0x87F2. */
REGION void tsl9_runtime_callbacks_block_87da(void)
{
    REGS;
    a5 = UINT32_C(0x00000426); LIVE;
    PORT(".option push\n.option norvc\nmul s2, s2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, s8\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 0(s2)\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 88(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87F2..0x87FA. */
REGION void tsl9_runtime_callbacks_block_87f2(void)
{
    REGS;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x87FA..0x87FC. */
REGION void tsl9_runtime_callbacks_block_87fa(void)
{
    REGS;
    PORT(".Lruntime_callbacks_edge_87fa:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_87fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_882e\n");
    __builtin_unreachable();
}

/* Original0x87FC..0x8814. */
REGION void tsl9_runtime_callbacks_block_87fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmv a5, gp\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000002a)); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 212(s7)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8814..0x8816. */
REGION void tsl9_runtime_callbacks_block_8814(void)
{
    REGS;
    PORT(".Lruntime_callbacks_edge_8814:\n.option push\n.option rvc\nc.bnez a0,.Lruntime_callbacks_edge_8814\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_87cc\n");
    __builtin_unreachable();
}

/* Original0x8816..0x882E. */
REGION void tsl9_runtime_callbacks_block_8816(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 4(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 2(s1)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 4(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 80(s7)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x882E..0x8834. */
REGION void tsl9_runtime_callbacks_block_882e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8832:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8832\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x8834..0x8844. */
REGION void tsl9_runtime_callbacks_block_8834(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s6)\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 0(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 88(s7)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8842:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8842\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_87f2\n");
    __builtin_unreachable();
}

/* Original0x8844..0x884A. */
REGION void tsl9_runtime_callbacks_block_8844(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 2(s6)\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8848:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8848\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_882e\n");
    __builtin_unreachable();
}

/* Original0x884A..0x8854. */
REGION void tsl9_runtime_callbacks_block_884a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a5, s0, 4\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_callbacks_edge_8850:\n.option push\n.option norvc\nbeqz a5,.Lruntime_callbacks_edge_8850\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x8854..0x886C. */
REGION void tsl9_runtime_callbacks_block_8854(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw a6, 424(a5)\n.option pop\n");
    a4 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\nmv a5, s4\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s5\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x886C..0x8872. */
REGION void tsl9_runtime_callbacks_block_886c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 4\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8870:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8870\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x8872..0x8886. */
REGION void tsl9_runtime_callbacks_block_8872(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001a4)); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x11\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000566); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8886..0x888C. */
REGION void tsl9_runtime_callbacks_block_8886(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 8\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_888a:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_888a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_866c\n");
    __builtin_unreachable();
}

/* Original0x8B6E..0x8B8A. */
REGION void tsl9_main_runtime_external_8b6e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a0; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000174)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 15\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000305); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8B8A..0x8B90. */
REGION void tsl9_runtime_callbacks_block_8b8a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8C82..0x8C96. */
REGION void tsl9_main_runtime_external_8c82(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8c94:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8c94\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8cb8\n");
    __builtin_unreachable();
}

/* Original0x8C96..0x8C9A. */
REGION void tsl9_runtime_callbacks_block_8c96(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_callbacks_edge_8c98:\n.option push\n.option rvc\nc.jal .Lruntime_callbacks_edge_8c98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8C9A..0x8CA8. */
REGION void tsl9_runtime_callbacks_block_8c9a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8CA8..0x8CAC. */
REGION void tsl9_runtime_callbacks_block_8ca8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8CAC..0x8CB8. */
REGION void tsl9_runtime_callbacks_block_8cac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8CB8..0x8CBE. */
REGION void tsl9_runtime_callbacks_block_8cb8(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    PORT(".Lruntime_callbacks_edge_8cbc:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8cbc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8d5c\n");
    __builtin_unreachable();
}

/* Original0x8CBE..0x8D32. */
REGION void tsl9_runtime_callbacks_block_8cbe(void)
{
    REGS;
    a5 = UINT32_C(0x10060000); LIVE;
    a5 = a5 + UINT32_C(0x00000102); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00005000); LIVE;
    a5 = a5 + UINT32_C(0x000004ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000045); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)) = (uint8_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008c)); LIVE;
    a4 = a5 + UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000b)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000090); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008c)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffffbf); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffffaa); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x53541000); LIVE;
    a5 = a5 + UINT32_C(0xfffff905); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00004000); LIVE;
    a5 = a5 + UINT32_C(0xfffff94c); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 372(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x0000001a); LIVE;
    a0 = UINT32_C(0x00000306); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8D32..0x8D3E. */
REGION void tsl9_runtime_callbacks_block_8d32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000028); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8D3E..0x8D4A. */
REGION void tsl9_runtime_callbacks_block_8d3e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000028); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8D4A..0x8D56. */
REGION void tsl9_runtime_callbacks_block_8d4a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 88(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8D56..0x8D5C. */
REGION void tsl9_runtime_callbacks_block_8d56(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8d5a:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8d5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}

/* Original0x8D5C..0x8D62. */
REGION void tsl9_runtime_callbacks_block_8d5c(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000004); LIVE;
    PORT(".Lruntime_callbacks_edge_8d60:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8d60\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8d88\n");
    __builtin_unreachable();
}

/* Original0x8D62..0x8D66. */
REGION void tsl9_runtime_callbacks_block_8d62(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lruntime_callbacks_edge_8d64:\n.option push\n.option rvc\nc.jal .Lruntime_callbacks_edge_8d64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8D66..0x8D76. */
REGION void tsl9_runtime_callbacks_block_8d66(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000092)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000320); LIVE;
    PORT(".Lruntime_callbacks_edge_8d74:\n.option push\n.option rvc\nc.beqz a4,.Lruntime_callbacks_edge_8d74\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8d7c\n");
    __builtin_unreachable();
}

/* Original0x8D76..0x8D7C. */
REGION void tsl9_runtime_callbacks_block_8d76(void)
{
    REGS;
    a2 = UINT32_C(0x00001000); LIVE;
    a2 = a2 + UINT32_C(0xfffffc80); LIVE;
    __builtin_unreachable();
}

/* Original0x8D7C..0x8D82. */
REGION void tsl9_runtime_callbacks_block_8d7c(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8D82..0x8D88. */
REGION void tsl9_runtime_callbacks_block_8d82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 4\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8d86:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8d86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}

/* Original0x8D88..0x8D8E. */
REGION void tsl9_runtime_callbacks_block_8d88(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Lruntime_callbacks_edge_8d8c:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8d8c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8da6\n");
    __builtin_unreachable();
}

/* Original0x8D8E..0x8D92. */
REGION void tsl9_runtime_callbacks_block_8d8e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_callbacks_edge_8d90:\n.option push\n.option rvc\nc.jal .Lruntime_callbacks_edge_8d90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8D92..0x8DA0. */
REGION void tsl9_runtime_callbacks_block_8d92(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8DA0..0x8DA6. */
REGION void tsl9_runtime_callbacks_block_8da0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 8\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8da4:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8da4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}

/* Original0x8DA6..0x8DAC. */
REGION void tsl9_runtime_callbacks_block_8da6(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000010); LIVE;
    PORT(".Lruntime_callbacks_edge_8daa:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_callbacks_edge_8daa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_callbacks_block_8df0\n");
    __builtin_unreachable();
}

/* Original0x8DAC..0x8DC4. */
REGION void tsl9_runtime_callbacks_block_8dac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 372(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x11\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000038); LIVE;
    a1 = UINT32_C(0x0000000d); LIVE;
    a0 = UINT32_C(0x00000306); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8DC4..0x8DD0. */
REGION void tsl9_runtime_callbacks_block_8dc4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s2)\n.option pop\n");
    a1 = UINT32_C(0x000000a0); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8DD0..0x8DDC. */
REGION void tsl9_runtime_callbacks_block_8dd0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s2)\n.option pop\n");
    a1 = UINT32_C(0x000000a0); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8DDC..0x8DEA. */
REGION void tsl9_runtime_callbacks_block_8ddc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 88(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8DEA..0x8DF0. */
REGION void tsl9_runtime_callbacks_block_8dea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 16\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8dee:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8dee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}

/* Original0x8DF0..0x8DFA. */
REGION void tsl9_runtime_callbacks_block_8df0(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000020); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_callbacks_edge_8df6:\n.option push\n.option norvc\nbeqz a5,.Lruntime_callbacks_edge_8df6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}

/* Original0x8DFA..0x8E06. */
REGION void tsl9_runtime_callbacks_block_8dfa(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lruntime_callbacks_edge_8e02:\n.option push\n.option norvc\nbeq a4,a5,.Lruntime_callbacks_edge_8e02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8e0e\n");
    __builtin_unreachable();
}

/* Original0x8E06..0x8E0E. */
REGION void tsl9_runtime_callbacks_block_8e06(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    PORT(".Lruntime_callbacks_edge_8e0a:\n.option push\n.option norvc\nbne a4,a5,.Lruntime_callbacks_edge_8e0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_callbacks_block_8e12\n");
    __builtin_unreachable();
}

/* Original0x8E0E..0x8E12. */
REGION void tsl9_runtime_callbacks_block_8e0e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lruntime_callbacks_edge_8e10:\n.option push\n.option rvc\nc.jal .Lruntime_callbacks_edge_8e10\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8E12..0x8E18. */
REGION void tsl9_runtime_callbacks_block_8e12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 32\n.option pop\n");
    PORT(".Lruntime_callbacks_edge_8e16:\n.option push\n.option rvc\nc.j .Lruntime_callbacks_edge_8e16\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_runtime_callbacks_block_8cac\n");
    __builtin_unreachable();
}
