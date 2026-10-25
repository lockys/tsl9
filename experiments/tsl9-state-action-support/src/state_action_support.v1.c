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

/* Fifteen connected state/action support functions:562B/199i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9FB2..0x9FB8. */
REGION void tsl9_state_action_support_entry_9fb2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ae)); LIVE;
    PORT(".Lstate_action_support_edge_9fb6:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_9fb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_9fc0\n");
    __builtin_unreachable();
}

/* Original0x9FB8..0x9FC0. */
REGION void tsl9_state_action_support_block_9fb8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ae)) = (uint8_t)0; LIVE;
    PORT(".Lstate_action_support_edge_9fbc:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_9fbc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17320\n");
    __builtin_unreachable();
}

/* Original0x9FC0..0x9FC2. */
REGION void tsl9_state_action_support_block_9fc0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA024..0xA02E. */
REGION void tsl9_record_state_controls_provider_a024(void)
{
    REGS;
    a5 = UINT32_C(0x00000019); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ad)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_action_support_edge_a02c:\n.option push\n.option rvc\nc.j .Lstate_action_support_edge_a02c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_provider_9f7a\n");
    __builtin_unreachable();
}

/* Original0xA02E..0xA04A. */
REGION void tsl9_state_action_support_entry_a02e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a2 = UINT32_C(0x00001000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ae)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000388); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_action_support_literal_a03e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_state_action_support_entry_9fb2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_action_support_literal_a03e\n.option pop\n");
    PORT(".Lstate_action_support_edge_a046:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_a046\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA04A..0xA050. */
REGION void tsl9_state_action_support_entry_a04a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ae)); LIVE;
    PORT(".Lstate_action_support_edge_a04e:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_a04e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_a052\n");
    __builtin_unreachable();
}

/* Original0xA050..0xA052. */
REGION void tsl9_state_action_support_block_a050(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_a050:\n.option push\n.option rvc\nc.j .Lstate_action_support_edge_a050\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_action_support_entry_a02e\n");
    __builtin_unreachable();
}

/* Original0xA052..0xA054. */
REGION void tsl9_state_action_support_block_a052(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA664..0xA674. */
REGION void tsl9_record_state_controls_provider_a664(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a5 & UINT32_C(0x00000006); LIVE;
    PORT(".Lstate_action_support_edge_a672:\n.option push\n.option rvc\nc.beqz a4,.Lstate_action_support_edge_a672\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_a6a8\n");
    __builtin_unreachable();
}

/* Original0xA674..0xA684. */
REGION void tsl9_state_action_support_block_a674(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff859)); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".Lstate_action_support_edge_a682:\n.option push\n.option rvc\nc.bnez a5,.Lstate_action_support_edge_a682\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_a6a8\n");
    __builtin_unreachable();
}

/* Original0xA684..0xA69E. */
REGION void tsl9_state_action_support_block_a684(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_action_support_literal_a688:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_action_support_literal_a688\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff83f)) = (uint8_t)a5; LIVE;
    PORT(".Lstate_action_support_edge_a69a:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_a69a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA69E..0xA6A8. */
REGION void tsl9_state_action_support_block_a69e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_a6a4:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_a6a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xA6A8..0xA6AA. */
REGION void tsl9_state_action_support_block_a6a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA2E..0xAA3C. */
REGION void tsl9_state_action_support_entry_aa2e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lstate_action_support_edge_aa3a:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_aa3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aa5e\n");
    __builtin_unreachable();
}

/* Original0xAA3C..0xAA44. */
REGION void tsl9_state_action_support_block_aa3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_action_support_edge_aa40:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aa40\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xAA44..0xAA46. */
REGION void tsl9_state_action_support_block_aa44(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_aa44:\n.option push\n.option rvc\nc.beqz a0,.Lstate_action_support_edge_aa44\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aa58\n");
    __builtin_unreachable();
}

