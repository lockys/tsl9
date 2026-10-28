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

/* Fourteen complete conditional SDK link-event bodies:1068B/428i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4D66E..0x4D67C. */
REGION void tsl9_candidate_link_event_4d66e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 12(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d67a:\n.option push\n.option rvc\nc.beqz s0,.Lresident_link_event_callback_edge_4d67a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d69e\n");
    __builtin_unreachable();
}

/* Original0x4D67C..0x4D680. */
REGION void tsl9_resident_link_event_callback_block_4d67c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 12(s0)\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d67e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_event_callback_edge_4d67e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d688\n");
    __builtin_unreachable();
}

/* Original0x4D680..0x4D688. */
REGION void tsl9_resident_link_event_callback_block_4d680(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_literal_4d680:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d680\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D688..0x4D68C. */
REGION void tsl9_resident_link_event_callback_block_4d688(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 20(s0)\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d68a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_event_callback_edge_4d68a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d694\n");
    __builtin_unreachable();
}

/* Original0x4D68C..0x4D694. */
REGION void tsl9_resident_link_event_callback_block_4d68c(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_literal_4d68c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d68c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D694..0x4D69E. */
REGION void tsl9_resident_link_event_callback_block_4d694(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_link_event_callback_literal_4d696:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d696\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D69E..0x4D6AC. */
REGION void tsl9_resident_link_event_callback_block_4d69e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_literal_4d6a4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d6a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D6AC..0x4D6BA. */
REGION void tsl9_resident_link_event_callback_block_4d6ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb49c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D70A..0x4D72C. */
REGION void tsl9_candidate_link_event_4d70a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a3 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\naddi s1, a0, -4\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a3, s1, a3\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a4 = a4 + a3; LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 10(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2736\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d728:\n.option push\n.option norvc\nbne a3,a1,.Lresident_link_event_callback_edge_4d728\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d756\n");
    __builtin_unreachable();
}

/* Original0x4D72C..0x4D730. */
REGION void tsl9_resident_link_event_callback_block_4d72c(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d72e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_event_callback_edge_4d72e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d756\n");
    __builtin_unreachable();
}

/* Original0x4D730..0x4D73C. */
REGION void tsl9_resident_link_event_callback_block_4d730(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, a5, 800\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d738:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_link_event_callback_edge_4d738\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d742\n");
    __builtin_unreachable();
}

/* Original0x4D73C..0x4D742. */
REGION void tsl9_resident_link_event_callback_block_4d73c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211c\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d73e:\n.option push\n.option norvc\nbne a5,a2,.Lresident_link_event_callback_edge_4d73e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d756\n");
    __builtin_unreachable();
}

/* Original0x4D742..0x4D74A. */
REGION void tsl9_resident_link_event_callback_block_4d742(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_literal_4d742:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d742\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D74A..0x4D756. */
REGION void tsl9_resident_link_event_callback_block_4d74a(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a5, s1, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x4D756..0x4D760. */
REGION void tsl9_resident_link_event_callback_block_4d756(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D760..0x4D77A. */
REGION void tsl9_candidate_link_event_4d760(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_link_event_callback_literal_4d772:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4d772\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D77A..0x4D77C. */
REGION void tsl9_resident_link_event_callback_block_4d77a(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4d77a:\n.option push\n.option rvc\nc.beqz s1,.Lresident_link_event_callback_edge_4d77a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d7b6\n");
    __builtin_unreachable();
}

/* Original0x4D77C..0x4D7B6. */
REGION void tsl9_resident_link_event_callback_block_4d77c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 28(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2cdc\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000004); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000310)); LIVE;
    a5 = a5 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239a\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa01a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23ba\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23fe\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa03a\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xffffff9e)); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 4(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa05a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209a\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa07a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20ba\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 4(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20da\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20fa\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D7B6..0x4D7C0. */
REGION void tsl9_resident_link_event_callback_block_4d7b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D820..0x4D82E. */
REGION void tsl9_candidate_link_event_4d820(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3508\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d82a:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d82a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x4D82E..0x4D83A. */
REGION void tsl9_resident_link_event_callback_block_4d82e(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D83A..0x4D85C. */
REGION void tsl9_candidate_link_event_4d83a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nli s6, 7\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D85C..0x4D864. */
REGION void tsl9_resident_link_event_callback_block_4d85c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, -95(s4)\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d860:\n.option push\n.option norvc\nbltu s0,a5,.Lresident_link_event_callback_edge_4d860\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d8aa\n");
    __builtin_unreachable();
}

/* Original0x4D864..0x4D868. */
REGION void tsl9_resident_link_event_callback_block_4d864(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4d864:\n.option push\n.option norvc\nbnez s3,.Lresident_link_event_callback_edge_4d864\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d896\n");
    __builtin_unreachable();
}

/* Original0x4D868..0x4D874. */
REGION void tsl9_resident_link_event_callback_block_4d868(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D874..0x4D87C. */
REGION void tsl9_resident_link_event_callback_block_4d874(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, -96(s3)\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d878:\n.option push\n.option norvc\nbltu s0,a5,.Lresident_link_event_callback_edge_4d878\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d8e0\n");
    __builtin_unreachable();
}

/* Original0x4D87C..0x4D880. */
REGION void tsl9_resident_link_event_callback_block_4d87c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D880..0x4D892. */
REGION void tsl9_resident_link_event_callback_block_4d880(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x10\n.option pop\n");
    a2 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x10\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d88e:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d88e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d70a\n");
    __builtin_unreachable();
}

/* Original0x4D892..0x4D896. */
REGION void tsl9_resident_link_event_callback_block_4d892(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4d892:\n.option push\n.option norvc\nbne s0,s1,.Lresident_link_event_callback_edge_4d892\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d880\n");
    __builtin_unreachable();
}

/* Original0x4D896..0x4D8AA. */
REGION void tsl9_resident_link_event_callback_block_4d896(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D8AA..0x4D8B8. */
REGION void tsl9_resident_link_event_callback_block_4d8aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, -104(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s1, s0, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8b6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_event_callback_edge_4d8b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d8d8\n");
    __builtin_unreachable();
}

/* Original0x4D8B8..0x4D8BE. */
REGION void tsl9_resident_link_event_callback_block_4d8b8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20fe\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8ba:\n.option push\n.option norvc\nbne a5,s2,.Lresident_link_event_callback_edge_4d8ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d8d8\n");
    __builtin_unreachable();
}

/* Original0x4D8BE..0x4D8C2. */
REGION void tsl9_resident_link_event_callback_block_4d8be(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4d8be:\n.option push\n.option norvc\nbne s3,s6,.Lresident_link_event_callback_edge_4d8be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d8c8\n");
    __builtin_unreachable();
}

/* Original0x4D8C2..0x4D8C8. */
REGION void tsl9_resident_link_event_callback_block_4d8c2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20aa\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8c4:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d8c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4ed48\n");
    __builtin_unreachable();
}

/* Original0x4D8C8..0x4D8D2. */
REGION void tsl9_resident_link_event_callback_block_4d8c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s3\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d8ce:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d8ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e43e\n");
    __builtin_unreachable();
}

/* Original0x4D8D2..0x4D8D8. */
REGION void tsl9_resident_link_event_callback_block_4d8d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8d4:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d8d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d66e\n");
    __builtin_unreachable();
}

/* Original0x4D8D8..0x4D8E0. */
REGION void tsl9_resident_link_event_callback_block_4d8d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8de:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_4d8de\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_4d85c\n");
    __builtin_unreachable();
}

/* Original0x4D8E0..0x4D8EE. */
REGION void tsl9_resident_link_event_callback_block_4d8e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, -104(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s1, s0, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8ec:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_event_callback_edge_4d8ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d90e\n");
    __builtin_unreachable();
}

/* Original0x4D8EE..0x4D8F4. */
REGION void tsl9_resident_link_event_callback_block_4d8ee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x349c\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8f0:\n.option push\n.option norvc\nbeq a5,s5,.Lresident_link_event_callback_edge_4d8f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d90e\n");
    __builtin_unreachable();
}

/* Original0x4D8F4..0x4D8FA. */
REGION void tsl9_resident_link_event_callback_block_4d8f4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20fe\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8f6:\n.option push\n.option norvc\nbne a5,s2,.Lresident_link_event_callback_edge_4d8f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d90e\n");
    __builtin_unreachable();
}

