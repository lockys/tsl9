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

/* Three complete public-SDK idle/helper bodies:518B/178i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x638EA..0x63944. */
REGION void tsl9_candidate_idle_register_block_638ea(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a3 = UINT32_C(0x00800000); LIVE;
    a2 = UINT32_C(0x80011000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a2 = a2 + UINT32_C(0xfffffec8); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x10000000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x000001d0); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000034)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000200)); LIVE;
    a3 = a4 << UINT32_C(0x00000019); LIVE;
    a3 = a3 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a2 = UINT32_C(0x82000000); LIVE;
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    a2 = a2 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 << UINT32_C(0x00000019); LIVE;
    a3 = a3 & a2; LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00090000); LIVE;
    a4 = a4 + UINT32_C(0x00000083); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6430E..0x6434A. */
REGION void tsl9_candidate_idle_register_block_6430e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0x0000008c); LIVE;
    a3 = UINT32_C(0x0000006c); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a4; LIVE;
    a2 = UINT32_C(0x0000003c); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000034)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000003c)) = (uint32_t)a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000044)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000538)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)) = (uint32_t)a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000074)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x0000f000); LIVE;
    a4 = a4 + UINT32_C(0x0000000f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000061A..0x2000064A. */
REGION void tsl9_candidate_external_ram_2000061a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 564\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 564\n.option pop\n");
    PORT(".Lresident_idle_service_edge_20000648:\n.option push\n.option rvc\nc.beqz a5,.Lresident_idle_service_edge_20000648\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_200006a6\n");
    __builtin_unreachable();
}

/* Original0x2000064A..0x20000658. */
REGION void tsl9_resident_idle_service_block_2000064a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000000b4)); LIVE;
    PORT(".Lresident_idle_service_edge_20000656:\n.option push\n.option rvc\nc.beqz a4,.Lresident_idle_service_edge_20000656\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_200006a6\n");
    __builtin_unreachable();
}

/* Original0x20000658..0x20000660. */
REGION void tsl9_resident_idle_service_block_20000658(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s1, 176(a5)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000065c:\n.option push\n.option norvc\nbeq s1,a0,.Lresident_idle_service_edge_2000065c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006a6\n");
    __builtin_unreachable();
}

/* Original0x20000660..0x20000672. */
REGION void tsl9_resident_idle_service_block_20000660(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x0000019c); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)); LIVE;
    PORT(".option push\n.option norvc\naddi s4, a5, 412\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000066e:\n.option push\n.option norvc\nbeq a4,a0,.Lresident_idle_service_edge_2000066e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_2000076c\n");
    __builtin_unreachable();
}

/* Original0x20000672..0x2000067C. */
REGION void tsl9_resident_idle_service_block_20000672(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 480(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000067C..0x20000680. */
REGION void tsl9_resident_idle_service_block_2000067c(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_2000067c:\n.option push\n.option norvc\nbltu s1,a0,.Lresident_idle_service_edge_2000067c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_20000766\n");
    __builtin_unreachable();
}

/* Original0x20000680..0x20000688. */
REGION void tsl9_resident_idle_service_block_20000680(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsub s1, s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000688..0x20000690. */
REGION void tsl9_resident_idle_service_block_20000688(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 16(s4)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000068c:\n.option push\n.option norvc\nbleu a4,s1,.Lresident_idle_service_edge_2000068c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_20000692\n");
    __builtin_unreachable();
}

/* Original0x20000690..0x20000692. */
REGION void tsl9_resident_idle_service_block_20000690(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000692..0x2000069E. */
REGION void tsl9_resident_idle_service_block_20000692(void)
{
    REGS;
    a5 = a4 + a0; LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a3, 4(s0)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000069a:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_idle_service_edge_2000069a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006a2\n");
    __builtin_unreachable();
}

/* Original0x2000069E..0x200006A2. */
REGION void tsl9_resident_idle_service_block_2000069e(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_2000069e:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_idle_service_edge_2000069e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006a6\n");
    __builtin_unreachable();
}

/* Original0x200006A2..0x200006A6. */
REGION void tsl9_resident_idle_service_block_200006a2(void)
{
    REGS;
    a0 = a5 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x200006A6..0x200006B4. */
REGION void tsl9_resident_idle_service_block_200006a6(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_200006b0:\n.option push\n.option norvc\nbne a5,a0,.Lresident_idle_service_edge_200006b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006ea\n");
    __builtin_unreachable();
}

/* Original0x200006B4..0x200006CA. */
REGION void tsl9_resident_idle_service_block_200006b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 412\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 16(s1)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".Lresident_idle_service_edge_200006c6:\n.option push\n.option norvc\nbne a4,a0,.Lresident_idle_service_edge_200006c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_20000770\n");
    __builtin_unreachable();
}

/* Original0x200006CA..0x200006CC. */
REGION void tsl9_resident_idle_service_block_200006ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200006CC..0x200006E2. */
REGION void tsl9_resident_idle_service_block_200006cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0xfe364000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc80); LIVE;
    a5 = a5 + a3; LIVE;
    a4 = a5 + a0; LIVE;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".Lresident_idle_service_edge_200006de:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_idle_service_edge_200006de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006e6\n");
    __builtin_unreachable();
}

