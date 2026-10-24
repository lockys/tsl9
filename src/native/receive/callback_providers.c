#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; never execute this experiment.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define CALL_PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Six complete callback functions, original stack frames and typed code/data references.
 * C arithmetic/volatile access is mixed with explicit register/control ports.
 * Seven relative dispatch words and two 17-byte templates are retained separately.
 * Regions need original fallthrough/placement and are not standard C ABI calls.
 * No physical state-field meaning, resident identity or hardware/OTA proof. */

/* Original B0D0..B0D8 */
REGION void tsl9_callback_provider_entry_b0d0(void)
{
    REGS;
    a5 = a1 & 0x1u; LIVE;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_provider_edge_b0d6:\nc.beqz a5,.Lcallback_provider_edge_b0d6\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_provider_block_b0fa\n");
    __builtin_unreachable();
}

/* Original B0D8..B0E2 */
REGION void tsl9_callback_provider_block_b0d8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a5, gp, 192\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi a3, gp, 195\n.option pop\n");
    a2 = UINT32_C(2); LIVE;
    __builtin_unreachable();
}

/* Original B0E2..B0EA */
REGION void tsl9_callback_provider_block_b0e2(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 1u); LIVE;
    CALL_PORT(".Lcallback_provider_edge_b0e6:\n.option push\n.option norvc\nbltu a2,a4,.Lcallback_provider_edge_b0e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_b0f0\n");
    __builtin_unreachable();
}

/* Original B0EA..B0F0 */
REGION void tsl9_callback_provider_block_b0ea(void)
{
    REGS;
    a4 = a4 + 0x1u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1u) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original B0F0..B0F6 */
REGION void tsl9_callback_provider_block_b0f0(void)
{
    REGS;
    a5 = a5 + 0x1u; LIVE;
    CALL_PORT(".Lcallback_provider_edge_b0f2:\n.option push\n.option norvc\nbne a5,a3,.Lcallback_provider_edge_b0f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_b0e2\n");
    __builtin_unreachable();
}

/* Original B0F6..B0FA */
REGION void tsl9_callback_provider_block_b0f6(void)
{
    REGS;
    a0 = a1 ^ 0x1u; LIVE;
    __builtin_unreachable();
}

