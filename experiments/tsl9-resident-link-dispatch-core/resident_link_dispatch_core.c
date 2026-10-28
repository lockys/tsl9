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

/* Fourteen complete conditional SDK link-dispatch bodies:1260B/495i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4D4BC..0x4D4BE. */
REGION void tsl9_candidate_link_dispatch_4d4bc(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d4bc:\n.option push\n.option rvc\nc.beqz a3,.Lresident_link_dispatch_core_edge_4d4bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d59a\n");
    __builtin_unreachable();
}

/* Original0x4D4BE..0x4D4DC. */
REGION void tsl9_resident_link_dispatch_core_block_4d4be(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a1\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d4d8:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4d4d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4f072\n");
    __builtin_unreachable();
}

/* Original0x4D4DC..0x4D4E0. */
REGION void tsl9_resident_link_dispatch_core_block_4d4dc(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d4de:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4d4de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d50c\n");
    __builtin_unreachable();
}

/* Original0x4D4E0..0x4D4F4. */
REGION void tsl9_resident_link_dispatch_core_block_4d4e0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa0)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xffffffa1)); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d4f2:\n.option push\n.option rvc\nc.bnez s0,.Lresident_link_dispatch_core_edge_4d4f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d4f8\n");
    __builtin_unreachable();
}

/* Original0x4D4F4..0x4D4F8. */
REGION void tsl9_resident_link_dispatch_core_block_4d4f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D4F8..0x4D506. */
REGION void tsl9_resident_link_dispatch_core_block_4d4f8(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xffffff98)); LIVE;
    PORT(".option push\n.option norvc\nslli a5, s1, 0x4\n.option pop\n");
    a5 = a5 + a4; LIVE;
    __builtin_unreachable();
}

/* Original0x4D506..0x4D50A. */
REGION void tsl9_resident_link_dispatch_core_block_4d506(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d506:\n.option push\n.option norvc\nbltu s1,a3,.Lresident_link_dispatch_core_edge_4d506\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4d520\n");
    __builtin_unreachable();
}

/* Original0x4D50A..0x4D50C. */
REGION void tsl9_resident_link_dispatch_core_block_4d50a(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    __builtin_unreachable();
}

/* Original0x4D50C..0x4D520. */
REGION void tsl9_resident_link_dispatch_core_block_4d50c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D520..0x4D52A. */
REGION void tsl9_resident_link_dispatch_core_block_4d520(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a5\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffff2)); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d528:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_dispatch_core_edge_4d528\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d532\n");
    __builtin_unreachable();
}

/* Original0x4D52A..0x4D532. */
REGION void tsl9_resident_link_dispatch_core_block_4d52a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d530:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4d530\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4d506\n");
    __builtin_unreachable();
}

/* Original0x4D532..0x4D534. */
REGION void tsl9_resident_link_dispatch_core_block_4d532(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d532:\n.option push\n.option rvc\nc.beqz s0,.Lresident_link_dispatch_core_edge_4d532\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d58e\n");
    __builtin_unreachable();
}

