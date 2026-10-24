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

/* Original1753A..17666 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * OriginalA6/A7 ports,guard-before-frame and16B/48B frames remain explicit.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 1753A..17546 */
REGION void tsl9_resident_providers_entry_1753a(void)
{
    REGS;
    CALL_PORT("mv a7, a2");
    CALL_PORT(".option push\n.option norvc\nauipc a2, 0x1fff5\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + 621u); LIVE;
    CALL_PORT(".Lrecord_control_edge_17544:\nc.bnez a2,.Lrecord_control_edge_17544\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_providers_block_175e4\n");
    __builtin_unreachable();
}

/* Original 17546..175B0 */
REGION void tsl9_resident_providers_block_17546(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a6, 366(gp)\n.option pop\n");
    CALL_PORT("addi a6, a6, 1");
    CALL_PORT(".option push\n.option norvc\nandi a6, a6, 15\n.option pop\n");
    CALL_PORT("mv a2, a4");
    CALL_PORT(".option push\n.option norvc\nsb a6, 366(gp)\n.option pop\n");
    a4 = a0 << 8u; LIVE;
    CALL_PORT("slli a6, a6, 0x4");
    a0 = a0 >> 8u; LIVE;
    CALL_PORT(".option push\n.option norvc\nor a6, a7, a6\n.option pop\n");
    a0 = a0 | a4; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + 582u) = (uint16_t)a0; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nsb a6, 576(a4)\n.option pop\n");
    CALL_PORT("addi sp, sp, -16");
    a4 = UINT32_C(50); LIVE;
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT("mv s1, a1");
    CALL_PORT("mv a1, a3");
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + 552u) = (uint8_t)a4; LIVE;
    a4 = a2 + 0x3u; LIVE;
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + 539u) = (uint8_t)a4; LIVE;
    CALL_PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + 522u) = (uint32_t)a5; LIVE;
    CALL_PORT("lw a5, 76(s0)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = a0 + 0x207u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 175B0..175B8 */
REGION void tsl9_resident_providers_block_175b0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlw a5, 512(s0)\n.option pop\n");
    CALL_PORT("mv a0, s1");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 175B8..175CA */
REGION void tsl9_resident_providers_block_175b8(void)
{
    REGS;
    CALL_PORT("lw a5, 88(s0)");
    a2 = UINT32_C(320); LIVE;
    a1 = UINT32_C(2); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 480u); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 175CA..175D8 */
REGION void tsl9_resident_providers_block_175ca(void)
{
    REGS;
    CALL_PORT("lw a5, 80(s0)");
    a1 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fff5\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 466u); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 175D8..175E4 */
REGION void tsl9_resident_providers_block_175d8(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw s1, 4(sp)");
    a0 = UINT32_C(0); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 175E4..175E8 */
REGION void tsl9_resident_providers_block_175e4(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 175E8..17608 */
REGION void tsl9_resident_providers_entry_175e8(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -48");
    CALL_PORT("sw s0, 40(sp)");
    CALL_PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    CALL_PORT("lw a5, 72(s0)");
    CALL_PORT("sw s1, 36(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc s1, 0x1fff5\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\naddi s1, s1, 428\n.option pop\n");
    CALL_PORT("sw ra, 44(sp)");
    a2 = UINT32_C(268); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("mv a0, s1");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17608..17616 */
REGION void tsl9_resident_providers_block_17608(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x0\n.option pop\n");
    a0 = a0 + 0xfffffe6au; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17616..17626 */
REGION void tsl9_resident_providers_block_17616(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 0(s1)\n.option pop\n");
    CALL_PORT("lw a5, 72(s0)");
    CALL_PORT("mv a0, sp");
    a2 = UINT32_C(32); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 17626..1765C */
REGION void tsl9_resident_providers_block_17626(void)
{
    REGS;
    a5 = UINT32_C(0x8e89c000); LIVE;
    a5 = a5 + 0xfffffed6u; LIVE;
    CALL_PORT("sw a5, 8(sp)");
    a5 = UINT32_C(0x555000); LIVE;
    a5 = a5 + 0x555u; LIVE;
    CALL_PORT("sw a5, 12(sp)");
    a5 = UINT32_C(0x2000); LIVE;
    a5 = a5 + 0x501u; LIVE;
    CALL_PORT(".option push\n.option norvc\nsh a5, 0(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x0\n.option pop\n");
    a5 = a5 + 0xfffffeaau; LIVE;
    CALL_PORT("sw a5, 16(sp)");
    a5 = UINT32_C(4); LIVE;
    CALL_PORT(".option push\n.option norvc\nsb a5, 25(sp)\n.option pop\n");
    CALL_PORT(".option push\n.option norvc\nlw a5, 452(s0)\n.option pop\n");
    CALL_PORT("mv a0, sp");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 1765C..17666 */
REGION void tsl9_resident_providers_block_1765c(void)
{
    REGS;
    CALL_PORT("lw ra, 44(sp)");
    CALL_PORT("lw s0, 40(sp)");
    CALL_PORT("lw s1, 36(sp)");
    CALL_PORT("addi sp, sp, 48");
    CALL_PORT("ret");
    __builtin_unreachable();
}
