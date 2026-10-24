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

/* Six complete output/control functions:956B/298i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9AE4..0x9AF0. */
REGION void tsl9_action_primitives_provider_9ae4(void)
{
    REGS;
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff814)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB6F4..0xB702. */
REGION void tsl9_record_dispatch_provider_b6f4(void)
{
    REGS;
    a5 = a0 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000011); LIVE;
    PORT(".Loutput_builder_edge_b6fe:\n.option push\n.option norvc\nbltu a4,a5,.Loutput_builder_edge_b6fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_b72e\n");
    __builtin_unreachable();
}

/* Original0xB702..0xB70E. */
REGION void tsl9_output_builder_block_b702(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Loutput_builder_edge_b70a:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_b70a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0xB70E..0xB714. */
REGION void tsl9_output_builder_block_b70e(void)
{
    REGS;
    a5 = UINT32_C(0x0000000b); LIVE;
    PORT(".Loutput_builder_edge_b710:\n.option push\n.option norvc\nbleu s0,a5,.Loutput_builder_edge_b710\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_b71a\n");
    __builtin_unreachable();
}

/* Original0xB714..0xB71A. */
REGION void tsl9_output_builder_block_b714(void)
{
    REGS;
    a5 = UINT32_C(0x00000012); LIVE;
    PORT(".Loutput_builder_edge_b716:\n.option push\n.option norvc\nbne s0,a5,.Loutput_builder_edge_b716\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_b71e\n");
    __builtin_unreachable();
}

/* Original0xB71A..0xB71E. */
REGION void tsl9_output_builder_block_b71a(void)
{
    REGS;
    PORT(".Loutput_builder_edge_b71a:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_b71a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_9fc8\n");
    __builtin_unreachable();
}

/* Original0xB71E..0xB72E. */
REGION void tsl9_output_builder_block_b71e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 2030(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB72E..0xB730. */
REGION void tsl9_output_builder_block_b72e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDEA0..0xDEAC. */
REGION void tsl9_record_dispatch_provider_dea0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Loutput_builder_edge_dea8:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_dea8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xDEAC..0xDEAE. */
REGION void tsl9_output_builder_block_deac(void)
{
    REGS;
    PORT(".Loutput_builder_edge_deac:\n.option push\n.option rvc\nc.bnez a0,.Loutput_builder_edge_deac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_ded6\n");
    __builtin_unreachable();
}

/* Original0xDEAE..0xDEBA. */
REGION void tsl9_output_builder_block_deae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 210(a5)\n.option pop\n");
    PORT(".Loutput_builder_edge_deb6:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_deb6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f822\n");
    __builtin_unreachable();
}

/* Original0xDEBA..0xDEBC. */
REGION void tsl9_output_builder_block_deba(void)
{
    REGS;
    PORT(".Loutput_builder_edge_deba:\n.option push\n.option rvc\nc.bnez a0,.Loutput_builder_edge_deba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_dece\n");
    __builtin_unreachable();
}

/* Original0xDEBC..0xDEC2. */
REGION void tsl9_output_builder_block_debc(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Loutput_builder_edge_debe:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_debe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f818\n");
    __builtin_unreachable();
}

/* Original0xDEC2..0xDECE. */
REGION void tsl9_output_builder_block_dec2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Loutput_builder_edge_deca:\n.option push\n.option norvc\njal zero,.Loutput_builder_edge_deca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0xDECE..0xDED4. */
REGION void tsl9_output_builder_block_dece(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Loutput_builder_edge_ded0:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_ded0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_d810\n");
    __builtin_unreachable();
}

/* Original0xDED4..0xDED6. */
REGION void tsl9_output_builder_block_ded4(void)
{
    REGS;
    PORT(".Loutput_builder_edge_ded4:\n.option push\n.option rvc\nc.j .Loutput_builder_edge_ded4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_builder_block_dec2\n");
    __builtin_unreachable();
}

/* Original0xDED6..0xDEE2. */
REGION void tsl9_output_builder_block_ded6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Loutput_builder_edge_dede:\n.option push\n.option norvc\njal zero,.Loutput_builder_edge_dede\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0x17C4E..0x17CAC. */
REGION void tsl9_action_primitives_provider_17c4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = UINT32_C(0x000004f3); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffcc6); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)) = (uint8_t)a4; LIVE;
    a4 = a5 & UINT32_C(0x000000ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a4; LIVE;
    a4 = a5 >> UINT32_C(0x00000008); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint8_t)a4; LIVE;
    a4 = a5 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)); LIVE;
    a5 = a5 >> UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)) = (uint8_t)a5; LIVE;
    PORT(".Loutput_builder_edge_17ca8:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17ca8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x17CAC..0x17CB2. */
REGION void tsl9_output_builder_block_17cac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17CB2..0x17CBA. */
REGION void tsl9_output_builder_provider_17cb2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a7, 0(a0)\n.option pop\n");
    PORT(".Loutput_builder_edge_17cb6:\n.option push\n.option norvc\nbeqz a7,.Loutput_builder_edge_17cb6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17ce0\n");
    __builtin_unreachable();
}

