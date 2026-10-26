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

/* Two public-SDK bodies:164B/62i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x431BA..0x431D4. */
REGION void tsl9_candidate_message_deallocate_431ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40024\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 524(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_message_api_edge_431d2:\n.option push\n.option rvc\nc.bnez a0,.Lresident_message_api_edge_431d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_api_block_431e4\n");
    __builtin_unreachable();
}

/* Original0x431D4..0x431DA. */
REGION void tsl9_resident_message_api_block_431d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 524(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0x431DA..0x431E4. */
REGION void tsl9_resident_message_api_block_431da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x431E4..0x431F0. */
REGION void tsl9_resident_message_api_block_431e4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffffe)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_message_api_edge_431ec:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_message_api_edge_431ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_api_block_431f8\n");
    __builtin_unreachable();
}

/* Original0x431F0..0x431F8. */
REGION void tsl9_resident_message_api_block_431f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 524(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_message_api_edge_431f6:\n.option push\n.option rvc\nc.j .Lresident_message_api_edge_431f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_api_block_431da\n");
    __builtin_unreachable();
}

/* Original0x431F8..0x43200. */
REGION void tsl9_resident_message_api_block_431f8(void)
{
    REGS;
    PORT(".Lresident_message_api_literal_431f8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_message_api_literal_431f8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43200..0x43208. */
REGION void tsl9_resident_message_api_block_43200(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(s0)\n.option pop\n");
    PORT(".Lresident_message_api_edge_43206:\n.option push\n.option rvc\nc.j .Lresident_message_api_edge_43206\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_api_block_431da\n");
    __builtin_unreachable();
}

/* Original0x20000236..0x20000252. */
REGION void tsl9_candidate_message_allocate_20000236(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40024\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_message_api_edge_20000250:\n.option push\n.option rvc\nc.bnez a0,.Lresident_message_api_edge_20000250\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_api_block_20000262\n");
    __builtin_unreachable();
}

/* Original0x20000252..0x20000256. */
REGION void tsl9_resident_message_api_block_20000252(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000256..0x20000262. */
REGION void tsl9_resident_message_api_block_20000256(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000262..0x20000270. */
REGION void tsl9_resident_message_api_block_20000262(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    a1 = UINT32_C(0x0000f000); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nor a1, a1, s0\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_message_api_edge_2000026e:\n.option push\n.option rvc\nc.jal .Lresident_message_api_edge_2000026e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_heap_allocate_20000040\n");
    __builtin_unreachable();
}

/* Original0x20000270..0x20000272. */
REGION void tsl9_resident_message_api_block_20000270(void)
{
    REGS;
    PORT(".Lresident_message_api_edge_20000270:\n.option push\n.option rvc\nc.beqz a0,.Lresident_message_api_edge_20000270\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_api_block_20000284\n");
    __builtin_unreachable();
}

/* Original0x20000272..0x20000284. */
REGION void tsl9_resident_message_api_block_20000272(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sh s0, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa142\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17c\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_message_api_edge_20000282:\n.option push\n.option rvc\nc.j .Lresident_message_api_edge_20000282\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_api_block_20000256\n");
    __builtin_unreachable();
}

/* Original0x20000284..0x2000028C. */
REGION void tsl9_resident_message_api_block_20000284(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_message_api_edge_2000028a:\n.option push\n.option rvc\nc.j .Lresident_message_api_edge_2000028a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_api_block_20000256\n");
    __builtin_unreachable();
}
