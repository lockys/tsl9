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

/* Three complete callback dependency functions:464B/170i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x11356..0x11362. */
REGION void tsl9_registered_callbacks_provider_11356(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffc72); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lcallback_dependencies_edge_11360:\n.option push\n.option rvc\nc.beqz a4,.Lcallback_dependencies_edge_11360\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_11440\n");
    __builtin_unreachable();
}

/* Original0x11362..0x11384. */
REGION void tsl9_callback_dependencies_block_11362(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 0(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_11382:\n.option push\n.option rvc\nc.bnez a5,.Lcallback_dependencies_edge_11382\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_113f0\n");
    __builtin_unreachable();
}

/* Original0x11384..0x11392. */
REGION void tsl9_callback_dependencies_block_11384(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s4, gp, 88\n.option pop\n");
    PORT(".option push\n.option rvc\nli s5, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s3, 252\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11392..0x113AC. */
REGION void tsl9_callback_dependencies_block_11392(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 4(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".Lcallback_dependencies_edge_113a8:\n.option push\n.option norvc\nbne a4,a3,.Lcallback_dependencies_edge_113a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_dependencies_block_113d6\n");
    __builtin_unreachable();
}

/* Original0x113AC..0x113B0. */
REGION void tsl9_callback_dependencies_block_113ac(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_113ac:\n.option push\n.option norvc\nbeq s1,s5,.Lcallback_dependencies_edge_113ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_dependencies_block_11436\n");
    __builtin_unreachable();
}

/* Original0x113B0..0x113BA. */
REGION void tsl9_callback_dependencies_block_113b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 10(s2)\n.option pop\n");
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lcallback_dependencies_edge_113b8:\n.option push\n.option rvc\nc.beqz a4,.Lcallback_dependencies_edge_113b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_11430\n");
    __builtin_unreachable();
}

/* Original0x113BA..0x113BE. */
REGION void tsl9_callback_dependencies_block_113ba(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    __builtin_unreachable();
}

/* Original0x113BE..0x113C2. */
REGION void tsl9_callback_dependencies_block_113be(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_113be:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_113be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_155d0\n");
    __builtin_unreachable();
}

/* Original0x113C2..0x113D6. */
REGION void tsl9_callback_dependencies_block_113c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 88(s6)\n.option pop\n");
    a2 = UINT32_C(0x000000a0); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffbfc)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x113D6..0x113DC. */
REGION void tsl9_callback_dependencies_block_113d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 6\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_113d8:\n.option push\n.option norvc\nbne s0,s3,.Lcallback_dependencies_edge_113d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_dependencies_block_11392\n");
    __builtin_unreachable();
}

/* Original0x113DC..0x113F0. */
REGION void tsl9_callback_dependencies_block_113dc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x113F0..0x11404. */
REGION void tsl9_callback_dependencies_block_113f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbd9)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbe8)) = (uint8_t)0; LIVE;
    PORT(".Lcallback_dependencies_edge_11400:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_11400\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x11404..0x11406. */
REGION void tsl9_callback_dependencies_block_11404(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_11404:\n.option push\n.option rvc\nc.bnez s1,.Lcallback_dependencies_edge_11404\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_113dc\n");
    __builtin_unreachable();
}

/* Original0x11406..0x11430. */
REGION void tsl9_callback_dependencies_block_11406(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffbaa)); LIVE;
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11430..0x11436. */
REGION void tsl9_callback_dependencies_block_11430(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lcallback_dependencies_edge_11434:\n.option push\n.option rvc\nc.j .Lcallback_dependencies_edge_11434\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_dependencies_block_113be\n");
    __builtin_unreachable();
}

/* Original0x11436..0x1143E. */
REGION void tsl9_callback_dependencies_block_11436(void)
{
    REGS;
    a0 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lcallback_dependencies_edge_1143a:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_1143a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_155d0\n");
    __builtin_unreachable();
}

/* Original0x1143E..0x11440. */
REGION void tsl9_callback_dependencies_block_1143e(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_1143e:\n.option push\n.option rvc\nc.j .Lcallback_dependencies_edge_1143e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_dependencies_block_113d6\n");
    __builtin_unreachable();
}

