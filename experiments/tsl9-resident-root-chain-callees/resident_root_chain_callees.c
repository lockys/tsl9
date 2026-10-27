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

/* Ten complete conditional SDK root-callee bodies:1064B/352i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43ED2..0x43EDC. */
REGION void tsl9_candidate_external_flash_43ed2(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000244)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55D00..0x55D16. */
REGION void tsl9_candidate_external_flash_55d00(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000028)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55d12:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_root_chain_callees_edge_55d12\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55d24\n");
    __builtin_unreachable();
}

/* Original0x55D16..0x55D1C. */
REGION void tsl9_resident_root_chain_callees_block_55d16(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_root_chain_callees_edge_55d18:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_55d18\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43a14\n");
    __builtin_unreachable();
}

/* Original0x55D1C..0x55D24. */
REGION void tsl9_resident_root_chain_callees_block_55d1c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55D24..0x55D3C. */
REGION void tsl9_resident_root_chain_callees_block_55d24(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, s0, 40\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a0 = UINT32_C(0x00057000); LIVE;
    a0 = a0 + UINT32_C(0xfffffcdc); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55d38:\n.option push\n.option norvc\njal zero,.Lresident_root_chain_callees_edge_55d38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x55D3C..0x55D6E. */
REGION void tsl9_candidate_external_flash_55d3c(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a4 + UINT32_C(0x000003b8); LIVE;
    a3 = UINT32_C(0x0000001b); LIVE;
    /* Conditional Xwchc: qk.c.lhu a1, 34(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33ae\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 46(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x37f2\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001dc)) = (uint16_t)a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d8)) = (uint16_t)a3; LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 48(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3b96\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a6, 327(a0)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d4)) = (uint16_t)a1; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d0)) = (uint16_t)a2; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d2)) = (uint16_t)a3; LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = a4 + UINT32_C(0x000003b8); LIVE;
    PORT(".Lresident_root_chain_callees_edge_55d6a:\n.option push\n.option norvc\nbeq a6,a5,.Lresident_root_chain_callees_edge_55d6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55dd6\n");
    __builtin_unreachable();
}

/* Original0x55D6E..0x55D72. */
REGION void tsl9_resident_root_chain_callees_block_55d6e(void)
{
    REGS;
    a5 = UINT32_C(0x00000148); LIVE;
    __builtin_unreachable();
}

/* Original0x55D72..0x55D80. */
REGION void tsl9_resident_root_chain_callees_block_55d72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a7, 326(a0)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001de)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nli a6, 2\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55d7c:\n.option push\n.option norvc\nbne a7,a6,.Lresident_root_chain_callees_edge_55d7c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55dde\n");
    __builtin_unreachable();
}

/* Original0x55D80..0x55D8C. */
REGION void tsl9_resident_root_chain_callees_block_55d80(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 40(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x371a\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d6)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffffa90); LIVE;
    __builtin_unreachable();
}

/* Original0x55D8C..0x55D98. */
REGION void tsl9_resident_root_chain_callees_block_55d8c(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001da)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\nli a6, 27\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, a1\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55d94:\n.option push\n.option norvc\nbleu a1,a6,.Lresident_root_chain_callees_edge_55d94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55d9a\n");
    __builtin_unreachable();
}

/* Original0x55D98..0x55D9A. */
REGION void tsl9_resident_root_chain_callees_block_55d98(void)
{
    REGS;
    a4 = UINT32_C(0x0000001b); LIVE;
    __builtin_unreachable();
}

/* Original0x55D9A..0x55DAC. */
REGION void tsl9_resident_root_chain_callees_block_55d9a(void)
{
    REGS;
    a1 = a4 << UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e4)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\nli a6, 27\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a4, a2\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55da8:\n.option push\n.option norvc\nbleu a2,a6,.Lresident_root_chain_callees_edge_55da8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55dae\n");
    __builtin_unreachable();
}

