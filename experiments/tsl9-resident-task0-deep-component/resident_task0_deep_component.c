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

/* Six complete conditional SDK slot3/record bodies:2130B/713i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x435CE..0x435FA. */
REGION void tsl9_candidate_external_flash_435ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    a4 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(a4)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a4 = a0 + UINT32_C(0xfffffff0); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lresident_task0_deep_component_edge_435f6:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task0_deep_component_edge_435f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_4369c\n");
    __builtin_unreachable();
}

/* Original0x435FA..0x4360E. */
REGION void tsl9_resident_task0_deep_component_block_435fa(void)
{
    REGS;
    a3 = UINT32_C(0x0000000c); LIVE;
    a3 = a0 * a3; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000022c)); LIVE;
    a4 = a4 + a3; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_4360c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_4360c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_4369c\n");
    __builtin_unreachable();
}

/* Original0x4360E..0x4362E. */
REGION void tsl9_resident_task0_deep_component_block_4360e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrli s1, a0, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    a0 = a0 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nsll a0, s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s0, a0, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".Lresident_task0_deep_component_literal_43626:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_timer_lookup_20000314\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_deep_component_literal_43626\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4362E..0x43632. */
REGION void tsl9_resident_task0_deep_component_block_4362e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s4, a0\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_43630:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_deep_component_edge_43630\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_43682\n");
    __builtin_unreachable();
}

/* Original0x43632..0x43638. */
REGION void tsl9_resident_task0_deep_component_block_43632(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_43636:\n.option push\n.option rvc\nc.jal .Lresident_task0_deep_component_edge_43636\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_clear_event_4358a\n");
    __builtin_unreachable();
}

/* Original0x43638..0x4364A. */
REGION void tsl9_resident_task0_deep_component_block_43638(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 564\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4364A..0x4366A. */
REGION void tsl9_resident_task0_deep_component_block_4364a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249e\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a1, a5, s3\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    PORT(".option push\n.option norvc\nmulhu a5, a5, s3\n.option pop\n");
    a0 = a1 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a1, a0, a1\n.option pop\n");
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_task0_deep_component_edge_43666:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_43666\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x4366A..0x43676. */
REGION void tsl9_resident_task0_deep_component_block_4366a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a5, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a3, 4(s1)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_43672:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_task0_deep_component_edge_43672\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_4367a\n");
    __builtin_unreachable();
}

/* Original0x43676..0x4367A. */
REGION void tsl9_resident_task0_deep_component_block_43676(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_43676:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_task0_deep_component_edge_43676\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_4367e\n");
    __builtin_unreachable();
}

/* Original0x4367A..0x4367E. */
REGION void tsl9_resident_task0_deep_component_block_4367a(void)
{
    REGS;
    a4 = a5 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x4367E..0x43682. */
REGION void tsl9_resident_task0_deep_component_block_4367e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a4, 8(s4)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43682..0x4368C. */
REGION void tsl9_resident_task0_deep_component_block_43682(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4368C..0x4369C. */
REGION void tsl9_resident_task0_deep_component_block_4368c(void)
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

/* Original0x4369C..0x436A8. */
REGION void tsl9_resident_task0_deep_component_block_4369c(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_436a6:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_436a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_4368c\n");
    __builtin_unreachable();
}

/* Original0x55DEA..0x55DF8. */
REGION void tsl9_candidate_external_flash_55dea(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000146)); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55df4:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task0_deep_component_edge_55df4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55e30\n");
    __builtin_unreachable();
}

/* Original0x55DF8..0x55E02. */
REGION void tsl9_resident_task0_deep_component_block_55df8(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000148)); LIVE;
    a5 = a5 + UINT32_C(0xfffffe88); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e00:\n.option push\n.option rvc\nc.beqz a3,.Lresident_task0_deep_component_edge_55e00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_55e0e\n");
    __builtin_unreachable();
}

/* Original0x55E02..0x55E0A. */
REGION void tsl9_resident_task0_deep_component_block_55e02(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    __builtin_unreachable();
}

/* Original0x55E0A..0x55E0E. */
REGION void tsl9_resident_task0_deep_component_block_55e0a(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e0c:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_55e0c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_55e18\n");
    __builtin_unreachable();
}

/* Original0x55E0E..0x55E18. */
REGION void tsl9_resident_task0_deep_component_block_55e0e(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    __builtin_unreachable();
}

/* Original0x55E18..0x55E28. */
REGION void tsl9_resident_task0_deep_component_block_55e18(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e4)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e24:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_task0_deep_component_edge_55e24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55e2a\n");
    __builtin_unreachable();
}

