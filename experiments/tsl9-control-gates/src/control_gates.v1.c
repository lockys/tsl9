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

/* Twelve complete control gate functions:892B/308i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x81EE..0x81F8. */
REGION void tsl9_control_gates_provider_81ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20004\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffce7)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA658..0xA664. */
REGION void tsl9_control_gates_provider_a658(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff876)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA9DE..0xA9E8. */
REGION void tsl9_control_gates_provider_a9de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000004fe)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCD6A..0xCD78. */
REGION void tsl9_record_dispatch_provider_cd6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lcontrol_gates_edge_cd74:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_cd74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_81ee\n");
    __builtin_unreachable();
}

/* Original0xCD78..0xCD84. */
REGION void tsl9_control_gates_block_cd78(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lcontrol_gates_edge_cd80:\n.option push\n.option norvc\nbltu a5,a4,.Lcontrol_gates_edge_cd80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_cd90\n");
    __builtin_unreachable();
}

/* Original0xCD84..0xCD90. */
REGION void tsl9_control_gates_block_cd84(void)
{
    REGS;
    a5 = UINT32_C(0x0000065e); LIVE;
    PORT(".option push\n.option norvc\nsrl a5, a5, a4\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_cd8e:\n.option push\n.option rvc\nc.bnez a5,.Lcontrol_gates_edge_cd8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cda6\n");
    __builtin_unreachable();
}

/* Original0xCD90..0xCD96. */
REGION void tsl9_control_gates_block_cd90(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_cd92:\n.option push\n.option norvc\nbeq a1,a5,.Lcontrol_gates_edge_cd92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce58\n");
    __builtin_unreachable();
}

/* Original0xCD96..0xCD98. */
REGION void tsl9_control_gates_block_cd96(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_cd96:\n.option push\n.option rvc\nc.beqz a1,.Lcontrol_gates_edge_cd96\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_ce48\n");
    __builtin_unreachable();
}

/* Original0xCD98..0xCD9E. */
REGION void tsl9_control_gates_block_cd98(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_cd9a:\n.option push\n.option norvc\nbeq a1,a4,.Lcontrol_gates_edge_cd9a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce7a\n");
    __builtin_unreachable();
}

/* Original0xCD9E..0xCDA6. */
REGION void tsl9_control_gates_block_cd9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCDA6..0xCDB4. */
REGION void tsl9_control_gates_block_cda6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000185)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_cdb0:\n.option push\n.option norvc\nbeq a1,a5,.Lcontrol_gates_edge_cdb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce08\n");
    __builtin_unreachable();
}

/* Original0xCDB4..0xCDB6. */
REGION void tsl9_control_gates_block_cdb4(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_cdb4:\n.option push\n.option rvc\nc.beqz a1,.Lcontrol_gates_edge_cdb4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cde8\n");
    __builtin_unreachable();
}

/* Original0xCDB6..0xCDBC. */
REGION void tsl9_control_gates_block_cdb6(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_cdb8:\n.option push\n.option norvc\nbeq a1,a4,.Lcontrol_gates_edge_cdb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce26\n");
    __builtin_unreachable();
}

/* Original0xCDBC..0xCDC6. */
REGION void tsl9_control_gates_block_cdbc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000016f)); LIVE;
    PORT(".Lcontrol_gates_edge_cdc4:\n.option push\n.option rvc\nc.beqz a5,.Lcontrol_gates_edge_cdc4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCDC6..0xCDCE. */
REGION void tsl9_control_gates_block_cdc6(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffc); LIVE;
    a5 = a5 & UINT32_C(0x000000fb); LIVE;
    PORT(".Lcontrol_gates_edge_cdcc:\n.option push\n.option rvc\nc.bnez a5,.Lcontrol_gates_edge_cdcc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_ce3c\n");
    __builtin_unreachable();
}

/* Original0xCDCE..0xCDD8. */
REGION void tsl9_control_gates_block_cdce(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000015c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xCDD8..0xCDDC. */
REGION void tsl9_control_gates_block_cdd8(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_cdd8:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_cdd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a658\n");
    __builtin_unreachable();
}

/* Original0xCDDC..0xCDE8. */
REGION void tsl9_control_gates_block_cddc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lcontrol_gates_edge_cde4:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_cde4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xCDE8..0xCDEC. */
REGION void tsl9_control_gates_block_cde8(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_cde8:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_cde8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_cdfc\n");
    __builtin_unreachable();
}

/* Original0xCDEC..0xCDF2. */
REGION void tsl9_control_gates_block_cdec(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_cdee:\n.option push\n.option norvc\nbne a0,a5,.Lcontrol_gates_edge_cdee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_cdbc\n");
    __builtin_unreachable();
}

/* Original0xCDF2..0xCDFC. */
REGION void tsl9_control_gates_block_cdf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000139)) = (uint8_t)a0; LIVE;
    PORT(".Lcontrol_gates_edge_cdfa:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_cdfa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdbc\n");
    __builtin_unreachable();
}

