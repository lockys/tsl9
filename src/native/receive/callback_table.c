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

/* Original901A..9124 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Shared loop9070 is not a function entry; genuine frame entries901A,907A,90B0.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 901A..9026 */
REGION void tsl9_callback_table_entry_901a(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT("li s0, 0");
    a4 = UINT32_C(15); LIVE;
    __builtin_unreachable();
}

/* Original 9026..902E */
REGION void tsl9_callback_table_block_9026(void)
{
    REGS;
    CALL_PORT("sra a5, a1, s0");
    a5 = a5 & 0x1u; LIVE;
    CALL_PORT(".Lcallback_edge_902c:\nc.beqz a5,.Lcallback_edge_902c\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_table_block_9070\n");
    __builtin_unreachable();
}

/* Original 902E..9044 */
REGION void tsl9_callback_table_block_902e(void)
{
    REGS;
    a5 = UINT32_C(12); LIVE;
    CALL_PORT("mul a4, s0, a5");
    CALL_PORT("auipc a5, 0x20003");
    a5 = a5 + 0xfffffdd4u; LIVE;
    CALL_PORT("mv s1, a1");
    a5 = a5 + a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + 4u); LIVE;
    CALL_PORT(".Lcallback_edge_9042:\nc.beqz a3,.Lcallback_edge_9042\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_table_block_905a\n");
    __builtin_unreachable();
}

/* Original 9044..9050 */
REGION void tsl9_callback_table_block_9044(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + 0u); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + 8u); LIVE;
    a4 = a4 & 0xffu; LIVE;
    CALL_PORT(".Lcallback_edge_904e:\nc.bnez a4,.Lcallback_edge_904e\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_table_block_9058\n");
    __builtin_unreachable();
}

/* Original 9050..9058 */
REGION void tsl9_callback_table_block_9050(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + 4u) = 0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 8u) = 0; LIVE;
    __builtin_unreachable();
}

/* Original 9058..905A */
REGION void tsl9_callback_table_block_9058(void)
{
    REGS;
    CALL_PORT("c.jalr a3");
    __builtin_unreachable();
}

/* Original 905A..9066 */
REGION void tsl9_callback_table_block_905a(void)
{
    REGS;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT("sll a0, a0, s0");
    CALL_PORT("xor a0, a0, s1");
    a0 = a0 << 16u; LIVE;
    a0 = a0 >> 16u; LIVE;
    __builtin_unreachable();
}

/* Original 9066..9070 */
REGION void tsl9_callback_table_block_9066(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw s1, 4(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 9070..9076 */
REGION void tsl9_callback_table_block_9070(void)
{
    REGS;
    CALL_PORT("addi s0, s0, 1");
    CALL_PORT(".Lcallback_edge_9072:\n.option push\n.option norvc\nbne s0,a4,.Lcallback_edge_9072\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_table_block_9026\n");
    __builtin_unreachable();
}

/* Original 9076..907A */
REGION void tsl9_callback_table_block_9076(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    CALL_PORT(".Lcallback_edge_9078:\nc.j .Lcallback_edge_9078\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_table_block_9066\n");
    __builtin_unreachable();
}

/* Original 907A..9096 */
REGION void tsl9_callback_table_entry_907a(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("lui s0, 0x40");
    CALL_PORT("lw a5, 72(s0)");
    CALL_PORT("sw ra, 12(sp)");
    a2 = UINT32_C(180); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT("auipc a0, 0x20003");
    a0 = a0 + 0xfffffd7cu; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 9096..90A4 */
REGION void tsl9_callback_table_block_9096(void)
{
    REGS;
    CALL_PORT("lw a5, 128(s0)");
    CALL_PORT("auipc a0, 0x0");
    a0 = a0 + 0xffffff80u; LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 90A4..90B0 */
REGION void tsl9_callback_table_block_90a4(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("sb a0, 166(gp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 90B0..90C6 */
REGION void tsl9_callback_table_entry_90b0(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("auipc a5, 0x20003");
    a5 = a5 + 0xfffffd56u; LIVE;
    CALL_PORT("sw s0, 8(sp)");
    CALL_PORT("sw s1, 4(sp)");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("li s0, 0");
    CALL_PORT("mv s1, a5");
    a4 = UINT32_C(15); LIVE;
    __builtin_unreachable();
}

/* Original 90C6..90CC */
REGION void tsl9_callback_table_block_90c6(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + 4u); LIVE;
    CALL_PORT(".Lcallback_edge_90c8:\n.option push\n.option norvc\nbne a3,a0,.Lcallback_edge_90c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_table_block_9110\n");
    __builtin_unreachable();
}

/* Original 90CC..90D8 */
REGION void tsl9_callback_table_block_90cc(void)
{
    REGS;
    a5 = UINT32_C(12); LIVE;
    CALL_PORT("mul a5, s0, a5");
    CALL_PORT("add a5, a5, s1");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + 8u); LIVE;
    CALL_PORT(".Lcallback_edge_90d6:\nc.beqz a0,.Lcallback_edge_90d6\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_table_block_90e0\n");
    __builtin_unreachable();
}

/* Original 90D8..90E0 */
REGION void tsl9_callback_table_block_90d8(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 104u); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 90E0..9110 */
REGION void tsl9_callback_table_block_90e0(void)
{
    REGS;
    a5 = UINT32_C(12); LIVE;
    CALL_PORT("mul a5, s0, a5");
    a1 = UINT32_C(1); LIVE;
    CALL_PORT("sll a1, a1, s0");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw ra, 12(sp)");
    a1 = a1 << 16u; LIVE;
    CALL_PORT("lbu a0, 166(gp)");
    a1 = a1 >> 16u; LIVE;
    CALL_PORT("add s1, s1, a5");
    a5 = UINT32_C(0x40000); LIVE;
    CALL_PORT("sw zero, 4(s1)");
    CALL_PORT("sw zero, 8(s1)");
    CALL_PORT("lw t1, 92(a5)");
    CALL_PORT("lw s1, 4(sp)");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("jr t1");
    __builtin_unreachable();
}

/* Original 9110..9118 */
REGION void tsl9_callback_table_block_9110(void)
{
    REGS;
    CALL_PORT("addi s0, s0, 1");
    a5 = a5 + 0xcu; LIVE;
    CALL_PORT(".Lcallback_edge_9114:\n.option push\n.option norvc\nbne s0,a4,.Lcallback_edge_9114\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_table_block_90c6\n");
    __builtin_unreachable();
}

/* Original 9118..9124 */
REGION void tsl9_callback_table_block_9118(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("lw s0, 8(sp)");
    CALL_PORT("lw s1, 4(sp)");
    a0 = UINT32_C(1); LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}