/* Original0x55E28..0x55E2A. */
REGION void tsl9_resident_task0_deep_component_block_55e28(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55E2A..0x55E30. */
REGION void tsl9_resident_task0_deep_component_block_55e2a(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004e)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55E30..0x55E36. */
REGION void tsl9_resident_task0_deep_component_block_55e30(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e32:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task0_deep_component_edge_55e32\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55e3e\n");
    __builtin_unreachable();
}

/* Original0x55E36..0x55E3E. */
REGION void tsl9_resident_task0_deep_component_block_55e36(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffbc); LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e3c:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_55e3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_55e18\n");
    __builtin_unreachable();
}

/* Original0x55E3E..0x55E44. */
REGION void tsl9_resident_task0_deep_component_block_55e3e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffb0); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55e42:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_55e42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_55e0a\n");
    __builtin_unreachable();
}

/* Original0x55F94..0x55FA4. */
REGION void tsl9_candidate_external_flash_55f94(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d6)); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001da)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_55fa0:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_task0_deep_component_edge_55fa0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55fa6\n");
    __builtin_unreachable();
}

/* Original0x55FA4..0x55FA6. */
REGION void tsl9_resident_task0_deep_component_block_55fa4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55FA6..0x55FB6. */
REGION void tsl9_resident_task0_deep_component_block_55fa6(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000146)); LIVE;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55fb2:\n.option push\n.option norvc\nbne a2,a3,.Lresident_task0_deep_component_edge_55fb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56028\n");
    __builtin_unreachable();
}

/* Original0x55FB6..0x55FC0. */
REGION void tsl9_resident_task0_deep_component_block_55fb6(void)
{
    REGS;
    a3 = UINT32_C(0x00001000); LIVE;
    a3 = a3 + UINT32_C(0xfffffa90); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55fbc:\n.option push\n.option norvc\nbleu a3,a4,.Lresident_task0_deep_component_edge_55fbc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55fc2\n");
    __builtin_unreachable();
}

/* Original0x55FC0..0x55FC2. */
REGION void tsl9_resident_task0_deep_component_block_55fc0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55FC2..0x55FC8. */
REGION void tsl9_resident_task0_deep_component_block_55fc2(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x55FC8..0x55FD0. */
REGION void tsl9_resident_task0_deep_component_block_55fc8(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55fcc:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_task0_deep_component_edge_55fcc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55fda\n");
    __builtin_unreachable();
}

/* Original0x55FD0..0x55FDA. */
REGION void tsl9_resident_task0_deep_component_block_55fd0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)) = (uint16_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000007c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x55FDA..0x55FE6. */
REGION void tsl9_resident_task0_deep_component_block_55fda(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001d2)); LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001de)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55fe2:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_task0_deep_component_edge_55fe2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55fe8\n");
    __builtin_unreachable();
}

/* Original0x55FE6..0x55FE8. */
REGION void tsl9_resident_task0_deep_component_block_55fe6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x55FE8..0x55FF8. */
REGION void tsl9_resident_task0_deep_component_block_55fe8(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000147)); LIVE;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55ff4:\n.option push\n.option norvc\nbne a2,a3,.Lresident_task0_deep_component_edge_55ff4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56042\n");
    __builtin_unreachable();
}

/* Original0x55FF8..0x56002. */
REGION void tsl9_resident_task0_deep_component_block_55ff8(void)
{
    REGS;
    a3 = UINT32_C(0x00001000); LIVE;
    a3 = a3 + UINT32_C(0xfffffa90); LIVE;
    PORT(".Lresident_task0_deep_component_edge_55ffe:\n.option push\n.option norvc\nbleu a3,a4,.Lresident_task0_deep_component_edge_55ffe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56004\n");
    __builtin_unreachable();
}

/* Original0x56002..0x56004. */
REGION void tsl9_resident_task0_deep_component_block_56002(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56004..0x5600A. */
REGION void tsl9_resident_task0_deep_component_block_56004(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x5600A..0x56012. */
REGION void tsl9_resident_task0_deep_component_block_5600a(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_5600e:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_task0_deep_component_edge_5600e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_5601c\n");
    __builtin_unreachable();
}

/* Original0x56012..0x5601C. */
REGION void tsl9_resident_task0_deep_component_block_56012(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)) = (uint16_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000007c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5601C..0x56020. */
REGION void tsl9_resident_task0_deep_component_block_5601c(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_5601c:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_5601c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55dea\n");
    __builtin_unreachable();
}

/* Original0x56020..0x56028. */
REGION void tsl9_resident_task0_deep_component_block_56020(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56028..0x56032. */
REGION void tsl9_resident_task0_deep_component_block_56028(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a2 = a5 + UINT32_C(0xfffff848); LIVE;
    PORT(".Lresident_task0_deep_component_edge_5602e:\n.option push\n.option norvc\nbleu a4,a2,.Lresident_task0_deep_component_edge_5602e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_55fc8\n");
    __builtin_unreachable();
}

/* Original0x56032..0x5603E. */
REGION void tsl9_resident_task0_deep_component_block_56032(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000100)); LIVE;
    a5 = a5 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 & a3; LIVE;
    PORT(".Lresident_task0_deep_component_edge_5603c:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_deep_component_edge_5603c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_55fc8\n");
    __builtin_unreachable();
}

/* Original0x5603E..0x56042. */
REGION void tsl9_resident_task0_deep_component_block_5603e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a2\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56040:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56040\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_55fc8\n");
    __builtin_unreachable();
}

