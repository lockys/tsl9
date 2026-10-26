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

/* One complete public-SDK arithmetic body:914B/296i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x6DF1A..0x6DF26. */
REGION void tsl9_candidate_external_flash_6df1a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a7, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv t1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a6, a1\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6df22:\n.option push\n.option norvc\nbnez a3,.Lresident_arithmetic_helper_edge_6df22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e078\n");
    __builtin_unreachable();
}

/* Original0x6DF26..0x6DF2A. */
REGION void tsl9_resident_arithmetic_helper_block_6df26(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6df26:\n.option push\n.option norvc\nbleu a2,a1,.Lresident_arithmetic_helper_edge_6df26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6dfd6\n");
    __builtin_unreachable();
}

/* Original0x6DF2A..0x6DF30. */
REGION void tsl9_resident_arithmetic_helper_block_6df2a(void)
{
    REGS;
    a4 = UINT32_C(0x00010000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6df2c:\n.option push\n.option norvc\nbltu a2,a4,.Lresident_arithmetic_helper_edge_6df2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e0e2\n");
    __builtin_unreachable();
}

/* Original0x6DF30..0x6DF38. */
REGION void tsl9_resident_arithmetic_helper_block_6df30(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6df34:\n.option push\n.option norvc\nbltu a2,a5,.Lresident_arithmetic_helper_edge_6df34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e274\n");
    __builtin_unreachable();
}

/* Original0x6DF38..0x6DF3E. */
REGION void tsl9_resident_arithmetic_helper_block_6df38(void)
{
    REGS;
    a3 = a2 >> UINT32_C(0x00000018); LIVE;
    a5 = UINT32_C(0x00000018); LIVE;
    __builtin_unreachable();
}

/* Original0x6DF3E..0x6DF54. */
REGION void tsl9_resident_arithmetic_helper_block_6df3e(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_literal_6df3e:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_bitlength_table_6e95c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_arithmetic_helper_literal_6df3e\n.option pop\n");
    a4 = a4 + a3; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2318\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x00000020); LIVE;
    a4 = a4 - a5; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6df52:\n.option push\n.option rvc\nc.beqz a4,.Lresident_arithmetic_helper_edge_6df52\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_arithmetic_helper_block_6df68\n");
    __builtin_unreachable();
}

/* Original0x6DF54..0x6DF68. */
REGION void tsl9_resident_arithmetic_helper_block_6df54(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsll a6, a1, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsrl a5, a0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a7, a2, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nor a6, a5, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nsll t1, a0, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DF68..0x6DF8C. */
REGION void tsl9_resident_arithmetic_helper_block_6df68(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a2, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a0, a6, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a3, a7, 0x10\n.option pop\n");
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsrli a5, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a4, a6, a2\n.option pop\n");
    a1 = a3 * a0; LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nor a6, a4, a5\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6df88:\n.option push\n.option norvc\nbleu a1,a6,.Lresident_arithmetic_helper_edge_6df88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6df9c\n");
    __builtin_unreachable();
}

/* Original0x6DF8C..0x6DF96. */
REGION void tsl9_resident_arithmetic_helper_block_6df8c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a6, a6, a7\n.option pop\n");
    a5 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6df92:\n.option push\n.option norvc\nbltu a6,a7,.Lresident_arithmetic_helper_edge_6df92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6df9a\n");
    __builtin_unreachable();
}

/* Original0x6DF96..0x6DF9A. */
REGION void tsl9_resident_arithmetic_helper_block_6df96(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6df96:\n.option push\n.option norvc\nbltu a6,a1,.Lresident_arithmetic_helper_edge_6df96\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e2a0\n");
    __builtin_unreachable();
}

/* Original0x6DF9A..0x6DF9C. */
REGION void tsl9_resident_arithmetic_helper_block_6df9a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DF9C..0x6DFBC. */
REGION void tsl9_resident_arithmetic_helper_block_6df9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a6, a6, a1\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a4, a6, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nslli t1, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t1, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a6, a6, a2\n.option pop\n");
    a3 = a3 * a4; LIVE;
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nor a6, a6, t1\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6dfb8:\n.option push\n.option norvc\nbleu a3,a6,.Lresident_arithmetic_helper_edge_6dfb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6dfce\n");
    __builtin_unreachable();
}

