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

/* Four complete original record-dispatch functions:3904B/1571i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x10DCC..0x10DDE. */
REGION void tsl9_registered_callbacks_provider_10dcc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000215)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)); LIVE;
    PORT(".Lrecord_dispatch_edge_10ddc:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_dispatch_edge_10ddc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_10e6c\n");
    __builtin_unreachable();
}

/* Original0x10DDE..0x10DE8. */
REGION void tsl9_record_dispatch_block_10dde(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000058); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = a5 + UINT32_C(0x000000fc); LIVE;
    __builtin_unreachable();
}

/* Original0x10DE8..0x10DF6. */
REGION void tsl9_record_dispatch_block_10de8(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".Lrecord_dispatch_edge_10df4:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_dispatch_edge_10df4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_10e6c\n");
    __builtin_unreachable();
}

/* Original0x10DF6..0x10DFC. */
REGION void tsl9_record_dispatch_block_10df6(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_dispatch_edge_10df8:\n.option push\n.option norvc\nbne a5,a3,.Lrecord_dispatch_edge_10df8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_10de8\n");
    __builtin_unreachable();
}

/* Original0x10DFC..0x10E0C. */
REGION void tsl9_record_dispatch_block_10dfc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_10e08:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_10e08\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_10d9a\n");
    __builtin_unreachable();
}

/* Original0x10E0C..0x10E12. */
REGION void tsl9_record_dispatch_block_10e0c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_dispatch_edge_10e0e:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_dispatch_edge_10e0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_10e3c\n");
    __builtin_unreachable();
}

/* Original0x10E12..0x10E20. */
REGION void tsl9_record_dispatch_block_10e12(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s1, 129\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E20..0x10E32. */
REGION void tsl9_record_dispatch_block_10e20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 64(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E32..0x10E34. */
REGION void tsl9_record_dispatch_block_10e32(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_10e32:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_dispatch_edge_10e32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_10e4a\n");
    __builtin_unreachable();
}

/* Original0x10E34..0x10E3C. */
REGION void tsl9_record_dispatch_block_10e34(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 43\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_10e38:\n.option push\n.option norvc\nbne s0,s1,.Lrecord_dispatch_edge_10e38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_10e20\n");
    __builtin_unreachable();
}

/* Original0x10E3C..0x10E4A. */
REGION void tsl9_record_dispatch_block_10e3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E4A..0x10E6A. */
REGION void tsl9_record_dispatch_block_10e4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000178)); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E6A..0x10E6C. */
REGION void tsl9_record_dispatch_block_10e6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E6C..0x10E82. */
REGION void tsl9_record_dispatch_block_10e6c(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000015c)); LIVE;
    PORT(".Lrecord_dispatch_edge_10e80:\n.option push\n.option rvc\nc.j .Lrecord_dispatch_edge_10e80\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_block_10e6a\n");
    __builtin_unreachable();
}

/* Original0x13EB4..0x13EB6. */
REGION void tsl9_callback_dependencies_provider_13eb4(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_13eb4:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_dispatch_edge_13eb4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_13f34\n");
    __builtin_unreachable();
}

/* Original0x13EB6..0x13EDC. */
REGION void tsl9_record_dispatch_block_13eb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s2, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s4, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, -1848\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, -2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, a0, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13EDC..0x13EEA. */
REGION void tsl9_record_dispatch_block_13edc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a5, s1, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s4\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lrecord_dispatch_edge_13ee6:\n.option push\n.option norvc\nbeq s2,a4,.Lrecord_dispatch_edge_13ee6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_13f10\n");
    __builtin_unreachable();
}

/* Original0x13EEA..0x13EF4. */
REGION void tsl9_record_dispatch_block_13eea(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_dispatch_edge_13ef2:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_dispatch_edge_13ef2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_13f10\n");
    __builtin_unreachable();
}

/* Original0x13EF4..0x13EFE. */
REGION void tsl9_record_dispatch_block_13ef4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_dispatch_edge_13efc:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_dispatch_edge_13efc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_13f10\n");
    __builtin_unreachable();
}

/* Original0x13EFE..0x13F10. */
REGION void tsl9_record_dispatch_block_13efe(void)
{
    REGS;
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s5\n.option pop\n");
    a1 = UINT32_C(0x000000ba); LIVE;
    PORT(".Lrecord_dispatch_edge_13f0c:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_13f0c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x13F10..0x13F14. */
REGION void tsl9_record_dispatch_block_13f10(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_13f10:\n.option push\n.option norvc\nbne s1,s3,.Lrecord_dispatch_edge_13f10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_13f30\n");
    __builtin_unreachable();
}

/* Original0x13F14..0x13F30. */
REGION void tsl9_record_dispatch_block_13f14(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 104(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13F30..0x13F34. */
REGION void tsl9_record_dispatch_block_13f30(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_13f32:\n.option push\n.option rvc\nc.j .Lrecord_dispatch_edge_13f32\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_block_13edc\n");
    __builtin_unreachable();
}

/* Original0x13F34..0x13F36. */
REGION void tsl9_record_dispatch_block_13f34(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x155D0..0x155E8. */
REGION void tsl9_callback_dependencies_provider_155d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, gp, 84\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_dispatch_edge_155e6:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_dispatch_edge_155e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_155f6\n");
    __builtin_unreachable();
}

/* Original0x155E8..0x155F6. */
REGION void tsl9_record_dispatch_block_155e8(void)
{
    REGS;
    a5 = a0 + UINT32_C(0x00000006); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_dispatch_edge_155f2:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_dispatch_edge_155f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_1578c\n");
    __builtin_unreachable();
}

/* Original0x155F6..0x155FC. */
REGION void tsl9_record_dispatch_block_155f6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000166)); LIVE;
    PORT(".Lrecord_dispatch_edge_155fa:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_dispatch_edge_155fa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_1560e\n");
    __builtin_unreachable();
}

/* Original0x155FC..0x1560E. */
REGION void tsl9_record_dispatch_block_155fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000166)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1560a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1560a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_18110\n");
    __builtin_unreachable();
}

/* Original0x1560E..0x1561E. */
REGION void tsl9_record_dispatch_block_1560e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, a0, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a4, s2, 255\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1561a:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_dispatch_edge_1561a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_15630\n");
    __builtin_unreachable();
}

