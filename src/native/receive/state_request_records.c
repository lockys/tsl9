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

/* Eleven connected state request/record functions:740B/256i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x94EE..0x9508. */
REGION void tsl9_selector_notifications_provider_94ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff9ce); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv t1, a0\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint16_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9EF0..0x9EFA. */
REGION void tsl9_selector_notifications_provider_9ef0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lstate_request_records_edge_9ef8:\n.option push\n.option rvc\nc.jal .Lstate_request_records_edge_9ef8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_9e84\n");
    __builtin_unreachable();
}

/* Original0x9EFA..0x9F06. */
REGION void tsl9_state_request_records_block_9efa(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option norvc\nsh s0, 10(sp)\n.option pop\n");
    PORT(".Lstate_request_records_edge_9f04:\n.option push\n.option rvc\nc.jal .Lstate_request_records_edge_9f04\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_entry_9e5c\n");
    __builtin_unreachable();
}

/* Original0x9F06..0x9F0A. */
REGION void tsl9_state_request_records_block_9f06(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_9f06:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_9f06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_entry_937e\n");
    __builtin_unreachable();
}

/* Original0x9F0A..0x9F12. */
REGION void tsl9_state_request_records_block_9f0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA9E8..0xAA00. */
REGION void tsl9_selector_notifications_provider_a9e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff88a)); LIVE;
    a0 = a5 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    a5 = a5 >> UINT32_C(0x0000000c); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lstate_request_records_edge_a9fc:\n.option push\n.option norvc\nbeq a0,a4,.Lstate_request_records_edge_a9fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_aa16\n");
    __builtin_unreachable();
}

/* Original0xAA00..0xAA04. */
REGION void tsl9_state_request_records_block_aa00(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_aa00:\n.option push\n.option norvc\nbeq a5,a4,.Lstate_request_records_edge_aa00\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_aa14\n");
    __builtin_unreachable();
}

/* Original0xAA04..0xAA0A. */
REGION void tsl9_state_request_records_block_aa04(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_aa06:\n.option push\n.option norvc\nbeq a0,a4,.Lstate_request_records_edge_aa06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_aa16\n");
    __builtin_unreachable();
}

/* Original0xAA0A..0xAA10. */
REGION void tsl9_state_request_records_block_aa0a(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_aa0c:\n.option push\n.option norvc\nbeq a5,a4,.Lstate_request_records_edge_aa0c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_aa16\n");
    __builtin_unreachable();
}

/* Original0xAA10..0xAA14. */
REGION void tsl9_state_request_records_block_aa10(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA14..0xAA16. */
REGION void tsl9_state_request_records_block_aa14(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xAA16..0xAA18. */
REGION void tsl9_state_request_records_block_aa16(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAA18..0xAA2E. */
REGION void tsl9_main_services_provider_aa18(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x0000000d); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = a0 + UINT32_C(0x000004ac); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xABFC..0xAC0A. */
REGION void tsl9_selector_notifications_provider_abfc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000066c)); LIVE;
    a0 = a0 >> UINT32_C(0x00000008); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDA36..0xDA4A. */
REGION void tsl9_selector_notifications_provider_da36(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a4 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x18\n.option pop\n");
    PORT(".Lstate_request_records_edge_da46:\n.option push\n.option norvc\nbgez a4,.Lstate_request_records_edge_da46\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_da72\n");
    __builtin_unreachable();
}

/* Original0xDA4A..0xDA4C. */
REGION void tsl9_state_request_records_block_da4a(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_da4a:\n.option push\n.option rvc\nc.beqz a0,.Lstate_request_records_edge_da4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_da52\n");
    __builtin_unreachable();
}

/* Original0xDA4C..0xDA4E. */
REGION void tsl9_state_request_records_block_da4c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xDA4E..0xDA52. */
REGION void tsl9_state_request_records_block_da4e(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_da4e:\n.option push\n.option norvc\njal zero,.Lstate_request_records_edge_da4e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_entry_fe1c\n");
    __builtin_unreachable();
}

/* Original0xDA52..0xDA56. */
REGION void tsl9_state_request_records_block_da52(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lstate_request_records_edge_da54:\n.option push\n.option rvc\nc.beqz a5,.Lstate_request_records_edge_da54\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_da6e\n");
    __builtin_unreachable();
}

/* Original0xDA56..0xDA5E. */
REGION void tsl9_state_request_records_block_da56(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_request_records_edge_da5a:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_da5a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_provider_d76c\n");
    __builtin_unreachable();
}

/* Original0xDA5E..0xDA60. */
REGION void tsl9_state_request_records_block_da5e(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_da5e:\n.option push\n.option rvc\nc.beqz a0,.Lstate_request_records_edge_da5e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_da68\n");
    __builtin_unreachable();
}

/* Original0xDA60..0xDA68. */
REGION void tsl9_state_request_records_block_da60(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_request_records_edge_da66:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_da66\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_da4e\n");
    __builtin_unreachable();
}

/* Original0xDA68..0xDA6E. */
REGION void tsl9_state_request_records_block_da68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDA6E..0xDA72. */
REGION void tsl9_state_request_records_block_da6e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_request_records_edge_da70:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_da70\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_da4e\n");
    __builtin_unreachable();
}

