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

/* Four complete conditional SDK slot3/record bodies:1892B/626i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x436A8..0x436CA. */
REGION void tsl9_candidate_external_flash_436a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_436c6:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_RAM_dependencies_edge_436c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_4371c\n");
    __builtin_unreachable();
}

/* Original0x436CA..0x436DE. */
REGION void tsl9_resident_task0_RAM_dependencies_block_436ca(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    a4 = a0 * a4; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000022c)); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_436dc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_RAM_dependencies_edge_436dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_4371c\n");
    __builtin_unreachable();
}

/* Original0x436DE..0x436F6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_436de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsll s0, s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_436ee:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_timer_lookup_20000314\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_436ee\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x436F6..0x436FA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_436f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_436f8:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_dependencies_edge_436f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_43704\n");
    __builtin_unreachable();
}

/* Original0x436FA..0x43700. */
REGION void tsl9_resident_task0_RAM_dependencies_block_436fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_436fe:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_dependencies_edge_436fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_clear_event_4358a\n");
    __builtin_unreachable();
}

/* Original0x43700..0x43704. */
REGION void tsl9_resident_task0_RAM_dependencies_block_43700(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 8(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43704..0x4370E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_43704(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4370E..0x4371C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_4370e(void)
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

/* Original0x4371C..0x43728. */
REGION void tsl9_resident_task0_RAM_dependencies_block_4371c(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_43726:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_43726\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_4370e\n");
    __builtin_unreachable();
}

/* Original0x20000D50..0x20000DA2. */
REGION void tsl9_candidate_external_ram_20000d50(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s3, 952\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 164(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 564\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x279e\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s2, 134(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 144(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s2, s2, a5\n.option pop\n");
    a5 = UINT32_C(0x000f4000); LIVE;
    a4 = a5 + UINT32_C(0x0000023f); LIVE;
    a5 = a5 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 952\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 564\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a4\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s2, s2, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000d9e:\n.option push\n.option norvc\nbltu a0,s2,.Lresident_task0_RAM_dependencies_edge_20000d9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000dd8\n");
    __builtin_unreachable();
}

/* Original0x20000DA2..0x20000DB0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000da2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub s2, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000DB0..0x20000DB4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000db0(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000db0:\n.option push\n.option norvc\nbltu s2,a0,.Lresident_task0_RAM_dependencies_edge_20000db0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000dde\n");
    __builtin_unreachable();
}

/* Original0x20000DB4..0x20000DBC. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000db4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s2, s2, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000db8:\n.option push\n.option norvc\nbltz s2,.Lresident_task0_RAM_dependencies_edge_20000db8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000de4\n");
    __builtin_unreachable();
}

/* Original0x20000DBC..0x20000DD2. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dbc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 31(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 320(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000dce:\n.option push\n.option norvc\nbnez a5,.Lresident_task0_RAM_dependencies_edge_20000dce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000ed6\n");
    __builtin_unreachable();
}

/* Original0x20000DD2..0x20000DD6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dd2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000dd4:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_dependencies_edge_20000dd4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_200014c6\n");
    __builtin_unreachable();
}

/* Original0x20000DD6..0x20000DD8. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dd6(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000dd6:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000dd6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000eda\n");
    __builtin_unreachable();
}

/* Original0x20000DD8..0x20000DDE. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    a0 = a0 + a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000ddc:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000ddc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000da2\n");
    __builtin_unreachable();
}

/* Original0x20000DDE..0x20000DE4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dde(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000de2:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000de2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000db4\n");
    __builtin_unreachable();
}

/* Original0x20000DE4..0x20000DEA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000de4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000DEA..0x20000DF2. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000dea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 136(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000dee:\n.option push\n.option norvc\nbltu a0,a4,.Lresident_task0_RAM_dependencies_edge_20000dee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e8c\n");
    __builtin_unreachable();
}

/* Original0x20000DF2..0x20000DF4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000df2(void)
{
    REGS;
    a0 = a0 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20000DF4..0x20000E0E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000df4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e0a:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_RAM_dependencies_edge_20000e0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e94\n");
    __builtin_unreachable();
}

/* Original0x20000E0E..0x20000E1A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s5, 0xf4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s6, s5, 575\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, s5, 576\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000E1A..0x20000E2A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e1a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 320(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e28:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_RAM_dependencies_edge_20000e28\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e2e\n");
    __builtin_unreachable();
}

/* Original0x20000E2A..0x20000E2E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e2a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e2c:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_dependencies_edge_20000e2c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_200014c6\n");
    __builtin_unreachable();
}

/* Original0x20000E2E..0x20000E38. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20000e30:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_56972\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20000e30\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000E38..0x20000E3C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e38(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e38:\n.option push\n.option norvc\nbnez a0,.Lresident_task0_RAM_dependencies_edge_20000e38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001092\n");
    __builtin_unreachable();
}

/* Original0x20000E3C..0x20000E4E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 144(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 140(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 4(s1)\n.option pop\n");
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e4a:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_task0_RAM_dependencies_edge_20000e4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e52\n");
    __builtin_unreachable();
}

/* Original0x20000E4E..0x20000E52. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e4e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e4e:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task0_RAM_dependencies_edge_20000e4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e56\n");
    __builtin_unreachable();
}

/* Original0x20000E52..0x20000E56. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e52(void)
{
    REGS;
    a0 = a5 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20000E56..0x20000E74. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e56(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s2, 134(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a0, 144(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc7c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249e\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s2, s2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, s6\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s2, s2, s5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e70:\n.option push\n.option norvc\nbltu a0,s2,.Lresident_task0_RAM_dependencies_edge_20000e70\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000ec8\n");
    __builtin_unreachable();
}

/* Original0x20000E74..0x20000E78. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e74(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s2, a0, s2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000E78..0x20000E7E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000E7E..0x20000E82. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e7e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e7e:\n.option push\n.option norvc\nbltu s2,a0,.Lresident_task0_RAM_dependencies_edge_20000e7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000ed0\n");
    __builtin_unreachable();
}

/* Original0x20000E82..0x20000E8A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s2, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e86:\n.option push\n.option norvc\nbltz a0,.Lresident_task0_RAM_dependencies_edge_20000e86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000e1a\n");
    __builtin_unreachable();
}

/* Original0x20000E8A..0x20000E8C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e8a(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e8a:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000e8a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000dbc\n");
    __builtin_unreachable();
}

/* Original0x20000E8C..0x20000E94. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e8c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    a5 = a5 - a4; LIVE;
    a0 = a0 + a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000e92:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000e92\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000df4\n");
    __builtin_unreachable();
}

/* Original0x20000E94..0x20000EA0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000e94(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20000e98:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_568f6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20000e98\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000EA0..0x20000EB0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ea0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 544(a5)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000eac:\n.option push\n.option norvc\nbeqz t1,.Lresident_task0_RAM_dependencies_edge_20000eac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001092\n");
    __builtin_unreachable();
}

/* Original0x20000EB0..0x20000EC8. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000eb0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000EC8..0x20000ED0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ec8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s2, a4, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000ece:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000ece\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000e78\n");
    __builtin_unreachable();
}

/* Original0x20000ED0..0x20000ED6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ed0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000ed4:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20000ed4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000e82\n");
    __builtin_unreachable();
}

/* Original0x20000ED6..0x20000EDA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ed6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000ed8:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_dependencies_edge_20000ed8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_2000156c\n");
    __builtin_unreachable();
}

/* Original0x20000EDA..0x20000EE4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000eda(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20000edc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_56972\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20000edc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000EE4..0x20000EE8. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ee4(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000ee4:\n.option push\n.option norvc\nbnez a0,.Lresident_task0_RAM_dependencies_edge_20000ee4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001092\n");
    __builtin_unreachable();
}

/* Original0x20000EE8..0x20000F14. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ee8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x248a\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 134(s0)\n.option pop\n");
    a3 = UINT32_C(0x000f4000); LIVE;
    a2 = a3 + UINT32_C(0x0000023f); LIVE;
    a5 = a5 * a0; LIVE;
    a3 = a3 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nlw a4, 144(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 54(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 4(s1)\n.option pop\n");
    a5 = a5 + a2; LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f10:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task0_RAM_dependencies_edge_20000f10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010a6\n");
    __builtin_unreachable();
}

/* Original0x20000F14..0x20000F18. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f14(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    __builtin_unreachable();
}

/* Original0x20000F18..0x20000F2C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f18(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 140(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 136(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s6, 0\n.option pop\n");
    a5 = a3 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv s2, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f28:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_task0_RAM_dependencies_edge_20000f28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f30\n");
    __builtin_unreachable();
}

/* Original0x20000F2C..0x20000F30. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f2c(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f2c:\n.option push\n.option norvc\nbltu a5,s5,.Lresident_task0_RAM_dependencies_edge_20000f2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f34\n");
    __builtin_unreachable();
}

/* Original0x20000F30..0x20000F34. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f30(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s2, a5, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F34..0x20000F3C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f34(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 32(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x301e\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s2, 144(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f3a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_RAM_dependencies_edge_20000f3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f8a\n");
    __builtin_unreachable();
}

/* Original0x20000F3C..0x20000F6E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a3, 64(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 36(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x305a\n.option pop\n");
    a2 = UINT32_C(0x000f4000); LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 36(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb056\n.option pop\n");
    a4 = a3 - a4; LIVE;
    a5 = a5 * a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 34(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x303a\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a0 = a5 * a0; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 34(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb03e\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20000f66:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6df1a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20000f66\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F6E..0x20000F70. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f6e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f6e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_dependencies_edge_20000f6e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f8a\n");
    __builtin_unreachable();
}

/* Original0x20000F70..0x20000F7E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f70(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd a0, a0, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu s2, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f7a:\n.option push\n.option norvc\nbne s6,s2,.Lresident_task0_RAM_dependencies_edge_20000f7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f82\n");
    __builtin_unreachable();
}

/* Original0x20000F7E..0x20000F82. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f7e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f7e:\n.option push\n.option norvc\nbltu a0,s5,.Lresident_task0_RAM_dependencies_edge_20000f7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f86\n");
    __builtin_unreachable();
}

/* Original0x20000F82..0x20000F86. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a5, a0, s5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F86..0x20000F8A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f86(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 144(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F8A..0x20000F90. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F90..0x20000F92. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F92..0x20000F98. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f92(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000F98..0x20000F9C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f98(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000f98:\n.option push\n.option norvc\nbeq a0,s2,.Lresident_task0_RAM_dependencies_edge_20000f98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20000f92\n");
    __builtin_unreachable();
}

/* Original0x20000F9C..0x20000FA6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000f9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 136(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000FA6..0x20000FAA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000fa6(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000fa6:\n.option push\n.option norvc\nbltu s2,a0,.Lresident_task0_RAM_dependencies_edge_20000fa6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010b0\n");
    __builtin_unreachable();
}

/* Original0x20000FAA..0x20000FB2. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000faa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s2, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20000fae:\n.option push\n.option norvc\nbeqz a0,.Lresident_task0_RAM_dependencies_edge_20000fae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010d2\n");
    __builtin_unreachable();
}

/* Original0x20000FB2..0x20000FDE. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000fb2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu s5, 8(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 134(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0xf4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s2, 575\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a5, a5, s5\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 576\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, s2\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000203)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20000fda:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_RAM_dependencies_edge_20000fda\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010d2\n");
    __builtin_unreachable();
}

/* Original0x20000FDE..0x20000FF6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000fde(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmulhu a1, a0, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s4, 34(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a0, a0, s2\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20000fee:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6df1a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20000fee\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000FF6..0x20001012. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20000ff6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd s6, s4, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s4, s5\n.option pop\n");
    a2 = UINT32_C(0x000f4000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_literal_2000100a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6df1a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_2000100a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001012..0x20001014. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001012(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001012:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_dependencies_edge_20001012\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001034\n");
    __builtin_unreachable();
}

/* Original0x20001014..0x2000102E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001014(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmulhu a5, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a1, s2, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s2, a0\n.option pop\n");
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_literal_20001026:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6df1a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20001026\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000102E..0x20001034. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000102e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s4, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a0, 34(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb02a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001034..0x2000103E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001034(void)
{
    REGS;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_literal_20001036:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_registers_63eda\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20001036\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000103E..0x2000104A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000103e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s0, 164(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3438\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001046:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_RAM_dependencies_edge_20001046\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010b6\n");
    __builtin_unreachable();
}

/* Original0x2000104A..0x20001058. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000104a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffd0); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004fc)); LIVE;
    __builtin_unreachable();
}

/* Original0x20001058..0x2000105C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001058(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000105a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_RAM_dependencies_edge_2000105a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010c6\n");
    __builtin_unreachable();
}

/* Original0x2000105C..0x20001060. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000105c(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000105c:\n.option push\n.option norvc\njal ra,.Lresident_task0_RAM_dependencies_edge_2000105c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_callback_set_2000078a\n");
    __builtin_unreachable();
}

/* Original0x20001060..0x20001092. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001060(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    a4 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3f8\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000053c)); LIVE;
    a3 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option rvc\nslli s6, s6, 0x1\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nsw s6, 100(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20001092..0x200010A6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001092(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200010A6..0x200010B0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010a6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a3, a4, s5\n.option pop\n");
    a5 = a3 - a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200010ae:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200010ae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000f18\n");
    __builtin_unreachable();
}

/* Original0x200010B0..0x200010B6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200010b4:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200010b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20000faa\n");
    __builtin_unreachable();
}

/* Original0x200010B6..0x200010C6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010b6(void)
{
    REGS;
    a5 = UINT32_C(0xffffffc1); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004f4)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200010c4:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200010c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001058\n");
    __builtin_unreachable();
}

/* Original0x200010C6..0x200010D0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010c6(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_literal_200010c8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_43b28\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_200010c8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200010D0..0x200010D2. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010d0(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_200010d0:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200010d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001060\n");
    __builtin_unreachable();
}

/* Original0x200010D2..0x200010DA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010d2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 164(s3)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200010d8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_RAM_dependencies_edge_200010d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200010f8\n");
    __builtin_unreachable();
}

/* Original0x200010DA..0x200010EA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010da(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004ec)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_literal_200010e2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_43ed2\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_200010e2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200010EA..0x200010F8. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010ea(void)
{
    REGS;
    a5 = UINT32_C(0xe000e000); LIVE;
    a4 = UINT32_C(0x02000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000204)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200010f6:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200010f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001092\n");
    __builtin_unreachable();
}

/* Original0x200010F8..0x20001122. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200010f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsll a1, a1, a5\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_2000111a:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_set_event_4354a\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_2000111a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001122..0x20001144. */
REGION void tsl9_candidate_external_ram_20001122(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 0(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 11(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3538\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 144(a0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001140:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_RAM_dependencies_edge_20001140\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_2000132a\n");
    __builtin_unreachable();
}

/* Original0x20001144..0x20001160. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001144(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000080)); LIVE;
    PORT(".option push\n.option norvc\nlhu s6, 60(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, s4, 564\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s5, 8(a3)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, 564\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000115c:\n.option push\n.option norvc\nbleu s6,a5,.Lresident_task0_RAM_dependencies_edge_2000115c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012fa\n");
    __builtin_unreachable();
}

/* Original0x20001160..0x20001166. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001160(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2914\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001162:\n.option push\n.option norvc\nbne a3,a4,.Lresident_task0_RAM_dependencies_edge_20001162\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012fa\n");
    __builtin_unreachable();
}

/* Original0x20001166..0x2000116E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001166(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000118)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000116a:\n.option push\n.option norvc\nbnez a4,.Lresident_task0_RAM_dependencies_edge_2000116a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012fa\n");
    __builtin_unreachable();
}

/* Original0x2000116E..0x20001176. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000116e(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a4)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001172:\n.option push\n.option norvc\nbnez a4,.Lresident_task0_RAM_dependencies_edge_20001172\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012fa\n");
    __builtin_unreachable();
}

/* Original0x20001176..0x2000117E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001176(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 15(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3574\n.option pop\n");
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000117a:\n.option push\n.option norvc\nbne a3,a4,.Lresident_task0_RAM_dependencies_edge_2000117a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012fa\n");
    __builtin_unreachable();
}

/* Original0x2000117E..0x200011C4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000117e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d2a\n.option pop\n");
    PORT(".option push\n.option norvc\nsub s6, s6, a5\n.option pop\n");
    a5 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option norvc\nmul a0, a0, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 148(s0)\n.option pop\n");
    a2 = UINT32_C(0x000f4000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 * a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000202)); LIVE;
    PORT(".option push\n.option norvc\ndivu s1, a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhu a1, s5, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s1, 134(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s5, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_200011bc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6df1a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_200011bc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200011C4..0x200011D4. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200011c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s3, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a0, s3, a0\n.option pop\n");
    a0 = a0 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv a4, s3\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 4(s4)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200011d2:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task0_RAM_dependencies_edge_200011d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200011d8\n");
    __builtin_unreachable();
}

/* Original0x200011D4..0x200011D8. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200011d4(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_200011d4:\n.option push\n.option norvc\nbltu s3,a5,.Lresident_task0_RAM_dependencies_edge_200011d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200011dc\n");
    __builtin_unreachable();
}

/* Original0x200011D8..0x200011DC. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200011d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a4, s3, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200011DC..0x20001200. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200011dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul s1, s1, s5\n.option pop\n");
    a3 = UINT32_C(0x000f4000); LIVE;
    a5 = a3 + UINT32_C(0x0000023f); LIVE;
    a3 = a3 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nsw a4, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s1, s1, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a5, s6, 0x1\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200011fc:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task0_RAM_dependencies_edge_200011fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012ee\n");
    __builtin_unreachable();
}

/* Original0x20001200..0x20001202. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001200(void)
{
    REGS;
    a4 = a4 - a5; LIVE;
    __builtin_unreachable();
}

/* Original0x20001202..0x20001206. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001202(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a4, 0(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001206..0x20001214. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001206(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 480(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001214..0x20001218. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001214(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001214:\n.option push\n.option norvc\nbltu s1,a0,.Lresident_task0_RAM_dependencies_edge_20001214\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001330\n");
    __builtin_unreachable();
}

/* Original0x20001218..0x20001220. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001218(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s1, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000121c:\n.option push\n.option norvc\nbgez a0,.Lresident_task0_RAM_dependencies_edge_2000121c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200012d6\n");
    __builtin_unreachable();
}

/* Original0x20001220..0x2000122E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001220(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s6, s6, 564\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000122E..0x20001236. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000122e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 0(s2)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001232:\n.option push\n.option norvc\nbltu a0,a4,.Lresident_task0_RAM_dependencies_edge_20001232\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_2000133c\n");
    __builtin_unreachable();
}

/* Original0x20001236..0x20001238. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001236(void)
{
    REGS;
    a0 = a0 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x20001238..0x20001254. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001238(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 8(s6)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001250:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_RAM_dependencies_edge_20001250\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001346\n");
    __builtin_unreachable();
}

/* Original0x20001254..0x20001260. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001254(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0xf4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, s4, 575\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, 576\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001260..0x20001270. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001260(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 320(s0)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000126e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_RAM_dependencies_edge_2000126e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001274\n");
    __builtin_unreachable();
}

/* Original0x20001270..0x20001274. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001270(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001272:\n.option push\n.option rvc\nc.jal .Lresident_task0_RAM_dependencies_edge_20001272\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_200014c6\n");
    __builtin_unreachable();
}

/* Original0x20001274..0x2000127E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001274(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_20001276:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_56972\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_20001276\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000127E..0x20001280. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000127e(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000127e:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task0_RAM_dependencies_edge_2000127e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001360\n");
    __builtin_unreachable();
}

/* Original0x20001280..0x20001294. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001280(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 144(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 140(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 4(s6)\n.option pop\n");
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001290:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_task0_RAM_dependencies_edge_20001290\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001298\n");
    __builtin_unreachable();
}

/* Original0x20001294..0x20001298. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001294(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001294:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task0_RAM_dependencies_edge_20001294\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_2000129c\n");
    __builtin_unreachable();
}

/* Original0x20001298..0x2000129C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001298(void)
{
    REGS;
    a0 = a5 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x2000129C..0x200012BC. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000129c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s1, 134(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a0, 144(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc7c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 8(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, s5\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s1, s1, s4\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200012b8:\n.option push\n.option norvc\nbltu a0,s1,.Lresident_task0_RAM_dependencies_edge_200012b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_2000137e\n");
    __builtin_unreachable();
}

/* Original0x200012BC..0x200012C0. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a0, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200012C0..0x200012CA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s1, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200012CA..0x200012CE. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012ca(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_200012ca:\n.option push\n.option norvc\nbltu s1,a0,.Lresident_task0_RAM_dependencies_edge_200012ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001386\n");
    __builtin_unreachable();
}

/* Original0x200012CE..0x200012D6. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, s1, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_200012d2:\n.option push\n.option norvc\nbltz a0,.Lresident_task0_RAM_dependencies_edge_200012d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001260\n");
    __builtin_unreachable();
}

/* Original0x200012D6..0x200012E2. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012d6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000203)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200012de:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_RAM_dependencies_edge_200012de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001362\n");
    __builtin_unreachable();
}

/* Original0x200012E2..0x200012EE. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012e2(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsw s0, 1116(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200012ec:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200012ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001362\n");
    __builtin_unreachable();
}

/* Original0x200012EE..0x200012FA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 4(s4)\n.option pop\n");
    a5 = a3 - a5; LIVE;
    a4 = a4 + a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200012f8:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_200012f8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001202\n");
    __builtin_unreachable();
}

/* Original0x200012FA..0x20001318. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200012fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 134(s0)\n.option pop\n");
    a4 = UINT32_C(0x000f4000); LIVE;
    PORT(".option push\n.option norvc\nmul s1, a5, s5\n.option pop\n");
    a5 = a4 + UINT32_C(0x0000023f); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, a4, 576\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu s1, a5, s1\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001314:\n.option push\n.option norvc\nbltu s3,s1,.Lresident_task0_RAM_dependencies_edge_20001314\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001322\n");
    __builtin_unreachable();
}

/* Original0x20001318..0x20001322. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001318(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, s3, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s1, 0(s2)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001320:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20001320\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001206\n");
    __builtin_unreachable();
}

/* Original0x20001322..0x2000132A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001322(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s3, s3, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001328:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20001328\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001318\n");
    __builtin_unreachable();
}

/* Original0x2000132A..0x20001330. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000132a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s3, 0(a1)\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000132e:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_2000132e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001206\n");
    __builtin_unreachable();
}

/* Original0x20001330..0x2000133C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001330(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000238)); LIVE;
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000133a:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_2000133a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001218\n");
    __builtin_unreachable();
}

/* Original0x2000133C..0x20001346. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000133c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s6)\n.option pop\n");
    a5 = a5 - a4; LIVE;
    a0 = a0 + a5; LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001344:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20001344\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001238\n");
    __builtin_unreachable();
}

/* Original0x20001346..0x20001352. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001346(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_2000134a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_568f6\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_2000134a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001352..0x20001360. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001352(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000135e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_RAM_dependencies_edge_2000135e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001376\n");
    __builtin_unreachable();
}

/* Original0x20001360..0x20001362. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001360(void)
{
    REGS;
    a0 = UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x20001362..0x20001376. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001362(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001376..0x2000137C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001376(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000137C..0x2000137E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000137c(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000137c:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_2000137c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001360\n");
    __builtin_unreachable();
}

/* Original0x2000137E..0x20001386. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000137e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a4, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a0\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001384:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_20001384\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_200012c0\n");
    __builtin_unreachable();
}

/* Original0x20001386..0x2000138E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001386(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s6)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_2000138c:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_2000138c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_200012ce\n");
    __builtin_unreachable();
}

/* Original0x200014C6..0x200014F2. */
REGION void tsl9_candidate_external_ram_200014c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000035)); LIVE;
    PORT(".option push\n.option norvc\nlbu s0, 311(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    a5 = UINT32_C(0x00000024); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_200014ee:\n.option push\n.option norvc\nbleu s0,a5,.Lresident_task0_RAM_dependencies_edge_200014ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_200014fa\n");
    __builtin_unreachable();
}

/* Original0x200014F2..0x200014FA. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200014f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, -37\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200014FA..0x20001514. */
REGION void tsl9_resident_task0_RAM_dependencies_block_200014fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s4, 312(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 316(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 311(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_2000150c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6dec2\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_2000150c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001514..0x20001518. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001514(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001516:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task0_RAM_dependencies_edge_20001516\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001542\n");
    __builtin_unreachable();
}

/* Original0x20001518..0x20001528. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001518(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s6, 301(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nremu s6, s0, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nli s7, 37\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001528..0x20001536. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001528(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_literal_2000152e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6dec2\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_RAM_dependencies_literal_2000152e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001536..0x2000153A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001536(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_RAM_dependencies_edge_20001538:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_RAM_dependencies_edge_20001538\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001564\n");
    __builtin_unreachable();
}

/* Original0x2000153A..0x2000153E. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000153a(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000153a:\n.option push\n.option norvc\nbne s3,s6,.Lresident_task0_RAM_dependencies_edge_2000153a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_2000155c\n");
    __builtin_unreachable();
}

/* Original0x2000153E..0x20001542. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000153e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s0, s2, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001542..0x2000155C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001542(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 310(s1)\n.option pop\n");
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

/* Original0x2000155C..0x20001564. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000155c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s3, s3, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s3, s3, 0x18\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai s3, s3, 0x18\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001564..0x2000156A. */
REGION void tsl9_resident_task0_RAM_dependencies_block_20001564(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    PORT(".Lresident_task0_RAM_dependencies_edge_20001566:\n.option push\n.option norvc\nbne s2,s7,.Lresident_task0_RAM_dependencies_edge_20001566\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_RAM_dependencies_block_20001528\n");
    __builtin_unreachable();
}

/* Original0x2000156A..0x2000156C. */
REGION void tsl9_resident_task0_RAM_dependencies_block_2000156a(void)
{
    REGS;
    PORT(".Lresident_task0_RAM_dependencies_edge_2000156a:\n.option push\n.option rvc\nc.j .Lresident_task0_RAM_dependencies_edge_2000156a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_RAM_dependencies_block_20001542\n");
    __builtin_unreachable();
}
