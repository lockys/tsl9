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

/* Three complete original dependency functions:776B/262i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x85C8..0x85D0. */
REGION void tsl9_incoming_entry_85c8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    PORT(".Lincoming_edge_85cc:\n.option push\n.option norvc\nbeq a5,a0,.Lincoming_edge_85cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_860e\n");
    __builtin_unreachable();
}

/* Original0x85D0..0x85D8. */
REGION void tsl9_incoming_block_85d0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    PORT(".Lincoming_edge_85d4:\n.option push\n.option norvc\nbne a5,a0,.Lincoming_edge_85d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8612\n");
    __builtin_unreachable();
}

/* Original0x85D8..0x85DA. */
REGION void tsl9_incoming_block_85d8(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x85DA..0x85E6. */
REGION void tsl9_incoming_block_85da(void)
{
    REGS;
    a1 = a1 + UINT32_C(0xfffffff4); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a4 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lincoming_edge_85e2:\n.option push\n.option norvc\nbltu a4,a1,.Lincoming_edge_85e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_85f0\n");
    __builtin_unreachable();
}

/* Original0x85E6..0x85E8. */
REGION void tsl9_incoming_block_85e6(void)
{
    REGS;
    PORT(".Lincoming_edge_85e6:\n.option push\n.option rvc\nc.bnez a2,.Lincoming_edge_85e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_incoming_block_85f0\n");
    __builtin_unreachable();
}

/* Original0x85E8..0x85F0. */
REGION void tsl9_incoming_block_85e8(void)
{
    REGS;
    a4 = UINT32_C(0x000000c8); LIVE;
    PORT(".Lincoming_edge_85ec:\n.option push\n.option norvc\nbeq a3,a4,.Lincoming_edge_85ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8612\n");
    __builtin_unreachable();
}

/* Original0x85F0..0x860E. */
REGION void tsl9_incoming_block_85f0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000094); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 88(a4)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00001000); LIVE;
    a2 = a2 + UINT32_C(0x000002c0); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x860E..0x8612. */
REGION void tsl9_incoming_block_860e(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lincoming_edge_8610:\n.option push\n.option rvc\nc.j .Lincoming_edge_8610\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_85da\n");
    __builtin_unreachable();
}

/* Original0x8612..0x8614. */
REGION void tsl9_incoming_block_8612(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x888C..0x8898. */
REGION void tsl9_incoming_entry_888c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a6, 8(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a6, a6, 32\n.option pop\n");
    PORT(".Lincoming_edge_8894:\n.option push\n.option norvc\nbnez a6,.Lincoming_edge_8894\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a52\n");
    __builtin_unreachable();
}

/* Original0x8898..0x88A2. */
REGION void tsl9_incoming_block_8898(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a7, 0(a1)\n.option pop\n");
    PORT(".option push\n.option rvc\nli a6, 2\n.option pop\n");
    PORT(".Lincoming_edge_889e:\n.option push\n.option norvc\nbeq a7,a6,.Lincoming_edge_889e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_88a6\n");
    __builtin_unreachable();
}

/* Original0x88A2..0x88A6. */
REGION void tsl9_incoming_block_88a2(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x88A6..0x88BE. */
REGION void tsl9_incoming_block_88a6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a6, 4(a1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui a7, 0x3\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a7, a7, -1790\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a6, 0(a6)\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    PORT(".Lincoming_edge_88ba:\n.option push\n.option norvc\nbne a6,a7,.Lincoming_edge_88ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_88ca\n");
    __builtin_unreachable();
}

/* Original0x88BE..0x88CA. */
REGION void tsl9_incoming_block_88be(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 324(a5)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x88CA..0x88D8. */
REGION void tsl9_incoming_block_88ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmv a4, gp\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000024)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lincoming_edge_88d4:\n.option push\n.option norvc\nbne a6,a4,.Lincoming_edge_88d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_88a2\n");
    __builtin_unreachable();
}

/* Original0x88D8..0x88E4. */
REGION void tsl9_incoming_block_88d8(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x0000000a)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000002a)); LIVE;
    PORT(".Lincoming_edge_88e0:\n.option push\n.option norvc\nbne a4,a5,.Lincoming_edge_88e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_88a2\n");
    __builtin_unreachable();
}

