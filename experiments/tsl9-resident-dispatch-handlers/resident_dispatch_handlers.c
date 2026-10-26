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

/* Four complete public-SDK handler/provider bodies:1118B/384i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x57DAE..0x57DD0. */
REGION void tsl9_candidate_external_flash_57dae(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s3, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s3, 1300\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_57dcc:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_dispatch_handlers_edge_57dcc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_57dd8\n");
    __builtin_unreachable();
}

/* Original0x57DD0..0x57DD8. */
REGION void tsl9_resident_dispatch_handlers_block_57dd0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30fc\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_57dd4:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_57dd4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_57df2\n");
    __builtin_unreachable();
}

/* Original0x57DD8..0x57DDC. */
REGION void tsl9_resident_dispatch_handlers_block_57dd8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x349c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_57dda:\n.option push\n.option rvc\nc.bnez a5,.Lresident_dispatch_handlers_edge_57dda\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_57de2\n");
    __builtin_unreachable();
}

/* Original0x57DDC..0x57DE2. */
REGION void tsl9_resident_dispatch_handlers_block_57ddc(void)
{
    REGS;
    a5 = UINT32_C(0x00000107); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa49e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57DE2..0x57DF2. */
REGION void tsl9_resident_dispatch_handlers_block_57de2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57DF2..0x57E04. */
REGION void tsl9_resident_dispatch_handlers_block_57df2(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlw s0, 1100(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_57e00:\n.option push\n.option norvc\njal ra,.Lresident_dispatch_handlers_edge_57e00\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63eda\n");
    __builtin_unreachable();
}

/* Original0x57E04..0x57E28. */
REGION void tsl9_resident_dispatch_handlers_block_57e04(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s2)\n.option pop\n");
    a5 = UINT32_C(0x8e89c000); LIVE;
    a5 = a5 + UINT32_C(0xfffffed6); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00555000); LIVE;
    a5 = a5 + UINT32_C(0x00000555); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 58(s0)\n.option pop\n");
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_57e24:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_dispatch_handlers_edge_57e24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_57e32\n");
    __builtin_unreachable();
}

/* Original0x57E28..0x57E32. */
REGION void tsl9_resident_dispatch_handlers_block_57e28(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 57(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 58(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57E32..0x57E3C. */
REGION void tsl9_resident_dispatch_handlers_block_57e32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 57(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_57e38:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_dispatch_handlers_edge_57e38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_57e44\n");
    __builtin_unreachable();
}

/* Original0x57E3C..0x57E44. */
REGION void tsl9_resident_dispatch_handlers_block_57e3c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 57(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x57E44..0x57E6C. */
REGION void tsl9_resident_dispatch_handlers_block_57e44(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1340(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000025); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0xffffffb2); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa07c\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 7(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb0fc\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s3)\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_57e68:\n.option push\n.option norvc\njal ra,.Lresident_dispatch_handlers_edge_57e68\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63c54\n");
    __builtin_unreachable();
}

/* Original0x57E6C..0x57E9C. */
REGION void tsl9_resident_dispatch_handlers_block_57e6c(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    PORT(".option push\n.option rvc\nmv s3, a4\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 5(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x305c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 1288(s2)\n.option pop\n");
    a3 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_57e9a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_57e9a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_57ea4\n");
    __builtin_unreachable();
}

/* Original0x57E9C..0x57EA4. */
REGION void tsl9_resident_dispatch_handlers_block_57e9c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004f0)); LIVE;
    __builtin_unreachable();
}

/* Original0x57EA4..0x57EAC. */
REGION void tsl9_resident_dispatch_handlers_block_57ea4(void)
{
    REGS;
    PORT(".Lresident_dispatch_handlers_literal_57ea4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_dispatch_handlers_literal_57ea4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57EAC..0x57EEA. */
REGION void tsl9_resident_dispatch_handlers_block_57eac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s2)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s4)\n.option pop\n");
    a4 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 5(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_dispatch_handlers_edge_57ee8:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_57ee8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_57de2\n");
    __builtin_unreachable();
}

/* Original0x6020A..0x6022C. */
REGION void tsl9_candidate_external_flash_6020a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s4, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s4, 1300\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_60228:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_dispatch_handlers_edge_60228\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_60234\n");
    __builtin_unreachable();
}

/* Original0x6022C..0x60234. */
REGION void tsl9_resident_dispatch_handlers_block_6022c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_60230:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_60230\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_6024e\n");
    __builtin_unreachable();
}

