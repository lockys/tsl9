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

/* Two complete public-SDK random/range bodies:144B/52i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x433A8..0x433D2. */
REGION void tsl9_candidate_tmos_rand_433a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000210)); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -312\n.option pop\n");
    PORT(".Lresident_range_random_edge_433d0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_range_random_edge_433d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_range_random_block_433dc\n");
    __builtin_unreachable();
}

/* Original0x433D2..0x433D4. */
REGION void tsl9_resident_range_random_block_433d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x433D4..0x433DC. */
REGION void tsl9_resident_range_random_block_433d4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a0 = a0 + a5; LIVE;
    PORT(".option push\n.option rvc\nsw a0, 0(s0)\n.option pop\n");
    PORT(".Lresident_range_random_edge_433da:\n.option push\n.option rvc\nc.j .Lresident_range_random_edge_433da\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_range_random_block_433e6\n");
    __builtin_unreachable();
}

/* Original0x433DC..0x433E6. */
REGION void tsl9_resident_range_random_block_433dc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".Lresident_range_random_edge_433e4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_range_random_edge_433e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_range_random_block_433d2\n");
    __builtin_unreachable();
}

/* Original0x433E6..0x43414. */
REGION void tsl9_resident_range_random_block_433e6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a4 = UINT32_C(0x00034000); LIVE;
    a4 = a4 + UINT32_C(0x000003fd); LIVE;
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x0026a000); LIVE;
    a4 = a4 + UINT32_C(0xfffffec3); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nsw a5, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 0(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43E6A..0x43E78. */
REGION void tsl9_candidate_external_flash_43e6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_range_random_edge_43e74:\n.option push\n.option norvc\njal ra,.Lresident_range_random_edge_43e74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_rand_433a8\n");
    __builtin_unreachable();
}

/* Original0x43E78..0x43E8E. */
REGION void tsl9_resident_range_random_block_43e78(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsub a1, a1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhsu a0, a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
