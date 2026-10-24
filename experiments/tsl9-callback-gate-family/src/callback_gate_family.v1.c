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

/* Eight complete original dependency functions:370B/121i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9A24..0x9A3C. */
REGION void tsl9_callback_gate_entry_9a24(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint16_t)a1; LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)) = (uint16_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".Lcallback_gate_edge_9a38:\n.option push\n.option norvc\njal ra,.Lcallback_gate_edge_9a38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_18f88\n");
    __builtin_unreachable();
}

/* Original0x9A3C..0x9A42. */
REGION void tsl9_callback_gate_block_9a3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9AD2..0x9AE4. */
REGION void tsl9_callback_gate_entry_9ad2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a8)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = UINT32_C(0x40011000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff814)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9AF0..0x9AF6. */
REGION void tsl9_callback_flow_external_9af0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a8)); LIVE;
    PORT(".Lcallback_gate_edge_9af4:\n.option push\n.option rvc\nc.bnez a5,.Lcallback_gate_edge_9af4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_gate_block_9b00\n");
    __builtin_unreachable();
}

/* Original0x9AF6..0x9B00. */
REGION void tsl9_callback_gate_block_9af6(void)
{
    REGS;
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff810)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x9B00..0x9B02. */
REGION void tsl9_callback_gate_block_9b00(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9B4E..0x9B64. */
REGION void tsl9_main_provider_9b4e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000a8)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lcallback_gate_edge_9b62:\n.option push\n.option rvc\nc.beqz a5,.Lcallback_gate_edge_9b62\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_gate_block_9b7a\n");
    __builtin_unreachable();
}

/* Original0x9B64..0x9B7A. */
REGION void tsl9_callback_gate_block_9b64(void)
{
    REGS;
    a2 = UINT32_C(0x00001000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000388); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcallback_gate_literal_9b6e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_gate_entry_9ad2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_gate_literal_9b6e\n.option pop\n");
    PORT(".Lcallback_gate_edge_9b76:\n.option push\n.option norvc\njal ra,.Lcallback_gate_edge_9b76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x9B7A..0x9B88. */
REGION void tsl9_callback_gate_block_9b7a(void)
{
    REGS;
    a0 = UINT32_C(0x40011000); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = a0 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lcallback_gate_edge_9b86:\n.option push\n.option rvc\nc.jal .Lcallback_gate_edge_9b86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x9B88..0x9B8E. */
REGION void tsl9_callback_gate_block_9b88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcallback_gate_edge_9b8c:\n.option push\n.option rvc\nc.j .Lcallback_gate_edge_9b8c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_9af0\n");
    __builtin_unreachable();
}

/* Original0xB5B4..0xB5C6. */
REGION void tsl9_callback_flow_external_b5b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff93b)); LIVE;
    a0 = (uint32_t)(a0 < UINT32_C(0x00000002)); LIVE;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD314..0xD322. */
REGION void tsl9_callback_flow_external_d314(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xfffffc48)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD3E8..0xD3F6. */
REGION void tsl9_callback_flow_external_d3e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffb77)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18F88..0x18F94. */
REGION void tsl9_callback_gate_entry_18f88(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nandi a6, a5, 15\n.option pop\n");
    PORT(".Lcallback_gate_edge_18f92:\n.option push\n.option rvc\nc.beqz a4,.Lcallback_gate_edge_18f92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_gate_block_18f9a\n");
    __builtin_unreachable();
}

