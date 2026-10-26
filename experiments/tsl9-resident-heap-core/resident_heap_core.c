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

/* Two public-SDK heap helpers:420B/145i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x20000040..0x20000058. */
REGION void tsl9_candidate_heap_allocate_20000040(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_heap_core_edge_20000056:\n.option push\n.option rvc\nc.beqz a0,.Lresident_heap_core_edge_20000056\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_2000005a\n");
    __builtin_unreachable();
}

/* Original0x20000058..0x2000005A. */
REGION void tsl9_resident_heap_core_block_20000058(void)
{
    REGS;
    PORT(".Lresident_heap_core_edge_20000058:\n.option push\n.option rvc\nc.bnez a1,.Lresident_heap_core_edge_20000058\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_20000066\n");
    __builtin_unreachable();
}

/* Original0x2000005A..0x20000066. */
REGION void tsl9_resident_heap_core_block_2000005a(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s0, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_heap_core_edge_20000064:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_20000064\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_20000104\n");
    __builtin_unreachable();
}

/* Original0x20000066..0x2000007C. */
REGION void tsl9_resident_heap_core_block_20000066(void)
{
    REGS;
    a5 = a0 + UINT32_C(0x00000003); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a4 = UINT32_C(0x00000034); LIVE;
    PORT(".Lresident_heap_core_edge_20000078:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_heap_core_edge_20000078\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200000a4\n");
    __builtin_unreachable();
}

/* Original0x2000007C..0x20000084. */
REGION void tsl9_resident_heap_core_block_2000007c(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000194)); LIVE;
    __builtin_unreachable();
}

/* Original0x20000084..0x2000008C. */
REGION void tsl9_resident_heap_core_block_20000084(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000018c)); LIVE;
    __builtin_unreachable();
}

/* Original0x2000008C..0x20000090. */
REGION void tsl9_resident_heap_core_block_2000008c(void)
{
    REGS;
    PORT(".Lresident_heap_core_edge_2000008c:\n.option push\n.option norvc\nbne a3,a0,.Lresident_heap_core_edge_2000008c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200000ae\n");
    __builtin_unreachable();
}

/* Original0x20000090..0x2000009A. */
REGION void tsl9_resident_heap_core_block_20000090(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_heap_core_edge_20000098:\n.option push\n.option rvc\nc.beqz a4,.Lresident_heap_core_edge_20000098\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_2000005a\n");
    __builtin_unreachable();
}

/* Original0x2000009A..0x200000A2. */
REGION void tsl9_resident_heap_core_block_2000009a(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a1 = a1 | a5; LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200000A2..0x200000A4. */
REGION void tsl9_resident_heap_core_block_200000a2(void)
{
    REGS;
    PORT(".Lresident_heap_core_edge_200000a2:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_200000a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_2000005a\n");
    __builtin_unreachable();
}

/* Original0x200000A4..0x200000AE. */
REGION void tsl9_resident_heap_core_block_200000a4(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000190)); LIVE;
    PORT(".Lresident_heap_core_edge_200000ac:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_200000ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_20000084\n");
    __builtin_unreachable();
}

/* Original0x200000AE..0x200000B2. */
REGION void tsl9_resident_heap_core_block_200000ae(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x217a\n.option pop\n");
    PORT(".Lresident_heap_core_edge_200000b0:\n.option push\n.option rvc\nc.bnez a4,.Lresident_heap_core_edge_200000b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_2000010c\n");
    __builtin_unreachable();
}

/* Original0x200000B2..0x200000B8. */
REGION void tsl9_resident_heap_core_block_200000b2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x215a\n.option pop\n");
    PORT(".Lresident_heap_core_edge_200000b4:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_heap_core_edge_200000b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_2000010c\n");
    __builtin_unreachable();
}