/* Original B0FA..B0FC */
REGION void tsl9_callback_provider_block_b0fa(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B0FC..B116 */
REGION void tsl9_callback_provider_entry_b0fc(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    CALL_PORT("lw a5, 72(s1)");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT(".option push\n.option norvc\naddi s0, gp, 192\n.option pop\n");
    CALL_PORT("sw ra, 12(sp)");
    a2 = UINT32_C(4); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("mv a0, s0");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original B116..B132 */
REGION void tsl9_callback_provider_block_b116(void)
{
    REGS;
    a5 = UINT32_C(3); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 1(s0)\n.option pop\n");
    a5 = UINT32_C(771); LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 2(s0)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a5, 128(s1)\n.option pop\n");
    CALL_PORT(".Lcallback_provider_literal_b128:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_provider_entry_b0d0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_provider_literal_b128\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original B132..B14A */
REGION void tsl9_callback_provider_block_b132(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 0(s0)\n.option pop\n");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nlw t1, 556(s1)\n.option pop\n");
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s1, 4(sp)");
    a2 = UINT32_C(1600); LIVE;
    a1 = UINT32_C(1); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("jr t1");
    __builtin_unreachable();
}

/* Original D272..D288 */
REGION void tsl9_callback_provider_entry_d272(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    CALL_PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(19); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + 0xfffffccau; LIVE;
    CALL_PORT("jr t1");
    __builtin_unreachable();
}

/* Original 10630..10698 */
REGION void tsl9_callback_provider_entry_10630(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    a5 = UINT32_C(540); LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 4(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fffc\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 - 1666u); LIVE;
    a5 = UINT32_C(8); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 6(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsnez a4, a4\n.option pop\n");
    a5 = UINT32_C(17); LIVE;
    a5 = a4 * a5; LIVE;
    CALL_PORT(".Lcallback_provider_literal_10652:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_provider_templates_1a4f4\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_provider_literal_10652\n.option pop\n");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT(".option push\n.option norvc\naddi a3, gp, 328\n.option pop\n");
    CALL_PORT("addi a0, sp, 4");
    CALL_PORT("sw zero, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nsb zero, 12(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsb zero, 15(sp)\n.option pop\n");
    a4 = a4 + a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + 0u); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 7(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + 0u); LIVE;
    a4 = a4 + a5; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1u); LIVE;
    a2 = a5 << 4u; LIVE;
    a5 = a5 + 0x1u; LIVE;
    a5 = a5 & 0xfu; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a2, 13(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsb a4, 14(sp)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + 0u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Lcallback_provider_edge_10694:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_10694\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_12a08\n");
    __builtin_unreachable();
}

/* Original 10698..1069E */
REGION void tsl9_callback_provider_block_10698(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 12B24..12B30 */
REGION void tsl9_callback_provider_entry_12b24(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT("sw s0, 24(sp)");
    CALL_PORT("mv s0, a0");
    CALL_PORT(".Lcallback_provider_edge_12b2c:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b2c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_1070a\n");
    __builtin_unreachable();
}

/* Original 12B30..12B34 */
REGION void tsl9_callback_provider_block_12b30(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_12b30:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b30\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_129c4\n");
    __builtin_unreachable();
}

/* Original 12B34..12B3A */
REGION void tsl9_callback_provider_block_12b34(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12b36:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b36\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_12aa0\n");
    __builtin_unreachable();
}

/* Original 12B3A..12B40 */
REGION void tsl9_callback_provider_block_12b3a(void)
{
    REGS;
    a0 = UINT32_C(2); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12b3c:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b3c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_12aa0\n");
    __builtin_unreachable();
}

/* Original 12B40..12B46 */
REGION void tsl9_callback_provider_block_12b40(void)
{
    REGS;
    a5 = UINT32_C(6); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12b42:\n.option push\n.option norvc\nbltu a5,s0,.Lcallback_provider_edge_12b42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_12b7a\n");
    __builtin_unreachable();
}

/* Original 12B46..12B58 */
REGION void tsl9_callback_provider_block_12b46(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_literal_12b46:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_provider_relative_table_1a680\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_provider_literal_12b46\n.option pop\n");
    CALL_PORT("slli s0, s0, 0x2");
    CALL_PORT("add s0, s0, a4");
    CALL_PORT("lw a5, 0(s0)");
    a5 = a5 + a4; LIVE;
    CALL_PORT("jr a5");
    __builtin_unreachable();
}

/* Original 12B58..12B6A */
REGION void tsl9_callback_provider_block_12b58(void)
{
    REGS;
    a5 = UINT32_C(0x3e90000); LIVE;
    a5 = a5 + 0x334u; LIVE;
    a1 = UINT32_C(4); LIVE;
    CALL_PORT("addi a0, sp, 8");
    CALL_PORT("sw a5, 8(sp)");
    CALL_PORT(".Lcallback_provider_edge_12b66:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b66\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_128fe\n");
    __builtin_unreachable();
}

/* Original 12B6A..12B7A */
REGION void tsl9_callback_provider_block_12b6a(void)
{
    REGS;
    a5 = UINT32_C(1); LIVE;
    a2 = UINT32_C(2); LIVE;
    CALL_PORT("addi a1, sp, 4");
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 4(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_provider_edge_12b76:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_12abe\n");
    __builtin_unreachable();
}

/* Original 12B7A..12B82 */
REGION void tsl9_callback_provider_block_12b7a(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("lw s0, 24(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 12B82..12B86 */
REGION void tsl9_callback_provider_block_12b82(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_12b82:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b82\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_1299e\n");
    __builtin_unreachable();
}

/* Original 12B86..12B8C */
REGION void tsl9_callback_provider_block_12b86(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12b88:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_16dd4\n");
    __builtin_unreachable();
}

/* Original 12B8C..12B92 */
REGION void tsl9_callback_provider_block_12b8c(void)
{
    REGS;
    a0 = UINT32_C(2); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12b8e:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12b8e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_16dd4\n");
    __builtin_unreachable();
}

/* Original 12B92..12B94 */
REGION void tsl9_callback_provider_block_12b92(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_12b92:\nc.j .Lcallback_provider_edge_12b92\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_12b7a\n");
    __builtin_unreachable();
}

/* Original 12B94..12B98 */
REGION void tsl9_callback_provider_block_12b94(void)
{
    REGS;
    a5 = UINT32_C(0x4980000); LIVE;
    __builtin_unreachable();
}

/* Original 12B98..12BA0 */
REGION void tsl9_callback_provider_block_12b98(void)
{
    REGS;
    a5 = a5 + 0xa9u; LIVE;
    CALL_PORT("sw a5, 8(sp)");
    a1 = UINT32_C(4); LIVE;
    __builtin_unreachable();
}

/* Original 12BA0..12BA6 */
REGION void tsl9_callback_provider_block_12ba0(void)
{
    REGS;
    CALL_PORT("addi a0, sp, 8");
    CALL_PORT(".Lcallback_provider_edge_12ba2:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_12ba2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_128fe\n");
    __builtin_unreachable();
}

/* Original 12BA6..12BA8 */
REGION void tsl9_callback_provider_block_12ba6(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_12ba6:\nc.j .Lcallback_provider_edge_12ba6\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_12b7a\n");
    __builtin_unreachable();
}

/* Original 12BA8..12BAE */
REGION void tsl9_callback_provider_block_12ba8(void)
{
    REGS;
    a5 = UINT32_C(0x21c0000); LIVE;
    CALL_PORT(".Lcallback_provider_edge_12bac:\nc.j .Lcallback_provider_edge_12bac\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_12b98\n");
    __builtin_unreachable();
}

/* Original 12BAE..12BB2 */
REGION void tsl9_callback_provider_block_12bae(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a5, gp, 112\n.option pop\n");
    __builtin_unreachable();
}

/* Original 12BB2..12BC2 */
REGION void tsl9_callback_provider_block_12bb2(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 4u); LIVE;
    a1 = UINT32_C(6); LIVE;
    CALL_PORT("sw a4, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nsh a5, 12(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_provider_edge_12bc0:\nc.j .Lcallback_provider_edge_12bc0\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_12ba0\n");
    __builtin_unreachable();
}

/* Original 12BC2..12BC8 */
REGION void tsl9_callback_provider_block_12bc2(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a5, gp, 120\n.option pop\n");
    CALL_PORT(".Lcallback_provider_edge_12bc6:\nc.j .Lcallback_provider_edge_12bc6\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_12bb2\n");
    __builtin_unreachable();
}

/* Original 13D48..13D50 */
REGION void tsl9_callback_provider_entry_13d48(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".Lcallback_provider_edge_13d4c:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_13d4c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_135e6\n");
    __builtin_unreachable();
}

/* Original 13D50..13D68 */
REGION void tsl9_callback_provider_block_13d50(void)
{
    REGS;
    a4 = UINT32_C(0x10000); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fff9\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 - 1468u); LIVE;
    a4 = a4 + 0xfffffffeu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    a5 = a5 + 0xfffffa38u; LIVE;
    CALL_PORT(".Lcallback_provider_edge_13d64:\n.option push\n.option norvc\nbeq a3,a4,.Lcallback_provider_edge_13d64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_13d72\n");
    __builtin_unreachable();
}

/* Original 13D68..13D72 */
REGION void tsl9_callback_provider_block_13d68(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 5u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_provider_edge_13d70:\nc.beqz a4,.Lcallback_provider_edge_13d70\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_provider_block_13d88\n");
    __builtin_unreachable();
}

/* Original 13D72..13D7E */
REGION void tsl9_callback_provider_block_13d72(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + 6u); LIVE;
    a4 = UINT32_C(0x10000); LIVE;
    a4 = a4 + 0xfffffffeu; LIVE;
    CALL_PORT(".Lcallback_provider_edge_13d7a:\n.option push\n.option norvc\nbeq a4,a3,.Lcallback_provider_edge_13d7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_13dce\n");
    __builtin_unreachable();
}

/* Original 13D7E..13D88 */
REGION void tsl9_callback_provider_block_13d7e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 9u); LIVE;
    a5 = a5 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_provider_edge_13d86:\nc.bnez a5,.Lcallback_provider_edge_13d86\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_provider_block_13dce\n");
    __builtin_unreachable();
}

/* Original 13D88..13D8A */
REGION void tsl9_callback_provider_block_13d88(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_13d88:\nc.beqz a0,.Lcallback_provider_edge_13d88\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_provider_block_13da2\n");
    __builtin_unreachable();
}

/* Original 13D8A..13D90 */
REGION void tsl9_callback_provider_block_13d8a(void)
{
    REGS;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(100); LIVE;
    __builtin_unreachable();
}

/* Original 13D90..13DA2 */
REGION void tsl9_callback_provider_block_13d90(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_provider_literal_13d94:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_provider_external_13346\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_provider_literal_13d94\n.option pop\n");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT(".Lcallback_provider_edge_13d9e:\n.option push\n.option norvc\njal zero,.Lcallback_provider_edge_13d9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_9124\n");
    __builtin_unreachable();
}

/* Original 13DA2..13DA6 */
REGION void tsl9_callback_provider_block_13da2(void)
{
    REGS;
    CALL_PORT(".Lcallback_provider_edge_13da2:\n.option push\n.option norvc\njal ra,.Lcallback_provider_edge_13da2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_81b0\n");
    __builtin_unreachable();
}

/* Original 13DA6..13DB8 */
REGION void tsl9_callback_provider_block_13da6(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a5, gp, 344\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a4 = UINT32_C(34); LIVE;
    CALL_PORT(".option push\n.option norvc\nsub a5, a0, a5\n.option pop\n");
    CALL_PORT(".Lcallback_provider_edge_13db4:\n.option push\n.option norvc\nbleu a5,a4,.Lcallback_provider_edge_13db4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_provider_block_13dc6\n");
    __builtin_unreachable();
}

/* Original 13DB8..13DC6 */
REGION void tsl9_callback_provider_block_13db8(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nsw a0, 344(gp)\n.option pop\n");
    a0 = UINT32_C(0); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT(".Lcallback_provider_edge_13dc2:\n.option push\n.option norvc\njal zero,.Lcallback_provider_edge_13dc2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_external_13346\n");
    __builtin_unreachable();
}

/* Original 13DC6..13DCE */
REGION void tsl9_callback_provider_block_13dc6(void)
{
    REGS;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(35); LIVE;
    CALL_PORT(".Lcallback_provider_edge_13dcc:\nc.j .Lcallback_provider_edge_13dcc\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_provider_block_13d90\n");
    __builtin_unreachable();
}

/* Original 13DCE..13DD4 */
REGION void tsl9_callback_provider_block_13dce(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original seven signed relative dispatch words. */
__asm__(".pushsection .rodata.tsl9_callback_provider_relative_table_1a680,\"a\",@progbits\n.globl tsl9_callback_provider_relative_table_1a680\n.type tsl9_callback_provider_relative_table_1a680,@object\n.p2align 2\ntsl9_callback_provider_relative_table_1a680:\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12b58\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12b82\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12ba8\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12ba8\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12bae\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12bc2\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.word 0\n.reloc .-4,R_RISCV_ADD32,tsl9_callback_provider_block_12b94\n.reloc .-4,R_RISCV_SUB32,tsl9_callback_provider_relative_table_1a680\n.size tsl9_callback_provider_relative_table_1a680,.-tsl9_callback_provider_relative_table_1a680\n.popsection\n");

/* Original two 17-byte templates; lookup index bounds remain unproved. */
ENTRY __attribute__((used,section(".rodata.tsl9_callback_provider_templates_1a4f4"),aligned(1)))
const uint8_t tsl9_callback_provider_templates_1a4f4[34] = {9,245,76,154,35,43,146,68,253,84,237,59,130,138,51,229,92,10,210,107,189,4,12,181,99,218,115,202,28,165,173,20,194,123};