/* Original0xDA72..0xDA74. */
REGION void tsl9_state_request_records_block_da72(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFBA2..0xFBB6. */
REGION void tsl9_feature_external_fba2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000122)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lstate_request_records_edge_fbb2:\n.option push\n.option norvc\nbeq a4,a5,.Lstate_request_records_edge_fbb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc60\n");
    __builtin_unreachable();
}

/* Original0xFBB6..0xFBBC. */
REGION void tsl9_state_request_records_block_fbb6(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_fbb8:\n.option push\n.option norvc\nbeq a4,a5,.Lstate_request_records_edge_fbb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc7a\n");
    __builtin_unreachable();
}

/* Original0xFBBC..0xFBBE. */
REGION void tsl9_state_request_records_block_fbbc(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xFBBE..0xFBD4. */
REGION void tsl9_state_request_records_block_fbbe(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000054); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000020); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lstate_request_records_edge_fbd0:\n.option push\n.option norvc\nbne a4,a2,.Lstate_request_records_edge_fbd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc0a\n");
    __builtin_unreachable();
}

/* Original0xFBD4..0xFBE4. */
REGION void tsl9_state_request_records_block_fbd4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_request_records_edge_fbe0:\n.option push\n.option norvc\nbleu a4,a2,.Lstate_request_records_edge_fbe0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc0a\n");
    __builtin_unreachable();
}

/* Original0xFBE4..0xFBF0. */
REGION void tsl9_state_request_records_block_fbe4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000005f4)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_fbee:\n.option push\n.option rvc\nc.beqz a5,.Lstate_request_records_edge_fbee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fbfe\n");
    __builtin_unreachable();
}

/* Original0xFBF0..0xFBFE. */
REGION void tsl9_state_request_records_block_fbf0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffe7); LIVE;
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFBFE..0xFC0A. */
REGION void tsl9_state_request_records_block_fbfe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFC0A..0xFC12. */
REGION void tsl9_state_request_records_block_fc0a(void)
{
    REGS;
    a4 = *(volatile int8_t *)(uintptr_t)(a3 + UINT32_C(0x00000001)); LIVE;
    PORT(".Lstate_request_records_edge_fc0e:\n.option push\n.option norvc\nbgez a4,.Lstate_request_records_edge_fc0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc1e\n");
    __builtin_unreachable();
}

/* Original0xFC12..0xFC1E. */
REGION void tsl9_state_request_records_block_fc12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFC1E..0xFC28. */
REGION void tsl9_state_request_records_block_fc1e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_fc24:\n.option push\n.option norvc\nbeq a4,a3,.Lstate_request_records_edge_fc24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc90\n");
    __builtin_unreachable();
}

