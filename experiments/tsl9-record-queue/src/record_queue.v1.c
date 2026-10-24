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

/* Original1787C..1798A only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Queue16B/constructor32B frames andno-frame encoder share the1787C path.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 1787C..1789A */
REGION void tsl9_record_queue_entry_1787c(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc s1, 0x1fff5\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlbu s1, 44(s1)\n.option pop\n");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 34u); LIVE;
    a5 = UINT32_C(15); LIVE;
    CALL_PORT(".Lrecord_control_edge_17896:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_control_edge_17896\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_queue_block_178dc\n");
    __builtin_unreachable();
}

/* Original 1789A..178BE */
REGION void tsl9_record_queue_block_1789a(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc s0, 0x1fff5\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi s0, s0, 18\n.option pop\n");
    CALL_PORT("mv a1, a0");
    CALL_PORT(".option push\n.option norvc\nlbu a0, 1(s0)\n.option pop\n");
    a5 = UINT32_C(7); LIVE;
    a4 = UINT32_C(0x40000); LIVE;
    a5 = a5 * a0; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + 76u); LIVE;
    a2 = UINT32_C(7); LIVE;
    a5 = a5 + 0x3u; LIVE;
    CALL_PORT(".option push\n.option norvc\nadd a0, s0, a5\n.option pop\n");
    CALL_PORT("c.jalr a4");
    __builtin_unreachable();
}

/* Original 178BE..178DC */
REGION void tsl9_record_queue_block_178be(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 1(s0)\n.option pop\n");
    a5 = a5 + 0x1u; LIVE;
    a5 = a5 & 0xfu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 - 25u) = (uint8_t)a5; LIVE;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 2(s0)\n.option pop\n");
    a5 = a5 + 0x1u; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 - 38u) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original 178DC..178DE */
REGION void tsl9_record_queue_block_178dc(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_178dc:\nc.bnez s1,.Lrecord_control_edge_178dc\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_queue_block_178ee\n");
    __builtin_unreachable();
}

/* Original 178DE..178EE */
REGION void tsl9_record_queue_block_178de(void)
{
    REGS;
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s1, 4(sp)");
    a0 = UINT32_C(255); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT(".Lrecord_control_edge_178ea:\n.option push\n.option norvc\njal zero,.Lrecord_control_edge_178ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_provider_17666\n");
    __builtin_unreachable();
}

/* Original 178EE..178F8 */
REGION void tsl9_record_queue_block_178ee(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw s1, 4(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 178F8..1790A */
REGION void tsl9_record_queue_entry_178f8(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 72u); LIVE;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT("addi a0, sp, 8");
    a2 = UINT32_C(7); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 1790A..17942 */
REGION void tsl9_record_queue_block_1790a(void)
{
    REGS;
    CALL_PORT("lw a5, 8(sp)");
    a4 = UINT32_C(0xff001000); LIVE;
    a4 = a4 + 0xfffffc00u; LIVE;
    a5 = a5 & 0x3ffu; LIVE;
    a5 = a5 | a4; LIVE;
    CALL_PORT("sw a5, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nlhu a5, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0xffffe000); LIVE;
    CALL_PORT("addi a0, sp, 8");
    a5 = a5 & a4; LIVE;
    a4 = UINT32_C(0x2000); LIVE;
    a4 = a4 + 0xffffff00u; LIVE;
    a5 = a5 | a4; LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 12(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlbu a5, 14(sp)\n.option pop\n");
    a5 = a5 | 0xffffff80u; LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 14(sp)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_1793e:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_1793e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_1787c\n");
    __builtin_unreachable();
}

/* Original 17942..17948 */
REGION void tsl9_record_queue_block_17942(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 17948..1796C */
REGION void tsl9_record_queue_entry_17948(void)
{
    REGS;
    a0 = a0 & 0x3fu; LIVE;
    a5 = a0 << 10u; LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a2 + 0u); LIVE;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + 0x3ffu; LIVE;
    a0 = a0 & a4; LIVE;
    a0 = a0 | a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + 6u); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + 0u) = (uint32_t)a0; LIVE;
    a5 = a5 | 0xffffff80u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a2 + 6u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Lrecord_control_edge_1796a:\nc.beqz a1,.Lrecord_control_edge_1796a\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_queue_block_17988\n");
    __builtin_unreachable();
}

/* Original 1796C..17972 */
REGION void tsl9_record_queue_block_1796c(void)
{
    REGS;
    a5 = UINT32_C(2); LIVE;
    CALL_PORT(".Lrecord_control_edge_1796e:\n.option push\n.option norvc\nbeq a1,a5,.Lrecord_control_edge_1796e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_queue_block_17982\n");
    __builtin_unreachable();
}

/* Original 17972..17982 */
REGION void tsl9_record_queue_block_17972(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a2 + 4u); LIVE;
    a4 = UINT32_C(0x2000); LIVE;
    a4 = a4 + 0xffffff00u; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a2 + 4u) = (uint16_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original 17982..17988 */
REGION void tsl9_record_queue_block_17982(void)
{
    REGS;
    CALL_PORT("mv a0, a2");
    CALL_PORT(".Lrecord_control_edge_17984:\n.option push\n.option norvc\njal zero,.Lrecord_control_edge_17984\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_1787c\n");
    __builtin_unreachable();
}

/* Original 17988..1798A */
REGION void tsl9_record_queue_block_17988(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}