/* Original0x6DFBC..0x6DFC6. */
REGION void tsl9_resident_arithmetic_helper_block_6dfbc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a6, a6, a7\n.option pop\n");
    a5 = a4 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6dfc2:\n.option push\n.option norvc\nbltu a6,a7,.Lresident_arithmetic_helper_edge_6dfc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6dfcc\n");
    __builtin_unreachable();
}

/* Original0x6DFC6..0x6DFCC. */
REGION void tsl9_resident_arithmetic_helper_block_6dfc6(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6dfc8:\n.option push\n.option norvc\nbltu a6,a3,.Lresident_arithmetic_helper_edge_6dfc8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6dfce\n");
    __builtin_unreachable();
}

/* Original0x6DFCC..0x6DFCE. */
REGION void tsl9_resident_arithmetic_helper_block_6dfcc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DFCE..0x6DFD6. */
REGION void tsl9_resident_arithmetic_helper_block_6dfce(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 | a4; LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DFD6..0x6DFD8. */
REGION void tsl9_resident_arithmetic_helper_block_6dfd6(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6dfd6:\n.option push\n.option rvc\nc.bnez a2,.Lresident_arithmetic_helper_edge_6dfd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_arithmetic_helper_block_6dfde\n");
    __builtin_unreachable();
}

/* Original0x6DFD8..0x6DFDE. */
REGION void tsl9_resident_arithmetic_helper_block_6dfd8(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\ndivu a7, a4, a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6DFDE..0x6DFE4. */
REGION void tsl9_resident_arithmetic_helper_block_6dfde(void)
{
    REGS;
    a4 = UINT32_C(0x00010000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6dfe0:\n.option push\n.option norvc\nbltu a7,a4,.Lresident_arithmetic_helper_edge_6dfe0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e0d0\n");
    __builtin_unreachable();
}

/* Original0x6DFE4..0x6DFEC. */
REGION void tsl9_resident_arithmetic_helper_block_6dfe4(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6dfe8:\n.option push\n.option norvc\nbltu a7,a5,.Lresident_arithmetic_helper_edge_6dfe8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e27c\n");
    __builtin_unreachable();
}

/* Original0x6DFEC..0x6DFF2. */
REGION void tsl9_resident_arithmetic_helper_block_6dfec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a3, a7, 0x18\n.option pop\n");
    a5 = UINT32_C(0x00000018); LIVE;
    __builtin_unreachable();
}

/* Original0x6DFF2..0x6E008. */
REGION void tsl9_resident_arithmetic_helper_block_6dff2(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_literal_6dff2:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_bitlength_table_6e95c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_arithmetic_helper_literal_6dff2\n.option pop\n");
    a4 = a4 + a3; LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2314\n.option pop\n");
    a3 = a3 + a5; LIVE;
    a5 = UINT32_C(0x00000020); LIVE;
    a5 = a5 - a3; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e006:\n.option push\n.option rvc\nc.bnez a5,.Lresident_arithmetic_helper_edge_6e006\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_arithmetic_helper_block_6e0f4\n");
    __builtin_unreachable();
}

/* Original0x6E008..0x6E01A. */
REGION void tsl9_resident_arithmetic_helper_block_6e008(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli t4, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a4, a1, a7\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t5, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t4, t4, 0x10\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x6E01A..0x6E032. */
REGION void tsl9_resident_arithmetic_helper_block_6e01a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a5, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a0, a4, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a4, a4, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a3, a0, t4\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e02e:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_arithmetic_helper_edge_6e02e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e042\n");
    __builtin_unreachable();
}

/* Original0x6E032..0x6E03C. */
REGION void tsl9_resident_arithmetic_helper_block_6e032(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a5, a5, a7\n.option pop\n");
    a4 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e038:\n.option push\n.option norvc\nbltu a5,a7,.Lresident_arithmetic_helper_edge_6e038\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e040\n");
    __builtin_unreachable();
}

/* Original0x6E03C..0x6E040. */
REGION void tsl9_resident_arithmetic_helper_block_6e03c(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e03c:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_arithmetic_helper_edge_6e03c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e2a6\n");
    __builtin_unreachable();
}

/* Original0x6E040..0x6E042. */
REGION void tsl9_resident_arithmetic_helper_block_6e040(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E042..0x6E060. */
REGION void tsl9_resident_arithmetic_helper_block_6e042(void)
{
    REGS;
    a5 = a5 - a3; LIVE;
    PORT(".option push\n.option norvc\ndivu a4, a5, t5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli t1, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t1, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul t4, a4, t4\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nor a5, a5, t1\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e05c:\n.option push\n.option norvc\nbleu t4,a5,.Lresident_arithmetic_helper_edge_6e05c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e072\n");
    __builtin_unreachable();
}

/* Original0x6E060..0x6E06A. */
REGION void tsl9_resident_arithmetic_helper_block_6e060(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a5, a5, a7\n.option pop\n");
    a3 = a4 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e066:\n.option push\n.option norvc\nbltu a5,a7,.Lresident_arithmetic_helper_edge_6e066\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e070\n");
    __builtin_unreachable();
}

/* Original0x6E06A..0x6E070. */
REGION void tsl9_resident_arithmetic_helper_block_6e06a(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e06c:\n.option push\n.option norvc\nbltu a5,t4,.Lresident_arithmetic_helper_edge_6e06c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e072\n");
    __builtin_unreachable();
}

/* Original0x6E070..0x6E072. */
REGION void tsl9_resident_arithmetic_helper_block_6e070(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E072..0x6E078. */
REGION void tsl9_resident_arithmetic_helper_block_6e072(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 | a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E078..0x6E07C. */
REGION void tsl9_resident_arithmetic_helper_block_6e078(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e078:\n.option push\n.option norvc\nbltu a1,a3,.Lresident_arithmetic_helper_edge_6e078\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e0ba\n");
    __builtin_unreachable();
}

/* Original0x6E07C..0x6E082. */
REGION void tsl9_resident_arithmetic_helper_block_6e07c(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e07e:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_arithmetic_helper_edge_6e07e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e0c0\n");
    __builtin_unreachable();
}

/* Original0x6E082..0x6E08A. */
REGION void tsl9_resident_arithmetic_helper_block_6e082(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e086:\n.option push\n.option norvc\nbltu a3,a5,.Lresident_arithmetic_helper_edge_6e086\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e26c\n");
    __builtin_unreachable();
}

/* Original0x6E08A..0x6E090. */
REGION void tsl9_resident_arithmetic_helper_block_6e08a(void)
{
    REGS;
    a4 = a3 >> UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nli a6, 24\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E090..0x6E0AA. */
REGION void tsl9_resident_arithmetic_helper_block_6e090(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_literal_6e090:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_bitlength_table_6e95c\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_arithmetic_helper_literal_6e090\n.option pop\n");
    a5 = a5 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    PORT(".option push\n.option norvc\nli t3, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nsub t3, t3, a4\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e0a6:\n.option push\n.option norvc\nbnez t3,.Lresident_arithmetic_helper_edge_6e0a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e17a\n");
    __builtin_unreachable();
}

/* Original0x6E0AA..0x6E0AE. */
REGION void tsl9_resident_arithmetic_helper_block_6e0aa(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e0aa:\n.option push\n.option norvc\nbltu a3,a1,.Lresident_arithmetic_helper_edge_6e0aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e284\n");
    __builtin_unreachable();
}

/* Original0x6E0AE..0x6E0BA. */
REGION void tsl9_resident_arithmetic_helper_block_6e0ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsltu a0, a0, a2\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E0BA..0x6E0C0. */
REGION void tsl9_resident_arithmetic_helper_block_6e0ba(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E0C0..0x6E0C8. */
REGION void tsl9_resident_arithmetic_helper_block_6e0c0(void)
{
    REGS;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e0c4:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_arithmetic_helper_edge_6e0c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e28a\n");
    __builtin_unreachable();
}

/* Original0x6E0C8..0x6E0D0. */
REGION void tsl9_resident_arithmetic_helper_block_6e0c8(void)
{
    REGS;
    a4 = a3 >> UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nli a6, 8\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e0ce:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e0ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e090\n");
    __builtin_unreachable();
}

/* Original0x6E0D0..0x6E0DA. */
REGION void tsl9_resident_arithmetic_helper_block_6e0d0(void)
{
    REGS;
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a3, a7\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e0d6:\n.option push\n.option norvc\nbleu a7,a4,.Lresident_arithmetic_helper_edge_6e0d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6dff2\n");
    __builtin_unreachable();
}

/* Original0x6E0DA..0x6E0E2. */
REGION void tsl9_resident_arithmetic_helper_block_6e0da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a3, a7, 0x8\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e0e0:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e0e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6dff2\n");
    __builtin_unreachable();
}

/* Original0x6E0E2..0x6E0EC. */
REGION void tsl9_resident_arithmetic_helper_block_6e0e2(void)
{
    REGS;
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a3, a2\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e0e8:\n.option push\n.option norvc\nbleu a2,a4,.Lresident_arithmetic_helper_edge_6e0e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6df3e\n");
    __builtin_unreachable();
}

/* Original0x6E0EC..0x6E0F4. */
REGION void tsl9_resident_arithmetic_helper_block_6e0ec(void)
{
    REGS;
    a3 = a2 >> UINT32_C(0x00000008); LIVE;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e0f2:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e0f2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6df3e\n");
    __builtin_unreachable();
}

/* Original0x6E0F4..0x6E12E. */
REGION void tsl9_resident_arithmetic_helper_block_6e0f4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsll a7, a7, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsrl a2, a1, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t5, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu t3, a2, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a4, a1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsrl a3, a0, a3\n.option pop\n");
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option norvc\nslli t4, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t4, t4, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsll t1, a0, a5\n.option pop\n");
    a1 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nremu a3, a2, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a5, t4, t3\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 | a1; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e12a:\n.option push\n.option norvc\nbleu a5,a3,.Lresident_arithmetic_helper_edge_6e12a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e140\n");
    __builtin_unreachable();
}

/* Original0x6E12E..0x6E138. */
REGION void tsl9_resident_arithmetic_helper_block_6e12e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a3, a3, a7\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, t3, -1\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e134:\n.option push\n.option norvc\nbltu a3,a7,.Lresident_arithmetic_helper_edge_6e134\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e29c\n");
    __builtin_unreachable();
}

/* Original0x6E138..0x6E13C. */
REGION void tsl9_resident_arithmetic_helper_block_6e138(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e138:\n.option push\n.option norvc\nbleu a5,a3,.Lresident_arithmetic_helper_edge_6e138\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e29c\n");
    __builtin_unreachable();
}

/* Original0x6E13C..0x6E140. */
REGION void tsl9_resident_arithmetic_helper_block_6e13c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi t3, t3, -2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a3, a3, a7\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E140..0x6E15E. */
REGION void tsl9_resident_arithmetic_helper_block_6e140(void)
{
    REGS;
    a3 = a3 - a5; LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a3, t5\n.option pop\n");
    a5 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nremu a3, a3, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, t4, a2\n.option pop\n");
    a4 = a3 << UINT32_C(0x00000010); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e15a:\n.option push\n.option norvc\nbleu a0,a4,.Lresident_arithmetic_helper_edge_6e15a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e170\n");
    __builtin_unreachable();
}

/* Original0x6E15E..0x6E168. */
REGION void tsl9_resident_arithmetic_helper_block_6e15e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a4, a4, a7\n.option pop\n");
    a5 = a2 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e164:\n.option push\n.option norvc\nbltu a4,a7,.Lresident_arithmetic_helper_edge_6e164\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e294\n");
    __builtin_unreachable();
}

/* Original0x6E168..0x6E16C. */
REGION void tsl9_resident_arithmetic_helper_block_6e168(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e168:\n.option push\n.option norvc\nbleu a0,a4,.Lresident_arithmetic_helper_edge_6e168\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e294\n");
    __builtin_unreachable();
}

/* Original0x6E16C..0x6E170. */
REGION void tsl9_resident_arithmetic_helper_block_6e16c(void)
{
    REGS;
    a2 = a2 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option rvc\nadd a4, a4, a7\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E170..0x6E17A. */
REGION void tsl9_resident_arithmetic_helper_block_6e170(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a1, t3, 0x10\n.option pop\n");
    a4 = a4 - a0; LIVE;
    a1 = a1 | a2; LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e178:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e178\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e01a\n");
    __builtin_unreachable();
}

/* Original0x6E17A..0x6E1BE. */
REGION void tsl9_resident_arithmetic_helper_block_6e17a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrl a5, a2, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a3, a3, t3\n.option pop\n");
    a3 = a3 | a5; LIVE;
    PORT(".option push\n.option norvc\nsrl t1, a1, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t5, a3, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a5, t1, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nslli t4, a3, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli t4, t4, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a6, a1, t3\n.option pop\n");
    PORT(".option push\n.option norvc\nsrl a4, a0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nor a6, a4, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a7, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a2, a2, t3\n.option pop\n");
    PORT(".option push\n.option norvc\nremu t1, t1, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a1, t4, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli t1, t1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nor a7, t1, a7\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e1ba:\n.option push\n.option norvc\nbleu a1,a7,.Lresident_arithmetic_helper_edge_6e1ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e1d0\n");
    __builtin_unreachable();
}

/* Original0x6E1BE..0x6E1C8. */
REGION void tsl9_resident_arithmetic_helper_block_6e1be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a7, a7, a3\n.option pop\n");
    a4 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e1c4:\n.option push\n.option norvc\nbltu a7,a3,.Lresident_arithmetic_helper_edge_6e1c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e298\n");
    __builtin_unreachable();
}

/* Original0x6E1C8..0x6E1CC. */
REGION void tsl9_resident_arithmetic_helper_block_6e1c8(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e1c8:\n.option push\n.option norvc\nbleu a1,a7,.Lresident_arithmetic_helper_edge_6e1c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e298\n");
    __builtin_unreachable();
}

/* Original0x6E1CC..0x6E1D0. */
REGION void tsl9_resident_arithmetic_helper_block_6e1cc(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option rvc\nadd a7, a7, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E1D0..0x6E1F0. */
REGION void tsl9_resident_arithmetic_helper_block_6e1d0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a7, a7, a1\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a4, a7, t5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli a6, a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a7, a7, t5\n.option pop\n");
    PORT(".option push\n.option norvc\nmul t1, t4, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nslli a7, a7, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nor a1, a7, a6\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e1ec:\n.option push\n.option norvc\nbleu t1,a1,.Lresident_arithmetic_helper_edge_6e1ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e202\n");
    __builtin_unreachable();
}

/* Original0x6E1F0..0x6E1FA. */
REGION void tsl9_resident_arithmetic_helper_block_6e1f0(void)
{
    REGS;
    a1 = a1 + a3; LIVE;
    PORT(".option push\n.option norvc\naddi a6, a4, -1\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e1f6:\n.option push\n.option norvc\nbltu a1,a3,.Lresident_arithmetic_helper_edge_6e1f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e290\n");
    __builtin_unreachable();
}

/* Original0x6E1FA..0x6E1FE. */
REGION void tsl9_resident_arithmetic_helper_block_6e1fa(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e1fa:\n.option push\n.option norvc\nbleu t1,a1,.Lresident_arithmetic_helper_edge_6e1fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e290\n");
    __builtin_unreachable();
}

/* Original0x6E1FE..0x6E202. */
REGION void tsl9_resident_arithmetic_helper_block_6e1fe(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    a1 = a1 + a3; LIVE;
    __builtin_unreachable();
}

/* Original0x6E202..0x6E238. */
REGION void tsl9_resident_arithmetic_helper_block_6e202(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nlui t5, 0x10\n.option pop\n");
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\naddi a4, t5, -1\n.option pop\n");
    a3 = a5 & a4; LIVE;
    PORT(".option push\n.option norvc\nsrli a7, a5, 0x10\n.option pop\n");
    a4 = a4 & a2; LIVE;
    a2 = a2 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nmul t4, a3, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a1, a1, t1\n.option pop\n");
    a3 = a3 * a2; LIVE;
    PORT(".option push\n.option norvc\nsrli a6, t4, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a4, a7, a4\n.option pop\n");
    a3 = a3 + a4; LIVE;
    PORT(".option push\n.option rvc\nadd a3, a3, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a2, a7, a2\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e234:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_arithmetic_helper_edge_6e234\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e23a\n");
    __builtin_unreachable();
}

/* Original0x6E238..0x6E23A. */
REGION void tsl9_resident_arithmetic_helper_block_6e238(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a2, a2, t5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E23A..0x6E244. */
REGION void tsl9_resident_arithmetic_helper_block_6e23a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a7, a3, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a2, a2, a7\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e240:\n.option push\n.option norvc\nbltu a1,a2,.Lresident_arithmetic_helper_edge_6e240\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e264\n");
    __builtin_unreachable();
}

/* Original0x6E244..0x6E248. */
REGION void tsl9_resident_arithmetic_helper_block_6e244(void)
{
    REGS;
    PORT(".Lresident_arithmetic_helper_edge_6e244:\n.option push\n.option norvc\nbeq a1,a2,.Lresident_arithmetic_helper_edge_6e244\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e24e\n");
    __builtin_unreachable();
}

/* Original0x6E248..0x6E24E. */
REGION void tsl9_resident_arithmetic_helper_block_6e248(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E24E..0x6E264. */
REGION void tsl9_resident_arithmetic_helper_block_6e24e(void)
{
    REGS;
    a4 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a3 = a3 & a4; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nand t4, t4, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a0, a0, t3\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a3, a3, t4\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e260:\n.option push\n.option norvc\nbleu a3,a0,.Lresident_arithmetic_helper_edge_6e260\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_arithmetic_helper_block_6e248\n");
    __builtin_unreachable();
}

/* Original0x6E264..0x6E26C. */
REGION void tsl9_resident_arithmetic_helper_block_6e264(void)
{
    REGS;
    a0 = a5 + UINT32_C(0xffffffff); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E26C..0x6E274. */
REGION void tsl9_resident_arithmetic_helper_block_6e26c(void)
{
    REGS;
    a4 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nli a6, 16\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e272:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e272\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e090\n");
    __builtin_unreachable();
}

/* Original0x6E274..0x6E27C. */
REGION void tsl9_resident_arithmetic_helper_block_6e274(void)
{
    REGS;
    a3 = a2 >> UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e27a:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e27a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6df3e\n");
    __builtin_unreachable();
}

/* Original0x6E27C..0x6E284. */
REGION void tsl9_resident_arithmetic_helper_block_6e27c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli a3, a7, 0x10\n.option pop\n");
    a5 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_arithmetic_helper_edge_6e282:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e282\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6dff2\n");
    __builtin_unreachable();
}

/* Original0x6E284..0x6E28A. */
REGION void tsl9_resident_arithmetic_helper_block_6e284(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6E28A..0x6E290. */
REGION void tsl9_resident_arithmetic_helper_block_6e28a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nli a6, 0\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e28e:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e28e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e090\n");
    __builtin_unreachable();
}

/* Original0x6E290..0x6E294. */
REGION void tsl9_resident_arithmetic_helper_block_6e290(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a6\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e292:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e292\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e202\n");
    __builtin_unreachable();
}

/* Original0x6E294..0x6E298. */
REGION void tsl9_resident_arithmetic_helper_block_6e294(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a5\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e296:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e296\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e170\n");
    __builtin_unreachable();
}

/* Original0x6E298..0x6E29C. */
REGION void tsl9_resident_arithmetic_helper_block_6e298(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e29a:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e29a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e1d0\n");
    __builtin_unreachable();
}

/* Original0x6E29C..0x6E2A0. */
REGION void tsl9_resident_arithmetic_helper_block_6e29c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv t3, a2\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e29e:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e29e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e140\n");
    __builtin_unreachable();
}

/* Original0x6E2A0..0x6E2A6. */
REGION void tsl9_resident_arithmetic_helper_block_6e2a0(void)
{
    REGS;
    a0 = a0 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option rvc\nadd a6, a6, a7\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e2a4:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e2a4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6df9c\n");
    __builtin_unreachable();
}

/* Original0x6E2A6..0x6E2AC. */
REGION void tsl9_resident_arithmetic_helper_block_6e2a6(void)
{
    REGS;
    a0 = a0 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, a7\n.option pop\n");
    PORT(".Lresident_arithmetic_helper_edge_6e2aa:\n.option push\n.option rvc\nc.j .Lresident_arithmetic_helper_edge_6e2aa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_arithmetic_helper_block_6e042\n");
    __builtin_unreachable();
}

ENTRY __attribute__((used,aligned(1),section(".rodata.tsl9_candidate_bitlength_table_6e95c"))) const uint8_t tsl9_candidate_bitlength_table_6e95c[256] = {0,1,2,2,3,3,3,3,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8};