/* Original0x56042..0x5604C. */
REGION void tsl9_resident_task0_deep_component_block_56042(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a2 = a5 + UINT32_C(0xfffff848); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56048:\n.option push\n.option norvc\nbleu a4,a2,.Lresident_task0_deep_component_edge_56048\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_5600a\n");
    __builtin_unreachable();
}

/* Original0x5604C..0x56058. */
REGION void tsl9_resident_task0_deep_component_block_5604c(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000100)); LIVE;
    a5 = a5 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 & a3; LIVE;
    PORT(".Lresident_task0_deep_component_edge_56056:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_deep_component_edge_56056\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_5600a\n");
    __builtin_unreachable();
}

/* Original0x56058..0x5605C. */
REGION void tsl9_resident_task0_deep_component_block_56058(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a2\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_5605a:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_5605a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_5600a\n");
    __builtin_unreachable();
}

/* Original0x5627A..0x56294. */
REGION void tsl9_candidate_external_flash_5627a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 180(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56290:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_task0_deep_component_edge_56290\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_562d6\n");
    __builtin_unreachable();
}

/* Original0x56294..0x562C2. */
REGION void tsl9_resident_task0_deep_component_block_56294(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)); LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a5 = a5 + a0; LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000023c)); LIVE;
    a5 = a5 + UINT32_C(0x00000271); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nmulhsu a1, a5, a0\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 * a5; LIVE;
    PORT(".Lresident_task0_deep_component_edge_562be:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_562be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x562C2..0x562D2. */
REGION void tsl9_resident_task0_deep_component_block_562c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 85(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a7, 156(s1)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    a2 = a2 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nli t1, 40\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x562D2..0x562D6. */
REGION void tsl9_resident_task0_deep_component_block_562d2(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_562d2:\n.option push\n.option norvc\nbltu a3,a2,.Lresident_task0_deep_component_edge_562d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_562e0\n");
    __builtin_unreachable();
}

/* Original0x562D6..0x562E0. */
REGION void tsl9_resident_task0_deep_component_block_562d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x562E0..0x562EE. */
REGION void tsl9_resident_task0_deep_component_block_562e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a4, a3, t1\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 144(s0)\n.option pop\n");
    a1 = UINT32_C(0xffffffff); LIVE;
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option rvc\nmv a5, a7\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x562EE..0x562F0. */
REGION void tsl9_resident_task0_deep_component_block_562ee(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_562ee:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task0_deep_component_edge_562ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_562f6\n");
    __builtin_unreachable();
}

/* Original0x562F0..0x562F6. */
REGION void tsl9_resident_task0_deep_component_block_562f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a3, 86(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_562f4:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_562f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_562d6\n");
    __builtin_unreachable();
}

/* Original0x562F6..0x562FA. */
REGION void tsl9_resident_task0_deep_component_block_562f6(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_562f6:\n.option push\n.option norvc\nbne s0,a5,.Lresident_task0_deep_component_edge_562f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_562fe\n");
    __builtin_unreachable();
}

/* Original0x562FA..0x562FE. */
REGION void tsl9_resident_task0_deep_component_block_562fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_562fc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_562fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_562f0\n");
    __builtin_unreachable();
}

/* Original0x562FE..0x5630A. */
REGION void tsl9_resident_task0_deep_component_block_562fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw t3, 140(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a6, 140(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56306:\n.option push\n.option norvc\nbne t3,a6,.Lresident_task0_deep_component_edge_56306\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_5631a\n");
    __builtin_unreachable();
}

/* Original0x5630A..0x56316. */
REGION void tsl9_resident_task0_deep_component_block_5630a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a6, 144(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a1, a6, a4\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56312:\n.option push\n.option norvc\nbltu a4,a6,.Lresident_task0_deep_component_edge_56312\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_5631a\n");
    __builtin_unreachable();
}

/* Original0x56316..0x5631A. */
REGION void tsl9_resident_task0_deep_component_block_56316(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a1, a4, a6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5631A..0x5631E. */
REGION void tsl9_resident_task0_deep_component_block_5631a(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_5631a:\n.option push\n.option norvc\nbltu a1,a0,.Lresident_task0_deep_component_edge_5631a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56322\n");
    __builtin_unreachable();
}

/* Original0x5631E..0x56322. */
REGION void tsl9_resident_task0_deep_component_block_5631e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56320:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56320\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_562ee\n");
    __builtin_unreachable();
}

/* Original0x56322..0x56326. */
REGION void tsl9_resident_task0_deep_component_block_56322(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56324:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56324\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_562d2\n");
    __builtin_unreachable();
}

/* Original0x56972..0x56978. */
REGION void tsl9_candidate_external_flash_56972(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x253c\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56974:\n.option push\n.option norvc\nbeqz a5,.Lresident_task0_deep_component_edge_56974\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56cae\n");
    __builtin_unreachable();
}

/* Original0x56978..0x56998. */
REGION void tsl9_resident_task0_deep_component_block_56978(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000080)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000080)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 15(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x357c\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000018)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56996:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task0_deep_component_edge_56996\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_569be\n");
    __builtin_unreachable();
}