/* Original0x4D8FA..0x4D900. */
REGION void tsl9_resident_link_event_callback_block_4d8fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d8fc:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d8fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d820\n");
    __builtin_unreachable();
}

/* Original0x4D900..0x4D908. */
REGION void tsl9_resident_link_event_callback_block_4d900(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    a1 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d904:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d904\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e46e\n");
    __builtin_unreachable();
}

/* Original0x4D908..0x4D90E. */
REGION void tsl9_resident_link_event_callback_block_4d908(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d90a:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d90a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d66e\n");
    __builtin_unreachable();
}

/* Original0x4D90E..0x4D916. */
REGION void tsl9_resident_link_event_callback_block_4d90e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d914:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_4d914\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_4d874\n");
    __builtin_unreachable();
}

/* Original0x4D916..0x4D91E. */
REGION void tsl9_candidate_link_event_4d916(void)
{
    REGS;
    a4 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d91a:\n.option push\n.option norvc\nbeq a0,a4,.Lresident_link_event_callback_edge_4d91a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d950\n");
    __builtin_unreachable();
}

/* Original0x4D91E..0x4D92C. */
REGION void tsl9_resident_link_event_callback_block_4d91e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d928:\n.option push\n.option norvc\nbne a1,a5,.Lresident_link_event_callback_edge_4d928\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d93a\n");
    __builtin_unreachable();
}

