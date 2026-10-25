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

/* Seventeen connected record/state control functions:1322B/441i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xAAD8..0xAAE2. */
REGION void tsl9_record_state_controls_entry_aad8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000040a)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAC78..0xAC90. */
REGION void tsl9_selector_notifications_provider_ac78(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, gp, 84\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a5 & UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_state_controls_edge_ac8e:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_state_controls_edge_ac8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAC90..0xAC96. */
REGION void tsl9_record_state_controls_block_ac90(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lrecord_state_controls_edge_ac94:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_state_controls_edge_ac94\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAC96..0xAC9C. */
REGION void tsl9_record_state_controls_block_ac96(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_ac98:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ac98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xAC9C..0xACA2. */
REGION void tsl9_record_state_controls_block_ac9c(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_state_controls_edge_ac9e:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_state_controls_edge_ac9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xACA2..0xACA8. */
REGION void tsl9_record_state_controls_block_aca2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_aca4:\n.option push\n.option norvc\nbne s0,a5,.Lrecord_state_controls_edge_aca4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acc0\n");
    __builtin_unreachable();
}

/* Original0xACA8..0xACB2. */
REGION void tsl9_record_state_controls_block_aca8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0xACB2..0xACB6. */
REGION void tsl9_record_state_controls_block_acb2(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_acb2:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_state_controls_edge_acb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acd2\n");
    __builtin_unreachable();
}

/* Original0xACB6..0xACC0. */
REGION void tsl9_record_state_controls_block_acb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xACC0..0xACC6. */
REGION void tsl9_record_state_controls_block_acc0(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_state_controls_edge_acc2:\n.option push\n.option norvc\nbne s0,a5,.Lrecord_state_controls_edge_acc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_ace4\n");
    __builtin_unreachable();
}

/* Original0xACC6..0xACD2. */
REGION void tsl9_record_state_controls_block_acc6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_state_controls_edge_acce:\n.option push\n.option norvc\nbne a5,a0,.Lrecord_state_controls_edge_acce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xACD2..0xACD6. */
REGION void tsl9_record_state_controls_block_acd2(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_acd2:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_acd2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xACD6..0xACD8. */
REGION void tsl9_record_state_controls_block_acd6(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_acd6:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_state_controls_edge_acd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_acf6\n");
    __builtin_unreachable();
}

/* Original0xACD8..0xACE4. */
REGION void tsl9_record_state_controls_block_acd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_ace0:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_ace0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_a664\n");
    __builtin_unreachable();
}

/* Original0xACE4..0xACEA. */
REGION void tsl9_record_state_controls_block_ace4(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_state_controls_edge_ace6:\n.option push\n.option norvc\nbne s0,a5,.Lrecord_state_controls_edge_ace6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xACEA..0xACF6. */
REGION void tsl9_record_state_controls_block_acea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000006); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_state_controls_edge_acf4:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_acf4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_acb2\n");
    __builtin_unreachable();
}

/* Original0xACF6..0xAD14. */
REGION void tsl9_record_state_controls_block_acf6(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000007d0); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_literal_ad00:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_state_controls_entry_aad8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_state_controls_literal_ad00\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001da)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_state_controls_edge_ad10:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad10\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xAD14..0xAD1A. */
REGION void tsl9_record_state_controls_block_ad14(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_ad16:\n.option push\n.option norvc\nbne s0,a5,.Lrecord_state_controls_edge_ad16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAD1A..0xAD20. */
REGION void tsl9_record_state_controls_block_ad1a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lrecord_state_controls_edge_ad1e:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_state_controls_edge_ad1e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAD20..0xAD24. */
REGION void tsl9_record_state_controls_block_ad20(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_ad22:\n.option push\n.option rvc\nc.jal .Lrecord_state_controls_edge_ad22\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0xAD24..0xAD36. */
REGION void tsl9_record_state_controls_block_ad24(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000160); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_state_controls_edge_ad32:\n.option push\n.option norvc\nbltu s0,a5,.Lrecord_state_controls_edge_ad32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAD36..0xAD3A. */
REGION void tsl9_record_state_controls_block_ad36(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_ad36:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad36\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xAD3A..0xAD3C. */
REGION void tsl9_record_state_controls_block_ad3a(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_ad3a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_state_controls_edge_ad3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_acb6\n");
    __builtin_unreachable();
}

/* Original0xAD3C..0xAD48. */
REGION void tsl9_record_state_controls_block_ad3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_ad46:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_ad46\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_adb8\n");
    __builtin_unreachable();
}

/* Original0xAD48..0xAD54. */
REGION void tsl9_record_state_controls_entry_ad48(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000199)); LIVE;
    PORT(".Lrecord_state_controls_edge_ad50:\n.option push\n.option norvc\nbeq a5,a0,.Lrecord_state_controls_edge_ad50\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_adb6\n");
    __builtin_unreachable();
}

/* Original0xAD54..0xAD6C. */
REGION void tsl9_record_state_controls_block_ad54(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000018d)) = (uint8_t)a0; LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000050); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_ad68:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad68\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xAD6C..0xAD76. */
REGION void tsl9_record_state_controls_block_ad6c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000175)); LIVE;
    PORT(".Lrecord_state_controls_edge_ad74:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_ad74\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_adb2\n");
    __builtin_unreachable();
}

