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

/* Five complete conditional status gates:246B/86i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x56086..0x5609A. */
REGION void tsl9_candidate_unprovided_flash_56086(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000114)); LIVE;
    a2 = UINT32_C(0x00000003); LIVE;
    a3 = UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 13(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb558\n.option pop\n");
    PORT(".Lresident_completion_status_gates_edge_56096:\n.option push\n.option norvc\nbne a4,a2,.Lresident_completion_status_gates_edge_56096\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_completion_status_gates_block_5609c\n");
    __builtin_unreachable();
}

/* Original0x5609A..0x5609C. */
REGION void tsl9_resident_completion_status_gates_block_5609a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5609C..0x560AA. */
REGION void tsl9_resident_completion_status_gates_block_5609c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a3, 23(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb974\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 18(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa938\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 22(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa97c\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560B2..0x560C6. */
REGION void tsl9_candidate_unprovided_flash_560b2(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000114)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2558\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a3, a4, 0x3\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x2\n.option pop\n");
    a5 = a5 ^ a3; LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_status_gates_edge_560c4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_status_gates_edge_560c4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_560d0\n");
    __builtin_unreachable();
}

/* Original0x560C6..0x560D0. */
REGION void tsl9_resident_completion_status_gates_block_560c6(void)
{
    REGS;
    a4 = a4 ^ UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa558\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560D0..0x560D4. */
REGION void tsl9_resident_completion_status_gates_block_560d0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560D4..0x560E8. */
REGION void tsl9_candidate_unprovided_flash_560d4(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000114)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2558\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a3, a4, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x3\n.option pop\n");
    a5 = a5 ^ a3; LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_completion_status_gates_edge_560e6:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_status_gates_edge_560e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_560f2\n");
    __builtin_unreachable();
}

/* Original0x560E8..0x560F2. */
REGION void tsl9_resident_completion_status_gates_block_560e8(void)
{
    REGS;
    a4 = a4 ^ UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa558\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560F2..0x560F6. */
REGION void tsl9_resident_completion_status_gates_block_560f2(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560F6..0x56102. */
REGION void tsl9_candidate_unprovided_flash_560f6(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e4)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_completion_status_gates_edge_56100:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_status_gates_edge_56100\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_5610c\n");
    __builtin_unreachable();
}

/* Original0x56102..0x5610C. */
REGION void tsl9_resident_completion_status_gates_block_56102(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e8)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e8)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5610C..0x56116. */
REGION void tsl9_resident_completion_status_gates_block_5610c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e8)); LIVE;
    a5 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_status_gates_edge_56114:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_status_gates_edge_56114\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_56120\n");
    __builtin_unreachable();
}

/* Original0x56116..0x56120. */
REGION void tsl9_resident_completion_status_gates_block_56116(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e4)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000e8)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x56120..0x5612A. */
REGION void tsl9_resident_completion_status_gates_block_56120(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_completion_status_gates_edge_56128:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_status_gates_edge_56128\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_56144\n");
    __builtin_unreachable();
}

/* Original0x5612A..0x56144. */
REGION void tsl9_resident_completion_status_gates_block_5612a(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000048)); LIVE;
    a5 = a5 + a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000046)) = (uint16_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)); LIVE;
    a5 = a5 & UINT32_C(0xfffffbff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x56144..0x56146. */
REGION void tsl9_resident_completion_status_gates_block_56144(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56146..0x56152. */
REGION void tsl9_candidate_unprovided_flash_56146(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000ec)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000ec)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_completion_status_gates_edge_56150:\n.option push\n.option rvc\nc.bnez a5,.Lresident_completion_status_gates_edge_56150\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_5615c\n");
    __builtin_unreachable();
}

/* Original0x56152..0x5615C. */
REGION void tsl9_resident_completion_status_gates_block_56152(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000f0)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000f0)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5615C..0x56166. */
REGION void tsl9_resident_completion_status_gates_block_5615c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000f0)); LIVE;
    a5 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_completion_status_gates_edge_56164:\n.option push\n.option rvc\nc.beqz a5,.Lresident_completion_status_gates_edge_56164\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_56170\n");
    __builtin_unreachable();
}

/* Original0x56166..0x56170. */
REGION void tsl9_resident_completion_status_gates_block_56166(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000ec)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000f0)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x56170..0x5617A. */
REGION void tsl9_resident_completion_status_gates_block_56170(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_completion_status_gates_edge_56178:\n.option push\n.option rvc\nc.beqz a4,.Lresident_completion_status_gates_edge_56178\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_completion_status_gates_block_56182\n");
    __builtin_unreachable();
}

/* Original0x5617A..0x56182. */
REGION void tsl9_resident_completion_status_gates_block_5617a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x56182..0x56184. */
REGION void tsl9_resident_completion_status_gates_block_56182(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
