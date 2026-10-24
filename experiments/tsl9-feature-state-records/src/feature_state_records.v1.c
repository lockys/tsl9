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

/* Nineteen complete feature-state functions:1260B/424i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x1056E..0x1057E. */
REGION void tsl9_feature_state_records_provider_1056e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0xfffffff7); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lfeature_state_records_edge_1057a:\n.option push\n.option norvc\nbltu a4,a5,.Lfeature_state_records_edge_1057a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10598\n");
    __builtin_unreachable();
}

/* Original0x1057E..0x10586. */
REGION void tsl9_feature_state_records_block_1057e(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_edge_10584:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_10584\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10594\n");
    __builtin_unreachable();
}

/* Original0x10586..0x1058C. */
REGION void tsl9_feature_state_records_block_10586(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lfeature_state_records_edge_1058a:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_1058a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10594\n");
    __builtin_unreachable();
}

/* Original0x1058C..0x10594. */
REGION void tsl9_feature_state_records_block_1058c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x10594..0x10598. */
REGION void tsl9_feature_state_records_block_10594(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10598..0x1059C. */
REGION void tsl9_feature_state_records_block_10598(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_edge_1059a:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_1059a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10594\n");
    __builtin_unreachable();
}

/* Original0x1059C..0x105A2. */
REGION void tsl9_feature_state_records_provider_1059c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".Lfeature_state_records_edge_105a0:\n.option push\n.option rvc\nc.bnez a5,.Lfeature_state_records_edge_105a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105c0\n");
    __builtin_unreachable();
}

/* Original0x105A2..0x105A8. */
REGION void tsl9_feature_state_records_block_105a2(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lfeature_state_records_edge_105a6:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_105a6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105bc\n");
    __builtin_unreachable();
}

/* Original0x105A8..0x105AE. */
REGION void tsl9_feature_state_records_block_105a8(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lfeature_state_records_edge_105ac:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_105ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105bc\n");
    __builtin_unreachable();
}

/* Original0x105AE..0x105B4. */
REGION void tsl9_feature_state_records_block_105ae(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lfeature_state_records_edge_105b2:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_105b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105bc\n");
    __builtin_unreachable();
}

/* Original0x105B4..0x105BC. */
REGION void tsl9_feature_state_records_block_105b4(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)); LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x105BC..0x105C0. */
REGION void tsl9_feature_state_records_block_105bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x105C0..0x105C4. */
REGION void tsl9_feature_state_records_block_105c0(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_edge_105c2:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_105c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_105bc\n");
    __builtin_unreachable();
}

/* Original0x105C4..0x105D0. */
REGION void tsl9_feature_state_records_provider_105c4(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a0 = a0 + UINT32_C(0xfffffffc); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x105D0..0x105D6. */
REGION void tsl9_feature_state_records_provider_105d0(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    PORT(".Lfeature_state_records_edge_105d4:\n.option push\n.option rvc\nc.bnez a5,.Lfeature_state_records_edge_105d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105e8\n");
    __builtin_unreachable();
}

/* Original0x105D6..0x105DC. */
REGION void tsl9_feature_state_records_block_105d6(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lfeature_state_records_edge_105da:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_105da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_105e4\n");
    __builtin_unreachable();
}

/* Original0x105DC..0x105E4. */
REGION void tsl9_feature_state_records_block_105dc(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)); LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x105E4..0x105E8. */
REGION void tsl9_feature_state_records_block_105e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x105E8..0x105EC. */
REGION void tsl9_feature_state_records_block_105e8(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_edge_105ea:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_105ea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_105e4\n");
    __builtin_unreachable();
}

/* Original0x105EC..0x105F6. */
REGION void tsl9_feature_state_records_provider_105ec(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lfeature_state_records_edge_105f2:\n.option push\n.option norvc\nbltu a5,a4,.Lfeature_state_records_edge_105f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10618\n");
    __builtin_unreachable();
}