/* Original0x55DAC..0x55DAE. */
REGION void tsl9_resident_root_chain_callees_block_55dac(void)
{
    REGS;
    a4 = UINT32_C(0x0000001b); LIVE;
    __builtin_unreachable();
}

/* Original0x55DAE..0x55DBE. */
REGION void tsl9_resident_root_chain_callees_block_55dae(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e0)) = (uint16_t)a4; LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d6)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001da)); LIVE;
    PORT(".Lresident_root_chain_callees_edge_55dba:\n.option push\n.option norvc\nbleu a4,a2,.Lresident_root_chain_callees_edge_55dba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55dc0\n");
    __builtin_unreachable();
}

/* Original0x55DBE..0x55DC0. */
REGION void tsl9_resident_root_chain_callees_block_55dbe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55DC0..0x55DCA. */
REGION void tsl9_resident_root_chain_callees_block_55dc0(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_55dc6:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_root_chain_callees_edge_55dc6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_55dcc\n");
    __builtin_unreachable();
}

/* Original0x55DCA..0x55DCC. */
REGION void tsl9_resident_root_chain_callees_block_55dca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55DCC..0x55DD6. */
REGION void tsl9_resident_root_chain_callees_block_55dcc(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)) = (uint16_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004e)) = (uint8_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55DD6..0x55DDE. */
REGION void tsl9_resident_root_chain_callees_block_55dd6(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a5 = a5 + UINT32_C(0xfffffa90); LIVE;
    PORT(".Lresident_root_chain_callees_edge_55ddc:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_55ddc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_55d72\n");
    __builtin_unreachable();
}

/* Original0x55DDE..0x55DEA. */
REGION void tsl9_resident_root_chain_callees_block_55dde(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 38(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x337a\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d6)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x00000148); LIVE;
    PORT(".Lresident_root_chain_callees_edge_55de8:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_55de8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_55d8c\n");
    __builtin_unreachable();
}

/* Original0x5605C..0x56072. */
REGION void tsl9_candidate_external_flash_5605c(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000004a)); LIVE;
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.lhu a2, 62(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d72\n.option pop\n");
    a5 = a4 * a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d36\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a1, a5, 0x3\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_5606e:\n.option push\n.option norvc\nble a1,a2,.Lresident_root_chain_callees_edge_5606e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56078\n");
    __builtin_unreachable();
}

/* Original0x56072..0x56078. */
REGION void tsl9_resident_root_chain_callees_block_56072(void)
{
    REGS;
    a4 = a4 - a2; LIVE;
    a5 = a4 << UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x56078..0x56086. */
REGION void tsl9_resident_root_chain_callees_block_56078(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a3\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000048)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x560AA..0x560B2. */
REGION void tsl9_candidate_external_flash_560aa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x255c\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa55c\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56326..0x56366. */
REGION void tsl9_candidate_external_flash_56326(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 56(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d1e\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    a3 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000234); LIVE;
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s3, 8(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 4(a5)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = a5 + UINT32_C(0x000003b8); LIVE;
    a1 = *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0x000000b4)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000088)); LIVE;
    PORT(".Lresident_root_chain_callees_edge_56362:\n.option push\n.option norvc\nbleu a1,a2,.Lresident_root_chain_callees_edge_56362\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56458\n");
    __builtin_unreachable();
}

/* Original0x56366..0x56384. */
REGION void tsl9_resident_root_chain_callees_block_56366(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a3, a3, s3\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a5, 952\n.option pop\n");
    a5 = UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option rvc\nli s4, 0\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a3, a3, a5\n.option pop\n");
    a4 = a4 + a3; LIVE;
    PORT(".option push\n.option rvc\nmv s2, a4\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_56380:\n.option push\n.option norvc\nbltu a4,a3,.Lresident_root_chain_callees_edge_56380\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56388\n");
    __builtin_unreachable();
}

