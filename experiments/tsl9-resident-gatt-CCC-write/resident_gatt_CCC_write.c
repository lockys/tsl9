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

/* Six complete conditional SDK CCC bodies:274B/115i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4B2E4..0x4B2EE. */
REGION void tsl9_candidate_external_flash_4b2e4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b5)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4B2EE..0x4B2F2. */
REGION void tsl9_resident_gatt_CCC_write_block_4b2ee(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4b2ee:\n.option push\n.option norvc\nbltu a5,a3,.Lresident_gatt_CCC_write_edge_4b2ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4b2f8\n");
    __builtin_unreachable();
}

/* Original0x4B2F2..0x4B2F4. */
REGION void tsl9_resident_gatt_CCC_write_block_4b2f2(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4B2F4..0x4B2F8. */
REGION void tsl9_resident_gatt_CCC_write_block_4b2f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B2F8..0x4B304. */
REGION void tsl9_resident_gatt_CCC_write_block_4b2f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a1\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000004); LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0xfffffffc)); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b300:\n.option push\n.option norvc\nbeq a2,a0,.Lresident_gatt_CCC_write_edge_4b300\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4b2f4\n");
    __builtin_unreachable();
}

/* Original0x4B304..0x4B308. */
REGION void tsl9_resident_gatt_CCC_write_block_4b304(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b306:\n.option push\n.option rvc\nc.j .Lresident_gatt_CCC_write_edge_4b306\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_CCC_write_block_4b2ee\n");
    __builtin_unreachable();
}

/* Original0x4B33C..0x4B348. */
REGION void tsl9_candidate_external_flash_4b33c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b5)); LIVE;
    a3 = UINT32_C(0xffffffff); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4B348..0x4B34C. */
REGION void tsl9_resident_gatt_CCC_write_block_4b348(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4b348:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_gatt_CCC_write_edge_4b348\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4b34e\n");
    __builtin_unreachable();
}

/* Original0x4B34C..0x4B34E. */
REGION void tsl9_resident_gatt_CCC_write_block_4b34c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B34E..0x4B35A. */
REGION void tsl9_resident_gatt_CCC_write_block_4b34e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a3, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa116\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)0; LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a0 = a0 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b358:\n.option push\n.option rvc\nc.j .Lresident_gatt_CCC_write_edge_4b358\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_CCC_write_block_4b348\n");
    __builtin_unreachable();
}

/* Original0x4B456..0x4B45E. */
REGION void tsl9_candidate_external_flash_4b456(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4b45a:\n.option push\n.option norvc\njal ra,.Lresident_gatt_CCC_write_edge_4b45a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b2e4\n");
    __builtin_unreachable();
}

/* Original0x4B45E..0x4B460. */
REGION void tsl9_resident_gatt_CCC_write_block_4b45e(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4b45e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_CCC_write_edge_4b45e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4b468\n");
    __builtin_unreachable();
}