/* Original0x88E4..0x8908. */
REGION void tsl9_incoming_block_88e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a3\n.option pop\n");
    PORT(".Lincoming_edge_8906:\n.option push\n.option rvc\nc.jal .Lincoming_edge_8906\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0x8908..0x891A. */
REGION void tsl9_incoming_block_8908(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x000000a0); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x0000012b); LIVE;
    a5 = a0 - a5; LIVE;
    PORT(".Lincoming_edge_8916:\n.option push\n.option norvc\nbleu a5,a4,.Lincoming_edge_8916\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_891e\n");
    __builtin_unreachable();
}

/* Original0x891A..0x891E. */
REGION void tsl9_incoming_block_891a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x891E..0x8938. */
REGION void tsl9_incoming_block_891e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a0)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s5, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nli s6, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s7, 3\n.option pop\n");
    PORT(".option push\n.option rvc\nli s8, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nli s9, 5\n.option pop\n");
    PORT(".option push\n.option rvc\nli s10, 6\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, gp, 165\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s11, gp, 142\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8938..0x8942. */
REGION void tsl9_incoming_block_8938(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a5, s0, 0x10\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lincoming_edge_893e:\n.option push\n.option norvc\nbltu a5,s2,.Lincoming_edge_893e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8962\n");
    __builtin_unreachable();
}

/* Original0x8942..0x8962. */
REGION void tsl9_incoming_block_8942(void)
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
    PORT(".option push\n.option rvc\nlw s11, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8962..0x8970. */
REGION void tsl9_incoming_block_8962(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a5, s4, s0\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lincoming_edge_896e:\n.option push\n.option rvc\nc.bnez a4,.Lincoming_edge_896e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_incoming_block_8982\n");
    __builtin_unreachable();
}

/* Original0x8970..0x8978. */
REGION void tsl9_incoming_block_8970(void)
{
    REGS;
    a4 = UINT32_C(0x00000055); LIVE;
    PORT(".Lincoming_edge_8974:\n.option push\n.option norvc\nbne a5,a4,.Lincoming_edge_8974\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a4c\n");
    __builtin_unreachable();
}

/* Original0x8978..0x897E. */
REGION void tsl9_incoming_block_8978(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x897E..0x8982. */
REGION void tsl9_incoming_block_897e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lincoming_edge_8980:\n.option push\n.option rvc\nc.j .Lincoming_edge_8980\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_8938\n");
    __builtin_unreachable();
}

/* Original0x8982..0x8986. */
REGION void tsl9_incoming_block_8982(void)
{
    REGS;
    PORT(".Lincoming_edge_8982:\n.option push\n.option norvc\nbne a4,s5,.Lincoming_edge_8982\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_899a\n");
    __builtin_unreachable();
}

/* Original0x8986..0x898E. */
REGION void tsl9_incoming_block_8986(void)
{
    REGS;
    a4 = UINT32_C(0x0000007f); LIVE;
    PORT(".Lincoming_edge_898a:\n.option push\n.option norvc\nbne a5,a4,.Lincoming_edge_898a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a4c\n");
    __builtin_unreachable();
}

/* Original0x898E..0x899A. */
REGION void tsl9_incoming_block_898e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a5)) = (uint8_t)0; LIVE;
    PORT(".Lincoming_edge_8998:\n.option push\n.option rvc\nc.j .Lincoming_edge_8998\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_897e\n");
    __builtin_unreachable();
}

/* Original0x899A..0x899E. */
REGION void tsl9_incoming_block_899a(void)
{
    REGS;
    PORT(".Lincoming_edge_899a:\n.option push\n.option norvc\nbne a4,s6,.Lincoming_edge_899a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_89b4\n");
    __builtin_unreachable();
}

/* Original0x899E..0x89A8. */
REGION void tsl9_incoming_block_899e(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a4)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x89A8..0x89B4. */
REGION void tsl9_incoming_block_89a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s1)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a5)) = (uint8_t)a5; LIVE;
    PORT(".Lincoming_edge_89b2:\n.option push\n.option rvc\nc.j .Lincoming_edge_89b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_897e\n");
    __builtin_unreachable();
}

