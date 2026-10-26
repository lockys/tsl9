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

/* Ten candidate bodies:764B/288i; incoming invocation unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x81CA..0x81D0. */
REGION void tsl9_safe_gap_entry_81ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_81ce:\n.option push\n.option rvc\nc.jal .Lsafe_gap_functions_edge_81ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0x81D0..0x81DE. */
REGION void tsl9_safe_gap_functions_block_81d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x000003e8); LIVE;
    a0 = a0 * a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9B02..0x9B16. */
REGION void tsl9_safe_gap_entry_9b02(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsafe_gap_functions_literal_9b08:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_gate_entry_9ad2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_9b08\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_9b12:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_9b12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x9B16..0x9B1C. */
REGION void tsl9_safe_gap_functions_block_9b16(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 168(gp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_9b1a:\n.option push\n.option rvc\nc.beqz s0,.Lsafe_gap_functions_edge_9b1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_9b2e\n");
    __builtin_unreachable();
}

/* Original0x9B1C..0x9B2E. */
REGION void tsl9_safe_gap_functions_block_9b1c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff814)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9B2E..0x9B36. */
REGION void tsl9_safe_gap_functions_block_9b2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_9b34:\n.option push\n.option rvc\nc.j .Lsafe_gap_functions_edge_9b34\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_9af0\n");
    __builtin_unreachable();
}

/* Original0x12A6E..0x12A78. */
REGION void tsl9_safe_gap_entry_12a6e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_12a74:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_12a74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_1070a\n");
    __builtin_unreachable();
}

/* Original0x12A78..0x12A7C. */
REGION void tsl9_safe_gap_functions_block_12a78(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lsafe_gap_functions_edge_12a7a:\n.option push\n.option rvc\nc.bnez a0,.Lsafe_gap_functions_edge_12a7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_12a9a\n");
    __builtin_unreachable();
}

/* Original0x12A7C..0x12A94. */
REGION void tsl9_safe_gap_functions_block_12a7c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000028)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000028)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 28\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000020)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000024)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".Lsafe_gap_functions_edge_12a90:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_12a90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_filter_program_18ba2\n");
    __builtin_unreachable();
}

