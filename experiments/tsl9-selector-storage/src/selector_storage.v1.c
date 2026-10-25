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

/* One selector state machine and four lookup objects functions:252B/81i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xEBAC..0xEBBE. */
REGION void tsl9_feature_state_records_provider_ebac(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Lselector_storage_edge_ebba:\n.option push\n.option norvc\nbeq a5,a4,.Lselector_storage_edge_ebba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec50\n");
    __builtin_unreachable();
}

/* Original0xEBBE..0xEBC0. */
REGION void tsl9_selector_storage_block_ebbe(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ebbe:\n.option push\n.option rvc\nc.beqz a5,.Lselector_storage_edge_ebbe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_storage_block_ebce\n");
    __builtin_unreachable();
}

/* Original0xEBC0..0xEBC6. */
REGION void tsl9_selector_storage_block_ebc0(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_storage_edge_ebc2:\n.option push\n.option norvc\nbeq a5,a4,.Lselector_storage_edge_ebc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec90\n");
    __builtin_unreachable();
}

/* Original0xEBC6..0xEBCE. */
REGION void tsl9_selector_storage_block_ebc6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEBCE..0xEBD6. */
REGION void tsl9_selector_storage_block_ebce(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000001)); LIVE;
    PORT(".Lselector_storage_edge_ebd2:\n.option push\n.option norvc\nbeq a0,a1,.Lselector_storage_edge_ebd2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec22\n");
    __builtin_unreachable();
}

/* Original0xEBD6..0xEBE4. */
REGION void tsl9_selector_storage_block_ebd6(void)
{
    REGS;
    a4 = a0 + UINT32_C(0xffffffc6); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_storage_edge_ebe0:\n.option push\n.option norvc\nbleu a4,a3,.Lselector_storage_edge_ebe0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ebf6\n");
    __builtin_unreachable();
}

/* Original0xEBE4..0xEBEC. */
REGION void tsl9_selector_storage_block_ebe4(void)
{
    REGS;
    a4 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_storage_edge_ebe8:\n.option push\n.option norvc\nbeq a5,a4,.Lselector_storage_edge_ebe8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec1a\n");
    __builtin_unreachable();
}

/* Original0xEBEC..0xEBEE. */
REGION void tsl9_selector_storage_block_ebec(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ebec:\n.option push\n.option rvc\nc.beqz a5,.Lselector_storage_edge_ebec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_storage_block_ebf6\n");
    __builtin_unreachable();
}

/* Original0xEBEE..0xEBF6. */
REGION void tsl9_selector_storage_block_ebee(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lselector_storage_edge_ebf2:\n.option push\n.option norvc\nbne a4,a0,.Lselector_storage_edge_ebf2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec1a\n");
    __builtin_unreachable();
}