/* Original0x1561E..0x15630. */
REGION void tsl9_record_dispatch_block_1561e(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_dispatch_literal_15624:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_1552a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_dispatch_literal_15624\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1562c:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1562c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x15630..0x1563C. */
REGION void tsl9_record_dispatch_block_15630(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s2, s2, 255\n.option pop\n");
    a5 = UINT32_C(0x000000fc); LIVE;
    PORT(".Lrecord_dispatch_edge_15638:\n.option push\n.option norvc\nbltu a5,s2,.Lrecord_dispatch_edge_15638\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_1578c\n");
    __builtin_unreachable();
}

/* Original0x1563C..0x15650. */
REGION void tsl9_record_dispatch_block_1563c(void)
{
    REGS;
    PORT(".Lrecord_dispatch_literal_1563c:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_table_1a6f4\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_dispatch_literal_1563c\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s2, s2, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x15650..0x15666. */
REGION void tsl9_record_dispatch_block_15650(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15662:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15662\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x15666..0x1567C. */
REGION void tsl9_record_dispatch_block_15666(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15678:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15678\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x1567C..0x15694. */
REGION void tsl9_record_dispatch_block_1567c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000080); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15690:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15690\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x15694..0x156AC. */
REGION void tsl9_record_dispatch_block_15694(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_156a8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_156a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x156AC..0x156C2. */
REGION void tsl9_record_dispatch_block_156ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_156be:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_156be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x156C2..0x156D8. */
REGION void tsl9_record_dispatch_block_156c2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_156d4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_156d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x156D8..0x156F0. */
REGION void tsl9_record_dispatch_block_156d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_156ec:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_156ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x156F0..0x15706. */
REGION void tsl9_record_dispatch_block_156f0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15702:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15702\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x15706..0x15714. */
REGION void tsl9_record_dispatch_block_15706(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15710:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15710\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f63c\n");
    __builtin_unreachable();
}

/* Original0x15714..0x15724. */
REGION void tsl9_record_dispatch_block_15714(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15720:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15720\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15724..0x15734. */
REGION void tsl9_record_dispatch_block_15724(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15730:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15730\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15734..0x15744. */
REGION void tsl9_record_dispatch_block_15734(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15740:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15740\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15744..0x15754. */
REGION void tsl9_record_dispatch_block_15744(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15750:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15750\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15754..0x1576A. */
REGION void tsl9_record_dispatch_block_15754(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, -14\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15766:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15766\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f998\n");
    __builtin_unreachable();
}

/* Original0x1576A..0x15774. */
REGION void tsl9_record_dispatch_block_1576a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_dispatch_edge_15772:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_dispatch_edge_15772\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_15786\n");
    __builtin_unreachable();
}

/* Original0x15774..0x15786. */
REGION void tsl9_record_dispatch_block_15774(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15782:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15782\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0x15786..0x1578A. */
REGION void tsl9_record_dispatch_block_15786(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15786:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15786\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x1578A..0x1578C. */
REGION void tsl9_record_dispatch_block_1578a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1578a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_dispatch_edge_1578a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_15774\n");
    __builtin_unreachable();
}

/* Original0x1578C..0x15798. */
REGION void tsl9_record_dispatch_block_1578c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x15798..0x157AA. */
REGION void tsl9_record_dispatch_block_15798(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_157a6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_157a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0x157AA..0x157B4. */
REGION void tsl9_record_dispatch_block_157aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_dispatch_edge_157b2:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_dispatch_edge_157b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_157d0\n");
    __builtin_unreachable();
}

/* Original0x157B4..0x157B8. */
REGION void tsl9_record_dispatch_block_157b4(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157b4:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_157b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0x157B8..0x157D0. */
REGION void tsl9_record_dispatch_block_157b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_157cc:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_157cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0x157D0..0x157D4. */
REGION void tsl9_record_dispatch_block_157d0(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157d0:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_157d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x157D4..0x157D6. */
REGION void tsl9_record_dispatch_block_157d4(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157d4:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_dispatch_edge_157d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_1578c\n");
    __builtin_unreachable();
}

/* Original0x157D6..0x157D8. */
REGION void tsl9_record_dispatch_block_157d6(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157d6:\n.option push\n.option rvc\nc.j .Lrecord_dispatch_edge_157d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_block_157b4\n");
    __builtin_unreachable();
}

/* Original0x157D8..0x157DC. */
REGION void tsl9_record_dispatch_block_157d8(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157d8:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_157d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x157DC..0x157F2. */
REGION void tsl9_record_dispatch_block_157dc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_157ee:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_157ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0x157F2..0x157F6. */
REGION void tsl9_record_dispatch_block_157f2(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157f2:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_157f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x157F6..0x157F8. */
REGION void tsl9_record_dispatch_block_157f6(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_157f6:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_dispatch_edge_157f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_1578c\n");
    __builtin_unreachable();
}

/* Original0x157F8..0x15808. */
REGION void tsl9_record_dispatch_block_157f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15804:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15804\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0x15808..0x1580C. */
REGION void tsl9_record_dispatch_block_15808(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15808:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15808\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x1580C..0x1580E. */
REGION void tsl9_record_dispatch_block_1580c(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1580c:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_dispatch_edge_1580c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_1578c\n");
    __builtin_unreachable();
}

/* Original0x1580E..0x1581E. */
REGION void tsl9_record_dispatch_block_1580e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1581a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1581a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0x1581E..0x1582C. */
REGION void tsl9_record_dispatch_block_1581e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15828:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15828\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_e1a6\n");
    __builtin_unreachable();
}

/* Original0x1582C..0x15830. */
REGION void tsl9_record_dispatch_block_1582c(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1582c:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1582c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_faf2\n");
    __builtin_unreachable();
}

/* Original0x15830..0x15846. */
REGION void tsl9_record_dispatch_block_15830(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15842:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15842\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fae6\n");
    __builtin_unreachable();
}

/* Original0x15846..0x15854. */
REGION void tsl9_record_dispatch_block_15846(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15850:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15850\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f630\n");
    __builtin_unreachable();
}

/* Original0x15854..0x15864. */
REGION void tsl9_record_dispatch_block_15854(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15860:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15860\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f0c6\n");
    __builtin_unreachable();
}

/* Original0x15864..0x15874. */
REGION void tsl9_record_dispatch_block_15864(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15870:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15870\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0x15874..0x15884. */
REGION void tsl9_record_dispatch_block_15874(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15880:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15880\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0x15884..0x15888. */
REGION void tsl9_record_dispatch_block_15884(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15884:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15884\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d314\n");
    __builtin_unreachable();
}

/* Original0x15888..0x1589E. */
REGION void tsl9_record_dispatch_block_15888(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1589a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1589a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0x1589E..0x158A2. */
REGION void tsl9_record_dispatch_block_1589e(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1589e:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1589e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original0x158A2..0x158B8. */
REGION void tsl9_record_dispatch_block_158a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_158b4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_158b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d3c6\n");
    __builtin_unreachable();
}

/* Original0x158B8..0x158C8. */
REGION void tsl9_record_dispatch_block_158b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_158c4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_158c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d3c6\n");
    __builtin_unreachable();
}

/* Original0x158C8..0x158D8. */
REGION void tsl9_record_dispatch_block_158c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_158d4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_158d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d3c6\n");
    __builtin_unreachable();
}

/* Original0x158D8..0x158DC. */
REGION void tsl9_record_dispatch_block_158d8(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_158d8:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_158d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f67e\n");
    __builtin_unreachable();
}

/* Original0x158DC..0x158F2. */
REGION void tsl9_record_dispatch_block_158dc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_158ee:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_158ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f672\n");
    __builtin_unreachable();
}

/* Original0x158F2..0x15902. */
REGION void tsl9_record_dispatch_block_158f2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_158fe:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_158fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f672\n");
    __builtin_unreachable();
}

/* Original0x15902..0x15912. */
REGION void tsl9_record_dispatch_block_15902(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1590e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1590e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f672\n");
    __builtin_unreachable();
}

/* Original0x15912..0x15920. */
REGION void tsl9_record_dispatch_block_15912(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1591c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1591c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_deec\n");
    __builtin_unreachable();
}

/* Original0x15920..0x1592E. */
REGION void tsl9_record_dispatch_block_15920(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1592a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1592a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_e042\n");
    __builtin_unreachable();
}

/* Original0x1592E..0x1593C. */
REGION void tsl9_record_dispatch_block_1592e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15938:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15938\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_e048\n");
    __builtin_unreachable();
}

/* Original0x1593C..0x15940. */
REGION void tsl9_record_dispatch_block_1593c(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1593c:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1593c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7ec\n");
    __builtin_unreachable();
}

/* Original0x15940..0x15956. */
REGION void tsl9_record_dispatch_block_15940(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15952:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15952\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7dc\n");
    __builtin_unreachable();
}

/* Original0x15956..0x1595A. */
REGION void tsl9_record_dispatch_block_15956(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15956:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15956\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f80a\n");
    __builtin_unreachable();
}

/* Original0x1595A..0x15970. */
REGION void tsl9_record_dispatch_block_1595a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1596c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1596c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f800\n");
    __builtin_unreachable();
}

/* Original0x15970..0x15980. */
REGION void tsl9_record_dispatch_block_15970(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1597c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1597c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x15980..0x15990. */
REGION void tsl9_record_dispatch_block_15980(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1598c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1598c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x15990..0x159A2. */
REGION void tsl9_record_dispatch_block_15990(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1599e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1599e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x159A2..0x159B4. */
REGION void tsl9_record_dispatch_block_159a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_159b0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_159b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x159B4..0x159C6. */
REGION void tsl9_record_dispatch_block_159b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_159c2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_159c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x159C6..0x159D8. */
REGION void tsl9_record_dispatch_block_159c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_159d4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_159d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x159D8..0x159EA. */
REGION void tsl9_record_dispatch_block_159d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_159e6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_159e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ec\n");
    __builtin_unreachable();
}

/* Original0x159EA..0x159FC. */
REGION void tsl9_record_dispatch_block_159ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_159f8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_159f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ec\n");
    __builtin_unreachable();
}

/* Original0x159FC..0x15A0E. */
REGION void tsl9_record_dispatch_block_159fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a0a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a0a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x15A0E..0x15A20. */
REGION void tsl9_record_dispatch_block_15a0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a1c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a1c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x15A20..0x15A32. */
REGION void tsl9_record_dispatch_block_15a20(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a2e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a2e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f71e\n");
    __builtin_unreachable();
}

/* Original0x15A32..0x15A44. */
REGION void tsl9_record_dispatch_block_15a32(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a40:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a40\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f71e\n");
    __builtin_unreachable();
}

/* Original0x15A44..0x15A48. */
REGION void tsl9_record_dispatch_block_15a44(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15a44:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15a44\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7d2\n");
    __builtin_unreachable();
}

/* Original0x15A48..0x15A60. */
REGION void tsl9_record_dispatch_block_15a48(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a5c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a5c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f796\n");
    __builtin_unreachable();
}

/* Original0x15A60..0x15A72. */
REGION void tsl9_record_dispatch_block_15a60(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a6e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f796\n");
    __builtin_unreachable();
}

/* Original0x15A72..0x15A84. */
REGION void tsl9_record_dispatch_block_15a72(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a80:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f796\n");
    __builtin_unreachable();
}

/* Original0x15A84..0x15A88. */
REGION void tsl9_record_dispatch_block_15a84(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15a84:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15a84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f822\n");
    __builtin_unreachable();
}

/* Original0x15A88..0x15A9C. */
REGION void tsl9_record_dispatch_block_15a88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15a98:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15a98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f818\n");
    __builtin_unreachable();
}

/* Original0x15A9C..0x15AAC. */
REGION void tsl9_record_dispatch_block_15a9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15aa8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15aa8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f818\n");
    __builtin_unreachable();
}

/* Original0x15AAC..0x15ABC. */
REGION void tsl9_record_dispatch_block_15aac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ab8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ab8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f818\n");
    __builtin_unreachable();
}

/* Original0x15ABC..0x15ACC. */
REGION void tsl9_record_dispatch_block_15abc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 0(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nseqz s0, a5\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15aca:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_dispatch_edge_15aca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_15ace\n");
    __builtin_unreachable();
}

/* Original0x15ACC..0x15ACE. */
REGION void tsl9_record_dispatch_block_15acc(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x15ACE..0x15ADC. */
REGION void tsl9_record_dispatch_block_15ace(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a2 = a5 >> UINT32_C(0x00000001); LIVE;
    a2 = a2 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_dispatch_edge_15ad8:\n.option push\n.option norvc\nbeq a2,a4,.Lrecord_dispatch_edge_15ad8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_15aea\n");
    __builtin_unreachable();
}

/* Original0x15ADC..0x15AEA. */
REGION void tsl9_record_dispatch_block_15adc(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0xfffffff9); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_dispatch_edge_15ae6:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15ae6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13138\n");
    __builtin_unreachable();
}

/* Original0x15AEA..0x15AEE. */
REGION void tsl9_record_dispatch_block_15aea(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15aea:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15aea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_a6aa\n");
    __builtin_unreachable();
}

/* Original0x15AEE..0x15AFE. */
REGION void tsl9_record_dispatch_block_15aee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15afa:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15afa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0x15AFE..0x15B0C. */
REGION void tsl9_record_dispatch_block_15afe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 0(s1)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a4 = a5 >> UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_dispatch_edge_15b0a:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_dispatch_edge_15b0a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_dispatch_block_15b16\n");
    __builtin_unreachable();
}

/* Original0x15B0C..0x15B0E. */
REGION void tsl9_record_dispatch_block_15b0c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffff9); LIVE;
    __builtin_unreachable();
}

/* Original0x15B0E..0x15B16. */
REGION void tsl9_record_dispatch_block_15b0e(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_dispatch_edge_15b12:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15b12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13138\n");
    __builtin_unreachable();
}

/* Original0x15B16..0x15B24. */
REGION void tsl9_record_dispatch_block_15b16(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15b20:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15b20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_a6aa\n");
    __builtin_unreachable();
}

/* Original0x15B24..0x15B3A. */
REGION void tsl9_record_dispatch_block_15b24(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 0(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a4 = a5 >> UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    a5 = a5 | UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_dispatch_edge_15b36:\n.option push\n.option norvc\nbeq a4,a2,.Lrecord_dispatch_edge_15b36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_15b16\n");
    __builtin_unreachable();
}

/* Original0x15B3A..0x15B3C. */
REGION void tsl9_record_dispatch_block_15b3a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15b3a:\n.option push\n.option rvc\nc.j .Lrecord_dispatch_edge_15b3a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_block_15b0e\n");
    __builtin_unreachable();
}

/* Original0x15B3C..0x15B56. */
REGION void tsl9_record_dispatch_block_15b3c(void)
{
    REGS;
    a0 = UINT32_C(0x00000046); LIVE;
    PORT(".option push\n.option rvc\nsub a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15b52:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15b52\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f016\n");
    __builtin_unreachable();
}

/* Original0x15B56..0x15B5A. */
REGION void tsl9_record_dispatch_block_15b56(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15b56:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15b56\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_b5b4\n");
    __builtin_unreachable();
}

/* Original0x15B5A..0x15B70. */
REGION void tsl9_record_dispatch_block_15b5a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15b6c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15b6c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b594\n");
    __builtin_unreachable();
}

/* Original0x15B70..0x15B80. */
REGION void tsl9_record_dispatch_block_15b70(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15b7c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15b7c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b594\n");
    __builtin_unreachable();
}

/* Original0x15B80..0x15B90. */
REGION void tsl9_record_dispatch_block_15b80(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15b8c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15b8c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b594\n");
    __builtin_unreachable();
}

/* Original0x15B90..0x15B94. */
REGION void tsl9_record_dispatch_block_15b90(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15b90:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15b90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b584\n");
    __builtin_unreachable();
}

/* Original0x15B94..0x15BAA. */
REGION void tsl9_record_dispatch_block_15b94(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ba6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ba6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b572\n");
    __builtin_unreachable();
}

/* Original0x15BAA..0x15BBA. */
REGION void tsl9_record_dispatch_block_15baa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15bb6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15bb6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b572\n");
    __builtin_unreachable();
}

/* Original0x15BBA..0x15BCA. */
REGION void tsl9_record_dispatch_block_15bba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15bc6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15bc6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b572\n");
    __builtin_unreachable();
}

/* Original0x15BCA..0x15BDE. */
REGION void tsl9_record_dispatch_block_15bca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15bda:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15bda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x15BDE..0x15BF2. */
REGION void tsl9_record_dispatch_block_15bde(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15bee:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15bee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x15BF2..0x15C02. */
REGION void tsl9_record_dispatch_block_15bf2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15bfe:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15bfe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18218\n");
    __builtin_unreachable();
}

/* Original0x15C02..0x15C12. */
REGION void tsl9_record_dispatch_block_15c02(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c0e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c0e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18218\n");
    __builtin_unreachable();
}

/* Original0x15C12..0x15C26. */
REGION void tsl9_record_dispatch_block_15c12(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c22:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x15C26..0x15C3A. */
REGION void tsl9_record_dispatch_block_15c26(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c36:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c36\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x15C3A..0x15C4A. */
REGION void tsl9_record_dispatch_block_15c3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c46:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ef76\n");
    __builtin_unreachable();
}

/* Original0x15C4A..0x15C64. */
REGION void tsl9_record_dispatch_block_15c4a(void)
{
    REGS;
    a0 = UINT32_C(0x0000005a); LIVE;
    PORT(".option push\n.option rvc\nsub a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c60:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c60\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f016\n");
    __builtin_unreachable();
}

/* Original0x15C64..0x15C68. */
REGION void tsl9_record_dispatch_block_15c64(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15c64:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15c64\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_c35a\n");
    __builtin_unreachable();
}

/* Original0x15C68..0x15C7E. */
REGION void tsl9_record_dispatch_block_15c68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c7a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x15C7E..0x15C82. */
REGION void tsl9_record_dispatch_block_15c7e(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15c7e:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15c7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original0x15C82..0x15C9A. */
REGION void tsl9_record_dispatch_block_15c82(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15c96:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15c96\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x15C9A..0x15C9E. */
REGION void tsl9_record_dispatch_block_15c9a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15c9a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15c9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6b0\n");
    __builtin_unreachable();
}

/* Original0x15C9E..0x15CB6. */
REGION void tsl9_record_dispatch_block_15c9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15cb2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15cb2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x15CB6..0x15CBA. */
REGION void tsl9_record_dispatch_block_15cb6(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15cb6:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15cb6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f714\n");
    __builtin_unreachable();
}

/* Original0x15CBA..0x15CD2. */
REGION void tsl9_record_dispatch_block_15cba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15cce:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15cce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ec\n");
    __builtin_unreachable();
}

/* Original0x15CD2..0x15CD6. */
REGION void tsl9_record_dispatch_block_15cd2(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15cd2:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15cd2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6e2\n");
    __builtin_unreachable();
}

/* Original0x15CD6..0x15CEE. */
REGION void tsl9_record_dispatch_block_15cd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15cea:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15cea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x15CEE..0x15CF2. */
REGION void tsl9_record_dispatch_block_15cee(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15cee:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15cee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f746\n");
    __builtin_unreachable();
}

/* Original0x15CF2..0x15D0A. */
REGION void tsl9_record_dispatch_block_15cf2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d06:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f71e\n");
    __builtin_unreachable();
}

/* Original0x15D0A..0x15D0E. */
REGION void tsl9_record_dispatch_block_15d0a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15d0a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15d0a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f78c\n");
    __builtin_unreachable();
}

/* Original0x15D0E..0x15D26. */
REGION void tsl9_record_dispatch_block_15d0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d22:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d22\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f750\n");
    __builtin_unreachable();
}