/* Original0x11440..0x11442. */
REGION void tsl9_callback_dependencies_block_11440(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13CDC..0x13CF6. */
REGION void tsl9_registered_callbacks_provider_13cdc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 112(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    a0 = a1 + UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13CF6..0x13CF8. */
REGION void tsl9_callback_dependencies_block_13cf6(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_13cf6:\n.option push\n.option rvc\nc.beqz a0,.Lcallback_dependencies_edge_13cf6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_13d3c\n");
    __builtin_unreachable();
}

/* Original0x13CF8..0x13D08. */
REGION void tsl9_callback_dependencies_block_13cf8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a2; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 76(s1)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13D08..0x13D0C. */
REGION void tsl9_callback_dependencies_block_13d08(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_13d08:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_13d08\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_135e6\n");
    __builtin_unreachable();
}

/* Original0x13D0C..0x13D12. */
REGION void tsl9_callback_dependencies_block_13d0c(void)
{
    REGS;
    a2 = UINT32_C(0x00000064); LIVE;
    PORT(".Lcallback_dependencies_edge_13d10:\n.option push\n.option rvc\nc.bnez a0,.Lcallback_dependencies_edge_13d10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_13d14\n");
    __builtin_unreachable();
}

/* Original0x13D12..0x13D14. */
REGION void tsl9_callback_dependencies_block_13d12(void)
{
    REGS;
    a2 = UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x13D14..0x13D24. */
REGION void tsl9_callback_dependencies_block_13d14(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcallback_dependencies_literal_13d18:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_dependencies_provider_13eb4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_dependencies_literal_13d18\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_13d20:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_13d20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x13D24..0x13D26. */
REGION void tsl9_callback_dependencies_block_13d24(void)
{
    REGS;
    PORT(".Lcallback_dependencies_edge_13d24:\n.option push\n.option rvc\nc.beqz a0,.Lcallback_dependencies_edge_13d24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_13d3c\n");
    __builtin_unreachable();
}

/* Original0x13D26..0x13D3C. */
REGION void tsl9_callback_dependencies_block_13d26(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13D3C..0x13D48. */
REGION void tsl9_callback_dependencies_block_13d3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16E88..0x16E96. */
REGION void tsl9_registered_callbacks_provider_16e88(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16e92:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16e92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_reply_external_16e0c\n");
    __builtin_unreachable();
}

/* Original0x16E96..0x16E9A. */
REGION void tsl9_callback_dependencies_block_16e96(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16e98:\n.option push\n.option rvc\nc.bnez a0,.Lcallback_dependencies_edge_16e98\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_dependencies_block_16ef4\n");
    __builtin_unreachable();
}

/* Original0x16E9A..0x16EA4. */
REGION void tsl9_callback_dependencies_block_16e9a(void)
{
    REGS;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ea0:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ea0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_169dc\n");
    __builtin_unreachable();
}

/* Original0x16EA4..0x16EB0. */
REGION void tsl9_callback_dependencies_block_16ea4(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000002a); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16eac:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16eac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16EB0..0x16EBE. */
REGION void tsl9_callback_dependencies_block_16eb0(void)
{
    REGS;
    a2 = UINT32_C(0x00000090); LIVE;
    a1 = UINT32_C(0x00000029); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16eba:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16eba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16EBE..0x16ECC. */
REGION void tsl9_callback_dependencies_block_16ebe(void)
{
    REGS;
    a2 = UINT32_C(0x00000082); LIVE;
    a1 = UINT32_C(0x00000028); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ec8:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ec8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16ECC..0x16ED4. */
REGION void tsl9_callback_dependencies_block_16ecc(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ed0:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ed0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_16b50\n");
    __builtin_unreachable();
}

/* Original0x16ED4..0x16EDC. */
REGION void tsl9_callback_dependencies_block_16ed4(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ed8:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ed8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_16b50\n");
    __builtin_unreachable();
}

/* Original0x16EDC..0x16EE8. */
REGION void tsl9_callback_dependencies_block_16edc(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000002c); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ee4:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ee4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16EE8..0x16EF4. */
REGION void tsl9_callback_dependencies_block_16ee8(void)
{
    REGS;
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x0000002b); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcallback_dependencies_edge_16ef0:\n.option push\n.option norvc\njal ra,.Lcallback_dependencies_edge_16ef0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_write_entry_16a30\n");
    __builtin_unreachable();
}

/* Original0x16EF4..0x16F00. */
REGION void tsl9_callback_dependencies_block_16ef4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