/* Original0x105F6..0x10606. */
REGION void tsl9_feature_state_records_block_105f6(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    a3 = a5 & UINT32_C(0x000000df); LIVE;
    PORT(".Lfeature_state_records_edge_10602:\n.option push\n.option norvc\nbeq a3,a4,.Lfeature_state_records_edge_10602\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_1061a\n");
    __builtin_unreachable();
}

/* Original0x10606..0x1060E. */
REGION void tsl9_feature_state_records_block_10606(void)
{
    REGS;
    a4 = UINT32_C(0x00000020); LIVE;
    PORT(".Lfeature_state_records_edge_1060a:\n.option push\n.option norvc\nbeq a5,a4,.Lfeature_state_records_edge_1060a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_1061a\n");
    __builtin_unreachable();
}

/* Original0x1060E..0x10618. */
REGION void tsl9_feature_state_records_block_1060e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffff0c); LIVE;
    a0 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10618..0x1061A. */
REGION void tsl9_feature_state_records_block_10618(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1061A..0x1061C. */
REGION void tsl9_feature_state_records_block_1061a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x106C0..0x106CE. */
REGION void tsl9_feature_state_records_provider_106c0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lfeature_state_records_edge_106ca:\n.option push\n.option norvc\nbltz a5,.Lfeature_state_records_edge_106ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_106de\n");
    __builtin_unreachable();
}

/* Original0x106CE..0x106DE. */
REGION void tsl9_feature_state_records_block_106ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffc\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffff8ee); LIVE;
    a1 = UINT32_C(0x00000052); LIVE;
    PORT(".Lfeature_state_records_edge_106da:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_106da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0x106DE..0x106E0. */
REGION void tsl9_feature_state_records_block_106de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x106E0..0x106E8. */
REGION void tsl9_feature_state_records_provider_106e0(void)
{
    REGS;
    a0 = UINT32_C(0x00000052); LIVE;
    PORT(".Lfeature_state_records_edge_106e4:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_106e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_106c0\n");
    __builtin_unreachable();
}

/* Original0x107C6..0x107D8. */
REGION void tsl9_feature_state_records_provider_107c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nmv s1, a2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x107D8..0x107DA. */
REGION void tsl9_feature_state_records_block_107d8(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_107d8:\n.option push\n.option rvc\nc.beqz a0,.Lfeature_state_records_edge_107d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10810\n");
    __builtin_unreachable();
}

/* Original0x107DA..0x107EA. */
REGION void tsl9_feature_state_records_block_107da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lfeature_state_records_edge_107e6:\n.option push\n.option norvc\nbleu a1,a5,.Lfeature_state_records_edge_107e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_107f8\n");
    __builtin_unreachable();
}

/* Original0x107EA..0x107EE. */
REGION void tsl9_feature_state_records_block_107ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 0(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x107EE..0x107F8. */
REGION void tsl9_feature_state_records_block_107ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x107F8..0x10802. */
REGION void tsl9_feature_state_records_block_107f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_edge_107fe:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_107fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_clear_820c\n");
    __builtin_unreachable();
}

/* Original0x10802..0x10810. */
REGION void tsl9_feature_state_records_block_10802(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lfeature_state_records_edge_1080c:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_1080c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1074c\n");
    __builtin_unreachable();
}

/* Original0x10810..0x10816. */
REGION void tsl9_feature_state_records_block_10810(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s0)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10814:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10814\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_107ee\n");
    __builtin_unreachable();
}

/* Original0x10870..0x10880. */
REGION void tsl9_feature_external_10870(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lfeature_state_records_edge_1087e:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_1087e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_108c0\n");
    __builtin_unreachable();
}

/* Original0x10880..0x10886. */
REGION void tsl9_feature_state_records_block_10880(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lfeature_state_records_edge_10884:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_10884\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_108c6\n");
    __builtin_unreachable();
}

