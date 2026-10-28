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

/* Four complete conditional SDK GATT registration/UUID bodies:536B/219i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x445E6..0x445E8. */
REGION void tsl9_candidate_external_flash_445e6(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_445e6:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_registration_edge_445e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_44620\n");
    __builtin_unreachable();
}

/* Original0x445E8..0x445F6. */
REGION void tsl9_resident_gatt_registration_block_445e8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_registration_edge_445f4:\n.option push\n.option rvc\nc.beqz a1,.Lresident_gatt_registration_edge_445f4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_44616\n");
    __builtin_unreachable();
}

/* Original0x445F6..0x4460C. */
REGION void tsl9_resident_gatt_registration_block_445f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    a1 = UINT32_C(0x0006e000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = a1 + UINT32_C(0x00000370); LIVE;
    PORT(".Lresident_gatt_registration_literal_44604:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_44604\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4460C..0x44616. */
REGION void tsl9_resident_gatt_registration_block_4460c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 12(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa45c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x309c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb45c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44616..0x44620. */
REGION void tsl9_resident_gatt_registration_block_44616(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44620..0x44624. */
REGION void tsl9_resident_gatt_registration_block_44620(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44624..0x44636. */
REGION void tsl9_candidate_external_flash_44624(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_44632:\n.option push\n.option norvc\nbeq a1,a4,.Lresident_gatt_registration_edge_44632\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_44674\n");
    __builtin_unreachable();
}

/* Original0x44636..0x4463E. */
REGION void tsl9_resident_gatt_registration_block_44636(void)
{
    REGS;
    a2 = UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_registration_edge_4463a:\n.option push\n.option norvc\nbne a1,a2,.Lresident_gatt_registration_edge_4463a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_44650\n");
    __builtin_unreachable();
}

/* Original0x4463E..0x44642. */
REGION void tsl9_resident_gatt_registration_block_4463e(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_4463e:\n.option push\n.option norvc\nbeq a3,a4,.Lresident_gatt_registration_edge_4463e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_4465c\n");
    __builtin_unreachable();
}

/* Original0x44642..0x44646. */
REGION void tsl9_resident_gatt_registration_block_44642(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_44642:\n.option push\n.option norvc\nbne a3,a1,.Lresident_gatt_registration_edge_44642\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_44650\n");
    __builtin_unreachable();
}

/* Original0x44646..0x44648. */
REGION void tsl9_resident_gatt_registration_block_44646(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_44646:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_44646\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_44678\n");
    __builtin_unreachable();
}

/* Original0x44648..0x44650. */
REGION void tsl9_resident_gatt_registration_block_44648(void)
{
    REGS;
    a4 = UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_registration_edge_4464c:\n.option push\n.option norvc\nbeq a3,a4,.Lresident_gatt_registration_edge_4464c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_44668\n");
    __builtin_unreachable();
}

/* Original0x44650..0x4465C. */
REGION void tsl9_resident_gatt_registration_block_44650(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4465C..0x44662. */
REGION void tsl9_resident_gatt_registration_block_4465c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_44660:\n.option push\n.option rvc\nc.jal .Lresident_gatt_registration_edge_44660\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_flash_445e6\n");
    __builtin_unreachable();
}

/* Original0x44662..0x44668. */
REGION void tsl9_resident_gatt_registration_block_44662(void)
{
    REGS;
    a2 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_44666:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_44666\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4467c\n");
    __builtin_unreachable();
}

/* Original0x44668..0x4466C. */
REGION void tsl9_resident_gatt_registration_block_44668(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4466a:\n.option push\n.option rvc\nc.jal .Lresident_gatt_registration_edge_4466a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_flash_445e6\n");
    __builtin_unreachable();
}

/* Original0x4466C..0x44674. */
REGION void tsl9_resident_gatt_registration_block_4466c(void)
{
    REGS;
    a2 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_44672:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_44672\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4467e\n");
    __builtin_unreachable();
}

/* Original0x44674..0x44678. */
REGION void tsl9_resident_gatt_registration_block_44674(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_44674:\n.option push\n.option norvc\nbne a3,a1,.Lresident_gatt_registration_edge_44674\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_44648\n");
    __builtin_unreachable();
}

/* Original0x44678..0x4467C. */
REGION void tsl9_resident_gatt_registration_block_44678(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4467C..0x4467E. */
REGION void tsl9_resident_gatt_registration_block_4467c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4467E..0x44686. */
REGION void tsl9_resident_gatt_registration_block_4467e(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_literal_4467e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20000442\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_4467e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x44686..0x4468A. */
REGION void tsl9_resident_gatt_registration_block_44686(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_44688:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_44688\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_44650\n");
    __builtin_unreachable();
}

/* Original0x4CE22..0x4CE26. */
REGION void tsl9_candidate_external_flash_4ce22(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211e\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4ce24:\n.option push\n.option rvc\nc.bnez a5,.Lresident_gatt_registration_edge_4ce24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4ce2c\n");
    __builtin_unreachable();
}

/* Original0x4CE26..0x4CE2C. */
REGION void tsl9_resident_gatt_registration_block_4ce26(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CE2C..0x4CE4C. */
REGION void tsl9_resident_gatt_registration_block_4ce2c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2094\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 4(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0x0006f000); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = a0 + UINT32_C(0xfffffa90); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ce48:\n.option push\n.option norvc\njal ra,.Lresident_gatt_registration_edge_4ce48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_44624\n");
    __builtin_unreachable();
}

/* Original0x4CE4C..0x4CE4E. */
REGION void tsl9_resident_gatt_registration_block_4ce4c(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_4ce4c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_registration_edge_4ce4c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4ce60\n");
    __builtin_unreachable();
}

/* Original0x4CE4E..0x4CE5C. */
REGION void tsl9_resident_gatt_registration_block_4ce4e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203c\n.option pop\n");
    a4 = UINT32_C(0x00000009); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ce58:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_gatt_registration_edge_4ce58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_4ce84\n");
    __builtin_unreachable();
}

/* Original0x4CE5C..0x4CE60. */
REGION void tsl9_resident_gatt_registration_block_4ce5c(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ce5e:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4ce5e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CE60..0x4CE72. */
REGION void tsl9_resident_gatt_registration_block_4ce60(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2094\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a2, 4(s1)\n.option pop\n");
    a0 = UINT32_C(0x0006f000); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = a0 + UINT32_C(0xfffffa9c); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ce6e:\n.option push\n.option norvc\njal ra,.Lresident_gatt_registration_edge_4ce6e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_44624\n");
    __builtin_unreachable();
}

/* Original0x4CE72..0x4CE74. */
REGION void tsl9_resident_gatt_registration_block_4ce72(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_4ce72:\n.option push\n.option rvc\nc.bnez a0,.Lresident_gatt_registration_edge_4ce72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4ce4e\n");
    __builtin_unreachable();
}

/* Original0x4CE74..0x4CE76. */
REGION void tsl9_resident_gatt_registration_block_4ce74(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x4CE76..0x4CE84. */
REGION void tsl9_resident_gatt_registration_block_4ce76(void)
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

/* Original0x4CE84..0x4CE94. */
REGION void tsl9_resident_gatt_registration_block_4ce84(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a3, -276(s2)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s2, -276\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4ce92:\n.option push\n.option rvc\nc.beqz a3,.Lresident_gatt_registration_edge_4ce92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CE94..0x4CE9E. */
REGION void tsl9_resident_gatt_registration_block_4ce94(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201a\n.option pop\n");
    a4 = a4 + a3; LIVE;
    a3 = UINT32_C(0x00010000); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ce9a:\n.option push\n.option norvc\nblt a3,a4,.Lresident_gatt_registration_edge_4ce9a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CE9E..0x4CEAE. */
REGION void tsl9_resident_gatt_registration_block_4ce9e(void)
{
    REGS;
    a1 = UINT32_C(0x00004000); LIVE;
    a1 = a1 + UINT32_C(0x00000702); LIVE;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lresident_gatt_registration_literal_4cea6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_4cea6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CEAE..0x4CEB4. */
REGION void tsl9_resident_gatt_registration_block_4ceae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ceb2:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_registration_edge_4ceb2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CEB4..0x4CEC0. */
REGION void tsl9_resident_gatt_registration_block_4ceb4(void)
{
    REGS;
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_registration_literal_4ceb8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_4ceb8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CEC0..0x4CECA. */
REGION void tsl9_resident_gatt_registration_block_4cec0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a1, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x4CECA..0x4CED6. */
REGION void tsl9_resident_gatt_registration_block_4ceca(void)
{
    REGS;
    a3 = a1 + a4; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_gatt_registration_edge_4ced2:\n.option push\n.option norvc\nbltu a4,a5,.Lresident_gatt_registration_edge_4ced2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_4cf08\n");
    __builtin_unreachable();
}

/* Original0x4CED6..0x4CEDE. */
REGION void tsl9_resident_gatt_registration_block_4ced6(void)
{
    REGS;
    a5 = a5 + a1; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cedc:\n.option push\n.option rvc\nc.beqz a2,.Lresident_gatt_registration_edge_4cedc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cee2\n");
    __builtin_unreachable();
}

/* Original0x4CEDE..0x4CEE2. */
REGION void tsl9_resident_gatt_registration_block_4cede(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a5, 0(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CEE2..0x4CEF6. */
REGION void tsl9_resident_gatt_registration_block_4cee2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 0(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 4\n.option pop\n");
    PORT(".Lresident_gatt_registration_literal_4ceee:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_4ceee\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CEF6..0x4CF02. */
REGION void tsl9_resident_gatt_registration_block_4cef6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xffffff88); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf00:\n.option push\n.option rvc\nc.bnez a4,.Lresident_gatt_registration_edge_4cf00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf1a\n");
    __builtin_unreachable();
}

/* Original0x4CF02..0x4CF08. */
REGION void tsl9_resident_gatt_registration_block_4cf02(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw s1, 0(a5)\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf06:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf06\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CF08..0x4CF18. */
REGION void tsl9_resident_gatt_registration_block_4cf08(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a2, 4(s0)\n.option pop\n");
    a0 = a4 << UINT32_C(0x00000004); LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    a2 = a2 + a0; LIVE;
    /* Conditional Xwchc: qk.c.sh a3, 10(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xa636\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf16:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf16\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4ceca\n");
    __builtin_unreachable();
}

/* Original0x4CF18..0x4CF1A. */
REGION void tsl9_resident_gatt_registration_block_4cf18(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CF1A..0x4CF1E. */
REGION void tsl9_resident_gatt_registration_block_4cf1a(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf1c:\n.option push\n.option rvc\nc.bnez a5,.Lresident_gatt_registration_edge_4cf1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf18\n");
    __builtin_unreachable();
}

/* Original0x4CF1E..0x4CF22. */
REGION void tsl9_resident_gatt_registration_block_4cf1e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw s1, 0(a4)\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf20:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf20\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4ce76\n");
    __builtin_unreachable();
}

/* Original0x4CF22..0x4CF2E. */
REGION void tsl9_candidate_external_flash_4cf22(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf2c:\n.option push\n.option rvc\nc.bnez a0,.Lresident_gatt_registration_edge_4cf2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf3e\n");
    __builtin_unreachable();
}

/* Original0x4CF2E..0x4CF30. */
REGION void tsl9_resident_gatt_registration_block_4cf2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CF30..0x4CF3E. */
REGION void tsl9_resident_gatt_registration_block_4cf30(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CF3E..0x4CF4E. */
REGION void tsl9_resident_gatt_registration_block_4cf3e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a3\n.option pop\n");
    /* Conditional Xwchc: qk.c.shsp a1, 8(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x846c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sbsp a2, 10(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x8550\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf4a:\n.option push\n.option norvc\njal ra,.Lresident_gatt_registration_edge_4cf4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4ce22\n");
    __builtin_unreachable();
}

/* Original0x4CF4E..0x4CF52. */
REGION void tsl9_resident_gatt_registration_block_4cf4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf50:\n.option push\n.option rvc\nc.bnez a0,.Lresident_gatt_registration_edge_4cf50\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf30\n");
    __builtin_unreachable();
}

/* Original0x4CF52..0x4CF56. */
REGION void tsl9_resident_gatt_registration_block_4cf52(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_4cf52:\n.option push\n.option norvc\nbeqz s2,.Lresident_gatt_registration_edge_4cf52\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_gatt_registration_block_4cf30\n");
    __builtin_unreachable();
}

/* Original0x4CF56..0x4CF5A. */
REGION void tsl9_resident_gatt_registration_block_4cf56(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243e\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf58:\n.option push\n.option rvc\nc.beqz a5,.Lresident_gatt_registration_edge_4cf58\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf2e\n");
    __builtin_unreachable();
}

/* Original0x4CF5A..0x4CF6A. */
REGION void tsl9_resident_gatt_registration_block_4cf5a(void)
{
    REGS;
    a1 = UINT32_C(0x00004000); LIVE;
    a1 = a1 + UINT32_C(0x00000705); LIVE;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lresident_gatt_registration_literal_4cf62:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_gatt_registration_literal_4cf62\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CF6A..0x4CF6C. */
REGION void tsl9_resident_gatt_registration_block_4cf6a(void)
{
    REGS;
    PORT(".Lresident_gatt_registration_edge_4cf6a:\n.option push\n.option rvc\nc.beqz a0,.Lresident_gatt_registration_edge_4cf6a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf92\n");
    __builtin_unreachable();
}

/* Original0x4CF6C..0x4CF84. */
REGION void tsl9_resident_gatt_registration_block_4cf6c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x243e\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsw s2, 8(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa15e\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xffffff94); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf82:\n.option push\n.option rvc\nc.bnez a4,.Lresident_gatt_registration_edge_4cf82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf8a\n");
    __builtin_unreachable();
}

/* Original0x4CF84..0x4CF88. */
REGION void tsl9_resident_gatt_registration_block_4cf84(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf86:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4cf30\n");
    __builtin_unreachable();
}

/* Original0x4CF88..0x4CF8A. */
REGION void tsl9_resident_gatt_registration_block_4cf88(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4CF8A..0x4CF8E. */
REGION void tsl9_resident_gatt_registration_block_4cf8a(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf8c:\n.option push\n.option rvc\nc.bnez a5,.Lresident_gatt_registration_edge_4cf8c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_gatt_registration_block_4cf88\n");
    __builtin_unreachable();
}

/* Original0x4CF8E..0x4CF92. */
REGION void tsl9_resident_gatt_registration_block_4cf8e(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_gatt_registration_edge_4cf90:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4cf30\n");
    __builtin_unreachable();
}

/* Original0x4CF92..0x4CF96. */
REGION void tsl9_resident_gatt_registration_block_4cf92(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 19\n.option pop\n");
    PORT(".Lresident_gatt_registration_edge_4cf94:\n.option push\n.option rvc\nc.j .Lresident_gatt_registration_edge_4cf94\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_gatt_registration_block_4cf30\n");
    __builtin_unreachable();
}
