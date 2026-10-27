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

/* Two complete conditional SDK handler/comparison bodies:592B/211i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x585C8..0x585DC. */
REGION void tsl9_candidate_external_flash_585c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000007c)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_585da:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_comparison_edge_585da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_585f0\n");
    __builtin_unreachable();
}

/* Original0x585DC..0x585E2. */
REGION void tsl9_resident_record_comparison_block_585dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 132(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_585e0:\n.option push\n.option rvc\nc.bnez a0,.Lresident_record_comparison_edge_585e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58684\n");
    __builtin_unreachable();
}

/* Original0x585E2..0x585EA. */
REGION void tsl9_resident_record_comparison_block_585e2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3458\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_comparison_edge_585e6:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_comparison_edge_585e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58720\n");
    __builtin_unreachable();
}

/* Original0x585EA..0x585F0. */
REGION void tsl9_resident_record_comparison_block_585ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 116(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a1, 120(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_585ee:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_585ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_586f2\n");
    __builtin_unreachable();
}

/* Original0x585F0..0x585F6. */
REGION void tsl9_resident_record_comparison_block_585f0(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000084)); LIVE;
    PORT(".Lresident_record_comparison_edge_585f4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_comparison_edge_585f4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_5863c\n");
    __builtin_unreachable();
}

/* Original0x585F6..0x585FA. */
REGION void tsl9_resident_record_comparison_block_585f6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x253c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_585f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_585f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_5863c\n");
    __builtin_unreachable();
}

/* Original0x585FA..0x58600. */
REGION void tsl9_resident_record_comparison_block_585fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 125(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_585fe:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_585fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_5867e\n");
    __builtin_unreachable();
}

/* Original0x58600..0x58610. */
REGION void tsl9_resident_record_comparison_block_58600(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 131(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_record_comparison_edge_5860c:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_comparison_edge_5860c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_5867e\n");
    __builtin_unreachable();
}

/* Original0x58610..0x5861C. */
REGION void tsl9_resident_record_comparison_block_58610(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, s0, 126\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000001a); LIVE;
    PORT(".Lresident_record_comparison_edge_58618:\n.option push\n.option norvc\njal ra,.Lresident_record_comparison_edge_58618\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e4b0\n");
    __builtin_unreachable();
}