/* Original0x60234..0x60238. */
REGION void tsl9_resident_dispatch_handlers_block_60234(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_60236:\n.option push\n.option rvc\nc.bnez a5,.Lresident_dispatch_handlers_edge_60236\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_6023e\n");
    __builtin_unreachable();
}

/* Original0x60238..0x6023E. */
REGION void tsl9_resident_dispatch_handlers_block_60238(void)
{
    REGS;
    a5 = UINT32_C(0x00000106); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6023E..0x6024E. */
REGION void tsl9_resident_dispatch_handlers_block_6023e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6024E..0x60276. */
REGION void tsl9_resident_dispatch_handlers_block_6024e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s1, 1080(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a0 = UINT32_C(0x00000006); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_60272:\n.option push\n.option norvc\njal ra,.Lresident_dispatch_handlers_edge_60272\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63eda\n");
    __builtin_unreachable();
}

/* Original0x60276..0x6029A. */
REGION void tsl9_resident_dispatch_handlers_block_60276(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s3)\n.option pop\n");
    a5 = UINT32_C(0x8e89c000); LIVE;
    a5 = a5 + UINT32_C(0xfffffed6); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00555000); LIVE;
    a5 = a5 + UINT32_C(0x00000555); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 34(s1)\n.option pop\n");
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_60296:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_dispatch_handlers_edge_60296\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_602a4\n");
    __builtin_unreachable();
}

/* Original0x6029A..0x602A4. */
REGION void tsl9_resident_dispatch_handlers_block_6029a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 33(s1)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 34(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x602A4..0x602AE. */
REGION void tsl9_resident_dispatch_handlers_block_602a4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 33(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_602aa:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_dispatch_handlers_edge_602aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_602b0\n");
    __builtin_unreachable();
}

/* Original0x602AE..0x602B0. */
REGION void tsl9_resident_dispatch_handlers_block_602ae(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x602B0..0x602D4. */
REGION void tsl9_resident_dispatch_handlers_block_602b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1340(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000ff); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0xffffffa1); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4bc\n.option pop\n");
    a5 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s4)\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_602d0:\n.option push\n.option norvc\njal ra,.Lresident_dispatch_handlers_edge_602d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63c54\n");
    __builtin_unreachable();
}

/* Original0x602D4..0x60302. */
REGION void tsl9_resident_dispatch_handlers_block_602d4(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x349c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 1288(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a3 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_60300:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_60300\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_60312\n");
    __builtin_unreachable();
}

/* Original0x60302..0x60312. */
REGION void tsl9_resident_dispatch_handlers_block_60302(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004f8)); LIVE;
    PORT(".Lresident_dispatch_handlers_literal_6030a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_dispatch_handlers_literal_6030a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60312..0x60350. */
REGION void tsl9_resident_dispatch_handlers_block_60312(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s3)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s1)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a4 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_dispatch_handlers_edge_6034e:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_6034e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_6023e\n");
    __builtin_unreachable();
}

/* Original0x63C54..0x63C5E. */
REGION void tsl9_candidate_registers_63c54(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000050c)); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63c5c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_63c5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63c76\n");
    __builtin_unreachable();
}

/* Original0x63C5E..0x63C76. */
REGION void tsl9_resident_dispatch_handlers_block_63c5e(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nlw a6, 8(a5)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nor a4, a4, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x63C76..0x63C98. */
REGION void tsl9_resident_dispatch_handlers_block_63c76(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu a6, 1296(a4)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = a0 & UINT32_C(0x00000002); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    PORT(".option push\n.option norvc\nandi a6, a6, 1\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63c96:\n.option push\n.option rvc\nc.beqz a3,.Lresident_dispatch_handlers_edge_63c96\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63cfa\n");
    __builtin_unreachable();
}

/* Original0x63C98..0x63CDC. */
REGION void tsl9_resident_dispatch_handlers_block_63c98(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = UINT32_C(0xffffd000); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a3 = a3 & a0; LIVE;
    a0 = UINT32_C(0x00002000); LIVE;
    a3 = a3 | a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00090000); LIVE;
    a3 = a3 + UINT32_C(0x00000086); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x08302000); LIVE;
    a3 = a3 + UINT32_C(0xfffffff1); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00031000); LIVE;
    a3 = a3 + UINT32_C(0x00000619); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00003000); LIVE;
    a3 = a3 + UINT32_C(0xfffff8de); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000028)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x01006000); LIVE;
    a3 = a3 + UINT32_C(0x00000310); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x003fa000); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63cd8:\n.option push\n.option norvc\nbnez a6,.Lresident_dispatch_handlers_edge_63cd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63ce0\n");
    __builtin_unreachable();
}

