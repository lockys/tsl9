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

/* Three complete selector transition functions:246B/94i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xAB08..0xAB12. */
REGION void tsl9_input_state_decoders_provider_ab08(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lselector_transitions_edge_ab0e:\n.option push\n.option norvc\nbeq a0,a2,.Lselector_transitions_edge_ab0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_ab5c\n");
    __builtin_unreachable();
}

/* Original0xAB12..0xAB26. */
REGION void tsl9_selector_transitions_block_ab12(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lselector_transitions_edge_ab24:\n.option push\n.option rvc\nc.beqz a2,.Lselector_transitions_edge_ab24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_transitions_block_ab4c\n");
    __builtin_unreachable();
}

/* Original0xAB26..0xAB2C. */
REGION void tsl9_selector_transitions_block_ab26(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lselector_transitions_edge_ab2a:\n.option push\n.option rvc\nc.bnez a4,.Lselector_transitions_edge_ab2a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_transitions_block_ab36\n");
    __builtin_unreachable();
}

/* Original0xAB2C..0xAB36. */
REGION void tsl9_selector_transitions_block_ab2c(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)a4; LIVE;
    PORT(".Lselector_transitions_edge_ab32:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ab32\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xAB36..0xAB3C. */
REGION void tsl9_selector_transitions_block_ab36(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lselector_transitions_edge_ab38:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ab38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xAB3C..0xAB4C. */
REGION void tsl9_selector_transitions_block_ab3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAB4C..0xAB5A. */
REGION void tsl9_selector_transitions_block_ab4c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000003e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".Lselector_transitions_edge_ab56:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ab56\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xAB5A..0xAB5C. */
REGION void tsl9_selector_transitions_block_ab5a(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_ab5a:\n.option push\n.option rvc\nc.j .Lselector_transitions_edge_ab5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_transitions_block_ab3c\n");
    __builtin_unreachable();
}

/* Original0xAB5C..0xAB5E. */
REGION void tsl9_selector_transitions_block_ab5c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAB7C..0xAB90. */
REGION void tsl9_input_state_decoders_provider_ab7c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 868(s1)\n.option pop\n");
    PORT(".Lselector_transitions_edge_ab8c:\n.option push\n.option norvc\nbeq s1,a0,.Lselector_transitions_edge_ab8c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_abc0\n");
    __builtin_unreachable();
}

/* Original0xAB90..0xAB96. */
REGION void tsl9_selector_transitions_block_ab90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lselector_transitions_edge_ab92:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ab92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xAB96..0xAB98. */
REGION void tsl9_selector_transitions_block_ab96(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_ab96:\n.option push\n.option rvc\nc.beqz a0,.Lselector_transitions_edge_ab96\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_transitions_block_abac\n");
    __builtin_unreachable();
}

/* Original0xAB98..0xABA0. */
REGION void tsl9_selector_transitions_block_ab98(void)
{
    REGS;
    a0 = UINT32_C(0x00000096); LIVE;
    PORT(".Lselector_transitions_edge_ab9c:\n.option push\n.option norvc\nbltu s0,s1,.Lselector_transitions_edge_ab9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_aba8\n");
    __builtin_unreachable();
}

/* Original0xABA0..0xABA4. */
REGION void tsl9_selector_transitions_block_aba0(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_aba0:\n.option push\n.option norvc\nbleu s0,s1,.Lselector_transitions_edge_aba0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_abac\n");
    __builtin_unreachable();
}

/* Original0xABA4..0xABA8. */
REGION void tsl9_selector_transitions_block_aba4(void)
{
    REGS;
    a0 = UINT32_C(0x00000097); LIVE;
    __builtin_unreachable();
}

/* Original0xABA8..0xABAC. */
REGION void tsl9_selector_transitions_block_aba8(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_aba8:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_aba8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xABAC..0xABB6. */
REGION void tsl9_selector_transitions_block_abac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 828(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xABB6..0xABC0. */
REGION void tsl9_selector_transitions_block_abb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xABC0..0xABC4. */
REGION void tsl9_selector_transitions_block_abc0(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_transitions_edge_abc2:\n.option push\n.option rvc\nc.j .Lselector_transitions_edge_abc2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_transitions_block_abb6\n");
    __builtin_unreachable();
}

/* Original0xECA8..0xECB6. */
REGION void tsl9_input_state_decoders_provider_eca8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lselector_transitions_edge_ecb2:\n.option push\n.option norvc\nbeq a1,a4,.Lselector_transitions_edge_ecb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_ecc8\n");
    __builtin_unreachable();
}

/* Original0xECB6..0xECBA. */
REGION void tsl9_selector_transitions_block_ecb6(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_ecb6:\n.option push\n.option norvc\nbeq a1,a5,.Lselector_transitions_edge_ecb6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_ecc8\n");
    __builtin_unreachable();
}

/* Original0xECBA..0xECBC. */
REGION void tsl9_selector_transitions_block_ecba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xECBC..0xECC8. */
REGION void tsl9_selector_transitions_block_ecbc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xECC8..0xECD4. */
REGION void tsl9_selector_transitions_block_ecc8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)a2; LIVE;
    PORT(".Lselector_transitions_edge_ecd0:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ecd0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_guard_828c\n");
    __builtin_unreachable();
}

/* Original0xECD4..0xECDA. */
REGION void tsl9_selector_transitions_block_ecd4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)); LIVE;
    PORT(".Lselector_transitions_edge_ecd8:\n.option push\n.option rvc\nc.beqz a0,.Lselector_transitions_edge_ecd8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_transitions_block_ecfa\n");
    __builtin_unreachable();
}

/* Original0xECDA..0xECE2. */
REGION void tsl9_selector_transitions_block_ecda(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s1)\n.option pop\n");
    PORT(".Lselector_transitions_edge_ecde:\n.option push\n.option norvc\nbeq a5,a1,.Lselector_transitions_edge_ecde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_ecba\n");
    __builtin_unreachable();
}

/* Original0xECE2..0xECEE. */
REGION void tsl9_selector_transitions_block_ece2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nsb a1, 0(s1)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    PORT(".Lselector_transitions_edge_ecea:\n.option push\n.option norvc\nbeq a1,a4,.Lselector_transitions_edge_ecea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_transitions_block_ecf2\n");
    __builtin_unreachable();
}

/* Original0xECEE..0xECF2. */
REGION void tsl9_selector_transitions_block_ecee(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xECF2..0xECF8. */
REGION void tsl9_selector_transitions_block_ecf2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a2\n.option pop\n");
    PORT(".Lselector_transitions_edge_ecf4:\n.option push\n.option norvc\njal ra,.Lselector_transitions_edge_ecf4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xECF8..0xECFA. */
REGION void tsl9_selector_transitions_block_ecf8(void)
{
    REGS;
    PORT(".Lselector_transitions_edge_ecf8:\n.option push\n.option rvc\nc.j .Lselector_transitions_edge_ecf8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_transitions_block_ecbc\n");
    __builtin_unreachable();
}

/* Original0xECFA..0xED00. */
REGION void tsl9_selector_transitions_block_ecfa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a1, 0(s1)\n.option pop\n");
    PORT(".Lselector_transitions_edge_ecfe:\n.option push\n.option rvc\nc.j .Lselector_transitions_edge_ecfe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_transitions_block_ecbc\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
