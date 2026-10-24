#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; not a host memcpy implementation.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Complete original19BF0..19CA6 forward transfer,182B/54 instructions.
 * C arithmetic/volatile access plus explicit register and control ports.
 * Original unsigned address tests,byte/word paths and36B bulk order are retained.
 * The bulk path loads8 words,stores1,loads the ninth,then completes the stores.
 * T0/T1/T2/T3/T4/T5/T6/A6/A7 remain original scratch register ports;
 * the pinned profile reserves them from C allocation. A0 is unchanged.
 * These15 regions require original adjacency; they are not normal C ABI functions.
 * No overlap,bounds,trap/IRQ,physical MCU/ROM/RAM or OTA compatibility claim. */

/* Original 19BF0..19BFC */
REGION void tsl9_callback_flow_external_19bf0(void)
{
    REGS;
    a5 = a1 ^ a0; LIVE;
    a5 = a5 & 0x3u; LIVE;
    a4 = a0 + a2; LIVE;
    PORT(".Lmemory_transfer_edge_19bfa:\n.option push\n.option rvc\nc.bnez a5,.Lmemory_transfer_edge_19bfa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_memory_transfer_block_19c02\n");
    __builtin_unreachable();
}

/* Original 19BFC..19C02 */
REGION void tsl9_memory_transfer_block_19bfc(void)
{
    REGS;
    a5 = UINT32_C(3); LIVE;
    PORT(".Lmemory_transfer_edge_19bfe:\n.option push\n.option norvc\nbltu a5,a2,.Lmemory_transfer_edge_19bfe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19c1a\n");
    __builtin_unreachable();
}

/* Original 19C02..19C08 */
REGION void tsl9_memory_transfer_block_19c02(void)
{
    REGS;
    a5 = a0; LIVE;
    PORT(".Lmemory_transfer_edge_19c04:\n.option push\n.option norvc\nbleu a4,a0,.Lmemory_transfer_edge_19c04\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19ca4\n");
    __builtin_unreachable();
}

/* Original 19C08..19C18 */
REGION void tsl9_memory_transfer_block_19c08(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a1 + 0u); LIVE;
    a5 = a5 + 0x1u; LIVE;
    a1 = a1 + 0x1u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 - 1u) = (uint8_t)a3; LIVE;
    PORT(".Lmemory_transfer_edge_19c14:\n.option push\n.option norvc\nbltu a5,a4,.Lmemory_transfer_edge_19c14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19c08\n");
    __builtin_unreachable();
}

/* Original 19C18..19C1A */
REGION void tsl9_memory_transfer_block_19c18(void)
{
    REGS;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19C1A..19C20 */
REGION void tsl9_memory_transfer_block_19c1a(void)
{
    REGS;
    a3 = a0 & 0x3u; LIVE;
    a5 = a0; LIVE;
    __builtin_unreachable();
}

/* Original 19C20..19C22 */
REGION void tsl9_memory_transfer_block_19c20(void)
{
    REGS;
    PORT(".Lmemory_transfer_edge_19c20:\n.option push\n.option rvc\nc.beqz a3,.Lmemory_transfer_edge_19c20\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_memory_transfer_block_19c34\n");
    __builtin_unreachable();
}

/* Original 19C22..19C34 */
REGION void tsl9_memory_transfer_block_19c22(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a1 + 0u); LIVE;
    a5 = a5 + 0x1u; LIVE;
    a1 = a1 + 0x1u; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 - 1u) = (uint8_t)a3; LIVE;
    a3 = a5 & 0x3u; LIVE;
    PORT(".Lmemory_transfer_edge_19c32:\n.option push\n.option rvc\nc.j .Lmemory_transfer_edge_19c32\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_memory_transfer_block_19c20\n");
    __builtin_unreachable();
}

/* Original 19C34..19C3C */
REGION void tsl9_memory_transfer_block_19c34(void)
{
    REGS;
    a3 = a4 & 0xfffffffcu; LIVE;
    a2 = a3 + 0xffffffe0u; LIVE;
    __builtin_unreachable();
}

/* Original 19C3C..19C40 */
REGION void tsl9_memory_transfer_block_19c3c(void)
{
    REGS;
    PORT(".Lmemory_transfer_edge_19c3c:\n.option push\n.option norvc\nbleu a2,a5,.Lmemory_transfer_edge_19c3c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19c9c\n");
    __builtin_unreachable();
}

/* Original 19C40..19C92 */
REGION void tsl9_memory_transfer_block_19c40(void)
{
    REGS;
    /* Preserve the original9-word batch register bank and interleaved memory order. */
    PORT(".option push\n.option norvc\nlw t2, 0(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t0, 4(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t6, 8(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t5, 12(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t4, 16(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t3, 20(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 24(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a7, 28(a1)\n.option pop\n");
    a1 = a1 + 0x24u; LIVE;
    PORT(".option push\n.option norvc\nsw t2, 0(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a6, -4(a1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t0, 4(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t6, 8(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t5, 12(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t4, 16(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t3, 20(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t1, 24(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a7, 28(a5)\n.option pop\n");
    a5 = a5 + 0x24u; LIVE;
    PORT(".option push\n.option norvc\nsw a6, -4(a5)\n.option pop\n");
    PORT(".Lmemory_transfer_edge_19c90:\n.option push\n.option rvc\nc.j .Lmemory_transfer_edge_19c90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_memory_transfer_block_19c3c\n");
    __builtin_unreachable();
}

/* Original 19C92..19C9C */
REGION void tsl9_memory_transfer_block_19c92(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a1 + 0u); LIVE;
    a5 = a5 + 0x4u; LIVE;
    a1 = a1 + 0x4u; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 4u) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original 19C9C..19CA0 */
REGION void tsl9_memory_transfer_block_19c9c(void)
{
    REGS;
    PORT(".Lmemory_transfer_edge_19c9c:\n.option push\n.option norvc\nbltu a5,a3,.Lmemory_transfer_edge_19c9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19c92\n");
    __builtin_unreachable();
}

/* Original 19CA0..19CA4 */
REGION void tsl9_memory_transfer_block_19ca0(void)
{
    REGS;
    PORT(".Lmemory_transfer_edge_19ca0:\n.option push\n.option norvc\nbltu a5,a4,.Lmemory_transfer_edge_19ca0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_memory_transfer_block_19c08\n");
    __builtin_unreachable();
}

/* Original 19CA4..19CA6 */
REGION void tsl9_memory_transfer_block_19ca4(void)
{
    REGS;
    PORT("ret");
    __builtin_unreachable();
}