/* Original0x63CDC..0x63CE0. */
REGION void tsl9_resident_dispatch_handlers_block_63cdc(void)
{
    REGS;
    a3 = UINT32_C(0x0034a000); LIVE;
    __builtin_unreachable();
}

/* Original0x63CE0..0x63CEC. */
REGION void tsl9_resident_dispatch_handlers_block_63ce0(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x000004df); LIVE;
    a1 = a1 << UINT32_C(0x00000007); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a3; LIVE;
    a1 = a1 + UINT32_C(0x00000364); LIVE;
    __builtin_unreachable();
}

/* Original0x63CEC..0x63CF0. */
REGION void tsl9_resident_dispatch_handlers_block_63cec(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63cee:\n.option push\n.option rvc\nc.beqz a2,.Lresident_dispatch_handlers_edge_63cee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63cf4\n");
    __builtin_unreachable();
}

/* Original0x63CF0..0x63CF4. */
REGION void tsl9_resident_dispatch_handlers_block_63cf0(void)
{
    REGS;
    a2 = a2 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x63CF4..0x63CFA. */
REGION void tsl9_resident_dispatch_handlers_block_63cf4(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63CFA..0x63D2E. */
REGION void tsl9_resident_dispatch_handlers_block_63cfa(void)
{
    REGS;
    a3 = UINT32_C(0x00090000); LIVE;
    a3 = a3 + UINT32_C(0x00000083); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x08102000); LIVE;
    a3 = a3 + UINT32_C(0xfffff901); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00031000); LIVE;
    a3 = a3 + UINT32_C(0x00000624); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00003000); LIVE;
    a3 = a3 + UINT32_C(0xfffff8be); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000028)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x01006000); LIVE;
    a3 = a3 + UINT32_C(0x00000310); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63d2a:\n.option push\n.option norvc\nbeqz a6,.Lresident_dispatch_handlers_edge_63d2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63d56\n");
    __builtin_unreachable();
}

/* Original0x63D2E..0x63D36. */
REGION void tsl9_resident_dispatch_handlers_block_63d2e(void)
{
    REGS;
    a3 = UINT32_C(0x003fa000); LIVE;
    a3 = a3 + UINT32_C(0x000002ce); LIVE;
    __builtin_unreachable();
}

/* Original0x63D36..0x63D4C. */
REGION void tsl9_resident_dispatch_handlers_block_63d36(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0xffffd000); LIVE;
    PORT(".option push\n.option norvc\naddi a6, a3, -1\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nli a7, 1\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nand a3, a3, a6\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63d48:\n.option push\n.option norvc\nbne a0,a7,.Lresident_dispatch_handlers_edge_63d48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63d60\n");
    __builtin_unreachable();
}

/* Original0x63D4C..0x63D50. */
REGION void tsl9_resident_dispatch_handlers_block_63d4c(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a1 = a1 << UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x63D50..0x63D56. */
REGION void tsl9_resident_dispatch_handlers_block_63d50(void)
{
    REGS;
    a1 = a1 + UINT32_C(0x0000003c); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63d54:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_63d54\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_63cec\n");
    __builtin_unreachable();
}

/* Original0x63D56..0x63D60. */
REGION void tsl9_resident_dispatch_handlers_block_63d56(void)
{
    REGS;
    a3 = UINT32_C(0x00322000); LIVE;
    a3 = a3 + UINT32_C(0x000002d0); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63d5e:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_63d5e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_63d36\n");
    __builtin_unreachable();
}

/* Original0x63D60..0x63D6A. */
REGION void tsl9_resident_dispatch_handlers_block_63d60(void)
{
    REGS;
    a0 = UINT32_C(0x00001000); LIVE;
    a3 = a3 | a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63d68:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_63d68\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_63d50\n");
    __builtin_unreachable();
}

/* Original0x63EDA..0x63F02. */
REGION void tsl9_candidate_registers_63eda(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f00:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_63f00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63f56\n");
    __builtin_unreachable();
}

/* Original0x63F02..0x63F18. */
REGION void tsl9_resident_dispatch_handlers_block_63f02(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f14:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_63f14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f28\n");
    __builtin_unreachable();
}

/* Original0x63F18..0x63F28. */
REGION void tsl9_resident_dispatch_handlers_block_63f18(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000550)); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63F28..0x63F2E. */
REGION void tsl9_resident_dispatch_handlers_block_63f28(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f2a:\n.option push\n.option norvc\nbne s1,a4,.Lresident_dispatch_handlers_edge_63f2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f6a\n");
    __builtin_unreachable();
}

