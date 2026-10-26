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

/* Five complete conditional SDK startup stages:234B/67i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x40000..0x40004. */
REGION void tsl9_candidate_resident_header_40000(void)
{
    REGS;
    PORT(".Lresident_slot2_startup_edge_40000:\n.option push\n.option norvc\njal zero,.Lresident_slot2_startup_edge_40000\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_startup_entry_6de7e\n");
    __builtin_unreachable();
}

/* Original0x6DE0C..0x6DE52. */
REGION void tsl9_candidate_startup_loader_6de0c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a4 = UINT32_C(0x20000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x20000000); LIVE;
    a4 = a4 + UINT32_C(0x000007d0); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20002000); LIVE;
    a4 = a4 + UINT32_C(0x0000051c); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0xfffffe34); LIVE;
    a2 = UINT32_C(0x20003000); LIVE;
    a1 = UINT32_C(0x20000000); LIVE;
    a0 = UINT32_C(0x00040000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a2 = a2 + UINT32_C(0xfffffe70); LIVE;
    a1 = a1 + UINT32_C(0x00000040); LIVE;
    a0 = a0 + UINT32_C(0x000002b0); LIVE;
    PORT(".Lresident_slot2_startup_literal_6de4a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_seed_word_copy_20000010\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot2_startup_literal_6de4a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DE52..0x6DE72. */
REGION void tsl9_resident_slot2_startup_block_6de52(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a1 = UINT32_C(0x20003000); LIVE;
    a0 = UINT32_C(0x0006f000); LIVE;
    a2 = a2 + UINT32_C(0xfffffef8); LIVE;
    a1 = a1 + UINT32_C(0xfffffe70); LIVE;
    a0 = a0 + UINT32_C(0xfffffaa4); LIVE;
    PORT(".Lresident_slot2_startup_literal_6de6a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_seed_word_copy_20000010\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot2_startup_literal_6de6a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DE72..0x6DE7E. */
REGION void tsl9_resident_slot2_startup_block_6de72(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_slot2_startup_literal_6de76:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_seed_zero_20000022\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot2_startup_literal_6de76\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DE7E..0x6DEAA. */
REGION void tsl9_candidate_startup_entry_6de7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc gp, 0x1ff96\n.option pop\n");
    PORT(".option push\n.option norvc\naddi gp, gp, 386\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc sp, 0x1ffa2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi sp, sp, 378\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0xfffd2\n.option pop\n");
    a0 = a0 + UINT32_C(0x000003f2); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1ff92\n.option pop\n");
    a1 = a1 + UINT32_C(0x0000017a); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x1ff92\n.option pop\n");
    a2 = a2 + UINT32_C(0x000001a2); LIVE;
    PORT(".Lresident_slot2_startup_edge_6dea6:\n.option push\n.option norvc\nbleu a2,a1,.Lresident_slot2_startup_edge_6dea6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot2_startup_block_6debe\n");
    __builtin_unreachable();
}

/* Original0x6DEAA..0x6DEBA. */
REGION void tsl9_resident_slot2_startup_block_6deaa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw t0, 0(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw t0, 0(a1)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000004); LIVE;
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_slot2_startup_edge_6deb6:\n.option push\n.option norvc\nbltu a1,a2,.Lresident_slot2_startup_edge_6deb6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot2_startup_block_6deaa\n");
    __builtin_unreachable();
}

/* Original0x6DEBA..0x6DEBE. */
REGION void tsl9_resident_slot2_startup_block_6deba(void)
{
    REGS;
    PORT(".Lresident_slot2_startup_edge_6deba:\n.option push\n.option norvc\njal ra,.Lresident_slot2_startup_edge_6deba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_startup_loader_6de0c\n");
    __builtin_unreachable();
}

/* Original0x6DEBE..0x6DEC2. */
REGION void tsl9_resident_slot2_startup_block_6debe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000010..0x20000014. */
REGION void tsl9_candidate_seed_word_copy_20000010(void)
{
    REGS;
    PORT(".Lresident_slot2_startup_edge_20000010:\n.option push\n.option norvc\nbleu a1,a2,.Lresident_slot2_startup_edge_20000010\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot2_startup_block_20000016\n");
    __builtin_unreachable();
}

/* Original0x20000014..0x20000016. */
REGION void tsl9_resident_slot2_startup_block_20000014(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000016..0x20000022. */
REGION void tsl9_resident_slot2_startup_block_20000016(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    a0 = a0 + UINT32_C(0x00000004); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0xfffffffc)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_slot2_startup_edge_20000020:\n.option push\n.option rvc\nc.j .Lresident_slot2_startup_edge_20000020\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_seed_word_copy_20000010\n");
    __builtin_unreachable();
}

/* Original0x20000022..0x20000032. */
REGION void tsl9_candidate_seed_zero_20000022(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xfffffef8); LIVE;
    a4 = a4 + UINT32_C(0x00000614); LIVE;
    __builtin_unreachable();
}

/* Original0x20000032..0x20000036. */
REGION void tsl9_resident_slot2_startup_block_20000032(void)
{
    REGS;
    PORT(".Lresident_slot2_startup_edge_20000032:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_slot2_startup_edge_20000032\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot2_startup_block_20000038\n");
    __builtin_unreachable();
}

/* Original0x20000036..0x20000038. */
REGION void tsl9_resident_slot2_startup_block_20000036(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000038..0x20000040. */
REGION void tsl9_resident_slot2_startup_block_20000038(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    a5 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_slot2_startup_edge_2000003e:\n.option push\n.option rvc\nc.j .Lresident_slot2_startup_edge_2000003e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot2_startup_block_20000032\n");
    __builtin_unreachable();
}