/* Original0x5861C..0x58626. */
REGION void tsl9_resident_record_comparison_block_5861c(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 132(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58622:\n.option push\n.option norvc\nbne a0,a4,.Lresident_record_comparison_edge_58622\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_5865c\n");
    __builtin_unreachable();
}

/* Original0x58626..0x5863C. */
REGION void tsl9_resident_record_comparison_block_58626(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 124(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a5 + UINT32_C(0x0000000c); LIVE;
    PORT(".Lresident_record_comparison_literal_58634:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_58634\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5863C..0x58646. */
REGION void tsl9_resident_record_comparison_block_5863c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 124(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_comparison_edge_58642:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_record_comparison_edge_58642\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_585dc\n");
    __builtin_unreachable();
}

/* Original0x58646..0x58658. */
REGION void tsl9_resident_record_comparison_block_58646(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 126\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 102\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_58650:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_58650\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58658..0x5865A. */
REGION void tsl9_resident_record_comparison_block_58658(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_58658:\n.option push\n.option rvc\nc.bnez a0,.Lresident_record_comparison_edge_58658\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_585dc\n");
    __builtin_unreachable();
}

/* Original0x5865A..0x5865C. */
REGION void tsl9_resident_record_comparison_block_5865a(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_5865a:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_5865a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x5865C..0x58660. */
REGION void tsl9_resident_record_comparison_block_5865c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5865e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_comparison_edge_5865e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58672\n");
    __builtin_unreachable();
}

/* Original0x58660..0x58662. */
REGION void tsl9_resident_record_comparison_block_58660(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58662..0x58672. */
REGION void tsl9_resident_record_comparison_block_58662(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58672..0x5867C. */
REGION void tsl9_resident_record_comparison_block_58672(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_record_comparison_edge_5867a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_5867a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_5863c\n");
    __builtin_unreachable();
}

/* Original0x5867C..0x5867E. */
REGION void tsl9_resident_record_comparison_block_5867c(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_5867c:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_5867c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x5867E..0x58682. */
REGION void tsl9_resident_record_comparison_block_5867e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x311c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58680:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_comparison_edge_58680\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_5863c\n");
    __builtin_unreachable();
}

/* Original0x58682..0x58684. */
REGION void tsl9_resident_record_comparison_block_58682(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_58682:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58682\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x58684..0x58688. */
REGION void tsl9_resident_record_comparison_block_58684(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 18(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x293c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58686:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_58686\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_585e2\n");
    __builtin_unreachable();
}

/* Original0x58688..0x5868E. */
REGION void tsl9_resident_record_comparison_block_58688(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 117(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5868c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_5868c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58718\n");
    __builtin_unreachable();
}

/* Original0x5868E..0x5869E. */
REGION void tsl9_resident_record_comparison_block_5868e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 123(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_record_comparison_edge_5869a:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_comparison_edge_5869a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58718\n");
    __builtin_unreachable();
}

/* Original0x5869E..0x586AC. */
REGION void tsl9_resident_record_comparison_block_5869e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s3, s0, 118\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000002a); LIVE;
    PORT(".Lresident_record_comparison_edge_586a8:\n.option push\n.option norvc\njal ra,.Lresident_record_comparison_edge_586a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e4b0\n");
    __builtin_unreachable();
}

/* Original0x586AC..0x586BA. */
REGION void tsl9_resident_record_comparison_block_586ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 132(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_586b6:\n.option push\n.option norvc\nbne s2,a5,.Lresident_record_comparison_edge_586b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58706\n");
    __builtin_unreachable();
}

/* Original0x586BA..0x586C8. */
REGION void tsl9_resident_record_comparison_block_586ba(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_record_comparison_literal_586c0:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_586c0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x586C8..0x586D2. */
REGION void tsl9_resident_record_comparison_block_586c8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_record_comparison_edge_586d0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_586d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_585e2\n");
    __builtin_unreachable();
}

/* Original0x586D2..0x586DE. */
REGION void tsl9_resident_record_comparison_block_586d2(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x345c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_586da:\n.option push\n.option norvc\nbne a5,s2,.Lresident_record_comparison_edge_586da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58662\n");
    __builtin_unreachable();
}

/* Original0x586DE..0x586F2. */
REGION void tsl9_resident_record_comparison_block_586de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 132(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23aa\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23da\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23ee\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x279e\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a0 = a0 | a4; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a1 = a1 | a5; LIVE;
    __builtin_unreachable();
}

/* Original0x586F2..0x58706. */
REGION void tsl9_resident_record_comparison_block_586f2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_586fe:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002276\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_586fe\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58706..0x5870A. */
REGION void tsl9_resident_record_comparison_block_58706(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x311c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58708:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_comparison_edge_58708\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x5870A..0x58716. */
REGION void tsl9_resident_record_comparison_block_5870a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_record_comparison_edge_58712:\n.option push\n.option norvc\nbeqz a5,.Lresident_record_comparison_edge_58712\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_585e2\n");
    __builtin_unreachable();
}

/* Original0x58716..0x58718. */
REGION void tsl9_resident_record_comparison_block_58716(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_58716:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58716\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x58718..0x5871E. */
REGION void tsl9_resident_record_comparison_block_58718(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x311c\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5871a:\n.option push\n.option norvc\nbnez a5,.Lresident_record_comparison_edge_5871a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_585e2\n");
    __builtin_unreachable();
}

/* Original0x5871E..0x58720. */
REGION void tsl9_resident_record_comparison_block_5871e(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_5871e:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_5871e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x58720..0x5872C. */
REGION void tsl9_resident_record_comparison_block_58720(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 109(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 117(s0)\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58728:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_comparison_edge_58728\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58660\n");
    __builtin_unreachable();
}

/* Original0x5872C..0x5873E. */
REGION void tsl9_resident_record_comparison_block_5872c(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 118\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 110\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_58736:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_58736\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5873E..0x58744. */
REGION void tsl9_resident_record_comparison_block_5873e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsnez s1, a0\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58742:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58742\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58662\n");
    __builtin_unreachable();
}

/* Original0x588B4..0x588D4. */
REGION void tsl9_candidate_external_flash_588b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000098)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_588cc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_588cc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x588D4..0x588D8. */
REGION void tsl9_resident_record_comparison_block_588d4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_588d6:\n.option push\n.option rvc\nc.bnez a0,.Lresident_record_comparison_edge_588d6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x588D8..0x588F0. */
REGION void tsl9_resident_record_comparison_block_588d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s2, 152(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nlbu s0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nandi s0, s0, 15\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s0, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb480\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 10(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4bc\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_588ec:\n.option push\n.option norvc\nbne s0,a4,.Lresident_record_comparison_edge_588ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58974\n");
    __builtin_unreachable();
}

/* Original0x588F0..0x588FA. */
REGION void tsl9_resident_record_comparison_block_588f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s3, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a4, s3, 0x6\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_588f8:\n.option push\n.option rvc\nc.bnez a4,.Lresident_record_comparison_edge_588f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58978\n");
    __builtin_unreachable();
}

/* Original0x588FA..0x58902. */
REGION void tsl9_resident_record_comparison_block_588fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a4, s3, 1\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_588fe:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_comparison_edge_588fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_5897c\n");
    __builtin_unreachable();
}

/* Original0x58902..0x5890C. */
REGION void tsl9_resident_record_comparison_block_58902(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s2)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_record_comparison_edge_58908:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_comparison_edge_58908\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58980\n");
    __builtin_unreachable();
}

/* Original0x5890C..0x5892A. */
REGION void tsl9_resident_record_comparison_block_5890c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s2, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 117(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 118\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_58922:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_58922\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5892A..0x5894E. */
REGION void tsl9_resident_record_comparison_block_5892a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 124(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 152(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s2, 10\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 126\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 125(s1)\n.option pop\n");
    PORT(".Lresident_record_comparison_literal_58946:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_comparison_literal_58946\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5894E..0x58954. */
REGION void tsl9_resident_record_comparison_block_5894e(void)
{
    REGS;
    a5 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lresident_record_comparison_edge_58950:\n.option push\n.option norvc\nbne s3,a5,.Lresident_record_comparison_edge_58950\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_comparison_block_58984\n");
    __builtin_unreachable();
}

/* Original0x58954..0x5895A. */
REGION void tsl9_resident_record_comparison_block_58954(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58956:\n.option push\n.option norvc\njal ra,.Lresident_record_comparison_edge_58956\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_585c8\n");
    __builtin_unreachable();
}

/* Original0x5895A..0x5895C. */
REGION void tsl9_resident_record_comparison_block_5895a(void)
{
    REGS;
    PORT(".Lresident_record_comparison_edge_5895a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_comparison_edge_5895a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x5895C..0x58962. */
REGION void tsl9_resident_record_comparison_block_5895c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5895e:\n.option push\n.option norvc\njal ra,.Lresident_record_comparison_edge_5895e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58498\n");
    __builtin_unreachable();
}

/* Original0x58962..0x58964. */
REGION void tsl9_resident_record_comparison_block_58962(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58964..0x58974. */
REGION void tsl9_resident_record_comparison_block_58964(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58974..0x58978. */
REGION void tsl9_resident_record_comparison_block_58974(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 7\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58976:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58976\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x58978..0x5897C. */
REGION void tsl9_resident_record_comparison_block_58978(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 5\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5897a:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_5897a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x5897C..0x58980. */
REGION void tsl9_resident_record_comparison_block_5897c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 25\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_5897e:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_5897e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x58980..0x58984. */
REGION void tsl9_resident_record_comparison_block_58980(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 17\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58982:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58982\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}

/* Original0x58984..0x58988. */
REGION void tsl9_resident_record_comparison_block_58984(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 24\n.option pop\n");
    PORT(".Lresident_record_comparison_edge_58986:\n.option push\n.option rvc\nc.j .Lresident_record_comparison_edge_58986\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_comparison_block_58964\n");
    __builtin_unreachable();
}