/* Original0xAD76..0xAD7A. */
REGION void tsl9_record_state_controls_block_ad76(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_ad76:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_a024\n");
    __builtin_unreachable();
}

/* Original0xAD7A..0xAD84. */
REGION void tsl9_record_state_controls_block_ad7a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000168)); LIVE;
    PORT(".Lrecord_state_controls_edge_ad82:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_ad82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_adac\n");
    __builtin_unreachable();
}

/* Original0xAD84..0xAD98. */
REGION void tsl9_record_state_controls_block_ad84(void)
{
    REGS;
    PORT(".Lrecord_state_controls_literal_ad84:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_state_controls_entry_aad8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_state_controls_literal_ad84\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000156)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_state_controls_edge_ad94:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xAD98..0xAD9C. */
REGION void tsl9_record_state_controls_block_ad98(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_ad98:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ad98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_a664\n");
    __builtin_unreachable();
}

/* Original0xAD9C..0xAD9E. */
REGION void tsl9_record_state_controls_block_ad9c(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_ad9c:\n.option push\n.option rvc\nc.jal .Lrecord_state_controls_edge_ad9c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_provider_aa60\n");
    __builtin_unreachable();
}

/* Original0xAD9E..0xADA4. */
REGION void tsl9_record_state_controls_block_ad9e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_edge_ada0:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_ada0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xADA4..0xADAC. */
REGION void tsl9_record_state_controls_block_ada4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_ada8:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_ada8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xADAC..0xADB0. */
REGION void tsl9_record_state_controls_block_adac(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_state_controls_edge_adae:\n.option push\n.option rvc\nc.jal .Lrecord_state_controls_edge_adae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_ac78\n");
    __builtin_unreachable();
}

/* Original0xADB0..0xADB2. */
REGION void tsl9_record_state_controls_block_adb0(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_adb0:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_adb0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_ad9c\n");
    __builtin_unreachable();
}

/* Original0xADB2..0xADB4. */
REGION void tsl9_record_state_controls_block_adb2(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_adb2:\n.option push\n.option rvc\nc.jal .Lrecord_state_controls_edge_adb2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_aaa0\n");
    __builtin_unreachable();
}

/* Original0xADB4..0xADB6. */
REGION void tsl9_record_state_controls_block_adb4(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_adb4:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_adb4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_ad9e\n");
    __builtin_unreachable();
}

/* Original0xADB6..0xADB8. */
REGION void tsl9_record_state_controls_block_adb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC364..0xC37C. */
REGION void tsl9_selector_notifications_provider_c364(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffba6)); LIVE;
    PORT(".option push\n.option norvc\nauipc s0, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -1142\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_c37a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_c37a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c382\n");
    __builtin_unreachable();
}