/* Original0x15D26..0x15D38. */
REGION void tsl9_record_dispatch_block_15d26(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d34:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d34\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f750\n");
    __builtin_unreachable();
}

/* Original0x15D38..0x15D4A. */
REGION void tsl9_record_dispatch_block_15d38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d46:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f750\n");
    __builtin_unreachable();
}

/* Original0x15D4A..0x15D58. */
REGION void tsl9_record_dispatch_block_15d4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d54:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc60\n");
    __builtin_unreachable();
}

/* Original0x15D58..0x15D68. */
REGION void tsl9_record_dispatch_block_15d58(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d64:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d64\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d07c\n");
    __builtin_unreachable();
}

/* Original0x15D68..0x15D78. */
REGION void tsl9_record_dispatch_block_15d68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d74:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d07c\n");
    __builtin_unreachable();
}

/* Original0x15D78..0x15D88. */
REGION void tsl9_record_dispatch_block_15d78(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15d84:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15d84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d07c\n");
    __builtin_unreachable();
}

/* Original0x15D88..0x15D8C. */
REGION void tsl9_record_dispatch_block_15d88(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15d88:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15d88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x15D8C..0x15D94. */
REGION void tsl9_record_dispatch_block_15d8c(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_dispatch_edge_15d90:\n.option push\n.option norvc\nbeq a0,a4,.Lrecord_dispatch_edge_15d90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_dispatch_block_15d96\n");
    __builtin_unreachable();
}

/* Original0x15D94..0x15D96. */
REGION void tsl9_record_dispatch_block_15d94(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x15D96..0x15DA6. */
REGION void tsl9_record_dispatch_block_15d96(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15da2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15da2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d07c\n");
    __builtin_unreachable();
}

/* Original0x15DA6..0x15DB6. */
REGION void tsl9_record_dispatch_block_15da6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15db2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15db2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ef76\n");
    __builtin_unreachable();
}

/* Original0x15DB6..0x15DC6. */
REGION void tsl9_record_dispatch_block_15db6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15dc2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15dc2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ef76\n");
    __builtin_unreachable();
}