/* Original0x12A94..0x12A9A. */
REGION void tsl9_safe_gap_functions_block_12a94(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12A9A..0x12A9E. */
REGION void tsl9_safe_gap_functions_block_12a9a(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_12a9a:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_12a9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_safe_gap_entry_16c72\n");
    __builtin_unreachable();
}

/* Original0x12A9E..0x12AA0. */
REGION void tsl9_safe_gap_functions_block_12a9e(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_12a9e:\n.option push\n.option rvc\nc.j .Lsafe_gap_functions_edge_12a9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_safe_gap_functions_block_12a94\n");
    __builtin_unreachable();
}

/* Original0x13660..0x13674. */
REGION void tsl9_safe_gap_entry_13660(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13674..0x13676. */
REGION void tsl9_safe_gap_functions_block_13674(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13674:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_13674\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_136c6\n");
    __builtin_unreachable();
}

/* Original0x13676..0x13698. */
REGION void tsl9_safe_gap_functions_block_13676(void)
{
    REGS;
    a5 = UINT32_C(0xffffffab); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000060); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsh s1, 0(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000100); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    PORT(".Lsafe_gap_functions_edge_13694:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13694\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_135e6\n");
    __builtin_unreachable();
}

/* Original0x13698..0x1369E. */
REGION void tsl9_safe_gap_functions_block_13698(void)
{
    REGS;
    a2 = UINT32_C(0x00000064); LIVE;
    PORT(".Lsafe_gap_functions_edge_1369c:\n.option push\n.option rvc\nc.bnez a0,.Lsafe_gap_functions_edge_1369c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_136a0\n");
    __builtin_unreachable();
}

/* Original0x1369E..0x136A0. */
REGION void tsl9_safe_gap_functions_block_1369e(void)
{
    REGS;
    a2 = UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x136A0..0x136B0. */
REGION void tsl9_safe_gap_functions_block_136a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsafe_gap_functions_literal_136a4:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_safe_gap_entry_13f36\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_136a4\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_136ac:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_136ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x136B0..0x136B2. */
REGION void tsl9_safe_gap_functions_block_136b0(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_136b0:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_136b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_136c6\n");
    __builtin_unreachable();
}

/* Original0x136B2..0x136C6. */
REGION void tsl9_safe_gap_functions_block_136b2(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x136C6..0x136D0. */
REGION void tsl9_safe_gap_functions_block_136c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x136D0..0x136E4. */
REGION void tsl9_safe_gap_entry_136d0(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x136E4..0x136E6. */
REGION void tsl9_safe_gap_functions_block_136e4(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_136e4:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_136e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13736\n");
    __builtin_unreachable();
}

/* Original0x136E6..0x13708. */
REGION void tsl9_safe_gap_functions_block_136e6(void)
{
    REGS;
    a5 = UINT32_C(0xffffffba); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000058); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsh s1, 0(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000100); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    PORT(".Lsafe_gap_functions_edge_13704:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13704\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_135e6\n");
    __builtin_unreachable();
}

/* Original0x13708..0x1370E. */
REGION void tsl9_safe_gap_functions_block_13708(void)
{
    REGS;
    a2 = UINT32_C(0x00000064); LIVE;
    PORT(".Lsafe_gap_functions_edge_1370c:\n.option push\n.option rvc\nc.bnez a0,.Lsafe_gap_functions_edge_1370c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13710\n");
    __builtin_unreachable();
}

/* Original0x1370E..0x13710. */
REGION void tsl9_safe_gap_functions_block_1370e(void)
{
    REGS;
    a2 = UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x13710..0x13720. */
REGION void tsl9_safe_gap_functions_block_13710(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsafe_gap_functions_literal_13714:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_safe_gap_entry_13f36\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_13714\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_1371c:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_1371c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x13720..0x13722. */
REGION void tsl9_safe_gap_functions_block_13720(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13720:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_13720\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13736\n");
    __builtin_unreachable();
}

/* Original0x13722..0x13736. */
REGION void tsl9_safe_gap_functions_block_13722(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13736..0x13740. */
REGION void tsl9_safe_gap_functions_block_13736(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13740..0x13758. */
REGION void tsl9_safe_gap_entry_13740(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13758..0x1375A. */
REGION void tsl9_safe_gap_functions_block_13758(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13758:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_13758\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_137b6\n");
    __builtin_unreachable();
}

/* Original0x1375A..0x13772. */
REGION void tsl9_safe_gap_functions_block_1375a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffffb9); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nsh s1, 0(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000068); LIVE;
    PORT(".Lsafe_gap_functions_edge_13770:\n.option push\n.option rvc\nc.bnez a1,.Lsafe_gap_functions_edge_13770\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13776\n");
    __builtin_unreachable();
}

/* Original0x13772..0x13776. */
REGION void tsl9_safe_gap_functions_block_13772(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000064); LIVE;
    __builtin_unreachable();
}

/* Original0x13776..0x13784. */
REGION void tsl9_safe_gap_functions_block_13776(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 8(s0)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_13782:\n.option push\n.option rvc\nc.bnez a2,.Lsafe_gap_functions_edge_13782\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_1378c\n");
    __builtin_unreachable();
}

/* Original0x13784..0x13788. */
REGION void tsl9_safe_gap_functions_block_13784(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13784:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13784\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_135e6\n");
    __builtin_unreachable();
}

/* Original0x13788..0x1378C. */
REGION void tsl9_safe_gap_functions_block_13788(void)
{
    REGS;
    a2 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lsafe_gap_functions_edge_1378a:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_1378a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13790\n");
    __builtin_unreachable();
}

/* Original0x1378C..0x13790. */
REGION void tsl9_safe_gap_functions_block_1378c(void)
{
    REGS;
    a2 = UINT32_C(0x00000064); LIVE;
    __builtin_unreachable();
}

/* Original0x13790..0x137A0. */
REGION void tsl9_safe_gap_functions_block_13790(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsafe_gap_functions_literal_13794:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_safe_gap_entry_13f36\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_13794\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_1379c:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_1379c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x137A0..0x137A2. */
REGION void tsl9_safe_gap_functions_block_137a0(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_137a0:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_137a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_137b6\n");
    __builtin_unreachable();
}

/* Original0x137A2..0x137B6. */
REGION void tsl9_safe_gap_functions_block_137a2(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x137B6..0x137C0. */
REGION void tsl9_safe_gap_functions_block_137b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13DD4..0x13DE4. */
REGION void tsl9_safe_gap_entry_13dd4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".Lsafe_gap_functions_literal_13dd6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_safe_gap_entry_13dd4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_13dd6\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_13de0:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13de0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x13DE4..0x13DEA. */
REGION void tsl9_safe_gap_functions_block_13de4(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsafe_gap_functions_edge_13de6:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13de6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0x13DEA..0x13DEE. */
REGION void tsl9_safe_gap_functions_block_13dea(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13dea:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13dea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_status_81aa\n");
    __builtin_unreachable();
}

/* Original0x13DEE..0x13DF0. */
REGION void tsl9_safe_gap_functions_block_13dee(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13dee:\n.option push\n.option rvc\nc.bnez a0,.Lsafe_gap_functions_edge_13dee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13e08\n");
    __builtin_unreachable();
}

/* Original0x13DF0..0x13E08. */
REGION void tsl9_safe_gap_functions_block_13df0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x0000012c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsafe_gap_functions_literal_13dfa:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_secondary_message_dispatch_entry_13f88\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsafe_gap_functions_literal_13dfa\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_13e04:\n.option push\n.option norvc\njal zero,.Lsafe_gap_functions_edge_13e04\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x13E08..0x13E0E. */
REGION void tsl9_safe_gap_functions_block_13e08(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13F36..0x13F38. */
REGION void tsl9_safe_gap_entry_13f36(void)
{
    REGS;
    PORT(".Lsafe_gap_functions_edge_13f36:\n.option push\n.option rvc\nc.beqz a0,.Lsafe_gap_functions_edge_13f36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_safe_gap_functions_block_13f64\n");
    __builtin_unreachable();
}

/* Original0x13F38..0x13F52. */
REGION void tsl9_safe_gap_functions_block_13f38(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lsafe_gap_functions_edge_13f4e:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_13f4e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x13F52..0x13F64. */
REGION void tsl9_safe_gap_functions_block_13f52(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13F64..0x13F66. */
REGION void tsl9_safe_gap_functions_block_13f64(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x14CC8..0x14CD6. */
REGION void tsl9_safe_gap_entry_14cc8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_14cd2:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_14cd2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original0x14CD6..0x14CDE. */
REGION void tsl9_safe_gap_functions_block_14cd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsafe_gap_functions_edge_14cda:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_14cda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original0x14CDE..0x14CEA. */
REGION void tsl9_safe_gap_functions_block_14cde(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x0000001e); LIVE;
    PORT(".option push\n.option rvc\nslli s1, s1, 0x1f\n.option pop\n");
    PORT(".option push\n.option rvc\nor s1, s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsafe_gap_functions_edge_14ce6:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_14ce6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original0x14CEA..0x14CF0. */
REGION void tsl9_safe_gap_functions_block_14cea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_14cec:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_14cec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_mode_getter_829e\n");
    __builtin_unreachable();
}

/* Original0x14CF0..0x14D2E. */
REGION void tsl9_safe_gap_functions_block_14cf0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000160); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000005)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000002)); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a3 = a3 << UINT32_C(0x00000003); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)); LIVE;
    a3 = a3 << UINT32_C(0x00000002); LIVE;
    a5 = a5 | a3; LIVE;
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    a5 = a5 | a4; LIVE;
    a5 = a5 | a0; LIVE;
    PORT(".option push\n.option norvc\nslli a0, s0, 0x1d\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nor a0, a0, s1\n.option pop\n");
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16C72..0x16C80. */
REGION void tsl9_safe_gap_entry_16c72(void)
{
    REGS;
    a5 = a0 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsafe_gap_functions_edge_16c7c:\n.option push\n.option norvc\nbltu a4,a5,.Lsafe_gap_functions_edge_16c7c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_safe_gap_functions_block_16cc2\n");
    __builtin_unreachable();
}

/* Original0x16C80..0x16C8E. */
REGION void tsl9_safe_gap_functions_block_16c80(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_16c8a:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_16c8a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_16858\n");
    __builtin_unreachable();
}

/* Original0x16C8E..0x16C98. */
REGION void tsl9_safe_gap_functions_block_16c8e(void)
{
    REGS;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_16c94:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_16c94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_169dc\n");
    __builtin_unreachable();
}

/* Original0x16C98..0x16CA6. */
REGION void tsl9_safe_gap_functions_block_16c98(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000060); LIVE;
    a1 = UINT32_C(0x00000060); LIVE;
    PORT(".Lsafe_gap_functions_edge_16ca2:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_16ca2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16CA6..0x16CB4. */
REGION void tsl9_safe_gap_functions_block_16ca6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = UINT32_C(0x00000070); LIVE;
    a2 = UINT32_C(0x00000060); LIVE;
    PORT(".Lsafe_gap_functions_edge_16cb0:\n.option push\n.option norvc\njal ra,.Lsafe_gap_functions_edge_16cb0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16CB4..0x16CC2. */
REGION void tsl9_safe_gap_functions_block_16cb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsafe_gap_functions_edge_16cbe:\n.option push\n.option norvc\njal zero,.Lsafe_gap_functions_edge_16cbe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_169dc\n");
    __builtin_unreachable();
}

/* Original0x16CC2..0x16CC4. */
REGION void tsl9_safe_gap_functions_block_16cc2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
