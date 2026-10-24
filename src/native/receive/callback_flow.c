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

/* Nine complete callback-flow functions, original stack frames and typed code/data references.
 * C arithmetic/volatile access is mixed with explicit register/control ports.
 * The complete 672B state builder and a 96B readonly constant block are retained.
 * Regions need original fallthrough/placement and are not standard C ABI calls.
 * No physical state-field meaning, resident identity or hardware/OTA proof. */

/* Original 1061C..10630 */
REGION void tsl9_callback_flow_entry_1061c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 - 1636u) = 0; LIVE;
    CALL_PORT(".Lcallback_flow_literal_10624:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_flow_entry_1061c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_flow_literal_10624\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_1062c:\n.option push\n.option norvc\njal zero,.Lcallback_flow_edge_1062c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original 1070A..10712 */
REGION void tsl9_callback_flow_entry_1070a(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".Lcallback_flow_edge_1070e:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1070e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_10032\n");
    __builtin_unreachable();
}

/* Original 10712..10718 */
REGION void tsl9_callback_flow_block_10712(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_flow_edge_10714:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_10714\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_1061c\n");
    __builtin_unreachable();
}

/* Original 10718..1072C */
REGION void tsl9_callback_flow_block_10718(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 72u); LIVE;
    a2 = UINT32_C(12); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fffc\n.option pop\n");
    a0 = a0 + 0xfffff896u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 1072C..10730 */
REGION void tsl9_callback_flow_block_1072c(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_edge_1072c:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1072c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_9af0\n");
    __builtin_unreachable();
}

