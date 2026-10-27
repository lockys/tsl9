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

/* Two complete conditional SDK slot3/record bodies:258B/84i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x60754..0x6077E. */
REGION void tsl9_candidate_external_flash_60754(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 9(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3718\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_6077c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_timer_expiry_path_edge_6077c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_expiry_path_block_6078a\n");
    __builtin_unreachable();
}

/* Original0x6077E..0x60786. */
REGION void tsl9_resident_timer_expiry_path_block_6077e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2794\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_60782:\n.option push\n.option norvc\nbne a3,a4,.Lresident_timer_expiry_path_edge_60782\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_expiry_path_block_6078a\n");
    __builtin_unreachable();
}

/* Original0x60786..0x6078A. */
REGION void tsl9_resident_timer_expiry_path_block_60786(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x6078A..0x60792. */
REGION void tsl9_resident_timer_expiry_path_block_6078a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_6078e:\n.option push\n.option norvc\nbeq a3,a4,.Lresident_timer_expiry_path_edge_6078e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_expiry_path_block_6079a\n");
    __builtin_unreachable();
}

/* Original0x60792..0x6079A. */
REGION void tsl9_resident_timer_expiry_path_block_60792(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_60796:\n.option push\n.option norvc\nbne a3,a4,.Lresident_timer_expiry_path_edge_60796\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_expiry_path_block_607a2\n");
    __builtin_unreachable();
}

/* Original0x6079A..0x607A2. */
REGION void tsl9_resident_timer_expiry_path_block_6079a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa798\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb798\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x607A2..0x607A6. */
REGION void tsl9_resident_timer_expiry_path_block_607a2(void)
{
    REGS;
    PORT(".Lresident_timer_expiry_path_edge_607a2:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_607a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x607A6..0x607C8. */
REGION void tsl9_resident_timer_expiry_path_block_607a6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s0, 1080(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 412\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 68(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 10(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 8(s0)\n.option pop\n");
    PORT(".Lresident_timer_expiry_path_literal_607c0:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_timer_expiry_path_literal_607c0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x607C8..0x607DC. */
REGION void tsl9_resident_timer_expiry_path_block_607c8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30a8\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsh zero, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 68(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 72(s0)\n.option pop\n");
    PORT(".Lresident_timer_expiry_path_edge_607d8:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_607d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x607DC..0x607E4. */
REGION void tsl9_resident_timer_expiry_path_block_607dc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30a8\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_607e0:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_607e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x607E4..0x607F0. */
REGION void tsl9_resident_timer_expiry_path_block_607e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 49(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_607ec:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_timer_expiry_path_edge_607ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_expiry_path_block_607fa\n");
    __builtin_unreachable();
}

/* Original0x607F0..0x607F4. */
REGION void tsl9_resident_timer_expiry_path_block_607f0(void)
{
    REGS;
    PORT(".Lresident_timer_expiry_path_edge_607f0:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_607f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x607F4..0x607FA. */
REGION void tsl9_resident_timer_expiry_path_block_607f4(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 49(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x607FA..0x60806. */
REGION void tsl9_resident_timer_expiry_path_block_607fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 48(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_60802:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_timer_expiry_path_edge_60802\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_expiry_path_block_60810\n");
    __builtin_unreachable();
}

/* Original0x60806..0x6080A. */
REGION void tsl9_resident_timer_expiry_path_block_60806(void)
{
    REGS;
    PORT(".Lresident_timer_expiry_path_edge_60806:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_60806\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x6080A..0x60810. */
REGION void tsl9_resident_timer_expiry_path_block_6080a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 48(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60810..0x6081A. */
REGION void tsl9_resident_timer_expiry_path_block_60810(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_60818:\n.option push\n.option rvc\nc.beqz a5,.Lresident_timer_expiry_path_edge_60818\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_expiry_path_block_60824\n");
    __builtin_unreachable();
}

/* Original0x6081A..0x60824. */
REGION void tsl9_resident_timer_expiry_path_block_6081a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_timer_expiry_path_literal_6081c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_timer_expiry_path_literal_6081c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60824..0x60838. */
REGION void tsl9_resident_timer_expiry_path_block_60824(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60838..0x6084E. */
REGION void tsl9_candidate_external_flash_60838(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000031)) = (uint8_t)a5; LIVE;
    a2 = UINT32_C(0x00000011); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_timer_expiry_path_edge_6084a:\n.option push\n.option norvc\njal ra,.Lresident_timer_expiry_path_edge_6084a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x6084E..0x60856. */
REGION void tsl9_resident_timer_expiry_path_block_6084e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_timer_expiry_path_edge_60852:\n.option push\n.option norvc\njal zero,.Lresident_timer_expiry_path_edge_60852\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_60754\n");
    __builtin_unreachable();
}