/* Original0x4B460..0x4B462. */
REGION void tsl9_resident_gatt_CCC_write_block_4b460(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x2128\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B462..0x4B468. */
REGION void tsl9_resident_gatt_CCC_write_block_4b462(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B468..0x4B46C. */
REGION void tsl9_resident_gatt_CCC_write_block_4b468(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b46a:\n.option push\n.option rvc\nc.j .Lresident_gatt_CCC_write_edge_4b46a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_CCC_write_block_4b462\n");
    __builtin_unreachable();
}

/* Original0x4B46C..0x4B480. */
REGION void tsl9_candidate_external_flash_4b46c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4b47c:\n.option push\n.option norvc\njal ra,.Lresident_gatt_CCC_write_edge_4b47c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b2e4\n");
    __builtin_unreachable();
}

/* Original0x4B480..0x4B482. */
REGION void tsl9_resident_gatt_CCC_write_block_4b480(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4b480:\n.option push\n.option rvc\nc.bnez a0,.Lresident_gatt_CCC_write_edge_4b480\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4b492\n");
    __builtin_unreachable();
}

/* Original0x4B482..0x4B48C. */
REGION void tsl9_resident_gatt_CCC_write_block_4b482(void)
{
    REGS;
    a0 = UINT32_C(0x00010000); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b488:\n.option push\n.option norvc\njal ra,.Lresident_gatt_CCC_write_edge_4b488\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b2e4\n");
    __builtin_unreachable();
}

/* Original0x4B48C..0x4B490. */
REGION void tsl9_resident_gatt_CCC_write_block_4b48c(void)
{
    REGS;
    a5 = UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b48e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_CCC_write_edge_4b48e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4b496\n");
    __builtin_unreachable();
}

/* Original0x4B490..0x4B492. */
REGION void tsl9_resident_gatt_CCC_write_block_4b490(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh s1, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa106\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B492..0x4B496. */
REGION void tsl9_resident_gatt_CCC_write_block_4b492(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb s0, 2(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa120\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4B496..0x4B4A4. */
REGION void tsl9_resident_gatt_CCC_write_block_4b496(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B4A4..0x4B4A6. */
REGION void tsl9_candidate_external_flash_4b4a4(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4b4a4:\n.option push\n.option rvc\nc.bnez a4,.Lresident_gatt_CCC_write_edge_4b4a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4b4ea\n");
    __builtin_unreachable();
}

/* Original0x4B4A6..0x4B4AE. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4a6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli a7, 2\n.option pop\n");
    a4 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b4aa:\n.option push\n.option norvc\nbne a3,a7,.Lresident_gatt_CCC_write_edge_4b4aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4b4ec\n");
    __builtin_unreachable();
}

/* Original0x4B4AE..0x4B4C8. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3218\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x2210\n.option pop\n");
    PORT(".option push\n.option norvc\nnot a5, a5\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a2 = a2 | a4; LIVE;
    a5 = a5 & a2; LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b4c6:\n.option push\n.option rvc\nc.bnez a5,.Lresident_gatt_CCC_write_edge_4b4c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4b4f0\n");
    __builtin_unreachable();
}

/* Original0x4B4C8..0x4B4D2. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s1, 12(a1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4b4ce:\n.option push\n.option norvc\njal ra,.Lresident_gatt_CCC_write_edge_4b4ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b456\n");
    __builtin_unreachable();
}

/* Original0x4B4D2..0x4B4DA. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4d2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4b4d6:\n.option push\n.option norvc\nbeq a2,a0,.Lresident_gatt_CCC_write_edge_4b4d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4b4f4\n");
    __builtin_unreachable();
}

/* Original0x4B4DA..0x4B4EA. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4b4e6:\n.option push\n.option norvc\njal zero,.Lresident_gatt_CCC_write_edge_4b4e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b46c\n");
    __builtin_unreachable();
}

/* Original0x4B4EA..0x4B4EC. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4ea(void)
{
    REGS;
    a4 = UINT32_C(0x0000000b); LIVE;
    __builtin_unreachable();
}

/* Original0x4B4EC..0x4B4F0. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4ec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4B4F0..0x4B4F4. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4f0(void)
{
    REGS;
    a4 = UINT32_C(0x00000080); LIVE;
    __builtin_unreachable();
}

/* Original0x4B4F4..0x4B500. */
REGION void tsl9_resident_gatt_CCC_write_block_4b4f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CFD0..0x4CFD8. */
REGION void tsl9_candidate_external_flash_4cfd0(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_gatt_CCC_write_edge_4cfd4:\n.option push\n.option norvc\nbne a0,a5,.Lresident_gatt_CCC_write_edge_4cfd4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_CCC_write_block_4cfde\n");
    __builtin_unreachable();
}

/* Original0x4CFD8..0x4CFDE. */
REGION void tsl9_resident_gatt_CCC_write_block_4cfd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4cfda:\n.option push\n.option norvc\njal zero,.Lresident_gatt_CCC_write_edge_4cfda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b33c\n");
    __builtin_unreachable();
}

/* Original0x4CFDE..0x4CFE6. */
REGION void tsl9_resident_gatt_CCC_write_block_4cfde(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_gatt_CCC_write_edge_4cfe2:\n.option push\n.option norvc\njal ra,.Lresident_gatt_CCC_write_edge_4cfe2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4b2e4\n");
    __builtin_unreachable();
}

/* Original0x4CFE6..0x4CFE8. */
REGION void tsl9_resident_gatt_CCC_write_block_4cfe6(void)
{
    REGS;
    PORT(".Lresident_gatt_CCC_write_edge_4cfe6:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_CCC_write_edge_4cfe6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_CCC_write_block_4cff0\n");
    __builtin_unreachable();
}

/* Original0x4CFE8..0x4CFF0. */
REGION void tsl9_resident_gatt_CCC_write_block_4cfe8(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa11e\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x4CFF0..0x4CFF6. */
REGION void tsl9_resident_gatt_CCC_write_block_4cff0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