/* Original0xC37C..0xC382. */
REGION void tsl9_record_state_controls_block_c37c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_edge_c37e:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_c37e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ef76\n");
    __builtin_unreachable();
}

/* Original0xC382..0xC38C. */
REGION void tsl9_record_state_controls_block_c382(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 22(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_state_controls_edge_c38a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_c38a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c392\n");
    __builtin_unreachable();
}

/* Original0xC38C..0xC392. */
REGION void tsl9_record_state_controls_block_c38c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_edge_c38e:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_c38e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0xC392..0xC39C. */
REGION void tsl9_record_state_controls_block_c392(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 23(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_state_controls_edge_c39a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_c39a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c3a4\n");
    __builtin_unreachable();
}

/* Original0xC39C..0xC3A4. */
REGION void tsl9_record_state_controls_block_c39c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb77)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xC3A4..0xC3AC. */
REGION void tsl9_record_state_controls_block_c3a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC3AC..0xC3BE. */
REGION void tsl9_record_dispatch_provider_c3ac(void)
{
    REGS;
    a5 = UINT32_C(0x00000032); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb5e)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_c3ba:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_c3ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0xC3BE..0xC3D4. */
REGION void tsl9_main_services_provider_c3be(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x0000001c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb32); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC3D4..0xC3EA. */
REGION void tsl9_feature_external_c3d4(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0x00000047); LIVE;
    PORT(".Lrecord_state_controls_edge_c3e8:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_state_controls_edge_c3e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c410\n");
    __builtin_unreachable();
}

/* Original0xC3EA..0xC3F6. */
REGION void tsl9_record_state_controls_block_c3ea(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    a0 = UINT32_C(0x00000048); LIVE;
    PORT(".Lrecord_state_controls_edge_c3f2:\n.option push\n.option norvc\nbltz a5,.Lrecord_state_controls_edge_c3f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_c410\n");
    __builtin_unreachable();
}

/* Original0xC3F6..0xC404. */
REGION void tsl9_record_state_controls_block_c3f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000049); LIVE;
    a4 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_c402:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_state_controls_edge_c402\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c410\n");
    __builtin_unreachable();
}

/* Original0xC404..0xC40C. */
REGION void tsl9_record_state_controls_block_c404(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000046); LIVE;
    PORT(".Lrecord_state_controls_edge_c40a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_c40a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_c410\n");
    __builtin_unreachable();
}

/* Original0xC40C..0xC410. */
REGION void tsl9_record_state_controls_block_c40c(void)
{
    REGS;
    a0 = UINT32_C(0x0000004a); LIVE;
    __builtin_unreachable();
}

/* Original0xC410..0xC420. */
REGION void tsl9_record_state_controls_block_c410(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20000\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffffb0c); LIVE;
    a1 = UINT32_C(0x00000046); LIVE;
    PORT(".Lrecord_state_controls_edge_c41c:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_c41c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0xC420..0xC432. */
REGION void tsl9_record_state_controls_block_c420(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffaf4)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_state_controls_edge_c42e:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_state_controls_edge_c42e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_c45a\n");
    __builtin_unreachable();
}

/* Original0xC432..0xC444. */
REGION void tsl9_record_state_controls_block_c432(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffae6)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x0000004e); LIVE;
    PORT(".Lrecord_state_controls_edge_c440:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_state_controls_edge_c440\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_c448\n");
    __builtin_unreachable();
}

/* Original0xC444..0xC448. */
REGION void tsl9_record_state_controls_block_c444(void)
{
    REGS;
    a0 = UINT32_C(0x0000004f); LIVE;
    __builtin_unreachable();
}