/* Original0x10886..0x1088C. */
REGION void tsl9_feature_state_records_block_10886(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lfeature_state_records_edge_1088a:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_1088a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_108cc\n");
    __builtin_unreachable();
}

/* Original0x1088C..0x10890. */
REGION void tsl9_feature_state_records_block_1088c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lfeature_state_records_edge_1088e:\n.option push\n.option rvc\nc.bnez a5,.Lfeature_state_records_edge_1088e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_108d2\n");
    __builtin_unreachable();
}

/* Original0x10890..0x1089C. */
REGION void tsl9_feature_state_records_block_10890(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nli s0, 82\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lfeature_state_records_edge_1089a:\n.option push\n.option rvc\nc.beqz a5,.Lfeature_state_records_edge_1089a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_108b4\n");
    __builtin_unreachable();
}

/* Original0x1089C..0x108A0. */
REGION void tsl9_feature_state_records_block_1089c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 87\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x108A0..0x108B4. */
REGION void tsl9_feature_state_records_block_108a0(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000258); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lfeature_state_records_literal_108a8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_106e0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_108a8\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108b0:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_108b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x108B4..0x108C0. */
REGION void tsl9_feature_state_records_block_108b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108bc:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_108bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_106c0\n");
    __builtin_unreachable();
}

/* Original0x108C0..0x108C6. */
REGION void tsl9_feature_state_records_block_108c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 83\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108c4:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_108c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_108a0\n");
    __builtin_unreachable();
}

/* Original0x108C6..0x108CC. */
REGION void tsl9_feature_state_records_block_108c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 84\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108ca:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_108ca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_108a0\n");
    __builtin_unreachable();
}

/* Original0x108CC..0x108D2. */
REGION void tsl9_feature_state_records_block_108cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 85\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108d0:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_108d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_108a0\n");
    __builtin_unreachable();
}

/* Original0x108D2..0x108D8. */
REGION void tsl9_feature_state_records_block_108d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 86\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108d6:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_108d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_108a0\n");
    __builtin_unreachable();
}

/* Original0x108D8..0x108EE. */
REGION void tsl9_feature_external_108d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lfeature_state_records_literal_108e0:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_1056e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_108e0\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_108ea:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_108ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1083c\n");
    __builtin_unreachable();
}

/* Original0x108EE..0x108F0. */
REGION void tsl9_feature_state_records_block_108ee(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_108ee:\n.option push\n.option rvc\nc.beqz a0,.Lfeature_state_records_edge_108ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_1092e\n");
    __builtin_unreachable();
}

/* Original0x108F0..0x108FA. */
REGION void tsl9_feature_state_records_block_108f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000006c8)); LIVE;
    PORT(".Lfeature_state_records_edge_108f8:\n.option push\n.option rvc\nc.beqz a5,.Lfeature_state_records_edge_108f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_1092e\n");
    __builtin_unreachable();
}

/* Original0x108FA..0x1092E. */
REGION void tsl9_feature_state_records_block_108fa(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    PORT(".Lfeature_state_records_literal_10904:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_static_data_1a4e4\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10904\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 10(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_1092a:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_1092a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x1092E..0x10936. */
REGION void tsl9_feature_state_records_block_1092e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10936..0x10944. */
REGION void tsl9_feature_external_10936(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".Lfeature_state_records_literal_10938:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_1059c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10938\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10940:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10940\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1083c\n");
    __builtin_unreachable();
}

/* Original0x10944..0x1095A. */
REGION void tsl9_feature_external_10944(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lfeature_state_records_literal_1094c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105c4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_1094c\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10956:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_10956\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1083c\n");
    __builtin_unreachable();
}

/* Original0x1095A..0x1095C. */
REGION void tsl9_feature_state_records_block_1095a(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_1095a:\n.option push\n.option rvc\nc.beqz a0,.Lfeature_state_records_edge_1095a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_109bc\n");
    __builtin_unreachable();
}

/* Original0x1095C..0x10966. */
REGION void tsl9_feature_state_records_block_1095c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000065c)); LIVE;
    PORT(".Lfeature_state_records_edge_10964:\n.option push\n.option rvc\nc.beqz a5,.Lfeature_state_records_edge_10964\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_109bc\n");
    __builtin_unreachable();
}

