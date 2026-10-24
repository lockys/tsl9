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

/* Six complete original platform primitives:356B/134i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9290..0x929C. */
REGION void tsl9_main_services_provider_9290(void)
{
    REGS;
    a1 = a1 << UINT32_C(0x00000008); LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a0 = a0 ^ a1; LIVE;
    a5 = UINT32_C(0x00000009); LIVE;
    a4 = a4 + UINT32_C(0x00000021); LIVE;
    __builtin_unreachable();
}

/* Original0x929C..0x92A4. */
REGION void tsl9_platform_primitives_block_929c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lplatform_primitives_edge_92a2:\n.option push\n.option rvc\nc.bnez a5,.Lplatform_primitives_edge_92a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_platform_primitives_block_92a6\n");
    __builtin_unreachable();
}

/* Original0x92A4..0x92A6. */
REGION void tsl9_platform_primitives_block_92a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x92A6..0x92B2. */
REGION void tsl9_platform_primitives_block_92a6(void)
{
    REGS;
    a3 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a3, a3, 0x10\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000001); LIVE;
    PORT(".Lplatform_primitives_edge_92ae:\n.option push\n.option norvc\nbgez a3,.Lplatform_primitives_edge_92ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_platform_primitives_block_92b4\n");
    __builtin_unreachable();
}

/* Original0x92B2..0x92B4. */
REGION void tsl9_platform_primitives_block_92b2(void)
{
    REGS;
    a0 = a0 ^ a4; LIVE;
    __builtin_unreachable();
}

/* Original0x92B4..0x92BA. */
REGION void tsl9_platform_primitives_block_92b4(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lplatform_primitives_edge_92b8:\n.option push\n.option rvc\nc.j .Lplatform_primitives_edge_92b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_platform_primitives_block_929c\n");
    __builtin_unreachable();
}

/* Original0x18604..0x18622. */
REGION void tsl9_main_services_provider_18604(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 786\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000038); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18622..0x18630. */
REGION void tsl9_platform_primitives_block_18622(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18E1C..0x18E34. */
REGION void tsl9_main_services_provider_18e1c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nlw a6, 0(a0)\n.option pop\n");
    a1 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)); LIVE;
    a2 = UINT32_C(0x40010000); LIVE;
    a5 = a2 + UINT32_C(0x00000400); LIVE;
    a4 = a4 + a5; LIVE;
    PORT(".option push\n.option norvc\nnot a3, a6\n.option pop\n");
    PORT(".Lplatform_primitives_edge_18e32:\n.option push\n.option rvc\nc.beqz a1,.Lplatform_primitives_edge_18e32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_platform_primitives_block_18e7e\n");
    __builtin_unreachable();
}

/* Original0x18E34..0x18E66. */
REGION void tsl9_platform_primitives_block_18e34(void)
{
    REGS;
    a1 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000400)); LIVE;
    a1 = a1 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000400)) = (uint32_t)a1; LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 & a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nor a3, a3, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nnot a3, a4\n.option pop\n");
    a2 = a2 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a3 = a3 & a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    PORT(".Lplatform_primitives_edge_18e62:\n.option push\n.option norvc\nbne a3,a2,.Lplatform_primitives_edge_18e62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_platform_primitives_block_18e74\n");
    __builtin_unreachable();
}

/* Original0x18E66..0x18E74. */
REGION void tsl9_platform_primitives_block_18e66(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a3 = a3 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18E74..0x18E7E. */
REGION void tsl9_platform_primitives_block_18e74(void)
{
    REGS;
    a5 = a5 + a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18E7E..0x18E86. */
REGION void tsl9_platform_primitives_block_18e7e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1904A..0x19076. */
REGION void tsl9_main_services_provider_1904a(void)
{
    REGS;
    a4 = a1 & UINT32_C(0x000000fc); LIVE;
    a5 = a1 & UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x40010000); LIVE;
    a1 = a1 + a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nsll a4, a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a4, a4\n.option pop\n");
    a4 = a4 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nsll a0, a0, a5\n.option pop\n");
    a0 = a0 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x196C4..0x1971E. */
REGION void tsl9_main_services_provider_196c4(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x00003000); LIVE;
    a5 = a5 + UINT32_C(0x00000040); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000002)); LIVE;
    a4 = a4 & a5; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x0000000a)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x0000000e)); LIVE;
    a5 = a5 | a3; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)); LIVE;
    a5 = UINT32_C(0xfffff000); LIVE;
    a5 = a5 + UINT32_C(0x000007ff); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)) = (uint16_t)a5; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000010)); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1971E..0x19724. */
REGION void tsl9_main_services_provider_1971e(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lplatform_primitives_edge_19722:\n.option push\n.option rvc\nc.beqz a1,.Lplatform_primitives_edge_19722\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_platform_primitives_block_1972e\n");
    __builtin_unreachable();
}

/* Original0x19724..0x19728. */
REGION void tsl9_platform_primitives_block_19724(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    __builtin_unreachable();
}

/* Original0x19728..0x1972E. */
REGION void tsl9_platform_primitives_block_19728(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1972E..0x1973C. */
REGION void tsl9_platform_primitives_block_1972e(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0xffffffbf); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lplatform_primitives_edge_1973a:\n.option push\n.option rvc\nc.j .Lplatform_primitives_edge_1973a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_platform_primitives_block_19728\n");
    __builtin_unreachable();
}