/* Original0xC448..0xC450. */
REGION void tsl9_record_state_controls_block_c448(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_c44c:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_c44c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xC450..0xC45A. */
REGION void tsl9_record_state_controls_block_c450(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_c456:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_c456\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xC45A..0xC462. */
REGION void tsl9_record_state_controls_block_c45a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD50A..0xD512. */
REGION void tsl9_record_state_controls_entry_d50a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d50e:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d50e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xD512..0xD518. */
REGION void tsl9_record_state_controls_block_d512(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_d514:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_state_controls_edge_d514\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d536\n");
    __builtin_unreachable();
}

/* Original0xD518..0xD51E. */
REGION void tsl9_record_state_controls_block_d518(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lrecord_state_controls_edge_d51c:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_state_controls_edge_d51c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d52c\n");
    __builtin_unreachable();
}

/* Original0xD51E..0xD52C. */
REGION void tsl9_record_state_controls_block_d51e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d528:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d528\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_d05c\n");
    __builtin_unreachable();
}

/* Original0xD52C..0xD536. */
REGION void tsl9_record_state_controls_block_d52c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d532:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d532\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_10022\n");
    __builtin_unreachable();
}

/* Original0xD536..0xD53C. */
REGION void tsl9_record_state_controls_block_d536(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD53C..0xD544. */
REGION void tsl9_record_state_controls_entry_d53c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d540:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d540\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_bcec\n");
    __builtin_unreachable();
}

/* Original0xD544..0xD54A. */
REGION void tsl9_record_state_controls_block_d544(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f0)); LIVE;
    PORT(".Lrecord_state_controls_edge_d548:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_d548\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d562\n");
    __builtin_unreachable();
}

/* Original0xD54A..0xD54C. */
REGION void tsl9_record_state_controls_block_d54a(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d54a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_state_controls_edge_d54a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d572\n");
    __builtin_unreachable();
}

/* Original0xD54C..0xD55A. */
REGION void tsl9_record_state_controls_block_d54c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f1)) = (uint8_t)a5; LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x0000004c); LIVE;
    __builtin_unreachable();
}

/* Original0xD55A..0xD562. */
REGION void tsl9_record_state_controls_block_d55a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d55e:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d55e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xD562..0xD564. */
REGION void tsl9_record_state_controls_block_d562(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d562:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_state_controls_edge_d562\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d572\n");
    __builtin_unreachable();
}

/* Original0xD564..0xD572. */
REGION void tsl9_record_state_controls_block_d564(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f1)) = (uint8_t)0; LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x0000004d); LIVE;
    PORT(".Lrecord_state_controls_edge_d570:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_d570\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_d55a\n");
    __builtin_unreachable();
}

/* Original0xD572..0xD578. */
REGION void tsl9_record_state_controls_block_d572(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD578..0xD588. */
REGION void tsl9_record_state_controls_entry_d578(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f0)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d584:\n.option push\n.option norvc\nbeq a4,a0,.Lrecord_state_controls_edge_d584\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d5a8\n");
    __builtin_unreachable();
}

/* Original0xD588..0xD5A2. */
REGION void tsl9_record_state_controls_block_d588(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f0)) = (uint8_t)a0; LIVE;
    a4 = UINT32_C(0x00000040); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lrecord_state_controls_edge_d59e:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_state_controls_edge_d59e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d5a6\n");
    __builtin_unreachable();
}

/* Original0xD5A2..0xD5A6. */
REGION void tsl9_record_state_controls_block_d5a2(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5a2:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_fda6\n");
    __builtin_unreachable();
}

/* Original0xD5A6..0xD5A8. */
REGION void tsl9_record_state_controls_block_d5a6(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5a6:\n.option push\n.option rvc\nc.jal .Lrecord_state_controls_edge_d5a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_entry_d53c\n");
    __builtin_unreachable();
}