/* Original0xFC28..0xFC2E. */
REGION void tsl9_state_request_records_block_fc28(void)
{
    REGS;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lstate_request_records_edge_fc2a:\n.option push\n.option norvc\nbeq a4,a3,.Lstate_request_records_edge_fc2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fcb8\n");
    __builtin_unreachable();
}

/* Original0xFC2E..0xFC34. */
REGION void tsl9_state_request_records_block_fc2e(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_request_records_edge_fc30:\n.option push\n.option norvc\nbne a4,a3,.Lstate_request_records_edge_fc30\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fc44\n");
    __builtin_unreachable();
}

/* Original0xFC34..0xFC42. */
REGION void tsl9_state_request_records_block_fc34(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFC42..0xFC44. */
REGION void tsl9_state_request_records_block_fc42(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFC44..0xFC4E. */
REGION void tsl9_state_request_records_block_fc44(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_request_records_edge_fc4a:\n.option push\n.option norvc\nbeq a4,a3,.Lstate_request_records_edge_fc4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fcda\n");
    __builtin_unreachable();
}

/* Original0xFC4E..0xFC54. */
REGION void tsl9_state_request_records_block_fc4e(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_request_records_edge_fc50:\n.option push\n.option norvc\nbeq a4,a3,.Lstate_request_records_edge_fc50\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fd1a\n");
    __builtin_unreachable();
}

/* Original0xFC54..0xFC56. */
REGION void tsl9_state_request_records_block_fc54(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_fc54:\n.option push\n.option rvc\nc.bnez a5,.Lstate_request_records_edge_fc54\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fce6\n");
    __builtin_unreachable();
}

/* Original0xFC56..0xFC60. */
REGION void tsl9_state_request_records_block_fc56(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFC60..0xFC6C. */
REGION void tsl9_state_request_records_block_fc60(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a3 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lstate_request_records_edge_fc68:\n.option push\n.option norvc\nbeq a3,a4,.Lstate_request_records_edge_fc68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_request_records_block_fbbc\n");
    __builtin_unreachable();
}

/* Original0xFC6C..0xFC72. */
REGION void tsl9_state_request_records_block_fc6c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFC72..0xFC7A. */
REGION void tsl9_state_request_records_block_fc72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_request_records_edge_fc78:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fc78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fbbe\n");
    __builtin_unreachable();
}

/* Original0xFC7A..0xFC82. */
REGION void tsl9_state_request_records_block_fc7a(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lstate_request_records_edge_fc80:\n.option push\n.option rvc\nc.beqz a5,.Lstate_request_records_edge_fc80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fbbc\n");
    __builtin_unreachable();
}

/* Original0xFC82..0xFC86. */
REGION void tsl9_state_request_records_block_fc82(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_fc82:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fc82\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xFC86..0xFC88. */
REGION void tsl9_state_request_records_block_fc86(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_fc86:\n.option push\n.option rvc\nc.bnez a0,.Lstate_request_records_edge_fc86\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fbbc\n");
    __builtin_unreachable();
}

/* Original0xFC88..0xFC90. */
REGION void tsl9_state_request_records_block_fc88(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    PORT(".Lstate_request_records_edge_fc8e:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fc8e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fc72\n");
    __builtin_unreachable();
}

/* Original0xFC90..0xFCB6. */
REGION void tsl9_state_request_records_block_fc90(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lstate_request_records_literal_fca6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_state_request_records_entry_fd3e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_request_records_literal_fca6\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    PORT(".Lstate_request_records_edge_fcb2:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fcb2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xFCB6..0xFCB8. */
REGION void tsl9_state_request_records_block_fcb6(void)
{
    REGS;
    PORT(".Lstate_request_records_edge_fcb6:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fcb6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fc42\n");
    __builtin_unreachable();
}

/* Original0xFCB8..0xFCDA. */
REGION void tsl9_state_request_records_block_fcb8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x000000f0); LIVE;
    a4 = a4 + UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    PORT(".Lstate_request_records_edge_fcd8:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fcd8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fc42\n");
    __builtin_unreachable();
}

/* Original0xFCDA..0xFCE6. */
REGION void tsl9_state_request_records_block_fcda(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFCE6..0xFD06. */
REGION void tsl9_state_request_records_block_fce6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 2(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a4 = a5 & UINT32_C(0x000000f0); LIVE;
    a4 = a4 + UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    a1 = UINT32_C(0x00000007); LIVE;
    PORT(".Lstate_request_records_edge_fd02:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fd02\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xFD06..0xFD1A. */
REGION void tsl9_state_request_records_block_fd06(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s1, s1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 3(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_request_records_edge_fd16:\n.option push\n.option norvc\njal zero,.Lstate_request_records_edge_fd16\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xFD1A..0xFD3E. */
REGION void tsl9_state_request_records_block_fd1a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000121)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffbf); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x000000f0); LIVE;
    a4 = a4 + UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    PORT(".Lstate_request_records_edge_fd3c:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fd3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fce6\n");
    __builtin_unreachable();
}

/* Original0xFD3E..0xFD4C. */
REGION void tsl9_state_request_records_entry_fd3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x0000000d); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lstate_request_records_edge_fd48:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fd48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xFD4C..0xFD52. */
REGION void tsl9_state_request_records_block_fd4c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Lstate_request_records_edge_fd50:\n.option push\n.option rvc\nc.beqz a5,.Lstate_request_records_edge_fd50\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fd58\n");
    __builtin_unreachable();
}

/* Original0xFD52..0xFD58. */
REGION void tsl9_state_request_records_block_fd52(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lstate_request_records_edge_fd54:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fd54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_fba2\n");
    __builtin_unreachable();
}

/* Original0xFD58..0xFD5E. */
REGION void tsl9_state_request_records_block_fd58(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFD5E..0xFD64. */
REGION void tsl9_state_request_records_entry_fd5e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFD64..0xFD6A. */
REGION void tsl9_state_request_records_entry_fd64(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFE1C..0xFE22. */
REGION void tsl9_state_request_records_entry_fe1c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_request_records_edge_fe20:\n.option push\n.option rvc\nc.beqz a0,.Lstate_request_records_edge_fe20\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_request_records_block_fe4c\n");
    __builtin_unreachable();
}

/* Original0xFE22..0xFE34. */
REGION void tsl9_state_request_records_block_fe22(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_request_records_literal_fe24:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_request_records_literal_fe24\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000123)) = (uint8_t)a5; LIVE;
    PORT(".Lstate_request_records_edge_fe30:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fe30\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFE34..0xFE44. */
REGION void tsl9_state_request_records_block_fe34(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_request_records_literal_fe3c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_request_records_literal_fe3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFE44..0xFE4C. */
REGION void tsl9_state_request_records_block_fe44(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_request_records_edge_fe48:\n.option push\n.option norvc\njal zero,.Lstate_request_records_edge_fe48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xFE4C..0xFE58. */
REGION void tsl9_state_request_records_block_fe4c(void)
{
    REGS;
    PORT(".Lstate_request_records_literal_fe4c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_request_records_literal_fe4c\n.option pop\n");
    PORT(".Lstate_request_records_edge_fe54:\n.option push\n.option norvc\njal ra,.Lstate_request_records_edge_fe54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFE58..0xFE6A. */
REGION void tsl9_state_request_records_block_fe58(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_request_records_literal_fe60:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_request_records_literal_fe60\n.option pop\n");
    PORT(".Lstate_request_records_edge_fe68:\n.option push\n.option rvc\nc.j .Lstate_request_records_edge_fe68\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_request_records_block_fe44\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