/* Original0xEBF6..0xEC12. */
REGION void tsl9_selector_storage_block_ebf6(void)
{
    REGS;
    a1 = a5 + UINT32_C(0x00000001); LIVE;
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 2(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a1, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 0(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_storage_edge_ec0e:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec0e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xEC12..0xEC16. */
REGION void tsl9_selector_storage_block_ec12(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ec12:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xEC16..0xEC1A. */
REGION void tsl9_selector_storage_block_ec16(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 4(s0)\n.option pop\n");
    PORT(".Lselector_storage_edge_ec18:\n.option push\n.option rvc\nc.j .Lselector_storage_edge_ec18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC1A..0xEC22. */
REGION void tsl9_selector_storage_block_ec1a(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1(s0)\n.option pop\n");
    PORT(".Lselector_storage_edge_ec20:\n.option push\n.option rvc\nc.j .Lselector_storage_edge_ec20\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_storage_block_ec12\n");
    __builtin_unreachable();
}

/* Original0xEC22..0xEC24. */
REGION void tsl9_selector_storage_block_ec22(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ec22:\n.option push\n.option rvc\nc.beqz a5,.Lselector_storage_edge_ec22\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC24..0xEC28. */
REGION void tsl9_selector_storage_block_ec24(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ec24:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec24\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xEC28..0xEC34. */
REGION void tsl9_selector_storage_block_ec28(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    a0 = a0 - a5; LIVE;
    a5 = UINT32_C(0x000001f3); LIVE;
    PORT(".Lselector_storage_edge_ec30:\n.option push\n.option norvc\nbleu a0,a5,.Lselector_storage_edge_ec30\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC34..0xEC40. */
REGION void tsl9_selector_storage_block_ec34(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1(s0)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_storage_edge_ec3c:\n.option push\n.option norvc\nbeq a1,a5,.Lselector_storage_edge_ec3c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec4a\n");
    __builtin_unreachable();
}

/* Original0xEC40..0xEC4A. */
REGION void tsl9_selector_storage_block_ec40(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 2(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_storage_edge_ec46:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xEC4A..0xEC50. */
REGION void tsl9_selector_storage_block_ec4a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    PORT(".Lselector_storage_edge_ec4e:\n.option push\n.option rvc\nc.j .Lselector_storage_edge_ec4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC50..0xEC58. */
REGION void tsl9_selector_storage_block_ec50(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lselector_storage_edge_ec54:\n.option push\n.option norvc\nbne a5,a0,.Lselector_storage_edge_ec54\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ec82\n");
    __builtin_unreachable();
}

/* Original0xEC58..0xEC5C. */
REGION void tsl9_selector_storage_block_ec58(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ec58:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec58\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xEC5C..0xEC68. */
REGION void tsl9_selector_storage_block_ec5c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    a0 = a0 - a5; LIVE;
    a5 = UINT32_C(0x000001f3); LIVE;
    PORT(".Lselector_storage_edge_ec64:\n.option push\n.option norvc\nbleu a0,a5,.Lselector_storage_edge_ec64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC68..0xEC78. */
REGION void tsl9_selector_storage_block_ec68(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 2(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 0(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0xEC78..0xEC82. */
REGION void tsl9_selector_storage_block_ec78(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_storage_edge_ec7e:\n.option push\n.option norvc\njal zero,.Lselector_storage_edge_ec7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xEC82..0xEC90. */
REGION void tsl9_selector_storage_block_ec82(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 1(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lselector_storage_edge_ec8e:\n.option push\n.option rvc\nc.j .Lselector_storage_edge_ec8e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_storage_block_ec78\n");
    __builtin_unreachable();
}

/* Original0xEC90..0xEC94. */
REGION void tsl9_selector_storage_block_ec90(void)
{
    REGS;
    PORT(".Lselector_storage_edge_ec90:\n.option push\n.option norvc\nbne a0,a1,.Lselector_storage_edge_ec90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

/* Original0xEC94..0xECA2. */
REGION void tsl9_selector_storage_block_ec94(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 2(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    PORT(".Lselector_storage_edge_ec9e:\n.option push\n.option norvc\njal ra,.Lselector_storage_edge_ec9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xECA2..0xECA8. */
REGION void tsl9_selector_storage_block_eca2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 0(s0)\n.option pop\n");
    PORT(".Lselector_storage_edge_eca6:\n.option push\n.option rvc\nc.j .Lselector_storage_edge_eca6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_storage_block_ebc6\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
TABLE_DATA(".rodata.tsl9_feature_state_records_static_data_1a4e4") const uint8_t tsl9_feature_state_records_static_data_1a4e4[16] = {0xd2, 0x6b, 0xbd, 0x04, 0x0c, 0xb5, 0x63, 0xda, 0x73, 0xca, 0x1c, 0xa5, 0xad, 0x14, 0xc2, 0x7b};
TABLE_DATA(".rodata.tsl9_feature_state_records_static_data_1a518") const uint8_t tsl9_feature_state_records_static_data_1a518[15] = {0x22, 0x7f, 0x98, 0xc5, 0x4b, 0x16, 0xf1, 0xac, 0xf0, 0xad, 0x4a, 0x17, 0x99, 0xc4, 0x23};
TABLE_DATA(".rodata.tsl9_feature_state_records_static_data_1a528") const uint8_t tsl9_feature_state_records_static_data_1a528[15] = {0x95, 0xc8, 0x2f, 0x72, 0xfc, 0xa1, 0x46, 0x1b, 0x47, 0x1a, 0xfd, 0xa0, 0x2e, 0x73, 0x94};
TABLE_DATA(".rodata.tsl9_feature_state_records_static_data_1a538") const uint8_t tsl9_feature_state_records_static_data_1a538[15] = {0xfc, 0xa1, 0x46, 0x1b, 0x95, 0xc8, 0x2f, 0x72, 0x2e, 0x73, 0x94, 0xc9, 0x47, 0x1a, 0xfd};