/* Original0xAA46..0xAA4A. */
REGION void tsl9_state_action_support_block_aa46(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_aa46:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aa46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xAA4A..0xAA4C. */
REGION void tsl9_state_action_support_block_aa4a(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_aa4a:\n.option push\n.option rvc\nc.bnez a0,.Lstate_action_support_edge_aa4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aa58\n");
    __builtin_unreachable();
}

/* Original0xAA4C..0xAA58. */
REGION void tsl9_state_action_support_block_aa4c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_aa54:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_aa54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0xAA58..0xAA5E. */
REGION void tsl9_state_action_support_block_aa58(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA5E..0xAA60. */
REGION void tsl9_state_action_support_block_aa5e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA60..0xAA6E. */
REGION void tsl9_record_state_controls_provider_aa60(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lstate_action_support_edge_aa6c:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_aa6c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aa9e\n");
    __builtin_unreachable();
}

/* Original0xAA6E..0xAA76. */
REGION void tsl9_state_action_support_block_aa6e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_action_support_edge_aa72:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aa72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xAA76..0xAA78. */
REGION void tsl9_state_action_support_block_aa76(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_aa76:\n.option push\n.option rvc\nc.bnez a0,.Lstate_action_support_edge_aa76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aa98\n");
    __builtin_unreachable();
}

/* Original0xAA78..0xAA8C. */
REGION void tsl9_state_action_support_block_aa78(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000003e8); LIVE;
    PORT(".Lstate_action_support_literal_aa80:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_state_action_support_entry_aa2e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_action_support_literal_aa80\n.option pop\n");
    PORT(".Lstate_action_support_edge_aa88:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aa88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xAA8C..0xAA98. */
REGION void tsl9_state_action_support_block_aa8c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_aa94:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_aa94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0xAA98..0xAA9E. */
REGION void tsl9_state_action_support_block_aa98(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA9E..0xAAA0. */
REGION void tsl9_state_action_support_block_aa9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAAA0..0xAAAE. */
REGION void tsl9_selector_notifications_provider_aaa0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lstate_action_support_edge_aaac:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_aaac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aad6\n");
    __builtin_unreachable();
}

/* Original0xAAAE..0xAAB6. */
REGION void tsl9_state_action_support_block_aaae(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_action_support_edge_aab2:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aab2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xAAB6..0xAAB8. */
REGION void tsl9_state_action_support_block_aab6(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_aab6:\n.option push\n.option rvc\nc.beqz a0,.Lstate_action_support_edge_aab6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_aad0\n");
    __builtin_unreachable();
}

/* Original0xAAB8..0xAAC4. */
REGION void tsl9_state_action_support_block_aab8(void)
{
    REGS;
    PORT(".Lstate_action_support_literal_aab8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_state_action_support_entry_aa2e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_action_support_literal_aab8\n.option pop\n");
    PORT(".Lstate_action_support_edge_aac0:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_aac0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xAAC4..0xAAD0. */
REGION void tsl9_state_action_support_block_aac4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_aacc:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_aacc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0xAAD0..0xAAD6. */
REGION void tsl9_state_action_support_block_aad0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAAD6..0xAAD8. */
REGION void tsl9_state_action_support_block_aad6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xADB8..0xADC8. */
REGION void tsl9_selector_notifications_provider_adb8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_action_support_edge_adc4:\n.option push\n.option norvc\nbltu a4,a5,.Lstate_action_support_edge_adc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_action_support_block_add4\n");
    __builtin_unreachable();
}

/* Original0xADC8..0xADD2. */
REGION void tsl9_state_action_support_block_adc8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000118)); LIVE;
    PORT(".Lstate_action_support_edge_add0:\n.option push\n.option rvc\nc.bnez a5,.Lstate_action_support_edge_add0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_add4\n");
    __builtin_unreachable();
}

/* Original0xADD2..0xADD4. */
REGION void tsl9_state_action_support_block_add2(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_add2:\n.option push\n.option rvc\nc.j .Lstate_action_support_edge_add2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_entry_ad48\n");
    __builtin_unreachable();
}

/* Original0xADD4..0xADD6. */
REGION void tsl9_state_action_support_block_add4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBCEC..0xBCF6. */
REGION void tsl9_record_state_controls_provider_bcec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000210)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBCF6..0xBD00. */
REGION void tsl9_record_dispatch_provider_bcf6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000207)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD00..0xBD0A. */
REGION void tsl9_selector_notifications_provider_bd00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000001fd)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFDA0..0xFDA6. */
REGION void tsl9_record_state_controls_provider_fda0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFDA6..0xFDAC. */
REGION void tsl9_record_state_controls_provider_fda6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lstate_action_support_edge_fdaa:\n.option push\n.option rvc\nc.beqz a0,.Lstate_action_support_edge_fdaa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_fdde\n");
    __builtin_unreachable();
}

/* Original0xFDAC..0xFDB0. */
REGION void tsl9_state_action_support_block_fdac(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_fdac:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_fdac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xFDB0..0xFDB6. */
REGION void tsl9_state_action_support_block_fdb0(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lstate_action_support_edge_fdb2:\n.option push\n.option norvc\nbne a0,a5,.Lstate_action_support_edge_fdb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_action_support_block_fdf0\n");
    __builtin_unreachable();
}

/* Original0xFDB6..0xFDBA. */
REGION void tsl9_state_action_support_block_fdb6(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_fdb6:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_fdb6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xFDBA..0xFDC0. */
REGION void tsl9_state_action_support_block_fdba(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lstate_action_support_edge_fdbc:\n.option push\n.option norvc\nbleu a0,a5,.Lstate_action_support_edge_fdbc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_action_support_block_fdf0\n");
    __builtin_unreachable();
}

/* Original0xFDC0..0xFDC2. */
REGION void tsl9_state_action_support_block_fdc0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFDC2..0xFDD0. */
REGION void tsl9_state_action_support_block_fdc2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x0000000d); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)) = (uint8_t)a5; LIVE;
    PORT(".Lstate_action_support_edge_fdcc:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_fdcc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xFDD0..0xFDD6. */
REGION void tsl9_state_action_support_block_fdd0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Lstate_action_support_edge_fdd4:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_fdd4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_fdf0\n");
    __builtin_unreachable();
}