/* Original0x17CBA..0x17CC6. */
REGION void tsl9_output_builder_block_17cba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a7, a5, a6\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a7, a7, 5\n.option pop\n");
    PORT(".option push\n.option rvc\nli t1, 10\n.option pop\n");
    PORT(".Loutput_builder_edge_17cc2:\n.option push\n.option norvc\nbltu t1,a7,.Loutput_builder_edge_17cc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17ccc\n");
    __builtin_unreachable();
}

/* Original0x17CC6..0x17CCC. */
REGION void tsl9_output_builder_block_17cc6(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17CCC..0x17CD2. */
REGION void tsl9_output_builder_block_17ccc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsltu a7, a6, a5\n.option pop\n");
    PORT(".Loutput_builder_edge_17cd0:\n.option push\n.option rvc\nc.beqz a1,.Loutput_builder_edge_17cd0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17ce2\n");
    __builtin_unreachable();
}

/* Original0x17CD2..0x17CDA. */
REGION void tsl9_output_builder_block_17cd2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a7, 0(a0)\n.option pop\n");
    PORT(".Loutput_builder_edge_17cd6:\n.option push\n.option norvc\nbleu a5,a6,.Loutput_builder_edge_17cd6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17ce0\n");
    __builtin_unreachable();
}

/* Original0x17CDA..0x17CDE. */
REGION void tsl9_output_builder_block_17cda(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a3; LIVE;
    __builtin_unreachable();
}

/* Original0x17CDE..0x17CE0. */
REGION void tsl9_output_builder_block_17cde(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x17CE0..0x17CE2. */
REGION void tsl9_output_builder_block_17ce0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17CE2..0x17CEE. */
REGION void tsl9_output_builder_block_17ce2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a7, a7, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a7, 0(a0)\n.option pop\n");
    PORT(".Loutput_builder_edge_17cea:\n.option push\n.option norvc\nbltu a6,a5,.Loutput_builder_edge_17cea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17ce0\n");
    __builtin_unreachable();
}

/* Original0x17CEE..0x17CF4. */
REGION void tsl9_output_builder_block_17cee(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".Loutput_builder_edge_17cf2:\n.option push\n.option rvc\nc.j .Loutput_builder_edge_17cf2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_builder_block_17cde\n");
    __builtin_unreachable();
}

/* Original0x17CF4..0x17D0A. */
REGION void tsl9_output_builder_provider_17cf4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc34)); LIVE;
    PORT(".Loutput_builder_edge_17d06:\n.option push\n.option norvc\nbeqz a5,.Loutput_builder_edge_17d06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17e0e\n");
    __builtin_unreachable();
}

/* Original0x17D0A..0x17D14. */
REGION void tsl9_output_builder_block_17d0a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Loutput_builder_edge_17d10:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17d10\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0x17D14..0x17D48. */
REGION void tsl9_output_builder_block_17d14(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nlw a6, 4(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x1b\n.option pop\n");
    PORT(".option push\n.option norvc\nor a6, a5, a6\n.option pop\n");
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc12)); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffbff)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffbfb); LIVE;
    PORT(".Loutput_builder_edge_17d44:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17d44\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17D48..0x17D84. */
REGION void tsl9_output_builder_block_17d48(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s0, 0x1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s0, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nand a6, a6, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbe0)); LIVE;
    a4 = UINT32_C(0x00000040); LIVE;
    a3 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffbc4)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffbc0); LIVE;
    PORT(".Loutput_builder_edge_17d80:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17d80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17D84..0x17DAC. */
REGION void tsl9_output_builder_block_17d84(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbba)); LIVE;
    a4 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x14\n.option pop\n");
    a3 = UINT32_C(0x00004000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffb9d)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb99); LIVE;
    PORT(".Loutput_builder_edge_17da8:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17da8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17DAC..0x17DDE. */
REGION void tsl9_output_builder_block_17dac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb93)); LIVE;
    PORT(".option push\n.option norvc\naddi a4, s0, -2048\n.option pop\n");
    PORT(".option push\n.option norvc\nand a6, a6, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    a3 = UINT32_C(0x00000400); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffb6c)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb68); LIVE;
    PORT(".Loutput_builder_edge_17dda:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17dda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17DDE..0x17DE8. */
REGION void tsl9_output_builder_block_17dde(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb59)); LIVE;
    PORT(".Loutput_builder_edge_17de6:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17de6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17e0e\n");
    __builtin_unreachable();
}

/* Original0x17DE8..0x17DF2. */
REGION void tsl9_output_builder_block_17de8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb50)); LIVE;
    PORT(".Loutput_builder_edge_17df0:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17df0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17e0e\n");
    __builtin_unreachable();
}

/* Original0x17DF2..0x17DFC. */
REGION void tsl9_output_builder_block_17df2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb47)); LIVE;
    PORT(".Loutput_builder_edge_17dfa:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17dfa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17e0e\n");
    __builtin_unreachable();
}

