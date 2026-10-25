#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 context required; this is not a host or radio model.
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

/* Three complete original bodies. Register-bound C preserves unsigned
 * arithmetic and volatile memory accesses; explicit ports retain original
 * PC-relative RAM addressing, stack/RA/S registers, ROM calls and REMU.
 * These basic blocks require original VMAs and register/ROM contracts.
 * The original 0x10D2E body really is RET; no substitute stub is added.
 * Not integrated into the curated firmware component; no flash claim. */

/* Original 0x10C36..0x10C42. */
REGION void tsl9_central_callback_leaves_10c36(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000003b8)); LIVE;
    PORT(".Lcentral_leaves_edge_10c3e:\n.option push\n.option norvc\nbeq a5,a0,.Lcentral_leaves_edge_10c3e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_callback_leaves_10c72\n");
    __builtin_unreachable();
}

/* Original 0x10C42..0x10C4E. */
REGION void tsl9_central_callback_leaves_10c42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000003b8)); LIVE;
    PORT(".Lcentral_leaves_edge_10c4a:\n.option push\n.option norvc\nbeq a5,a0,.Lcentral_leaves_edge_10c4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_callback_leaves_10c76\n");
    __builtin_unreachable();
}

/* Original 0x10C4E..0x10C5A. */
REGION void tsl9_central_callback_leaves_10c4e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000003b8)); LIVE;
    PORT(".Lcentral_leaves_edge_10c56:\n.option push\n.option norvc\nbne a5,a0,.Lcentral_leaves_edge_10c56\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_callback_leaves_10c70\n");
    __builtin_unreachable();
}

/* Original 0x10C5A..0x10C5C. */
REGION void tsl9_central_callback_leaves_10c5a(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original 0x10C5C..0x10C70. */
REGION void tsl9_central_callback_leaves_10c5c(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = a4 + UINT32_C(0x0000038a); LIVE;
    a5 = a5 + a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)a1; LIVE;
    __builtin_unreachable();
}

/* Original 0x10C70..0x10C72. */
REGION void tsl9_central_callback_leaves_10c70(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original 0x10C72..0x10C76. */
REGION void tsl9_central_callback_leaves_10c72(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcentral_leaves_edge_10c74:\n.option push\n.option rvc\nc.j .Lcentral_leaves_edge_10c74\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_callback_leaves_10c5c\n");
    __builtin_unreachable();
}

/* Original 0x10C76..0x10C7A. */
REGION void tsl9_central_callback_leaves_10c76(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcentral_leaves_edge_10c78:\n.option push\n.option rvc\nc.j .Lcentral_leaves_edge_10c78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_callback_leaves_10c5c\n");
    __builtin_unreachable();
}

/* Original 0x10D2E..0x10D30. */
REGION void tsl9_central_callback_leaves_10d2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original 0x10D30..0x10D42. */
REGION void tsl9_central_callback_leaves_10d30(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 56(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original 0x10D42..0x10D60. */
REGION void tsl9_central_callback_leaves_10d42(void)
{
    REGS;
    a2 = UINT32_C(0x000f4000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nremu a2, a0, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 368(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}