/* Original0x18F94..0x18F9A. */
REGION void tsl9_callback_gate_block_18f94(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nor a6, a6, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18F9A..0x18FA4. */
REGION void tsl9_callback_gate_block_18f9a(void)
{
    REGS;
    a1 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a4 = a1 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lcallback_gate_edge_18fa2:\n.option push\n.option rvc\nc.beqz a4,.Lcallback_gate_edge_18fa2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_gate_block_18fe8\n");
    __builtin_unreachable();
}

/* Original0x18FA4..0x18FB6. */
REGION void tsl9_callback_gate_block_18fa4(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nli t4, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nli t5, 15\n.option pop\n");
    PORT(".option push\n.option norvc\nli t6, 40\n.option pop\n");
    PORT(".option push\n.option norvc\nli t0, 72\n.option pop\n");
    PORT(".option push\n.option rvc\nli t3, 8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18FB6..0x18FC2. */
REGION void tsl9_callback_gate_block_18fb6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsll a2, t4, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nand a7, a1, a2\n.option pop\n");
    PORT(".Lcallback_gate_edge_18fbe:\n.option push\n.option norvc\nbne a2,a7,.Lcallback_gate_edge_18fbe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_18fe0\n");
    __builtin_unreachable();
}

/* Original0x18FC2..0x18FDE. */
REGION void tsl9_callback_gate_block_18fc2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a7, a3, 0x2\n.option pop\n");
    PORT(".option push\n.option norvc\nsll t1, t5, a7\n.option pop\n");
    PORT(".option push\n.option norvc\nnot t1, t1\n.option pop\n");
    PORT(".option push\n.option norvc\nand a4, t1, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a7, a6, a7\n.option pop\n");
    PORT(".option push\n.option norvc\nor a4, a7, a4\n.option pop\n");
    PORT(".Lcallback_gate_edge_18fda:\n.option push\n.option norvc\nbne a5,t6,.Lcallback_gate_edge_18fda\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_19038\n");
    __builtin_unreachable();
}

/* Original0x18FDE..0x18FE0. */
REGION void tsl9_callback_gate_block_18fde(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000014)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x18FE0..0x18FE6. */
REGION void tsl9_callback_gate_block_18fe0(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    PORT(".Lcallback_gate_edge_18fe2:\n.option push\n.option norvc\nbne a3,t3,.Lcallback_gate_edge_18fe2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_18fb6\n");
    __builtin_unreachable();
}

/* Original0x18FE6..0x18FE8. */
REGION void tsl9_callback_gate_block_18fe6(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x18FE8..0x18FF0. */
REGION void tsl9_callback_gate_block_18fe8(void)
{
    REGS;
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lcallback_gate_edge_18fec:\n.option push\n.option norvc\nbleu a1,a4,.Lcallback_gate_edge_18fec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_19036\n");
    __builtin_unreachable();
}

/* Original0x18FF0..0x19002. */
REGION void tsl9_callback_gate_block_18ff0(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nli t4, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nli t5, 15\n.option pop\n");
    PORT(".option push\n.option norvc\nli t6, 40\n.option pop\n");
    PORT(".option push\n.option norvc\nli t0, 72\n.option pop\n");
    PORT(".option push\n.option rvc\nli t3, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19002..0x1900E. */
REGION void tsl9_callback_gate_block_19002(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsll a7, t4, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nand a4, a1, a7\n.option pop\n");
    PORT(".Lcallback_gate_edge_1900a:\n.option push\n.option norvc\nbne a7,a4,.Lcallback_gate_edge_1900a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_1902e\n");
    __builtin_unreachable();
}

/* Original0x1900E..0x1902A. */
REGION void tsl9_callback_gate_block_1900e(void)
{
    REGS;
    a4 = a2 << UINT32_C(0x00000002); LIVE;
    a4 = a4 + UINT32_C(0xffffffe0); LIVE;
    PORT(".option push\n.option norvc\nsll t1, t5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nnot t1, t1\n.option pop\n");
    PORT(".option push\n.option norvc\nand a3, t1, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a4, a6, a4\n.option pop\n");
    a3 = a3 | a4; LIVE;
    PORT(".Lcallback_gate_edge_19026:\n.option push\n.option norvc\nbne a5,t6,.Lcallback_gate_edge_19026\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_19040\n");
    __builtin_unreachable();
}

/* Original0x1902A..0x1902E. */
REGION void tsl9_callback_gate_block_1902a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a7, 20(a0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1902E..0x19034. */
REGION void tsl9_callback_gate_block_1902e(void)
{
    REGS;
    a2 = a2 + UINT32_C(0x00000001); LIVE;
    PORT(".Lcallback_gate_edge_19030:\n.option push\n.option norvc\nbne a2,t3,.Lcallback_gate_edge_19030\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_19002\n");
    __builtin_unreachable();
}

/* Original0x19034..0x19036. */
REGION void tsl9_callback_gate_block_19034(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0x19036..0x19038. */
REGION void tsl9_callback_gate_block_19036(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x19038..0x1903C. */
REGION void tsl9_callback_gate_block_19038(void)
{
    REGS;
    PORT(".Lcallback_gate_edge_19038:\n.option push\n.option norvc\nbne a5,t0,.Lcallback_gate_edge_19038\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_18fe0\n");
    __builtin_unreachable();
}

/* Original0x1903C..0x19040. */
REGION void tsl9_callback_gate_block_1903c(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint32_t)a2; LIVE;
    PORT(".Lcallback_gate_edge_1903e:\n.option push\n.option rvc\nc.j .Lcallback_gate_edge_1903e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_gate_block_18fe0\n");
    __builtin_unreachable();
}

/* Original0x19040..0x19044. */
REGION void tsl9_callback_gate_block_19040(void)
{
    REGS;
    PORT(".Lcallback_gate_edge_19040:\n.option push\n.option norvc\nbne a5,t0,.Lcallback_gate_edge_19040\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_gate_block_1902e\n");
    __builtin_unreachable();
}

/* Original0x19044..0x1904A. */
REGION void tsl9_callback_gate_block_19044(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a7, 16(a0)\n.option pop\n");
    PORT(".Lcallback_gate_edge_19048:\n.option push\n.option rvc\nc.j .Lcallback_gate_edge_19048\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_gate_block_1902e\n");
    __builtin_unreachable();
}
