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

/* Original979E..9958 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * SP/S registers, AUIPC, signed DIV, calls and MRET stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 979E..97B6 */
REGION void tsl9_timer3_entry_979e(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    __asm__ volatile("sw s0, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("lui s0, 0x40000":::"memory"); LIVE;
    __asm__ volatile("addi s0, s0, 1024":::"memory"); LIVE;
    __asm__ volatile("lhu a5, 16(s0)":"=r"(a5)::"memory"); LIVE;
    __asm__ volatile("sw s1, 8(sp)":::"memory"); LIVE;
    __asm__ volatile("sw s2, 4(sp)":::"memory"); LIVE;
    a5 = a5 & 0x1u; LIVE;
    CALL_PORT(".Ltimer_edge_97b4:\nc.beqz a5,.Ltimer_edge_97b4\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}

/* Original 97B6..97D6 */
REGION void tsl9_timer3_block_97b6(void)
{
    REGS;
    __asm__ volatile("lhu a5, 16(s0)":"=r"(a5)::"memory"); LIVE;
    __asm__ volatile("auipc s2, 0x20002":::"memory"); LIVE;
    __asm__ volatile("addi s2, s2, 1794":::"memory"); LIVE;
    __asm__ volatile("mv s1, s2":::"memory"); LIVE;
    a5 = a5 << 16u; LIVE;
    a5 = a5 >> 16u; LIVE;
    a5 = a5 & 0xfffffffeu; LIVE;
    a5 = a5 << 16u; LIVE;
    a5 = a5 >> 16u; LIVE;
    __asm__ volatile("sh a5, 16(s0)"::"r"(a5):"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_97d2:\n.option push\n.option norvc\njal ra,.Ltimer_edge_97d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original 97D6..97DE */
REGION void tsl9_timer3_block_97d6(void)
{
    REGS;
    __asm__ volatile("lw a5, 0(s2)":"=r"(a5)::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_97da:\n.option push\n.option norvc\nbltu a0,a5,.Ltimer_edge_97da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}

/* Original 97DE..97EC */
REGION void tsl9_timer3_block_97de(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 1763u); LIVE;
    a4 = UINT32_C(1); LIVE;
    CALL_PORT(".Ltimer_edge_97e8:\n.option push\n.option norvc\nbeq a5,a4,.Ltimer_edge_97e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_timer3_block_9892\n");
    __builtin_unreachable();
}

/* Original 97EC..97EE */
REGION void tsl9_timer3_block_97ec(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_97ec:\nc.beqz a5,.Ltimer_edge_97ec\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_9806\n");
    __builtin_unreachable();
}

/* Original 97EE..97F4 */
REGION void tsl9_timer3_block_97ee(void)
{
    REGS;
    a4 = UINT32_C(2); LIVE;
    CALL_PORT(".Ltimer_edge_97f0:\n.option push\n.option norvc\nbeq a5,a4,.Ltimer_edge_97f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_timer3_block_98cc\n");
    __builtin_unreachable();
}

/* Original 97F4..97FA */
REGION void tsl9_timer3_block_97f4(void)
{
    REGS;
    a4 = UINT32_C(3); LIVE;
    CALL_PORT(".Ltimer_edge_97f6:\n.option push\n.option norvc\nbeq a5,a4,.Ltimer_edge_97f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_timer3_block_993a\n");
    __builtin_unreachable();
}

/* Original 97FA..9806 */
REGION void tsl9_timer3_block_97fa(void)
{
    REGS;
    __asm__ volatile("lw s0, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("lw s1, 8(sp)":::"memory"); LIVE;
    __asm__ volatile("lw s2, 4(sp)":::"memory"); LIVE;
    __asm__ volatile("addi sp, sp, 16":::"memory"); LIVE;
    __asm__ volatile("mret":::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 9806..9842 */
REGION void tsl9_timer3_block_9806(void)
{
    REGS;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1724u); LIVE;
    a3 = UINT32_C(6); LIVE;
    a4 = a4 * a3; LIVE;
    __asm__ volatile("lw a5, 16(s2)":"=r"(a5)::"memory"); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + 0u); LIVE;
    a5 = UINT32_C(0xf4000); LIVE;
    a5 = a5 + 0x240u; LIVE;
    __asm__ volatile("div a5, a5, a4":"+r"(a5):"r"(a4):"memory"); LIVE;
    a4 = UINT32_C(200); LIVE;
    a5 = a5 + 0xffffffffu; LIVE;
    a5 = a5 << 16u; LIVE;
    a5 = a5 >> 16u; LIVE;
    __asm__ volatile("sh a5, 44(s0)"::"r"(a5):"memory"); LIVE;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 1672u); LIVE;
    CALL_PORT(".Ltimer_edge_9840:\nc.bnez a5,.Ltimer_edge_9840\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_984c\n");
    __builtin_unreachable();
}

/* Original 9842..984C */
REGION void tsl9_timer3_block_9842(void)
{
    REGS;
    __asm__ volatile("addi a5, gp, 84":"=r"(a5)::"memory"); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 2u); LIVE;
    __builtin_unreachable();
}

/* Original 984C..9864 */
REGION void tsl9_timer3_block_984c(void)
{
    REGS;
    a5 = UINT32_C(0x40000000); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + 1084u) = (uint16_t)a4; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + 1084u); LIVE;
    a4 = UINT32_C(200); LIVE;
    a5 = a5 + 0x400u; LIVE;
    CALL_PORT(".Ltimer_edge_9860:\n.option push\n.option norvc\nbleu a3,a4,.Ltimer_edge_9860\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_timer3_block_9868\n");
    __builtin_unreachable();
}

/* Original 9864..9868 */
REGION void tsl9_timer3_block_9864(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a5 + 60u) = (uint16_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original 9868..986C */
REGION void tsl9_timer3_block_9868(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9868:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9868\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original 986C..988C */
REGION void tsl9_timer3_block_986c(void)
{
    REGS;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1622u); LIVE;
    a3 = UINT32_C(6); LIVE;
    a4 = a4 * a3; LIVE;
    __asm__ volatile("lw a5, 16(s1)":"=r"(a5)::"memory"); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 2u); LIVE;
    a0 = a0 + a5; LIVE;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 1592u) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original 988C..9892 */
REGION void tsl9_timer3_block_988c(void)
{
    REGS;
    __asm__ volatile("lbu a5, 5(s1)":"=r"(a5)::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_9890:\nc.j .Ltimer_edge_9890\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_98c0\n");
    __builtin_unreachable();
}

/* Original 9892..989A */
REGION void tsl9_timer3_block_9892(void)
{
    REGS;
    __asm__ volatile("sh zero, 60(s0)":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_9896:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9896\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original 989A..98C0 */
REGION void tsl9_timer3_block_989a(void)
{
    REGS;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1576u); LIVE;
    a3 = UINT32_C(6); LIVE;
    a4 = a4 * a3; LIVE;
    __asm__ volatile("lw a5, 16(s2)":"=r"(a5)::"memory"); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 4u); LIVE;
    a0 = a0 + a5; LIVE;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 1544u) = (uint32_t)a0; LIVE;
    __asm__ volatile("lbu a5, 5(s2)":"=r"(a5)::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 98C0..98CC */
REGION void tsl9_timer3_block_98c0(void)
{
    REGS;
    a5 = a5 + 0x1u; LIVE;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 1535u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Ltimer_edge_98ca:\nc.j .Ltimer_edge_98ca\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}

/* Original 98CC..98F0 */
REGION void tsl9_timer3_block_98cc(void)
{
    REGS;
    __asm__ volatile("lbu a5, 6(s2)":"=r"(a5)::"memory"); LIVE;
    __asm__ volatile("lw a0, 16(s2)":"=r"(a0)::"memory"); LIVE;
    a5 = a5 + 0x1u; LIVE;
    a5 = a5 & 0xffu; LIVE;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + 1512u) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(6); LIVE;
    a5 = a5 * a4; LIVE;
    a5 = a5 + a0; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 0u); LIVE;
    CALL_PORT(".Ltimer_edge_98ee:\nc.bnez a5,.Ltimer_edge_98ee\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_9930\n");
    __builtin_unreachable();
}

/* Original 98F0..98F2 */
REGION void tsl9_timer3_block_98f0(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_98f0:\nc.beqz a0,.Ltimer_edge_98f0\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_9902\n");
    __builtin_unreachable();
}

/* Original 98F2..98FA */
REGION void tsl9_timer3_block_98f2(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 104u); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 98FA..9902 */
REGION void tsl9_timer3_block_98fa(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 1490u) = 0; LIVE;
    __builtin_unreachable();
}

/* Original 9902..990C */
REGION void tsl9_timer3_block_9902(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 1474u); LIVE;
    CALL_PORT(".Ltimer_edge_990a:\nc.beqz a5,.Ltimer_edge_990a\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_992c\n");
    __builtin_unreachable();
}

