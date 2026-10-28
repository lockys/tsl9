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

/* Three complete conditional transmit handlers:3576B/1173i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x5774E..0x57756. */
REGION void tsl9_candidate_transmit_handler_5774e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57756..0x5775C. */
REGION void tsl9_resident_transmit_handlers_block_57756(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5775a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_5775a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5780a\n");
    __builtin_unreachable();
}

/* Original0x5775C..0x57762. */
REGION void tsl9_resident_transmit_handlers_block_5775c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_57760:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_57760\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5782a\n");
    __builtin_unreachable();
}

/* Original0x57762..0x57768. */
REGION void tsl9_resident_transmit_handlers_block_57762(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 272(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_57766:\n.option push\n.option rvc\nc.beqz a0,.Lresident_transmit_handlers_edge_57766\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57770\n");
    __builtin_unreachable();
}

/* Original0x57768..0x57770. */
REGION void tsl9_resident_transmit_handlers_block_57768(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_57768:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_57768\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57770..0x5777C. */
REGION void tsl9_resident_transmit_handlers_block_57770(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 39(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_transmit_handlers_edge_57778:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_transmit_handlers_edge_57778\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_57780\n");
    __builtin_unreachable();
}

/* Original0x5777C..0x57780. */
REGION void tsl9_resident_transmit_handlers_block_5777c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5777c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5777c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x57780..0x5778C. */
REGION void tsl9_resident_transmit_handlers_block_57780(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 38(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_transmit_handlers_edge_57788:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_transmit_handlers_edge_57788\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_57790\n");
    __builtin_unreachable();
}

/* Original0x5778C..0x57790. */
REGION void tsl9_resident_transmit_handlers_block_5778c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5778c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5778c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x57790..0x5779C. */
REGION void tsl9_resident_transmit_handlers_block_57790(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 40(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_transmit_handlers_edge_57798:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_transmit_handlers_edge_57798\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_577a0\n");
    __builtin_unreachable();
}

/* Original0x5779C..0x577A0. */
REGION void tsl9_resident_transmit_handlers_block_5779c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5779c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5779c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x577A0..0x577AC. */
REGION void tsl9_resident_transmit_handlers_block_577a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 41(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_transmit_handlers_edge_577a8:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_transmit_handlers_edge_577a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_577b6\n");
    __builtin_unreachable();
}

/* Original0x577AC..0x577B0. */
REGION void tsl9_resident_transmit_handlers_block_577ac(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_577ac:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_577ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x577B0..0x577B6. */
REGION void tsl9_resident_transmit_handlers_block_577b0(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 41(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x577B6..0x577BA. */
REGION void tsl9_resident_transmit_handlers_block_577b6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_577b8:\n.option push\n.option rvc\nc.jal .Lresident_transmit_handlers_edge_577b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_flash_57a4a\n");
    __builtin_unreachable();
}

/* Original0x577BA..0x577C8. */
REGION void tsl9_resident_transmit_handlers_block_577ba(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000000b4)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_577c6:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_577c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57802\n");
    __builtin_unreachable();
}

/* Original0x577C8..0x577E6. */
REGION void tsl9_resident_transmit_handlers_block_577c8(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000004ec)) = (uint32_t)0; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000238)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000b0)) = (uint32_t)a4; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001f4)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_577e4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_577e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57802\n");
    __builtin_unreachable();
}

/* Original0x577E6..0x577F2. */
REGION void tsl9_resident_transmit_handlers_block_577e6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 412\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 32(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_577f0:\n.option push\n.option rvc\nc.beqz a0,.Lresident_transmit_handlers_edge_577f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57802\n");
    __builtin_unreachable();
}

/* Original0x577F2..0x577FA. */
REGION void tsl9_resident_transmit_handlers_block_577f2(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_577f2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_577f2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x577FA..0x57802. */
REGION void tsl9_resident_transmit_handlers_block_577fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 32(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 36(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57802..0x5780A. */
REGION void tsl9_resident_transmit_handlers_block_57802(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5780A..0x5780E. */
REGION void tsl9_resident_transmit_handlers_block_5780a(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5780c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_transmit_handlers_edge_5780c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57816\n");
    __builtin_unreachable();
}

/* Original0x5780E..0x57816. */
REGION void tsl9_resident_transmit_handlers_block_5780e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_5780e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5780e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57816..0x5782A. */
REGION void tsl9_resident_transmit_handlers_block_57816(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27ba\n.option pop\n");
    a4 = a4 | UINT32_C(0xffffff00); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7ba\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 280(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_57828:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_57828\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_57756\n");
    __builtin_unreachable();
}

/* Original0x5782A..0x5782E. */
REGION void tsl9_resident_transmit_handlers_block_5782a(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5782c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_transmit_handlers_edge_5782c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_57836\n");
    __builtin_unreachable();
}

/* Original0x5782E..0x57836. */
REGION void tsl9_resident_transmit_handlers_block_5782e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_5782e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5782e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57836..0x5784A. */
REGION void tsl9_resident_transmit_handlers_block_57836(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27ba\n.option pop\n");
    a4 = a4 | UINT32_C(0xffffff00); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7ba\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_57848:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_57848\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5775c\n");
    __builtin_unreachable();
}

/* Original0x59042..0x59062. */
REGION void tsl9_candidate_transmit_handler_59042(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000036)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000036)) = (uint8_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 19(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x393c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5905e:\n.option push\n.option norvc\nbnez a5,.Lresident_transmit_handlers_edge_5905e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_595a8\n");
    __builtin_unreachable();
}

/* Original0x59062..0x59082. */
REGION void tsl9_resident_transmit_handlers_block_59062(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x255c\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 19(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb938\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 17(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3918\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffec); LIVE;
    a5 = a5 | UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa55c\n.option pop\n");
    a5 = a4 << UINT32_C(0x00000018); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000001b)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5907e:\n.option push\n.option norvc\nbgez a5,.Lresident_transmit_handlers_edge_5907e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5908e\n");
    __builtin_unreachable();
}

/* Original0x59082..0x59088. */
REGION void tsl9_resident_transmit_handlers_block_59082(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000007f); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 17(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb918\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59088..0x5908C. */
REGION void tsl9_resident_transmit_handlers_block_59088(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59088:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59088\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x5908C..0x5908E. */
REGION void tsl9_resident_transmit_handlers_block_5908c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5908c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5908c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5908E..0x59098. */
REGION void tsl9_resident_transmit_handlers_block_5908e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)); LIVE;
    a3 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59096:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_59096\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_590e4\n");
    __builtin_unreachable();
}

/* Original0x59098..0x590A6. */
REGION void tsl9_resident_transmit_handlers_block_59098(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000100)); LIVE;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_590a4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_590a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_590de\n");
    __builtin_unreachable();
}

/* Original0x590A6..0x590AA. */
REGION void tsl9_resident_transmit_handlers_block_590a6(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_590a6:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_590a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a326\n");
    __builtin_unreachable();
}

/* Original0x590AA..0x590B2. */
REGION void tsl9_resident_transmit_handlers_block_590aa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c38\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_590ae:\n.option push\n.option norvc\nbne a4,a5,.Lresident_transmit_handlers_edge_590ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5919c\n");
    __builtin_unreachable();
}

/* Original0x590B2..0x590D0. */
REGION void tsl9_resident_transmit_handlers_block_590b2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2458\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa398\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3858\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb398\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 280(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s1)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    __builtin_unreachable();
}

/* Original0x590D0..0x590DE. */
REGION void tsl9_resident_transmit_handlers_block_590d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x590DE..0x590E2. */
REGION void tsl9_resident_transmit_handlers_block_590de(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_590de:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_590de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a306\n");
    __builtin_unreachable();
}