/* Original0x56998..0x569A2. */
REGION void tsl9_resident_task0_deep_component_block_56998(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_task0_deep_component_edge_5699e:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_task0_deep_component_edge_5699e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_569a6\n");
    __builtin_unreachable();
}

/* Original0x569A2..0x569A6. */
REGION void tsl9_resident_task0_deep_component_block_569a2(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task0_deep_component_edge_569a4:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_569a4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_569b4\n");
    __builtin_unreachable();
}

/* Original0x569A6..0x569AE. */
REGION void tsl9_resident_task0_deep_component_block_569a6(void)
{
    REGS;
    a1 = UINT32_C(0x0000003e); LIVE;
    PORT(".Lresident_task0_deep_component_edge_569aa:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_569aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x569AE..0x569B4. */
REGION void tsl9_resident_task0_deep_component_block_569ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x569B4..0x569BE. */
REGION void tsl9_resident_task0_deep_component_block_569b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x569BE..0x569C4. */
REGION void tsl9_resident_task0_deep_component_block_569be(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task0_deep_component_edge_569c2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task0_deep_component_edge_569c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56a1a\n");
    __builtin_unreachable();
}

/* Original0x569C4..0x569E2. */
REGION void tsl9_resident_task0_deep_component_block_569c4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 15(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb57c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 11(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3538\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)) = (uint8_t)0; LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_569de:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_deep_component_edge_569de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56a1a\n");
    __builtin_unreachable();
}

/* Original0x569E2..0x56A1A. */
REGION void tsl9_resident_task0_deep_component_block_569e2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d3e\n.option pop\n");
    a2 = UINT32_C(0x000004e2); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000094)); LIVE;
    a5 = a5 * a2; LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000202)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000037)); LIVE;
    a3 = a3 + UINT32_C(0x00000050); LIVE;
    a4 = a4 * a2; LIVE;
    a5 = a5 + a3; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000084)) = (uint16_t)a5; LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a5 = a5 + a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000082)) = (uint16_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x56A1A..0x56A20. */
REGION void tsl9_resident_task0_deep_component_block_56a1a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56a1e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56a1e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56ae8\n");
    __builtin_unreachable();
}

