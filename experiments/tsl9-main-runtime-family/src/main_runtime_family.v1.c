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

/* Six complete original dependency functions:704B/241i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x8E88..0x8EA8. */
REGION void tsl9_main_provider_8e88(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    a2 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffff84c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20002\n.option pop\n");
    a0 = a0 + UINT32_C(0x000002f0); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8EA8..0x8EAC. */
REGION void tsl9_main_runtime_block_8ea8(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_8ea8:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_8ea8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_199e2\n");
    __builtin_unreachable();
}

/* Original0x8EAC..0x8EB0. */
REGION void tsl9_main_runtime_block_8eac(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_8eac:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_8eac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_19b16\n");
    __builtin_unreachable();
}

/* Original0x8EB0..0x8EB2. */
REGION void tsl9_main_runtime_block_8eb0(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_8eb0:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_8eb0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_table_entry_907a\n");
    __builtin_unreachable();
}

/* Original0x8EB2..0x8EB8. */
REGION void tsl9_main_runtime_block_8eb2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 416(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8EB8..0x8EBE. */
REGION void tsl9_main_runtime_block_8eb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 428(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8EBE..0x8EC4. */
REGION void tsl9_main_runtime_block_8ebe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 448(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8EC4..0x8ED2. */
REGION void tsl9_main_runtime_block_8ec4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".Lmain_runtime_literal_8ec8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_runtime_external_8614\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_runtime_literal_8ec8\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8ED2..0x8EF8. */
REGION void tsl9_main_runtime_block_8ed2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009d)) = (uint8_t)a0; LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x000003e8); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 372(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x11\n.option pop\n");
    a2 = a2 + UINT32_C(0xffffff04); LIVE;
    a1 = UINT32_C(0x0000000d); LIVE;
    a0 = UINT32_C(0x00000306); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8EF8..0x8F06. */
REGION void tsl9_main_runtime_block_8ef8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 372(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000311); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F06..0x8F16. */
REGION void tsl9_main_runtime_block_8f06(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 372(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 14\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000312); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F16..0x8F22. */
REGION void tsl9_main_runtime_block_8f16(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x000000a0); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F22..0x8F2E. */
REGION void tsl9_main_runtime_block_8f22(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x000000a0); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F2E..0x8F32. */
REGION void tsl9_main_runtime_block_8f2e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lmain_runtime_edge_8f30:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_8f30\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_8b6e\n");
    __builtin_unreachable();
}

/* Original0x8F32..0x8F44. */
REGION void tsl9_main_runtime_block_8f32(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lmain_runtime_edge_8f40:\n.option push\n.option norvc\nbeq a5,a4,.Lmain_runtime_edge_8f40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_runtime_block_8f5e\n");
    __builtin_unreachable();
}

/* Original0x8F44..0x8F5E. */
REGION void tsl9_main_runtime_block_8f44(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x12\n.option pop\n");
    a4 = a4 + UINT32_C(0xfffffbf0); LIVE;
    a5 = a5 + a4; LIVE;
    a1 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000019); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F5E..0x8F76. */
REGION void tsl9_main_runtime_block_8f5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 14\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000400); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F76..0x8F7E. */
REGION void tsl9_main_runtime_block_8f76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 196(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, -2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F7E..0x8F8C. */
REGION void tsl9_main_runtime_block_8f7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".Lmain_runtime_literal_8f82:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_runtime_external_8614\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_runtime_literal_8f82\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8F8C..0x8FA2. */
REGION void tsl9_main_runtime_block_8f8c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000094)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option norvc\nsh s1, 150(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".Lmain_runtime_literal_8f98:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_runtime_external_8614\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_runtime_literal_8f98\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FA2..0x8FB8. */
REGION void tsl9_main_runtime_block_8fa2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000098)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option norvc\nsh s1, 154(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 312(s0)\n.option pop\n");
    a0 = UINT32_C(0x00010000); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = original_gp + UINT32_C(0x00000080); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FB8..0x8FCE. */
REGION void tsl9_main_runtime_block_8fb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 304(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x11\n.option pop\n");
    a3 = a3 + UINT32_C(0xfffffe40); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nmv a0, gp\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FCE..0x8FD8. */
REGION void tsl9_main_runtime_block_8fce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 80(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000009d)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FD8..0x8FDC. */
REGION void tsl9_main_runtime_block_8fd8(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_8fd8:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_8fd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_12506\n");
    __builtin_unreachable();
}

/* Original0x8FDC..0x8FE0. */
REGION void tsl9_main_runtime_block_8fdc(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_8fdc:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_8fdc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_resident_providers_entry_175e8\n");
    __builtin_unreachable();
}

/* Original0x8FE0..0x8FEC. */
REGION void tsl9_main_runtime_block_8fe0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000090); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FEC..0x8FFA. */
REGION void tsl9_main_runtime_block_8fec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".Lmain_runtime_literal_8ff0:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_runtime_external_8c82\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_runtime_literal_8ff0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8FFA..0x9008. */
REGION void tsl9_main_runtime_block_8ffa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000090)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x937E..0x9388. */
REGION void tsl9_main_runtime_entry_937e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".Lmain_runtime_edge_9384:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_9384\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_9e84\n");
    __builtin_unreachable();
}

