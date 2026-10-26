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

/* Two complete public-SDK scheduler-state bodies:178B/66i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x63DD0..0x63DEA. */
REGION void tsl9_candidate_external_flash_63dd0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2798\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".Lresident_scheduler_state_services_edge_63de6:\n.option push\n.option norvc\nbne a4,a5,.Lresident_scheduler_state_services_edge_63de6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_state_services_block_63e14\n");
    __builtin_unreachable();
}

/* Original0x63DEA..0x63E02. */
REGION void tsl9_resident_scheduler_state_services_block_63dea(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000540)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.lbu a2, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23b4\n.option pop\n");
    PORT(".Lresident_scheduler_state_services_edge_63e00:\n.option push\n.option rvc\nc.beqz a4,.Lresident_scheduler_state_services_edge_63e00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_63e4a\n");
    __builtin_unreachable();
}

/* Original0x63E02..0x63E06. */
REGION void tsl9_resident_scheduler_state_services_block_63e02(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_63e04:\n.option push\n.option rvc\nc.beqz a0,.Lresident_scheduler_state_services_edge_63e04\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_63e4a\n");
    __builtin_unreachable();
}

/* Original0x63E06..0x63E0A. */
REGION void tsl9_resident_scheduler_state_services_block_63e06(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x310c\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x63E0A..0x63E0E. */
REGION void tsl9_resident_scheduler_state_services_block_63e0a(void)
{
    REGS;
    PORT(".Lresident_scheduler_state_services_edge_63e0a:\n.option push\n.option norvc\njal ra,.Lresident_scheduler_state_services_edge_63e0a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_64f04\n");
    __builtin_unreachable();
}

/* Original0x63E0E..0x63E10. */
REGION void tsl9_resident_scheduler_state_services_block_63e0e(void)
{
    REGS;
    PORT(".Lresident_scheduler_state_services_edge_63e0e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_scheduler_state_services_edge_63e0e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_63e14\n");
    __builtin_unreachable();
}

/* Original0x63E10..0x63E14. */
REGION void tsl9_resident_scheduler_state_services_block_63e10(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63E14..0x63E1C. */
REGION void tsl9_resident_scheduler_state_services_block_63e14(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2418\n.option pop\n");
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_63e18:\n.option push\n.option norvc\nbne a4,a5,.Lresident_scheduler_state_services_edge_63e18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_state_services_block_63e2c\n");
    __builtin_unreachable();
}

/* Original0x63E1C..0x63E28. */
REGION void tsl9_resident_scheduler_state_services_block_63e1c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000438)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 11(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x37bc\n.option pop\n");
    PORT(".Lresident_scheduler_state_services_edge_63e26:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_state_services_edge_63e26\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_63e50\n");
    __builtin_unreachable();
}

/* Original0x63E28..0x63E2C. */
REGION void tsl9_resident_scheduler_state_services_block_63e28(void)
{
    REGS;
    PORT(".Lresident_scheduler_state_services_edge_63e28:\n.option push\n.option norvc\njal ra,.Lresident_scheduler_state_services_edge_63e28\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6020a\n");
    __builtin_unreachable();
}

/* Original0x63E2C..0x63E34. */
REGION void tsl9_resident_scheduler_state_services_block_63e2c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2418\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_63e30:\n.option push\n.option norvc\nbne a4,a5,.Lresident_scheduler_state_services_edge_63e30\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduler_state_services_block_63e50\n");
    __builtin_unreachable();
}

/* Original0x63E34..0x63E40. */
REGION void tsl9_resident_scheduler_state_services_block_63e34(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000044c)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    PORT(".Lresident_scheduler_state_services_edge_63e3e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduler_state_services_edge_63e3e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_63e50\n");
    __builtin_unreachable();
}

/* Original0x63E40..0x63E4A. */
REGION void tsl9_resident_scheduler_state_services_block_63e40(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_scheduler_state_services_edge_63e46:\n.option push\n.option norvc\njal zero,.Lresident_scheduler_state_services_edge_63e46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57dae\n");
    __builtin_unreachable();
}

/* Original0x63E4A..0x63E50. */
REGION void tsl9_resident_scheduler_state_services_block_63e4a(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_63e4e:\n.option push\n.option rvc\nc.j .Lresident_scheduler_state_services_edge_63e4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_scheduler_state_services_block_63e0a\n");
    __builtin_unreachable();
}

/* Original0x63E50..0x63E58. */
REGION void tsl9_resident_scheduler_state_services_block_63e50(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002610..0x20002620. */
REGION void tsl9_candidate_external_ram_20002610(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = a3 + UINT32_C(0x00000514); LIVE;
    __builtin_unreachable();
}

/* Original0x20002620..0x20002628. */
REGION void tsl9_resident_scheduler_state_services_block_20002620(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000514)); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_20002626:\n.option push\n.option rvc\nc.bnez a4,.Lresident_scheduler_state_services_edge_20002626\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_20002634\n");
    __builtin_unreachable();
}

/* Original0x20002628..0x2000262E. */
REGION void tsl9_resident_scheduler_state_services_block_20002628(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3398\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_2000262c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_scheduler_state_services_edge_2000262c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_20002634\n");
    __builtin_unreachable();
}

/* Original0x2000262E..0x20002632. */
REGION void tsl9_resident_scheduler_state_services_block_2000262e(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_scheduler_state_services_edge_20002630:\n.option push\n.option rvc\nc.bnez a4,.Lresident_scheduler_state_services_edge_20002630\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduler_state_services_block_20002620\n");
    __builtin_unreachable();
}

/* Original0x20002632..0x20002634. */
REGION void tsl9_resident_scheduler_state_services_block_20002632(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33d8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002634..0x2000263A. */
REGION void tsl9_resident_scheduler_state_services_block_20002634(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