/* Original0xCDFC..0xCDFE. */
REGION void tsl9_control_gates_block_cdfc(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0xCDFE..0xCE08. */
REGION void tsl9_control_gates_block_cdfe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000012d)) = (uint8_t)a5; LIVE;
    PORT(".Lcontrol_gates_edge_ce06:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce06\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdbc\n");
    __builtin_unreachable();
}

/* Original0xCE08..0xCE0C. */
REGION void tsl9_control_gates_block_ce08(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce08:\n.option push\n.option norvc\nbeq a0,a1,.Lcontrol_gates_edge_ce08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce1a\n");
    __builtin_unreachable();
}

/* Original0xCE0C..0xCE12. */
REGION void tsl9_control_gates_block_ce0c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_ce0e:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_ce0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce20\n");
    __builtin_unreachable();
}

/* Original0xCE12..0xCE16. */
REGION void tsl9_control_gates_block_ce12(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lcontrol_gates_edge_ce14:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce14\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE16..0xCE1A. */
REGION void tsl9_control_gates_block_ce16(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lcontrol_gates_edge_ce18:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE1A..0xCE1E. */
REGION void tsl9_control_gates_block_ce1a(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lcontrol_gates_edge_ce1c:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE1E..0xCE20. */
REGION void tsl9_control_gates_block_ce1e(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce1e:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce1e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdbc\n");
    __builtin_unreachable();
}

/* Original0xCE20..0xCE24. */
REGION void tsl9_control_gates_block_ce20(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lcontrol_gates_edge_ce22:\n.option push\n.option rvc\nc.beqz s0,.Lcontrol_gates_edge_ce22\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE24..0xCE26. */
REGION void tsl9_control_gates_block_ce24(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce24:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce24\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdbc\n");
    __builtin_unreachable();
}

/* Original0xCE26..0xCE2A. */
REGION void tsl9_control_gates_block_ce26(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce26:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_ce26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce34\n");
    __builtin_unreachable();
}

/* Original0xCE2A..0xCE2E. */
REGION void tsl9_control_gates_block_ce2a(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce2a:\n.option push\n.option norvc\nbne a0,a1,.Lcontrol_gates_edge_ce2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce12\n");
    __builtin_unreachable();
}

/* Original0xCE2E..0xCE30. */
REGION void tsl9_control_gates_block_ce2e(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce2e:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdf2\n");
    __builtin_unreachable();
}

/* Original0xCE30..0xCE34. */
REGION void tsl9_control_gates_block_ce30(void)
{
    REGS;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lcontrol_gates_edge_ce32:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce32\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdf2\n");
    __builtin_unreachable();
}

/* Original0xCE34..0xCE38. */
REGION void tsl9_control_gates_block_ce34(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lcontrol_gates_edge_ce36:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE38..0xCE3C. */
REGION void tsl9_control_gates_block_ce38(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lcontrol_gates_edge_ce3a:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce3a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cdfe\n");
    __builtin_unreachable();
}

/* Original0xCE3C..0xCE48. */
REGION void tsl9_control_gates_block_ce3c(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000ee)) = (uint8_t)a5; LIVE;
    PORT(".Lcontrol_gates_edge_ce46:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce46\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCE48..0xCE4C. */
REGION void tsl9_control_gates_block_ce48(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce48:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_ce48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce84\n");
    __builtin_unreachable();
}

/* Original0xCE4C..0xCE52. */
REGION void tsl9_control_gates_block_ce4c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_ce4e:\n.option push\n.option norvc\nbne a0,a5,.Lcontrol_gates_edge_ce4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCE52..0xCE54. */
REGION void tsl9_control_gates_block_ce52(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    __builtin_unreachable();
}

/* Original0xCE54..0xCE58. */
REGION void tsl9_control_gates_block_ce54(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".Lcontrol_gates_edge_ce56:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce56\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ce6a\n");
    __builtin_unreachable();
}

/* Original0xCE58..0xCE5C. */
REGION void tsl9_control_gates_block_ce58(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce58:\n.option push\n.option norvc\nbeq a0,a1,.Lcontrol_gates_edge_ce58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce66\n");
    __builtin_unreachable();
}

/* Original0xCE5C..0xCE62. */
REGION void tsl9_control_gates_block_ce5c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_ce5e:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_ce5e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce72\n");
    __builtin_unreachable();
}

/* Original0xCE62..0xCE64. */
REGION void tsl9_control_gates_block_ce62(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce62:\n.option push\n.option rvc\nc.beqz s0,.Lcontrol_gates_edge_ce62\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_ce74\n");
    __builtin_unreachable();
}

/* Original0xCE64..0xCE66. */
REGION void tsl9_control_gates_block_ce64(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce64:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ce68\n");
    __builtin_unreachable();
}

/* Original0xCE66..0xCE68. */
REGION void tsl9_control_gates_block_ce66(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce66:\n.option push\n.option rvc\nc.beqz s0,.Lcontrol_gates_edge_ce66\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCE68..0xCE6A. */
REGION void tsl9_control_gates_block_ce68(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    __builtin_unreachable();
}

/* Original0xCE6A..0xCE6E. */
REGION void tsl9_control_gates_block_ce6a(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce6a:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_ce6a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0xCE6E..0xCE70. */
REGION void tsl9_control_gates_block_ce6e(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce6e:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce6e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cdd8\n");
    __builtin_unreachable();
}

/* Original0xCE70..0xCE72. */
REGION void tsl9_control_gates_block_ce70(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce70:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce70\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCE72..0xCE74. */
REGION void tsl9_control_gates_block_ce72(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce72:\n.option push\n.option rvc\nc.bnez s0,.Lcontrol_gates_edge_ce72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_cd9e\n");
    __builtin_unreachable();
}

/* Original0xCE74..0xCE7A. */
REGION void tsl9_control_gates_block_ce74(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".Lcontrol_gates_edge_ce78:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ce6a\n");
    __builtin_unreachable();
}

/* Original0xCE7A..0xCE7E. */
REGION void tsl9_control_gates_block_ce7a(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce7a:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_ce7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce84\n");
    __builtin_unreachable();
}

/* Original0xCE7E..0xCE82. */
REGION void tsl9_control_gates_block_ce7e(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce7e:\n.option push\n.option norvc\nbne a0,a1,.Lcontrol_gates_edge_ce7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ce62\n");
    __builtin_unreachable();
}

/* Original0xCE82..0xCE84. */
REGION void tsl9_control_gates_block_ce82(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_ce82:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce82\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ce52\n");
    __builtin_unreachable();
}

/* Original0xCE84..0xCE88. */
REGION void tsl9_control_gates_block_ce84(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lcontrol_gates_edge_ce86:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ce86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ce54\n");
    __builtin_unreachable();
}

/* Original0xD07C..0xD088. */
REGION void tsl9_record_dispatch_provider_d07c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffec8)); LIVE;
    PORT(".Lcontrol_gates_edge_d084:\n.option push\n.option norvc\nbeq a5,a0,.Lcontrol_gates_edge_d084\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_d0ec\n");
    __builtin_unreachable();
}

/* Original0xD088..0xD094. */
REGION void tsl9_control_gates_block_d088(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lcontrol_gates_edge_d090:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_d090\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xD094..0xD09A. */
REGION void tsl9_control_gates_block_d094(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lcontrol_gates_edge_d096:\n.option push\n.option norvc\nbltu a5,a0,.Lcontrol_gates_edge_d096\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_d0cc\n");
    __builtin_unreachable();
}

/* Original0xD09A..0xD0A0. */
REGION void tsl9_control_gates_block_d09a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lcontrol_gates_edge_d09e:\n.option push\n.option rvc\nc.bnez a5,.Lcontrol_gates_edge_d09e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_d0de\n");
    __builtin_unreachable();
}

/* Original0xD0A0..0xD0A6. */
REGION void tsl9_control_gates_block_d0a0(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_d0a2:\n.option push\n.option norvc\nbeq s0,a5,.Lcontrol_gates_edge_d0a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_d0d4\n");
    __builtin_unreachable();
}

/* Original0xD0A6..0xD0AC. */
REGION void tsl9_control_gates_block_d0a6(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lcontrol_gates_edge_d0a8:\n.option push\n.option norvc\nbeq s0,a5,.Lcontrol_gates_edge_d0a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_d0bc\n");
    __builtin_unreachable();
}

/* Original0xD0AC..0xD0B2. */
REGION void tsl9_control_gates_block_d0ac(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_d0ae:\n.option push\n.option norvc\nbne s0,a5,.Lcontrol_gates_edge_d0ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_d0cc\n");
    __builtin_unreachable();
}

/* Original0xD0B2..0xD0BC. */
REGION void tsl9_control_gates_block_d0b2(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    a5 = a5 + UINT32_C(0x00000501); LIVE;
    PORT(".Lcontrol_gates_edge_d0ba:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_d0ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_d0c4\n");
    __builtin_unreachable();
}

/* Original0xD0BC..0xD0C4. */
REGION void tsl9_control_gates_block_d0bc(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    a5 = a5 + UINT32_C(0x00000401); LIVE;
    __builtin_unreachable();
}

/* Original0xD0C4..0xD0CC. */
REGION void tsl9_control_gates_block_d0c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xfffffe74)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xD0CC..0xD0D4. */
REGION void tsl9_control_gates_block_d0cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD0D4..0xD0DE. */
REGION void tsl9_control_gates_block_d0d4(void)
{
    REGS;
    a5 = UINT32_C(0x01000000); LIVE;
    a5 = a5 + UINT32_C(0x00000201); LIVE;
    PORT(".Lcontrol_gates_edge_d0dc:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_d0dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_d0c4\n");
    __builtin_unreachable();
}

/* Original0xD0DE..0xD0EC. */
REGION void tsl9_control_gates_block_d0de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcontrol_gates_edge_d0e8:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_d0e8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_10022\n");
    __builtin_unreachable();
}

