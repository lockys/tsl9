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

/* One complete conditional SDK slot3/record bodies:90B/35i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x2000138E..0x20001390. */
REGION void tsl9_candidate_external_ram_2000138e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_callback_edge_2000138e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_callback_edge_2000138e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_callback_block_200013e6\n");
    __builtin_unreachable();
}

/* Original0x20001390..0x2000139C. */
REGION void tsl9_resident_task0_RAM_callback_block_20001390(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a1, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_callback_edge_2000139a:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_callback_edge_2000139a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_20001122\n");
    __builtin_unreachable();
}

/* Original0x2000139C..0x2000139E. */
REGION void tsl9_resident_task0_RAM_callback_block_2000139c(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_callback_edge_2000139c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_callback_edge_2000139c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_callback_block_200013e2\n");
    __builtin_unreachable();
}

/* Original0x2000139E..0x200013A4. */
REGION void tsl9_resident_task0_RAM_callback_block_2000139e(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_task0_RAM_callback_edge_200013a0:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_task0_RAM_callback_edge_200013a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_callback_block_200013ce\n");
    __builtin_unreachable();
}

/* Original0x200013A4..0x200013B4. */
REGION void tsl9_resident_task0_RAM_callback_block_200013a4(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = a3 + UINT32_C(0x000001ec); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 23(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x3afc\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000028)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_task0_RAM_callback_edge_200013b2:\n.option push\n.option rvc\nc.beqz a3,.Lresident_task0_RAM_callback_edge_200013b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_callback_block_200013b6\n");
    __builtin_unreachable();
}

/* Original0x200013B4..0x200013B6. */
REGION void tsl9_resident_task0_RAM_callback_block_200013b4(void)
{
    REGS;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x200013B6..0x200013BA. */
REGION void tsl9_resident_task0_RAM_callback_block_200013b6(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_callback_edge_200013b6:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task0_RAM_callback_edge_200013b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_callback_block_200013d6\n");
    __builtin_unreachable();
}

/* Original0x200013BA..0x200013CE. */
REGION void tsl9_resident_task0_RAM_callback_block_200013ba(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 41(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_callback_literal_200013c6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_436a8\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_callback_literal_200013c6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200013CE..0x200013D6. */
REGION void tsl9_resident_task0_RAM_callback_block_200013ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200013D6..0x200013E2. */
REGION void tsl9_resident_task0_RAM_callback_block_200013d6(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000238)); LIVE;
    a4 = a4 + a3; LIVE;
    PORT(".Lresident_task0_RAM_callback_edge_200013e0:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_callback_edge_200013e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_callback_block_200013ba\n");
    __builtin_unreachable();
}

/* Original0x200013E2..0x200013E4. */
REGION void tsl9_resident_task0_RAM_callback_block_200013e2(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_callback_edge_200013e2:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_callback_edge_200013e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_20000d50\n");
    __builtin_unreachable();
}

/* Original0x200013E4..0x200013E6. */
REGION void tsl9_resident_task0_RAM_callback_block_200013e4(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_callback_edge_200013e4:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_callback_edge_200013e4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_callback_block_200013ce\n");
    __builtin_unreachable();
}

/* Original0x200013E6..0x200013E8. */
REGION void tsl9_resident_task0_RAM_callback_block_200013e6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