/* Original0x56384..0x56388. */
REGION void tsl9_resident_root_chain_callees_block_56384(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_56384:\n.option push\n.option norvc\nbltu a4,s5,.Lresident_root_chain_callees_edge_56384\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_5638c\n");
    __builtin_unreachable();
}

/* Original0x56388..0x5638C. */
REGION void tsl9_resident_root_chain_callees_block_56388(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s2, a4, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5638C..0x563B6. */
REGION void tsl9_resident_root_chain_callees_block_5638c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s2, 144(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 486(s0)\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)); LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a0 = a0 + a5; LIVE;
    a0 = a0 + UINT32_C(0x00000271); LIVE;
    PORT(".option push\n.option norvc\nmulhsu a1, a0, s3\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s3, a0\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_563b2:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_563b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x563B6..0x563BE. */
REGION void tsl9_resident_root_chain_callees_block_563b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s7, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s6, 156(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x563BE..0x563DA. */
REGION void tsl9_resident_root_chain_callees_block_563be(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a5, s3, s1\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, s3, s1\n.option pop\n");
    a0 = a5 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a0, a5\n.option pop\n");
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_root_chain_callees_edge_563d6:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_563d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x563DA..0x563E0. */
REGION void tsl9_resident_root_chain_callees_block_563da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a0, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, s6\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x563E0..0x563E2. */
REGION void tsl9_resident_root_chain_callees_block_563e0(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_563e0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_root_chain_callees_edge_563e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_5642c\n");
    __builtin_unreachable();
}

/* Original0x563E2..0x563FE. */
REGION void tsl9_resident_root_chain_callees_block_563e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a4, s3, s1\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, s3, s1\n.option pop\n");
    a0 = a4 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a4, a0, a4\n.option pop\n");
    a1 = a1 + a4; LIVE;
    PORT(".Lresident_root_chain_callees_edge_563fa:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_563fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x563FE..0x5640A. */
REGION void tsl9_resident_root_chain_callees_block_563fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s2, s2, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, s2\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_56406:\n.option push\n.option norvc\nbne s4,a0,.Lresident_root_chain_callees_edge_56406\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_5640e\n");
    __builtin_unreachable();
}

/* Original0x5640A..0x5640E. */
REGION void tsl9_resident_root_chain_callees_block_5640a(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_5640a:\n.option push\n.option norvc\nbltu s2,s5,.Lresident_root_chain_callees_edge_5640a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56412\n");
    __builtin_unreachable();
}

/* Original0x5640E..0x56412. */
REGION void tsl9_resident_root_chain_callees_block_5640e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a5, s2, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56412..0x56416. */
REGION void tsl9_resident_root_chain_callees_block_56412(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 144(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56416..0x5642C. */
REGION void tsl9_resident_root_chain_callees_block_56416(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5642C..0x56430. */
REGION void tsl9_resident_root_chain_callees_block_5642c(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_5642c:\n.option push\n.option norvc\nbne a4,s0,.Lresident_root_chain_callees_edge_5642c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56434\n");
    __builtin_unreachable();
}

/* Original0x56430..0x56434. */
REGION void tsl9_resident_root_chain_callees_block_56430(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_root_chain_callees_edge_56432:\n.option push\n.option rvc\nc.beqz a4,.Lresident_root_chain_callees_edge_56432\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_563e2\n");
    __builtin_unreachable();
}

/* Original0x56434..0x56440. */
REGION void tsl9_resident_root_chain_callees_block_56434(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000008c)); LIVE;
    PORT(".option push\n.option norvc\nlw a3, 140(s0)\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_5643c:\n.option push\n.option norvc\nbne a2,a3,.Lresident_root_chain_callees_edge_5643c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56450\n");
    __builtin_unreachable();
}

/* Original0x56440..0x5644C. */
REGION void tsl9_resident_root_chain_callees_block_56440(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000090)); LIVE;
    a5 = a3 - a0; LIVE;
    PORT(".Lresident_root_chain_callees_edge_56448:\n.option push\n.option norvc\nbltu a0,a3,.Lresident_root_chain_callees_edge_56448\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56450\n");
    __builtin_unreachable();
}

/* Original0x5644C..0x56450. */
REGION void tsl9_resident_root_chain_callees_block_5644c(void)
{
    REGS;
    a5 = a0 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x56450..0x56454. */
REGION void tsl9_resident_root_chain_callees_block_56450(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_56450:\n.option push\n.option norvc\nbltu a5,s7,.Lresident_root_chain_callees_edge_56450\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_5648c\n");
    __builtin_unreachable();
}

/* Original0x56454..0x56458. */
REGION void tsl9_resident_root_chain_callees_block_56454(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_root_chain_callees_edge_56456:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_56456\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_563e0\n");
    __builtin_unreachable();
}

/* Original0x56458..0x5647E. */
REGION void tsl9_resident_root_chain_callees_block_56458(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000037)); LIVE;
    a5 = (uint32_t)(a5 < UINT32_C(0x00000002)); LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option norvc\nmul a5, a5, s3\n.option pop\n");
    a3 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_5647a:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_root_chain_callees_edge_5647a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56482\n");
    __builtin_unreachable();
}

/* Original0x5647E..0x56482. */
REGION void tsl9_resident_root_chain_callees_block_5647e(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_5647e:\n.option push\n.option norvc\nbltu a4,s5,.Lresident_root_chain_callees_edge_5647e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_56486\n");
    __builtin_unreachable();
}

/* Original0x56482..0x56486. */
REGION void tsl9_resident_root_chain_callees_block_56482(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a3, a4, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56486..0x5648C. */
REGION void tsl9_resident_root_chain_callees_block_56486(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000090)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_root_chain_callees_edge_5648a:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_5648a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_56416\n");
    __builtin_unreachable();
}

/* Original0x5648C..0x5649A. */
REGION void tsl9_resident_root_chain_callees_block_5648c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 55(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, 1\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_root_chain_callees_edge_56496:\n.option push\n.option norvc\nbltu s1,a5,.Lresident_root_chain_callees_edge_56496\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_563be\n");
    __builtin_unreachable();
}

/* Original0x5649A..0x5649C. */
REGION void tsl9_resident_root_chain_callees_block_5649a(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_5649a:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_5649a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_563e2\n");
    __builtin_unreachable();
}

/* Original0x56716..0x5672E. */
REGION void tsl9_candidate_external_flash_56716(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000234); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 12(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2750\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    PORT(".Lresident_root_chain_callees_edge_5672c:\n.option push\n.option rvc\nc.beqz a2,.Lresident_root_chain_callees_edge_5672c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_56768\n");
    __builtin_unreachable();
}

/* Original0x5672E..0x56738. */
REGION void tsl9_resident_root_chain_callees_block_5672e(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x000004ec)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_56736:\n.option push\n.option rvc\nc.bnez a2,.Lresident_root_chain_callees_edge_56736\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_5674a\n");
    __builtin_unreachable();
}

