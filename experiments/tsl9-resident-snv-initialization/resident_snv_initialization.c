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

/* Three public-SDK isbufset/message/SNV bodies:232B/83i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4329A..0x432A4. */
REGION void tsl9_candidate_message_initialize_4329a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000198)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44022..0x44038. */
REGION void tsl9_candidate_system_task_initialize_44022(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 492\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_44036:\n.option push\n.option rvc\nc.bnez a0,.Lresident_snv_initialization_edge_44036\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_44046\n");
    __builtin_unreachable();
}

/* Original0x44038..0x4403A. */
REGION void tsl9_resident_snv_initialization_block_44038(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x4403A..0x44046. */
REGION void tsl9_resident_snv_initialization_block_4403a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44046..0x4404E. */
REGION void tsl9_resident_snv_initialization_block_44046(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 492\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 56(s0)\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_4404c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_snv_initialization_edge_4404c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_44038\n");
    __builtin_unreachable();
}

/* Original0x4404E..0x44052. */
REGION void tsl9_resident_snv_initialization_block_4404e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 60(s0)\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_44050:\n.option push\n.option rvc\nc.beqz a4,.Lresident_snv_initialization_edge_44050\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_44038\n");
    __builtin_unreachable();
}

/* Original0x44052..0x44058. */
REGION void tsl9_resident_snv_initialization_block_44052(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44058..0x44060. */
REGION void tsl9_resident_snv_initialization_block_44058(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 8(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_snv_initialization_edge_4405c:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_snv_initialization_edge_4405c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_snv_initialization_block_44038\n");
    __builtin_unreachable();
}

/* Original0x44060..0x44072. */
REGION void tsl9_resident_snv_initialization_block_44060(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x244a\n.option pop\n");
    a1 = UINT32_C(0x0000004e); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".Lresident_snv_initialization_literal_4406a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_snv_initialization_literal_4406a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44072..0x4407E. */
REGION void tsl9_resident_snv_initialization_block_44072(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a4, s1, 412\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 412\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_4407c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_snv_initialization_edge_4407c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_44038\n");
    __builtin_unreachable();
}

/* Original0x4407E..0x4408E. */
REGION void tsl9_resident_snv_initialization_block_4407e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2452\n.option pop\n");
    a1 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".Lresident_snv_initialization_literal_44086:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_snv_initialization_literal_44086\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4408E..0x44096. */
REGION void tsl9_resident_snv_initialization_block_4408e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 32(s1)\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_44092:\n.option push\n.option norvc\nblt s2,a5,.Lresident_snv_initialization_edge_44092\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_snv_initialization_block_440ac\n");
    __builtin_unreachable();
}

/* Original0x44096..0x440A0. */
REGION void tsl9_resident_snv_initialization_block_44096(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a2\n.option pop\n");
    PORT(".Lresident_snv_initialization_literal_44098:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_snv_initialization_literal_44098\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x440A0..0x440AC. */
REGION void tsl9_resident_snv_initialization_block_440a0(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsw zero, 32(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 36(s1)\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_440aa:\n.option push\n.option rvc\nc.j .Lresident_snv_initialization_edge_440aa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_snv_initialization_block_4403a\n");
    __builtin_unreachable();
}

/* Original0x440AC..0x440C0. */
REGION void tsl9_resident_snv_initialization_block_440ac(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x244e\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 60(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a5, a1, s2\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    a0 = a0 + a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x440C0..0x440C2. */
REGION void tsl9_resident_snv_initialization_block_440c0(void)
{
    REGS;
    PORT(".Lresident_snv_initialization_edge_440c0:\n.option push\n.option rvc\nc.j .Lresident_snv_initialization_edge_440c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_snv_initialization_block_4408e\n");
    __builtin_unreachable();
}

/* Original0x200004BC..0x200004CE. */
REGION void tsl9_candidate_isbufset_200004bc(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_snv_initialization_edge_200004cc:\n.option push\n.option rvc\nc.beqz a0,.Lresident_snv_initialization_edge_200004cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_200004d4\n");
    __builtin_unreachable();
}

/* Original0x200004CE..0x200004D4. */
REGION void tsl9_resident_snv_initialization_block_200004ce(void)
{
    REGS;
    a4 = a0 + a2; LIVE;
    PORT(".Lresident_snv_initialization_edge_200004d2:\n.option push\n.option rvc\nc.bnez a2,.Lresident_snv_initialization_edge_200004d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_snv_initialization_block_200004e0\n");
    __builtin_unreachable();
}

/* Original0x200004D4..0x200004E0. */
REGION void tsl9_resident_snv_initialization_block_200004d4(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200004E0..0x200004EA. */
REGION void tsl9_resident_snv_initialization_block_200004e0(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xffffffff)); LIVE;
    PORT(".Lresident_snv_initialization_edge_200004e6:\n.option push\n.option norvc\nbne a3,a1,.Lresident_snv_initialization_edge_200004e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_snv_initialization_block_200004d4\n");
    __builtin_unreachable();
}

/* Original0x200004EA..0x200004EE. */
REGION void tsl9_resident_snv_initialization_block_200004ea(void)
{
    REGS;
    PORT(".Lresident_snv_initialization_edge_200004ea:\n.option push\n.option norvc\nbne a0,a4,.Lresident_snv_initialization_edge_200004ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_snv_initialization_block_200004e0\n");
    __builtin_unreachable();
}

/* Original0x200004EE..0x200004FA. */
REGION void tsl9_resident_snv_initialization_block_200004ee(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)a5; LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