/* Original0x89B4..0x89B8. */
REGION void tsl9_incoming_block_89b4(void)
{
    REGS;
    PORT(".Lincoming_edge_89b4:\n.option push\n.option norvc\nbne a4,s7,.Lincoming_edge_89b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_89c8\n");
    __builtin_unreachable();
}

/* Original0x89B8..0x89C8. */
REGION void tsl9_incoming_block_89b8(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)a4; LIVE;
    a4 = a5 << UINT32_C(0x00000008); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008e)) = (uint16_t)a4; LIVE;
    PORT(".Lincoming_edge_89c6:\n.option push\n.option rvc\nc.j .Lincoming_edge_89c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_89a8\n");
    __builtin_unreachable();
}

/* Original0x89C8..0x89CC. */
REGION void tsl9_incoming_block_89c8(void)
{
    REGS;
    PORT(".Lincoming_edge_89c8:\n.option push\n.option norvc\nbne a4,s8,.Lincoming_edge_89c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_89f6\n");
    __builtin_unreachable();
}

/* Original0x89CC..0x89DC. */
REGION void tsl9_incoming_block_89cc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008a)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option norvc\nlhu a4, 0(s11)\n.option pop\n");
    a4 = a4 | a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008e)) = (uint16_t)a4; LIVE;
    PORT(".Lincoming_edge_89da:\n.option push\n.option rvc\nc.bnez a4,.Lincoming_edge_89da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_incoming_block_89e0\n");
    __builtin_unreachable();
}

/* Original0x89DC..0x89E0. */
REGION void tsl9_incoming_block_89dc(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lincoming_edge_89de:\n.option push\n.option rvc\nc.j .Lincoming_edge_89de\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_89ea\n");
    __builtin_unreachable();
}

/* Original0x89E0..0x89E8. */
REGION void tsl9_incoming_block_89e0(void)
{
    REGS;
    a3 = UINT32_C(0x00000410); LIVE;
    PORT(".Lincoming_edge_89e4:\n.option push\n.option norvc\nbltu a3,a4,.Lincoming_edge_89e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_89f0\n");
    __builtin_unreachable();
}

/* Original0x89E8..0x89EA. */
REGION void tsl9_incoming_block_89e8(void)
{
    REGS;
    a4 = UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0x89EA..0x89F0. */
REGION void tsl9_incoming_block_89ea(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)a4; LIVE;
    PORT(".Lincoming_edge_89ee:\n.option push\n.option rvc\nc.j .Lincoming_edge_89ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_89a8\n");
    __builtin_unreachable();
}

/* Original0x89F0..0x89F6. */
REGION void tsl9_incoming_block_89f0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)0; LIVE;
    PORT(".Lincoming_edge_89f4:\n.option push\n.option rvc\nc.j .Lincoming_edge_89f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_89a8\n");
    __builtin_unreachable();
}

/* Original0x89F6..0x89FA. */
REGION void tsl9_incoming_block_89f6(void)
{
    REGS;
    PORT(".Lincoming_edge_89f6:\n.option push\n.option norvc\nbne a4,s9,.Lincoming_edge_89f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a2a\n");
    __builtin_unreachable();
}

/* Original0x89FA..0x8A06. */
REGION void tsl9_incoming_block_89fa(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a2 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008a)); LIVE;
    a4 = UINT32_C(0x0000040f); LIVE;
    PORT(".Lincoming_edge_8a02:\n.option push\n.option norvc\nbltu a4,a2,.Lincoming_edge_8a02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a4c\n");
    __builtin_unreachable();
}

/* Original0x8A06..0x8A28. */
REGION void tsl9_incoming_block_8a06(void)
{
    REGS;
    a4 = a2 + UINT32_C(0x00000001); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008a)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x20003\n.option pop\n");
    a3 = a3 + UINT32_C(0xffffffc6); LIVE;
    a3 = a3 + a2; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008e)); LIVE;
    PORT(".Lincoming_edge_8a24:\n.option push\n.option norvc\nbltu a4,a3,.Lincoming_edge_8a24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_89a8\n");
    __builtin_unreachable();
}

