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

/* Original173EE..17476 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Completion16B frame/optional callback tail andframeless retry tail remain explicit.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 173EE..17408 */
REGION void tsl9_rf_completion_entry_173ee(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 92u); LIVE;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("mv s0, a0");
    a1 = UINT32_C(2); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 930u); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17408..17428 */
REGION void tsl9_rf_completion_block_17408(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + 928u) = 0; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + 921u) = 0; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = a5 + 0x388u; LIVE;
    CALL_PORT(".option push\n.option norvc\nlw t1, 4(a5)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_17424:\n.option push\n.option norvc\nbeqz t1,.Lrecord_control_edge_17424\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_completion_block_1743a\n");
    __builtin_unreachable();
}

/* Original 17428..1743A */
REGION void tsl9_rf_completion_block_17428(void)
{
    REGS;
    CALL_PORT("mv a0, s0");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + 886u) = 0; LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("jr t1");
    __builtin_unreachable();
}

/* Original 1743A..17442 */
REGION void tsl9_rf_completion_block_1743a(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 17442..1745A */
REGION void tsl9_rf_completion_entry_17442(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 870u); LIVE;
    a5 = a5 + 0xffffffffu; LIVE;
    a5 = a5 & 0xffu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + 856u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Lrecord_control_edge_17458:\nc.bnez a5,.Lrecord_control_edge_17458\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rf_completion_block_17460\n");
    __builtin_unreachable();
}

/* Original 1745A..17460 */
REGION void tsl9_rf_completion_block_1745a(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lrecord_control_edge_1745c:\n.option push\n.option norvc\njal zero,.Lrecord_control_edge_1745c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rf_completion_entry_173ee\n");
    __builtin_unreachable();
}

/* Original 17460..17476 */
REGION void tsl9_rf_completion_block_17460(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    CALL_PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    a2 = UINT32_C(2); LIVE;
    a1 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 820u); LIVE;
    CALL_PORT("jr t1");
    __builtin_unreachable();
}