/* Original0xD5A8..0xD5B2. */
REGION void tsl9_record_state_controls_block_d5a8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ed)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f0)); LIVE;
    PORT(".Lrecord_state_controls_edge_d5b0:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_state_controls_edge_d5b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d606\n");
    __builtin_unreachable();
}

/* Original0xD5B2..0xD5B4. */
REGION void tsl9_record_state_controls_block_d5b2(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5b2:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_d5b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD5B4..0xD5B6. */
REGION void tsl9_record_state_controls_block_d5b4(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5b4:\n.option push\n.option rvc\nc.beqz s0,.Lrecord_state_controls_edge_d5b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD5B6..0xD5D2. */
REGION void tsl9_record_state_controls_block_d5b6(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ed)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000080); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lrecord_state_controls_edge_d5ce:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_state_controls_edge_d5ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d5d8\n");
    __builtin_unreachable();
}

/* Original0xD5D2..0xD5D8. */
REGION void tsl9_record_state_controls_block_d5d2(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_d5d4:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_fda6\n");
    __builtin_unreachable();
}

/* Original0xD5D8..0xD5DC. */
REGION void tsl9_record_state_controls_block_d5d8(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5d8:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xD5DC..0xD5DE. */
REGION void tsl9_record_state_controls_block_d5dc(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5dc:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_state_controls_edge_d5dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD5DE..0xD5E6. */
REGION void tsl9_record_state_controls_block_d5de(void)
{
    REGS;
    a0 = UINT32_C(0x000000a0); LIVE;
    PORT(".Lrecord_state_controls_edge_d5e2:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xD5E6..0xD5EA. */
REGION void tsl9_record_state_controls_block_d5e6(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5e6:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_fda0\n");
    __builtin_unreachable();
}

/* Original0xD5EA..0xD5F0. */
REGION void tsl9_record_state_controls_block_d5ea(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_d5ec:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_state_controls_edge_d5ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d62a\n");
    __builtin_unreachable();
}

/* Original0xD5F0..0xD5F4. */
REGION void tsl9_record_state_controls_block_d5f0(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d5f0:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d5f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xD5F4..0xD5FA. */
REGION void tsl9_record_state_controls_block_d5f4(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_state_controls_edge_d5f6:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_state_controls_edge_d5f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d62a\n");
    __builtin_unreachable();
}

/* Original0xD5FA..0xD606. */
REGION void tsl9_record_state_controls_block_d5fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d602:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d602\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_fda6\n");
    __builtin_unreachable();
}

/* Original0xD606..0xD608. */
REGION void tsl9_record_state_controls_block_d606(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d606:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_state_controls_edge_d606\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD608..0xD622. */
REGION void tsl9_record_state_controls_block_d608(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ed)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000080); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lrecord_state_controls_edge_d61e:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_state_controls_edge_d61e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD622..0xD628. */
REGION void tsl9_record_state_controls_block_d622(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_edge_d624:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_d624\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_fda6\n");
    __builtin_unreachable();
}

/* Original0xD628..0xD62A. */
REGION void tsl9_record_state_controls_block_d628(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d628:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_d628\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_d5e6\n");
    __builtin_unreachable();
}

/* Original0xD62A..0xD632. */
REGION void tsl9_record_state_controls_block_d62a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD632..0xD64A. */
REGION void tsl9_feature_external_d632(void)
{
    REGS;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a1 = (uint32_t)(a1 < UINT32_C(0x00000026)); LIVE;
    a0 = a0 >> UINT32_C(0x00000006); LIVE;
    a1 = a1 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_d646:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d646\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_entry_d578\n");
    __builtin_unreachable();
}

/* Original0xD64A..0xD662. */
REGION void tsl9_feature_external_d64a(void)
{
    REGS;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a1 = (uint32_t)(a1 < UINT32_C(0x00000051)); LIVE;
    a0 = a0 >> UINT32_C(0x00000009); LIVE;
    a1 = a1 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_d65e:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d65e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_entry_d578\n");
    __builtin_unreachable();
}

/* Original0xD662..0xD668. */
REGION void tsl9_selector_notifications_provider_d662(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f1)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD668..0xD66A. */
REGION void tsl9_record_dispatch_provider_d668(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_d668:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_state_controls_edge_d668\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_d67e\n");
    __builtin_unreachable();
}

/* Original0xD66A..0xD67E. */
REGION void tsl9_record_state_controls_block_d66a(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_state_controls_literal_d672:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_state_controls_entry_d50a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_state_controls_literal_d672\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d67a:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d67a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xD67E..0xD68A. */
REGION void tsl9_record_state_controls_block_d67e(void)
{
    REGS;
    PORT(".Lrecord_state_controls_literal_d67e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_state_controls_entry_d50a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_state_controls_literal_d67e\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_d686:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d686\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xD68A..0xD69C. */
REGION void tsl9_main_services_provider_d68a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000f0); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD69C..0xD6E0. */
REGION void tsl9_feature_external_d69c(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = a4 >> UINT32_C(0x00000006); LIVE;
    a3 = a4 & UINT32_C(0x0000003f); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a3 = a3 << UINT32_C(0x00000004); LIVE;
    a1 = a1 >> UINT32_C(0x00000004); LIVE;
    a1 = a1 | a3; LIVE;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = a2 & UINT32_C(0x00000003); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = a2 >> UINT32_C(0x00000002); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)); LIVE;
    a2 = a2 & UINT32_C(0x0000000f); LIVE;
    a2 = a2 << UINT32_C(0x00000006); LIVE;
    a2 = a2 | a3; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f4)); LIVE;
    PORT(".Lrecord_state_controls_edge_d6dc:\n.option push\n.option norvc\nbne a3,a1,.Lrecord_state_controls_edge_d6dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d6f8\n");
    __builtin_unreachable();
}

/* Original0xD6E0..0xD6E8. */
REGION void tsl9_record_state_controls_block_d6e0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f6)); LIVE;
    PORT(".Lrecord_state_controls_edge_d6e4:\n.option push\n.option norvc\nbne a3,a4,.Lrecord_state_controls_edge_d6e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d6f8\n");
    __builtin_unreachable();
}

