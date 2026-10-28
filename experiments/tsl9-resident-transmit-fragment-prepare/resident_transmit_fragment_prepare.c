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

/* One complete conditional RAM fragment preparer:250B/94i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x20000AC6..0x20000ACC. */
REGION void tsl9_candidate_transmit_fragment_20000ac6(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000118)); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000aca:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_fragment_prepare_edge_20000aca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000bbc\n");
    __builtin_unreachable();
}

/* Original0x20000ACC..0x20000AEE. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000acc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x255c\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004e)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000fc); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa55c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 9(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3714\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 12(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2752\n.option pop\n");
    a0 = a3 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x18\n.option pop\n");
    PORT(".Lresident_transmit_fragment_prepare_edge_20000aea:\n.option push\n.option norvc\nbleu a2,a1,.Lresident_transmit_fragment_prepare_edge_20000aea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b58\n");
    __builtin_unreachable();
}

/* Original0x20000AEE..0x20000AF2. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000aee(void)
{
    REGS;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000aee:\n.option push\n.option norvc\nbgez a0,.Lresident_transmit_fragment_prepare_edge_20000aee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b50\n");
    __builtin_unreachable();
}

/* Original0x20000AF2..0x20000B04. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000af2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 8(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2708\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000007f); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 9(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb714\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a3 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b00:\n.option push\n.option norvc\nbne a0,a2,.Lresident_transmit_fragment_prepare_edge_20000b00\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b08\n");
    __builtin_unreachable();
}

/* Original0x20000B04..0x20000B08. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b04(void)
{
    REGS;
    a3 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x20000B08..0x20000B10. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b08(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a3, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa454\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x20000B10..0x20000B20. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b10(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a1, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb84c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 272(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    a1 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b1c:\n.option push\n.option norvc\njal ra,.Lresident_transmit_fragment_prepare_edge_20000b1c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_copy_arch_20000332\n");
    __builtin_unreachable();
}

/* Original0x20000B20..0x20000B36. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3850\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27da\n.option pop\n");
    a3 = a3 + a2; LIVE;
    a4 = a4 - a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7da\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc3c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000B36..0x20000B46. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b36(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 54(s0)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000001fe)); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b42:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_transmit_fragment_prepare_edge_20000b42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b84\n");
    __builtin_unreachable();
}

/* Original0x20000B46..0x20000B50. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b46(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x245c\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45c\n.option pop\n");
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b4e:\n.option push\n.option rvc\nc.j .Lresident_transmit_fragment_prepare_edge_20000b4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_fragment_prepare_block_20000b84\n");
    __builtin_unreachable();
}

/* Original0x20000B50..0x20000B58. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b50(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45c\n.option pop\n");
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b56:\n.option push\n.option rvc\nc.j .Lresident_transmit_fragment_prepare_edge_20000b56\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_fragment_prepare_block_20000b10\n");
    __builtin_unreachable();
}

/* Original0x20000B58..0x20000B60. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b58(void)
{
    REGS;
    a3 = a2 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b5c:\n.option push\n.option norvc\nbgez a0,.Lresident_transmit_fragment_prepare_edge_20000b5c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b8e\n");
    __builtin_unreachable();
}

/* Original0x20000B60..0x20000B6C. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b60(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 8(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2708\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a2 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b68:\n.option push\n.option norvc\nbne a0,a1,.Lresident_transmit_fragment_prepare_edge_20000b68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b70\n");
    __builtin_unreachable();
}

/* Original0x20000B6C..0x20000B70. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b6c(void)
{
    REGS;
    a2 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x20000B70..0x20000B7A. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b70(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a2, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa450\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb854\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x20000B7A..0x20000B84. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b7a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc3c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000b82:\n.option push\n.option rvc\nc.bnez a5,.Lresident_transmit_fragment_prepare_edge_20000b82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_fragment_prepare_block_20000b36\n");
    __builtin_unreachable();
}

/* Original0x20000B84..0x20000B8E. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b84(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000B8E..0x20000BA6. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000b8e(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb854\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlw a0, 272(s0)\n.option pop\n");
    a1 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000ba2:\n.option push\n.option norvc\njal ra,.Lresident_transmit_fragment_prepare_edge_20000ba2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_copy_arch_20000332\n");
    __builtin_unreachable();
}

/* Original0x20000BA6..0x20000BBC. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000ba6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3850\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27da\n.option pop\n");
    a3 = a3 + a2; LIVE;
    a4 = a4 - a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7da\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_transmit_fragment_prepare_edge_20000bba:\n.option push\n.option rvc\nc.j .Lresident_transmit_fragment_prepare_edge_20000bba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_fragment_prepare_block_20000b7a\n");
    __builtin_unreachable();
}

/* Original0x20000BBC..0x20000BC0. */
REGION void tsl9_resident_transmit_fragment_prepare_block_20000bbc(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