/* Original0x56738..0x5674A. */
REGION void tsl9_resident_root_chain_callees_block_56738(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000b0)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20001000); LIVE;
    a4 = a4 + UINT32_C(0x000003e8); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x000004ec)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x5674A..0x56756. */
REGION void tsl9_resident_root_chain_callees_block_5674a(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x000004ec)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a4)) = (uint32_t)0; LIVE;
    PORT(".Lresident_root_chain_callees_edge_56752:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_56752\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43ed2\n");
    __builtin_unreachable();
}

/* Original0x56756..0x56768. */
REGION void tsl9_resident_root_chain_callees_block_56756(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0xe000e000); LIVE;
    a4 = UINT32_C(0x02000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000204)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56768..0x567A0. */
REGION void tsl9_resident_root_chain_callees_block_56768(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 8(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2712\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a4)) = (uint32_t)0; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000086)); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x000004ec)) = (uint32_t)0; LIVE;
    a5 = a5 * a2; LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000090)); LIVE;
    a0 = a2 + UINT32_C(0x0000023f); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a5 = a5 + a0; LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a2\n.option pop\n");
    a2 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000203)); LIVE;
    a2 = a2 + a5; LIVE;
    PORT(".Lresident_root_chain_callees_edge_5679c:\n.option push\n.option norvc\nbltu a3,a2,.Lresident_root_chain_callees_edge_5679c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_567b8\n");
    __builtin_unreachable();
}