/* Original0x63F2E..0x63F32. */
REGION void tsl9_resident_dispatch_handlers_block_63f2e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f30:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_63f30\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63f3c\n");
    __builtin_unreachable();
}

/* Original0x63F32..0x63F38. */
REGION void tsl9_resident_dispatch_handlers_block_63f32(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x241c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f34:\n.option push\n.option norvc\nbne a5,s1,.Lresident_dispatch_handlers_edge_63f34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f3c\n");
    __builtin_unreachable();
}

/* Original0x63F38..0x63F3C. */
REGION void tsl9_resident_dispatch_handlers_block_63f38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63F3C..0x63F44. */
REGION void tsl9_resident_dispatch_handlers_block_63f3c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f40:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_63f40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f4a\n");
    __builtin_unreachable();
}

/* Original0x63F44..0x63F4A. */
REGION void tsl9_resident_dispatch_handlers_block_63f44(void)
{
    REGS;
    a5 = UINT32_C(0x00000108); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63F4A..0x63F56. */
REGION void tsl9_resident_dispatch_handlers_block_63f4a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)0; LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f52:\n.option push\n.option norvc\njal ra,.Lresident_dispatch_handlers_edge_63f52\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x63F56..0x63F6A. */
REGION void tsl9_resident_dispatch_handlers_block_63f56(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63F6A..0x63F70. */
REGION void tsl9_resident_dispatch_handlers_block_63f6a(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f6c:\n.option push\n.option norvc\nbne s1,a5,.Lresident_dispatch_handlers_edge_63f6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f7e\n");
    __builtin_unreachable();
}

/* Original0x63F70..0x63F74. */
REGION void tsl9_resident_dispatch_handlers_block_63f70(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f72:\n.option push\n.option rvc\nc.beqz a5,.Lresident_dispatch_handlers_edge_63f72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63f3c\n");
    __builtin_unreachable();
}

/* Original0x63F74..0x63F7C. */
REGION void tsl9_resident_dispatch_handlers_block_63f74(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2418\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f78:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_63f78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f3c\n");
    __builtin_unreachable();
}

/* Original0x63F7C..0x63F7E. */
REGION void tsl9_resident_dispatch_handlers_block_63f7c(void)
{
    REGS;
    PORT(".Lresident_dispatch_handlers_edge_63f7c:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_63f7c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_63f38\n");
    __builtin_unreachable();
}

/* Original0x63F7E..0x63F84. */
REGION void tsl9_resident_dispatch_handlers_block_63f7e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3074\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f80:\n.option push\n.option norvc\nbeq a4,a3,.Lresident_dispatch_handlers_edge_63f80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f92\n");
    __builtin_unreachable();
}

/* Original0x63F84..0x63F8A. */
REGION void tsl9_resident_dispatch_handlers_block_63f84(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3078\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f86:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_dispatch_handlers_edge_63f86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f92\n");
    __builtin_unreachable();
}

/* Original0x63F8A..0x63F92. */
REGION void tsl9_resident_dispatch_handlers_block_63f8a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_dispatch_handlers_edge_63f8e:\n.option push\n.option norvc\nbne a4,a5,.Lresident_dispatch_handlers_edge_63f8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_dispatch_handlers_block_63f4a\n");
    __builtin_unreachable();
}

/* Original0x63F92..0x63F96. */
REGION void tsl9_resident_dispatch_handlers_block_63f92(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x341c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f94:\n.option push\n.option rvc\nc.bnez a5,.Lresident_dispatch_handlers_edge_63f94\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_dispatch_handlers_block_63f4a\n");
    __builtin_unreachable();
}

/* Original0x63F96..0x63FA0. */
REGION void tsl9_resident_dispatch_handlers_block_63f96(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41c\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    PORT(".Lresident_dispatch_handlers_edge_63f9e:\n.option push\n.option rvc\nc.j .Lresident_dispatch_handlers_edge_63f9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_dispatch_handlers_block_63f4a\n");
    __builtin_unreachable();
}