/* Original0xD6E8..0xD6F0. */
REGION void tsl9_record_state_controls_block_d6e8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f8)); LIVE;
    PORT(".Lrecord_state_controls_edge_d6ec:\n.option push\n.option norvc\nbne a3,a5,.Lrecord_state_controls_edge_d6ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d6f8\n");
    __builtin_unreachable();
}

/* Original0xD6F0..0xD6F8. */
REGION void tsl9_record_state_controls_block_d6f0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000fa)); LIVE;
    PORT(".Lrecord_state_controls_edge_d6f4:\n.option push\n.option norvc\nbeq a3,a2,.Lrecord_state_controls_edge_d6f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_d752\n");
    __builtin_unreachable();
}

/* Original0xD6F8..0xD752. */
REGION void tsl9_record_state_controls_block_d6f8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f4)) = (uint16_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f6)) = (uint16_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000f8)) = (uint16_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x000000fa)) = (uint16_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000fc); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 & UINT32_C(0xfffffc00); LIVE;
    a3 = a3 | a1; LIVE;
    a1 = a4 << UINT32_C(0x0000000a); LIVE;
    a4 = UINT32_C(0xfff00000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a4 = a4 & a3; LIVE;
    a3 = a5 << UINT32_C(0x00000014); LIVE;
    a5 = UINT32_C(0xc0100000); LIVE;
    a4 = a4 | a1; LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    a5 = a5 | a3; LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a2 << UINT32_C(0x0000001e); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x000000fc)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a2 = a2 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0xffffff00); LIVE;
    a2 = a2 | a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x00000100)) = (uint32_t)a2; LIVE;
    PORT(".Lrecord_state_controls_edge_d74e:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_d74e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD752..0xD754. */
REGION void tsl9_record_state_controls_block_d752(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x101DE..0x101E8. */
REGION void tsl9_selector_notifications_provider_101de(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_state_controls_edge_101e4:\n.option push\n.option norvc\nbeq a0,a4,.Lrecord_state_controls_edge_101e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_10220\n");
    __builtin_unreachable();
}

/* Original0x101E8..0x101EA. */
REGION void tsl9_record_state_controls_block_101e8(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_101e8:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_state_controls_edge_101e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_101fc\n");
    __builtin_unreachable();
}

/* Original0x101EA..0x101F0. */
REGION void tsl9_record_state_controls_block_101ea(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_state_controls_edge_101ec:\n.option push\n.option norvc\nbeq a0,a3,.Lrecord_state_controls_edge_101ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_1023a\n");
    __builtin_unreachable();
}

/* Original0x101F0..0x101F6. */
REGION void tsl9_record_state_controls_block_101f0(void)
{
    REGS;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_state_controls_edge_101f2:\n.option push\n.option norvc\nbeq a0,a3,.Lrecord_state_controls_edge_101f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_state_controls_block_10258\n");
    __builtin_unreachable();
}

/* Original0x101F6..0x101FC. */
REGION void tsl9_record_state_controls_block_101f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x101FC..0x1020C. */
REGION void tsl9_record_state_controls_block_101fc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lrecord_state_controls_edge_1020a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_1020a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_101f6\n");
    __builtin_unreachable();
}

/* Original0x1020C..0x10216. */
REGION void tsl9_record_state_controls_block_1020c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000130)) = (uint8_t)a4; LIVE;
    PORT(".Lrecord_state_controls_edge_10212:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_10212\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x10216..0x10220. */
REGION void tsl9_record_state_controls_block_10216(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_state_controls_edge_1021c:\n.option push\n.option norvc\njal zero,.Lrecord_state_controls_edge_1021c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_provider_1016e\n");
    __builtin_unreachable();
}

/* Original0x10220..0x1022E. */
REGION void tsl9_record_state_controls_block_10220(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_state_controls_edge_1022c:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_state_controls_edge_1022c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_101f6\n");
    __builtin_unreachable();
}

/* Original0x1022E..0x10238. */
REGION void tsl9_record_state_controls_block_1022e(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000131)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_state_controls_edge_10234:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_10234\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x10238..0x1023A. */
REGION void tsl9_record_state_controls_block_10238(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_10238:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_10238\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_10216\n");
    __builtin_unreachable();
}

/* Original0x1023A..0x1024A. */
REGION void tsl9_record_state_controls_block_1023a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lrecord_state_controls_edge_10248:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_10248\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_101f6\n");
    __builtin_unreachable();
}

/* Original0x1024A..0x10256. */
REGION void tsl9_record_state_controls_block_1024a(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000132)) = (uint8_t)a4; LIVE;
    PORT(".Lrecord_state_controls_edge_10252:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_10252\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x10256..0x10258. */
REGION void tsl9_record_state_controls_block_10256(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_10256:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_10256\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_10216\n");
    __builtin_unreachable();
}

/* Original0x10258..0x10268. */
REGION void tsl9_record_state_controls_block_10258(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lrecord_state_controls_edge_10266:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_state_controls_edge_10266\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_state_controls_block_101f6\n");
    __builtin_unreachable();
}

/* Original0x10268..0x10274. */
REGION void tsl9_record_state_controls_block_10268(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000133)) = (uint8_t)a4; LIVE;
    PORT(".Lrecord_state_controls_edge_10270:\n.option push\n.option norvc\njal ra,.Lrecord_state_controls_edge_10270\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x10274..0x10276. */
REGION void tsl9_record_state_controls_block_10274(void)
{
    REGS;
    PORT(".Lrecord_state_controls_edge_10274:\n.option push\n.option rvc\nc.j .Lrecord_state_controls_edge_10274\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_block_10216\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