/* Original0x567A0..0x567B8. */
REGION void tsl9_resident_root_chain_callees_block_567a0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000008c)); LIVE;
    a0 = UINT32_C(0x20001000); LIVE;
    a2 = a3 - a2; LIVE;
    a0 = a0 + UINT32_C(0x0000038e); LIVE;
    a3 = a1 + UINT32_C(0x00000029); LIVE;
    PORT(".Lresident_root_chain_callees_edge_567b4:\n.option push\n.option norvc\njal zero,.Lresident_root_chain_callees_edge_567b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43414\n");
    __builtin_unreachable();
}

/* Original0x567B8..0x567BE. */
REGION void tsl9_resident_root_chain_callees_block_567b8(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 + a5; LIVE;
    PORT(".Lresident_root_chain_callees_edge_567bc:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_567bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_567a0\n");
    __builtin_unreachable();
}

/* Original0x57B28..0x57B4E. */
REGION void tsl9_candidate_external_flash_57b28(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s4, 312(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 316(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000137)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000012d)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nli s2, 37\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57B4E..0x57B58. */
REGION void tsl9_resident_root_chain_callees_block_57b4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_57b54:\n.option push\n.option norvc\njal ra,.Lresident_root_chain_callees_edge_57b54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6dec2\n");
    __builtin_unreachable();
}

/* Original0x57B58..0x57B5C. */
REGION void tsl9_resident_root_chain_callees_block_57b58(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_root_chain_callees_edge_57b5a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_root_chain_callees_edge_57b5a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_57b66\n");
    __builtin_unreachable();
}