/* Original0x4D92C..0x4D93A. */
REGION void tsl9_resident_link_event_callback_block_4d92c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4d936:\n.option push\n.option norvc\njal zero,.Lresident_link_event_callback_edge_4d936\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d83a\n");
    __builtin_unreachable();
}

/* Original0x4D93A..0x4D940. */
REGION void tsl9_resident_link_event_callback_block_4d93a(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d93c:\n.option push\n.option norvc\nbne a1,a5,.Lresident_link_event_callback_edge_4d93c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4d948\n");
    __builtin_unreachable();
}

/* Original0x4D940..0x4D946. */
REGION void tsl9_resident_link_event_callback_block_4d940(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_link_event_callback_edge_4d942:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4d942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4f072\n");
    __builtin_unreachable();
}

/* Original0x4D946..0x4D948. */
REGION void tsl9_resident_link_event_callback_block_4d946(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4d946:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_event_callback_edge_4d946\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4d92c\n");
    __builtin_unreachable();
}

/* Original0x4D948..0x4D950. */
REGION void tsl9_resident_link_event_callback_block_4d948(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D950..0x4D952. */
REGION void tsl9_resident_link_event_callback_block_4d950(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E2EE..0x4E30E. */
REGION void tsl9_candidate_link_event_4e2ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_link_event_callback_literal_4e306:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4e306\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E30E..0x4E310. */
REGION void tsl9_resident_link_event_callback_block_4e30e(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4e30e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_event_callback_edge_4e30e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e358\n");
    __builtin_unreachable();
}

/* Original0x4E310..0x4E332. */
REGION void tsl9_resident_link_event_callback_block_4e310(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0xffffffa2); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa008\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb010\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a1, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa02e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 4(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa058\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 5(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb054\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 8\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e330:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_event_callback_edge_4e330\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e34c\n");
    __builtin_unreachable();
}

/* Original0x4E332..0x4E33C. */
REGION void tsl9_resident_link_event_callback_block_4e332(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, a5\n.option pop\n");
    PORT(".Lresident_link_event_callback_literal_4e334:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4e334\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E33C..0x4E34C. */
REGION void tsl9_resident_link_event_callback_block_4e33c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e348:\n.option push\n.option norvc\njal zero,.Lresident_link_event_callback_edge_4e348\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x4E34C..0x4E356. */
REGION void tsl9_resident_link_event_callback_block_4e34c(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_literal_4e34e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4e34e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E356..0x4E358. */
REGION void tsl9_resident_link_event_callback_block_4e356(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_4e356:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_4e356\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_4e33c\n");
    __builtin_unreachable();
}

/* Original0x4E358..0x4E362. */
REGION void tsl9_resident_link_event_callback_block_4e358(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E3EC..0x4E3F8. */
REGION void tsl9_candidate_link_event_4e3ec(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e3f6:\n.option push\n.option rvc\nc.beqz a1,.Lresident_link_event_callback_edge_4e3f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e414\n");
    __builtin_unreachable();
}

/* Original0x4E3F8..0x4E402. */
REGION void tsl9_resident_link_event_callback_block_4e3f8(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000060); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E402..0x4E40A. */
REGION void tsl9_resident_link_event_callback_block_4e402(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x206e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2408\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e406:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4e406\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e2ee\n");
    __builtin_unreachable();
}

/* Original0x4E40A..0x4E414. */
REGION void tsl9_resident_link_event_callback_block_4e40a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E414..0x4E422. */
REGION void tsl9_resident_link_event_callback_block_4e414(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a2\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    a2 = UINT32_C(0x00000016); LIVE;
    PORT(".Lresident_link_event_callback_literal_4e41a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4e41a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E422..0x4E426. */
REGION void tsl9_resident_link_event_callback_block_4e422(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.shsp s1, 8(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x8464\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e424:\n.option push\n.option rvc\nc.bnez s1,.Lresident_link_event_callback_edge_4e424\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e432\n");
    __builtin_unreachable();
}

/* Original0x4E426..0x4E432. */
REGION void tsl9_resident_link_event_callback_block_4e426(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203e\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 12(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a1, sp, 12\n.option pop\n");
    /* Conditional Xwchc: qk.c.shsp a5, 10(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x857c\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e42e:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4e42e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d760\n");
    __builtin_unreachable();
}

/* Original0x4E432..0x4E43E. */
REGION void tsl9_resident_link_event_callback_block_4e432(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a5, sp, 8\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000060); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e43c:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_4e43c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_4e402\n");
    __builtin_unreachable();
}

/* Original0x4E43E..0x4E446. */
REGION void tsl9_candidate_link_event_4e43e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e444:\n.option push\n.option rvc\nc.bnez a1,.Lresident_link_event_callback_edge_4e444\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e458\n");
    __builtin_unreachable();
}

/* Original0x4E446..0x4E452. */
REGION void tsl9_resident_link_event_callback_block_4e446(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x213e\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)); LIVE;
    /* Conditional Xwchc: qk.c.shsp a2, 12(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x8670\n.option pop\n");
    /* Conditional Xwchc: qk.c.shsp a5, 8(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x847c\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a5, sp, 8\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e450:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_event_callback_edge_4e450\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4e458\n");
    __builtin_unreachable();
}

/* Original0x4E452..0x4E458. */
REGION void tsl9_resident_link_event_callback_block_4e452(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x233e\n.option pop\n");
    /* Conditional Xwchc: qk.c.shsp a5, 10(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x857c\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a5, sp, 8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E458..0x4E468. */
REGION void tsl9_resident_link_event_callback_block_4e458(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x216e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 8(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2508\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000060); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e464:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4e464\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e2ee\n");
    __builtin_unreachable();
}

/* Original0x4E468..0x4E46E. */
REGION void tsl9_resident_link_event_callback_block_4e468(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E46E..0x4E47E. */
REGION void tsl9_candidate_link_event_4e46e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211c\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e47a:\n.option push\n.option norvc\nbne a5,a4,.Lresident_link_event_callback_edge_4e47a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4e49e\n");
    __builtin_unreachable();
}

/* Original0x4E47E..0x4E48E. */
REGION void tsl9_resident_link_event_callback_block_4e47e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x216e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 8(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2508\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e48a:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4e48a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e2ee\n");
    __builtin_unreachable();
}

/* Original0x4E48E..0x4E490. */
REGION void tsl9_resident_link_event_callback_block_4e48e(void)
{
    REGS;
    a2 = UINT32_C(0x00000012); LIVE;
    __builtin_unreachable();
}

/* Original0x4E490..0x4E49E. */
REGION void tsl9_resident_link_event_callback_block_4e490(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x206e\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e49a:\n.option push\n.option norvc\njal zero,.Lresident_link_event_callback_edge_4e49a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d70a\n");
    __builtin_unreachable();
}

/* Original0x4E49E..0x4E4A8. */
REGION void tsl9_resident_link_event_callback_block_4e49e(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x000000fb); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e4a4:\n.option push\n.option norvc\nbne a4,a3,.Lresident_link_event_callback_edge_4e4a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4e4b2\n");
    __builtin_unreachable();
}

/* Original0x4E4A8..0x4E4AE. */
REGION void tsl9_resident_link_event_callback_block_4e4a8(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e4aa:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4e4aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e3ec\n");
    __builtin_unreachable();
}

/* Original0x4E4AE..0x4E4B2. */
REGION void tsl9_resident_link_event_callback_block_4e4ae(void)
{
    REGS;
    a2 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e4b0:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_4e4b0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_4e490\n");
    __builtin_unreachable();
}

/* Original0x4E4B2..0x4E4B8. */
REGION void tsl9_resident_link_event_callback_block_4e4b2(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_link_event_callback_edge_4e4b4:\n.option push\n.option norvc\nbne a5,a4,.Lresident_link_event_callback_edge_4e4b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4e4c4\n");
    __builtin_unreachable();
}

/* Original0x4E4B8..0x4E4C4. */
REGION void tsl9_resident_link_event_callback_block_4e4b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4e4c0:\n.option push\n.option norvc\njal zero,.Lresident_link_event_callback_edge_4e4c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e43e\n");
    __builtin_unreachable();
}

/* Original0x4E4C4..0x4E4CC. */
REGION void tsl9_resident_link_event_callback_block_4e4c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EBC2..0x4EBDA. */
REGION void tsl9_candidate_link_event_4ebc2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa11c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219e\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb11c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21be\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa13c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21be\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 3(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb13c\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4ED48..0x4ED6A. */
REGION void tsl9_candidate_link_event_4ed48(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    /* Conditional Xwchc: qk.c.shsp a0, 14(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x8768\n.option pop\n");
    a3 = UINT32_C(0x0004f000); LIVE;
    a0 = UINT32_C(0x00010000); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\nli a6, 0\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    a3 = a3 + UINT32_C(0xfffffbc2); LIVE;
    a1 = UINT32_C(0x00000006); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lresident_link_event_callback_edge_4ed66:\n.option push\n.option norvc\njal ra,.Lresident_link_event_callback_edge_4ed66\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_4eb12\n");
    __builtin_unreachable();
}

/* Original0x4ED6A..0x4ED70. */
REGION void tsl9_resident_link_event_callback_block_4ed6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F072..0x4F07A. */
REGION void tsl9_candidate_link_event_4f072(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_link_event_callback_edge_4f076:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_link_event_callback_edge_4f076\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_4f0a0\n");
    __builtin_unreachable();
}

/* Original0x4F07A..0x4F08A. */
REGION void tsl9_resident_link_event_callback_block_4f07a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lresident_link_event_callback_literal_4f082:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_link_event_20000a94\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_event_callback_literal_4f082\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F08A..0x4F090. */
REGION void tsl9_resident_link_event_callback_block_4f08a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_event_callback_edge_4f08e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_event_callback_edge_4f08e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_event_callback_block_4f098\n");
    __builtin_unreachable();
}

/* Original0x4F090..0x4F098. */
REGION void tsl9_resident_link_event_callback_block_4f090(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23c8\n.option pop\n");
    PORT(".option push\n.option rvc\nand s0, s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsnez a0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F098..0x4F0A0. */
REGION void tsl9_resident_link_event_callback_block_4f098(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F0A0..0x4F0A4. */
REGION void tsl9_resident_link_event_callback_block_4f0a0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000A94..0x20000AA6. */
REGION void tsl9_candidate_link_event_20000a94(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b4)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000354)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x20000AA6..0x20000AAA. */
REGION void tsl9_resident_link_event_callback_block_20000aa6(void)
{
    REGS;
    PORT(".Lresident_link_event_callback_edge_20000aa6:\n.option push\n.option norvc\nbne a2,a5,.Lresident_link_event_callback_edge_20000aa6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_20000ab0\n");
    __builtin_unreachable();
}

/* Original0x20000AAA..0x20000AAC. */
REGION void tsl9_resident_link_event_callback_block_20000aaa(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x20000AAC..0x20000AB0. */
REGION void tsl9_resident_link_event_callback_block_20000aac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000AB0..0x20000ABE. */
REGION void tsl9_resident_link_event_callback_block_20000ab0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    a4 = a4 + UINT32_C(0x0000003c); LIVE;
    a1 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xffffffc6)); LIVE;
    PORT(".Lresident_link_event_callback_edge_20000aba:\n.option push\n.option norvc\nbeq a1,a0,.Lresident_link_event_callback_edge_20000aba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_event_callback_block_20000aac\n");
    __builtin_unreachable();
}

/* Original0x20000ABE..0x20000AC6. */
REGION void tsl9_resident_link_event_callback_block_20000abe(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_link_event_callback_edge_20000ac4:\n.option push\n.option rvc\nc.j .Lresident_link_event_callback_edge_20000ac4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_event_callback_block_20000aa6\n");
    __builtin_unreachable();
}
