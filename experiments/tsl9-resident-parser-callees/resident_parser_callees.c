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

/* Sixteen complete conditional SDK parser-callee/lookup/event bodies:2492B/940i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x52418..0x52440. */
REGION void tsl9_candidate_external_flash_52418(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a0\n.option pop\n");
    a0 = UINT32_C(0x00000031); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nmv s4, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a5\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_52438:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_52438\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x52440..0x52442. */
REGION void tsl9_resident_parser_callees_block_52440(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_52440:\n.option push\n.option rvc\nc.beqz a0,.Lresident_parser_callees_edge_52440\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5249e\n");
    __builtin_unreachable();
}

/* Original0x52442..0x5246A. */
REGION void tsl9_resident_parser_callees_block_52442(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a2 = UINT32_C(0x01024000); LIVE;
    a5 = a0 + UINT32_C(0x00000008); LIVE;
    a2 = a2 + UINT32_C(0xfffffe91); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option norvc\nsb s5, 8(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a1, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb50c\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s4\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_parser_callees_literal_52462:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_52462\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5246A..0x5247C. */
REGION void tsl9_resident_parser_callees_block_5246a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s1, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa804\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 17\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_52474:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_52474\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5247C..0x5249E. */
REGION void tsl9_resident_parser_callees_block_5247c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s2, 48(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003ac)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5249a:\n.option push\n.option norvc\njal zero,.Lresident_parser_callees_edge_5249a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x5249E..0x524B0. */
REGION void tsl9_resident_parser_callees_block_5249e(void)
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

/* Original0x527FA..0x52826. */
REGION void tsl9_candidate_external_flash_527fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s7, a0\n.option pop\n");
    a0 = UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s8, a5\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5281e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5281e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x52826..0x52828. */
REGION void tsl9_resident_parser_callees_block_52826(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_52826:\n.option push\n.option rvc\nc.beqz a0,.Lresident_parser_callees_edge_52826\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5289e\n");
    __builtin_unreachable();
}

/* Original0x52828..0x5283C. */
REGION void tsl9_resident_parser_callees_block_52828(void)
{
    REGS;
    a4 = UINT32_C(0x010b4000); LIVE;
    a4 = a4 + UINT32_C(0xfffffe91); LIVE;
    PORT(".option push\n.option norvc\naddi s0, a0, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 4(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5283C..0x52854. */
REGION void tsl9_resident_parser_callees_block_5283c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s7, 0(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s6, 1(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5284c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5284c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x52854..0x52868. */
REGION void tsl9_resident_parser_callees_block_52854(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 9\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s4, 8(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_52860:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_52860\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x52868..0x5287A. */
REGION void tsl9_resident_parser_callees_block_52868(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s8, 15(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30b8\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s2, s2, 255\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s0, s0, 16\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_52876:\n.option push\n.option norvc\nbltu s2,a4,.Lresident_parser_callees_edge_52876\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5283c\n");
    __builtin_unreachable();
}

/* Original0x5287A..0x5289E. */
REGION void tsl9_resident_parser_callees_block_5287a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003ac)); LIVE;
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5289a:\n.option push\n.option norvc\njal zero,.Lresident_parser_callees_edge_5289a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x5289E..0x528B6. */
REGION void tsl9_resident_parser_callees_block_5289e(void)
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
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E4B0..0x5E4E2. */
REGION void tsl9_candidate_external_flash_5e4b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31bc\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sbsp a5, 15(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x87dc\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 4(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21dc\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 16\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sbsp a5, 14(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x875c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 5(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31dc\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sbsp a5, 13(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x86dc\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint32_t)0; LIVE;
    PORT(".Lresident_parser_callees_literal_5e4da:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_200022be\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5e4da\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E4E2..0x5E4EE. */
REGION void tsl9_resident_parser_callees_block_5e4e2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001f)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_parser_callees_edge_5e4ea:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5e4ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5e506\n");
    __builtin_unreachable();
}

/* Original0x5E4EE..0x5E4FA. */
REGION void tsl9_resident_parser_callees_block_5e4ee(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001e)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x301c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_parser_callees_edge_5e4f6:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5e4f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5e506\n");
    __builtin_unreachable();
}

/* Original0x5E4FA..0x5E506. */
REGION void tsl9_resident_parser_callees_block_5e4fa(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001d)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203c\n.option pop\n");
    a0 = a0 - a5; LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x5E506..0x5E50E. */
REGION void tsl9_resident_parser_callees_block_5e506(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E950..0x5E960. */
REGION void tsl9_candidate_external_flash_5e950(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000005c)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e95e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5e95e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9c6\n");
    __builtin_unreachable();
}

/* Original0x5E960..0x5E972. */
REGION void tsl9_resident_parser_callees_block_5e960(void)
{
    REGS;
    a1 = a0 + UINT32_C(0x0000005e); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a0 = a0 + UINT32_C(0x0000004e); LIVE;
    PORT(".Lresident_parser_callees_literal_5e96a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5e96a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E972..0x5E976. */
REGION void tsl9_resident_parser_callees_block_5e972(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e974:\n.option push\n.option rvc\nc.bnez a0,.Lresident_parser_callees_edge_5e974\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9c6\n");
    __builtin_unreachable();
}

/* Original0x5E976..0x5E97C. */
REGION void tsl9_resident_parser_callees_block_5e976(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x281c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5e97a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5e97a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9da\n");
    __builtin_unreachable();
}

/* Original0x5E97C..0x5E986. */
REGION void tsl9_resident_parser_callees_block_5e97c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_parser_callees_edge_5e984:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5e984\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9bc\n");
    __builtin_unreachable();
}

/* Original0x5E986..0x5E98C. */
REGION void tsl9_resident_parser_callees_block_5e986(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 93(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e98a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5e98a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9bc\n");
    __builtin_unreachable();
}

/* Original0x5E98C..0x5E99C. */
REGION void tsl9_resident_parser_callees_block_5e98c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 99(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_parser_callees_edge_5e998:\n.option push\n.option norvc\nbne a5,a4,.Lresident_parser_callees_edge_5e998\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5e9bc\n");
    __builtin_unreachable();
}

/* Original0x5E99C..0x5E9A8. */
REGION void tsl9_resident_parser_callees_block_5e99c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 92\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5e9a0:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_200020b6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5e9a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E9A8..0x5E9AC. */
REGION void tsl9_resident_parser_callees_block_5e9a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 100(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e9aa:\n.option push\n.option rvc\nc.beqz a0,.Lresident_parser_callees_edge_5e9aa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9bc\n");
    __builtin_unreachable();
}

/* Original0x5E9AC..0x5E9BC. */
REGION void tsl9_resident_parser_callees_block_5e9ac(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 92(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 77(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5e9ba:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5e9ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ea0c\n");
    __builtin_unreachable();
}

/* Original0x5E9BC..0x5E9C6. */
REGION void tsl9_resident_parser_callees_block_5e9bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 92(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5e9c2:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5e9c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5e9ce\n");
    __builtin_unreachable();
}

/* Original0x5E9C6..0x5E9CC. */
REGION void tsl9_resident_parser_callees_block_5e9c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 84(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e9ca:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5e9ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ea12\n");
    __builtin_unreachable();
}

/* Original0x5E9CC..0x5E9CE. */
REGION void tsl9_resident_parser_callees_block_5e9cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E9CE..0x5E9DA. */
REGION void tsl9_resident_parser_callees_block_5e9ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E9DA..0x5E9E0. */
REGION void tsl9_resident_parser_callees_block_5e9da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 93(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5e9de:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5e9de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9ce\n");
    __builtin_unreachable();
}

/* Original0x5E9E0..0x5E9F0. */
REGION void tsl9_resident_parser_callees_block_5e9e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 99(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_parser_callees_edge_5e9ec:\n.option push\n.option norvc\nbne a5,a4,.Lresident_parser_callees_edge_5e9ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5e9ce\n");
    __builtin_unreachable();
}

/* Original0x5E9F0..0x5E9FA. */
REGION void tsl9_resident_parser_callees_block_5e9f0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_parser_callees_edge_5e9f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5e9f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9c6\n");
    __builtin_unreachable();
}

/* Original0x5E9FA..0x5EA06. */
REGION void tsl9_resident_parser_callees_block_5e9fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 92\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5e9fe:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_200020b6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5e9fe\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EA06..0x5EA0C. */
REGION void tsl9_resident_parser_callees_block_5ea06(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 100(s0)\n.option pop\n");
    a5 = UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_parser_callees_edge_5ea0a:\n.option push\n.option rvc\nc.bnez a0,.Lresident_parser_callees_edge_5ea0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9ac\n");
    __builtin_unreachable();
}

/* Original0x5EA0C..0x5EA12. */
REGION void tsl9_resident_parser_callees_block_5ea0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 93(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea10:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ea10\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5e9c6\n");
    __builtin_unreachable();
}

/* Original0x5EA12..0x5EA1C. */
REGION void tsl9_resident_parser_callees_block_5ea12(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b9)); LIVE;
    PORT(".Lresident_parser_callees_edge_5ea1a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ea1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9cc\n");
    __builtin_unreachable();
}

/* Original0x5EA1C..0x5EA26. */
REGION void tsl9_resident_parser_callees_block_5ea1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 84\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea24:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ea24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ea76\n");
    __builtin_unreachable();
}

/* Original0x5EA26..0x5EA36. */
REGION void tsl9_resident_parser_callees_block_5ea26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 91(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_parser_callees_edge_5ea32:\n.option push\n.option norvc\nbne a5,a4,.Lresident_parser_callees_edge_5ea32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ea76\n");
    __builtin_unreachable();
}

/* Original0x5EA36..0x5EA3E. */
REGION void tsl9_resident_parser_callees_block_5ea36(void)
{
    REGS;
    PORT(".Lresident_parser_callees_literal_5ea36:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002078\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ea36\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EA3E..0x5EA42. */
REGION void tsl9_resident_parser_callees_block_5ea3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 100(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea40:\n.option push\n.option rvc\nc.beqz a0,.Lresident_parser_callees_edge_5ea40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9cc\n");
    __builtin_unreachable();
}

/* Original0x5EA42..0x5EA54. */
REGION void tsl9_resident_parser_callees_block_5ea42(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, s0, 86\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a0 = a0 + UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_parser_callees_literal_5ea4c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ea4c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EA54..0x5EA74. */
REGION void tsl9_resident_parser_callees_block_5ea54(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a1, 100(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31bc\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 85(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5ea6c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ea6c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EA74..0x5EA76. */
REGION void tsl9_resident_parser_callees_block_5ea74(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ea74:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ea74\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5e9cc\n");
    __builtin_unreachable();
}

/* Original0x5EA76..0x5EA7E. */
REGION void tsl9_resident_parser_callees_block_5ea76(void)
{
    REGS;
    PORT(".Lresident_parser_callees_literal_5ea76:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_2000202c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ea76\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EA7E..0x5EA82. */
REGION void tsl9_resident_parser_callees_block_5ea7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 100(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea80:\n.option push\n.option rvc\nc.beqz a0,.Lresident_parser_callees_edge_5ea80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9cc\n");
    __builtin_unreachable();
}

/* Original0x5EA82..0x5EA8C. */
REGION void tsl9_resident_parser_callees_block_5ea82(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 18(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x293c\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea8a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ea8a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5e9cc\n");
    __builtin_unreachable();
}

/* Original0x5EA8C..0x5EA9A. */
REGION void tsl9_resident_parser_callees_block_5ea8c(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 84(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu s1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3104\n.option pop\n");
    PORT(".option push\n.option norvc\nsnez s1, s1\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ea98:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ea98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5e9ce\n");
    __builtin_unreachable();
}

/* Original0x5EA9A..0x5EAA0. */
REGION void tsl9_candidate_external_flash_5ea9a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000054)); LIVE;
    PORT(".Lresident_parser_callees_edge_5ea9e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_parser_callees_edge_5ea9e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5eac4\n");
    __builtin_unreachable();
}

/* Original0x5EAA0..0x5EAAA. */
REGION void tsl9_resident_parser_callees_block_5eaa0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2918\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5eaa8:\n.option push\n.option rvc\nc.beqz a4,.Lresident_parser_callees_edge_5eaa8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5eac8\n");
    __builtin_unreachable();
}

/* Original0x5EAAA..0x5EABA. */
REGION void tsl9_resident_parser_callees_block_5eaaa(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000054)); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5eab2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002276\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5eab2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EABA..0x5EAC4. */
REGION void tsl9_resident_parser_callees_block_5eaba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EAC4..0x5EAC8. */
REGION void tsl9_resident_parser_callees_block_5eac4(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EAC8..0x5EACA. */
REGION void tsl9_resident_parser_callees_block_5eac8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EACA..0x5EAD6. */
REGION void tsl9_candidate_external_flash_5eaca(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 18(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x293c\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ead4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ead4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5eb3a\n");
    __builtin_unreachable();
}

/* Original0x5EAD6..0x5EAE2. */
REGION void tsl9_resident_parser_callees_block_5ead6(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000042)); LIVE;
    PORT(".Lresident_parser_callees_edge_5eade:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_parser_callees_edge_5eade\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eb3a\n");
    __builtin_unreachable();
}

/* Original0x5EAE2..0x5EAEA. */
REGION void tsl9_resident_parser_callees_block_5eae2(void)
{
    REGS;
    PORT(".Lresident_parser_callees_literal_5eae2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_200020f4\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5eae2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EAEA..0x5EAF0. */
REGION void tsl9_resident_parser_callees_block_5eaea(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5eaec:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_parser_callees_edge_5eaec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eafa\n");
    __builtin_unreachable();
}

/* Original0x5EAF0..0x5EAF2. */
REGION void tsl9_resident_parser_callees_block_5eaf0(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x5EAF2..0x5EAFA. */
REGION void tsl9_resident_parser_callees_block_5eaf2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EAFA..0x5EB04. */
REGION void tsl9_resident_parser_callees_block_5eafa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x345c\n.option pop\n");
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nlw a0, 72(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5eb00:\n.option push\n.option norvc\nbne a5,a4,.Lresident_parser_callees_edge_5eb00\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eb08\n");
    __builtin_unreachable();
}

/* Original0x5EB04..0x5EB08. */
REGION void tsl9_resident_parser_callees_block_5eb04(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB08..0x5EB2A. */
REGION void tsl9_resident_parser_callees_block_5eb08(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa15c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 86\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 5(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb15c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 42(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x343e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 8(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa51e\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_5eb22:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5eb22\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB2A..0x5EB3A. */
REGION void tsl9_resident_parser_callees_block_5eb2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 72(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB3A..0x5EB46. */
REGION void tsl9_resident_parser_callees_block_5eb3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 28(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3448\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_parser_callees_edge_5eb42:\n.option push\n.option norvc\nbgez a4,.Lresident_parser_callees_edge_5eb42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec18\n");
    __builtin_unreachable();
}

/* Original0x5EB46..0x5EB4C. */
REGION void tsl9_resident_parser_callees_block_5eb46(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_parser_callees_edge_5eb48:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_parser_callees_edge_5eb48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eb76\n");
    __builtin_unreachable();
}

/* Original0x5EB4C..0x5EB56. */
REGION void tsl9_resident_parser_callees_block_5eb4c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    a3 = UINT32_C(0x00000025); LIVE;
    PORT(".Lresident_parser_callees_edge_5eb52:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_parser_callees_edge_5eb52\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eaf0\n");
    __builtin_unreachable();
}

/* Original0x5EB56..0x5EB58. */
REGION void tsl9_resident_parser_callees_block_5eb56(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5eb56:\n.option push\n.option rvc\nc.bnez a0,.Lresident_parser_callees_edge_5eb56\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ebe4\n");
    __builtin_unreachable();
}

/* Original0x5EB58..0x5EB5A. */
REGION void tsl9_resident_parser_callees_block_5eb58(void)
{
    REGS;
    a4 = UINT32_C(0x00000013); LIVE;
    __builtin_unreachable();
}

/* Original0x5EB5A..0x5EB5E. */
REGION void tsl9_resident_parser_callees_block_5eb5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a4, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB5E..0x5EB72. */
REGION void tsl9_resident_parser_callees_block_5eb5e(void)
{
    REGS;
    a4 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 41(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 62(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 45(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5eb6e:\n.option push\n.option norvc\nbne a0,a4,.Lresident_parser_callees_edge_5eb6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec0a\n");
    __builtin_unreachable();
}

/* Original0x5EB72..0x5EB76. */
REGION void tsl9_resident_parser_callees_block_5eb72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 46(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB76..0x5EB80. */
REGION void tsl9_resident_parser_callees_block_5eb76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu t3, 46(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli t1, 0\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5eb7c:\n.option push\n.option norvc\nbeqz t3,.Lresident_parser_callees_edge_5eb7c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eb92\n");
    __builtin_unreachable();
}

/* Original0x5EB80..0x5EB92. */
REGION void tsl9_resident_parser_callees_block_5eb80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu t1, 14(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub t1, t1, t3\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, t1, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 120(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd t1, t1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EB92..0x5EBCE. */
REGION void tsl9_resident_parser_callees_block_5eb92(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu t4, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 44(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t1, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a0, t4, 0x10\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nandi t4, t4, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, s0, 86\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 45(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a6, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu t5, 62(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a7, 21(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ebca:\n.option push\n.option norvc\nbeqz t4,.Lresident_parser_callees_edge_5ebca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec12\n");
    __builtin_unreachable();
}

/* Original0x5EBCE..0x5EBDA. */
REGION void tsl9_resident_parser_callees_block_5ebce(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi t1, s0, 94\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t1, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu t1, 93(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t1, 4(sp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EBDA..0x5EBE0. */
REGION void tsl9_resident_parser_callees_block_5ebda(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw t5, 0(sp)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ebdc:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_5ebdc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_event_wrapper_6a79e\n");
    __builtin_unreachable();
}

/* Original0x5EBE0..0x5EBE4. */
REGION void tsl9_resident_parser_callees_block_5ebe0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebe2:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ebe2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eaf2\n");
    __builtin_unreachable();
}

/* Original0x5EBE4..0x5EBEA. */
REGION void tsl9_resident_parser_callees_block_5ebe4(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebe6:\n.option push\n.option norvc\nbne a0,a3,.Lresident_parser_callees_edge_5ebe6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ebee\n");
    __builtin_unreachable();
}

/* Original0x5EBEA..0x5EBEE. */
REGION void tsl9_resident_parser_callees_block_5ebea(void)
{
    REGS;
    a4 = UINT32_C(0x00000015); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebec:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ebec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eb5a\n");
    __builtin_unreachable();
}

/* Original0x5EBEE..0x5EBF4. */
REGION void tsl9_resident_parser_callees_block_5ebee(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebf0:\n.option push\n.option norvc\nbne a0,a3,.Lresident_parser_callees_edge_5ebf0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ebf8\n");
    __builtin_unreachable();
}

/* Original0x5EBF4..0x5EBF8. */
REGION void tsl9_resident_parser_callees_block_5ebf4(void)
{
    REGS;
    a4 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebf6:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ebf6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eb5a\n");
    __builtin_unreachable();
}

/* Original0x5EBF8..0x5EBFE. */
REGION void tsl9_resident_parser_callees_block_5ebf8(void)
{
    REGS;
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_parser_callees_edge_5ebfa:\n.option push\n.option norvc\nbne a0,a3,.Lresident_parser_callees_edge_5ebfa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec02\n");
    __builtin_unreachable();
}

/* Original0x5EBFE..0x5EC02. */
REGION void tsl9_resident_parser_callees_block_5ebfe(void)
{
    REGS;
    a4 = UINT32_C(0x0000001b); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec00:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec00\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eb5a\n");
    __builtin_unreachable();
}

/* Original0x5EC02..0x5EC06. */
REGION void tsl9_resident_parser_callees_block_5ec02(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ec02:\n.option push\n.option norvc\nbne a0,a4,.Lresident_parser_callees_edge_5ec02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eb5e\n");
    __builtin_unreachable();
}

/* Original0x5EC06..0x5EC0A. */
REGION void tsl9_resident_parser_callees_block_5ec06(void)
{
    REGS;
    a4 = UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec08:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec08\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eb5a\n");
    __builtin_unreachable();
}

/* Original0x5EC0A..0x5EC12. */
REGION void tsl9_resident_parser_callees_block_5ec0a(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 46(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ec10:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec10\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5eb76\n");
    __builtin_unreachable();
}

/* Original0x5EC12..0x5EC18. */
REGION void tsl9_resident_parser_callees_block_5ec12(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    PORT(".Lresident_parser_callees_edge_5ec16:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec16\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ebda\n");
    __builtin_unreachable();
}

/* Original0x5EC18..0x5EC1E. */
REGION void tsl9_resident_parser_callees_block_5ec18(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec1a:\n.option push\n.option norvc\nbne a0,a5,.Lresident_parser_callees_edge_5ec1a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec66\n");
    __builtin_unreachable();
}

/* Original0x5EC1E..0x5EC38. */
REGION void tsl9_resident_parser_callees_block_5ec1e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000438)); LIVE;
    PORT(".option push\n.option norvc\naddi a2, s0, 86\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 85(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 16(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2b18\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a5, 21(s0)\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec36:\n.option push\n.option rvc\nc.beqz a4,.Lresident_parser_callees_edge_5ec36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ec5a\n");
    __builtin_unreachable();
}

/* Original0x5EC38..0x5EC3E. */
REGION void tsl9_resident_parser_callees_block_5ec38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 93(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ec3c:\n.option push\n.option rvc\nc.beqz a3,.Lresident_parser_callees_edge_5ec3c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ec5a\n");
    __builtin_unreachable();
}

/* Original0x5EC3E..0x5EC4E. */
REGION void tsl9_resident_parser_callees_block_5ec3e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 99(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000040); LIVE;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec4a:\n.option push\n.option norvc\nbne a4,a0,.Lresident_parser_callees_edge_5ec4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec5a\n");
    __builtin_unreachable();
}

/* Original0x5EC4E..0x5EC58. */
REGION void tsl9_resident_parser_callees_block_5ec4e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a4, s0, 94\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec54:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_5ec54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6a796\n");
    __builtin_unreachable();
}

/* Original0x5EC58..0x5EC5A. */
REGION void tsl9_resident_parser_callees_block_5ec58(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ec58:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec58\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ebe0\n");
    __builtin_unreachable();
}

/* Original0x5EC5A..0x5EC60. */
REGION void tsl9_resident_parser_callees_block_5ec5a(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x5EC60..0x5EC64. */
REGION void tsl9_resident_parser_callees_block_5ec60(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ec60:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_5ec60\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6a730\n");
    __builtin_unreachable();
}

/* Original0x5EC64..0x5EC66. */
REGION void tsl9_resident_parser_callees_block_5ec64(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ec64:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ebe0\n");
    __builtin_unreachable();
}

/* Original0x5EC66..0x5EC70. */
REGION void tsl9_resident_parser_callees_block_5ec66(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2474\n.option pop\n");
    a5 = UINT32_C(0x00000025); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec6c:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_parser_callees_edge_5ec6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5eaf0\n");
    __builtin_unreachable();
}

/* Original0x5EC70..0x5EC76. */
REGION void tsl9_resident_parser_callees_block_5ec70(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec72:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_parser_callees_edge_5ec72\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec80\n");
    __builtin_unreachable();
}

/* Original0x5EC76..0x5EC7C. */
REGION void tsl9_resident_parser_callees_block_5ec76(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec78:\n.option push\n.option norvc\nbne a0,a5,.Lresident_parser_callees_edge_5ec78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ec82\n");
    __builtin_unreachable();
}

/* Original0x5EC7C..0x5EC80. */
REGION void tsl9_resident_parser_callees_block_5ec7c(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec7e:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ec7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ec82\n");
    __builtin_unreachable();
}

/* Original0x5EC80..0x5EC82. */
REGION void tsl9_resident_parser_callees_block_5ec80(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x5EC82..0x5EC90. */
REGION void tsl9_resident_parser_callees_block_5ec82(void)
{
    REGS;
    a3 = a3 + UINT32_C(0xfffffffa); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsb a3, 46(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_parser_callees_edge_5ec8e:\n.option push\n.option rvc\nc.beqz a3,.Lresident_parser_callees_edge_5ec8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ec94\n");
    __builtin_unreachable();
}

/* Original0x5EC90..0x5EC94. */
REGION void tsl9_resident_parser_callees_block_5ec90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 120(s0)\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x5EC94..0x5ECA2. */
REGION void tsl9_resident_parser_callees_block_5ec94(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 21(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, s0, 86\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 85(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5eca0:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5eca0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ec60\n");
    __builtin_unreachable();
}

/* Original0x5ECF6..0x5ED1E. */
REGION void tsl9_candidate_external_flash_5ecf6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x0000000c); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa55c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa398\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x255c\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb31c\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004d)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004c)) = (uint8_t)0; LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed1c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ed1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed5c\n");
    __builtin_unreachable();
}

/* Original0x5ED1E..0x5ED26. */
REGION void tsl9_resident_parser_callees_block_5ed1e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000054)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed24:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ed24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed6c\n");
    __builtin_unreachable();
}

/* Original0x5ED26..0x5ED2A. */
REGION void tsl9_resident_parser_callees_block_5ed26(void)
{
    REGS;
    a1 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed28:\n.option push\n.option rvc\nc.bnez a1,.Lresident_parser_callees_edge_5ed28\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed42\n");
    __builtin_unreachable();
}

/* Original0x5ED2A..0x5ED30. */
REGION void tsl9_resident_parser_callees_block_5ed2a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a1, 100(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 18(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x29bc\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ed2e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ed2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed64\n");
    __builtin_unreachable();
}

/* Original0x5ED30..0x5ED40. */
REGION void tsl9_resident_parser_callees_block_5ed30(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 116(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000014); LIVE;
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_parser_callees_literal_5ed38:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ed38\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ED40..0x5ED42. */
REGION void tsl9_resident_parser_callees_block_5ed40(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_5ed40:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ed40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ed64\n");
    __builtin_unreachable();
}

/* Original0x5ED42..0x5ED46. */
REGION void tsl9_resident_parser_callees_block_5ed42(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25bc\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ed44:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ed44\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed2a\n");
    __builtin_unreachable();
}

/* Original0x5ED46..0x5ED5C. */
REGION void tsl9_resident_parser_callees_block_5ed46(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004c)) = (uint8_t)a5; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x0000000c); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_literal_5ed54:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ed54\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ED5C..0x5ED64. */
REGION void tsl9_resident_parser_callees_block_5ed5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 84(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed62:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5ed62\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed2a\n");
    __builtin_unreachable();
}

/* Original0x5ED64..0x5ED6C. */
REGION void tsl9_resident_parser_callees_block_5ed64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 76(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed6a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5ed6a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ed7e\n");
    __builtin_unreachable();
}

/* Original0x5ED6C..0x5ED7E. */
REGION void tsl9_resident_parser_callees_block_5ed6c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 116(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 78\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_literal_5ed76:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ed76\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ED7E..0x5ED88. */
REGION void tsl9_resident_parser_callees_block_5ed7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 84(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_parser_callees_edge_5ed84:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_parser_callees_edge_5ed84\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ed9a\n");
    __builtin_unreachable();
}

/* Original0x5ED88..0x5ED9A. */
REGION void tsl9_resident_parser_callees_block_5ed88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 116(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 86\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_parser_callees_literal_5ed92:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ed92\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ED9A..0x5EDA2. */
REGION void tsl9_resident_parser_callees_block_5ed9a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 77(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5eda0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5eda0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5edac\n");
    __builtin_unreachable();
}

/* Original0x5EDA2..0x5EDAC. */
REGION void tsl9_resident_parser_callees_block_5eda2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 76(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5eda8:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5eda8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5edb6\n");
    __builtin_unreachable();
}

/* Original0x5EDAC..0x5EDB6. */
REGION void tsl9_resident_parser_callees_block_5edac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x231c\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa31c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EDB6..0x5EDBE. */
REGION void tsl9_resident_parser_callees_block_5edb6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5edbc:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_5edbc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5edc8\n");
    __builtin_unreachable();
}

/* Original0x5EDBE..0x5EDC8. */
REGION void tsl9_resident_parser_callees_block_5edbe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 84(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_parser_callees_edge_5edc4:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5edc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5edd2\n");
    __builtin_unreachable();
}

/* Original0x5EDC8..0x5EDD2. */
REGION void tsl9_resident_parser_callees_block_5edc8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x231c\n.option pop\n");
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa31c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EDD2..0x5EDDC. */
REGION void tsl9_resident_parser_callees_block_5edd2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3458\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.lbu a1, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x244c\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5edd8:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_5edd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5edf0\n");
    __builtin_unreachable();
}

/* Original0x5EDDC..0x5EDE6. */
REGION void tsl9_resident_parser_callees_block_5eddc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 37(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffa6); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EDE6..0x5EDF0. */
REGION void tsl9_resident_parser_callees_block_5ede6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5edec:\n.option push\n.option norvc\njal zero,.Lresident_parser_callees_edge_5edec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x5EDF0..0x5EE02. */
REGION void tsl9_resident_parser_callees_block_5edf0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 33(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffa2); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_parser_callees_edge_5edfe:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_parser_callees_edge_5edfe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_5ede6\n");
    __builtin_unreachable();
}

/* Original0x5EE02..0x5EE06. */
REGION void tsl9_resident_parser_callees_block_5ee02(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_parser_callees_edge_5ee04:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ee04\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ede6\n");
    __builtin_unreachable();
}

/* Original0x5EE06..0x5EE4C. */
REGION void tsl9_candidate_external_flash_5ee06(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a5, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s1)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000514)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000200)); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 1288(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a4 = a5 << UINT32_C(0x00000019); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000002c)); LIVE;
    a3 = UINT32_C(0x82000000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a3; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ee48:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_5ee48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5ecf6\n");
    __builtin_unreachable();
}

/* Original0x5EE4C..0x5EE72. */
REGION void tsl9_resident_parser_callees_block_5ee4c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    PORT(".option push\n.option rvc\nlw a4, 116(s0)\n.option pop\n");
    a3 = UINT32_C(0x00800000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1288(s2)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_parser_callees_edge_5ee6e:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_5ee6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eaca\n");
    __builtin_unreachable();
}

/* Original0x5EE72..0x5EE7A. */
REGION void tsl9_resident_parser_callees_block_5ee72(void)
{
    REGS;
    PORT(".Lresident_parser_callees_literal_5ee72:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_5ee72\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EE7A..0x5EE80. */
REGION void tsl9_resident_parser_callees_block_5ee7a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x309c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_5ee7e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_parser_callees_edge_5ee7e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_5ee90\n");
    __builtin_unreachable();
}

/* Original0x5EE80..0x5EE84. */
REGION void tsl9_resident_parser_callees_block_5ee80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 1(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EE84..0x5EE90. */
REGION void tsl9_resident_parser_callees_block_5ee84(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EE90..0x5EE98. */
REGION void tsl9_resident_parser_callees_block_5ee90(void)
{
    REGS;
    a5 = UINT32_C(0xffffffa0); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_5ee96:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_5ee96\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_5ee84\n");
    __builtin_unreachable();
}

/* Original0x6A730..0x6A734. */
REGION void tsl9_candidate_external_flash_6a730(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_6a730:\n.option push\n.option norvc\njal zero,.Lresident_parser_callees_edge_6a730\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_52418\n");
    __builtin_unreachable();
}

/* Original0x6A796..0x6A79A. */
REGION void tsl9_candidate_external_flash_6a796(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_6a796:\n.option push\n.option norvc\njal zero,.Lresident_parser_callees_edge_6a796\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_527fa\n");
    __builtin_unreachable();
}

/* Original0x2000202C..0x20002048. */
REGION void tsl9_candidate_external_ram_2000202c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1156(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, a0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002048..0x2000204A. */
REGION void tsl9_resident_parser_callees_block_20002048(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002048:\n.option push\n.option rvc\nc.beqz s0,.Lresident_parser_callees_edge_20002048\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_20002068\n");
    __builtin_unreachable();
}

/* Original0x2000204A..0x20002054. */
REGION void tsl9_resident_parser_callees_block_2000204a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x309c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3038\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_20002050:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_parser_callees_edge_20002050\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002058\n");
    __builtin_unreachable();
}

/* Original0x20002054..0x20002058. */
REGION void tsl9_resident_parser_callees_block_20002054(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 60(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002056:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_20002056\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_20002048\n");
    __builtin_unreachable();
}

/* Original0x20002058..0x20002064. */
REGION void tsl9_resident_parser_callees_block_20002058(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002060:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_20002060\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20000442\n");
    __builtin_unreachable();
}

/* Original0x20002064..0x20002068. */
REGION void tsl9_resident_parser_callees_block_20002064(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002064:\n.option push\n.option norvc\nbne a0,s3,.Lresident_parser_callees_edge_20002064\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002054\n");
    __builtin_unreachable();
}

/* Original0x20002068..0x20002078. */
REGION void tsl9_resident_parser_callees_block_20002068(void)
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

/* Original0x20002078..0x20002090. */
REGION void tsl9_candidate_external_ram_20002078(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1156(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002090..0x20002092. */
REGION void tsl9_resident_parser_callees_block_20002090(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002090:\n.option push\n.option rvc\nc.bnez s0,.Lresident_parser_callees_edge_20002090\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_200020a0\n");
    __builtin_unreachable();
}

/* Original0x20002092..0x200020A0. */
REGION void tsl9_resident_parser_callees_block_20002092(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200020A0..0x200020AE. */
REGION void tsl9_resident_parser_callees_block_200020a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 42\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_200020a6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_5e4b0\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_200020a6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200020AE..0x200020B2. */
REGION void tsl9_resident_parser_callees_block_200020ae(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_200020ae:\n.option push\n.option norvc\nbeq a0,s2,.Lresident_parser_callees_edge_200020ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002092\n");
    __builtin_unreachable();
}

/* Original0x200020B2..0x200020B6. */
REGION void tsl9_resident_parser_callees_block_200020b2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 60(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_200020b4:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_200020b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_20002090\n");
    __builtin_unreachable();
}

/* Original0x200020B6..0x200020CE. */
REGION void tsl9_candidate_external_ram_200020b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1156(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200020CE..0x200020D0. */
REGION void tsl9_resident_parser_callees_block_200020ce(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_200020ce:\n.option push\n.option rvc\nc.bnez s0,.Lresident_parser_callees_edge_200020ce\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_200020de\n");
    __builtin_unreachable();
}

/* Original0x200020D0..0x200020DE. */
REGION void tsl9_resident_parser_callees_block_200020d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200020DE..0x200020EC. */
REGION void tsl9_resident_parser_callees_block_200020de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 26\n.option pop\n");
    PORT(".Lresident_parser_callees_literal_200020e4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_5e4b0\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_parser_callees_literal_200020e4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200020EC..0x200020F0. */
REGION void tsl9_resident_parser_callees_block_200020ec(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_200020ec:\n.option push\n.option norvc\nbeq a0,s2,.Lresident_parser_callees_edge_200020ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_200020d0\n");
    __builtin_unreachable();
}

/* Original0x200020F0..0x200020F4. */
REGION void tsl9_resident_parser_callees_block_200020f0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 60(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_200020f2:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_200020f2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_200020ce\n");
    __builtin_unreachable();
}

/* Original0x200020F4..0x2000210E. */
REGION void tsl9_candidate_external_ram_200020f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 68(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s4, 7\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, a0, 86\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000210E..0x20002114. */
REGION void tsl9_resident_parser_callees_block_2000210e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s1)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002110:\n.option push\n.option norvc\nbltu s0,a5,.Lresident_parser_callees_edge_20002110\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002118\n");
    __builtin_unreachable();
}

/* Original0x20002114..0x20002118. */
REGION void tsl9_resident_parser_callees_block_20002114(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_20002116:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_20002116\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_2000215a\n");
    __builtin_unreachable();
}

/* Original0x20002118..0x20002120. */
REGION void tsl9_resident_parser_callees_block_20002118(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 13(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x34d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 4(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x205c\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_2000211c:\n.option push\n.option norvc\nbne a4,s4,.Lresident_parser_callees_edge_2000211c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_2000216a\n");
    __builtin_unreachable();
}

/* Original0x20002120..0x20002128. */
REGION void tsl9_resident_parser_callees_block_20002120(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 40(s1)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002124:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_parser_callees_edge_20002124\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_2000212c\n");
    __builtin_unreachable();
}

/* Original0x20002128..0x2000212C. */
REGION void tsl9_resident_parser_callees_block_20002128(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 0(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_2000212a:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_2000212a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_2000210e\n");
    __builtin_unreachable();
}

/* Original0x2000212C..0x20002136. */
REGION void tsl9_resident_parser_callees_block_2000212c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 5(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3058\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 85(s1)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002132:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_20002132\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002136..0x20002142. */
REGION void tsl9_resident_parser_callees_block_20002136(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 6\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_2000213e:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_2000213e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20000442\n");
    __builtin_unreachable();
}

/* Original0x20002142..0x20002146. */
REGION void tsl9_resident_parser_callees_block_20002142(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002142:\n.option push\n.option norvc\nbne a0,s3,.Lresident_parser_callees_edge_20002142\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002146..0x20002150. */
REGION void tsl9_resident_parser_callees_block_20002146(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2458\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s1)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_2000214c:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_2000214c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002150..0x20002158. */
REGION void tsl9_resident_parser_callees_block_20002150(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 42(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x34be\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002154:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_20002154\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002158..0x2000215A. */
REGION void tsl9_resident_parser_callees_block_20002158(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x2000215A..0x2000216A. */
REGION void tsl9_resident_parser_callees_block_2000215a(void)
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

/* Original0x2000216A..0x2000216E. */
REGION void tsl9_resident_parser_callees_block_2000216a(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_2000216a:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_2000216a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x2000216E..0x20002178. */
REGION void tsl9_resident_parser_callees_block_2000216e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 5(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3058\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 85(s1)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002174:\n.option push\n.option norvc\nbne a4,a5,.Lresident_parser_callees_edge_20002174\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002178..0x20002184. */
REGION void tsl9_resident_parser_callees_block_20002178(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 6\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002180:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_20002180\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20000442\n");
    __builtin_unreachable();
}

/* Original0x20002184..0x20002188. */
REGION void tsl9_resident_parser_callees_block_20002184(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002184:\n.option push\n.option norvc\nbne a0,s3,.Lresident_parser_callees_edge_20002184\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_20002128\n");
    __builtin_unreachable();
}

/* Original0x20002188..0x2000218A. */
REGION void tsl9_resident_parser_callees_block_20002188(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_20002188:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_20002188\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_20002158\n");
    __builtin_unreachable();
}

/* Original0x20002276..0x2000228C. */
REGION void tsl9_candidate_external_ram_20002276(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1148(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000228C..0x2000228E. */
REGION void tsl9_resident_parser_callees_block_2000228c(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_2000228c:\n.option push\n.option rvc\nc.bnez s0,.Lresident_parser_callees_edge_2000228c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_2000229a\n");
    __builtin_unreachable();
}

/* Original0x2000228E..0x20002290. */
REGION void tsl9_resident_parser_callees_block_2000228e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x20002290..0x2000229A. */
REGION void tsl9_resident_parser_callees_block_20002290(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000229A..0x200022A4. */
REGION void tsl9_resident_parser_callees_block_2000229a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbusp a5, 9(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x849c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3018\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_200022a0:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_parser_callees_edge_200022a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_200022a8\n");
    __builtin_unreachable();
}

/* Original0x200022A4..0x200022A8. */
REGION void tsl9_resident_parser_callees_block_200022a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(s0)\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_200022a6:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_200022a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_2000228c\n");
    __builtin_unreachable();
}

/* Original0x200022A8..0x200022B6. */
REGION void tsl9_resident_parser_callees_block_200022a8(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, sp, 10\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 2\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_200022b2:\n.option push\n.option norvc\njal ra,.Lresident_parser_callees_edge_200022b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_ram_20000442\n");
    __builtin_unreachable();
}

/* Original0x200022B6..0x200022BA. */
REGION void tsl9_resident_parser_callees_block_200022b6(void)
{
    REGS;
    PORT(".Lresident_parser_callees_edge_200022b6:\n.option push\n.option norvc\nbne a0,s1,.Lresident_parser_callees_edge_200022b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_parser_callees_block_200022a4\n");
    __builtin_unreachable();
}

/* Original0x200022BA..0x200022BE. */
REGION void tsl9_resident_parser_callees_block_200022ba(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_200022bc:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_200022bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_20002290\n");
    __builtin_unreachable();
}

/* Original0x200022BE..0x200023AC. */
REGION void tsl9_candidate_external_ram_200022be(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a4 = UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3118\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 2(a0)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 0(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 3(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x18\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000028)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 5(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3158\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 6(a0)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 4(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 7(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x18\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3518\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 10(a0)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 8(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 11(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x18\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000030)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 13(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3558\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 14(a0)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 12(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 15(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3568\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a4 = a4 + a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000034)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3198\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21a8\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x2188\n.option pop\n");
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 3(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31a8\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a4 = a4 + a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 5(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 6(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21e8\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 4(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21c8\n.option pop\n");
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 7(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x31e8\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a4 = a4 + a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 9(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3598\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 10(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25a8\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 8(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x2588\n.option pop\n");
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 11(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x35a8\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000018); LIVE;
    a4 = a4 + a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 13(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x35d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 14(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25e8\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a4 = a4 + a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 12(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25c8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 15(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x35ec\n.option pop\n");
    a4 = a4 + a0; LIVE;
    a1 = a1 << UINT32_C(0x00000018); LIVE;
    a4 = a4 + a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x200023AC..0x200023B6. */
REGION void tsl9_resident_parser_callees_block_200023ac(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_parser_callees_edge_200023b4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_parser_callees_edge_200023b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_parser_callees_block_20002422\n");
    __builtin_unreachable();
}

/* Original0x200023B6..0x20002422. */
REGION void tsl9_resident_parser_callees_block_200023b6(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000018)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa21c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb21c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 2(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa23c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)); LIVE;
    a5 = a5 >> UINT32_C(0x00000018); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 3(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb23c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000504)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa258\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb258\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 6(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa278\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)); LIVE;
    a4 = a4 >> UINT32_C(0x00000018); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb278\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 8(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa618\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb618\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 10(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa638\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a4 = a4 >> UINT32_C(0x00000018); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 11(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb638\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 12(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa658\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 13(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb658\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 14(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa678\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    a5 = a5 >> UINT32_C(0x00000018); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 15(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb67c\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002422..0x20002426. */
REGION void tsl9_resident_parser_callees_block_20002422(void)
{
    REGS;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".Lresident_parser_callees_edge_20002424:\n.option push\n.option rvc\nc.j .Lresident_parser_callees_edge_20002424\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_parser_callees_block_200023ac\n");
    __builtin_unreachable();
}