/* Original0x15DC6..0x15DD8. */
REGION void tsl9_record_dispatch_block_15dc6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15dd4:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15dd4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cd6a\n");
    __builtin_unreachable();
}

/* Original0x15DD8..0x15DEA. */
REGION void tsl9_record_dispatch_block_15dd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15de6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15de6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cd6a\n");
    __builtin_unreachable();
}

/* Original0x15DEA..0x15DFC. */
REGION void tsl9_record_dispatch_block_15dea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15df8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15df8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cd6a\n");
    __builtin_unreachable();
}

/* Original0x15DFC..0x15E0E. */
REGION void tsl9_record_dispatch_block_15dfc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e0a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e0a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cd6a\n");
    __builtin_unreachable();
}

/* Original0x15E0E..0x15E20. */
REGION void tsl9_record_dispatch_block_15e0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e1c:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e1c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cd6a\n");
    __builtin_unreachable();
}

/* Original0x15E20..0x15E24. */
REGION void tsl9_record_dispatch_block_15e20(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15e20:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15e20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc82\n");
    __builtin_unreachable();
}

/* Original0x15E24..0x15E3A. */
REGION void tsl9_record_dispatch_block_15e24(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e36:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e36\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc78\n");
    __builtin_unreachable();
}

/* Original0x15E3A..0x15E4A. */
REGION void tsl9_record_dispatch_block_15e3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e46:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc78\n");
    __builtin_unreachable();
}

