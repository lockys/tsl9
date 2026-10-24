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

/* Ten complete original dependency functions:1052B/363i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x92BA..0x92D8. */
REGION void tsl9_callback_flow_external_92ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 76(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x1ffff\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, s0, 2028\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x92D8..0x92F2. */
REGION void tsl9_ota_runtime_block_92d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a1, s0, 2024\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 76(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s2, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x92F2..0x92F8. */
REGION void tsl9_ota_entry_92f2(void)
{
    REGS;
    a5 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lota_runtime_edge_92f4:\n.option push\n.option norvc\nbne a1,a5,.Lota_runtime_edge_92f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9330\n");
    __builtin_unreachable();
}

/* Original0x92F8..0x9304. */
REGION void tsl9_ota_runtime_block_92f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lota_runtime_edge_9302:\n.option push\n.option rvc\nc.jal .Lota_runtime_edge_9302\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_92ba\n");
    __builtin_unreachable();
}

/* Original0x9304..0x9308. */
REGION void tsl9_ota_runtime_block_9304(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x0000000e); LIVE;
    __builtin_unreachable();
}

/* Original0x9308..0x931C. */
REGION void tsl9_ota_runtime_block_9308(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a4, s0, a5\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nadd a4, sp, a5\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lota_runtime_edge_9318:\n.option push\n.option norvc\nbne a2,a4,.Lota_runtime_edge_9318\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_932c\n");
    __builtin_unreachable();
}

/* Original0x931C..0x9322. */
REGION void tsl9_ota_runtime_block_931c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_931e:\n.option push\n.option norvc\nbne a5,a3,.Lota_runtime_edge_931e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9308\n");
    __builtin_unreachable();
}

/* Original0x9322..0x9324. */
REGION void tsl9_ota_runtime_block_9322(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x9324..0x932C. */
REGION void tsl9_ota_runtime_block_9324(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x932C..0x9330. */
REGION void tsl9_ota_runtime_block_932c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_932e:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_932e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9324\n");
    __builtin_unreachable();
}

/* Original0x9330..0x9334. */
REGION void tsl9_ota_runtime_block_9330(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9C0A..0x9C22. */
REGION void tsl9_main_runtime_external_9c0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option norvc\nli s0, 136\n.option pop\n");
    PORT(".option push\n.option norvc\ncsrc 0x800, s0\n.option pop\n");
    PORT(".Lota_runtime_edge_9c1e:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9c1e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18e98\n");
    __builtin_unreachable();
}

/* Original0x9C22..0x9C2A. */
REGION void tsl9_ota_runtime_block_9c22(void)
{
    REGS;
    a0 = UINT32_C(0x00000031); LIVE;
    PORT(".Lota_runtime_edge_9c26:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9c26\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18e90\n");
    __builtin_unreachable();
}

/* Original0x9C2A..0x9C30. */
REGION void tsl9_ota_runtime_block_9c2a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lota_runtime_edge_9c2c:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9c2c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18ec4\n");
    __builtin_unreachable();
}

/* Original0x9C30..0x9C38. */
REGION void tsl9_ota_runtime_block_9c30(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lota_runtime_edge_9c34:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9c34\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18ef2\n");
    __builtin_unreachable();
}

/* Original0x9C38..0x9C3C. */
REGION void tsl9_ota_runtime_block_9c38(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9c38:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9c38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_flash_entry_18eb6\n");
    __builtin_unreachable();
}

/* Original0x9C3C..0x9C4A. */
REGION void tsl9_ota_runtime_block_9c3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\ncsrs 0x800, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9C4A..0x9C66. */
REGION void tsl9_ota_entry_9c4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000053); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Lota_runtime_edge_9c62:\n.option push\n.option norvc\nbeq a1,a5,.Lota_runtime_edge_9c62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9d80\n");
    __builtin_unreachable();
}

/* Original0x9C66..0x9C6A. */
REGION void tsl9_ota_runtime_block_9c66(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9c66:\n.option push\n.option norvc\nbltu a5,a1,.Lota_runtime_edge_9c66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c8c\n");
    __builtin_unreachable();
}

/* Original0x9C6A..0x9C72. */
REGION void tsl9_ota_runtime_block_9c6a(void)
{
    REGS;
    a5 = UINT32_C(0x00000045); LIVE;
    PORT(".Lota_runtime_edge_9c6e:\n.option push\n.option norvc\nbeq a1,a5,.Lota_runtime_edge_9c6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9df8\n");
    __builtin_unreachable();
}