/* Original0x590E2..0x590E4. */
REGION void tsl9_resident_transmit_handlers_block_590e2(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_590e2:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_590e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x590E4..0x590EA. */
REGION void tsl9_resident_transmit_handlers_block_590e4(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_590e8:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_590e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_590f6\n");
    __builtin_unreachable();
}

/* Original0x590EA..0x590F4. */
REGION void tsl9_resident_transmit_handlers_block_590ea(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_590f0:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_590f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a23e\n");
    __builtin_unreachable();
}

/* Original0x590F4..0x590F6. */
REGION void tsl9_resident_transmit_handlers_block_590f4(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_590f4:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_590f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x590F6..0x590FE. */
REGION void tsl9_resident_transmit_handlers_block_590f6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2914\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_590fa:\n.option push\n.option norvc\nbne a3,s2,.Lresident_transmit_handlers_edge_590fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59368\n");
    __builtin_unreachable();
}

/* Original0x590FE..0x59100. */
REGION void tsl9_resident_transmit_handlers_block_590fe(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_590fe:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_590fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_591b6\n");
    __builtin_unreachable();
}

/* Original0x59100..0x59106. */
REGION void tsl9_resident_transmit_handlers_block_59100(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59104:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59104\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59112\n");
    __builtin_unreachable();
}

/* Original0x59106..0x5910C. */
REGION void tsl9_resident_transmit_handlers_block_59106(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5910C..0x59110. */
REGION void tsl9_resident_transmit_handlers_block_5910c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5910c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5910c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a804\n");
    __builtin_unreachable();
}

/* Original0x59110..0x59112. */
REGION void tsl9_resident_transmit_handlers_block_59110(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59110:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59110\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59112..0x59118. */
REGION void tsl9_resident_transmit_handlers_block_59112(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59116:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59116\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59126\n");
    __builtin_unreachable();
}

/* Original0x59118..0x59124. */
REGION void tsl9_resident_transmit_handlers_block_59118(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffbf); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59120:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59120\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a370\n");
    __builtin_unreachable();
}

/* Original0x59124..0x59126. */
REGION void tsl9_resident_transmit_handlers_block_59124(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59124:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59124\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59126..0x5912C. */
REGION void tsl9_resident_transmit_handlers_block_59126(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5912a:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_5912a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5913a\n");
    __builtin_unreachable();
}

/* Original0x5912C..0x59134. */
REGION void tsl9_resident_transmit_handlers_block_5912c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffff7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x59134..0x59138. */
REGION void tsl9_resident_transmit_handlers_block_59134(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59134:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59134\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5bc76\n");
    __builtin_unreachable();
}

/* Original0x59138..0x5913A. */
REGION void tsl9_resident_transmit_handlers_block_59138(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59138:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59138\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5913A..0x59140. */
REGION void tsl9_resident_transmit_handlers_block_5913a(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000100); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5913e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_5913e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59150\n");
    __builtin_unreachable();
}

/* Original0x59140..0x59148. */
REGION void tsl9_resident_transmit_handlers_block_59140(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffeff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x59148..0x5914E. */
REGION void tsl9_resident_transmit_handlers_block_59148(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5914a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5914a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a48e\n");
    __builtin_unreachable();
}

/* Original0x5914E..0x59150. */
REGION void tsl9_resident_transmit_handlers_block_5914e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5914e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5914e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59150..0x59156. */
REGION void tsl9_resident_transmit_handlers_block_59150(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000400); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59154:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59154\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59164\n");
    __builtin_unreachable();
}

/* Original0x59156..0x59162. */
REGION void tsl9_resident_transmit_handlers_block_59156(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffbff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_5915e:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5915e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5af74\n");
    __builtin_unreachable();
}

/* Original0x59162..0x59164. */
REGION void tsl9_resident_transmit_handlers_block_59162(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59162:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59162\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59164..0x5916C. */
REGION void tsl9_resident_transmit_handlers_block_59164(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59168:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_59168\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59180\n");
    __builtin_unreachable();
}

/* Original0x5916C..0x59178. */
REGION void tsl9_resident_transmit_handlers_block_5916c(void)
{
    REGS;
    a4 = UINT32_C(0xfffff000); LIVE;
    a4 = a4 + UINT32_C(0x000007ff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x59178..0x5917E. */
REGION void tsl9_resident_transmit_handlers_block_59178(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5917a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5917a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a588\n");
    __builtin_unreachable();
}

/* Original0x5917E..0x59180. */
REGION void tsl9_resident_transmit_handlers_block_5917e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5917e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5917e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59180..0x59188. */
REGION void tsl9_resident_transmit_handlers_block_59180(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59184:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_59184\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59198\n");
    __builtin_unreachable();
}

/* Original0x59188..0x59196. */
REGION void tsl9_resident_transmit_handlers_block_59188(void)
{
    REGS;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59192:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59192\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a686\n");
    __builtin_unreachable();
}

/* Original0x59196..0x59198. */
REGION void tsl9_resident_transmit_handlers_block_59196(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59196:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59196\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59198..0x5919C. */
REGION void tsl9_resident_transmit_handlers_block_59198(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a8)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x5919C..0x591B6. */
REGION void tsl9_resident_transmit_handlers_block_5919c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 272(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2458\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa398\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 272(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3858\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb398\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 272(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_591b4:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_591b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590d0\n");
    __builtin_unreachable();
}

/* Original0x591B6..0x591BE. */
REGION void tsl9_resident_transmit_handlers_block_591b6(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591ba:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_591ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59590\n");
    __builtin_unreachable();
}

/* Original0x591BE..0x591C4. */
REGION void tsl9_resident_transmit_handlers_block_591be(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591c2:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_591c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_591d0\n");
    __builtin_unreachable();
}

/* Original0x591C4..0x591CE. */
REGION void tsl9_resident_transmit_handlers_block_591c4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_591ca:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_591ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a7ba\n");
    __builtin_unreachable();
}

/* Original0x591CE..0x591D0. */
REGION void tsl9_resident_transmit_handlers_block_591ce(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_591ce:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_591ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x591D0..0x591D6. */
REGION void tsl9_resident_transmit_handlers_block_591d0(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591d4:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_591d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_591e4\n");
    __builtin_unreachable();
}

/* Original0x591D6..0x591E2. */
REGION void tsl9_resident_transmit_handlers_block_591d6(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffbf); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_591de:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_591de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a2a2\n");
    __builtin_unreachable();
}

/* Original0x591E2..0x591E4. */
REGION void tsl9_resident_transmit_handlers_block_591e2(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_591e2:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_591e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x591E4..0x591EA. */
REGION void tsl9_resident_transmit_handlers_block_591e4(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000200); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591e8:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_591e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5921a\n");
    __builtin_unreachable();
}

/* Original0x591EA..0x591F0. */
REGION void tsl9_resident_transmit_handlers_block_591ea(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591ec:\n.option push\n.option norvc\nbnez a4,.Lresident_transmit_handlers_edge_591ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x591F0..0x591F6. */
REGION void tsl9_resident_transmit_handlers_block_591f0(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000001a4)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_591f4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_591f4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5920e\n");
    __builtin_unreachable();
}

/* Original0x591F6..0x5920C. */
REGION void tsl9_resident_transmit_handlers_block_591f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 420(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffdff); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59208:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59208\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a898\n");
    __builtin_unreachable();
}

/* Original0x5920C..0x5920E. */
REGION void tsl9_resident_transmit_handlers_block_5920c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5920c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5920c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5920E..0x59216. */
REGION void tsl9_resident_transmit_handlers_block_5920e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_5920e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_transmit_fragment_20000ac6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5920e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59216..0x59218. */
REGION void tsl9_resident_transmit_handlers_block_59216(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59216:\n.option push\n.option rvc\nc.bnez a0,.Lresident_transmit_handlers_edge_59216\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_591f6\n");
    __builtin_unreachable();
}

/* Original0x59218..0x5921A. */
REGION void tsl9_resident_transmit_handlers_block_59218(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59218:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59218\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5921A..0x59220. */
REGION void tsl9_resident_transmit_handlers_block_5921a(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5921e:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_5921e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59234\n");
    __builtin_unreachable();
}

/* Original0x59220..0x59226. */
REGION void tsl9_resident_transmit_handlers_block_59220(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59222:\n.option push\n.option norvc\nbnez a4,.Lresident_transmit_handlers_edge_59222\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x59226..0x5922C. */
REGION void tsl9_resident_transmit_handlers_block_59226(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5922C..0x59232. */
REGION void tsl9_resident_transmit_handlers_block_5922c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5922e:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5922e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a120\n");
    __builtin_unreachable();
}

/* Original0x59232..0x59234. */
REGION void tsl9_resident_transmit_handlers_block_59232(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59232:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59232\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59234..0x5923A. */
REGION void tsl9_resident_transmit_handlers_block_59234(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59238:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_59238\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5924c\n");
    __builtin_unreachable();
}

/* Original0x5923A..0x59240. */
REGION void tsl9_resident_transmit_handlers_block_5923a(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5923c:\n.option push\n.option norvc\nbnez a4,.Lresident_transmit_handlers_edge_5923c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x59240..0x5924A. */
REGION void tsl9_resident_transmit_handlers_block_59240(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59246:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59246\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a70c\n");
    __builtin_unreachable();
}

/* Original0x5924A..0x5924C. */
REGION void tsl9_resident_transmit_handlers_block_5924a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5924a:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5924a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5924C..0x59252. */
REGION void tsl9_resident_transmit_handlers_block_5924c(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000400); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59250:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_59250\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59260\n");
    __builtin_unreachable();
}

/* Original0x59252..0x5925E. */
REGION void tsl9_resident_transmit_handlers_block_59252(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffbff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_5925a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5925a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a348\n");
    __builtin_unreachable();
}

/* Original0x5925E..0x59260. */
REGION void tsl9_resident_transmit_handlers_block_5925e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5925e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5925e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59260..0x59268. */
REGION void tsl9_resident_transmit_handlers_block_59260(void)
{
    REGS;
    a3 = a5 << UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59264:\n.option push\n.option norvc\nbgez a3,.Lresident_transmit_handlers_edge_59264\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5927a\n");
    __builtin_unreachable();
}

/* Original0x59268..0x59278. */
REGION void tsl9_resident_transmit_handlers_block_59268(void)
{
    REGS;
    a4 = UINT32_C(0xfffff000); LIVE;
    a4 = a4 + UINT32_C(0x000007ff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59274:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59274\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5bbc2\n");
    __builtin_unreachable();
}

/* Original0x59278..0x5927A. */
REGION void tsl9_resident_transmit_handlers_block_59278(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59278:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59278\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5927A..0x59280. */
REGION void tsl9_resident_transmit_handlers_block_5927a(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5927e:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_5927e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_592a0\n");
    __builtin_unreachable();
}

/* Original0x59280..0x59288. */
REGION void tsl9_resident_transmit_handlers_block_59280(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_59280:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_transmit_fragment_20000ac6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_59280\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59288..0x5928C. */
REGION void tsl9_resident_transmit_handlers_block_59288(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59288:\n.option push\n.option norvc\nbeqz a0,.Lresident_transmit_handlers_edge_59288\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5928C..0x5929E. */
REGION void tsl9_resident_transmit_handlers_block_5928c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5929a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5929a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a25e\n");
    __builtin_unreachable();
}

/* Original0x5929E..0x592A0. */
REGION void tsl9_resident_transmit_handlers_block_5929e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5929e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5929e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x592A0..0x592A6. */
REGION void tsl9_resident_transmit_handlers_block_592a0(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_transmit_handlers_edge_592a4:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_592a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_592b4\n");
    __builtin_unreachable();
}

/* Original0x592A6..0x592AC. */
REGION void tsl9_resident_transmit_handlers_block_592a6(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x592AC..0x592B2. */
REGION void tsl9_resident_transmit_handlers_block_592ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_592ae:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_592ae\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5ae56\n");
    __builtin_unreachable();
}

/* Original0x592B2..0x592B4. */
REGION void tsl9_resident_transmit_handlers_block_592b2(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_592b2:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_592b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x592B4..0x592B8. */
REGION void tsl9_resident_transmit_handlers_block_592b4(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_592b4:\n.option push\n.option norvc\nbgez a5,.Lresident_transmit_handlers_edge_592b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_592ce\n");
    __builtin_unreachable();
}

/* Original0x592B8..0x592CE. */
REGION void tsl9_resident_transmit_handlers_block_592b8(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_592cc:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_592cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5919c\n");
    __builtin_unreachable();
}

/* Original0x592CE..0x592D6. */
REGION void tsl9_resident_transmit_handlers_block_592ce(void)
{
    REGS;
    a3 = a5 << UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_transmit_handlers_edge_592d2:\n.option push\n.option norvc\nbgez a3,.Lresident_transmit_handlers_edge_592d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_592ea\n");
    __builtin_unreachable();
}

/* Original0x592D6..0x592DA. */
REGION void tsl9_resident_transmit_handlers_block_592d6(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_transmit_handlers_edge_592d8:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_592d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x592DA..0x592E8. */
REGION void tsl9_resident_transmit_handlers_block_592da(void)
{
    REGS;
    a4 = UINT32_C(0xfffff000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_592e4:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_592e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a386\n");
    __builtin_unreachable();
}

/* Original0x592E8..0x592EA. */
REGION void tsl9_resident_transmit_handlers_block_592e8(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_592e8:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_592e8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x592EA..0x592F2. */
REGION void tsl9_resident_transmit_handlers_block_592ea(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_transmit_handlers_edge_592ee:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_592ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_592fe\n");
    __builtin_unreachable();
}

/* Original0x592F2..0x592FE. */
REGION void tsl9_resident_transmit_handlers_block_592f2(void)
{
    REGS;
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_592fc:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_592fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59148\n");
    __builtin_unreachable();
}

/* Original0x592FE..0x59306. */
REGION void tsl9_resident_transmit_handlers_block_592fe(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x0000000f); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59302:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_59302\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59316\n");
    __builtin_unreachable();
}

/* Original0x59306..0x59314. */
REGION void tsl9_resident_transmit_handlers_block_59306(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59310:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59310\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a9ac\n");
    __builtin_unreachable();
}

/* Original0x59314..0x59316. */
REGION void tsl9_resident_transmit_handlers_block_59314(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59314:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59314\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59316..0x5931E. */
REGION void tsl9_resident_transmit_handlers_block_59316(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x0000000e); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5931a:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_5931a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5932e\n");
    __builtin_unreachable();
}

/* Original0x5931E..0x5932C. */
REGION void tsl9_resident_transmit_handlers_block_5931e(void)
{
    REGS;
    a4 = UINT32_C(0xfffe0000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59328:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59328\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a568\n");
    __builtin_unreachable();
}

/* Original0x5932C..0x5932E. */
REGION void tsl9_resident_transmit_handlers_block_5932c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5932c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5932c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5932E..0x59336. */
REGION void tsl9_resident_transmit_handlers_block_5932e(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x0000000b); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59332:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_59332\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59348\n");
    __builtin_unreachable();
}

/* Original0x59336..0x59346. */
REGION void tsl9_resident_transmit_handlers_block_59336(void)
{
    REGS;
    a4 = UINT32_C(0xfff00000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59342:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59342\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a614\n");
    __builtin_unreachable();
}

/* Original0x59346..0x59348. */
REGION void tsl9_resident_transmit_handlers_block_59346(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59346:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59346\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59348..0x59350. */
REGION void tsl9_resident_transmit_handlers_block_59348(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000009); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5934c:\n.option push\n.option norvc\nbgez a4,.Lresident_transmit_handlers_edge_5934c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59362\n");
    __builtin_unreachable();
}

/* Original0x59350..0x59360. */
REGION void tsl9_resident_transmit_handlers_block_59350(void)
{
    REGS;
    a4 = UINT32_C(0xffc00000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_5935c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5935c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a6e0\n");
    __builtin_unreachable();
}

/* Original0x59360..0x59362. */
REGION void tsl9_resident_transmit_handlers_block_59360(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59360:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59360\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59362..0x59368. */
REGION void tsl9_resident_transmit_handlers_block_59362(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)0; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59366:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59366\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5919c\n");
    __builtin_unreachable();
}

/* Original0x59368..0x5936A. */
REGION void tsl9_resident_transmit_handlers_block_59368(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59368:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_59368\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x5936A..0x59372. */
REGION void tsl9_resident_transmit_handlers_block_5936a(void)
{
    REGS;
    a5 = UINT32_C(0x00000047); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5936e:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_5936e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5950e\n");
    __builtin_unreachable();
}

/* Original0x59372..0x59376. */
REGION void tsl9_resident_transmit_handlers_block_59372(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59372:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_59372\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5942c\n");
    __builtin_unreachable();
}

/* Original0x59376..0x5937E. */
REGION void tsl9_resident_transmit_handlers_block_59376(void)
{
    REGS;
    a5 = UINT32_C(0x0000002e); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5937a:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_5937a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_593b6\n");
    __builtin_unreachable();
}

/* Original0x5937E..0x59382. */
REGION void tsl9_resident_transmit_handlers_block_5937e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5937e:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_5937e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_593d0\n");
    __builtin_unreachable();
}

/* Original0x59382..0x5938A. */
REGION void tsl9_resident_transmit_handlers_block_59382(void)
{
    REGS;
    a5 = UINT32_C(0x00000023); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59386:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59386\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x5938A..0x5938E. */
REGION void tsl9_resident_transmit_handlers_block_5938a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5938a:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_5938a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939e\n");
    __builtin_unreachable();
}

/* Original0x5938E..0x59394. */
REGION void tsl9_resident_transmit_handlers_block_5938e(void)
{
    REGS;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59390:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59390\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59544\n");
    __builtin_unreachable();
}

/* Original0x59394..0x5939A. */
REGION void tsl9_resident_transmit_handlers_block_59394(void)
{
    REGS;
    a5 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59396:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59396\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59550\n");
    __builtin_unreachable();
}

/* Original0x5939A..0x5939E. */
REGION void tsl9_resident_transmit_handlers_block_5939a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5939c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5939c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59088\n");
    __builtin_unreachable();
}

/* Original0x5939E..0x593A6. */
REGION void tsl9_resident_transmit_handlers_block_5939e(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593a2:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_593a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59550\n");
    __builtin_unreachable();
}

/* Original0x593A6..0x593AE. */
REGION void tsl9_resident_transmit_handlers_block_593a6(void)
{
    REGS;
    a5 = UINT32_C(0x0000002c); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593aa:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_593aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5956e\n");
    __builtin_unreachable();
}

/* Original0x593AE..0x593B6. */
REGION void tsl9_resident_transmit_handlers_block_593ae(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593b2:\n.option push\n.option norvc\nbne a3,a5,.Lresident_transmit_handlers_edge_593b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x593B6..0x593BC. */
REGION void tsl9_resident_transmit_handlers_block_593b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_593b8:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_593b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x593BC..0x593D0. */
REGION void tsl9_resident_transmit_handlers_block_593bc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_593ce:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_593ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_594d4\n");
    __builtin_unreachable();
}

/* Original0x593D0..0x593D8. */
REGION void tsl9_resident_transmit_handlers_block_593d0(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593d4:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_593d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59568\n");
    __builtin_unreachable();
}

/* Original0x593D8..0x593DC. */
REGION void tsl9_resident_transmit_handlers_block_593d8(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_593d8:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_593d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59406\n");
    __builtin_unreachable();
}

/* Original0x593DC..0x593E4. */
REGION void tsl9_resident_transmit_handlers_block_593dc(void)
{
    REGS;
    a5 = UINT32_C(0x00000031); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593e0:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_593e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5910c\n");
    __builtin_unreachable();
}

/* Original0x593E4..0x593EC. */
REGION void tsl9_resident_transmit_handlers_block_593e4(void)
{
    REGS;
    a5 = UINT32_C(0x00000037); LIVE;
    PORT(".Lresident_transmit_handlers_edge_593e8:\n.option push\n.option norvc\nbne a3,a5,.Lresident_transmit_handlers_edge_593e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x593EC..0x59404. */
REGION void tsl9_resident_transmit_handlers_block_593ec(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004d)) = (uint8_t)a5; LIVE;
    a1 = a0 + UINT32_C(0x000000ac); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    a0 = a0 + UINT32_C(0x000000cc); LIVE;
    PORT(".Lresident_transmit_handlers_literal_593fc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_593fc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59404..0x59406. */
REGION void tsl9_resident_transmit_handlers_block_59404(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59404:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59404\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_592ac\n");
    __builtin_unreachable();
}

/* Original0x59406..0x5940E. */
REGION void tsl9_resident_transmit_handlers_block_59406(void)
{
    REGS;
    a5 = UINT32_C(0x00000041); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5940a:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_5940a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_594b8\n");
    __builtin_unreachable();
}

/* Original0x5940E..0x59412. */
REGION void tsl9_resident_transmit_handlers_block_5940e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5940e:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_transmit_handlers_edge_5940e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x59412..0x5941A. */
REGION void tsl9_resident_transmit_handlers_block_59412(void)
{
    REGS;
    a5 = UINT32_C(0x00000045); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59416:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_transmit_handlers_edge_59416\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x5941A..0x5942C. */
REGION void tsl9_resident_transmit_handlers_block_5941a(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000058)) = (uint16_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_5942a:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5942a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5953e\n");
    __builtin_unreachable();
}

/* Original0x5942C..0x59434. */
REGION void tsl9_resident_transmit_handlers_block_5942c(void)
{
    REGS;
    a5 = UINT32_C(0x00000066); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59430:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59430\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5959e\n");
    __builtin_unreachable();
}

/* Original0x59434..0x59438. */
REGION void tsl9_resident_transmit_handlers_block_59434(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59434:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_59434\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5946e\n");
    __builtin_unreachable();
}

/* Original0x59438..0x59440. */
REGION void tsl9_resident_transmit_handlers_block_59438(void)
{
    REGS;
    a5 = UINT32_C(0x00000055); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5943c:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_5943c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59590\n");
    __builtin_unreachable();
}

/* Original0x59440..0x59444. */
REGION void tsl9_resident_transmit_handlers_block_59440(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59440:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_59440\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59456\n");
    __builtin_unreachable();
}

/* Original0x59444..0x5944C. */
REGION void tsl9_resident_transmit_handlers_block_59444(void)
{
    REGS;
    a5 = UINT32_C(0x0000004b); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59448:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59448\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5958a\n");
    __builtin_unreachable();
}

/* Original0x5944C..0x59454. */
REGION void tsl9_resident_transmit_handlers_block_5944c(void)
{
    REGS;
    a5 = UINT32_C(0x00000051); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59450:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_59450\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59134\n");
    __builtin_unreachable();
}

/* Original0x59454..0x59456. */
REGION void tsl9_resident_transmit_handlers_block_59454(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59454:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59454\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x59456..0x5945E. */
REGION void tsl9_resident_transmit_handlers_block_59456(void)
{
    REGS;
    a5 = UINT32_C(0x00000057); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5945a:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_transmit_handlers_edge_5945a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59148\n");
    __builtin_unreachable();
}

/* Original0x5945E..0x59466. */
REGION void tsl9_resident_transmit_handlers_block_5945e(void)
{
    REGS;
    a5 = UINT32_C(0x00000061); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59462:\n.option push\n.option norvc\nbne a3,a5,.Lresident_transmit_handlers_edge_59462\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x59466..0x5946C. */
REGION void tsl9_resident_transmit_handlers_block_59466(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59468:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59468\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x5946C..0x5946E. */
REGION void tsl9_resident_transmit_handlers_block_5946c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5946c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5946c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_594d4\n");
    __builtin_unreachable();
}

/* Original0x5946E..0x59476. */
REGION void tsl9_resident_transmit_handlers_block_5946e(void)
{
    REGS;
    a5 = UINT32_C(0x00000072); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59472:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_transmit_handlers_edge_59472\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_594a2\n");
    __builtin_unreachable();
}

/* Original0x59476..0x5947E. */
REGION void tsl9_resident_transmit_handlers_block_59476(void)
{
    REGS;
    a5 = UINT32_C(0x00000071); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5947a:\n.option push\n.option norvc\nbleu a5,a3,.Lresident_transmit_handlers_edge_5947a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59466\n");
    __builtin_unreachable();
}

/* Original0x5947E..0x5948C. */
REGION void tsl9_resident_transmit_handlers_block_5947e(void)
{
    REGS;
    a5 = a3 + UINT32_C(0xffffff96); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59488:\n.option push\n.option norvc\nbltu s2,a5,.Lresident_transmit_handlers_edge_59488\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x5948C..0x59490. */
REGION void tsl9_resident_transmit_handlers_block_5948c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5948c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5948c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x59490..0x594A2. */
REGION void tsl9_resident_transmit_handlers_block_59490(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_594a0:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_594a0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_595a2\n");
    __builtin_unreachable();
}

/* Original0x594A2..0x594AA. */
REGION void tsl9_resident_transmit_handlers_block_594a2(void)
{
    REGS;
    a5 = UINT32_C(0x00000076); LIVE;
    PORT(".Lresident_transmit_handlers_edge_594a6:\n.option push\n.option norvc\nbeq a3,a5,.Lresident_transmit_handlers_edge_594a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59178\n");
    __builtin_unreachable();
}

/* Original0x594AA..0x594B2. */
REGION void tsl9_resident_transmit_handlers_block_594aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000086); LIVE;
    PORT(".Lresident_transmit_handlers_edge_594ae:\n.option push\n.option norvc\nbne a3,a5,.Lresident_transmit_handlers_edge_594ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x594B2..0x594B6. */
REGION void tsl9_resident_transmit_handlers_block_594b2(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_594b2:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_594b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a686\n");
    __builtin_unreachable();
}

/* Original0x594B6..0x594B8. */
REGION void tsl9_resident_transmit_handlers_block_594b6(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_594b6:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_594b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_594d4\n");
    __builtin_unreachable();
}

/* Original0x594B8..0x594C2. */
REGION void tsl9_resident_transmit_handlers_block_594b8(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)); LIVE;
    a4 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_transmit_handlers_edge_594be:\n.option push\n.option norvc\nbne a5,a4,.Lresident_transmit_handlers_edge_594be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_594e0\n");
    __builtin_unreachable();
}

/* Original0x594C2..0x594CA. */
REGION void tsl9_resident_transmit_handlers_block_594c2(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000100)); LIVE;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_594c8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_594c8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_594da\n");
    __builtin_unreachable();
}

/* Original0x594CA..0x594D4. */
REGION void tsl9_resident_transmit_handlers_block_594ca(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)) = (uint8_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_594d0:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_594d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a326\n");
    __builtin_unreachable();
}

/* Original0x594D4..0x594DA. */
REGION void tsl9_resident_transmit_handlers_block_594d4(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_594d8:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_594d8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x594DA..0x594DE. */
REGION void tsl9_resident_transmit_handlers_block_594da(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_594da:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_594da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a306\n");
    __builtin_unreachable();
}

/* Original0x594DE..0x594E0. */
REGION void tsl9_resident_transmit_handlers_block_594de(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_594de:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_594de\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_594d4\n");
    __builtin_unreachable();
}

/* Original0x594E0..0x594E6. */
REGION void tsl9_resident_transmit_handlers_block_594e0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_594e2:\n.option push\n.option norvc\nbne a5,s2,.Lresident_transmit_handlers_edge_594e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_594f8\n");
    __builtin_unreachable();
}

/* Original0x594E6..0x594F8. */
REGION void tsl9_resident_transmit_handlers_block_594e6(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000058)) = (uint16_t)a5; LIVE;
    PORT(".Lresident_transmit_handlers_edge_594f6:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_594f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5922c\n");
    __builtin_unreachable();
}

/* Original0x594F8..0x594FC. */
REGION void tsl9_resident_transmit_handlers_block_594f8(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_594f8:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_594f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x594FC..0x5950E. */
REGION void tsl9_resident_transmit_handlers_block_594fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 16(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5950c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5950c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5950E..0x59518. */
REGION void tsl9_resident_transmit_handlers_block_5950e(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)); LIVE;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59514:\n.option push\n.option norvc\nbne a4,a5,.Lresident_transmit_handlers_edge_59514\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5952e\n");
    __builtin_unreachable();
}

/* Original0x59518..0x5951C. */
REGION void tsl9_resident_transmit_handlers_block_59518(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59518:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59518\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a306\n");
    __builtin_unreachable();
}

/* Original0x5951C..0x59520. */
REGION void tsl9_resident_transmit_handlers_block_5951c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s2, 16(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59520..0x5952E. */
REGION void tsl9_resident_transmit_handlers_block_59520(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5952c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5952c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5952E..0x5953E. */
REGION void tsl9_resident_transmit_handlers_block_5952e(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000058)) = (uint16_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5953E..0x59542. */
REGION void tsl9_resident_transmit_handlers_block_5953e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5953e:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5953e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a120\n");
    __builtin_unreachable();
}

/* Original0x59542..0x59544. */
REGION void tsl9_resident_transmit_handlers_block_59542(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59542:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59542\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59520\n");
    __builtin_unreachable();
}

/* Original0x59544..0x59548. */
REGION void tsl9_resident_transmit_handlers_block_59544(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59544:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59544\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a1dc\n");
    __builtin_unreachable();
}

/* Original0x59548..0x59550. */
REGION void tsl9_resident_transmit_handlers_block_59548(void)
{
    REGS;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5954e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5954e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59550..0x59556. */
REGION void tsl9_resident_transmit_handlers_block_59550(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59552:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59552\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5c818\n");
    __builtin_unreachable();
}

/* Original0x59556..0x59568. */
REGION void tsl9_resident_transmit_handlers_block_59556(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 16(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59566:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59566\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x59568..0x5956C. */
REGION void tsl9_resident_transmit_handlers_block_59568(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59568:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59568\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a286\n");
    __builtin_unreachable();
}

/* Original0x5956C..0x5956E. */
REGION void tsl9_resident_transmit_handlers_block_5956c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5956c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5956c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5956E..0x59588. */
REGION void tsl9_resident_transmit_handlers_block_5956e(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004c)) = (uint8_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e4)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e8)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000ec)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000f0)) = (uint32_t)0; LIVE;
    PORT(".Lresident_transmit_handlers_edge_59584:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59584\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a222\n");
    __builtin_unreachable();
}

/* Original0x59588..0x5958A. */
REGION void tsl9_resident_transmit_handlers_block_59588(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59588:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59588\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5958A..0x5958E. */
REGION void tsl9_resident_transmit_handlers_block_5958a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5958a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5958a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5a370\n");
    __builtin_unreachable();
}

/* Original0x5958E..0x59590. */
REGION void tsl9_resident_transmit_handlers_block_5958e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5958e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5958e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_594d4\n");
    __builtin_unreachable();
}

/* Original0x59590..0x59598. */
REGION void tsl9_resident_transmit_handlers_block_59590(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_59590:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_transmit_fragment_20000ac6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_59590\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59598..0x5959C. */
REGION void tsl9_resident_transmit_handlers_block_59598(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59598:\n.option push\n.option norvc\nbeqz a0,.Lresident_transmit_handlers_edge_59598\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x5959C..0x5959E. */
REGION void tsl9_resident_transmit_handlers_block_5959c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5959c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_5959c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5939a\n");
    __builtin_unreachable();
}

/* Original0x5959E..0x595A2. */
REGION void tsl9_resident_transmit_handlers_block_5959e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5959e:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5959e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_5af74\n");
    __builtin_unreachable();
}

/* Original0x595A2..0x595A8. */
REGION void tsl9_resident_transmit_handlers_block_595a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s2, 16(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_595a6:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_595a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x595A8..0x595B8. */
REGION void tsl9_resident_transmit_handlers_block_595a8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2b9a\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xab9a\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_595b6:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_595b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_590aa\n");
    __builtin_unreachable();
}

/* Original0x595B8..0x595FC. */
REGION void tsl9_candidate_transmit_handler_595b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s2, 952\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 164(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x6e\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 952\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, s5, 564\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s6, s6, 1344\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x595FC..0x59606. */
REGION void tsl9_resident_transmit_handlers_block_595fc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    a4 = UINT32_C(0x000000c1); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59602:\n.option push\n.option norvc\nbne a5,a4,.Lresident_transmit_handlers_edge_59602\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59764\n");
    __builtin_unreachable();
}

/* Original0x59606..0x59610. */
REGION void tsl9_resident_transmit_handlers_block_59606(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5960e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_5960e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59636\n");
    __builtin_unreachable();
}

/* Original0x59610..0x5962E. */
REGION void tsl9_resident_transmit_handlers_block_59610(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffefc)) = (uint8_t)0; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a4 = a4 & UINT32_C(0xfffffff8); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000008); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 >> UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5962c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_5962c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59636\n");
    __builtin_unreachable();
}

/* Original0x5962E..0x59636. */
REGION void tsl9_resident_transmit_handlers_block_5962e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59636..0x5963C. */
REGION void tsl9_resident_transmit_handlers_block_59636(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 12(s5)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5963a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_5963a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59644\n");
    __builtin_unreachable();
}

/* Original0x5963C..0x59644. */
REGION void tsl9_resident_transmit_handlers_block_5963c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_5963c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_20000d42\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5963c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59644..0x596B0. */
REGION void tsl9_resident_transmit_handlers_block_59644(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a2, 1340(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000a0); LIVE;
    a1 = UINT32_C(0x82000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1288(s4)\n.option pop\n");
    a1 = a1 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nlui s7, 0x20003\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 322(s0)\n.option pop\n");
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    a3 = a4 << UINT32_C(0x00000019); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & a1; LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 152(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 156(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 1424(s7)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 310(s0)\n.option pop\n");
    a3 = a4 & UINT32_C(0x0000007f); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffff80); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_transmit_handlers_edge_596ac:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_596ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_transmit_handler_59042\n");
    __builtin_unreachable();
}

/* Original0x596B0..0x596B6. */
REGION void tsl9_resident_transmit_handlers_block_596b0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x385c\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, s7\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_596b4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_596b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59734\n");
    __builtin_unreachable();
}

/* Original0x596B6..0x596BE. */
REGION void tsl9_resident_transmit_handlers_block_596b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_596bc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_596bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59734\n");
    __builtin_unreachable();
}

/* Original0x596BE..0x596CA. */
REGION void tsl9_resident_transmit_handlers_block_596be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_literal_596c2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_20002426\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_596c2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x596CA..0x596CC. */
REGION void tsl9_resident_transmit_handlers_block_596ca(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_596ca:\n.option push\n.option rvc\nc.beqz a0,.Lresident_transmit_handlers_edge_596ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_596d2\n");
    __builtin_unreachable();
}

/* Original0x596CC..0x596D0. */
REGION void tsl9_resident_transmit_handlers_block_596cc(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_596cc:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_596cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x596D0..0x596D2. */
REGION void tsl9_resident_transmit_handlers_block_596d0(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_596d0:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_596d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59bfe\n");
    __builtin_unreachable();
}

/* Original0x596D2..0x59700. */
REGION void tsl9_resident_transmit_handlers_block_596d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s7)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000007a); LIVE;
    __builtin_unreachable();
}

/* Original0x59700..0x59720. */
REGION void tsl9_resident_transmit_handlers_block_59700(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3850\n.option pop\n");
    a5 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 326(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb0bc\n.option pop\n");
    a5 = UINT32_C(0xffffffc3); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 6(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a2 = a2 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5971c:\n.option push\n.option norvc\nbne a1,a5,.Lresident_transmit_handlers_edge_5971c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59728\n");
    __builtin_unreachable();
}

/* Original0x59720..0x59728. */
REGION void tsl9_resident_transmit_handlers_block_59720(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 328(s0)\n.option pop\n");
    a1 = a1 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x59728..0x5972A. */
REGION void tsl9_resident_transmit_handlers_block_59728(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x5972A..0x59732. */
REGION void tsl9_resident_transmit_handlers_block_5972a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_literal_5972a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_register_work_mode_200026ba\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5972a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59732..0x59734. */
REGION void tsl9_resident_transmit_handlers_block_59732(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59732:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59732\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_595fc\n");
    __builtin_unreachable();
}

/* Original0x59734..0x59764. */
REGION void tsl9_resident_transmit_handlers_block_59734(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000590)); LIVE;
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59762:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59762\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59700\n");
    __builtin_unreachable();
}

/* Original0x59764..0x5976C. */
REGION void tsl9_resident_transmit_handlers_block_59764(void)
{
    REGS;
    a4 = UINT32_C(0x000000c4); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59768:\n.option push\n.option norvc\nbne a5,a4,.Lresident_transmit_handlers_edge_59768\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59c50\n");
    __builtin_unreachable();
}

/* Original0x5976C..0x59774. */
REGION void tsl9_resident_transmit_handlers_block_5976c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59770:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_59770\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59c18\n");
    __builtin_unreachable();
}

/* Original0x59774..0x5977E. */
REGION void tsl9_resident_transmit_handlers_block_59774(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5977a:\n.option push\n.option norvc\nbgez a5,.Lresident_transmit_handlers_edge_5977a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_597a0\n");
    __builtin_unreachable();
}

/* Original0x5977E..0x597A0. */
REGION void tsl9_resident_transmit_handlers_block_5977e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 310(s0)\n.option pop\n");
    a4 = a5 >> UINT32_C(0x00000003); LIVE;
    a3 = a5 & UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nadd a4, a4, s0\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a3\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000130)); LIVE;
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a5 = a5 & a3; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000130)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x597A0..0x597A8. */
REGION void tsl9_resident_transmit_handlers_block_597a0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x347c\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_597a6:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_597a6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_597b8\n");
    __builtin_unreachable();
}

/* Original0x597A8..0x597B8. */
REGION void tsl9_resident_transmit_handlers_block_597a8(void)
{
    REGS;
    a4 = UINT32_C(0xffffff80); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac58\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb47c\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 168(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x597B8..0x597D2. */
REGION void tsl9_resident_transmit_handlers_block_597b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 76(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 276(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, s0, 50\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, s0, 52\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_literal_597ca:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_597ca\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x597D2..0x597EA. */
REGION void tsl9_resident_transmit_handlers_block_597d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 52(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 70(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a0, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa0e8\n.option pop\n");
    a5 = a5 - a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 52(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20fc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_597e6:\n.option push\n.option norvc\nbnez a5,.Lresident_transmit_handlers_edge_597e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59b30\n");
    __builtin_unreachable();
}

/* Original0x597EA..0x59804. */
REGION void tsl9_resident_transmit_handlers_block_597ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 25(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 128(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59800:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59800\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_560b2\n");
    __builtin_unreachable();
}

/* Original0x59804..0x59806. */
REGION void tsl9_resident_transmit_handlers_block_59804(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59804:\n.option push\n.option rvc\nc.bnez a0,.Lresident_transmit_handlers_edge_59804\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5985e\n");
    __builtin_unreachable();
}

/* Original0x59806..0x59810. */
REGION void tsl9_resident_transmit_handlers_block_59806(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 19(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5980e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_5980e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5984c\n");
    __builtin_unreachable();
}

/* Original0x59810..0x59814. */
REGION void tsl9_resident_transmit_handlers_block_59810(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c38\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59812:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59812\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5984c\n");
    __builtin_unreachable();
}

/* Original0x59814..0x5981A. */
REGION void tsl9_resident_transmit_handlers_block_59814(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3798\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59818:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_59818\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5984c\n");
    __builtin_unreachable();
}

/* Original0x5981A..0x5982C. */
REGION void tsl9_resident_transmit_handlers_block_5981a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27ba\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 | UINT32_C(0xffffff00); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7ba\n.option pop\n");
    PORT(".Lresident_transmit_handlers_literal_59824:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_59824\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5982C..0x59846. */
REGION void tsl9_resident_transmit_handlers_block_5982c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 68(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 68(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 280(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 420(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59844:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59844\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5984c\n");
    __builtin_unreachable();
}

/* Original0x59846..0x5984C. */
REGION void tsl9_resident_transmit_handlers_block_59846(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 420(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5984C..0x59850. */
REGION void tsl9_resident_transmit_handlers_block_5984c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x385c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5984e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_5984e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5985e\n");
    __builtin_unreachable();
}

/* Original0x59850..0x59858. */
REGION void tsl9_resident_transmit_handlers_block_59850(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59856:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59856\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5985e\n");
    __builtin_unreachable();
}

/* Original0x59858..0x5985E. */
REGION void tsl9_resident_transmit_handlers_block_59858(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5985a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5985a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_560f6\n");
    __builtin_unreachable();
}

/* Original0x5985E..0x59866. */
REGION void tsl9_resident_transmit_handlers_block_5985e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20fc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59862:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_59862\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59968\n");
    __builtin_unreachable();
}

/* Original0x59866..0x59870. */
REGION void tsl9_resident_transmit_handlers_block_59866(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5986c:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_5986c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59968\n");
    __builtin_unreachable();
}

/* Original0x59870..0x59876. */
REGION void tsl9_resident_transmit_handlers_block_59870(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c1c\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc1c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59876..0x59884. */
REGION void tsl9_resident_transmit_handlers_block_59876(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 3(s1)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_literal_5987c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_20000c86\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_5987c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59884..0x5988A. */
REGION void tsl9_resident_transmit_handlers_block_59884(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59886:\n.option push\n.option norvc\nbne a0,a5,.Lresident_transmit_handlers_edge_59886\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59b76\n");
    __builtin_unreachable();
}

/* Original0x5988A..0x59890. */
REGION void tsl9_resident_transmit_handlers_block_5988a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5988c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5988c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_transmit_handler_59042\n");
    __builtin_unreachable();
}

/* Original0x59890..0x5989A. */
REGION void tsl9_resident_transmit_handlers_block_59890(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59896:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_59896\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59b42\n");
    __builtin_unreachable();
}

/* Original0x5989A..0x598A0. */
REGION void tsl9_resident_transmit_handlers_block_5989a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x385c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5989c:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_5989c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59b42\n");
    __builtin_unreachable();
}

/* Original0x598A0..0x598AC. */
REGION void tsl9_resident_transmit_handlers_block_598a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_literal_598a4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_20002426\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_598a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x598AC..0x598B0. */
REGION void tsl9_resident_transmit_handlers_block_598ac(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_598ac:\n.option push\n.option norvc\nbnez a0,.Lresident_transmit_handlers_edge_598ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_596cc\n");
    __builtin_unreachable();
}

/* Original0x598B0..0x598E2. */
REGION void tsl9_resident_transmit_handlers_block_598b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000007a); LIVE;
    __builtin_unreachable();
}

/* Original0x598E2..0x598F2. */
REGION void tsl9_resident_transmit_handlers_block_598e2(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a1, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x384c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 326(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_598ee:\n.option push\n.option norvc\nbne a0,a5,.Lresident_transmit_handlers_edge_598ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_598fa\n");
    __builtin_unreachable();
}

/* Original0x598F2..0x598FA. */
REGION void tsl9_resident_transmit_handlers_block_598f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 328(s0)\n.option pop\n");
    a0 = a0 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x598FA..0x598FE. */
REGION void tsl9_resident_transmit_handlers_block_598fa(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_598fa:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_598fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x598FE..0x5991E. */
REGION void tsl9_resident_transmit_handlers_block_598fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00800000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    a5 = UINT32_C(0xffffffc3); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 12(s5)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5991c:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_5991c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5995c\n");
    __builtin_unreachable();
}

/* Original0x5991E..0x59924. */
REGION void tsl9_resident_transmit_handlers_block_5991e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59922:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59922\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5995c\n");
    __builtin_unreachable();
}

/* Original0x59924..0x5992A. */
REGION void tsl9_resident_transmit_handlers_block_59924(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3478\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59928:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59928\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5995c\n");
    __builtin_unreachable();
}

/* Original0x5992A..0x59938. */
REGION void tsl9_resident_transmit_handlers_block_5992a(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x278c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59934:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59934\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_6a722\n");
    __builtin_unreachable();
}

/* Original0x59938..0x5993A. */
REGION void tsl9_resident_transmit_handlers_block_59938(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59938:\n.option push\n.option rvc\nc.bnez a0,.Lresident_transmit_handlers_edge_59938\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5995c\n");
    __builtin_unreachable();
}

/* Original0x5993A..0x59956. */
REGION void tsl9_resident_transmit_handlers_block_5993a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27ba\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    a4 = a4 | UINT32_C(0xffffff00); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7ba\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 288(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 66(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59954:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59954\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_5995c\n");
    __builtin_unreachable();
}

/* Original0x59956..0x5995C. */
REGION void tsl9_resident_transmit_handlers_block_59956(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 66(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5995C..0x59968. */
REGION void tsl9_resident_transmit_handlers_block_5995c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3850\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 326(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    a2 = a2 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59966:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59966\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5972a\n");
    __builtin_unreachable();
}

/* Original0x59968..0x5996E. */
REGION void tsl9_resident_transmit_handlers_block_59968(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_5996a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_5996a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_560d4\n");
    __builtin_unreachable();
}

/* Original0x5996E..0x59972. */
REGION void tsl9_resident_transmit_handlers_block_5996e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_5996e:\n.option push\n.option norvc\nbnez a0,.Lresident_transmit_handlers_edge_5996e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x59972..0x59978. */
REGION void tsl9_resident_transmit_handlers_block_59972(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59974:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59974\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_56086\n");
    __builtin_unreachable();
}

/* Original0x59978..0x59980. */
REGION void tsl9_resident_transmit_handlers_block_59978(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5997e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_5997e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_599c2\n");
    __builtin_unreachable();
}

/* Original0x59980..0x59984. */
REGION void tsl9_resident_transmit_handlers_block_59980(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 22(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2878\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59982:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59982\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_599c2\n");
    __builtin_unreachable();
}

/* Original0x59984..0x5998C. */
REGION void tsl9_resident_transmit_handlers_block_59984(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3874\n.option pop\n");
    a4 = UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59988:\n.option push\n.option norvc\nbltu a4,a3,.Lresident_transmit_handlers_edge_59988\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_5999c\n");
    __builtin_unreachable();
}

/* Original0x5998C..0x5999C. */
REGION void tsl9_resident_transmit_handlers_block_5998c(void)
{
    REGS;
    a4 = UINT32_C(0x00022000); LIVE;
    a4 = a4 + UINT32_C(0x00000064); LIVE;
    PORT(".option push\n.option norvc\nsrl a4, a4, a3\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_5999a:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_5999a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_599c2\n");
    __builtin_unreachable();
}

/* Original0x5999C..0x599AA. */
REGION void tsl9_resident_transmit_handlers_block_5999c(void)
{
    REGS;
    a5 = UINT32_C(0x0000003d); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000027); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x599AA..0x599B4. */
REGION void tsl9_resident_transmit_handlers_block_599aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_599b0:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_599b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x599B4..0x599BA. */
REGION void tsl9_resident_transmit_handlers_block_599b4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 22(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x287c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_599b6:\n.option push\n.option norvc\nbeqz a5,.Lresident_transmit_handlers_edge_599b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x599BA..0x599C0. */
REGION void tsl9_resident_transmit_handlers_block_599ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_599bc:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_599bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_56146\n");
    __builtin_unreachable();
}

/* Original0x599C0..0x599C2. */
REGION void tsl9_resident_transmit_handlers_block_599c0(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_599c0:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_599c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x599C2..0x599CA. */
REGION void tsl9_resident_transmit_handlers_block_599c2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3454\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_transmit_handlers_edge_599c6:\n.option push\n.option norvc\nbne a3,a4,.Lresident_transmit_handlers_edge_599c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_599fc\n");
    __builtin_unreachable();
}

/* Original0x599CA..0x599D4. */
REGION void tsl9_resident_transmit_handlers_block_599ca(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x387c\n.option pop\n");
    a4 = UINT32_C(0x0000002a); LIVE;
    PORT(".Lresident_transmit_handlers_edge_599d0:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_transmit_handlers_edge_599d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_599ee\n");
    __builtin_unreachable();
}

/* Original0x599D4..0x599DC. */
REGION void tsl9_resident_transmit_handlers_block_599d4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x387c\n.option pop\n");
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_transmit_handlers_edge_599d8:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_transmit_handlers_edge_599d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_599aa\n");
    __builtin_unreachable();
}

/* Original0x599DC..0x599EE. */
REGION void tsl9_resident_transmit_handlers_block_599dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 45(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 168(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 168(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_599ec:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_599ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_599aa\n");
    __builtin_unreachable();
}

/* Original0x599EE..0x599F8. */
REGION void tsl9_resident_transmit_handlers_block_599ee(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s6\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x599F8..0x599FA. */
REGION void tsl9_resident_transmit_handlers_block_599f8(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_599f8:\n.option push\n.option rvc\nc.bnez a0,.Lresident_transmit_handlers_edge_599f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_599d4\n");
    __builtin_unreachable();
}

/* Original0x599FA..0x599FC. */
REGION void tsl9_resident_transmit_handlers_block_599fa(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_599fa:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_599fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_599aa\n");
    __builtin_unreachable();
}

/* Original0x599FC..0x59A00. */
REGION void tsl9_resident_transmit_handlers_block_599fc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3838\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_599fe:\n.option push\n.option rvc\nc.bnez a4,.Lresident_transmit_handlers_edge_599fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59a36\n");
    __builtin_unreachable();
}

/* Original0x59A00..0x59A08. */
REGION void tsl9_resident_transmit_handlers_block_59a00(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2818\n.option pop\n");
    a3 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a04:\n.option push\n.option norvc\nbne a4,a3,.Lresident_transmit_handlers_edge_59a04\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59a14\n");
    __builtin_unreachable();
}

/* Original0x59A08..0x59A0C. */
REGION void tsl9_resident_transmit_handlers_block_59a08(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x59A0C..0x59A0E. */
REGION void tsl9_resident_transmit_handlers_block_59a0c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59A0E..0x59A14. */
REGION void tsl9_resident_transmit_handlers_block_59a0e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a12:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59a12\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a36\n");
    __builtin_unreachable();
}

/* Original0x59A14..0x59A1A. */
REGION void tsl9_resident_transmit_handlers_block_59a14(void)
{
    REGS;
    a3 = UINT32_C(0x00000015); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a16:\n.option push\n.option norvc\nbne a4,a3,.Lresident_transmit_handlers_edge_59a16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59a20\n");
    __builtin_unreachable();
}

/* Original0x59A1A..0x59A20. */
REGION void tsl9_resident_transmit_handlers_block_59a1a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a1e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59a1e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a0c\n");
    __builtin_unreachable();
}

/* Original0x59A20..0x59A26. */
REGION void tsl9_resident_transmit_handlers_block_59a20(void)
{
    REGS;
    a3 = UINT32_C(0x0000001c); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a22:\n.option push\n.option norvc\nbne a4,a3,.Lresident_transmit_handlers_edge_59a22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59a4a\n");
    __builtin_unreachable();
}

/* Original0x59A26..0x59A36. */
REGION void tsl9_resident_transmit_handlers_block_59a26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 16(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59A36..0x59A3A. */
REGION void tsl9_resident_transmit_handlers_block_59a36(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 22(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x287c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a38:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59a38\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_599aa\n");
    __builtin_unreachable();
}

/* Original0x59A3A..0x59A44. */
REGION void tsl9_resident_transmit_handlers_block_59a3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_literal_59a3c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_20000bc0\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_59a3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59A44..0x59A48. */
REGION void tsl9_resident_transmit_handlers_block_59a44(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59a44:\n.option push\n.option norvc\nbnez a0,.Lresident_transmit_handlers_edge_59a44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x59A48..0x59A4A. */
REGION void tsl9_resident_transmit_handlers_block_59a48(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59a48:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59a48\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_599aa\n");
    __builtin_unreachable();
}

/* Original0x59A4A..0x59A52. */
REGION void tsl9_resident_transmit_handlers_block_59a4a(void)
{
    REGS;
    a3 = UINT32_C(0x00000059); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a4e:\n.option push\n.option norvc\nbne a4,a3,.Lresident_transmit_handlers_edge_59a4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59aea\n");
    __builtin_unreachable();
}

/* Original0x59A52..0x59A58. */
REGION void tsl9_resident_transmit_handlers_block_59a52(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 330(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a56:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59a56\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59a66\n");
    __builtin_unreachable();
}

/* Original0x59A58..0x59A66. */
REGION void tsl9_resident_transmit_handlers_block_59a58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 326(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a3, a3, a2\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a62:\n.option push\n.option norvc\nbne a4,a3,.Lresident_transmit_handlers_edge_59a62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59a7a\n");
    __builtin_unreachable();
}

/* Original0x59A66..0x59A6C. */
REGION void tsl9_resident_transmit_handlers_block_59a66(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 331(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a6a:\n.option push\n.option rvc\nc.beqz a2,.Lresident_transmit_handlers_edge_59a6a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59aa4\n");
    __builtin_unreachable();
}

/* Original0x59A6C..0x59A7A. */
REGION void tsl9_resident_transmit_handlers_block_59a6c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 327(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a3, a3, a1\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a76:\n.option push\n.option norvc\nbeq a2,a3,.Lresident_transmit_handlers_edge_59a76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59aa4\n");
    __builtin_unreachable();
}

/* Original0x59A7A..0x59A80. */
REGION void tsl9_resident_transmit_handlers_block_59a7a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59A80..0x59A82. */
REGION void tsl9_resident_transmit_handlers_block_59a80(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59a80:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59a80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59a0e\n");
    __builtin_unreachable();
}

/* Original0x59A82..0x59A8C. */
REGION void tsl9_resident_transmit_handlers_block_59a82(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nlhu a5, 486(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59a8a:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_handlers_edge_59a8a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59ad8\n");
    __builtin_unreachable();
}

/* Original0x59A8C..0x59A96. */
REGION void tsl9_resident_transmit_handlers_block_59a8c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 328(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffe88); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59a94:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59a94\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59ab6\n");
    __builtin_unreachable();
}

/* Original0x59A96..0x59AA0. */
REGION void tsl9_resident_transmit_handlers_block_59a96(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    __builtin_unreachable();
}

/* Original0x59AA0..0x59AA4. */
REGION void tsl9_resident_transmit_handlers_block_59aa0(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59aa2:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59aa2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59ac0\n");
    __builtin_unreachable();
}

/* Original0x59AA4..0x59AA8. */
REGION void tsl9_resident_transmit_handlers_block_59aa4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 30(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c7c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59aa6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59aa6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59a80\n");
    __builtin_unreachable();
}

/* Original0x59AA8..0x59AB6. */
REGION void tsl9_resident_transmit_handlers_block_59aa8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000200); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59ab4:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59ab4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a80\n");
    __builtin_unreachable();
}

/* Original0x59AB6..0x59AC0. */
REGION void tsl9_resident_transmit_handlers_block_59ab6(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    __builtin_unreachable();
}

/* Original0x59AC0..0x59AD0. */
REGION void tsl9_resident_transmit_handlers_block_59ac0(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 484(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59acc:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_transmit_handlers_edge_59acc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59ad2\n");
    __builtin_unreachable();
}

/* Original0x59AD0..0x59AD2. */
REGION void tsl9_resident_transmit_handlers_block_59ad0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59AD2..0x59AD8. */
REGION void tsl9_resident_transmit_handlers_block_59ad2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a4, 78(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59ad6:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59ad6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a0e\n");
    __builtin_unreachable();
}

/* Original0x59AD8..0x59ADC. */
REGION void tsl9_resident_transmit_handlers_block_59ad8(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59ada:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59ada\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59ae2\n");
    __builtin_unreachable();
}

/* Original0x59ADC..0x59AE2. */
REGION void tsl9_resident_transmit_handlers_block_59adc(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffb0); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59ae0:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59ae0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59aa0\n");
    __builtin_unreachable();
}

/* Original0x59AE2..0x59AEA. */
REGION void tsl9_resident_transmit_handlers_block_59ae2(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffbc); LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59ae8:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59ae8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59ac0\n");
    __builtin_unreachable();
}

/* Original0x59AEA..0x59AF2. */
REGION void tsl9_resident_transmit_handlers_block_59aea(void)
{
    REGS;
    a5 = UINT32_C(0x00000067); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59aee:\n.option push\n.option norvc\nbne a4,a5,.Lresident_transmit_handlers_edge_59aee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59b1a\n");
    __builtin_unreachable();
}

/* Original0x59AF2..0x59B1A. */
REGION void tsl9_resident_transmit_handlers_block_59af2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 10(s1)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    a4 = UINT32_C(0x40022000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000048)); LIVE;
    a5 = a5 & UINT32_C(0x000000fd); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000048)) = (uint8_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x245c\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59b18:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59b18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a0e\n");
    __builtin_unreachable();
}

/* Original0x59B1A..0x59B22. */
REGION void tsl9_resident_transmit_handlers_block_59b1a(void)
{
    REGS;
    a5 = UINT32_C(0x00000095); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59b1e:\n.option push\n.option norvc\nbne a4,a5,.Lresident_transmit_handlers_edge_59b1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59a36\n");
    __builtin_unreachable();
}

/* Original0x59B22..0x59B30. */
REGION void tsl9_resident_transmit_handlers_block_59b22(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 398(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 398(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59b2e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59b2e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59a0e\n");
    __builtin_unreachable();
}

/* Original0x59B30..0x59B42. */
REGION void tsl9_resident_transmit_handlers_block_59b30(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 24(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c1c\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 24(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac1c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 14(s2)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 14(s2)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59b40:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59b40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59876\n");
    __builtin_unreachable();
}

/* Original0x59B42..0x59B76. */
REGION void tsl9_resident_transmit_handlers_block_59b42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59b74:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59b74\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_598e2\n");
    __builtin_unreachable();
}

/* Original0x59B76..0x59B7A. */
REGION void tsl9_resident_transmit_handlers_block_59b76(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59b76:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59b76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x59B7A..0x59B84. */
REGION void tsl9_resident_transmit_handlers_block_59b7a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59b82:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_handlers_edge_59b82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bbe\n");
    __builtin_unreachable();
}

/* Original0x59B84..0x59B8A. */
REGION void tsl9_resident_transmit_handlers_block_59b84(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59b88:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59b88\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bbe\n");
    __builtin_unreachable();
}

/* Original0x59B8A..0x59B90. */
REGION void tsl9_resident_transmit_handlers_block_59b8a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3478\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59b8e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_handlers_edge_59b8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bbe\n");
    __builtin_unreachable();
}

/* Original0x59B90..0x59B9E. */
REGION void tsl9_resident_transmit_handlers_block_59b90(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x278c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59b9a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59b9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_6a722\n");
    __builtin_unreachable();
}

/* Original0x59B9E..0x59BA0. */
REGION void tsl9_resident_transmit_handlers_block_59b9e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59b9e:\n.option push\n.option rvc\nc.bnez a0,.Lresident_transmit_handlers_edge_59b9e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bbe\n");
    __builtin_unreachable();
}

/* Original0x59BA0..0x59BB8. */
REGION void tsl9_resident_transmit_handlers_block_59ba0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27ba\n.option pop\n");
    a4 = a4 | UINT32_C(0xffffff00); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7ba\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 288(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 66(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bb6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59bb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bbe\n");
    __builtin_unreachable();
}

/* Original0x59BB8..0x59BBE. */
REGION void tsl9_resident_transmit_handlers_block_59bb8(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 66(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59BBE..0x59BC4. */
REGION void tsl9_resident_transmit_handlers_block_59bbe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bc0:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59bc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_56d0e\n");
    __builtin_unreachable();
}

/* Original0x59BC4..0x59BC8. */
REGION void tsl9_resident_transmit_handlers_block_59bc4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c1c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bc6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59bc6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bee\n");
    __builtin_unreachable();
}

/* Original0x59BC8..0x59BCE. */
REGION void tsl9_resident_transmit_handlers_block_59bc8(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x000000f0); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59bcc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59bcc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bdc\n");
    __builtin_unreachable();
}

/* Original0x59BCE..0x59BD8. */
REGION void tsl9_resident_transmit_handlers_block_59bce(void)
{
    REGS;
    a1 = UINT32_C(0x0000003d); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bd4:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59bd4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x59BD8..0x59BDC. */
REGION void tsl9_resident_transmit_handlers_block_59bd8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59BDC..0x59BE6. */
REGION void tsl9_resident_transmit_handlers_block_59bdc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59be4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59be4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bee\n");
    __builtin_unreachable();
}

/* Original0x59BE6..0x59BEE. */
REGION void tsl9_resident_transmit_handlers_block_59be6(void)
{
    REGS;
    a1 = UINT32_C(0x00000005); LIVE;
    a0 = UINT32_C(0x00000086); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59BEE..0x59BF2. */
REGION void tsl9_resident_transmit_handlers_block_59bee(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 24(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c1c\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bf0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59bf0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bfe\n");
    __builtin_unreachable();
}

/* Original0x59BF2..0x59BF8. */
REGION void tsl9_resident_transmit_handlers_block_59bf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 82(s2)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bf6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59bf6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59bfe\n");
    __builtin_unreachable();
}

/* Original0x59BF8..0x59BFE. */
REGION void tsl9_resident_transmit_handlers_block_59bf8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59bfa:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59bfa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_58f14\n");
    __builtin_unreachable();
}

/* Original0x59BFE..0x59C18. */
REGION void tsl9_resident_transmit_handlers_block_59bfe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c14:\n.option push\n.option norvc\njal zero,.Lresident_transmit_handlers_edge_59c14\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_567be\n");
    __builtin_unreachable();
}

/* Original0x59C18..0x59C22. */
REGION void tsl9_resident_transmit_handlers_block_59c18(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59c1e:\n.option push\n.option norvc\nbnez a5,.Lresident_transmit_handlers_edge_59c1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_595fc\n");
    __builtin_unreachable();
}

/* Original0x59C22..0x59C26. */
REGION void tsl9_resident_transmit_handlers_block_59c22(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59c22:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x59C26..0x59C30. */
REGION void tsl9_resident_transmit_handlers_block_59c26(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c2c:\n.option push\n.option norvc\nbgez a5,.Lresident_transmit_handlers_edge_59c2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59c3a\n");
    __builtin_unreachable();
}

/* Original0x59C30..0x59C3A. */
REGION void tsl9_resident_transmit_handlers_block_59c30(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 18(s2)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 18(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59C3A..0x59C40. */
REGION void tsl9_resident_transmit_handlers_block_59c3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c3c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c3c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_56d0e\n");
    __builtin_unreachable();
}

/* Original0x59C40..0x59C4A. */
REGION void tsl9_resident_transmit_handlers_block_59c40(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c46:\n.option push\n.option norvc\nbgez a5,.Lresident_transmit_handlers_edge_59c46\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_59bfe\n");
    __builtin_unreachable();
}

/* Original0x59C4A..0x59C4E. */
REGION void tsl9_resident_transmit_handlers_block_59c4a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59c4a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43edc\n");
    __builtin_unreachable();
}

/* Original0x59C4E..0x59C50. */
REGION void tsl9_resident_transmit_handlers_block_59c4e(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59c4e:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59c4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59bf2\n");
    __builtin_unreachable();
}

/* Original0x59C50..0x59C58. */
REGION void tsl9_resident_transmit_handlers_block_59c50(void)
{
    REGS;
    a4 = UINT32_C(0x000000c3); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59c54:\n.option push\n.option norvc\nbne a5,a4,.Lresident_transmit_handlers_edge_59c54\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_596cc\n");
    __builtin_unreachable();
}

/* Original0x59C58..0x59C5E. */
REGION void tsl9_resident_transmit_handlers_block_59c58(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59c5c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59c5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59d32\n");
    __builtin_unreachable();
}

/* Original0x59C5E..0x59C6A. */
REGION void tsl9_resident_transmit_handlers_block_59c5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59c68:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59c68\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59c8c\n");
    __builtin_unreachable();
}

/* Original0x59C6A..0x59C6E. */
REGION void tsl9_resident_transmit_handlers_block_59c6a(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59c6a:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c6a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x59C6E..0x59C76. */
REGION void tsl9_resident_transmit_handlers_block_59c6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 39(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c72:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x59C76..0x59C86. */
REGION void tsl9_resident_transmit_handlers_block_59c76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 84(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 39(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c82:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c82\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x59C86..0x59C8C. */
REGION void tsl9_resident_transmit_handlers_block_59c86(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    PORT(".Lresident_transmit_handlers_edge_59c8a:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59c8a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59bfe\n");
    __builtin_unreachable();
}

/* Original0x59C8C..0x59CA2. */
REGION void tsl9_resident_transmit_handlers_block_59c8c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 480(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a2, 482(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 327(s0)\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59c9e:\n.option push\n.option norvc\njal ra,.Lresident_transmit_handlers_edge_59c9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x59CA2..0x59CAE. */
REGION void tsl9_resident_transmit_handlers_block_59ca2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s7, 0x20003\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59cac:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_handlers_edge_59cac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_handlers_block_59d02\n");
    __builtin_unreachable();
}

/* Original0x59CAE..0x59CBA. */
REGION void tsl9_resident_transmit_handlers_block_59cae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_transmit_handlers_literal_59cb2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_unprovided_ram_2000249a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_handlers_literal_59cb2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59CBA..0x59CE8. */
REGION void tsl9_resident_transmit_handlers_block_59cba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s7)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000079); LIVE;
    __builtin_unreachable();
}

/* Original0x59CE8..0x59D02. */
REGION void tsl9_resident_transmit_handlers_block_59ce8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a2, 480(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    a5 = UINT32_C(0xffffffc4); LIVE;
    a2 = a2 + UINT32_C(0x00000004); LIVE;
    a2 = a2 << UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    a2 = a2 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 327(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59d00:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59d00\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_5972a\n");
    __builtin_unreachable();
}

/* Original0x59D02..0x59D32. */
REGION void tsl9_resident_transmit_handlers_block_59d02(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s4)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s7)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000059); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59d30:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59d30\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_59ce8\n");
    __builtin_unreachable();
}

/* Original0x59D32..0x59D3C. */
REGION void tsl9_resident_transmit_handlers_block_59d32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_transmit_handlers_edge_59d38:\n.option push\n.option norvc\nbnez a5,.Lresident_transmit_handlers_edge_59d38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_handlers_block_595fc\n");
    __builtin_unreachable();
}

/* Original0x59D3C..0x59D3E. */
REGION void tsl9_resident_transmit_handlers_block_59d3c(void)
{
    REGS;
    PORT(".Lresident_transmit_handlers_edge_59d3c:\n.option push\n.option rvc\nc.j .Lresident_transmit_handlers_edge_59d3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_handlers_block_596cc\n");
    __builtin_unreachable();
}