/* Original0x10966..0x109BC. */
REGION void tsl9_feature_state_records_block_10966(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 7(s0)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a4 = a4 + UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    a4 = a4 | a3; LIVE;
    a5 = a5 + UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option norvc\nsh a4, 4(s0)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsh a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000019); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_109b8:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_109b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x109BC..0x109C4. */
REGION void tsl9_feature_state_records_block_109bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x109C4..0x109DA. */
REGION void tsl9_feature_external_109c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lfeature_state_records_literal_109cc:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105d0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_109cc\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_109d6:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_109d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1083c\n");
    __builtin_unreachable();
}

/* Original0x109DA..0x109DC. */
REGION void tsl9_feature_state_records_block_109da(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_109da:\n.option push\n.option rvc\nc.beqz a0,.Lfeature_state_records_edge_109da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_109f8\n");
    __builtin_unreachable();
}

/* Original0x109DC..0x109E6. */
REGION void tsl9_feature_state_records_block_109dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000005dc)); LIVE;
    PORT(".Lfeature_state_records_edge_109e4:\n.option push\n.option rvc\nc.beqz a5,.Lfeature_state_records_edge_109e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_109f8\n");
    __builtin_unreachable();
}

/* Original0x109E6..0x109F8. */
REGION void tsl9_feature_state_records_block_109e6(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_109f4:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_109f4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x109F8..0x10A00. */
REGION void tsl9_feature_state_records_block_109f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10A00..0x10A0A. */
REGION void tsl9_feature_external_10a00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005b8)); LIVE;
    PORT(".Lfeature_state_records_edge_10a08:\n.option push\n.option rvc\nc.beqz a4,.Lfeature_state_records_edge_10a08\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10a14\n");
    __builtin_unreachable();
}

/* Original0x10A0A..0x10A14. */
REGION void tsl9_feature_state_records_block_10a0a(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint8_t)a4; LIVE;
    PORT(".Lfeature_state_records_edge_10a10:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10a10\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x10A14..0x10A16. */
REGION void tsl9_feature_state_records_block_10a14(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10A16..0x10A2C. */
REGION void tsl9_feature_external_10a16(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lfeature_state_records_literal_10a1e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105ec\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10a1e\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10a28:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_10a28\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_1083c\n");
    __builtin_unreachable();
}

/* Original0x10A2C..0x10A2E. */
REGION void tsl9_feature_state_records_block_10a2c(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_10a2c:\n.option push\n.option rvc\nc.beqz a0,.Lfeature_state_records_edge_10a2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10abe\n");
    __builtin_unreachable();
}

/* Original0x10A2E..0x10A38. */
REGION void tsl9_feature_state_records_block_10a2e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000058a)); LIVE;
    PORT(".Lfeature_state_records_edge_10a36:\n.option push\n.option rvc\nc.beqz a5,.Lfeature_state_records_edge_10a36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10abe\n");
    __builtin_unreachable();
}

/* Original0x10A38..0x10A5A. */
REGION void tsl9_feature_state_records_block_10a38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a4 = UINT32_C(0x0000000f); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nrem a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x00000030); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000578)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10a58:\n.option push\n.option rvc\nc.beqz a4,.Lfeature_state_records_edge_10a58\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10a80\n");
    __builtin_unreachable();
}

/* Original0x10A5A..0x10A72. */
REGION void tsl9_feature_state_records_block_10a5a(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10a5a:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_static_data_1a518\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10a5a\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00003000); LIVE;
    a5 = a5 + UINT32_C(0xfffffe2b); LIVE;
    __builtin_unreachable();
}