/* Original0x200000B8..0x200000CA. */
REGION void tsl9_resident_heap_core_block_200000b8(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a2 = a4 - a5; LIVE;
    PORT(".option push\n.option rvc\nli a6, 8\n.option pop\n");
    a3 = a3 + UINT32_C(0x0000019c); LIVE;
    PORT(".Lresident_heap_core_edge_200000c6:\n.option push\n.option norvc\nbleu a2,a6,.Lresident_heap_core_edge_200000c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200000f0\n");
    __builtin_unreachable();
}

/* Original0x200000CA..0x200000F0. */
REGION void tsl9_resident_heap_core_block_200000ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a7, 0(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a6, 6(a3)\n.option pop\n");
    a2 = a5 + UINT32_C(0x00000008); LIVE;
    a4 = a4 - a5; LIVE;
    a2 = a2 + a0; LIVE;
    a4 = a4 + UINT32_C(0xfffffff8); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 4(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa25a\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a7, 0(a2)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a2 + UINT32_C(0x00000006)) = (uint16_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa15e\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, a6, -8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 6(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa2fa\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200000F0..0x20000104. */
REGION void tsl9_resident_heap_core_block_200000f0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a1, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa16e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 6(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x22ee\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000008); LIVE;
    a5 = a1 - a5; LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 6(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa2fe\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s0, 524(a5)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000104..0x2000010C. */
REGION void tsl9_resident_heap_core_block_20000104(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000010C..0x20000110. */
REGION void tsl9_resident_heap_core_block_2000010c(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_heap_core_edge_2000010e:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_2000010e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_2000008c\n");
    __builtin_unreachable();
}

/* Original0x20000110..0x20000122. */
REGION void tsl9_candidate_heap_release_20000110(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nlw a6, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_heap_core_edge_20000120:\n.option push\n.option rvc\nc.bnez a0,.Lresident_heap_core_edge_20000120\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_20000128\n");
    __builtin_unreachable();
}

/* Original0x20000122..0x20000128. */
REGION void tsl9_resident_heap_core_block_20000122(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a6, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000128..0x2000013C. */
REGION void tsl9_resident_heap_core_block_20000128(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t3, 404(a5)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 396(a5)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a5, t3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000013C..0x20000140. */
REGION void tsl9_resident_heap_core_block_2000013c(void)
{
    REGS;
    PORT(".Lresident_heap_core_edge_2000013c:\n.option push\n.option norvc\nbleu t1,a5,.Lresident_heap_core_edge_2000013c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001d8\n");
    __builtin_unreachable();
}

/* Original0x20000140..0x20000148. */
REGION void tsl9_resident_heap_core_block_20000140(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a7, 0(a5)\n.option pop\n");
    PORT(".Lresident_heap_core_edge_20000144:\n.option push\n.option norvc\nbltu a0,a5,.Lresident_heap_core_edge_20000144\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001de\n");
    __builtin_unreachable();
}

/* Original0x20000148..0x2000014C. */
REGION void tsl9_resident_heap_core_block_20000148(void)
{
    REGS;
    PORT(".Lresident_heap_core_edge_20000148:\n.option push\n.option norvc\nbltu a7,a0,.Lresident_heap_core_edge_20000148\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001de\n");
    __builtin_unreachable();
}

/* Original0x2000014C..0x20000154. */
REGION void tsl9_resident_heap_core_block_2000014c(void)
{
    REGS;
    a4 = a5 + UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_heap_core_edge_20000150:\n.option push\n.option norvc\nbltu a0,a4,.Lresident_heap_core_edge_20000150\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001d8\n");
    __builtin_unreachable();
}

/* Original0x20000154..0x2000015E. */
REGION void tsl9_resident_heap_core_block_20000154(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23f2\n.option pop\n");
    a4 = UINT32_C(0x00008000); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_heap_core_edge_2000015a:\n.option push\n.option norvc\nbne a2,a4,.Lresident_heap_core_edge_2000015a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_2000016c\n");
    __builtin_unreachable();
}

/* Original0x2000015E..0x2000016C. */
REGION void tsl9_resident_heap_core_block_2000015e(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xffffffa4)); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xffffffa4)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x2000016C..0x2000018C. */
REGION void tsl9_resident_heap_core_block_2000016c(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a0 = a2 + UINT32_C(0x0000019c); LIVE;
    /* Conditional Xwchc: qk.c.lhu a1, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23ce\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x217a\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)) = (uint16_t)0; LIVE;
    a2 = a2 + UINT32_C(0x0000019c); LIVE;
    a4 = a4 + a1; LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17a\n.option pop\n");
    PORT(".Lresident_heap_core_edge_20000188:\n.option push\n.option norvc\nbeq a5,t3,.Lresident_heap_core_edge_20000188\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001ae\n");
    __builtin_unreachable();
}

/* Original0x2000018C..0x20000198. */
REGION void tsl9_resident_heap_core_block_2000018c(void)
{
    REGS;
    a0 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000190)); LIVE;
    PORT(".Lresident_heap_core_edge_20000194:\n.option push\n.option norvc\nbeq a0,a5,.Lresident_heap_core_edge_20000194\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001ae\n");
    __builtin_unreachable();
}

/* Original0x20000198..0x2000019C. */
REGION void tsl9_resident_heap_core_block_20000198(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 6(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x22ea\n.option pop\n");
    PORT(".Lresident_heap_core_edge_2000019a:\n.option push\n.option rvc\nc.bnez a0,.Lresident_heap_core_edge_2000019a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_200001ae\n");
    __builtin_unreachable();
}

/* Original0x2000019C..0x200001AE. */
REGION void tsl9_resident_heap_core_block_2000019c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 4(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x22de\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a7, 0(a3)\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000008); LIVE;
    a1 = a1 + a5; LIVE;
    a1 = a1 + UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sh a1, 4(a3). */
    PORT(".option push\n.option rvc\n.2byte 0xa2ce\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a4, 6(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa27a\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200001AE..0x200001B4. */
REGION void tsl9_resident_heap_core_block_200001ae(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_heap_core_edge_200001b0:\n.option push\n.option norvc\nbeq a4,t1,.Lresident_heap_core_edge_200001b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001d8\n");
    __builtin_unreachable();
}

/* Original0x200001B4..0x200001C0. */
REGION void tsl9_resident_heap_core_block_200001b4(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000190)); LIVE;
    PORT(".Lresident_heap_core_edge_200001bc:\n.option push\n.option norvc\nbeq a4,a3,.Lresident_heap_core_edge_200001bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_heap_core_block_200001d8\n");
    __builtin_unreachable();
}

/* Original0x200001C0..0x200001C4. */
REGION void tsl9_resident_heap_core_block_200001c0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a3, 6(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2376\n.option pop\n");
    PORT(".Lresident_heap_core_edge_200001c2:\n.option push\n.option rvc\nc.bnez a3,.Lresident_heap_core_edge_200001c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_heap_core_block_200001d8\n");
    __builtin_unreachable();
}

/* Original0x200001C4..0x200001D8. */
REGION void tsl9_resident_heap_core_block_200001c4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a3, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23d6\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x234e\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 + UINT32_C(0x00000008); LIVE;
    a3 = a3 + a1; LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 6(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x227e\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 6(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa27e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200001D8..0x200001DE. */
REGION void tsl9_resident_heap_core_block_200001d8(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".Lresident_heap_core_edge_200001dc:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_200001dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_20000122\n");
    __builtin_unreachable();
}

/* Original0x200001DE..0x200001E4. */
REGION void tsl9_resident_heap_core_block_200001de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a7\n.option pop\n");
    PORT(".Lresident_heap_core_edge_200001e2:\n.option push\n.option rvc\nc.j .Lresident_heap_core_edge_200001e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_heap_core_block_2000013c\n");
    __builtin_unreachable();
}
