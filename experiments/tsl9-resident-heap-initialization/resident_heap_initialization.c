#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; no host ROM or radio model.
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

/* Two public-SDK initializer/accounting helpers:148B/49i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x430E0..0x430F2. */
REGION void tsl9_candidate_heap_free_sum_430e0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000194)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000018c)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x430F2..0x430F6. */
REGION void tsl9_resident_heap_initialization_block_430f2(void)
{
    REGS;
    PORT(".Lresident_heap_initialization_edge_430f2:\n.option push\n.option norvc\nbne a4,a5,.Lresident_heap_initialization_edge_430f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_initialization_block_430f8\n");
    __builtin_unreachable();
}

/* Original0x430F6..0x430F8. */
REGION void tsl9_resident_heap_initialization_block_430f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x430F8..0x430FC. */
REGION void tsl9_resident_heap_initialization_block_430f8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a3, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23f6\n.option pop\n");
    PORT(".Lresident_heap_initialization_edge_430fa:\n.option push\n.option rvc\nc.bnez a3,.Lresident_heap_initialization_edge_430fa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_initialization_block_43100\n");
    __builtin_unreachable();
}

/* Original0x430FC..0x43100. */
REGION void tsl9_resident_heap_initialization_block_430fc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a3, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23d6\n.option pop\n");
    a0 = a0 + a3; LIVE;
    __builtin_unreachable();
}

/* Original0x43100..0x43104. */
REGION void tsl9_resident_heap_initialization_block_43100(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_heap_initialization_edge_43102:\n.option push\n.option rvc\nc.j .Lresident_heap_initialization_edge_43102\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_initialization_block_430f2\n");
    __builtin_unreachable();
}

/* Original0x43104..0x4313C. */
REGION void tsl9_candidate_heap_initialize_43104(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001ec)); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000001ec); LIVE;
    a2 = a1 + UINT32_C(0x00000220); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000194)) = (uint32_t)a2; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23da\n.option pop\n");
    a5 = a1 + UINT32_C(0xfffffff8); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a0 = UINT32_C(0x00001000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000018c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000007); LIVE;
    a3 = a4 >> UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_heap_initialization_edge_43138:\n.option push\n.option norvc\nbleu a4,a0,.Lresident_heap_initialization_edge_43138\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_initialization_block_43140\n");
    __builtin_unreachable();
}

/* Original0x4313C..0x43140. */
REGION void tsl9_resident_heap_initialization_block_4313c(void)
{
    REGS;
    a3 = UINT32_C(0x00000200); LIVE;
    __builtin_unreachable();
}

/* Original0x43140..0x43166. */
REGION void tsl9_resident_heap_initialization_block_43140(void)
{
    REGS;
    a4 = a2 + a3; LIVE;
    a0 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000190)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000220)) = (uint32_t)a4; LIVE;
    a3 = a3 + UINT32_C(0xfffffff8); LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa256\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0x00000006)) = (uint16_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = a5 - a4; LIVE;
    a5 = a5 + UINT32_C(0xfffffff8); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa35e\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000006)) = (uint16_t)0; LIVE;
    PORT(".Lresident_heap_initialization_edge_43164:\n.option push\n.option rvc\nc.jal .Lresident_heap_initialization_edge_43164\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_heap_free_sum_430e0\n");
    __builtin_unreachable();
}

/* Original0x43166..0x43174. */
REGION void tsl9_resident_heap_initialization_block_43166(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000001a2)) = (uint16_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