/* Original0x9388..0x9392. */
REGION void tsl9_main_runtime_block_9388(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nlhu s0, 10(sp)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lmain_runtime_edge_9390:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_9390\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_9334\n");
    __builtin_unreachable();
}

/* Original0x9392..0x93AA. */
REGION void tsl9_main_runtime_block_9392(void)
{
    REGS;
    PORT(".option push\n.option rvc\nslli s0, s0, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a0, s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a7)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9958..0x9970. */
REGION void tsl9_main_provider_9958(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20002\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000556); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9970..0x998C. */
REGION void tsl9_main_runtime_block_9970(void)
{
    REGS;
    a3 = UINT32_C(0x40010000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffffc00); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x00000100); LIVE;
    a0 = UINT32_C(0x40011000); LIVE;
    PORT(".Lmain_runtime_edge_998a:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_998a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x998C..0x99E8. */
REGION void tsl9_main_runtime_block_998c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x0000006c); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x000f4000); LIVE;
    a5 = a5 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\ndivu a4, a4, a5\n.option pop\n");
    a5 = UINT32_C(0x40000000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000428)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000041c)); LIVE;
    a4 = a4 | UINT32_C(0x00000060); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000041c)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000420)); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000420)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000410)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a4 = a4 & UINT32_C(0xfffffffe); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000410)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000040c)); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000040c)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lmain_runtime_edge_99e6:\n.option push\n.option rvc\nc.j .Lmain_runtime_edge_99e6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_disarm_93ee\n");
    __builtin_unreachable();
}

/* Original0x9E5C..0x9E70. */
REGION void tsl9_main_runtime_entry_9e5c(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -272\n.option pop\n");
    PORT(".option push\n.option norvc\nsw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9E70..0x9E7C. */
REGION void tsl9_main_runtime_block_9e70(void)
{
    REGS;
    a0 = UINT32_C(0x08078000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb00); LIVE;
    PORT(".Lmain_runtime_edge_9e7a:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_9e7a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_external_9c0a\n");
    __builtin_unreachable();
}

/* Original0x9E7C..0x9E84. */
REGION void tsl9_main_runtime_block_9e7c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw ra, 268(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 272\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9E84..0x9E9C. */
REGION void tsl9_callback_flow_external_9e84(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a1 = UINT32_C(0x08078000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffffb00); LIVE;
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9E9C..0x9EA6. */
REGION void tsl9_main_runtime_block_9e9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9F12..0x9F1C. */
REGION void tsl9_main_provider_9f12(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a9)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lmain_runtime_edge_9f1a:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_9f1a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_9e84\n");
    __builtin_unreachable();
}

/* Original0x9F1C..0x9F2A. */
REGION void tsl9_main_runtime_block_9f1c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    PORT(".Lmain_runtime_edge_9f26:\n.option push\n.option norvc\nbne a4,a5,.Lmain_runtime_edge_9f26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_runtime_block_9f34\n");
    __builtin_unreachable();
}

/* Original0x9F2A..0x9F34. */
REGION void tsl9_main_runtime_block_9f2a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lmain_runtime_edge_9f32:\n.option push\n.option rvc\nc.beqz a5,.Lmain_runtime_edge_9f32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_main_runtime_block_9f42\n");
    __builtin_unreachable();
}

/* Original0x9F34..0x9F42. */
REGION void tsl9_main_runtime_block_9f34(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)0; LIVE;
    PORT(".Lmain_runtime_edge_9f40:\n.option push\n.option rvc\nc.jal .Lmain_runtime_edge_9f40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_entry_9e5c\n");
    __builtin_unreachable();
}

/* Original0x9F42..0x9F46. */
REGION void tsl9_main_runtime_block_9f42(void)
{
    REGS;
    PORT(".Lmain_runtime_edge_9f42:\n.option push\n.option norvc\njal ra,.Lmain_runtime_edge_9f42\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_entry_937e\n");
    __builtin_unreachable();
}

/* Original0x9F46..0x9F4C. */
REGION void tsl9_main_runtime_block_9f46(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