/* Original0x4D534..0x4D546. */
REGION void tsl9_resident_link_dispatch_core_block_4d534(void)
{
    REGS;
    a1 = UINT32_C(0x00005000); LIVE;
    a1 = a1 + UINT32_C(0xfffffc02); LIVE;
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_link_dispatch_core_literal_4d53e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4d53e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D546..0x4D54C. */
REGION void tsl9_resident_link_dispatch_core_block_4d546(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 12(s2)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d54a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4d54a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d50a\n");
    __builtin_unreachable();
}

/* Original0x4D54C..0x4D55E. */
REGION void tsl9_resident_link_dispatch_core_block_4d54c(void)
{
    REGS;
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 64\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4d556:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4d556\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D55E..0x4D562. */
REGION void tsl9_resident_link_dispatch_core_block_4d55e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh s1, 2(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D562..0x4D56C. */
REGION void tsl9_resident_link_dispatch_core_block_4d562(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s5, 6(s2)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d56a:\n.option push\n.option rvc\nc.beqz s0,.Lresident_link_dispatch_core_edge_4d56a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d594\n");
    __builtin_unreachable();
}

/* Original0x4D56C..0x4D586. */
REGION void tsl9_resident_link_dispatch_core_block_4d56c(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000310)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 8(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsub s0, s0, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 12(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai s0, s0, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x4\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s0, 28(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xafc0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D586..0x4D58E. */
REGION void tsl9_resident_link_dispatch_core_block_4d586(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s2, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d58c:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4d58c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4d50c\n");
    __builtin_unreachable();
}

/* Original0x4D58E..0x4D594. */
REGION void tsl9_resident_link_dispatch_core_block_4d58e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 12(s2)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d592:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4d592\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4d562\n");
    __builtin_unreachable();
}

/* Original0x4D594..0x4D59A. */
REGION void tsl9_resident_link_dispatch_core_block_4d594(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s4, 8(s2)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d598:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4d598\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4d586\n");
    __builtin_unreachable();
}

/* Original0x4D59A..0x4D5A0. */
REGION void tsl9_resident_link_dispatch_core_block_4d59a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D5A0..0x4D5B2. */
REGION void tsl9_candidate_link_dispatch_4d5a0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa0)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xffffff98)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4D5B2..0x4D5B6. */
REGION void tsl9_resident_link_dispatch_core_block_4d5b2(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d5b2:\n.option push\n.option norvc\nbne a1,a5,.Lresident_link_dispatch_core_edge_4d5b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4d5bc\n");
    __builtin_unreachable();
}

/* Original0x4D5B6..0x4D5B8. */
REGION void tsl9_resident_link_dispatch_core_block_4d5b6(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4D5B8..0x4D5BC. */
REGION void tsl9_resident_link_dispatch_core_block_4d5b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D5BC..0x4D5C2. */
REGION void tsl9_resident_link_dispatch_core_block_4d5bc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2332\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d5c0:\n.option push\n.option rvc\nc.beqz a2,.Lresident_link_dispatch_core_edge_4d5c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d5c6\n");
    __builtin_unreachable();
}

/* Original0x4D5C2..0x4D5C6. */
REGION void tsl9_resident_link_dispatch_core_block_4d5c2(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d5c2:\n.option push\n.option norvc\nbeq a2,a0,.Lresident_link_dispatch_core_edge_4d5c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4d5b8\n");
    __builtin_unreachable();
}

/* Original0x4D5C6..0x4D5D0. */
REGION void tsl9_resident_link_dispatch_core_block_4d5c6(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 + UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d5ce:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4d5ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4d5b2\n");
    __builtin_unreachable();
}

/* Original0x4D6E0..0x4D6E2. */
REGION void tsl9_candidate_link_dispatch_4d6e0(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4d6e0:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4d6e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d708\n");
    __builtin_unreachable();
}

/* Original0x4D6E2..0x4D6EE. */
REGION void tsl9_resident_link_dispatch_core_block_4d6e2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x213a\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d6ec:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_dispatch_core_edge_4d6ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4d700\n");
    __builtin_unreachable();
}

/* Original0x4D6EE..0x4D6F4. */
REGION void tsl9_resident_link_dispatch_core_block_4d6ee(void)
{
    REGS;
    a1 = UINT32_C(0x00000017); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d6f0:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4d6f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4e46e\n");
    __builtin_unreachable();
}

/* Original0x4D6F4..0x4D700. */
REGION void tsl9_resident_link_dispatch_core_block_4d6f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4d6fc:\n.option push\n.option norvc\njal zero,.Lresident_link_dispatch_core_edge_4d6fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d66e\n");
    __builtin_unreachable();
}

/* Original0x4D700..0x4D708. */
REGION void tsl9_resident_link_dispatch_core_block_4d700(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D708..0x4D70A. */
REGION void tsl9_resident_link_dispatch_core_block_4d708(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4D806..0x4D820. */
REGION void tsl9_candidate_link_dispatch_4d806(void)
{
    REGS;
    a2 = UINT32_C(0x00000640); LIVE;
    a2 = a1 * a2; LIVE;
    a3 = a0 + UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    a0 = UINT32_C(0x0004d000); LIVE;
    a0 = a0 + UINT32_C(0x000006e0); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4d81c:\n.option push\n.option norvc\njal zero,.Lresident_link_dispatch_core_edge_4d81c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x4DA42..0x4DA5A. */
REGION void tsl9_candidate_link_dispatch_4da42(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00005000); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffffc03); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4da52:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4da52\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DA5A..0x4DA5C. */
REGION void tsl9_resident_link_dispatch_core_block_4da5a(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4da5a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4da5a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4da6a\n");
    __builtin_unreachable();
}

/* Original0x4DA5C..0x4DA6A. */
REGION void tsl9_resident_link_dispatch_core_block_4da5c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0xfffffffa); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4da62:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_link_dispatch_200001e4\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4da62\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DA6A..0x4DA70. */
REGION void tsl9_resident_link_dispatch_core_block_4da6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E4CC..0x4E4E4. */
REGION void tsl9_candidate_link_dispatch_4e4cc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 0(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x219a\n.option pop\n");
    a3 = UINT32_C(0x0000000c); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0xfffffffc); LIVE;
    a4 = a4 * a3; LIVE;
    a5 = a5 + UINT32_C(0x00000320); LIVE;
    a5 = a5 + a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e4e2:\n.option push\n.option rvc\nc.bnez a4,.Lresident_link_dispatch_core_edge_4e4e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4e4f2\n");
    __builtin_unreachable();
}

/* Original0x4E4E4..0x4E4F2. */
REGION void tsl9_resident_link_dispatch_core_block_4e4e4(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.sh a0, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7aa\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21ba\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa79a\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E4F2..0x4E4F6. */
REGION void tsl9_resident_link_dispatch_core_block_4e4f2(void)
{
    REGS;
    a0 = UINT32_C(0x00000016); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E6CA..0x4E6CE. */
REGION void tsl9_candidate_link_dispatch_4e6ca(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 2(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x21ba\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4e6cc:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_dispatch_core_edge_4e6cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4e7a0\n");
    __builtin_unreachable();
}

/* Original0x4E6CE..0x4E6DC. */
REGION void tsl9_resident_link_dispatch_core_block_4e6ce(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xffffff9e)); LIVE;
    a5 = UINT32_C(0x0000001b); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e6d8:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_link_dispatch_core_edge_4e6d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e7a2\n");
    __builtin_unreachable();
}

/* Original0x4E6DC..0x4E6F4. */
REGION void tsl9_resident_link_dispatch_core_block_4e6dc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 4(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4e6ec:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_link_dispatch_200001e4\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4e6ec\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E6F4..0x4E71A. */
REGION void tsl9_resident_link_dispatch_core_block_4e6f4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203e\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa11c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203e\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb11c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa13c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201e\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 3(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb13c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2032\n.option pop\n");
    a5 = UINT32_C(0x00010000); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a2 = a2 + UINT32_C(0x00000004); LIVE;
    a2 = a2 << UINT32_C(0x00000010); LIVE;
    a2 = a2 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e716:\n.option push\n.option norvc\nbne s1,a5,.Lresident_link_dispatch_core_edge_4e716\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e75e\n");
    __builtin_unreachable();
}

/* Original0x4E71A..0x4E728. */
REGION void tsl9_resident_link_dispatch_core_block_4e71a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    a0 = UINT32_C(0x0000000c); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".Lresident_link_dispatch_core_literal_4e720:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4e720\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E728..0x4E72E. */
REGION void tsl9_resident_link_dispatch_core_block_4e728(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e72c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4e72c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E72E..0x4E750. */
REGION void tsl9_resident_link_dispatch_core_block_4e72e(void)
{
    REGS;
    a5 = UINT32_C(0xffffff90); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa11c\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xfffffffe); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa13e\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa15c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    /* Conditional Xwchc: qk.c.sh a2, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa172\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000314)); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e74c:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4e74c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x4E750..0x4E752. */
REGION void tsl9_resident_link_dispatch_core_block_4e750(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4E752..0x4E75E. */
REGION void tsl9_resident_link_dispatch_core_block_4e752(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E75E..0x4E766. */
REGION void tsl9_resident_link_dispatch_core_block_4e75e(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4e762:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4e762\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_534a6\n");
    __builtin_unreachable();
}

/* Original0x4E766..0x4E76A. */
REGION void tsl9_resident_link_dispatch_core_block_4e766(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4e768:\n.option push\n.option rvc\nc.bnez a0,.Lresident_link_dispatch_core_edge_4e768\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4e77c\n");
    __builtin_unreachable();
}

/* Original0x4E76A..0x4E772. */
REGION void tsl9_resident_link_dispatch_core_block_4e76a(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xffffffa2)); LIVE;
    __builtin_unreachable();
}

/* Original0x4E772..0x4E774. */
REGION void tsl9_resident_link_dispatch_core_block_4e772(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4e772:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_dispatch_core_edge_4e772\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E774..0x4E77C. */
REGION void tsl9_resident_link_dispatch_core_block_4e774(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xffffffa2)) = (uint8_t)a4; LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e77a:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4e77a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E77C..0x4E782. */
REGION void tsl9_resident_link_dispatch_core_block_4e77c(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e77e:\n.option push\n.option norvc\nbeq a0,a4,.Lresident_link_dispatch_core_edge_4e77e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e7a6\n");
    __builtin_unreachable();
}

/* Original0x4E782..0x4E788. */
REGION void tsl9_resident_link_dispatch_core_block_4e782(void)
{
    REGS;
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e784:\n.option push\n.option norvc\nbeq a0,a4,.Lresident_link_dispatch_core_edge_4e784\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e7aa\n");
    __builtin_unreachable();
}

/* Original0x4E788..0x4E78E. */
REGION void tsl9_resident_link_dispatch_core_block_4e788(void)
{
    REGS;
    a4 = UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e78a:\n.option push\n.option norvc\nbeq a0,a4,.Lresident_link_dispatch_core_edge_4e78a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e7ae\n");
    __builtin_unreachable();
}

/* Original0x4E78E..0x4E794. */
REGION void tsl9_resident_link_dispatch_core_block_4e78e(void)
{
    REGS;
    a4 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e790:\n.option push\n.option norvc\nbne a0,a4,.Lresident_link_dispatch_core_edge_4e790\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E794..0x4E7A0. */
REGION void tsl9_resident_link_dispatch_core_block_4e794(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xffffffa2)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e79e:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4e79e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4e772\n");
    __builtin_unreachable();
}

/* Original0x4E7A0..0x4E7A2. */
REGION void tsl9_resident_link_dispatch_core_block_4e7a0(void)
{
    REGS;
    a5 = UINT32_C(0x0000001b); LIVE;
    __builtin_unreachable();
}

/* Original0x4E7A2..0x4E7A6. */
REGION void tsl9_resident_link_dispatch_core_block_4e7a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4E7A6..0x4E7AA. */
REGION void tsl9_resident_link_dispatch_core_block_4e7a6(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e7a8:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4e7a8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E7AA..0x4E7AE. */
REGION void tsl9_resident_link_dispatch_core_block_4e7aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e7ac:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4e7ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4E7AE..0x4E7B2. */
REGION void tsl9_resident_link_dispatch_core_block_4e7ae(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4e7b0:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4e7b0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4e752\n");
    __builtin_unreachable();
}

/* Original0x4EA8C..0x4EAAA. */
REGION void tsl9_candidate_link_dispatch_4ea8c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    a0 = UINT32_C(0x00000017); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nsw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a2\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4eaa6:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eaa6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4da42\n");
    __builtin_unreachable();
}

/* Original0x4EAAA..0x4EAAC. */
REGION void tsl9_resident_link_dispatch_core_block_4eaaa(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eaaa:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4eaaa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eb0e\n");
    __builtin_unreachable();
}

/* Original0x4EAAC..0x4EAB4. */
REGION void tsl9_resident_link_dispatch_core_block_4eaac(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4eab2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_link_dispatch_core_edge_4eab2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eabe\n");
    __builtin_unreachable();
}

/* Original0x4EAB4..0x4EABE. */
REGION void tsl9_resident_link_dispatch_core_block_4eab4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a3 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a3\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EABE..0x4EAE6. */
REGION void tsl9_resident_link_dispatch_core_block_4eabe(void)
{
    REGS;
    a5 = a0 >> UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb s3, 0(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 1(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb03c\n.option pop\n");
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.shsp a5, 24(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x84fc\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa2)); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa028\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.shsp a0, 26(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x85e8\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a1, sp, 24\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eae4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_dispatch_core_edge_4eae4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eb08\n");
    __builtin_unreachable();
}

/* Original0x4EAE6..0x4EAEA. */
REGION void tsl9_resident_link_dispatch_core_block_4eae6(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eae6:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eae6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4e6ca\n");
    __builtin_unreachable();
}

/* Original0x4EAEA..0x4EAEE. */
REGION void tsl9_resident_link_dispatch_core_block_4eaea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eaec:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4eaec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eaf8\n");
    __builtin_unreachable();
}

/* Original0x4EAEE..0x4EAF8. */
REGION void tsl9_resident_link_dispatch_core_block_4eaee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4eaf0:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4eaf0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EAF8..0x4EB08. */
REGION void tsl9_resident_link_dispatch_core_block_4eaf8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EB08..0x4EB0C. */
REGION void tsl9_resident_link_dispatch_core_block_4eb08(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eb08:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eb08\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4e4cc\n");
    __builtin_unreachable();
}

/* Original0x4EB0C..0x4EB0E. */
REGION void tsl9_resident_link_dispatch_core_block_4eb0c(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eb0c:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4eb0c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4eaea\n");
    __builtin_unreachable();
}

/* Original0x4EB0E..0x4EB12. */
REGION void tsl9_resident_link_dispatch_core_block_4eb0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 19\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb10:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4eb10\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4eaf8\n");
    __builtin_unreachable();
}

/* Original0x4EB12..0x4EB30. */
REGION void tsl9_candidate_unprovided_flash_4eb12(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a3\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb2c:\n.option push\n.option norvc\nbne a1,a4,.Lresident_link_dispatch_core_edge_4eb2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4eb96\n");
    __builtin_unreachable();
}

/* Original0x4EB30..0x4EB38. */
REGION void tsl9_resident_link_dispatch_core_block_4eb30(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 2(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x222a\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 2\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb34:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eb34\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4d5a0\n");
    __builtin_unreachable();
}

/* Original0x4EB38..0x4EB3C. */
REGION void tsl9_resident_link_dispatch_core_block_4eb38(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4eb3a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4eb3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eba6\n");
    __builtin_unreachable();
}

/* Original0x4EB3C..0x4EB46. */
REGION void tsl9_resident_link_dispatch_core_block_4eb3c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nlhu s3, 6(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23be\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa09e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EB46..0x4EB68. */
REGION void tsl9_resident_link_dispatch_core_block_4eb46(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nsb s5, 0(a5)\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000031c)); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3ba\n.option pop\n");
    a4 = a2 + UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000031c)) = (uint8_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb66:\n.option push\n.option rvc\nc.bnez a4,.Lresident_link_dispatch_core_edge_4eb66\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eb6e\n");
    __builtin_unreachable();
}

/* Original0x4EB68..0x4EB6E. */
REGION void tsl9_resident_link_dispatch_core_block_4eb68(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000031c)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x4EB6E..0x4EB74. */
REGION void tsl9_resident_link_dispatch_core_block_4eb6e(void)
{
    REGS;
    a4 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4eb70:\n.option push\n.option norvc\nbne s2,a4,.Lresident_link_dispatch_core_edge_4eb70\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4eb7e\n");
    __builtin_unreachable();
}

/* Original0x4EB74..0x4EB7E. */
REGION void tsl9_resident_link_dispatch_core_block_4eb74(void)
{
    REGS;
    a4 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa0ba\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa79a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EB7E..0x4EB8A. */
REGION void tsl9_resident_link_dispatch_core_block_4eb7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb86:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eb86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4ea8c\n");
    __builtin_unreachable();
}

/* Original0x4EB8A..0x4EB90. */
REGION void tsl9_resident_link_dispatch_core_block_4eb8a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4eb8e:\n.option push\n.option rvc\nc.beqz s0,.Lresident_link_dispatch_core_edge_4eb8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4ebba\n");
    __builtin_unreachable();
}

/* Original0x4EB90..0x4EB94. */
REGION void tsl9_resident_link_dispatch_core_block_4eb90(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eb90:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eb90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_event_4d66e\n");
    __builtin_unreachable();
}

/* Original0x4EB94..0x4EB96. */
REGION void tsl9_resident_link_dispatch_core_block_4eb94(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4eb94:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4eb94\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4eba6\n");
    __builtin_unreachable();
}

/* Original0x4EB96..0x4EBA2. */
REGION void tsl9_resident_link_dispatch_core_block_4eb96(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a6\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a3, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eb9e:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4eb9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4d4bc\n");
    __builtin_unreachable();
}

/* Original0x4EBA2..0x4EBA6. */
REGION void tsl9_resident_link_dispatch_core_block_4eba2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4eba4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4eba4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4eb46\n");
    __builtin_unreachable();
}

/* Original0x4EBA6..0x4EBBA. */
REGION void tsl9_resident_link_dispatch_core_block_4eba6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EBBA..0x4EBC0. */
REGION void tsl9_resident_link_dispatch_core_block_4ebba(void)
{
    REGS;
    a1 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4ebbc:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4ebbc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4d806\n");
    __builtin_unreachable();
}

/* Original0x4EBC0..0x4EBC2. */
REGION void tsl9_resident_link_dispatch_core_block_4ebc0(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4ebc0:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4ebc0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4eba6\n");
    __builtin_unreachable();
}

/* Original0x4ED98..0x4EDB4. */
REGION void tsl9_candidate_link_dispatch_4ed98(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 856\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s0, 48\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EDB4..0x4EDB8. */
REGION void tsl9_resident_link_dispatch_core_block_4edb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4edb6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_link_dispatch_core_edge_4edb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4edbe\n");
    __builtin_unreachable();
}

/* Original0x4EDB8..0x4EDBE. */
REGION void tsl9_resident_link_dispatch_core_block_4edb8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EDBE..0x4EDC4. */
REGION void tsl9_resident_link_dispatch_core_block_4edbe(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 4\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4edc0:\n.option push\n.option norvc\nbne s0,s1,.Lresident_link_dispatch_core_edge_4edc0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4edb4\n");
    __builtin_unreachable();
}

/* Original0x4EDC4..0x4EDD2. */
REGION void tsl9_resident_link_dispatch_core_block_4edc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F00C..0x4F01A. */
REGION void tsl9_candidate_link_dispatch_4f00c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_literal_4f012:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_link_event_20000a94\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4f012\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F01A..0x4F01C. */
REGION void tsl9_resident_link_dispatch_core_block_4f01a(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4f01a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4f01a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4f054\n");
    __builtin_unreachable();
}

/* Original0x4F01C..0x4F026. */
REGION void tsl9_resident_link_dispatch_core_block_4f01c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x212a\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4f022:\n.option push\n.option norvc\njal ra,.Lresident_link_dispatch_core_edge_4f022\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_link_dispatch_4ed98\n");
    __builtin_unreachable();
}