/* Original0x8A28..0x8A2A. */
REGION void tsl9_incoming_block_8a28(void)
{
    REGS;
    PORT(".Lincoming_edge_8a28:\n.option push\n.option rvc\nc.j .Lincoming_edge_8a28\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_89dc\n");
    __builtin_unreachable();
}

/* Original0x8A2A..0x8A2E. */
REGION void tsl9_incoming_block_8a2a(void)
{
    REGS;
    PORT(".Lincoming_edge_8a2a:\n.option push\n.option norvc\nbne a4,s10,.Lincoming_edge_8a2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a4c\n");
    __builtin_unreachable();
}

/* Original0x8A2E..0x8A36. */
REGION void tsl9_incoming_block_8a2e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a5)); LIVE;
    PORT(".Lincoming_edge_8a32:\n.option push\n.option norvc\nbne a4,a5,.Lincoming_edge_8a32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8a4c\n");
    __builtin_unreachable();
}

/* Original0x8A36..0x8A4C. */
REGION void tsl9_incoming_block_8a36(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000008e)); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x20003\n.option pop\n");
    a2 = a2 + UINT32_C(0xffffff9e); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a4)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".Lincoming_edge_8a48:\n.option push\n.option norvc\njal ra,.Lincoming_edge_8a48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_incoming_external_14056\n");
    __builtin_unreachable();
}

/* Original0x8A4C..0x8A52. */
REGION void tsl9_incoming_block_8a4c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009c)) = (uint8_t)0; LIVE;
    PORT(".Lincoming_edge_8a50:\n.option push\n.option rvc\nc.j .Lincoming_edge_8a50\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_897e\n");
    __builtin_unreachable();
}

/* Original0x8A52..0x8A56. */
REGION void tsl9_incoming_block_8a52(void)
{
    REGS;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8B90..0x8B96. */
REGION void tsl9_incoming_entry_8b90(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lincoming_edge_8b92:\n.option push\n.option norvc\nbltu a0,a5,.Lincoming_edge_8b92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c80\n");
    __builtin_unreachable();
}

/* Original0x8B96..0x8BA6. */
REGION void tsl9_incoming_block_8b96(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lincoming_edge_8ba2:\n.option push\n.option norvc\nbleu a0,a5,.Lincoming_edge_8ba2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c3e\n");
    __builtin_unreachable();
}

/* Original0x8BA6..0x8BAC. */
REGION void tsl9_incoming_block_8ba6(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lincoming_edge_8ba8:\n.option push\n.option norvc\nbne a0,a5,.Lincoming_edge_8ba8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8BAC..0x8BB6. */
REGION void tsl9_incoming_block_8bac(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000002)); LIVE;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lincoming_edge_8bb2:\n.option push\n.option norvc\nbne a4,a5,.Lincoming_edge_8bb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8BB6..0x8BC6. */
REGION void tsl9_incoming_block_8bb6(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x0000000a)); LIVE;
    PORT(".Lincoming_edge_8bc2:\n.option push\n.option norvc\nbeq a4,a5,.Lincoming_edge_8bc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8be2\n");
    __builtin_unreachable();
}

/* Original0x8BC6..0x8BCE. */
REGION void tsl9_incoming_block_8bc6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    PORT(".Lincoming_edge_8bca:\n.option push\n.option norvc\nbeq a4,a5,.Lincoming_edge_8bca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c3a\n");
    __builtin_unreachable();
}