/* Original0x200006E2..0x200006E6. */
REGION void tsl9_resident_idle_service_block_200006e2(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_200006e2:\n.option push\n.option norvc\nbltu a4,a3,.Lresident_idle_service_edge_200006e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006ea\n");
    __builtin_unreachable();
}

/* Original0x200006E6..0x200006EA. */
REGION void tsl9_resident_idle_service_block_200006e6(void)
{
    REGS;
    a0 = a4 - a3; LIVE;
    __builtin_unreachable();
}

/* Original0x200006EA..0x200006FA. */
REGION void tsl9_resident_idle_service_block_200006ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 1300\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 1300\n.option pop\n");
    PORT(".Lresident_idle_service_edge_200006f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_idle_service_edge_200006f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_2000070e\n");
    __builtin_unreachable();
}

/* Original0x200006FA..0x2000070E. */
REGION void tsl9_resident_idle_service_block_200006fa(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a4 = UINT32_C(0xffcd0000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x2000070E..0x20000710. */
REGION void tsl9_resident_idle_service_block_2000070e(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_2000070e:\n.option push\n.option rvc\nc.bnez a0,.Lresident_idle_service_edge_2000070e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_20000712\n");
    __builtin_unreachable();
}

/* Original0x20000710..0x20000712. */
REGION void tsl9_resident_idle_service_block_20000710(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a0, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000712..0x20000720. */
REGION void tsl9_resident_idle_service_block_20000712(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 12(s1)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000214)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000720..0x20000722. */
REGION void tsl9_resident_idle_service_block_20000720(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_20000720:\n.option push\n.option rvc\nc.bnez a0,.Lresident_idle_service_edge_20000720\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_20000740\n");
    __builtin_unreachable();
}

/* Original0x20000722..0x20000726. */
REGION void tsl9_resident_idle_service_block_20000722(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 36(s1)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_20000724:\n.option push\n.option rvc\nc.beqz a5,.Lresident_idle_service_edge_20000724\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_2000073e\n");
    __builtin_unreachable();
}

/* Original0x20000726..0x2000072A. */
REGION void tsl9_resident_idle_service_block_20000726(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 12(s1)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_20000728:\n.option push\n.option rvc\nc.beqz a5,.Lresident_idle_service_edge_20000728\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_2000073e\n");
    __builtin_unreachable();
}

/* Original0x2000072A..0x20000732. */
REGION void tsl9_resident_idle_service_block_2000072a(void)
{
    REGS;
    PORT(".Lresident_idle_service_literal_2000072a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_idle_register_block_6430e\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_idle_service_literal_2000072a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000732..0x2000073A. */
REGION void tsl9_resident_idle_service_block_20000732(void)
{
    REGS;
    PORT(".Lresident_idle_service_literal_20000732:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_idle_register_block_638ea\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_idle_service_literal_20000732\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000073A..0x2000073E. */
REGION void tsl9_resident_idle_service_block_2000073a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 12(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000073E..0x20000740. */
REGION void tsl9_resident_idle_service_block_2000073e(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_2000073e:\n.option push\n.option rvc\nc.jal .Lresident_idle_service_edge_2000073e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_200004fa\n");
    __builtin_unreachable();
}

/* Original0x20000740..0x20000744. */
REGION void tsl9_resident_idle_service_block_20000740(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 36(s1)\n.option pop\n");
    PORT(".Lresident_idle_service_edge_20000742:\n.option push\n.option rvc\nc.beqz a5,.Lresident_idle_service_edge_20000742\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_idle_service_block_20000756\n");
    __builtin_unreachable();
}

/* Original0x20000744..0x20000756. */
REGION void tsl9_resident_idle_service_block_20000744(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x20000756..0x20000766. */
REGION void tsl9_resident_idle_service_block_20000756(void)
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

/* Original0x20000766..0x2000076C. */
REGION void tsl9_resident_idle_service_block_20000766(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000076a:\n.option push\n.option rvc\nc.j .Lresident_idle_service_edge_2000076a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_idle_service_block_20000680\n");
    __builtin_unreachable();
}

/* Original0x2000076C..0x20000770. */
REGION void tsl9_resident_idle_service_block_2000076c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000076e:\n.option push\n.option rvc\nc.j .Lresident_idle_service_edge_2000076e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_idle_service_block_200006a6\n");
    __builtin_unreachable();
}

/* Original0x20000770..0x20000772. */
REGION void tsl9_resident_idle_service_block_20000770(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000772..0x20000780. */
REGION void tsl9_resident_idle_service_block_20000772(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 16(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 4(s0)\n.option pop\n");
    a5 = a3 + a0; LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lresident_idle_service_edge_2000077c:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_idle_service_edge_2000077c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_20000784\n");
    __builtin_unreachable();
}

/* Original0x20000780..0x20000784. */
REGION void tsl9_resident_idle_service_block_20000780(void)
{
    REGS;
    PORT(".Lresident_idle_service_edge_20000780:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_idle_service_edge_20000780\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_idle_service_block_200006ea\n");
    __builtin_unreachable();
}

/* Original0x20000784..0x2000078A. */
REGION void tsl9_resident_idle_service_block_20000784(void)
{
    REGS;
    a0 = a5 - a4; LIVE;
    PORT(".Lresident_idle_service_edge_20000788:\n.option push\n.option rvc\nc.j .Lresident_idle_service_edge_20000788\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_idle_service_block_200006ea\n");
    __builtin_unreachable();
}