/* Original 10730..1073C */
REGION void tsl9_callback_flow_block_10730(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_literal_10730:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_queue_external_9b36\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_flow_literal_10730\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_10738:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_10738\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original 1073C..1074C */
REGION void tsl9_callback_flow_block_1073c(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT(".Lcallback_flow_literal_1073e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_deferred_107c0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_flow_literal_1073e\n.option pop\n");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT(".Lcallback_flow_edge_10748:\n.option push\n.option norvc\njal zero,.Lcallback_flow_edge_10748\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original 1299E..129B4 */
REGION void tsl9_callback_flow_entry_1299e(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -112");
    a2 = UINT32_C(96); LIVE;
    CALL_PORT(".Lcallback_flow_literal_129a4:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_flow_constants_19ca8\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_flow_literal_129a4\n.option pop\n");
    CALL_PORT("mv a0, sp");
    CALL_PORT("sw ra, 108(sp)");
    CALL_PORT(".Lcallback_flow_edge_129b0:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_129b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_19bf0\n");
    __builtin_unreachable();
}

/* Original 129B4..129BE */
REGION void tsl9_callback_flow_block_129b4(void)
{
    REGS;
    CALL_PORT("mv a0, sp");
    a1 = UINT32_C(96); LIVE;
    CALL_PORT(".Lcallback_flow_edge_129ba:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_129ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_128fe\n");
    __builtin_unreachable();
}

/* Original 129BE..129C4 */
REGION void tsl9_callback_flow_block_129be(void)
{
    REGS;
    CALL_PORT("lw ra, 108(sp)");
    CALL_PORT("addi sp, sp, 112");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 129C4..129D8 */
REGION void tsl9_callback_flow_entry_129c4(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -64");
    CALL_PORT("sw s0, 56(sp)");
    CALL_PORT("sw s1, 52(sp)");
    CALL_PORT("sw s2, 48(sp)");
    CALL_PORT("sw s3, 44(sp)");
    CALL_PORT("sw ra, 60(sp)");
    CALL_PORT("li s0, 0");
    CALL_PORT("li s3, 1");
    CALL_PORT("li s2, 1");
    CALL_PORT("li s1, 14");
    __builtin_unreachable();
}

/* Original 129D8..129F6 */
REGION void tsl9_callback_flow_block_129d8(void)
{
    REGS;
    CALL_PORT("sw zero, 20(sp)");
    CALL_PORT(".option push\n.option norvc\nsb s0, 22(sp)\n.option pop\n");
    CALL_PORT("addi s0, s0, 1");
    CALL_PORT("addi a0, sp, 12");
    CALL_PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    CALL_PORT("sw zero, 24(sp)");
    CALL_PORT(".option push\n.option norvc\nsb s3, 23(sp)\n.option pop\n");
    CALL_PORT("sw zero, 12(sp)");
    CALL_PORT("sw zero, 16(sp)");
    CALL_PORT("sw s2, 28(sp)");
    CALL_PORT(".Lcallback_flow_edge_129f2:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_129f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_filter_program_18ba2\n");
    __builtin_unreachable();
}

/* Original 129F6..129FA */
REGION void tsl9_callback_flow_block_129f6(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_edge_129f6:\n.option push\n.option norvc\nbne s0,s1,.Lcallback_flow_edge_129f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_129d8\n");
    __builtin_unreachable();
}

/* Original 129FA..12A08 */
REGION void tsl9_callback_flow_block_129fa(void)
{
    REGS;
    CALL_PORT("lw ra, 60(sp)");
    CALL_PORT("lw s0, 56(sp)");
    CALL_PORT("lw s1, 52(sp)");
    CALL_PORT("lw s2, 48(sp)");
    CALL_PORT("lw s3, 44(sp)");
    CALL_PORT("addi sp, sp, 64");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 12AA0..12AAA */
REGION void tsl9_callback_flow_entry_12aa0(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw a0, 12(sp)");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT(".Lcallback_flow_edge_12aa6:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_12aa6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_1070a\n");
    __builtin_unreachable();
}

/* Original 12AAA..12AAE */
REGION void tsl9_callback_flow_block_12aaa(void)
{
    REGS;
    CALL_PORT("lw a0, 12(sp)");
    CALL_PORT(".Lcallback_flow_edge_12aac:\nc.bnez a0,.Lcallback_flow_edge_12aac\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_12ab6\n");
    __builtin_unreachable();
}

/* Original 12AAE..12AB6 */
REGION void tsl9_callback_flow_block_12aae(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT(".Lcallback_flow_edge_12ab2:\n.option push\n.option norvc\njal zero,.Lcallback_flow_edge_12ab2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_129c4\n");
    __builtin_unreachable();
}

/* Original 12AB6..12ABE */
REGION void tsl9_callback_flow_block_12ab6(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT(".Lcallback_flow_edge_12aba:\n.option push\n.option norvc\njal zero,.Lcallback_flow_edge_12aba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_16dac\n");
    __builtin_unreachable();
}

/* Original 1333C..13346 */
REGION void tsl9_callback_flow_entry_1333c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + 1112u) = 0; LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 13346..13362 */
REGION void tsl9_callback_flow_entry_13346(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -144");
    CALL_PORT("sw ra, 140(sp)");
    CALL_PORT("sw s0, 136(sp)");
    CALL_PORT("sw s2, 128(sp)");
    CALL_PORT("sw s3, 124(sp)");
    CALL_PORT("sw s4, 120(sp)");
    CALL_PORT("sw s5, 116(sp)");
    CALL_PORT("sw s6, 112(sp)");
    CALL_PORT("sw s7, 108(sp)");
    CALL_PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    CALL_PORT("sw s1, 132(sp)");
    CALL_PORT(".Lcallback_flow_edge_1335e:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1335e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_9e84\n");
    __builtin_unreachable();
}

/* Original 13362..13382 */
REGION void tsl9_callback_flow_block_13362(void)
{
    REGS;
    CALL_PORT("lw a5, 72(s0)");
    CALL_PORT(".option push\n.option norvc\nsh a0, 12(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsh a1, 16(sp)\n.option pop\n");
    a0 = a0 >> 16u; LIVE;
    a1 = a1 >> 16u; LIVE;
    a2 = UINT32_C(76); LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a0, 14(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsh a1, 18(sp)\n.option pop\n");
    CALL_PORT("addi a0, sp, 20");
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 13382..133A6 */
REGION void tsl9_callback_flow_block_13382(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 12(sp)\n.option pop\n");
    CALL_PORT("addi a0, sp, 24");
    CALL_PORT(".option push\n.option norvc\nsb zero, 20(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsb a5, 21(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlbu a5, 13(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nauipc s5, 0x1fff9\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi s5, s5, 1024\n.option pop\n");
    CALL_PORT("lui s3, 0x10");
    CALL_PORT(".option push\n.option norvc\nsb a5, 22(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_133a2:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_133a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_92ba\n");
    __builtin_unreachable();
}

/* Original 133A6..133AC */
REGION void tsl9_callback_flow_block_133a6(void)
{
    REGS;
    CALL_PORT("lw s0, 76(s0)");
    CALL_PORT(".Lcallback_flow_edge_133a8:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_133a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d1a8\n");
    __builtin_unreachable();
}

/* Original 133AC..133B4 */
REGION void tsl9_callback_flow_block_133ac(void)
{
    REGS;
    CALL_PORT("mv a1, a0");
    a2 = UINT32_C(19); LIVE;
    CALL_PORT("addi a0, sp, 60");
    CALL_PORT("c.jalr s0");
    __builtin_unreachable();
}

/* Original 133B4..133C4 */
REGION void tsl9_callback_flow_block_133b4(void)
{
    REGS;
    CALL_PORT("li s2, 0");
    CALL_PORT("addi s3, s3, -2");
    CALL_PORT("mv s7, s5");
    CALL_PORT("li s6, 1");
    CALL_PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi s4, gp, 84\n.option pop\n");
    __builtin_unreachable();
}

/* Original 133C4..133D4 */
REGION void tsl9_callback_flow_block_133c4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nslli s1, s2, 0x2\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nadd a5, s5, s1\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + 2u); LIVE;
    CALL_PORT(".Lcallback_flow_edge_133d0:\n.option push\n.option norvc\nbeq s3,a4,.Lcallback_flow_edge_133d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_135ac\n");
    __builtin_unreachable();
}

/* Original 133D4..133E0 */
REGION void tsl9_callback_flow_block_133d4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 5u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_133dc:\n.option push\n.option norvc\nbnez a4,.Lcallback_flow_edge_133dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_135ac\n");
    __builtin_unreachable();
}

/* Original 133E0..133F0 */
REGION void tsl9_callback_flow_block_133e0(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 4u); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb s6, 23(sp)\n.option pop\n");
    a5 = a5 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_133ec:\n.option push\n.option norvc\nbeqz a5,.Lcallback_flow_edge_133ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_135ca\n");
    __builtin_unreachable();
}

/* Original 133F0..133F4 */
REGION void tsl9_callback_flow_block_133f0(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_edge_133f0:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_133f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_fa2a\n");
    __builtin_unreachable();
}

/* Original 133F4..13404 */
REGION void tsl9_callback_flow_block_133f4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 23(sp)\n.option pop\n");
    a0 = a0 << 1u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 23(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13400:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13400\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_b1b0\n");
    __builtin_unreachable();
}

/* Original 13404..13414 */
REGION void tsl9_callback_flow_block_13404(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 23(sp)\n.option pop\n");
    a0 = a0 << 2u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 23(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13410:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13410\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_fa36\n");
    __builtin_unreachable();
}

/* Original 13414..1342C */
REGION void tsl9_callback_flow_block_13414(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a4, 23(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlbu a5, 357(gp)\n.option pop\n");
    a5 = a5 << 4u; LIVE;
    a5 = a5 | a4; LIVE;
    a0 = a0 << 3u; LIVE;
    a5 = a5 | a0; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 23(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13428:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13428\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_a968\n");
    __builtin_unreachable();
}

/* Original 1342C..13434 */
REGION void tsl9_callback_flow_block_1342c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13430:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13430\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d314\n");
    __builtin_unreachable();
}

/* Original 13434..13444 */
REGION void tsl9_callback_flow_block_13434(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 1u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13440:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13440\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original 13444..13454 */
REGION void tsl9_callback_flow_block_13444(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 2u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13450:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13450\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_181c4\n");
    __builtin_unreachable();
}

/* Original 13454..13466 */
REGION void tsl9_callback_flow_block_13454(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 3u; LIVE;
    a0 = a0 & 0x8u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13462:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13462\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_181c4\n");
    __builtin_unreachable();
}

/* Original 13466..13478 */
REGION void tsl9_callback_flow_block_13466(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 3u; LIVE;
    a0 = a0 & 0x10u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13474:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13474\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_b5b4\n");
    __builtin_unreachable();
}

/* Original 13478..13488 */
REGION void tsl9_callback_flow_block_13478(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 5u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13484:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13484\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_c35a\n");
    __builtin_unreachable();
}

/* Original 13488..13498 */
REGION void tsl9_callback_flow_block_13488(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 6u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13494:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13494\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original 13498..134A8 */
REGION void tsl9_callback_flow_block_13498(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 38(sp)\n.option pop\n");
    a0 = a0 << 7u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 38(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134a4:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original 134A8..134B0 */
REGION void tsl9_callback_flow_block_134a8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134ac:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6b0\n");
    __builtin_unreachable();
}

/* Original 134B0..134C0 */
REGION void tsl9_callback_flow_block_134b0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 1u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134bc:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f714\n");
    __builtin_unreachable();
}

/* Original 134C0..134D0 */
REGION void tsl9_callback_flow_block_134c0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 2u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134cc:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6e2\n");
    __builtin_unreachable();
}

/* Original 134D0..134E0 */
REGION void tsl9_callback_flow_block_134d0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 3u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134dc:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f746\n");
    __builtin_unreachable();
}

/* Original 134E0..134F0 */
REGION void tsl9_callback_flow_block_134e0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 4u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134ec:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original 134F0..13500 */
REGION void tsl9_callback_flow_block_134f0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 5u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_134fc:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_134fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_f992\n");
    __builtin_unreachable();
}

/* Original 13500..13512 */
REGION void tsl9_callback_flow_block_13500(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 39(sp)\n.option pop\n");
    a0 = a0 << 6u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 39(sp)\n.option pop\n");
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_flow_edge_1350e:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1350e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original 13512..13516 */
REGION void tsl9_callback_flow_block_13512(void)
{
    REGS;
    a5 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_flow_edge_13514:\nc.bnez a0,.Lcallback_flow_edge_13514\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_13526\n");
    __builtin_unreachable();
}

/* Original 13516..13526 */
REGION void tsl9_callback_flow_block_13516(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlw a5, 0(s4)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 4u); LIVE;
    a5 = a5 >> 3u; LIVE;
    a5 = a5 ^ 0x1u; LIVE;
    a5 = a5 & 0x1u; LIVE;
    __builtin_unreachable();
}

/* Original 13526..13536 */
REGION void tsl9_callback_flow_block_13526(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a4, 39(sp)\n.option pop\n");
    a5 = a5 << 7u; LIVE;
    a5 = a5 | a4; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 39(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_13532:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13532\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_171ba\n");
    __builtin_unreachable();
}

/* Original 13536..1353E */
REGION void tsl9_callback_flow_block_13536(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsh a0, 40(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_1353a:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1353a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_mode_getter_829e\n");
    __builtin_unreachable();
}

/* Original 1353E..13552 */
REGION void tsl9_callback_flow_block_1353e(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 356(gp)\n.option pop\n");
    a0 = a0 & 0x1fu; LIVE;
    a5 = a5 << 7u; LIVE;
    a5 = a5 | a0; LIVE;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 42(sp)\n.option pop\n");
    CALL_PORT(".Lcallback_flow_edge_1354e:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1354e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original 13552..1355C */
REGION void tsl9_callback_flow_block_13552(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 43(sp)\n.option pop\n");
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lcallback_flow_edge_13558:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13558\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original 1355C..1356E */
REGION void tsl9_callback_flow_block_1355c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 43(sp)\n.option pop\n");
    a0 = a0 << 1u; LIVE;
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 43(sp)\n.option pop\n");
    a0 = UINT32_C(2); LIVE;
    CALL_PORT(".Lcallback_flow_edge_1356a:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_1356a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original 1356E..13586 */
REGION void tsl9_callback_flow_block_1356e(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 43(sp)\n.option pop\n");
    a0 = a0 << 2u; LIVE;
    CALL_PORT(".option push\n.option norvc\nlw a1, 0(s4)\n.option pop\n");
    a0 = a0 | a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a0, 43(sp)\n.option pop\n");
    CALL_PORT("lw a5, 76(s0)");
    a2 = UINT32_C(16); LIVE;
    CALL_PORT("addi a0, sp, 44");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 13586..13598 */
REGION void tsl9_callback_flow_block_13586(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlw a1, 0(s4)\n.option pop\n");
    CALL_PORT("lw a5, 76(s0)");
    a2 = UINT32_C(16); LIVE;
    a1 = a1 + 0x60u; LIVE;
    CALL_PORT(".option push\n.option norvc\naddi a0, sp, 79\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 13598..135AC */
REGION void tsl9_callback_flow_block_13598(void)
{
    REGS;
    CALL_PORT("add s1, s1, s7");
    CALL_PORT(".option push\n.option norvc\nlhu a0, 2(s1)\n.option pop\n");
    a3 = UINT32_C(76); LIVE;
    CALL_PORT("addi a2, sp, 20");
    a1 = UINT32_C(160); LIVE;
    CALL_PORT(".Lcallback_flow_edge_135a8:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_135a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_filter_external_8a56\n");
    __builtin_unreachable();
}

/* Original 135AC..135B0 */
REGION void tsl9_callback_flow_block_135ac(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_edge_135ac:\n.option push\n.option norvc\nbeqz s2,.Lcallback_flow_edge_135ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_135c6\n");
    __builtin_unreachable();
}

/* Original 135B0..135C6 */
REGION void tsl9_callback_flow_block_135b0(void)
{
    REGS;
    CALL_PORT("lw ra, 140(sp)");
    CALL_PORT("lw s0, 136(sp)");
    CALL_PORT("lw s1, 132(sp)");
    CALL_PORT("lw s2, 128(sp)");
    CALL_PORT("lw s3, 124(sp)");
    CALL_PORT("lw s4, 120(sp)");
    CALL_PORT("lw s5, 116(sp)");
    CALL_PORT("lw s6, 112(sp)");
    CALL_PORT("lw s7, 108(sp)");
    CALL_PORT("addi sp, sp, 144");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 135C6..135CA */
REGION void tsl9_callback_flow_block_135c6(void)
{
    REGS;
    CALL_PORT("li s2, 1");
    CALL_PORT(".Lcallback_flow_edge_135c8:\nc.j .Lcallback_flow_edge_135c8\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_block_133c4\n");
    __builtin_unreachable();
}

/* Original 135CA..135D8 */
REGION void tsl9_callback_flow_block_135ca(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsh zero, 38(sp)\n.option pop\n");
    CALL_PORT("lw a5, 72(s0)");
    CALL_PORT("addi a0, sp, 44");
    a2 = UINT32_C(16); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 135D8..135E4 */
REGION void tsl9_callback_flow_block_135d8(void)
{
    REGS;
    CALL_PORT("lw a5, 72(s0)");
    a2 = UINT32_C(16); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\naddi a0, sp, 79\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 135E4..135E6 */
REGION void tsl9_callback_flow_block_135e4(void)
{
    REGS;
    CALL_PORT(".Lcallback_flow_edge_135e4:\nc.j .Lcallback_flow_edge_135e4\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_block_13598\n");
    __builtin_unreachable();
}

/* Original 135E6..135FE */
REGION void tsl9_callback_flow_entry_135e6(void)
{
    REGS;
    a4 = UINT32_C(0x10000); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fff9\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + 430u); LIVE;
    a4 = a4 + 0xfffffffeu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    a5 = a5 + 0x1a2u; LIVE;
    CALL_PORT(".Lcallback_flow_edge_135fa:\n.option push\n.option norvc\nbeq a3,a4,.Lcallback_flow_edge_135fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_13612\n");
    __builtin_unreachable();
}

/* Original 135FE..13608 */
REGION void tsl9_callback_flow_block_135fe(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 5u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_13606:\nc.beqz a4,.Lcallback_flow_edge_13606\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_13612\n");
    __builtin_unreachable();
}

/* Original 13608..13612 */
REGION void tsl9_callback_flow_block_13608(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 4u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_13610:\nc.bnez a4,.Lcallback_flow_edge_13610\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_13634\n");
    __builtin_unreachable();
}

/* Original 13612..13620 */
REGION void tsl9_callback_flow_block_13612(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + 6u); LIVE;
    a4 = UINT32_C(0x10000); LIVE;
    a4 = a4 + 0xfffffffeu; LIVE;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_flow_edge_1361c:\n.option push\n.option norvc\nbeq a4,a3,.Lcallback_flow_edge_1361c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_1365e\n");
    __builtin_unreachable();
}

/* Original 13620..1362A */
REGION void tsl9_callback_flow_block_13620(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 9u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_13628:\nc.beqz a4,.Lcallback_flow_edge_13628\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_1365e\n");
    __builtin_unreachable();
}

/* Original 1362A..13634 */
REGION void tsl9_callback_flow_block_1362a(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + 8u); LIVE;
    a0 = a0 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_flow_edge_13632:\nc.beqz a0,.Lcallback_flow_edge_13632\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_flow_block_1365e\n");
    __builtin_unreachable();
}

/* Original 13634..13656 */
REGION void tsl9_callback_flow_block_13634(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    a5 = UINT32_C(1); LIVE;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(300); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_flow_literal_13640:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_flow_entry_1333c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_flow_literal_13640\n.option pop\n");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + 330u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Lcallback_flow_edge_13652:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_13652\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original 13656..1365E */
REGION void tsl9_callback_flow_block_13656(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    a0 = UINT32_C(1); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 1365E..13660 */
REGION void tsl9_callback_flow_block_1365e(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 16DD4..16DE2 */
REGION void tsl9_callback_flow_entry_16dd4(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT("sw zero, 8(sp)");
    CALL_PORT("sw zero, 12(sp)");
    a5 = UINT32_C(1); LIVE;
    CALL_PORT(".Lcallback_flow_edge_16dde:\n.option push\n.option norvc\nbne a0,a5,.Lcallback_flow_edge_16dde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_16dfc\n");
    __builtin_unreachable();
}

/* Original 16DE2..16DEA */
REGION void tsl9_callback_flow_block_16de2(void)
{
    REGS;
    a5 = UINT32_C(0x1450000); LIVE;
    a5 = a5 + 0x399u; LIVE;
    __builtin_unreachable();
}

/* Original 16DEA..16DEC */
REGION void tsl9_callback_flow_block_16dea(void)
{
    REGS;
    CALL_PORT("sw a5, 8(sp)");
    __builtin_unreachable();
}

/* Original 16DEC..16DF6 */
REGION void tsl9_callback_flow_block_16dec(void)
{
    REGS;
    CALL_PORT("addi a1, sp, 8");
    a3 = UINT32_C(1); LIVE;
    a2 = UINT32_C(8); LIVE;
    CALL_PORT(".Lcallback_flow_edge_16df2:\n.option push\n.option norvc\njal ra,.Lcallback_flow_edge_16df2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_16cc4\n");
    __builtin_unreachable();
}

/* Original 16DF6..16DFC */
REGION void tsl9_callback_flow_block_16df6(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 16DFC..16E02 */
REGION void tsl9_callback_flow_block_16dfc(void)
{
    REGS;
    a5 = UINT32_C(2); LIVE;
    CALL_PORT(".Lcallback_flow_edge_16dfe:\n.option push\n.option norvc\nbne a0,a5,.Lcallback_flow_edge_16dfe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_flow_block_16dec\n");
    __builtin_unreachable();
}

/* Original 16E02..16E0C */
REGION void tsl9_callback_flow_block_16e02(void)
{
    REGS;
    a5 = UINT32_C(0x39b0000); LIVE;
    a5 = a5 + 0x370u; LIVE;
    CALL_PORT(".Lcallback_flow_edge_16e0a:\nc.j .Lcallback_flow_edge_16e0a\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_block_16dea\n");
    __builtin_unreachable();
}

/* Original 96B source passed to the local19BF0 provider; its implementation remains unresolved. */
ENTRY __attribute__((used,section(".rodata.tsl9_callback_flow_constants_19ca8"),aligned(4)))
const uint8_t tsl9_callback_flow_constants_19ca8[96] = {225,2,41,1,41,2,87,2,115,2,51,3,194,3,226,3,245,3,243,2,130,0,179,3,93,2,24,1,195,3,73,2,233,3,157,3,2,1,3,1,58,3,182,3,227,3,223,3,90,2,182,2,52,3,216,3,102,2,229,2,31,3,254,3,147,2,226,4,227,4,12,2,67,2,33,3,253,3,243,4,249,1,57,3,120,6,121,6,50,3,56,2,255,7,5,4};