/* Original0xD0EC..0xD0EE. */
REGION void tsl9_control_gates_block_d0ec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD0EE..0xD104. */
REGION void tsl9_main_services_provider_d0ee(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffe3e); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFB1E..0xFB26. */
REGION void tsl9_control_gates_provider_fb1e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb22:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fb22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a9de\n");
    __builtin_unreachable();
}

/* Original0xFB26..0xFB2C. */
REGION void tsl9_control_gates_block_fb26(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_fb28:\n.option push\n.option norvc\nbeq a0,a5,.Lcontrol_gates_edge_fb28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fb4e\n");
    __builtin_unreachable();
}

/* Original0xFB2C..0xFB32. */
REGION void tsl9_control_gates_block_fb2c(void)
{
    REGS;
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".Lcontrol_gates_edge_fb2e:\n.option push\n.option norvc\nbeq a0,a4,.Lcontrol_gates_edge_fb2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fb4e\n");
    __builtin_unreachable();
}

/* Original0xFB32..0xFB4E. */
REGION void tsl9_control_gates_block_fb32(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000005dc); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcontrol_gates_literal_fb40:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_fb40\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb4a:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_fb4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xFB4E..0xFB5E. */
REGION void tsl9_control_gates_block_fb4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".Lcontrol_gates_literal_fb50:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_fb50\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb5a:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_fb5a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFB5E..0xFB66. */
REGION void tsl9_control_gates_provider_fb5e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb62:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fb62\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a9de\n");
    __builtin_unreachable();
}

