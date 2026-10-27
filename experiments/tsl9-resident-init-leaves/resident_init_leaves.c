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

/* Three complete required public-SDK leaves:90B/28i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43E24..0x43E34. */
REGION void tsl9_candidate_external_flash_43e24(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000023e)); LIVE;
    a4 = UINT32_C(0x00000014); LIVE;
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_init_leaves_edge_43e30:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e30\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E34..0x43E3C. */
REGION void tsl9_resident_init_leaves_block_43e34(void)
{
    REGS;
    a4 = UINT32_C(0x0000001e); LIVE;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_init_leaves_edge_43e38:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E3C..0x43E46. */
REGION void tsl9_resident_init_leaves_block_43e3c(void)
{
    REGS;
    a4 = UINT32_C(0x00000032); LIVE;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_init_leaves_edge_43e42:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E46..0x43E50. */
REGION void tsl9_resident_init_leaves_block_43e46(void)
{
    REGS;
    a4 = UINT32_C(0x0000004b); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_init_leaves_edge_43e4c:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e4c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E50..0x43E5A. */
REGION void tsl9_resident_init_leaves_block_43e50(void)
{
    REGS;
    a4 = UINT32_C(0x00000064); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_init_leaves_edge_43e56:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e56\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E5A..0x43E64. */
REGION void tsl9_resident_init_leaves_block_43e5a(void)
{
    REGS;
    a4 = UINT32_C(0x00000096); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_init_leaves_edge_43e60:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_init_leaves_edge_43e60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init_leaves_block_43e68\n");
    __builtin_unreachable();
}

/* Original0x43E64..0x43E68. */
REGION void tsl9_resident_init_leaves_block_43e64(void)
{
    REGS;
    a0 = (uint32_t)(a5 < UINT32_C(0x000000fb)); LIVE;
    __builtin_unreachable();
}

/* Original0x43E68..0x43E6A. */
REGION void tsl9_resident_init_leaves_block_43e68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55BD4..0x55BDE. */
REGION void tsl9_candidate_external_flash_55bd4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e0)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55C48..0x55C52. */
REGION void tsl9_candidate_external_flash_55c48(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e8)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