/* Original0x9C72..0x9C7A. */
REGION void tsl9_ota_runtime_block_9c72(void)
{
    REGS;
    a5 = UINT32_C(0x00000052); LIVE;
    PORT(".Lota_runtime_edge_9c76:\n.option push\n.option norvc\nbeq a1,a5,.Lota_runtime_edge_9c76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9dc6\n");
    __builtin_unreachable();
}

/* Original0x9C7A..0x9C8C. */
REGION void tsl9_ota_runtime_block_9c7a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9C8C..0x9C94. */
REGION void tsl9_ota_runtime_block_9c8c(void)
{
    REGS;
    a5 = UINT32_C(0x00000055); LIVE;
    PORT(".Lota_runtime_edge_9c90:\n.option push\n.option norvc\nbeq a1,a5,.Lota_runtime_edge_9c90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9d2a\n");
    __builtin_unreachable();
}

/* Original0x9C94..0x9C9C. */
REGION void tsl9_ota_runtime_block_9c94(void)
{
    REGS;
    a5 = UINT32_C(0x00000057); LIVE;
    PORT(".Lota_runtime_edge_9c98:\n.option push\n.option norvc\nbne a1,a5,.Lota_runtime_edge_9c98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9C9C..0x9CA2. */
REGION void tsl9_ota_runtime_block_9c9c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)); LIVE;
    PORT(".Lota_runtime_edge_9ca0:\n.option push\n.option rvc\nc.beqz a5,.Lota_runtime_edge_9ca0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9CA2..0x9CAA. */
REGION void tsl9_ota_runtime_block_9ca2(void)
{
    REGS;
    a5 = UINT32_C(0x00000402); LIVE;
    PORT(".Lota_runtime_edge_9ca6:\n.option push\n.option norvc\nbne a3,a5,.Lota_runtime_edge_9ca6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9CAA..0x9CD2. */
REGION void tsl9_ota_runtime_block_9caa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s4, 0(a2)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s4, s4, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nor s4, s4, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0xa\n.option pop\n");
    a4 = UINT32_C(0xf7fff000); LIVE;
    a5 = UINT32_C(0x00007000); LIVE;
    PORT(".option push\n.option rvc\nadd a4, a4, s1\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffff00); LIVE;
    PORT(".Lota_runtime_edge_9cce:\n.option push\n.option norvc\nbltu a5,a4,.Lota_runtime_edge_9cce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9CD2..0x9CE0. */
REGION void tsl9_ota_runtime_block_9cd2(void)
{
    REGS;
    a1 = a2 + UINT32_C(0x00000002); LIVE;
    a5 = a1 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsub s3, a1, a5\n.option pop\n");
    PORT(".Lota_runtime_edge_9cde:\n.option push\n.option rvc\nc.beqz a5,.Lota_runtime_edge_9cde\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_9cee\n");
    __builtin_unreachable();
}

/* Original0x9CE0..0x9CEE. */
REGION void tsl9_ota_runtime_block_9ce0(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a2 = UINT32_C(0x00000400); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9CEE..0x9CF4. */
REGION void tsl9_ota_runtime_block_9cee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 1024\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9CF4..0x9D02. */
REGION void tsl9_ota_runtime_block_9cf4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a1, s3, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a0, s1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 256\n.option pop\n");
    PORT(".Lota_runtime_edge_9d00:\n.option push\n.option rvc\nc.jal .Lota_runtime_edge_9d00\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x9D02..0x9D06. */
REGION void tsl9_ota_runtime_block_9d02(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9d02:\n.option push\n.option norvc\nbne s0,s5,.Lota_runtime_edge_9d02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9cf4\n");
    __builtin_unreachable();
}

/* Original0x9D06..0x9D0C. */
REGION void tsl9_ota_runtime_block_9d06(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    a4 = UINT32_C(0x00000400); LIVE;
    __builtin_unreachable();
}

/* Original0x9D0C..0x9D1C. */
REGION void tsl9_ota_runtime_block_9d0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a3, a5, s1\n.option pop\n");
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nadd a3, s3, a5\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lota_runtime_edge_9d18:\n.option push\n.option norvc\nbne a2,a3,.Lota_runtime_edge_9d18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9e52\n");
    __builtin_unreachable();
}

/* Original0x9D1C..0x9D22. */
REGION void tsl9_ota_runtime_block_9d1c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".Lota_runtime_edge_9d1e:\n.option push\n.option norvc\nbne a5,a4,.Lota_runtime_edge_9d1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9d0c\n");
    __builtin_unreachable();
}

/* Original0x9D22..0x9D2A. */
REGION void tsl9_ota_runtime_block_9d22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s4\n.option pop\n");
    a1 = UINT32_C(0x00000057); LIVE;
    PORT(".Lota_runtime_edge_9d28:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9d28\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9df2\n");
    __builtin_unreachable();
}

/* Original0x9D2A..0x9D3E. */
REGION void tsl9_ota_runtime_block_9d2a(void)
{
    REGS;
    a1 = a3 + UINT32_C(0xffffffff); LIVE;
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a0 = a2 + UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)) = (uint8_t)0; LIVE;
    PORT(".Lota_runtime_edge_9d3a:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9d3a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_entry_92f2\n");
    __builtin_unreachable();
}

/* Original0x9D3E..0x9D40. */
REGION void tsl9_ota_runtime_block_9d3e(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9d3e:\n.option push\n.option rvc\nc.bnez a0,.Lota_runtime_edge_9d3e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9D40..0x9D4A. */
REGION void tsl9_ota_runtime_block_9d40(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_9d46:\n.option push\n.option norvc\nbne a4,a5,.Lota_runtime_edge_9d46\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9d72\n");
    __builtin_unreachable();
}

/* Original0x9D4A..0x9D5E. */
REGION void tsl9_ota_runtime_block_9d4a(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000000c8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_literal_9d52:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_8e18\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lota_runtime_literal_9d52\n.option pop\n");
    PORT(".Lota_runtime_edge_9d5a:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9d5a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x9D5E..0x9D72. */
REGION void tsl9_ota_runtime_block_9d5e(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000190); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_literal_9d66:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_9ee0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lota_runtime_literal_9d66\n.option pop\n");
    PORT(".Lota_runtime_edge_9d6e:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9d6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x9D72..0x9D78. */
REGION void tsl9_ota_runtime_block_9d72(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000055); LIVE;
    __builtin_unreachable();
}

/* Original0x9D78..0x9D7E. */
REGION void tsl9_ota_runtime_block_9d78(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lota_runtime_edge_9d7a:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9d7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13f66\n");
    __builtin_unreachable();
}

/* Original0x9D7E..0x9D80. */
REGION void tsl9_ota_runtime_block_9d7e(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9d7e:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9d7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9D80..0x9D9E. */
REGION void tsl9_ota_runtime_block_9d80(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a1 = a3 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a0 = a2 + UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nsb s1, 13(sp)\n.option pop\n");
    PORT(".Lota_runtime_edge_9d9a:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9d9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_entry_92f2\n");
    __builtin_unreachable();
}

/* Original0x9D9E..0x9DA0. */
REGION void tsl9_ota_runtime_block_9d9e(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9d9e:\n.option push\n.option rvc\nc.bnez a0,.Lota_runtime_edge_9d9e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_9dba\n");
    __builtin_unreachable();
}

/* Original0x9DA0..0x9DA6. */
REGION void tsl9_ota_runtime_block_9da0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s0)\n.option pop\n");
    PORT(".Lota_runtime_edge_9da4:\n.option push\n.option rvc\nc.bnez a5,.Lota_runtime_edge_9da4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_9dba\n");
    __builtin_unreachable();
}

/* Original0x9DA6..0x9DAA. */
REGION void tsl9_ota_runtime_block_9da6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s1, 169(gp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9DAA..0x9DB2. */
REGION void tsl9_ota_runtime_block_9daa(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x00000053); LIVE;
    __builtin_unreachable();
}

/* Original0x9DB2..0x9DB8. */
REGION void tsl9_ota_runtime_block_9db2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lota_runtime_edge_9db4:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9db4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x9DB8..0x9DBA. */
REGION void tsl9_ota_runtime_block_9db8(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9db8:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9db8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9DBA..0x9DC6. */
REGION void tsl9_ota_runtime_block_9dba(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    PORT(".Lota_runtime_edge_9dc4:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9dc4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9daa\n");
    __builtin_unreachable();
}

/* Original0x9DC6..0x9DCE. */
REGION void tsl9_ota_runtime_block_9dc6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)); LIVE;
    PORT(".Lota_runtime_edge_9dca:\n.option push\n.option norvc\nbeqz a5,.Lota_runtime_edge_9dca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9DCE..0x9DD4. */
REGION void tsl9_ota_runtime_block_9dce(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    PORT(".Lota_runtime_edge_9dd0:\n.option push\n.option norvc\nbne a3,a5,.Lota_runtime_edge_9dd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9DD4..0x9DDE. */
REGION void tsl9_ota_runtime_block_9dd4(void)
{
    REGS;
    a1 = UINT32_C(0x0000000e); LIVE;
    a0 = a2 + UINT32_C(0x00000002); LIVE;
    PORT(".Lota_runtime_edge_9dda:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9dda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_entry_92f2\n");
    __builtin_unreachable();
}

/* Original0x9DDE..0x9DE2. */
REGION void tsl9_ota_runtime_block_9dde(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9dde:\n.option push\n.option norvc\nbnez a0,.Lota_runtime_edge_9dde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9DE2..0x9DF2. */
REGION void tsl9_ota_runtime_block_9de2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a2, 1(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000052); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a2 = a2 | a5; LIVE;
    __builtin_unreachable();
}

/* Original0x9DF2..0x9DF6. */
REGION void tsl9_ota_runtime_block_9df2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lota_runtime_edge_9df4:\n.option push\n.option rvc\nc.jal .Lota_runtime_edge_9df4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_external_9b8e\n");
    __builtin_unreachable();
}

/* Original0x9DF6..0x9DF8. */
REGION void tsl9_ota_runtime_block_9df6(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9df6:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9df6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9DF8..0x9E00. */
REGION void tsl9_ota_runtime_block_9df8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)); LIVE;
    PORT(".Lota_runtime_edge_9dfc:\n.option push\n.option norvc\nbeqz a5,.Lota_runtime_edge_9dfc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9E00..0x9E06. */
REGION void tsl9_ota_runtime_block_9e00(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lota_runtime_edge_9e02:\n.option push\n.option norvc\nbne a3,a5,.Lota_runtime_edge_9e02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9E06..0x9E0E. */
REGION void tsl9_ota_runtime_block_9e06(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lota_runtime_edge_9e0a:\n.option push\n.option norvc\nbnez a5,.Lota_runtime_edge_9e0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9E0E..0x9E18. */
REGION void tsl9_ota_runtime_block_9e0e(void)
{
    REGS;
    a1 = UINT32_C(0x0000000e); LIVE;
    a0 = a2 + UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_9e14:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9e14\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_entry_92f2\n");
    __builtin_unreachable();
}

/* Original0x9E18..0x9E1C. */
REGION void tsl9_ota_runtime_block_9e18(void)
{
    REGS;
    PORT(".Lota_runtime_edge_9e18:\n.option push\n.option norvc\nbnez a0,.Lota_runtime_edge_9e18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_9c7a\n");
    __builtin_unreachable();
}

/* Original0x9E1C..0x9E34. */
REGION void tsl9_ota_runtime_block_9e1c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000000c8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_literal_9e24:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_8e18\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lota_runtime_literal_9e24\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)) = (uint8_t)0; LIVE;
    PORT(".Lota_runtime_edge_9e30:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9e30\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x9E34..0x9E48. */
REGION void tsl9_ota_runtime_block_9e34(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000190); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_literal_9e3c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_99e8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lota_runtime_literal_9e3c\n.option pop\n");
    PORT(".Lota_runtime_edge_9e44:\n.option push\n.option norvc\njal ra,.Lota_runtime_edge_9e44\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x9E48..0x9E52. */
REGION void tsl9_ota_runtime_block_9e48(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000045); LIVE;
    PORT(".Lota_runtime_edge_9e50:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9e50\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9db2\n");
    __builtin_unreachable();
}

/* Original0x9E52..0x9E5C. */
REGION void tsl9_ota_runtime_block_9e52(void)
{
    REGS;
    a2 = UINT32_C(0x000000ff); LIVE;
    a1 = UINT32_C(0x00000057); LIVE;
    PORT(".Lota_runtime_edge_9e5a:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_9e5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_9d78\n");
    __builtin_unreachable();
}

/* Original0x13E0E..0x13E1C. */
REGION void tsl9_incoming_external_13e0e(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff984); LIVE;
    PORT(".Lota_runtime_edge_13e18:\n.option push\n.option norvc\nbeq a1,a4,.Lota_runtime_edge_13e18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e3a\n");
    __builtin_unreachable();
}

/* Original0x13E1C..0x13E22. */
REGION void tsl9_ota_runtime_block_13e1c(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_13e1e:\n.option push\n.option norvc\nbeq a1,a4,.Lota_runtime_edge_13e1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e2e\n");
    __builtin_unreachable();
}

/* Original0x13E22..0x13E2A. */
REGION void tsl9_ota_runtime_block_13e22(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lota_runtime_edge_13e26:\n.option push\n.option norvc\nbne a0,a4,.Lota_runtime_edge_13e26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e62\n");
    __builtin_unreachable();
}

/* Original0x13E2A..0x13E2E. */
REGION void tsl9_ota_runtime_block_13e2a(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_edge_13e2c:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_13e2c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_13e8c\n");
    __builtin_unreachable();
}

/* Original0x13E2E..0x13E36. */
REGION void tsl9_ota_runtime_block_13e2e(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lota_runtime_edge_13e32:\n.option push\n.option norvc\nbne a0,a4,.Lota_runtime_edge_13e32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e62\n");
    __builtin_unreachable();
}

/* Original0x13E36..0x13E3A. */
REGION void tsl9_ota_runtime_block_13e36(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_edge_13e38:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_13e38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_13e72\n");
    __builtin_unreachable();
}

/* Original0x13E3A..0x13E46. */
REGION void tsl9_ota_runtime_block_13e3a(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    a4 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lota_runtime_edge_13e42:\n.option push\n.option norvc\nbeq a4,a3,.Lota_runtime_edge_13e42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e5e\n");
    __builtin_unreachable();
}

/* Original0x13E46..0x13E4E. */
REGION void tsl9_ota_runtime_block_13e46(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lota_runtime_edge_13e4a:\n.option push\n.option norvc\nbne a4,a3,.Lota_runtime_edge_13e4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e80\n");
    __builtin_unreachable();
}

/* Original0x13E4E..0x13E50. */
REGION void tsl9_ota_runtime_block_13e4e(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x13E50..0x13E58. */
REGION void tsl9_ota_runtime_block_13e50(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint16_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x13E58..0x13E5E. */
REGION void tsl9_ota_runtime_block_13e58(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    PORT(".Lota_runtime_edge_13e5c:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_13e5c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_13e7c\n");
    __builtin_unreachable();
}

/* Original0x13E5E..0x13E62. */
REGION void tsl9_ota_runtime_block_13e5e(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_runtime_edge_13e60:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_13e60\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_13e50\n");
    __builtin_unreachable();
}

/* Original0x13E62..0x13E68. */
REGION void tsl9_ota_runtime_block_13e62(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_13e64:\n.option push\n.option norvc\nbne a1,a4,.Lota_runtime_edge_13e64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e82\n");
    __builtin_unreachable();
}

/* Original0x13E68..0x13E70. */
REGION void tsl9_ota_runtime_block_13e68(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lota_runtime_edge_13e6c:\n.option push\n.option norvc\nbne a0,a4,.Lota_runtime_edge_13e6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e80\n");
    __builtin_unreachable();
}

/* Original0x13E70..0x13E72. */
REGION void tsl9_ota_runtime_block_13e70(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x13E72..0x13E7C. */
REGION void tsl9_ota_runtime_block_13e72(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x13E7C..0x13E80. */
REGION void tsl9_ota_runtime_block_13e7c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x13E80..0x13E82. */
REGION void tsl9_ota_runtime_block_13e80(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13E82..0x13E8A. */
REGION void tsl9_ota_runtime_block_13e82(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lota_runtime_edge_13e86:\n.option push\n.option norvc\nbne a0,a4,.Lota_runtime_edge_13e86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_13e80\n");
    __builtin_unreachable();
}

/* Original0x13E8A..0x13E8C. */
REGION void tsl9_ota_runtime_block_13e8a(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x13E8C..0x13E98. */
REGION void tsl9_ota_runtime_block_13e8c(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0xfffffffe); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint16_t)a4; LIVE;
    PORT(".Lota_runtime_edge_13e96:\n.option push\n.option rvc\nc.j .Lota_runtime_edge_13e96\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_runtime_block_13e58\n");
    __builtin_unreachable();
}

/* Original0x18E90..0x18E98. */
REGION void tsl9_ota_flash_entry_18e90(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18E98..0x18EB6. */
REGION void tsl9_ota_flash_entry_18e98(void)
{
    REGS;
    a3 = UINT32_C(0x45670000); LIVE;
    a5 = UINT32_C(0x40022000); LIVE;
    a3 = a3 + UINT32_C(0x00000123); LIVE;
    a4 = UINT32_C(0xcdef9000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    a4 = a4 + UINT32_C(0xfffff9ab); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18EB6..0x18EC4. */
REGION void tsl9_ota_flash_entry_18eb6(void)
{
    REGS;
    a4 = UINT32_C(0x40022000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0x00008000); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18EC4..0x18EE0. */
REGION void tsl9_ota_flash_entry_18ec4(void)
{
    REGS;
    a5 = UINT32_C(0x40022000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0x00020000); LIVE;
    a0 = a0 & UINT32_C(0xffffff00); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a0; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a4 = a4 | UINT32_C(0x00000040); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x18EE0..0x18EE6. */
REGION void tsl9_ota_runtime_block_18ee0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_18ee4:\n.option push\n.option rvc\nc.bnez a4,.Lota_runtime_edge_18ee4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_18ee0\n");
    __builtin_unreachable();
}

/* Original0x18EE6..0x18EF2. */
REGION void tsl9_ota_runtime_block_18ee6(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0xfffe0000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18EF2..0x18F02. */
REGION void tsl9_ota_flash_entry_18ef2(void)
{
    REGS;
    a4 = UINT32_C(0x40022000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0x00010000); LIVE;
    a0 = a0 & UINT32_C(0xffffff00); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x18F02..0x18F08. */
REGION void tsl9_ota_runtime_block_18f02(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_18f06:\n.option push\n.option rvc\nc.bnez a5,.Lota_runtime_edge_18f06\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_18f02\n");
    __builtin_unreachable();
}

/* Original0x18F08..0x18F0C. */
REGION void tsl9_ota_runtime_block_18f08(void)
{
    REGS;
    a4 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x18F0C..0x18F12. */
REGION void tsl9_ota_runtime_block_18f0c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lota_runtime_edge_18f10:\n.option push\n.option rvc\nc.bnez a5,.Lota_runtime_edge_18f10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_18f0c\n");
    __builtin_unreachable();
}

/* Original0x18F12..0x18F1A. */
REGION void tsl9_ota_runtime_block_18f12(void)
{
    REGS;
    a4 = UINT32_C(0x40022000); LIVE;
    a2 = UINT32_C(0x00000100); LIVE;
    __builtin_unreachable();
}

/* Original0x18F1A..0x18F2A. */
REGION void tsl9_ota_runtime_block_18f1a(void)
{
    REGS;
    a3 = a1 + a5; LIVE;
    PORT(".option push\n.option norvc\nlw a6, 0(a3)\n.option pop\n");
    a3 = a0 + a5; LIVE;
    PORT(".option push\n.option norvc\nsw a6, 0(a3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18F2A..0x18F30. */
REGION void tsl9_ota_runtime_block_18f2a(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a3 = a3 & UINT32_C(0x00000002); LIVE;
    PORT(".Lota_runtime_edge_18f2e:\n.option push\n.option rvc\nc.bnez a3,.Lota_runtime_edge_18f2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_18f2a\n");
    __builtin_unreachable();
}

/* Original0x18F30..0x18F36. */
REGION void tsl9_ota_runtime_block_18f30(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".Lota_runtime_edge_18f32:\n.option push\n.option norvc\nbne a5,a2,.Lota_runtime_edge_18f32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_runtime_block_18f1a\n");
    __builtin_unreachable();
}

/* Original0x18F36..0x18F44. */
REGION void tsl9_ota_runtime_block_18f36(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0x00200000); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x40022000); LIVE;
    __builtin_unreachable();
}

/* Original0x18F44..0x18F4A. */
REGION void tsl9_ota_runtime_block_18f44(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lota_runtime_edge_18f48:\n.option push\n.option rvc\nc.bnez a4,.Lota_runtime_edge_18f48\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_runtime_block_18f44\n");
    __builtin_unreachable();
}

/* Original0x18F4A..0x18F56. */
REGION void tsl9_ota_runtime_block_18f4a(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0xffff0000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