/* Original0x4F026..0x4F02A. */
REGION void tsl9_resident_link_dispatch_core_block_4f026(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 44(s0)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4f028:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4f028\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4f032\n");
    __builtin_unreachable();
}

/* Original0x4F02A..0x4F032. */
REGION void tsl9_resident_link_dispatch_core_block_4f02a(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_literal_4f02a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4f02a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F032..0x4F042. */
REGION void tsl9_resident_link_dispatch_core_block_4f032(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x0000003c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_link_dispatch_core_literal_4f03a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_link_dispatch_core_literal_4f03a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F042..0x4F04C. */
REGION void tsl9_resident_link_dispatch_core_block_4f042(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa03e\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 4(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4F04C..0x4F054. */
REGION void tsl9_resident_link_dispatch_core_block_4f04c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F054..0x4F058. */
REGION void tsl9_resident_link_dispatch_core_block_4f054(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_4f056:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4f056\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4f04c\n");
    __builtin_unreachable();
}

/* Original0x4F0CC..0x4F0CE. */
REGION void tsl9_candidate_link_dispatch_4f0cc(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_4f0cc:\n.option push\n.option rvc\nc.beqz a0,.Lresident_link_dispatch_core_edge_4f0cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_link_dispatch_core_block_4f126\n");
    __builtin_unreachable();
}

/* Original0x4F0CE..0x4F0F6. */
REGION void tsl9_resident_link_dispatch_core_block_4f0ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s3, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 940\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 60\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F0F6..0x4F0FE. */
REGION void tsl9_resident_link_dispatch_core_block_4f0f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s2)\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4f0fa:\n.option push\n.option norvc\nblt s0,a5,.Lresident_link_dispatch_core_edge_4f0fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4f110\n");
    __builtin_unreachable();
}

/* Original0x4F0FE..0x4F110. */
REGION void tsl9_resident_link_dispatch_core_block_4f0fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F110..0x4F120. */
REGION void tsl9_resident_link_dispatch_core_block_4f110(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a0, s0, s5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 852(s4)\n.option pop\n");
    a0 = a0 + a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x213e\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4f11c:\n.option push\n.option norvc\nbeq a5,s3,.Lresident_link_dispatch_core_edge_4f11c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_4f122\n");
    __builtin_unreachable();
}

/* Original0x4F120..0x4F122. */
REGION void tsl9_resident_link_dispatch_core_block_4f120(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F122..0x4F126. */
REGION void tsl9_resident_link_dispatch_core_block_4f122(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_4f124:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_4f124\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_4f0f6\n");
    __builtin_unreachable();
}

/* Original0x4F126..0x4F128. */
REGION void tsl9_resident_link_dispatch_core_block_4f126(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x534A6..0x534AA. */
REGION void tsl9_candidate_link_dispatch_534a6(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_534a6:\n.option push\n.option norvc\njal zero,.Lresident_link_dispatch_core_edge_534a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_unprovided_flash_6a626\n");
    __builtin_unreachable();
}

/* Original0x200001E4..0x200001FA. */
REGION void tsl9_candidate_link_dispatch_200001e4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000194)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000018c)); LIVE;
    PORT(".option push\n.option rvc\nmv a4, a0\n.option pop\n");
    a1 = a0 - a1; LIVE;
    __builtin_unreachable();
}

