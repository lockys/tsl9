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

/* Four complete public-SDK RF init/task bodies:664B/216i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x641B0..0x641D0. */
REGION void tsl9_candidate_RF_common_reset_641b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3078\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_bridge_edge_641cc:\n.option push\n.option norvc\nbeq a5,a4,.Loriginal_RF_bridge_edge_641cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_64286\n");
    __builtin_unreachable();
}

/* Original0x641D0..0x641D6. */
REGION void tsl9_original_RF_bridge_block_641d0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3078\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_641d2:\n.option push\n.option norvc\nbeq a5,a4,.Loriginal_RF_bridge_edge_641d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_64286\n");
    __builtin_unreachable();
}

/* Original0x641D6..0x641EA. */
REGION void tsl9_original_RF_bridge_block_641d6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000504)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x40024\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 768\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_641e6:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_bridge_edge_641e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_64286\n");
    __builtin_unreachable();
}

/* Original0x641EA..0x641FC. */
REGION void tsl9_original_RF_bridge_block_641ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s4, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Loriginal_RF_bridge_edge_641f8:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_641f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63eda\n");
    __builtin_unreachable();
}

/* Original0x641FC..0x6424A. */
REGION void tsl9_original_RF_bridge_block_641fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1288(s5)\n.option pop\n");
    a3 = UINT32_C(0xffffd000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a4 = a4 & a3; LIVE;
    a3 = UINT32_C(0x00001000); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00330000); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1424(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a4 = UINT32_C(0x0000005d); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    PORT(".Loriginal_RF_bridge_edge_64246:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_64246\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6645c\n");
    __builtin_unreachable();
}

/* Original0x6424A..0x6424E. */
REGION void tsl9_original_RF_bridge_block_6424a(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_6424a:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_6424a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_67198\n");
    __builtin_unreachable();
}

/* Original0x6424E..0x64252. */
REGION void tsl9_original_RF_bridge_block_6424e(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_6424e:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_6424e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_662da\n");
    __builtin_unreachable();
}

/* Original0x64252..0x64256. */
REGION void tsl9_original_RF_bridge_block_64252(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_64252:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_64252\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6636e\n");
    __builtin_unreachable();
}

/* Original0x64256..0x64286. */
REGION void tsl9_original_RF_bridge_block_64256(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s5)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 1424(s3)\n.option pop\n");
    a4 = UINT32_C(0xffce0000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 7(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s4, 524(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64286..0x64298. */
REGION void tsl9_original_RF_bridge_block_64286(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64298..0x642FE. */
REGION void tsl9_candidate_RF_init_registers_64298(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000510)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000050c)) = (uint32_t)0; LIVE;
    a5 = UINT32_C(0x40024000); LIVE;
    a3 = a5 + UINT32_C(0x00000300); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000504)) = (uint32_t)a3; LIVE;
    a3 = a5 + UINT32_C(0x00000200); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000053c)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x40025000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)) = (uint32_t)a3; LIVE;
    a5 = a5 + UINT32_C(0x00000100); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3f8\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000001ec)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a4; LIVE;
    a4 = a4 + UINT32_C(0x00000110); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a4; LIVE;
    PORT(".Loriginal_RF_bridge_edge_642fc:\n.option push\n.option rvc\nc.jal .Loriginal_RF_bridge_edge_642fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_idle_register_block_6430e\n");
    __builtin_unreachable();
}

/* Original0x642FE..0x64302. */
REGION void tsl9_original_RF_bridge_block_642fe(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_642fe:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_642fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_660ce\n");
    __builtin_unreachable();
}

/* Original0x64302..0x64306. */
REGION void tsl9_original_RF_bridge_block_64302(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_64302:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_64302\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_idle_register_block_638ea\n");
    __builtin_unreachable();
}

/* Original0x64306..0x6430E. */
REGION void tsl9_original_RF_bridge_block_64306(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_6430a:\n.option push\n.option norvc\njal zero,.Loriginal_RF_bridge_edge_6430a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_common_reset_641b0\n");
    __builtin_unreachable();
}

/* Original0x65920..0x6592E. */
REGION void tsl9_candidate_RF_task_callback_65920(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_6592c:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_6592c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_65970\n");
    __builtin_unreachable();
}

/* Original0x6592E..0x6593C. */
REGION void tsl9_original_RF_bridge_block_6592e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d8\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_bridge_edge_6593a:\n.option push\n.option rvc\nc.beqz a4,.Loriginal_RF_bridge_edge_6593a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_65964\n");
    __builtin_unreachable();
}

/* Original0x6593C..0x6594E. */
REGION void tsl9_original_RF_bridge_block_6593c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2b88\n.option pop\n");
    a2 = UINT32_C(0x00000050); LIVE;
    a5 = a4 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_6594a:\n.option push\n.option norvc\nbgez a5,.Loriginal_RF_bridge_edge_6594a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_6595e\n");
    __builtin_unreachable();
}

/* Original0x6594E..0x6595E. */
REGION void tsl9_original_RF_bridge_block_6594e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000559)); LIVE;
    a5 = UINT32_C(0x000000a0); LIVE;
    a2 = a2 * a5; LIVE;
    __builtin_unreachable();
}