/* Original0x8BCE..0x8BD8. */
REGION void tsl9_incoming_block_8bce(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000017c)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8BD8..0x8BE2. */
REGION void tsl9_incoming_block_8bd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8BE2..0x8BE4. */
REGION void tsl9_incoming_block_8be2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8BE4..0x8C00. */
REGION void tsl9_incoming_block_8be4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a5, s0, 0x2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, gp, 148\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a0, 2(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 80(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 0(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8C00..0x8C18. */
REGION void tsl9_incoming_block_8c00(void)
{
    REGS;
    a5 = UINT32_C(0x000000f7); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a2, 0(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 216(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a1, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8C18..0x8C26. */
REGION void tsl9_incoming_block_8c18(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lincoming_edge_8c22:\n.option push\n.option norvc\nbeq a4,a5,.Lincoming_edge_8c22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c32\n");
    __builtin_unreachable();
}

/* Original0x8C26..0x8C30. */
REGION void tsl9_incoming_block_8c26(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lincoming_edge_8c2c:\n.option push\n.option norvc\nbeq a4,a5,.Lincoming_edge_8c2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c32\n");
    __builtin_unreachable();
}

/* Original0x8C30..0x8C32. */
REGION void tsl9_incoming_block_8c30(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x8C32..0x8C38. */
REGION void tsl9_incoming_block_8c32(void)
{
    REGS;
    a0 = (uint32_t)(a0 < UINT32_C(0x00000002)); LIVE;
    PORT(".Lincoming_edge_8c36:\n.option push\n.option rvc\nc.jal .Lincoming_edge_8c36\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8C38..0x8C3A. */
REGION void tsl9_incoming_block_8c38(void)
{
    REGS;
    PORT(".Lincoming_edge_8c38:\n.option push\n.option rvc\nc.j .Lincoming_edge_8c38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8C3A..0x8C3E. */
REGION void tsl9_incoming_block_8c3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".Lincoming_edge_8c3c:\n.option push\n.option rvc\nc.j .Lincoming_edge_8c3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_8be4\n");
    __builtin_unreachable();
}

/* Original0x8C3E..0x8C48. */
REGION void tsl9_incoming_block_8c3e(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000002)); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lincoming_edge_8c44:\n.option push\n.option norvc\nbne a4,a5,.Lincoming_edge_8c44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8C48..0x8C54. */
REGION void tsl9_incoming_block_8c48(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000096)); LIVE;
    PORT(".Lincoming_edge_8c50:\n.option push\n.option norvc\nbeq a4,a5,.Lincoming_edge_8c50\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8c7c\n");
    __builtin_unreachable();
}

/* Original0x8C54..0x8C5C. */
REGION void tsl9_incoming_block_8c54(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009a)); LIVE;
    PORT(".Lincoming_edge_8c58:\n.option push\n.option norvc\nbne a4,a5,.Lincoming_edge_8c58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8C5C..0x8C5E. */
REGION void tsl9_incoming_block_8c5c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x8C5E..0x8C70. */
REGION void tsl9_incoming_block_8c5e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000094); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0xfffffffe); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint16_t)a4; LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lincoming_edge_8c6e:\n.option push\n.option rvc\nc.jal .Lincoming_edge_8c6e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8C70..0x8C7A. */
REGION void tsl9_incoming_block_8c70(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a0, 4(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lincoming_edge_8c76:\n.option push\n.option norvc\njal ra,.Lincoming_edge_8c76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_incoming_external_13e0e\n");
    __builtin_unreachable();
}

/* Original0x8C7A..0x8C7C. */
REGION void tsl9_incoming_block_8c7a(void)
{
    REGS;
    PORT(".Lincoming_edge_8c7a:\n.option push\n.option rvc\nc.j .Lincoming_edge_8c7a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_8bd8\n");
    __builtin_unreachable();
}

/* Original0x8C7C..0x8C80. */
REGION void tsl9_incoming_block_8c7c(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lincoming_edge_8c7e:\n.option push\n.option rvc\nc.j .Lincoming_edge_8c7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_incoming_block_8c5e\n");
    __builtin_unreachable();
}

/* Original0x8C80..0x8C82. */
REGION void tsl9_incoming_block_8c80(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

typedef void (*tsl9_incoming_pointer)(void);

ENTRY __attribute__((used,aligned(4))) tsl9_incoming_pointer const tsl9_incoming_table_prefix_19de0[3] = { tsl9_incoming_entry_8b90,0,tsl9_incoming_entry_85c8 };

ENTRY __attribute__((used,aligned(4))) tsl9_incoming_pointer const tsl9_incoming_table_prefix_19dfc[3] = { 0,tsl9_incoming_entry_888c,0 };

ENTRY __attribute__((used,aligned(1))) const uint8_t tsl9_incoming_payload_prefix_19dec[13] = { 0x02,0x01,0x06,0x03,0x02,0xf0,0xff,0x05,0x09,0x54,0x53,0x4c,0x39 };

ENTRY __attribute__((used,aligned(1))) const uint8_t tsl9_incoming_lookup_1ab34[3] = { 0x7f,0x00,0x81 };