/* Original0x200001FA..0x200001FE. */
REGION void tsl9_resident_link_dispatch_core_block_200001fa(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_200001fa:\n.option push\n.option norvc\nbne a2,a5,.Lresident_link_dispatch_core_edge_200001fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_20000202\n");
    __builtin_unreachable();
}

/* Original0x200001FE..0x20000202. */
REGION void tsl9_resident_link_dispatch_core_block_200001fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_20000200:\n.option push\n.option rvc\nc.j .Lresident_link_dispatch_core_edge_20000200\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_link_dispatch_core_block_2000021a\n");
    __builtin_unreachable();
}

/* Original0x20000202..0x2000020C. */
REGION void tsl9_resident_link_dispatch_core_block_20000202(void)
{
    REGS;
    a3 = a5 + UINT32_C(0x00000008); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_link_dispatch_core_edge_20000208:\n.option push\n.option norvc\nbltu a4,a3,.Lresident_link_dispatch_core_edge_20000208\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_200001fa\n");
    __builtin_unreachable();
}

/* Original0x2000020C..0x20000210. */
REGION void tsl9_resident_link_dispatch_core_block_2000020c(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_2000020c:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_link_dispatch_core_edge_2000020c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_200001fa\n");
    __builtin_unreachable();
}

/* Original0x20000210..0x20000216. */
REGION void tsl9_resident_link_dispatch_core_block_20000210(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".Lresident_link_dispatch_core_edge_20000212:\n.option push\n.option norvc\nbltu a1,a3,.Lresident_link_dispatch_core_edge_20000212\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_200001fa\n");
    __builtin_unreachable();
}

/* Original0x20000216..0x2000021A. */
REGION void tsl9_resident_link_dispatch_core_block_20000216(void)
{
    REGS;
    PORT(".Lresident_link_dispatch_core_edge_20000216:\n.option push\n.option norvc\nbleu a5,a1,.Lresident_link_dispatch_core_edge_20000216\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_link_dispatch_core_block_200001fa\n");
    __builtin_unreachable();
}

/* Original0x2000021A..0x2000021C. */
REGION void tsl9_resident_link_dispatch_core_block_2000021a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