/* Original0x10A72..0x10A80. */
REGION void tsl9_feature_state_records_block_10a72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 10(s0)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10a7e:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10a7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10a98\n");
    __builtin_unreachable();
}

/* Original0x10A80..0x10A86. */
REGION void tsl9_feature_state_records_block_10a80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 6(s0)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10a84:\n.option push\n.option rvc\nc.bnez a4,.Lfeature_state_records_edge_10a84\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10aa4\n");
    __builtin_unreachable();
}

/* Original0x10A86..0x10A98. */
REGION void tsl9_feature_state_records_block_10a86(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10a86:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_static_data_1a528\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10a86\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10A98..0x10AA4. */
REGION void tsl9_feature_state_records_block_10a98(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10aa0:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10aa0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x10AA4..0x10ABE. */
REGION void tsl9_feature_state_records_block_10aa4(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10aa4:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_static_data_1a538\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10aa4\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00006000); LIVE;
    a5 = a5 + UINT32_C(0xfffff95d); LIVE;
    PORT(".Lfeature_state_records_edge_10abc:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10abc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10a72\n");
    __builtin_unreachable();
}

/* Original0x10ABE..0x10AC6. */
REGION void tsl9_feature_state_records_block_10abe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10AC6..0x10AD4. */
REGION void tsl9_feature_external_10ac6(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000053); LIVE;
    a3 = a4 & UINT32_C(0x00000040); LIVE;
    PORT(".Lfeature_state_records_edge_10ad2:\n.option push\n.option rvc\nc.bnez a3,.Lfeature_state_records_edge_10ad2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b04\n");
    __builtin_unreachable();
}

/* Original0x10AD4..0x10AE2. */
REGION void tsl9_feature_state_records_block_10ad4(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = UINT32_C(0x00000054); LIVE;
    a2 = a3 & UINT32_C(0x00000020); LIVE;
    PORT(".Lfeature_state_records_edge_10ae0:\n.option push\n.option rvc\nc.bnez a2,.Lfeature_state_records_edge_10ae0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b04\n");
    __builtin_unreachable();
}

/* Original0x10AE2..0x10AF0. */
REGION void tsl9_feature_state_records_block_10ae2(void)
{
    REGS;
    a2 = a4 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a2, a2, 0x18\n.option pop\n");
    a5 = UINT32_C(0x00000055); LIVE;
    PORT(".Lfeature_state_records_edge_10aec:\n.option push\n.option norvc\nbltz a2,.Lfeature_state_records_edge_10aec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10b04\n");
    __builtin_unreachable();
}

/* Original0x10AF0..0x10AF8. */
REGION void tsl9_feature_state_records_block_10af0(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000056); LIVE;
    PORT(".Lfeature_state_records_edge_10af6:\n.option push\n.option rvc\nc.bnez a3,.Lfeature_state_records_edge_10af6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b04\n");
    __builtin_unreachable();
}

/* Original0x10AF8..0x10B00. */
REGION void tsl9_feature_state_records_block_10af8(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000052); LIVE;
    PORT(".Lfeature_state_records_edge_10afe:\n.option push\n.option rvc\nc.beqz a4,.Lfeature_state_records_edge_10afe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b04\n");
    __builtin_unreachable();
}

/* Original0x10B00..0x10B04. */
REGION void tsl9_feature_state_records_block_10b00(void)
{
    REGS;
    a5 = UINT32_C(0x00000057); LIVE;
    __builtin_unreachable();
}

/* Original0x10B04..0x10B0A. */
REGION void tsl9_feature_state_records_block_10b04(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10b06:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10b06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_106c0\n");
    __builtin_unreachable();
}