/* Original0x15E4A..0x15E5A. */
REGION void tsl9_record_dispatch_block_15e4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e56:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e56\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc78\n");
    __builtin_unreachable();
}

/* Original0x15E5A..0x15E5E. */
REGION void tsl9_record_dispatch_block_15e5a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15e5a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15e5a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd64\n");
    __builtin_unreachable();
}

/* Original0x15E5E..0x15E74. */
REGION void tsl9_record_dispatch_block_15e5e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e70:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e70\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd5a\n");
    __builtin_unreachable();
}

/* Original0x15E74..0x15E84. */
REGION void tsl9_record_dispatch_block_15e74(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e80:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd5a\n");
    __builtin_unreachable();
}

/* Original0x15E84..0x15E94. */
REGION void tsl9_record_dispatch_block_15e84(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15e90:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15e90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd5a\n");
    __builtin_unreachable();
}

/* Original0x15E94..0x15EA4. */
REGION void tsl9_record_dispatch_block_15e94(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ea0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ea0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd0a\n");
    __builtin_unreachable();
}

/* Original0x15EA4..0x15EB4. */
REGION void tsl9_record_dispatch_block_15ea4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15eb0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15eb0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd0a\n");
    __builtin_unreachable();
}

/* Original0x15EB4..0x15EC2. */
REGION void tsl9_record_dispatch_block_15eb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ebe:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ebe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ce88\n");
    __builtin_unreachable();
}

