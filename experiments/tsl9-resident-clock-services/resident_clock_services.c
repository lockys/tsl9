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

/* Five complete public-SDK clock bodies:474B/168i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43520..0x43538. */
REGION void tsl9_candidate_TMOS_GetSystemClock_43520(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000230)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 412\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43536:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43536\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43540\n");
    __builtin_unreachable();
}

/* Original0x43538..0x4353A. */
REGION void tsl9_resident_clock_services_block_43538(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4353A..0x43540. */
REGION void tsl9_resident_clock_services_block_4353a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 20(s0)\n.option pop\n");
    a0 = a0 + a5; LIVE;
    PORT(".option push\n.option rvc\nsw a0, 20(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43540..0x4354A. */
REGION void tsl9_resident_clock_services_block_43540(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 20(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43B0A..0x43B18. */
REGION void tsl9_candidate_clock_provider_register_43b0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000230)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\njalr a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43B18..0x43B28. */
REGION void tsl9_resident_clock_services_block_43b18(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001b4)) = (uint32_t)a0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D62..0x43D7C. */
REGION void tsl9_candidate_clock_delta_43d62(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 564(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D7C..0x43D98. */
REGION void tsl9_resident_clock_services_block_43d7c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s4, 1600\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhu a1, a0, s4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s5, 8(s2)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, a0, s4\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43d94:\n.option push\n.option norvc\njal ra,.Lresident_clock_services_edge_43d94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x43D98..0x43DAA. */
REGION void tsl9_resident_clock_services_block_43d98(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x0000019c); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 24(a4)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_clock_services_edge_43da6:\n.option push\n.option norvc\nbeq s0,s1,.Lresident_clock_services_edge_43da6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_clock_services_block_43dd2\n");
    __builtin_unreachable();
}

/* Original0x43DAA..0x43DB6. */
REGION void tsl9_resident_clock_services_block_43daa(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s3, a5, 412\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a0, s1, s0\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43db2:\n.option push\n.option norvc\nbltu s0,s1,.Lresident_clock_services_edge_43db2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_clock_services_block_43dce\n");
    __builtin_unreachable();
}

/* Original0x43DB6..0x43DCA. */
REGION void tsl9_resident_clock_services_block_43db6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 4(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, s4, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s4, a0\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43dc6:\n.option push\n.option norvc\njal ra,.Lresident_clock_services_edge_43dc6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x43DCA..0x43DCE. */
REGION void tsl9_resident_clock_services_block_43dca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsub a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43DCE..0x43DD2. */
REGION void tsl9_resident_clock_services_block_43dce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 24(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43DD2..0x43DE4. */
REGION void tsl9_resident_clock_services_block_43dd2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F46..0x43F5E. */
REGION void tsl9_candidate_TMOS_TimerInit_43f46(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 492\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000030)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 492\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43f5c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43f64\n");
    __builtin_unreachable();
}

/* Original0x43F5E..0x43F62. */
REGION void tsl9_resident_clock_services_block_43f5e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F62..0x43F64. */
REGION void tsl9_resident_clock_services_block_43f62(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __builtin_unreachable();
}

/* Original0x43F64..0x43F66. */
REGION void tsl9_resident_clock_services_block_43f64(void)
{
    REGS;
    PORT(".Lresident_clock_services_edge_43f64:\n.option push\n.option rvc\nc.beqz a1,.Lresident_clock_services_edge_43f64\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fe6\n");
    __builtin_unreachable();
}

/* Original0x43F66..0x43F6C. */
REGION void tsl9_resident_clock_services_block_43f66(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_clock_services_edge_43f6a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f6a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fde\n");
    __builtin_unreachable();
}

/* Original0x43F6C..0x43F70. */
REGION void tsl9_resident_clock_services_block_43f6c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_clock_services_edge_43f6e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f6e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fde\n");
    __builtin_unreachable();
}

/* Original0x43F70..0x43F74. */
REGION void tsl9_resident_clock_services_block_43f70(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 8(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x259e\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43f72:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fde\n");
    __builtin_unreachable();
}

/* Original0x43F74..0x43F78. */
REGION void tsl9_resident_clock_services_block_43f74(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 10(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25be\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43f76:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fde\n");
    __builtin_unreachable();
}

/* Original0x43F78..0x43F7C. */
REGION void tsl9_resident_clock_services_block_43f78(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x25dc\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43f7a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_clock_services_edge_43f7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43f8c\n");
    __builtin_unreachable();
}

/* Original0x43F7C..0x43F8C. */
REGION void tsl9_resident_clock_services_block_43f7c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x385c\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_clock_services_edge_43f88:\n.option push\n.option norvc\nblt a4,a5,.Lresident_clock_services_edge_43f88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_clock_services_block_43fde\n");
    __builtin_unreachable();
}

/* Original0x43F8C..0x43F9E. */
REGION void tsl9_resident_clock_services_block_43f8c(void)
{
    REGS;
    a0 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    a0 = a0 + UINT32_C(0x00000234); LIVE;
    PORT(".Lresident_clock_services_literal_43f96:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_clock_services_literal_43f96\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43F9E..0x43FB2. */
REGION void tsl9_resident_clock_services_block_43f9e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000234)); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000001e0)) = (uint32_t)a3; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3878\n.option pop\n");
    PORT(".Lresident_clock_services_edge_43fb0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_clock_services_edge_43fb0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_clock_services_block_43fd2\n");
    __builtin_unreachable();
}

/* Original0x43FB2..0x43FD0. */
REGION void tsl9_resident_clock_services_block_43fb2(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000234); LIVE;
    /* Conditional Xwchc: qk.c.lhu a0, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x278a\n.option pop\n");
    a5 = UINT32_C(0x00000578); LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a0 = a0 * a5; LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_clock_services_edge_43fcc:\n.option push\n.option norvc\njal ra,.Lresident_clock_services_edge_43fcc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x43FD0..0x43FD2. */
REGION void tsl9_resident_clock_services_block_43fd0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a0, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb868\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43FD2..0x43FDC. */
REGION void tsl9_resident_clock_services_block_43fd2(void)
{
    REGS;
    a0 = UINT32_C(0x00044000); LIVE;
    a0 = a0 + UINT32_C(0xfffffd62); LIVE;
    PORT(".Lresident_clock_services_edge_43fda:\n.option push\n.option rvc\nc.jal .Lresident_clock_services_edge_43fda\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_clock_provider_register_43b0a\n");
    __builtin_unreachable();
}

/* Original0x43FDC..0x43FDE. */
REGION void tsl9_resident_clock_services_block_43fdc(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x43FDE..0x43FE6. */
REGION void tsl9_resident_clock_services_block_43fde(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43FE6..0x44022. */
REGION void tsl9_resident_clock_services_block_43fe6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x0000019c); LIVE;
    a4 = UINT32_C(0x20001000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)0; LIVE;
    a4 = a4 + UINT32_C(0xfffff986); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000234)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00328000); LIVE;
    a5 = a5 + UINT32_C(0x00000234); LIVE;
    a3 = UINT32_C(0xffffffff); LIVE;
    a4 = a4 + UINT32_C(0xfffffa12); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000268)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_clock_services_edge_44020:\n.option push\n.option rvc\nc.j .Lresident_clock_services_edge_44020\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_clock_services_block_43f9e\n");
    __builtin_unreachable();
}

/* Original0x20000986..0x200009BA. */
REGION void tsl9_candidate_default_clock_20000986(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)); LIVE;
    a5 = UINT32_C(0xffffc000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x0000019c); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000268)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)a3; LIVE;
    a0 = a0 << UINT32_C(0x0000001a); LIVE;
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