/* Original0x6595E..0x65964. */
REGION void tsl9_original_RF_bridge_block_6595e(void)
{
    REGS;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_bridge_edge_65960:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_65960\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x65964..0x65968. */
REGION void tsl9_original_RF_bridge_block_65964(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65968..0x65970. */
REGION void tsl9_original_RF_bridge_block_65968(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65970..0x65976. */
REGION void tsl9_original_RF_bridge_block_65970(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_bridge_edge_65974:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_65974\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_659b6\n");
    __builtin_unreachable();
}

/* Original0x65976..0x65984. */
REGION void tsl9_original_RF_bridge_block_65976(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d8\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_bridge_edge_65982:\n.option push\n.option rvc\nc.beqz a4,.Loriginal_RF_bridge_edge_65982\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_659b0\n");
    __builtin_unreachable();
}

/* Original0x65984..0x65996. */
REGION void tsl9_original_RF_bridge_block_65984(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2b88\n.option pop\n");
    a2 = UINT32_C(0x000000a0); LIVE;
    a5 = a4 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_65992:\n.option push\n.option norvc\nbgez a5,.Loriginal_RF_bridge_edge_65992\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_659aa\n");
    __builtin_unreachable();
}

/* Original0x65996..0x659AA. */
REGION void tsl9_original_RF_bridge_block_65996(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000559)); LIVE;
    a5 = UINT32_C(0x000000a0); LIVE;
    a2 = a2 * a5; LIVE;
    a2 = a2 + UINT32_C(0x00000028); LIVE;
    __builtin_unreachable();
}

/* Original0x659AA..0x659B0. */
REGION void tsl9_original_RF_bridge_block_659aa(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659ac:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_659ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x659B0..0x659B6. */
REGION void tsl9_original_RF_bridge_block_659b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_659b4:\n.option push\n.option rvc\nc.j .Loriginal_RF_bridge_edge_659b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_bridge_block_65968\n");
    __builtin_unreachable();
}

/* Original0x659B6..0x659BC. */
REGION void tsl9_original_RF_bridge_block_659b6(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659ba:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_659ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_659c6\n");
    __builtin_unreachable();
}

/* Original0x659BC..0x659C0. */
REGION void tsl9_original_RF_bridge_block_659bc(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_659bc:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_659bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_657d8\n");
    __builtin_unreachable();
}

/* Original0x659C0..0x659C6. */
REGION void tsl9_original_RF_bridge_block_659c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 4\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_659c4:\n.option push\n.option rvc\nc.j .Loriginal_RF_bridge_edge_659c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_bridge_block_65968\n");
    __builtin_unreachable();
}

/* Original0x659C6..0x659CC. */
REGION void tsl9_original_RF_bridge_block_659c6(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659ca:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_659ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_659e4\n");
    __builtin_unreachable();
}

/* Original0x659CC..0x659DA. */
REGION void tsl9_original_RF_bridge_block_659cc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659d8:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_659d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_659de\n");
    __builtin_unreachable();
}

/* Original0x659DA..0x659DE. */
REGION void tsl9_original_RF_bridge_block_659da(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_659da:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_659da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6575a\n");
    __builtin_unreachable();
}

/* Original0x659DE..0x659E4. */
REGION void tsl9_original_RF_bridge_block_659de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 8\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_659e2:\n.option push\n.option rvc\nc.j .Loriginal_RF_bridge_edge_659e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_bridge_block_65968\n");
    __builtin_unreachable();
}

/* Original0x659E4..0x659EC. */
REGION void tsl9_original_RF_bridge_block_659e4(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659ea:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_bridge_edge_659ea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_bridge_block_65968\n");
    __builtin_unreachable();
}

/* Original0x659EC..0x659F0. */
REGION void tsl9_original_RF_bridge_block_659ec(void)
{
    REGS;
    PORT(".Loriginal_RF_bridge_edge_659ec:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_659ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43edc\n");
    __builtin_unreachable();
}

/* Original0x659F0..0x65A00. */
REGION void tsl9_original_RF_bridge_block_659f0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Loriginal_RF_bridge_edge_659fc:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_bridge_edge_659fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_bridge_block_65a12\n");
    __builtin_unreachable();
}

/* Original0x65A00..0x65A12. */
REGION void tsl9_original_RF_bridge_block_65a00(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000570)); LIVE;
    a2 = UINT32_C(0x00000640); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".Loriginal_RF_bridge_edge_65a0e:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_65a0e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x65A12..0x65A18. */
REGION void tsl9_original_RF_bridge_block_65a12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 16\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_65a16:\n.option push\n.option rvc\nc.j .Loriginal_RF_bridge_edge_65a16\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_bridge_block_65968\n");
    __builtin_unreachable();
}

/* Original0x66056..0x66060. */
REGION void tsl9_candidate_RF_RoleInit_66056(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_6605c:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_6605c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_RF_init_registers_64298\n");
    __builtin_unreachable();
}

/* Original0x66060..0x66076. */
REGION void tsl9_original_RF_bridge_block_66060(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 1376\n.option pop\n");
    a2 = UINT32_C(0x00000024); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Loriginal_RF_bridge_literal_6606e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_bridge_literal_6606e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x66076..0x66088. */
REGION void tsl9_original_RF_bridge_block_66076(void)
{
    REGS;
    a0 = UINT32_C(0x00066000); LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    a0 = a0 + UINT32_C(0xfffff920); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 1376(s0)\n.option pop\n");
    PORT(".Loriginal_RF_bridge_edge_66084:\n.option push\n.option norvc\njal ra,.Loriginal_RF_bridge_edge_66084\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_process_event_register_43c4e\n");
    __builtin_unreachable();
}

/* Original0x66088..0x66098. */
REGION void tsl9_original_RF_bridge_block_66088(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a0, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa808\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