/* Original0x15EC2..0x15ED2. */
REGION void tsl9_record_dispatch_block_15ec2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ece:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ece\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15ED2..0x15EE2. */
REGION void tsl9_record_dispatch_block_15ed2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ede:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ede\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15EE2..0x15EF2. */
REGION void tsl9_record_dispatch_block_15ee2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15eee:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15eee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15EF2..0x15F02. */
REGION void tsl9_record_dispatch_block_15ef2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15efe:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15efe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F02..0x15F12. */
REGION void tsl9_record_dispatch_block_15f02(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f0e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f0e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F12..0x15F22. */
REGION void tsl9_record_dispatch_block_15f12(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f1e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f1e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F22..0x15F32. */
REGION void tsl9_record_dispatch_block_15f22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f2e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f2e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F32..0x15F42. */
REGION void tsl9_record_dispatch_block_15f32(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f3e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f3e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F42..0x15F52. */
REGION void tsl9_record_dispatch_block_15f42(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f4e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f4e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fe08\n");
    __builtin_unreachable();
}

/* Original0x15F52..0x15F62. */
REGION void tsl9_record_dispatch_block_15f52(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f5e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f5e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fdf6\n");
    __builtin_unreachable();
}

/* Original0x15F62..0x15F72. */
REGION void tsl9_record_dispatch_block_15f62(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f6e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fdf6\n");
    __builtin_unreachable();
}

/* Original0x15F72..0x15F82. */
REGION void tsl9_record_dispatch_block_15f72(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f7e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F82..0x15F92. */
REGION void tsl9_record_dispatch_block_15f82(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000e); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f8e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f8e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15F92..0x15FA2. */
REGION void tsl9_record_dispatch_block_15f92(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15f9e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15f9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x15FA2..0x15FA6. */
REGION void tsl9_record_dispatch_block_15fa2(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_15fa2:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_15fa2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bcf6\n");
    __builtin_unreachable();
}

/* Original0x15FA6..0x15FBC. */
REGION void tsl9_record_dispatch_block_15fa6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15fb8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15fb8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd0a\n");
    __builtin_unreachable();
}

/* Original0x15FBC..0x15FCC. */
REGION void tsl9_record_dispatch_block_15fbc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15fc8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15fc8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x15FCC..0x15FDC. */
REGION void tsl9_record_dispatch_block_15fcc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15fd8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15fd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x15FDC..0x15FEA. */
REGION void tsl9_record_dispatch_block_15fdc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15fe6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15fe6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd3a\n");
    __builtin_unreachable();
}

/* Original0x15FEA..0x15FFA. */
REGION void tsl9_record_dispatch_block_15fea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_15ff6:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_15ff6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x15FFA..0x1600A. */
REGION void tsl9_record_dispatch_block_15ffa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16006:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16006\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1600A..0x1601A. */
REGION void tsl9_record_dispatch_block_1600a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16016:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16016\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1601A..0x1602A. */
REGION void tsl9_record_dispatch_block_1601a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16026:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16026\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1602A..0x1603A. */
REGION void tsl9_record_dispatch_block_1602a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16036:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16036\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1603A..0x1605A. */
REGION void tsl9_record_dispatch_block_1603a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsltu a0, a5, a0\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16056:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16056\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1605A..0x1606A. */
REGION void tsl9_record_dispatch_block_1605a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16066:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16066\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1606A..0x1607A. */
REGION void tsl9_record_dispatch_block_1606a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16076:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16076\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1607A..0x1608A. */
REGION void tsl9_record_dispatch_block_1607a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16086:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16086\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1608A..0x1609A. */
REGION void tsl9_record_dispatch_block_1608a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16096:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16096\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0x1609A..0x1609E. */
REGION void tsl9_record_dispatch_block_1609a(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1609a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1609a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_f992\n");
    __builtin_unreachable();
}

/* Original0x1609E..0x160B4. */
REGION void tsl9_record_dispatch_block_1609e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_160b0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_160b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f97c\n");
    __builtin_unreachable();
}

/* Original0x160B4..0x160C4. */
REGION void tsl9_record_dispatch_block_160b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_160c0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_160c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f97c\n");
    __builtin_unreachable();
}

/* Original0x160C4..0x160D4. */
REGION void tsl9_record_dispatch_block_160c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_160d0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_160d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f97c\n");
    __builtin_unreachable();
}

/* Original0x160D4..0x160E4. */
REGION void tsl9_record_dispatch_block_160d4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_160e0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_160e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x160E4..0x160F4. */
REGION void tsl9_record_dispatch_block_160e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_160f0:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_160f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x160F4..0x16104. */
REGION void tsl9_record_dispatch_block_160f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000013); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16100:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16100\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x16104..0x16114. */
REGION void tsl9_record_dispatch_block_16104(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16110:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16110\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x16114..0x16118. */
REGION void tsl9_record_dispatch_block_16114(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_16114:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_16114\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_fa36\n");
    __builtin_unreachable();
}

/* Original0x16118..0x1612E. */
REGION void tsl9_record_dispatch_block_16118(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1612a:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1612a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fa30\n");
    __builtin_unreachable();
}

/* Original0x1612E..0x16132. */
REGION void tsl9_record_dispatch_block_1612e(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_1612e:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1612e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_fa2a\n");
    __builtin_unreachable();
}

/* Original0x16132..0x16148. */
REGION void tsl9_record_dispatch_block_16132(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16144:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16144\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fa24\n");
    __builtin_unreachable();
}

/* Original0x16148..0x1614C. */
REGION void tsl9_record_dispatch_block_16148(void)
{
    REGS;
    PORT(".Lrecord_dispatch_edge_16148:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_16148\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_b1b0\n");
    __builtin_unreachable();
}

/* Original0x1614C..0x16162. */
REGION void tsl9_record_dispatch_block_1614c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1615e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1615e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b176\n");
    __builtin_unreachable();
}

/* Original0x16162..0x16172. */
REGION void tsl9_record_dispatch_block_16162(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1616e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1616e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0x16172..0x16182. */
REGION void tsl9_record_dispatch_block_16172(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1617e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1617e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0x16182..0x16192. */
REGION void tsl9_record_dispatch_block_16182(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1618e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1618e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0x16192..0x161A2. */
REGION void tsl9_record_dispatch_block_16192(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1619e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1619e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0x161A2..0x161B0. */
REGION void tsl9_record_dispatch_block_161a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_161ac:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_161ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_c3ac\n");
    __builtin_unreachable();
}

/* Original0x161B0..0x161C0. */
REGION void tsl9_record_dispatch_block_161b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_161bc:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_161bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d668\n");
    __builtin_unreachable();
}

/* Original0x161C0..0x161CE. */
REGION void tsl9_record_dispatch_block_161c0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_161ca:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_161ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b220\n");
    __builtin_unreachable();
}

/* Original0x161CE..0x161E0. */
REGION void tsl9_record_dispatch_block_161ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x000001f4); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_161dc:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_161dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x161E0..0x161F6. */
REGION void tsl9_record_dispatch_block_161e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, -180\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_161f2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_161f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x161F6..0x16206. */
REGION void tsl9_record_dispatch_block_161f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16202:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16202\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_960e\n");
    __builtin_unreachable();
}

