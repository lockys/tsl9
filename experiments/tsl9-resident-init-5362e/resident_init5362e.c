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

/* One complete required public-SDK initializer:426B/138i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x5362E..0x53658. */
REGION void tsl9_candidate_external_flash_5362e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000128); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 952\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e4)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".Lresident_init5362e_literal_53650:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_init5362e_literal_53650\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x53658..0x5365E. */
REGION void tsl9_resident_init5362e_block_53658(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_init5362e_edge_5365a:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_5365a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55bd4\n");
    __builtin_unreachable();
}

/* Original0x5365E..0x53664. */
REGION void tsl9_resident_init5362e_block_5365e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_init5362e_edge_53660:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_53660\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55c48\n");
    __builtin_unreachable();
}

/* Original0x53664..0x53702. */
REGION void tsl9_resident_init5362e_block_53664(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsb s0, 415(a5)\n.option pop\n");
    a5 = UINT32_C(0x07d70000); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s1, 952\n.option pop\n");
    a5 = a5 + UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 20(s0)\n.option pop\n");
    a5 = UINT32_C(0x0d0db000); LIVE;
    a5 = a5 + UINT32_C(0x00000131); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 24(s0)\n.option pop\n");
    a5 = UINT32_C(0x07d7b000); LIVE;
    a5 = a5 + UINT32_C(0x00000131); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 28(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffb000); LIVE;
    a5 = a5 + UINT32_C(0x00000131); LIVE;
    a4 = UINT32_C(0x0000001f); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 32(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01e\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a4, 224(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nlw a4, 208(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 228(s0)\n.option pop\n");
    a5 = UINT32_C(0x072d8000); LIVE;
    a5 = a5 + UINT32_C(0xfffff9ff); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 212(s0)\n.option pop\n");
    a3 = UINT32_C(0x00002000); LIVE;
    a3 = a3 + UINT32_C(0xfffffb9e); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\naddi s2, s2, 492\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 212(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 220(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 14(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a4, 208(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a4, 216(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 193(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 201(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 262(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 264(s0)\n.option pop\n");
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 266(s0)\n.option pop\n");
    a5 = UINT32_C(0x00001000); LIVE;
    a5 = a5 + UINT32_C(0xffffff0f); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc3e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5e\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 57(s0)\n.option pop\n");
    PORT(".Lresident_init5362e_edge_536fe:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_536fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e24\n");
    __builtin_unreachable();
}

/* Original0x53702..0x53740. */
REGION void tsl9_resident_init5362e_block_53702(void)
{
    REGS;
    a5 = UINT32_C(0x000001cc); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 126(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 63(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 4(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 16(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a0, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb028\n.option pop\n");
    a5 = a5 >> UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 137(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 66(s0)\n.option pop\n");
    a5 = UINT32_C(0x06071000); LIVE;
    a5 = a5 + UINT32_C(0x00000440); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 68(s0)\n.option pop\n");
    a3 = UINT32_C(0x000000fb); LIVE;
    PORT(".option push\n.option norvc\naddi a5, s1, 952\n.option pop\n");
    PORT(".Lresident_init5362e_edge_5373c:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_init5362e_edge_5373c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init5362e_block_53744\n");
    __builtin_unreachable();
}

/* Original0x53740..0x53744. */
REGION void tsl9_resident_init5362e_block_53740(void)
{
    REGS;
    a4 = UINT32_C(0x000000fb); LIVE;
    __builtin_unreachable();
}

/* Original0x53744..0x5375A. */
REGION void tsl9_resident_init5362e_block_53744(void)
{
    REGS;
    a1 = a4 << UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 42(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7ba\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 46(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7fa\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000003c)); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a2 = a1 + UINT32_C(0x0000000e); LIVE;
    a4 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_init5362e_edge_53758:\n.option push\n.option rvc\nc.beqz a4,.Lresident_init5362e_edge_53758\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_init5362e_block_537cc\n");
    __builtin_unreachable();
}

/* Original0x5375A..0x53760. */
REGION void tsl9_resident_init5362e_block_5375a(void)
{
    REGS;
    a4 = a1 + UINT32_C(0x0000008a); LIVE;
    a4 = a4 << UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x53760..0x5376E. */
REGION void tsl9_resident_init5362e_block_53760(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000003d)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 44(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7da\n.option pop\n");
    a3 = a3 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_init5362e_edge_5376c:\n.option push\n.option rvc\nc.beqz a3,.Lresident_init5362e_edge_5376c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_init5362e_block_537d2\n");
    __builtin_unreachable();
}

/* Original0x5376E..0x53774. */
REGION void tsl9_resident_init5362e_block_5376e(void)
{
    REGS;
    a3 = a1 + UINT32_C(0x0000008a); LIVE;
    a3 = a3 << UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x53774..0x53786. */
REGION void tsl9_resident_init5362e_block_53774(void)
{
    REGS;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 48(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xbb96\n.option pop\n");
    a0 = UINT32_C(0x0000001b); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, a1\n.option pop\n");
    PORT(".Lresident_init5362e_edge_53782:\n.option push\n.option norvc\nbleu a0,a1,.Lresident_init5362e_edge_53782\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init5362e_block_53788\n");
    __builtin_unreachable();
}

/* Original0x53786..0x53788. */
REGION void tsl9_resident_init5362e_block_53786(void)
{
    REGS;
    a3 = UINT32_C(0x0000001b); LIVE;
    __builtin_unreachable();
}

/* Original0x53788..0x53794. */
REGION void tsl9_resident_init5362e_block_53788(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a3, 34(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb0b6\n.option pop\n");
    a1 = UINT32_C(0x00000148); LIVE;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    PORT(".Lresident_init5362e_edge_53790:\n.option push\n.option norvc\nbleu a1,a4,.Lresident_init5362e_edge_53790\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_init5362e_block_53798\n");
    __builtin_unreachable();
}

/* Original0x53794..0x53798. */
REGION void tsl9_resident_init5362e_block_53794(void)
{
    REGS;
    a3 = UINT32_C(0x00000148); LIVE;
    __builtin_unreachable();
}

/* Original0x53798..0x537B6. */
REGION void tsl9_resident_init5362e_block_53798(void)
{
    REGS;
    a4 = UINT32_C(0x000001cc); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000040)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x00160000); LIVE;
    a2 = a2 << UINT32_C(0x00000003); LIVE;
    a4 = a4 + UINT32_C(0xfffff900); LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 36(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d6\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a2, 38(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3f2\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a3, 40(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb796\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000034)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_init5362e_edge_537b2:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_537b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_init_registers_64298\n");
    __builtin_unreachable();
}

/* Original0x537B6..0x537BA. */
REGION void tsl9_resident_init5362e_block_537b6(void)
{
    REGS;
    PORT(".Lresident_init5362e_edge_537b6:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_537b6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57ac4\n");
    __builtin_unreachable();
}

/* Original0x537BA..0x537BE. */
REGION void tsl9_resident_init5362e_block_537ba(void)
{
    REGS;
    PORT(".Lresident_init5362e_edge_537ba:\n.option push\n.option norvc\njal ra,.Lresident_init5362e_edge_537ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_63704\n");
    __builtin_unreachable();
}

/* Original0x537BE..0x537CC. */
REGION void tsl9_resident_init5362e_block_537be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_init5362e_edge_537c8:\n.option push\n.option norvc\njal zero,.Lresident_init5362e_edge_537c8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e758\n");
    __builtin_unreachable();
}

/* Original0x537CC..0x537D2. */
REGION void tsl9_resident_init5362e_block_537cc(void)
{
    REGS;
    a4 = a2 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_init5362e_edge_537d0:\n.option push\n.option rvc\nc.j .Lresident_init5362e_edge_537d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_init5362e_block_53760\n");
    __builtin_unreachable();
}

/* Original0x537D2..0x537D8. */
REGION void tsl9_resident_init5362e_block_537d2(void)
{
    REGS;
    a3 = a2 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_init5362e_edge_537d6:\n.option push\n.option rvc\nc.j .Lresident_init5362e_edge_537d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_init5362e_block_53774\n");
    __builtin_unreachable();
}