/* Original0x17DFC..0x17E06. */
REGION void tsl9_output_builder_block_17dfc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb3e)); LIVE;
    PORT(".Loutput_builder_edge_17e04:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17e04\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17e0e\n");
    __builtin_unreachable();
}

/* Original0x17E06..0x17E0E. */
REGION void tsl9_output_builder_block_17e06(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb2c)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x17E0E..0x17E1A. */
REGION void tsl9_output_builder_block_17e0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb36)); LIVE;
    PORT(".Loutput_builder_edge_17e16:\n.option push\n.option norvc\nbeqz a5,.Loutput_builder_edge_17e16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_builder_block_17f1a\n");
    __builtin_unreachable();
}

/* Original0x17E1A..0x17E24. */
REGION void tsl9_output_builder_block_17e1a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000011); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Loutput_builder_edge_17e20:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17e20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0x17E24..0x17E58. */
REGION void tsl9_output_builder_block_17e24(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nlw a6, 4(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x1b\n.option pop\n");
    PORT(".option push\n.option norvc\nor a6, a5, a6\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb14)); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffb01)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffafd); LIVE;
    PORT(".Loutput_builder_edge_17e54:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17e54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17E58..0x17E90. */
REGION void tsl9_output_builder_block_17e58(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s0, 0x1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s0, s0, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nand a6, a6, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffae4)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffaca)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffac6); LIVE;
    PORT(".Loutput_builder_edge_17e8c:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17e8c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17E90..0x17EB8. */
REGION void tsl9_output_builder_block_17e90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffac0)); LIVE;
    a4 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x14\n.option pop\n");
    a3 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffaa3)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffa9f); LIVE;
    PORT(".Loutput_builder_edge_17eb4:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17eb4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17EB8..0x17EEA. */
REGION void tsl9_output_builder_block_17eb8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a6, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa99)); LIVE;
    a4 = UINT32_C(0x00000200); LIVE;
    PORT(".option push\n.option norvc\nand a6, a6, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    a3 = UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffa72)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffa6e); LIVE;
    PORT(".Loutput_builder_edge_17ee6:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17ee6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_17cb2\n");
    __builtin_unreachable();
}

/* Original0x17EEA..0x17EF4. */
REGION void tsl9_output_builder_block_17eea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa5f)); LIVE;
    PORT(".Loutput_builder_edge_17ef2:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17ef2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f1a\n");
    __builtin_unreachable();
}

/* Original0x17EF4..0x17EFE. */
REGION void tsl9_output_builder_block_17ef4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa56)); LIVE;
    PORT(".Loutput_builder_edge_17efc:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17efc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f1a\n");
    __builtin_unreachable();
}

/* Original0x17EFE..0x17F08. */
REGION void tsl9_output_builder_block_17efe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa4d)); LIVE;
    PORT(".Loutput_builder_edge_17f06:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17f06\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f1a\n");
    __builtin_unreachable();
}

/* Original0x17F08..0x17F12. */
REGION void tsl9_output_builder_block_17f08(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa44)); LIVE;
    PORT(".Loutput_builder_edge_17f10:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17f10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f1a\n");
    __builtin_unreachable();
}

/* Original0x17F12..0x17F1A. */
REGION void tsl9_output_builder_block_17f12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa32)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x17F1A..0x17F36. */
REGION void tsl9_output_builder_block_17f1a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffa06); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa04)) = (uint16_t)a5; LIVE;
    PORT(".Loutput_builder_edge_17f34:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17f34\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f48\n");
    __builtin_unreachable();
}

/* Original0x17F36..0x17F48. */
REGION void tsl9_output_builder_block_17f36(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9fa)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa04)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x17F48..0x17F56. */
REGION void tsl9_output_builder_block_17f48(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xfffff9d6)) = (uint32_t)a5; LIVE;
    PORT(".Loutput_builder_edge_17f52:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17f52\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17c4e\n");
    __builtin_unreachable();
}

/* Original0x17F56..0x17F60. */
REGION void tsl9_output_builder_block_17f56(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9dc)); LIVE;
    PORT(".Loutput_builder_edge_17f5e:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17f5e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f76\n");
    __builtin_unreachable();
}

/* Original0x17F60..0x17F6A. */
REGION void tsl9_output_builder_block_17f60(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9e4)); LIVE;
    PORT(".Loutput_builder_edge_17f68:\n.option push\n.option rvc\nc.bnez a5,.Loutput_builder_edge_17f68\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_builder_block_17f76\n");
    __builtin_unreachable();
}

/* Original0x17F6A..0x17F76. */
REGION void tsl9_output_builder_block_17f6a(void)
{
    REGS;
    PORT(".Loutput_builder_literal_17f6a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_output_builder_provider_17cf4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loutput_builder_literal_17f6a\n.option pop\n");
    PORT(".Loutput_builder_edge_17f72:\n.option push\n.option norvc\njal ra,.Loutput_builder_edge_17f72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x17F76..0x17F80. */
REGION void tsl9_output_builder_block_17f76(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
