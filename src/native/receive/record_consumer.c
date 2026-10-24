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

/* OriginalC776..C7E8 only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Copy16B frame/clear tail/conditional callback32B frame remain separate entries.
 * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original C776..C78A */
REGION void tsl9_record_consumer_entry_c776(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 76u); LIVE;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT("mv a1, a0");
    a2 = UINT32_C(7); LIVE;
    CALL_PORT(".option push\n.option norvc\naddi a0, gp, 220\n.option pop\n");
    CALL_PORT("c.jalr a5");
    __builtin_unreachable();
}

/* Original C78A..C798 */
REGION void tsl9_record_consumer_block_c78a(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = a0 + 0xfffffb04u; LIVE;
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT(".Lrecord_control_edge_c796:\nc.j .Lrecord_control_edge_c796\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_consumer_provider_c6a8\n");
    __builtin_unreachable();
}

/* Original C798..C7AA */
REGION void tsl9_record_consumer_entry_c798(void)
{
    REGS;
    a5 = UINT32_C(0x40000); LIVE;
    CALL_PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(7); LIVE;
    a1 = UINT32_C(0); LIVE;
    CALL_PORT(".option push\n.option norvc\naddi a0, gp, 220\n.option pop\n");
    CALL_PORT("jr t1");
    __builtin_unreachable();
}

/* Original C7AA..C7B4 */
REGION void tsl9_record_consumer_entry_c7aa(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + 1916u) = (uint8_t)a0; LIVE;
    CALL_PORT(".Lrecord_control_edge_c7b2:\nc.bnez a0,.Lrecord_control_edge_c7b2\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_consumer_block_c7e6\n");
    __builtin_unreachable();
}

/* Original C7B4..C7BC */
REGION void tsl9_record_consumer_block_c7b4(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -32");
    CALL_PORT("sw ra, 28(sp)");
    CALL_PORT(".Lrecord_control_edge_c7b8:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_c7b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_consumer_provider_faf8\n");
    __builtin_unreachable();
}

/* Original C7BC..C7CA */
REGION void tsl9_record_consumer_block_c7bc(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a5, gp, 84\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 0u); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 1u); LIVE;
    a5 = a5 & 0x4u; LIVE;
    CALL_PORT(".Lrecord_control_edge_c7c8:\nc.beqz a5,.Lrecord_control_edge_c7c8\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_consumer_block_c7e0\n");
    __builtin_unreachable();
}

/* Original C7CA..C7D4 */
REGION void tsl9_record_consumer_block_c7ca(void)
{
    REGS;
    CALL_PORT("addi a2, sp, 4");
    a1 = UINT32_C(8); LIVE;
    a0 = UINT32_C(1); LIVE;
    CALL_PORT(".Lrecord_control_edge_c7d0:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_c7d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_consumer_provider_82a8\n");
    __builtin_unreachable();
}

/* Original C7D4..C7DA */
REGION void tsl9_record_consumer_block_c7d4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a5, 6(sp)\n.option pop\n");
    CALL_PORT(".Lrecord_control_edge_c7d8:\nc.beqz a5,.Lrecord_control_edge_c7d8\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_consumer_block_c7e0\n");
    __builtin_unreachable();
}

/* Original C7DA..C7E0 */
REGION void tsl9_record_consumer_block_c7da(void)
{
    REGS;
    CALL_PORT("addi a0, sp, 4");
    CALL_PORT(".Lrecord_control_edge_c7dc:\n.option push\n.option norvc\njal ra,.Lrecord_control_edge_c7dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_consumer_provider_12a08\n");
    __builtin_unreachable();
}

/* Original C7E0..C7E6 */
REGION void tsl9_record_consumer_block_c7e0(void)
{
    REGS;
    CALL_PORT("lw ra, 28(sp)");
    CALL_PORT("addi sp, sp, 32");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original C7E6..C7E8 */
REGION void tsl9_record_consumer_block_c7e6(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}