/* Original0xFB66..0xFB6C. */
REGION void tsl9_control_gates_block_fb66(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lcontrol_gates_edge_fb68:\n.option push\n.option norvc\nbne a0,a5,.Lcontrol_gates_edge_fb68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fb8e\n");
    __builtin_unreachable();
}

/* Original0xFB6C..0xFB8E. */
REGION void tsl9_control_gates_block_fb6c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000123)) = (uint8_t)0; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000005dc); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcontrol_gates_literal_fb80:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_fb80\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb8a:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_fb8a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xFB8E..0xFBA2. */
REGION void tsl9_control_gates_block_fb8e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)0; LIVE;
    PORT(".Lcontrol_gates_literal_fb94:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_fb94\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fb9e:\n.option push\n.option norvc\njal zero,.Lcontrol_gates_edge_fb9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFD6A..0xFD70. */
REGION void tsl9_record_dispatch_provider_fd6a(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lcontrol_gates_edge_fd6c:\n.option push\n.option norvc\nbne a0,a5,.Lcontrol_gates_edge_fd6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fd9a\n");
    __builtin_unreachable();
}

/* Original0xFD70..0xFD76. */
REGION void tsl9_control_gates_block_fd70(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000122)); LIVE;
    PORT(".Lcontrol_gates_edge_fd74:\n.option push\n.option rvc\nc.beqz a4,.Lcontrol_gates_edge_fd74\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fd86\n");
    __builtin_unreachable();
}