/* Original0x16206..0x16216. */
REGION void tsl9_record_dispatch_block_16206(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16212:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16212\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_9658\n");
    __builtin_unreachable();
}

/* Original0x16216..0x16226. */
REGION void tsl9_record_dispatch_block_16216(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16222:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16222\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_96a2\n");
    __builtin_unreachable();
}

/* Original0x16226..0x16236. */
REGION void tsl9_record_dispatch_block_16226(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16232:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16232\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_973c\n");
    __builtin_unreachable();
}

/* Original0x16236..0x16246. */
REGION void tsl9_record_dispatch_block_16236(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16242:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16242\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_954e\n");
    __builtin_unreachable();
}

/* Original0x16246..0x16256. */
REGION void tsl9_record_dispatch_block_16246(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16252:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16252\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_95bc\n");
    __builtin_unreachable();
}

/* Original0x16256..0x16266. */
REGION void tsl9_record_dispatch_block_16256(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16262:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16262\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0x16266..0x16276. */
REGION void tsl9_record_dispatch_block_16266(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16272:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16272\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b0b0\n");
    __builtin_unreachable();
}

/* Original0x16276..0x16286. */
REGION void tsl9_record_dispatch_block_16276(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16282:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16282\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b0b0\n");
    __builtin_unreachable();
}

/* Original0x16286..0x16296. */
REGION void tsl9_record_dispatch_block_16286(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16292:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16292\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b0b0\n");
    __builtin_unreachable();
}

/* Original0x16296..0x162AC. */
REGION void tsl9_record_dispatch_block_16296(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 56\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_162a8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_162a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18232\n");
    __builtin_unreachable();
}

/* Original0x162AC..0x162BE. */
REGION void tsl9_record_dispatch_block_162ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_162ba:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_162ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x162BE..0x162D2. */
REGION void tsl9_record_dispatch_block_162be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000fc); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_162ce:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_162ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x162D2..0x162E6. */
REGION void tsl9_record_dispatch_block_162d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000fd); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_162e2:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_162e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x162E6..0x162FE. */
REGION void tsl9_record_dispatch_block_162e6(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 28\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_162fa:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_162fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x162FE..0x16304. */
REGION void tsl9_record_dispatch_block_162fe(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_dispatch_edge_16300:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_16300\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x16304..0x16318. */
REGION void tsl9_record_dispatch_block_16304(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16314:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16314\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x16318..0x1631E. */
REGION void tsl9_record_dispatch_block_16318(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_dispatch_edge_1631a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1631a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0x1631E..0x16332. */
REGION void tsl9_record_dispatch_block_1631e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000c9); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_1632e:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_1632e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x16332..0x16338. */
REGION void tsl9_record_dispatch_block_16332(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_dispatch_edge_16334:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_16334\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0x16338..0x1634C. */
REGION void tsl9_record_dispatch_block_16338(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x000000ca); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16348:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16348\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_8e6a\n");
    __builtin_unreachable();
}

/* Original0x1634C..0x16368. */
REGION void tsl9_record_dispatch_block_1634c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000003); LIVE;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16364:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16364\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_15532\n");
    __builtin_unreachable();
}

/* Original0x16368..0x16378. */
REGION void tsl9_record_dispatch_block_16368(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16374:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16374\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_15532\n");
    __builtin_unreachable();
}

/* Original0x16378..0x16388. */
REGION void tsl9_record_dispatch_block_16378(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_16384:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_16384\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_15532\n");
    __builtin_unreachable();
}

/* Original0x16388..0x1638E. */
REGION void tsl9_record_dispatch_block_16388(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_dispatch_edge_1638a:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_1638a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_96a2\n");
    __builtin_unreachable();
}

/* Original0x1638E..0x163AC. */
REGION void tsl9_record_dispatch_block_1638e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000003e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_dispatch_literal_1639e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_99e8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_dispatch_literal_1639e\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_dispatch_edge_163a8:\n.option push\n.option norvc\njal zero,.Lrecord_dispatch_edge_163a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x16B50..0x16B76. */
REGION void tsl9_callback_dependencies_provider_16b50(void)
{
    REGS;
    a5 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000420); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x0000e000); LIVE;
    a5 = a5 + UINT32_C(0x000000ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi a5, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a1 = a1 + a5; LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffff8)); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_dispatch_edge_16b72:\n.option push\n.option norvc\njal ra,.Lrecord_dispatch_edge_16b72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_tagged_external_168de\n");
    __builtin_unreachable();
}