/* Original0x57B5C..0x57B66. */
REGION void tsl9_resident_root_chain_callees_block_57b5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 301(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 301(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57B66..0x57B6C. */
REGION void tsl9_resident_root_chain_callees_block_57b66(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, 1\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_57b68:\n.option push\n.option norvc\nbne s1,s2,.Lresident_root_chain_callees_edge_57b68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_57b4e\n");
    __builtin_unreachable();
}

/* Original0x57B6C..0x57B7C. */
REGION void tsl9_resident_root_chain_callees_block_57b6c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63966..0x6396E. */
REGION void tsl9_candidate_external_flash_63966(void)
{
    REGS;
    a5 = UINT32_C(0x0000003e); LIVE;
    PORT(".Lresident_root_chain_callees_edge_6396a:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_root_chain_callees_edge_6396a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c6\n");
    __builtin_unreachable();
}

/* Original0x6396E..0x63978. */
REGION void tsl9_resident_root_chain_callees_block_6396e(void)
{
    REGS;
    a4 = UINT32_C(0x00000024); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_root_chain_callees_edge_63974:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_63974\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x63978..0x63980. */
REGION void tsl9_resident_root_chain_callees_block_63978(void)
{
    REGS;
    a4 = UINT32_C(0x0000001a); LIVE;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_root_chain_callees_edge_6397c:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_6397c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x63980..0x63988. */
REGION void tsl9_resident_root_chain_callees_block_63980(void)
{
    REGS;
    a4 = UINT32_C(0x00000014); LIVE;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_root_chain_callees_edge_63984:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_63984\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x63988..0x63990. */
REGION void tsl9_resident_root_chain_callees_block_63988(void)
{
    REGS;
    a4 = UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_root_chain_callees_edge_6398c:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_6398c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x63990..0x63998. */
REGION void tsl9_resident_root_chain_callees_block_63990(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_root_chain_callees_edge_63994:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_63994\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x63998..0x639A0. */
REGION void tsl9_resident_root_chain_callees_block_63998(void)
{
    REGS;
    a4 = UINT32_C(0x0000000a); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_root_chain_callees_edge_6399c:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_6399c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x639A0..0x639A8. */
REGION void tsl9_resident_root_chain_callees_block_639a0(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_root_chain_callees_edge_639a4:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_639a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x639A8..0x639B0. */
REGION void tsl9_resident_root_chain_callees_block_639a8(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    a5 = UINT32_C(0xfffffffd); LIVE;
    PORT(".Lresident_root_chain_callees_edge_639ac:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_639ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x639B0..0x639B8. */
REGION void tsl9_resident_root_chain_callees_block_639b0(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    a5 = UINT32_C(0xfffffffb); LIVE;
    PORT(".Lresident_root_chain_callees_edge_639b4:\n.option push\n.option norvc\nbltu a4,a0,.Lresident_root_chain_callees_edge_639b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x639B8..0x639C0. */
REGION void tsl9_resident_root_chain_callees_block_639b8(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = UINT32_C(0xffffffee); LIVE;
    PORT(".Lresident_root_chain_callees_edge_639bc:\n.option push\n.option norvc\nbleu a0,a4,.Lresident_root_chain_callees_edge_639bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x639C0..0x639C2. */
REGION void tsl9_resident_root_chain_callees_block_639c0(void)
{
    REGS;
    a5 = UINT32_C(0xfffffff6); LIVE;
    __builtin_unreachable();
}

/* Original0x639C2..0x639C6. */
REGION void tsl9_resident_root_chain_callees_block_639c2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x639C6..0x639CA. */
REGION void tsl9_resident_root_chain_callees_block_639c6(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_root_chain_callees_edge_639c8:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_639c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_639c2\n");
    __builtin_unreachable();
}

/* Original0x6DEC2..0x6DEC4. */
REGION void tsl9_candidate_external_flash_6dec2(void)
{
    REGS;
    PORT(".Lresident_root_chain_callees_edge_6dec2:\n.option push\n.option rvc\nc.beqz a2,.Lresident_root_chain_callees_edge_6dec2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_root_chain_callees_block_6dede\n");
    __builtin_unreachable();
}

/* Original0x6DEC4..0x6DECE. */
REGION void tsl9_resident_root_chain_callees_block_6dec4(void)
{
    REGS;
    a5 = UINT32_C(0x00000020); LIVE;
    a5 = a5 - a2; LIVE;
    PORT(".Lresident_root_chain_callees_edge_6deca:\n.option push\n.option norvc\nblez a5,.Lresident_root_chain_callees_edge_6deca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_root_chain_callees_block_6dee0\n");
    __builtin_unreachable();
}

/* Original0x6DECE..0x6DEDE. */
REGION void tsl9_resident_root_chain_callees_block_6dece(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrl a0, a0, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a5, a1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsrl a2, a1, a2\n.option pop\n");
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option rvc\nmv a1, a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DEDE..0x6DEE0. */
REGION void tsl9_resident_root_chain_callees_block_6dede(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DEE0..0x6DEEE. */
REGION void tsl9_resident_root_chain_callees_block_6dee0(void)
{
    REGS;
    a0 = a2 + UINT32_C(0xffffffe0); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsrl a0, a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a2\n.option pop\n");
    PORT(".Lresident_root_chain_callees_edge_6deec:\n.option push\n.option rvc\nc.j .Lresident_root_chain_callees_edge_6deec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_root_chain_callees_block_6dede\n");
    __builtin_unreachable();
}