/* Original0x10B0A..0x10B22. */
REGION void tsl9_feature_external_10b0a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004b8)) = (uint8_t)a5; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = UINT32_C(0x00000057); LIVE;
    a3 = a4 & UINT32_C(0x00000040); LIVE;
    PORT(".Lfeature_state_records_edge_10b20:\n.option push\n.option rvc\nc.bnez a3,.Lfeature_state_records_edge_10b20\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B22..0x10B30. */
REGION void tsl9_feature_state_records_block_10b22(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = UINT32_C(0x00000056); LIVE;
    a2 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lfeature_state_records_edge_10b2e:\n.option push\n.option rvc\nc.bnez a2,.Lfeature_state_records_edge_10b2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B30..0x10B3A. */
REGION void tsl9_feature_state_records_block_10b30(void)
{
    REGS;
    a2 = a3 & UINT32_C(0x00000002); LIVE;
    a5 = UINT32_C(0x00000054); LIVE;
    PORT(".Lfeature_state_records_edge_10b38:\n.option push\n.option rvc\nc.bnez a2,.Lfeature_state_records_edge_10b38\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B3A..0x10B42. */
REGION void tsl9_feature_state_records_block_10b3a(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000004); LIVE;
    a5 = UINT32_C(0x00000052); LIVE;
    PORT(".Lfeature_state_records_edge_10b40:\n.option push\n.option rvc\nc.beqz a3,.Lfeature_state_records_edge_10b40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B42..0x10B4C. */
REGION void tsl9_feature_state_records_block_10b42(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000053); LIVE;
    PORT(".Lfeature_state_records_edge_10b4a:\n.option push\n.option rvc\nc.bnez a3,.Lfeature_state_records_edge_10b4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B4C..0x10B56. */
REGION void tsl9_feature_state_records_block_10b4c(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000020); LIVE;
    a5 = UINT32_C(0x00000052); LIVE;
    PORT(".Lfeature_state_records_edge_10b54:\n.option push\n.option rvc\nc.beqz a4,.Lfeature_state_records_edge_10b54\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_feature_state_records_block_10b5a\n");
    __builtin_unreachable();
}

/* Original0x10B56..0x10B5A. */
REGION void tsl9_feature_state_records_block_10b56(void)
{
    REGS;
    a5 = UINT32_C(0x00000055); LIVE;
    __builtin_unreachable();
}

/* Original0x10B5A..0x10B60. */
REGION void tsl9_feature_state_records_block_10b5a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10b5c:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10b5c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_106c0\n");
    __builtin_unreachable();
}

/* Original0x10B60..0x10B6E. */
REGION void tsl9_feature_external_10b60(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000334); LIVE;
    PORT(".option push\n.option rvc\nmv a4, a0\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10b6a:\n.option push\n.option norvc\nbeq a5,a3,.Lfeature_state_records_edge_10b6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10bae\n");
    __builtin_unreachable();
}

/* Original0x10B6E..0x10B72. */
REGION void tsl9_feature_state_records_block_10b6e(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_10b6e:\n.option push\n.option norvc\nbltu a3,a5,.Lfeature_state_records_edge_10b6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10b84\n");
    __builtin_unreachable();
}

/* Original0x10B72..0x10B7A. */
REGION void tsl9_feature_state_records_block_10b72(void)
{
    REGS;
    a3 = UINT32_C(0x00000189); LIVE;
    PORT(".Lfeature_state_records_edge_10b76:\n.option push\n.option norvc\nbeq a5,a3,.Lfeature_state_records_edge_10b76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10c0a\n");
    __builtin_unreachable();
}

/* Original0x10B7A..0x10B82. */
REGION void tsl9_feature_state_records_block_10b7a(void)
{
    REGS;
    a3 = UINT32_C(0x0000021c); LIVE;
    PORT(".Lfeature_state_records_edge_10b7e:\n.option push\n.option norvc\nbeq a5,a3,.Lfeature_state_records_edge_10b7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10bc2\n");
    __builtin_unreachable();
}

/* Original0x10B82..0x10B84. */
REGION void tsl9_feature_state_records_block_10b82(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10B84..0x10B8C. */
REGION void tsl9_feature_state_records_block_10b84(void)
{
    REGS;
    a3 = UINT32_C(0x000003e9); LIVE;
    PORT(".Lfeature_state_records_edge_10b88:\n.option push\n.option norvc\nbeq a5,a3,.Lfeature_state_records_edge_10b88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10bae\n");
    __builtin_unreachable();
}

/* Original0x10B8C..0x10B94. */
REGION void tsl9_feature_state_records_block_10b8c(void)
{
    REGS;
    a3 = UINT32_C(0x00000498); LIVE;
    PORT(".Lfeature_state_records_edge_10b90:\n.option push\n.option norvc\nbeq a5,a3,.Lfeature_state_records_edge_10b90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10bf8\n");
    __builtin_unreachable();
}

/* Original0x10B94..0x10B9C. */
REGION void tsl9_feature_state_records_block_10b94(void)
{
    REGS;
    a3 = UINT32_C(0x000003a1); LIVE;
    PORT(".Lfeature_state_records_edge_10b98:\n.option push\n.option norvc\nbne a5,a3,.Lfeature_state_records_edge_10b98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_state_records_block_10c1c\n");
    __builtin_unreachable();
}

/* Original0x10B9C..0x10BAE. */
REGION void tsl9_feature_state_records_block_10b9c(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10b9c:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105ec\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10b9c\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000145); LIVE;
    PORT(".Lfeature_state_records_edge_10bac:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10bac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10bbe\n");
    __builtin_unreachable();
}

/* Original0x10BAE..0x10BBE. */
REGION void tsl9_feature_state_records_block_10bae(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10bae:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_predicate_1069e\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10bae\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000142); LIVE;
    __builtin_unreachable();
}

/* Original0x10BBE..0x10BC2. */
REGION void tsl9_feature_state_records_block_10bbe(void)
{
    REGS;
    PORT(".Lfeature_state_records_edge_10bbe:\n.option push\n.option norvc\njal zero,.Lfeature_state_records_edge_10bbe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_107c6\n");
    __builtin_unreachable();
}

/* Original0x10BC2..0x10BDE. */
REGION void tsl9_feature_state_records_block_10bc2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_literal_10bc6:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_1056e\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10bc6\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000146); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10bda:\n.option push\n.option norvc\njal ra,.Lfeature_state_records_edge_10bda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_107c6\n");
    __builtin_unreachable();
}

