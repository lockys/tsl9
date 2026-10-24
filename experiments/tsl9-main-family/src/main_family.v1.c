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

/* Original8180..81AA,9008..901A,9250..9290 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * SP/S registers, calls, RA returns and no-link tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 8180..8198 */
REGION void tsl9_main_family_entry_8180(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    __asm__ volatile("sw s0, 8(sp)":::"memory"); LIVE;
    __asm__ volatile("lui s0, 0xb":::"memory"); LIVE;
    __asm__ volatile("sw s1, 4(sp)":::"memory"); LIVE;
    __asm__ volatile("sw s2, 0(sp)":::"memory"); LIVE;
    __asm__ volatile("sw ra, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("lui s2, 0x20000":::"memory"); LIVE;
    __asm__ volatile("lui s1, 0x40003":::"memory"); LIVE;
    __asm__ volatile("addi s0, s0, -1366":::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 8198..819E */
REGION void tsl9_main_family_block_8198(void)
{
    REGS;
    __asm__ volatile("lw a5, 0(s2)":"=r"(a5)::"memory"); LIVE;
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original 819E..81A2 */
REGION void tsl9_main_family_block_819e(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_819e:\n.option push\n.option norvc\njal ra,.Ltimer_edge_819e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_17002\n");
    __builtin_unreachable();
}

/* Original 81A2..81A6 */
REGION void tsl9_main_family_block_81a2(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_81a2:\n.option push\n.option norvc\njal ra,.Ltimer_edge_81a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_12c58\n");
    __builtin_unreachable();
}

/* Original 81A6..81AA */
REGION void tsl9_main_family_block_81a6(void)
{
    REGS;
    __asm__ volatile("sw s0, 0(s1)":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_81a8:\nc.j .Ltimer_edge_81a8\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_family_block_8198\n");
    __builtin_unreachable();
}

/* Original 9008..900E */
REGION void tsl9_main_family_entry_9008(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    __asm__ volatile("sw ra, 12(sp)":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_900c:\nc.jal .Ltimer_edge_900c\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_family_entry_9250\n");
    __builtin_unreachable();
}

/* Original 900E..9012 */
REGION void tsl9_main_family_block_900e(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_900e:\n.option push\n.option norvc\njal ra,.Ltimer_edge_900e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_family_entry_8180\n");
    __builtin_unreachable();
}

/* Original 9012..901A */
REGION void tsl9_main_family_block_9012(void)
{
    REGS;
    __asm__ volatile("lw ra, 12(sp)":::"memory"); LIVE;
    a0 = UINT32_C(0); LIVE;
    __asm__ volatile("addi sp, sp, 16":::"memory"); LIVE;
    __asm__ volatile("ret":::"memory"); LIVE;
    __builtin_unreachable();
}

/* Original 9250..9258 */
REGION void tsl9_main_family_entry_9250(void)
{
    REGS;
    __asm__ volatile("addi sp, sp, -16":::"memory"); LIVE;
    __asm__ volatile("sw ra, 12(sp)":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_9254:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9254\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_18834\n");
    __builtin_unreachable();
}

/* Original 9258..925C */
REGION void tsl9_main_family_block_9258(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9258:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9258\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_9a42\n");
    __builtin_unreachable();
}

/* Original 925C..9260 */
REGION void tsl9_main_family_block_925c(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_925c:\n.option push\n.option norvc\njal ra,.Ltimer_edge_925c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_1973c\n");
    __builtin_unreachable();
}

/* Original 9260..9264 */
REGION void tsl9_main_family_block_9260(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9260:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9260\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_init_writes_9f4c\n");
    __builtin_unreachable();
}

/* Original 9264..9268 */
REGION void tsl9_main_family_block_9264(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9264:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9264\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_131c2\n");
    __builtin_unreachable();
}

/* Original 9268..926A */
REGION void tsl9_main_family_block_9268(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9268:\nc.jal .Ltimer_edge_9268\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_provider_8e88\n");
    __builtin_unreachable();
}

/* Original 926A..926E */
REGION void tsl9_main_family_block_926a(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_926a:\n.option push\n.option norvc\njal ra,.Ltimer_edge_926a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_9b4e\n");
    __builtin_unreachable();
}

/* Original 926E..9270 */
REGION void tsl9_main_family_block_926e(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_926e:\nc.jal .Ltimer_edge_926e\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_provider_9958\n");
    __builtin_unreachable();
}

/* Original 9270..9274 */
REGION void tsl9_main_family_block_9270(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9270:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9270\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_9f12\n");
    __builtin_unreachable();
}

/* Original 9274..9278 */
REGION void tsl9_main_family_block_9274(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9274:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9274\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_12d92\n");
    __builtin_unreachable();
}

/* Original 9278..927C */
REGION void tsl9_main_family_block_9278(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9278:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9278\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_14c8a\n");
    __builtin_unreachable();
}

/* Original 927C..9280 */
REGION void tsl9_main_family_block_927c(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_927c:\n.option push\n.option norvc\njal ra,.Ltimer_edge_927c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_154a6\n");
    __builtin_unreachable();
}

/* Original 9280..9284 */
REGION void tsl9_main_family_block_9280(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9280:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9280\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_17040\n");
    __builtin_unreachable();
}

/* Original 9284..9288 */
REGION void tsl9_main_family_block_9284(void)
{
    REGS;
    CALL_PORT(".Ltimer_edge_9284:\n.option push\n.option norvc\njal ra,.Ltimer_edge_9284\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_173a2\n");
    __builtin_unreachable();
}

/* Original 9288..9290 */
REGION void tsl9_main_family_block_9288(void)
{
    REGS;
    __asm__ volatile("lw ra, 12(sp)":::"memory"); LIVE;
    __asm__ volatile("addi sp, sp, 16":::"memory"); LIVE;
    CALL_PORT(".Ltimer_edge_928c:\n.option push\n.option norvc\njal zero,.Ltimer_edge_928c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_provider_17bf6\n");
    __builtin_unreachable();
}