/* Original0xFD76..0xFD7E. */
REGION void tsl9_control_gates_block_fd76(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_fd7a:\n.option push\n.option norvc\nbeq a4,a3,.Lcontrol_gates_edge_fd7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fd80\n");
    __builtin_unreachable();
}

/* Original0xFD7E..0xFD80. */
REGION void tsl9_control_gates_block_fd7e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xFD80..0xFD86. */
REGION void tsl9_control_gates_block_fd80(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000122)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFD86..0xFD96. */
REGION void tsl9_control_gates_block_fd86(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffc\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004d1)); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_fd92:\n.option push\n.option norvc\nbne a4,a5,.Lcontrol_gates_edge_fd92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fd80\n");
    __builtin_unreachable();
}

/* Original0xFD96..0xFD9A. */
REGION void tsl9_control_gates_block_fd96(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_fd98:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_fd98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_fd80\n");
    __builtin_unreachable();
}

/* Original0xFD9A..0xFDA0. */
REGION void tsl9_control_gates_block_fd9a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000122)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFDF6..0xFE02. */
REGION void tsl9_record_dispatch_provider_fdf6(void)
{
    REGS;
    a5 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    PORT(".Lcontrol_gates_edge_fe00:\n.option push\n.option rvc\nc.bnez a0,.Lcontrol_gates_edge_fe00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fe06\n");
    __builtin_unreachable();
}

/* Original0xFE02..0xFE06. */
REGION void tsl9_control_gates_block_fe02(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000123)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xFE06..0xFE08. */
REGION void tsl9_control_gates_block_fe06(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFE6A..0xFE7A. */
REGION void tsl9_control_gates_provider_fe6a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000009)); LIVE;
    a4 = a4 & UINT32_C(0x0000000c); LIVE;
    PORT(".Lcontrol_gates_edge_fe76:\n.option push\n.option norvc\nbeqz a4,.Lcontrol_gates_edge_fe76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ff42\n");
    __builtin_unreachable();
}

/* Original0xFE7A..0xFE8A. */
REGION void tsl9_control_gates_block_fe7a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fe86:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fe86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_guard_828c\n");
    __builtin_unreachable();
}

/* Original0xFE8A..0xFE8C. */
REGION void tsl9_control_gates_block_fe8a(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fe8a:\n.option push\n.option rvc\nc.beqz a0,.Lcontrol_gates_edge_fe8a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFE8C..0xFE8E. */
REGION void tsl9_control_gates_block_fe8c(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fe8c:\n.option push\n.option rvc\nc.beqz s1,.Lcontrol_gates_edge_fe8c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_ff16\n");
    __builtin_unreachable();
}

/* Original0xFE8E..0xFE92. */
REGION void tsl9_control_gates_block_fe8e(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fe8e:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fe8e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a9de\n");
    __builtin_unreachable();
}

/* Original0xFE92..0xFE9C. */
REGION void tsl9_control_gates_block_fe92(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000124)); LIVE;
    PORT(".Lcontrol_gates_edge_fe98:\n.option push\n.option norvc\nbeq a0,a4,.Lcontrol_gates_edge_fe98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fea2\n");
    __builtin_unreachable();
}

/* Original0xFE9C..0xFEA2. */
REGION void tsl9_control_gates_block_fe9c(void)
{
    REGS;
    a4 = UINT32_C(0x00000007); LIVE;
    PORT(".Lcontrol_gates_edge_fe9e:\n.option push\n.option norvc\nbne a0,a4,.Lcontrol_gates_edge_fe9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_feee\n");
    __builtin_unreachable();
}

/* Original0xFEA2..0xFEA4. */
REGION void tsl9_control_gates_block_fea2(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fea2:\n.option push\n.option rvc\nc.bnez a5,.Lcontrol_gates_edge_fea2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFEA4..0xFEA8. */
REGION void tsl9_control_gates_block_fea4(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fea4:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fea4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xFEA8..0xFEB4. */
REGION void tsl9_control_gates_block_fea8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x00000128)) = (uint32_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000123)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcontrol_gates_edge_feb2:\n.option push\n.option rvc\nc.bnez a4,.Lcontrol_gates_edge_feb2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_febe\n");
    __builtin_unreachable();
}