/* Original0x16B76..0x16B7C. */
REGION void tsl9_record_dispatch_block_16b76(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original relative jump words; valid only at the verified original layout. */
ENTRY __attribute__((used,aligned(4),section(".rodata.tsl9_record_dispatch_table_1a6f4"))) const uint32_t tsl9_record_dispatch_table_1a6f4[253] = {
    UINT32_C(0xffffaf5c),
    UINT32_C(0xffffaf72),
    UINT32_C(0xffffaf88),
    UINT32_C(0xffffafa0),
    UINT32_C(0xffffafb8),
    UINT32_C(0xffffafce),
    UINT32_C(0xffffafe4),
    UINT32_C(0xffffaffc),
    UINT32_C(0xffffb012),
    UINT32_C(0xffffb020),
    UINT32_C(0xffffb030),
    UINT32_C(0xffffb040),
    UINT32_C(0xffffb050),
    UINT32_C(0xffffb060),
    UINT32_C(0xffffb060),
    UINT32_C(0xffffb060),
    UINT32_C(0xffffb060),
    UINT32_C(0xffffb076),
    UINT32_C(0xffffb0a4),
    UINT32_C(0xffffb0b6),
    UINT32_C(0xffffb0e4),
    UINT32_C(0xffffb0fe),
    UINT32_C(0xffffb114),
    UINT32_C(0xffffb12a),
    UINT32_C(0xffffb138),
    UINT32_C(0xffffb152),
    UINT32_C(0xffffb160),
    UINT32_C(0xffffb170),
    UINT32_C(0xffffb180),
    UINT32_C(0xffffb190),
    UINT32_C(0xffffb1aa),
    UINT32_C(0xffffb1c4),
    UINT32_C(0xffffb1c4),
    UINT32_C(0xffffb1d4),
    UINT32_C(0xffffb1e4),
    UINT32_C(0xffffb1fe),
    UINT32_C(0xffffb20e),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb21e),
    UINT32_C(0xffffb22c),
    UINT32_C(0xffffb23a),
    UINT32_C(0xffffb248),
    UINT32_C(0xffffb262),
    UINT32_C(0xffffb27c),
    UINT32_C(0xffffb28c),
    UINT32_C(0xffffb29c),
    UINT32_C(0xffffb2ae),
    UINT32_C(0xffffb2c0),
    UINT32_C(0xffffb2d2),
    UINT32_C(0xffffb2e4),
    UINT32_C(0xffffb2f6),
    UINT32_C(0xffffb308),
    UINT32_C(0xffffb31a),
    UINT32_C(0xffffb32c),
    UINT32_C(0xffffb33e),
    UINT32_C(0xffffb350),
    UINT32_C(0xffffb36c),
    UINT32_C(0xffffb37e),
    UINT32_C(0xffffb390),
    UINT32_C(0xffffb3a8),
    UINT32_C(0xffffb3b8),
    UINT32_C(0xffffb3c8),
    UINT32_C(0xffffb40a),
    UINT32_C(0xffffb430),
    UINT32_C(0xffffb448),
    UINT32_C(0xffffb448),
    UINT32_C(0xffffb448),
    UINT32_C(0xffffb448),
    UINT32_C(0xffffb462),
    UINT32_C(0xffffb47c),
    UINT32_C(0xffffb48c),
    UINT32_C(0xffffb49c),
    UINT32_C(0xffffb4b6),
    UINT32_C(0xffffb4c6),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb4d6),
    UINT32_C(0xffffb4ea),
    UINT32_C(0xffffb4fe),
    UINT32_C(0xffffb50e),
    UINT32_C(0xffffb51e),
    UINT32_C(0xffffb532),
    UINT32_C(0xffffb546),
    UINT32_C(0xffffb556),
    UINT32_C(0xffffb556),
    UINT32_C(0xffffb556),
    UINT32_C(0xffffb556),
    UINT32_C(0xffffb556),
    UINT32_C(0xffffb570),
    UINT32_C(0xffffb58a),
    UINT32_C(0xffffb5a6),
    UINT32_C(0xffffb5c2),
    UINT32_C(0xffffb5de),
    UINT32_C(0xffffb5fa),
    UINT32_C(0xffffb616),
    UINT32_C(0xffffb632),
    UINT32_C(0xffffb644),
    UINT32_C(0xffffb656),
    UINT32_C(0xffffb664),
    UINT32_C(0xffffb674),
    UINT32_C(0xffffb684),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb694),
    UINT32_C(0xffffb6b2),
    UINT32_C(0xffffb6c2),
    UINT32_C(0xffffb6d2),
    UINT32_C(0xffffb6e4),
    UINT32_C(0xffffb6f6),
    UINT32_C(0xffffb708),
    UINT32_C(0xffffb71a),
    UINT32_C(0xffffb72c),
    UINT32_C(0xffffb746),
    UINT32_C(0xffffb756),
    UINT32_C(0xffffb766),
    UINT32_C(0xffffb780),
    UINT32_C(0xffffb790),
    UINT32_C(0xffffb7a0),
    UINT32_C(0xffffb7b0),
    UINT32_C(0xffffb7c0),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb7ce),
    UINT32_C(0xffffb7de),
    UINT32_C(0xffffb7ee),
    UINT32_C(0xffffb7fe),
    UINT32_C(0xffffb80e),
    UINT32_C(0xffffb81e),
    UINT32_C(0xffffb82e),
    UINT32_C(0xffffb83e),
    UINT32_C(0xffffb84e),
    UINT32_C(0xffffb85e),
    UINT32_C(0xffffb86e),
    UINT32_C(0xffffb87e),
    UINT32_C(0xffffb88e),
    UINT32_C(0xffffb89e),
    UINT32_C(0xffffb8ae),
    UINT32_C(0xffffb8c8),
    UINT32_C(0xffffb8d8),
    UINT32_C(0xffffb8e8),
    UINT32_C(0xffffb8f6),
    UINT32_C(0xffffb906),
    UINT32_C(0xffffb916),
    UINT32_C(0xffffb926),
    UINT32_C(0xffffb936),
    UINT32_C(0xffffb946),
    UINT32_C(0xffffb966),
    UINT32_C(0xffffb976),
    UINT32_C(0xffffb986),
    UINT32_C(0xffffb996),
    UINT32_C(0xffffb9a6),
    UINT32_C(0xffffb9c0),
    UINT32_C(0xffffb9d0),
    UINT32_C(0xffffb9e0),
    UINT32_C(0xffffb9f0),
    UINT32_C(0xffffba00),
    UINT32_C(0xffffba10),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffba20),
    UINT32_C(0xffffba3a),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffba54),
    UINT32_C(0xffffba6e),
    UINT32_C(0xffffba7e),
    UINT32_C(0xffffba8e),
    UINT32_C(0xffffba9e),
    UINT32_C(0xffffbaae),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffbabc),
    UINT32_C(0xffffbacc),
    UINT32_C(0xffffbada),
    UINT32_C(0xffffbaec),
    UINT32_C(0xffffbaec),
    UINT32_C(0xffffbaec),
    UINT32_C(0xffffbaec),
    UINT32_C(0xffffbaec),
    UINT32_C(0xffffbb02),
    UINT32_C(0xffffbb12),
    UINT32_C(0xffffbb22),
    UINT32_C(0xffffbb32),
    UINT32_C(0xffffbb42),
    UINT32_C(0xffffbb52),
    UINT32_C(0xffffbb62),
    UINT32_C(0xffffbb72),
    UINT32_C(0xffffbb82),
    UINT32_C(0xffffbb92),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffbba2),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffbbb8),
    UINT32_C(0xffffbbca),
    UINT32_C(0xffffbbde),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffbbf2),
    UINT32_C(0xffffb098),
    UINT32_C(0xffffbc0a),
    UINT32_C(0xffffbc24),
    UINT32_C(0xffffbc3e),
    UINT32_C(0xffffbc58),
    UINT32_C(0xffffbc74),
    UINT32_C(0xffffbc84),
    UINT32_C(0xffffbc94),
};
