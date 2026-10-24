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

/* Original17476..1753A only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Task16B frame/shared exits andframeless RF-status tail transfers remain explicit.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 17476..1748A */
REGION void tsl9_rf_callbacks_entry_17476(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    a5 = a1 << 16u; LIVE;
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT("srai a5, a5, 0x10");
    CALL_PORT("mv s0, a1");
    CALL_PORT(".Lrecord_control_edge_17486:\n.option push\n.option norvc\nbgez a5,.Lrecord_control_edge_17486\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_174a6\n");
    __builtin_unreachable();
}

/* Original 1748A..17492 */
REGION void tsl9_rf_callbacks_block_1748a(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    CALL_PORT("lw a5, 108(s1)");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17492..17494 */
REGION void tsl9_rf_callbacks_block_17492(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_17492:\nc.beqz a0,.Lrecord_control_edge_17492\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rf_callbacks_block_17498\n");
    __builtin_unreachable();
}

/* Original 17494..17498 */
REGION void tsl9_rf_callbacks_block_17494(void)
{
    REGS;
    CALL_PORT("lw a5, 104(s1)");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17498..1749C */
REGION void tsl9_rf_callbacks_block_17498(void)
{
    REGS;
    a0 = UINT32_C(0x8000); LIVE;
    CALL_PORT("xor a0, a0, s0");
    __builtin_unreachable();
}

/* Original 1749C..174A6 */
REGION void tsl9_rf_callbacks_block_1749c(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw s1, 4(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 174A6..174AC */
REGION void tsl9_rf_callbacks_block_174a6(void)
{
    REGS;
    a5 = a1 & 0x1u; LIVE;
    CALL_PORT(".Lrecord_control_edge_174aa:\nc.beqz a5,.Lrecord_control_edge_174aa\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rf_callbacks_block_174da\n");
    __builtin_unreachable();
}

/* Original 174AC..174B6 */
REGION void tsl9_rf_callbacks_block_174ac(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a5, 464(s1)\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 174B6..174D4 */
REGION void tsl9_rf_callbacks_block_174b6(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlw a5, 460(s1)\n.option pop\n");
    a3 = UINT32_C(255); LIVE;
    a2 = UINT32_C(255); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a1, 0x1fff5\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + 743u); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + 0x2e0u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 174D4..174DA */
REGION void tsl9_rf_callbacks_block_174d4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_174d8:\nc.j .Lrecord_control_edge_174d8\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rf_callbacks_block_1749c\n");
    __builtin_unreachable();
}

/* Original 174DA..174E2 */
REGION void tsl9_rf_callbacks_block_174da(void)
{
    REGS;
    a5 = a1 & 0x2u; LIVE;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lrecord_control_edge_174e0:\nc.beqz a5,.Lrecord_control_edge_174e0\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rf_callbacks_block_1749c\n");
    __builtin_unreachable();
}

/* Original 174E2..174E8 */
REGION void tsl9_rf_callbacks_block_174e2(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lrecord_control_edge_174e4:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_174e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rf_callbacks_provider_173ee\n");
    __builtin_unreachable();
}

/* Original 174E8..174EE */
REGION void tsl9_rf_callbacks_block_174e8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_174ec:\nc.j .Lrecord_control_edge_174ec\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rf_callbacks_block_1749c\n");
    __builtin_unreachable();
}

/* Original 174EE..174F4 */
REGION void tsl9_rf_callbacks_entry_174ee(void)
{
    REGS;
    a5 = UINT32_C(2); LIVE;
    CALL_PORT(".Lrecord_control_edge_174f0:\n.option push\n.option norvc\nbeq a0,a5,.Lrecord_control_edge_174f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17508\n");
    __builtin_unreachable();
}

/* Original 174F4..174F8 */
REGION void tsl9_rf_callbacks_block_174f4(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_174f4:\n.option push\n.option norvc\nbltu a0,a5,.Lrecord_control_edge_174f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17538\n");
    __builtin_unreachable();
}

/* Original 174F8..17504 */
REGION void tsl9_rf_callbacks_block_174f8(void)
{
    REGS;
    a0 = a0 + 0xffffffefu; LIVE;
    a0 = a0 & 0xffu; LIVE;
    a5 = UINT32_C(1); LIVE;
    CALL_PORT(".Lrecord_control_edge_17500:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_control_edge_17500\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17538\n");
    __builtin_unreachable();
}

/* Original 17504..17508 */
REGION void tsl9_rf_callbacks_block_17504(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_17504:\n.option push\n.option norvc\njal zero,.Lrecord_control_edge_17504\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rf_callbacks_provider_17442\n");
    __builtin_unreachable();
}

/* Original 17508..1750A */
REGION void tsl9_rf_callbacks_block_17508(void)
{
    REGS;
    CALL_PORT(".Lrecord_control_edge_17508:\nc.bnez a1,.Lrecord_control_edge_17508\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rf_callbacks_block_17504\n");
    __builtin_unreachable();
}

/* Original 1750A..17512 */
REGION void tsl9_rf_callbacks_block_1750a(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + 1u); LIVE;
    CALL_PORT(".Lrecord_control_edge_1750e:\n.option push\n.option norvc\nbne a5,a0,.Lrecord_control_edge_1750e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17504\n");
    __builtin_unreachable();
}

/* Original 17512..17522 */
REGION void tsl9_rf_callbacks_block_17512(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + 2u); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 660u); LIVE;
    CALL_PORT(".Lrecord_control_edge_1751e:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_control_edge_1751e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17504\n");
    __builtin_unreachable();
}

/* Original 17522..17532 */
REGION void tsl9_rf_callbacks_block_17522(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + 3u); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 645u); LIVE;
    CALL_PORT(".Lrecord_control_edge_1752e:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_control_edge_1752e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rf_callbacks_block_17504\n");
    __builtin_unreachable();
}

/* Original 17532..17538 */
REGION void tsl9_rf_callbacks_block_17532(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lrecord_control_edge_17534:\n.option push\n.option norvc\njal zero,.Lrecord_control_edge_17534\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rf_callbacks_provider_173ee\n");
    __builtin_unreachable();
}

/* Original 17538..1753A */
REGION void tsl9_rf_callbacks_block_17538(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}