/* Original0x56A20..0x56A2C. */
REGION void tsl9_resident_task0_deep_component_block_56a20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 94(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 64(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56a28:\n.option push\n.option norvc\nbne a5,a4,.Lresident_task0_deep_component_edge_56a28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c74\n");
    __builtin_unreachable();
}

/* Original0x56A2C..0x56A60. */
REGION void tsl9_resident_task0_deep_component_block_56a2c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a1, 92(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 96(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 85(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a1, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc6e\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 55(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 86(s0)\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 56(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc1e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 90(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 564\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5e\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56a5c:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_56a5c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_435ce\n");
    __builtin_unreachable();
}

/* Original0x56A60..0x56A6C. */
REGION void tsl9_resident_task0_deep_component_block_56a60(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 11(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3438\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 128(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 56(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c1e\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56a68:\n.option push\n.option norvc\nbnez a4,.Lresident_task0_deep_component_edge_56a68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c1c\n");
    __builtin_unreachable();
}

/* Original0x56A6C..0x56A8E. */
REGION void tsl9_resident_task0_deep_component_block_56a6c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 4(s1)\n.option pop\n");
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 144(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000014); LIVE;
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56a8a:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task0_deep_component_edge_56a8a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56a92\n");
    __builtin_unreachable();
}

/* Original0x56A8E..0x56A92. */
REGION void tsl9_resident_task0_deep_component_block_56a8e(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_56a8e:\n.option push\n.option norvc\nbltu a4,a2,.Lresident_task0_deep_component_edge_56a8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56a96\n");
    __builtin_unreachable();
}

/* Original0x56A92..0x56A96. */
REGION void tsl9_resident_task0_deep_component_block_56a92(void)
{
    REGS;
    a3 = a4 - a2; LIVE;
    __builtin_unreachable();
}

/* Original0x56A96..0x56AA4. */
REGION void tsl9_resident_task0_deep_component_block_56a96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 88(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a3, 144(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc3e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c5c\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56aa2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56aa2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56aaa\n");
    __builtin_unreachable();
}

/* Original0x56AA4..0x56AAA. */
REGION void tsl9_resident_task0_deep_component_block_56aa4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56aa6:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_56aa6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5627a\n");
    __builtin_unreachable();
}

/* Original0x56AAA..0x56AE8. */
REGION void tsl9_resident_task0_deep_component_block_56aaa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3e\n.option pop\n");
    a3 = UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsh zero, 34(s0)\n.option pop\n");
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a5, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a3\n.option pop\n");
    a3 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option norvc\nsw a2, 140(s0)\n.option pop\n");
    a5 = a5 * a3; LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 32(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 36(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb05e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x347c\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb47c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56AE8..0x56AEE. */
REGION void tsl9_resident_task0_deep_component_block_56ae8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56aec:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56aec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56b36\n");
    __builtin_unreachable();
}

/* Original0x56AEE..0x56B02. */
REGION void tsl9_resident_task0_deep_component_block_56aee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 302(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    a3 = a4 - a5; LIVE;
    a2 = a3 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56afe:\n.option push\n.option norvc\nbltz a2,.Lresident_task0_deep_component_edge_56afe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c7e\n");
    __builtin_unreachable();
}

/* Original0x56B02..0x56B06. */
REGION void tsl9_resident_task0_deep_component_block_56b02(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_56b02:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_deep_component_edge_56b02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56b36\n");
    __builtin_unreachable();
}

/* Original0x56B06..0x56B26. */
REGION void tsl9_resident_task0_deep_component_block_56b06(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nli a6, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s0, 312\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 312(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a6, 316(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 296\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_task0_deep_component_literal_56b1e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_deep_component_literal_56b1e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56B26..0x56B2C. */
REGION void tsl9_resident_task0_deep_component_block_56b26(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56b28:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_56b28\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ad8\n");
    __builtin_unreachable();
}

/* Original0x56B2C..0x56B36. */
REGION void tsl9_resident_task0_deep_component_block_56b2c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 301(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56B36..0x56B3E. */
REGION void tsl9_resident_task0_deep_component_block_56b36(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56b3c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task0_deep_component_edge_56b3c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56baa\n");
    __builtin_unreachable();
}

/* Original0x56B3E..0x56B52. */
REGION void tsl9_resident_task0_deep_component_block_56b3e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a3, 332(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 64(s0)\n.option pop\n");
    a2 = a3 - a4; LIVE;
    a1 = a2 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56b4e:\n.option push\n.option norvc\nbltz a1,.Lresident_task0_deep_component_edge_56b4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c7e\n");
    __builtin_unreachable();
}

/* Original0x56B52..0x56B56. */
REGION void tsl9_resident_task0_deep_component_block_56b52(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_56b52:\n.option push\n.option norvc\nbne a3,a4,.Lresident_task0_deep_component_edge_56b52\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56baa\n");
    __builtin_unreachable();
}

/* Original0x56B56..0x56B60. */
REGION void tsl9_resident_task0_deep_component_block_56b56(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 330(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56b5e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56b5e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56b6e\n");
    __builtin_unreachable();
}

/* Original0x56B60..0x56B68. */
REGION void tsl9_resident_task0_deep_component_block_56b60(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56b64:\n.option push\n.option norvc\nbeqz a4,.Lresident_task0_deep_component_edge_56b64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c92\n");
    __builtin_unreachable();
}

/* Original0x56B68..0x56B6A. */
REGION void tsl9_resident_task0_deep_component_block_56b68(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x56B6A..0x56B6E. */
REGION void tsl9_resident_task0_deep_component_block_56b6a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 326(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56B6E..0x56B74. */
REGION void tsl9_resident_task0_deep_component_block_56b6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 331(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56b72:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56b72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56b82\n");
    __builtin_unreachable();
}

/* Original0x56B74..0x56B7C. */
REGION void tsl9_resident_task0_deep_component_block_56b74(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56b78:\n.option push\n.option norvc\nbeqz a4,.Lresident_task0_deep_component_edge_56b78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56ca0\n");
    __builtin_unreachable();
}

/* Original0x56B7C..0x56B7E. */
REGION void tsl9_resident_task0_deep_component_block_56b7c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x56B7E..0x56B82. */
REGION void tsl9_resident_task0_deep_component_block_56b7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 327(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56B82..0x56B88. */
REGION void tsl9_resident_task0_deep_component_block_56b82(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56b84:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_56b84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55f94\n");
    __builtin_unreachable();
}

/* Original0x56B88..0x56B8E. */
REGION void tsl9_resident_task0_deep_component_block_56b88(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 124(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56b8c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56b8c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56b9a\n");
    __builtin_unreachable();
}

/* Original0x56B8E..0x56B9A. */
REGION void tsl9_resident_task0_deep_component_block_56b8e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56B9A..0x56BAA. */
REGION void tsl9_resident_task0_deep_component_block_56b9a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 43(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000200); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56BAA..0x56BB2. */
REGION void tsl9_resident_task0_deep_component_block_56baa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x381c\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56bb0:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task0_deep_component_edge_56bb0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56be8\n");
    __builtin_unreachable();
}

/* Original0x56BB2..0x56BDA. */
REGION void tsl9_resident_task0_deep_component_block_56bb2(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000040c)); LIVE;
    a2 = UINT32_C(0x00000058); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2354\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000028)); LIVE;
    a3 = a3 * a2; LIVE;
    a4 = a4 + a3; LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 28(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2f56\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 64(s0)\n.option pop\n");
    a4 = a3 - a4; LIVE;
    a2 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56bd6:\n.option push\n.option norvc\nbltz a2,.Lresident_task0_deep_component_edge_56bd6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56be8\n");
    __builtin_unreachable();
}

/* Original0x56BDA..0x56BE2. */
REGION void tsl9_resident_task0_deep_component_block_56bda(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 332(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56bde:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task0_deep_component_edge_56bde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56be8\n");
    __builtin_unreachable();
}

/* Original0x56BE2..0x56BE8. */
REGION void tsl9_resident_task0_deep_component_block_56be2(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56BE8..0x56BF4. */
REGION void tsl9_resident_task0_deep_component_block_56be8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56bf0:\n.option push\n.option norvc\nbeqz a5,.Lresident_task0_deep_component_edge_56bf0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_569a2\n");
    __builtin_unreachable();
}

/* Original0x56BF4..0x56C00. */
REGION void tsl9_resident_task0_deep_component_block_56bf4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 70(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56bfc:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_deep_component_edge_56bfc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_569a2\n");
    __builtin_unreachable();
}

/* Original0x56C00..0x56C0A. */
REGION void tsl9_resident_task0_deep_component_block_56c00(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2818\n.option pop\n");
    a5 = UINT32_C(0x0000004a); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c06:\n.option push\n.option norvc\nbne a4,a5,.Lresident_task0_deep_component_edge_56c06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c0e\n");
    __builtin_unreachable();
}

/* Original0x56C0A..0x56C0E. */
REGION void tsl9_resident_task0_deep_component_block_56c0a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56C0E..0x56C1C. */
REGION void tsl9_resident_task0_deep_component_block_56c0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000400); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56c1a:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56c1a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_569a2\n");
    __builtin_unreachable();
}

/* Original0x56C1C..0x56C28. */
REGION void tsl9_resident_task0_deep_component_block_56c1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 398(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a2, 88(s0)\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c26:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task0_deep_component_edge_56c26\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56c42\n");
    __builtin_unreachable();
}

/* Original0x56C28..0x56C42. */
REGION void tsl9_resident_task0_deep_component_block_56c28(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a3, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 400(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c2e\n.option pop\n");
    a4 = a4 - a3; LIVE;
    a4 = a4 * a1; LIVE;
    PORT(".option push\n.option norvc\ndiv a4, a4, a2\n.option pop\n");
    a4 = a4 + a3; LIVE;
    PORT(".option push\n.option norvc\nsh a4, 400(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56C42..0x56C44. */
REGION void tsl9_resident_task0_deep_component_block_56c42(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_56c42:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56c42\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56c70\n");
    __builtin_unreachable();
}

/* Original0x56C44..0x56C64. */
REGION void tsl9_resident_task0_deep_component_block_56c44(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x249a\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a1, 4(s1)\n.option pop\n");
    a5 = a4 * a5; LIVE;
    a4 = UINT32_C(0x00000320); LIVE;
    a5 = a5 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 144(s0)\n.option pop\n");
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56c60:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_task0_deep_component_edge_56c60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c68\n");
    __builtin_unreachable();
}

/* Original0x56C64..0x56C68. */
REGION void tsl9_resident_task0_deep_component_block_56c64(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_56c64:\n.option push\n.option norvc\nbltu a4,a1,.Lresident_task0_deep_component_edge_56c64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56c6c\n");
    __builtin_unreachable();
}

/* Original0x56C68..0x56C6C. */
REGION void tsl9_resident_task0_deep_component_block_56c68(void)
{
    REGS;
    a3 = a4 - a1; LIVE;
    __builtin_unreachable();
}

/* Original0x56C6C..0x56C70. */
REGION void tsl9_resident_task0_deep_component_block_56c6c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a3, 144(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56C70..0x56C74. */
REGION void tsl9_resident_task0_deep_component_block_56c70(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a2, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc32\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56c72:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56c72\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_56aaa\n");
    __builtin_unreachable();
}

/* Original0x56C74..0x56C7E. */
REGION void tsl9_resident_task0_deep_component_block_56c74(void)
{
    REGS;
    a5 = a5 - a4; LIVE;
    a4 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c7a:\n.option push\n.option norvc\nbgez a4,.Lresident_task0_deep_component_edge_56c7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_56ae8\n");
    __builtin_unreachable();
}

/* Original0x56C7E..0x56C88. */
REGION void tsl9_resident_task0_deep_component_block_56c7e(void)
{
    REGS;
    a1 = UINT32_C(0x00000028); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56c84:\n.option push\n.option norvc\njal ra,.Lresident_task0_deep_component_edge_56c84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x56C88..0x56C92. */
REGION void tsl9_resident_task0_deep_component_block_56c88(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000028); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c90:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56c90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_569b4\n");
    __builtin_unreachable();
}

/* Original0x56C92..0x56C96. */
REGION void tsl9_resident_task0_deep_component_block_56c92(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c94:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56c94\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56c9a\n");
    __builtin_unreachable();
}

/* Original0x56C96..0x56C9A. */
REGION void tsl9_resident_task0_deep_component_block_56c96(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56c98:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56c98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_56b6a\n");
    __builtin_unreachable();
}

/* Original0x56C9A..0x56CA0. */
REGION void tsl9_resident_task0_deep_component_block_56c9a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 326(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56c9e:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56c9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_56b6e\n");
    __builtin_unreachable();
}

/* Original0x56CA0..0x56CA4. */
REGION void tsl9_resident_task0_deep_component_block_56ca0(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56ca2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task0_deep_component_edge_56ca2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_56ca8\n");
    __builtin_unreachable();
}

/* Original0x56CA4..0x56CA8. */
REGION void tsl9_resident_task0_deep_component_block_56ca4(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task0_deep_component_edge_56ca6:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56ca6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_56b7e\n");
    __builtin_unreachable();
}

/* Original0x56CA8..0x56CAE. */
REGION void tsl9_resident_task0_deep_component_block_56ca8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 327(s0)\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_56cac:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_56cac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_56b82\n");
    __builtin_unreachable();
}

/* Original0x56CAE..0x56CB2. */
REGION void tsl9_resident_task0_deep_component_block_56cae(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000156C..0x2000177A. */
REGION void tsl9_candidate_external_ram_2000156c(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000098)); LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    a3 = a5 >> UINT32_C(0x00000010); LIVE;
    a3 = a3 ^ a5; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    a2 = a2 ^ a3; LIVE;
    PORT(".option push\n.option norvc\nsrai a4, a2, 0x7\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a5, a2, 0x5\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".option push\n.option norvc\nsrai a5, a2, 0x3\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".option push\n.option norvc\nsrai a5, a2, 0x1\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = a2 << UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = a2 << UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = a2 << UINT32_C(0x00000005); LIVE;
    a1 = a2 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    a2 = a2 << UINT32_C(0x00000007); LIVE;
    a4 = a4 | a5; LIVE;
    a2 = a2 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".option push\n.option norvc\nsrai a5, a1, 0x5\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a2, a1, 0x3\n.option pop\n");
    a2 = a2 & UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    a5 = a5 | a2; LIVE;
    PORT(".option push\n.option norvc\nsrai a2, a1, 0x7\n.option pop\n");
    a5 = a5 | a2; LIVE;
    PORT(".option push\n.option norvc\nsrai a2, a1, 0x1\n.option pop\n");
    a2 = a2 & UINT32_C(0x00000008); LIVE;
    a5 = a5 | a2; LIVE;
    a2 = a1 << UINT32_C(0x00000001); LIVE;
    a2 = a2 & UINT32_C(0x00000010); LIVE;
    a5 = a5 | a2; LIVE;
    a2 = a1 << UINT32_C(0x00000003); LIVE;
    a2 = a2 & UINT32_C(0x00000020); LIVE;
    a5 = a5 | a2; LIVE;
    a2 = a1 << UINT32_C(0x00000005); LIVE;
    a2 = a2 & UINT32_C(0x00000040); LIVE;
    a1 = a1 << UINT32_C(0x00000007); LIVE;
    a5 = a5 | a2; LIVE;
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 | a1; LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a2 = UINT32_C(0x00000011); LIVE;
    a4 = a4 | a5; LIVE;
    a4 = a4 * a2; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s4, 312(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 316(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    a4 = a4 + a3; LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsrai a5, a4, 0x7\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a0, a4, 0x5\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = a5 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a4, 0x3\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000004); LIVE;
    a5 = a5 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a4, 0x1\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000008); LIVE;
    a5 = a5 | a0; LIVE;
    a0 = a4 << UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000010); LIVE;
    a5 = a5 | a0; LIVE;
    a0 = a4 << UINT32_C(0x00000003); LIVE;
    a0 = a0 & UINT32_C(0x00000020); LIVE;
    a5 = a5 | a0; LIVE;
    a0 = a4 << UINT32_C(0x00000005); LIVE;
    a1 = a4 >> UINT32_C(0x00000008); LIVE;
    a0 = a0 & UINT32_C(0x00000040); LIVE;
    a4 = a4 << UINT32_C(0x00000007); LIVE;
    a5 = a5 | a0; LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x3\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a4, a1, 0x5\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000004); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x7\n.option pop\n");
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x1\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000008); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000010); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000003); LIVE;
    a0 = a0 & UINT32_C(0x00000020); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000005); LIVE;
    a0 = a0 & UINT32_C(0x00000040); LIVE;
    a1 = a1 << UINT32_C(0x00000007); LIVE;
    a4 = a4 | a0; LIVE;
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 | a1; LIVE;
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a5 = a5 * a2; LIVE;
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    a5 = a5 + a3; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsrai a4, a5, 0x7\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a0, a5, 0x5\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a5, 0x3\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000004); LIVE;
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a5, 0x1\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000008); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a5 << UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000010); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a5 << UINT32_C(0x00000003); LIVE;
    a0 = a0 & UINT32_C(0x00000020); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a5 << UINT32_C(0x00000005); LIVE;
    a1 = a5 >> UINT32_C(0x00000008); LIVE;
    a0 = a0 & UINT32_C(0x00000040); LIVE;
    a5 = a5 << UINT32_C(0x00000007); LIVE;
    a4 = a4 | a0; LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x3\n.option pop\n");
    PORT(".option push\n.option norvc\nsrai a4, a1, 0x5\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000004); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x7\n.option pop\n");
    a4 = a4 | a0; LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a1, 0x1\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000008); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000010); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000003); LIVE;
    a0 = a0 & UINT32_C(0x00000020); LIVE;
    a4 = a4 | a0; LIVE;
    a0 = a1 << UINT32_C(0x00000005); LIVE;
    a0 = a0 & UINT32_C(0x00000040); LIVE;
    a1 = a1 << UINT32_C(0x00000007); LIVE;
    a4 = a4 | a0; LIVE;
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 | a1; LIVE;
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a5 = a5 * a2; LIVE;
    a2 = UINT32_C(0x00000025); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    a5 = a5 + a3; LIVE;
    a3 = a3 ^ a5; LIVE;
    PORT(".option push\n.option norvc\nslli s1, a3, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a2, s1, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s6, a2, 255\n.option pop\n");
    PORT(".Lresident_task0_deep_component_literal_20001772:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6dec2\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_deep_component_literal_20001772\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000177A..0x2000177E. */
REGION void tsl9_resident_task0_deep_component_block_2000177a(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task0_deep_component_edge_2000177c:\n.option push\n.option rvc\nc.bnez a0,.Lresident_task0_deep_component_edge_2000177c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_200017b6\n");
    __builtin_unreachable();
}

/* Original0x2000177E..0x20001790. */
REGION void tsl9_resident_task0_deep_component_block_2000177e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 301(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s1, a5, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nli s8, 37\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20001790..0x2000179E. */
REGION void tsl9_resident_task0_deep_component_block_20001790(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lresident_task0_deep_component_literal_20001796:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_flash_6dec2\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task0_deep_component_literal_20001796\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000179E..0x200017A6. */
REGION void tsl9_resident_task0_deep_component_block_2000179e(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nandi s7, s2, 255\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_200017a4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task0_deep_component_edge_200017a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task0_deep_component_block_200017b0\n");
    __builtin_unreachable();
}

/* Original0x200017A6..0x200017AA. */
REGION void tsl9_resident_task0_deep_component_block_200017a6(void)
{
    REGS;
    PORT(".Lresident_task0_deep_component_edge_200017a6:\n.option push\n.option norvc\nbeq s1,s3,.Lresident_task0_deep_component_edge_200017a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_200017d2\n");
    __builtin_unreachable();
}

/* Original0x200017AA..0x200017B0. */
REGION void tsl9_resident_task0_deep_component_block_200017aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s3, s3, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s3, s3, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200017B0..0x200017B6. */
REGION void tsl9_resident_task0_deep_component_block_200017b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s2, s2, 1\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_200017b2:\n.option push\n.option norvc\nbne s2,s8,.Lresident_task0_deep_component_edge_200017b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task0_deep_component_block_20001790\n");
    __builtin_unreachable();
}

/* Original0x200017B6..0x200017D2. */
REGION void tsl9_resident_task0_deep_component_block_200017b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s6, 310(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200017D2..0x200017D6. */
REGION void tsl9_resident_task0_deep_component_block_200017d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s6, s7\n.option pop\n");
    PORT(".Lresident_task0_deep_component_edge_200017d4:\n.option push\n.option rvc\nc.j .Lresident_task0_deep_component_edge_200017d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task0_deep_component_block_200017b6\n");
    __builtin_unreachable();
}