/* Original0xFEB4..0xFEBE. */
REGION void tsl9_control_gates_block_feb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0xFEBE..0xFECE. */
REGION void tsl9_control_gates_block_febe(void)
{
    REGS;
    PORT(".Lcontrol_gates_literal_febe:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_febe\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000124)) = (uint8_t)a5; LIVE;
    PORT(".Lcontrol_gates_edge_feca:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_feca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFECE..0xFEDA. */
REGION void tsl9_control_gates_block_fece(void)
{
    REGS;
    PORT(".Lcontrol_gates_literal_fece:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_fece\n.option pop\n");
    PORT(".Lcontrol_gates_edge_fed6:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fed6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFEDA..0xFEE4. */
REGION void tsl9_control_gates_block_feda(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000123)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xFEE4..0xFEEE. */
REGION void tsl9_control_gates_block_fee4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFEEE..0xFEF0. */
REGION void tsl9_control_gates_block_feee(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_feee:\n.option push\n.option rvc\nc.beqz a5,.Lcontrol_gates_edge_feee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFEF0..0xFEF6. */
REGION void tsl9_control_gates_block_fef0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)); LIVE;
    PORT(".Lcontrol_gates_edge_fef4:\n.option push\n.option rvc\nc.bnez a5,.Lcontrol_gates_edge_fef4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFEF6..0xFEFA. */
REGION void tsl9_control_gates_block_fef6(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fef6:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fef6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_81ee\n");
    __builtin_unreachable();
}

/* Original0xFEFA..0xFEFC. */
REGION void tsl9_control_gates_block_fefa(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fefa:\n.option push\n.option rvc\nc.bnez a0,.Lcontrol_gates_edge_fefa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFEFC..0xFF00. */
REGION void tsl9_control_gates_block_fefc(void)
{
    REGS;
    PORT(".Lcontrol_gates_edge_fefc:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_fefc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xFF00..0xFF10. */
REGION void tsl9_control_gates_block_ff00(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000128); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = a0 - a5; LIVE;
    a5 = UINT32_C(0x000005db); LIVE;
    PORT(".Lcontrol_gates_edge_ff0c:\n.option push\n.option norvc\nbleu a0,a5,.Lcontrol_gates_edge_ff0c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFF10..0xFF16. */
REGION void tsl9_control_gates_block_ff10(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000124)) = (uint8_t)0; LIVE;
    PORT(".Lcontrol_gates_edge_ff14:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ff14\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFF16..0xFF1C. */
REGION void tsl9_control_gates_block_ff16(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000124)); LIVE;
    PORT(".Lcontrol_gates_edge_ff1a:\n.option push\n.option rvc\nc.beqz a5,.Lcontrol_gates_edge_ff1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_fee4\n");
    __builtin_unreachable();
}

/* Original0xFF1C..0xFF22. */
REGION void tsl9_control_gates_block_ff1c(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcontrol_gates_edge_ff1e:\n.option push\n.option norvc\nbne a5,a4,.Lcontrol_gates_edge_ff1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_control_gates_block_ff10\n");
    __builtin_unreachable();
}

/* Original0xFF22..0xFF2E. */
REGION void tsl9_control_gates_block_ff22(void)
{
    REGS;
    PORT(".Lcontrol_gates_literal_ff22:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb1e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_ff22\n.option pop\n");
    PORT(".Lcontrol_gates_edge_ff2a:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_ff2a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFF2E..0xFF3A. */
REGION void tsl9_control_gates_block_ff2e(void)
{
    REGS;
    PORT(".Lcontrol_gates_literal_ff2e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_control_gates_provider_fb5e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcontrol_gates_literal_ff2e\n.option pop\n");
    PORT(".Lcontrol_gates_edge_ff36:\n.option push\n.option norvc\njal ra,.Lcontrol_gates_edge_ff36\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xFF3A..0xFF42. */
REGION void tsl9_control_gates_block_ff3a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000120)) = (uint8_t)a5; LIVE;
    PORT(".Lcontrol_gates_edge_ff40:\n.option push\n.option rvc\nc.j .Lcontrol_gates_edge_ff40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_control_gates_block_ff10\n");
    __builtin_unreachable();
}

/* Original0xFF42..0xFF44. */
REGION void tsl9_control_gates_block_ff42(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10022..0x1002A. */
REGION void tsl9_control_gates_provider_10022(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012c)) = (uint8_t)a0; LIVE;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lcontrol_gates_edge_10028:\n.option push\n.option rvc\nc.bnez a1,.Lcontrol_gates_edge_10028\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_control_gates_block_1002c\n");
    __builtin_unreachable();
}

/* Original0x1002A..0x1002C. */
REGION void tsl9_control_gates_block_1002a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1002C..0x10032. */
REGION void tsl9_control_gates_block_1002c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012d)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