/* Original 990C..9910 */
REGION void tsl9_timer3_block_990c(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_990c:\n.option push\n.option norvc\njal ra,.Ltimer_edge_990c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original 9910..992C */
REGION void tsl9_timer3_block_9910(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + 1460u); LIVE;
    a0 = a0 + a5; LIVE;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 1442u) = (uint32_t)a0; LIVE;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + 1442u) = 0; LIVE;
    CALL_PORT(".Ltimer_edge_992a:\nc.j .Ltimer_edge_992a\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_988c\n");
    __builtin_unreachable();
}

/* Original 992C..992E */
REGION void tsl9_timer3_block_992c(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_992c:\nc.jal .Ltimer_edge_992c\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_disarm_93ee\n");
    __builtin_unreachable();
}

/* Original 992E..9930 */
REGION void tsl9_timer3_block_992e(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_992e:\nc.j .Ltimer_edge_992e\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}

/* Original 9930..993A */
REGION void tsl9_timer3_block_9930(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1425u) = 0; LIVE;
    CALL_PORT(".Ltimer_edge_9938:\nc.j .Ltimer_edge_9938\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}

/* Original 993A..993C */
REGION void tsl9_timer3_block_993a(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_993a:\nc.jal .Ltimer_edge_993a\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_disarm_93ee\n");
    __builtin_unreachable();
}

/* Original 993C..9942 */
REGION void tsl9_timer3_block_993c(void)
{
    REGS;
    __asm__ volatile("lw a5, 12(s2)":"=r"(a5)::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_9940:\nc.beqz a5,.Ltimer_edge_9940\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_timer3_block_994e\n");
    __builtin_unreachable();
}

/* Original 9942..994E */
REGION void tsl9_timer3_block_9942(void)
{
    REGS;
    __asm__ volatile("auipc a4, 0x20002":"=r"(a4)::"memory"); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 1414u) = 0; LIVE;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 994E..9958 */
REGION void tsl9_timer3_block_994e(void)
{
    REGS;
    __asm__ volatile("auipc a5, 0x20002":"=r"(a5)::"memory"); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1394u) = 0; LIVE;
    CALL_PORT(".Ltimer_edge_9956:\nc.j .Ltimer_edge_9956\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_timer3_block_97fa\n");
    __builtin_unreachable();
}