/* Original0xFDD6..0xFDDC. */
REGION void tsl9_state_action_support_block_fdd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lstate_action_support_edge_fdd8:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_fdd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_fba2\n");
    __builtin_unreachable();
}

/* Original0xFDDC..0xFDDE. */
REGION void tsl9_state_action_support_block_fddc(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_fddc:\n.option push\n.option rvc\nc.j .Lstate_action_support_edge_fddc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_action_support_block_fdf0\n");
    __builtin_unreachable();
}

/* Original0xFDDE..0xFDE8. */
REGION void tsl9_state_action_support_block_fdde(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_action_support_edge_fde4:\n.option push\n.option norvc\nbne a4,a5,.Lstate_action_support_edge_fde4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_action_support_block_fdec\n");
    __builtin_unreachable();
}

/* Original0xFDE8..0xFDEC. */
REGION void tsl9_state_action_support_block_fde8(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_action_support_edge_fdea:\n.option push\n.option rvc\nc.j .Lstate_action_support_edge_fdea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_action_support_block_fdc2\n");
    __builtin_unreachable();
}

/* Original0xFDEC..0xFDF0. */
REGION void tsl9_state_action_support_block_fdec(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xFDF0..0xFDF6. */
REGION void tsl9_state_action_support_block_fdf0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1016E..0x10176. */
REGION void tsl9_record_state_controls_provider_1016e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_action_support_edge_10172:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_10172\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0x10176..0x10178. */
REGION void tsl9_state_action_support_block_10176(void)
{
    REGS;
    PORT(".Lstate_action_support_edge_10176:\n.option push\n.option rvc\nc.beqz a0,.Lstate_action_support_edge_10176\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_10190\n");
    __builtin_unreachable();
}

/* Original0x10178..0x10190. */
REGION void tsl9_state_action_support_block_10178(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_action_support_literal_10182:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_state_controls_provider_1016e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_action_support_literal_10182\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_1018c:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_1018c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x10190..0x10196. */
REGION void tsl9_state_action_support_block_10190(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000130)); LIVE;
    PORT(".Lstate_action_support_edge_10194:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_10194\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_1019e\n");
    __builtin_unreachable();
}

/* Original0x10196..0x1019E. */
REGION void tsl9_state_action_support_block_10196(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000130)) = (uint8_t)0; LIVE;
    PORT(".Lstate_action_support_edge_1019a:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_1019a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x1019E..0x101A4. */
REGION void tsl9_state_action_support_block_1019e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000131)); LIVE;
    PORT(".Lstate_action_support_edge_101a2:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_101a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_101b0\n");
    __builtin_unreachable();
}

/* Original0x101A4..0x101B0. */
REGION void tsl9_state_action_support_block_101a4(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000131)) = (uint8_t)0; LIVE;
    PORT(".Lstate_action_support_edge_101ac:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_101ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x101B0..0x101B6. */
REGION void tsl9_state_action_support_block_101b0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000132)); LIVE;
    PORT(".Lstate_action_support_edge_101b4:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_101b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_101c2\n");
    __builtin_unreachable();
}

/* Original0x101B6..0x101C2. */
REGION void tsl9_state_action_support_block_101b6(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000132)) = (uint8_t)0; LIVE;
    PORT(".Lstate_action_support_edge_101be:\n.option push\n.option norvc\njal ra,.Lstate_action_support_edge_101be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x101C2..0x101C8. */
REGION void tsl9_state_action_support_block_101c2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000133)); LIVE;
    PORT(".Lstate_action_support_edge_101c6:\n.option push\n.option rvc\nc.beqz a5,.Lstate_action_support_edge_101c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_action_support_block_101d8\n");
    __builtin_unreachable();
}

/* Original0x101C8..0x101D8. */
REGION void tsl9_state_action_support_block_101c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000133)) = (uint8_t)0; LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_action_support_edge_101d4:\n.option push\n.option norvc\njal zero,.Lstate_action_support_edge_101d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x101D8..0x101DE. */
REGION void tsl9_state_action_support_block_101d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