/* Original0x10BDE..0x10BF8. */
REGION void tsl9_feature_state_records_block_10bde(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".Lfeature_state_records_literal_10be4:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105c4\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10be4\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000147); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lfeature_state_records_edge_10bf6:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10bf6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10bbe\n");
    __builtin_unreachable();
}

/* Original0x10BF8..0x10C0A. */
REGION void tsl9_feature_state_records_block_10bf8(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10bf8:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_1059c\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10bf8\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000143); LIVE;
    PORT(".Lfeature_state_records_edge_10c08:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10c08\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10bbe\n");
    __builtin_unreachable();
}

/* Original0x10C0A..0x10C1C. */
REGION void tsl9_feature_state_records_block_10c0a(void)
{
    REGS;
    PORT(".Lfeature_state_records_literal_10c0a:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_feature_state_records_provider_105d0\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lfeature_state_records_literal_10c0a\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000144); LIVE;
    PORT(".Lfeature_state_records_edge_10c1a:\n.option push\n.option rvc\nc.j .Lfeature_state_records_edge_10c1a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_state_records_block_10bbe\n");
    __builtin_unreachable();
}

/* Original0x10C1C..0x10C1E. */
REGION void tsl9_feature_state_records_block_10c1c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10C1E..0x10C34. */
REGION void tsl9_main_services_provider_10c1e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000038a); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10C34..0x10C36. */
REGION void tsl9_feature_state_records_block_10c34(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
