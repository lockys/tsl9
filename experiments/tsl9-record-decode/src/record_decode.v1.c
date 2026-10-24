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

/* OriginalC6A8..C776 andFAF8..FAFE only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Frameless decoder andGP284 low-byte status setter remain separate entries.
 * Fresh full-word source reads andbyte-preserving target writes stay exact.
 * Sourceword+4 includes one byte beyond theprior seven-byte copy;do not narrow it.
 * Direct12A08 no-link tail andRA returns remain explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original C6A8..C6B4 */
REGION void tsl9_record_decode_entry_c6a8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a4, gp, 220\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 0u); LIVE;
    a5 = a5 >> 9u; LIVE;
    a5 = a5 & 0x1u; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c6b2:\nc.beqz a5,.Lrecord_decode_edge_c6b2\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_decode_block_c774\n");
    __builtin_unreachable();
}

/* Original C6B4..C6C0 */
REGION void tsl9_record_decode_block_c6b4(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 0u); LIVE;
    a3 = UINT32_C(0); LIVE;
    a5 = a5 >> 10u; LIVE;
    a5 = a5 & 0x3fu; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c6be:\nc.beqz a5,.Lrecord_decode_edge_c6be\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_decode_block_c6e4\n");
    __builtin_unreachable();
}

/* Original C6C0..C6E4 */
REGION void tsl9_record_decode_block_c6c0(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 0u); LIVE;
    a3 = a5 >> 16u; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a5 = a5 & 0xffu; LIVE;
    a5 = a5 << 16u; LIVE;
    a5 = a5 | a3; LIVE;
    a3 = a5 >> 8u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + 4u) = (uint8_t)a5; LIVE;
    a5 = a5 >> 16u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + 5u) = (uint8_t)a3; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + 6u) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(1); LIVE;
    __builtin_unreachable();
}

/* Original C6E4..C6EC */
REGION void tsl9_record_decode_block_c6e4(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a5 = a5 >> 8u; LIVE;
    a5 = a5 & 0x1fu; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c6ea:\nc.beqz a5,.Lrecord_decode_edge_c6ea\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_decode_block_c772\n");
    __builtin_unreachable();
}

/* Original C6EC..C6F8 */
REGION void tsl9_record_decode_block_c6ec(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a3 = UINT32_C(10); LIVE;
    a5 = a5 >> 8u; LIVE;
    a5 = a5 & 0x1fu; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c6f4:\n.option push\n.option norvc\nbltu a3,a5,.Lrecord_decode_edge_c6f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_decode_block_c754\n");
    __builtin_unreachable();
}

/* Original C6F8..C70E */
REGION void tsl9_record_decode_block_c6f8(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a2 = UINT32_C(10); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + 7u); LIVE;
    a3 = a3 >> 8u; LIVE;
    a3 = a3 & 0x1fu; LIVE;
    a3 = a3 * a2; LIVE;
    a5 = a5 & 0x7fu; LIVE;
    a5 = a5 + a3; LIVE;
    __builtin_unreachable();
}

/* Original C70E..C71C */
REGION void tsl9_record_decode_block_c70e(void)
{
    REGS;
    a5 = a5 & 0xffu; LIVE;
    a2 = UINT32_C(100); LIVE;
    CALL_PORT("mv a3, a5");
    CALL_PORT(".Lrecord_decode_edge_c718:\n.option push\n.option norvc\nbleu a5,a2,.Lrecord_decode_edge_c718\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_decode_block_c720\n");
    __builtin_unreachable();
}

/* Original C71C..C720 */
REGION void tsl9_record_decode_block_c71c(void)
{
    REGS;
    a3 = UINT32_C(100); LIVE;
    __builtin_unreachable();
}

/* Original C720..C724 */
REGION void tsl9_record_decode_block_c720(void)
{
    REGS;
    a5 = a3 & 0xffu; LIVE;
    __builtin_unreachable();
}

/* Original C724..C736 */
REGION void tsl9_record_decode_block_c724(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + 7u); LIVE;
    a5 = a5 & 0x7fu; LIVE;
    a3 = a3 & 0xffffff80u; LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + 7u) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original C736..C73C */
REGION void tsl9_record_decode_block_c736(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + 2u); LIVE;
    CALL_PORT(".Lrecord_decode_edge_c73a:\nc.beqz a5,.Lrecord_decode_edge_c73a\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_decode_block_c774\n");
    __builtin_unreachable();
}

/* Original C73C..C754 */
REGION void tsl9_record_decode_block_c73c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a5 = a5 >> 13u; LIVE;
    a4 = a5 & 0x3u; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + 8u); LIVE;
    a5 = a5 & 0xfffffffcu; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + 8u) = (uint8_t)a5; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c750:\n.option push\n.option norvc\njal zero,.Lrecord_decode_edge_c750\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_decode_provider_12a08\n");
    __builtin_unreachable();
}

/* Original C754..C762 */
REGION void tsl9_record_decode_block_c754(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a2 = UINT32_C(20); LIVE;
    a5 = UINT32_C(0); LIVE;
    a3 = a3 >> 8u; LIVE;
    a3 = a3 & 0x1fu; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c75e:\n.option push\n.option norvc\nbltu a2,a3,.Lrecord_decode_edge_c75e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_decode_block_c724\n");
    __builtin_unreachable();
}

/* Original C762..C772 */
REGION void tsl9_record_decode_block_c762(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 4u); LIVE;
    a3 = UINT32_C(10); LIVE;
    a5 = a5 >> 8u; LIVE;
    a5 = a5 & 0x1fu; LIVE;
    a5 = a5 + 0xfffffff6u; LIVE;
    a5 = a5 * a3; LIVE;
    CALL_PORT(".Lrecord_decode_edge_c770:\nc.j .Lrecord_decode_edge_c770\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_decode_block_c70e\n");
    __builtin_unreachable();
}

/* Original C772..C774 */
REGION void tsl9_record_decode_block_c772(void)
{
    REGS;
    CALL_PORT(".Lrecord_decode_edge_c772:\nc.bnez a3,.Lrecord_decode_edge_c772\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_decode_block_c736\n");
    __builtin_unreachable();
}

/* Original C774..C776 */
REGION void tsl9_record_decode_block_c774(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original FAF8..FAFE */
REGION void tsl9_record_decode_entry_faf8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nsb a0, 284(gp)\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}
