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

/* Three public-SDK BLE entry/task/memset bodies:546B/193i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43B3E..0x43B76. */
REGION void tsl9_candidate_task_initialize_43b3e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e8)) = (uint32_t)0; LIVE;
    a0 = UINT32_C(0x20003000); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000230)) = (uint32_t)0; LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0x000001c8); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".Lresident_ble_initialization_literal_43b6e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43b6e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43B76..0x43B88. */
REGION void tsl9_resident_ble_initialization_block_43b76(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 412\n.option pop\n");
    a2 = UINT32_C(0x00000028); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_ble_initialization_literal_43b80:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43b80\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43B88..0x43B8C. */
REGION void tsl9_resident_ble_initialization_block_43b88(void)
{
    REGS;
    PORT(".Lresident_ble_initialization_edge_43b88:\n.option push\n.option norvc\njal ra,.Lresident_ble_initialization_edge_43b88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_heap_initialize_43104\n");
    __builtin_unreachable();
}

/* Original0x43B8C..0x43BC6. */
REGION void tsl9_resident_ble_initialization_block_43b8c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000201)); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 412\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a0 = a0 + a5; LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    a0 = a0 * a5; LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000000e); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa028\n.option pop\n");
    a0 = a0 * a5; LIVE;
    a0 = a0 + UINT32_C(0x00000240); LIVE;
    PORT(".Lresident_ble_initialization_literal_43bbe:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43bbe\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43BC6..0x43BCC. */
REGION void tsl9_resident_ble_initialization_block_43bc6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 556(s1)\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43bca:\n.option push\n.option rvc\nc.beqz a0,.Lresident_ble_initialization_edge_43bca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43c44\n");
    __builtin_unreachable();
}

/* Original0x43BCC..0x43BE2. */
REGION void tsl9_resident_ble_initialization_block_43bcc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2030\n.option pop\n");
    a5 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = a2 * a5; LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    PORT(".Lresident_ble_initialization_literal_43bda:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43bda\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43BE2..0x43C04. */
REGION void tsl9_resident_ble_initialization_block_43be2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 556(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2038\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000240); LIVE;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 452(s1)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000001e4)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_ble_initialization_edge_43c00:\n.option push\n.option norvc\njal ra,.Lresident_ble_initialization_edge_43c00\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_initialize_4329a\n");
    __builtin_unreachable();
}

/* Original0x43C04..0x43C06. */
REGION void tsl9_resident_ble_initialization_block_43c04(void)
{
    REGS;
    PORT(".Lresident_ble_initialization_edge_43c04:\n.option push\n.option rvc\nc.jal .Lresident_ble_initialization_edge_43c04\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_system_task_initialize_44022\n");
    __builtin_unreachable();
}

/* Original0x43C06..0x43C44. */
REGION void tsl9_resident_ble_initialization_block_43c06(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x301c\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 452(s1)\n.option pop\n");
    a2 = UINT32_C(0x00043000); LIVE;
    a4 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a4 + a3; LIVE;
    a2 = a2 + UINT32_C(0x000002a4); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    a4 = a5 + UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a2 = UINT32_C(0x00043000); LIVE;
    a4 = a4 + a3; LIVE;
    a2 = a2 + UINT32_C(0x00000326); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    a4 = a5 + UINT32_C(0x00000003); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb018\n.option pop\n");
    a5 = a5 + a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x43C44..0x43C4E. */
REGION void tsl9_resident_ble_initialization_block_43c44(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43C7E..0x43C82. */
REGION void tsl9_candidate_BLE_LibInit_43c7e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_ble_initialization_edge_43c80:\n.option push\n.option rvc\nc.beqz a5,.Lresident_ble_initialization_edge_43c80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d5c\n");
    __builtin_unreachable();
}

/* Original0x43C82..0x43C90. */
REGION void tsl9_resident_ble_initialization_block_43c82(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 & a5; LIVE;
    a3 = UINT32_C(0x20000000); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_ble_initialization_edge_43c8c:\n.option push\n.option norvc\nbne a4,a3,.Lresident_ble_initialization_edge_43c8c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_ble_initialization_block_43d5e\n");
    __builtin_unreachable();
}

/* Original0x43C90..0x43C94. */
REGION void tsl9_resident_ble_initialization_block_43c90(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 4(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x215a\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43c92:\n.option push\n.option rvc\nc.beqz a4,.Lresident_ble_initialization_edge_43c92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d5e\n");
    __builtin_unreachable();
}

/* Original0x43C94..0x43CAE. */
REGION void tsl9_resident_ble_initialization_block_43c94(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a1 = UINT32_C(0x000000ff); LIVE;
    a0 = a0 + UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lresident_ble_initialization_literal_43ca6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_isbufset_200004bc\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43ca6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43CAE..0x43CB6. */
REGION void tsl9_resident_ble_initialization_block_43cae(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_ble_initialization_edge_43cb2:\n.option push\n.option norvc\nbeq a0,a4,.Lresident_ble_initialization_edge_43cb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_ble_initialization_block_43d50\n");
    __builtin_unreachable();
}

/* Original0x43CB6..0x43CBA. */
REGION void tsl9_resident_ble_initialization_block_43cb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s1)\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43cb8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_ble_initialization_edge_43cb8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43cc4\n");
    __builtin_unreachable();
}

/* Original0x43CBA..0x43CC0. */
REGION void tsl9_resident_ble_initialization_block_43cba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 56(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_ble_initialization_edge_43cbe:\n.option push\n.option rvc\nc.beqz a4,.Lresident_ble_initialization_edge_43cbe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d50\n");
    __builtin_unreachable();
}

/* Original0x43CC0..0x43CC4. */
REGION void tsl9_resident_ble_initialization_block_43cc0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 60(s1)\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43cc2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_ble_initialization_edge_43cc2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d50\n");
    __builtin_unreachable();
}

/* Original0x43CC4..0x43CDA. */
REGION void tsl9_resident_ble_initialization_block_43cc4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    a2 = UINT32_C(0x00000040); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 492\n.option pop\n");
    PORT(".Lresident_ble_initialization_literal_43cd2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43cd2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43CDA..0x43CEC. */
REGION void tsl9_resident_ble_initialization_block_43cda(void)
{
    REGS;
    a2 = UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 492\n.option pop\n");
    PORT(".Lresident_ble_initialization_literal_43ce4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_ble_initialization_literal_43ce4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43CEC..0x43CF4. */
REGION void tsl9_resident_ble_initialization_block_43cec(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, 492\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27da\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43cf2:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43cf2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43cfa\n");
    __builtin_unreachable();
}

/* Original0x43CF4..0x43CFA. */
REGION void tsl9_resident_ble_initialization_block_43cf4(void)
{
    REGS;
    a4 = UINT32_C(0x00000100); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7da\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43CFA..0x43CFE. */
REGION void tsl9_resident_ble_initialization_block_43cfa(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 14(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27f8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43cfc:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43cfc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d02\n");
    __builtin_unreachable();
}

/* Original0x43CFE..0x43D02. */
REGION void tsl9_resident_ble_initialization_block_43cfe(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 14(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7f8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D02..0x43D06. */
REGION void tsl9_resident_ble_initialization_block_43d02(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2b9a\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d04:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d04\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d0a\n");
    __builtin_unreachable();
}

/* Original0x43D06..0x43D0A. */
REGION void tsl9_resident_ble_initialization_block_43d06(void)
{
    REGS;
    a4 = UINT32_C(0x0000001b); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xab9a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D0A..0x43D0E. */
REGION void tsl9_resident_ble_initialization_block_43d0a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 15(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x37f8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d0c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d0c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d12\n");
    __builtin_unreachable();
}

/* Original0x43D0E..0x43D12. */
REGION void tsl9_resident_ble_initialization_block_43d0e(void)
{
    REGS;
    a4 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 15(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7f8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D12..0x43D16. */
REGION void tsl9_resident_ble_initialization_block_43d12(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 18(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bb8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d14:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d14\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d1a\n");
    __builtin_unreachable();
}

/* Original0x43D16..0x43D1A. */
REGION void tsl9_resident_ble_initialization_block_43d16(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 18(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xabb8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D1A..0x43D1E. */
REGION void tsl9_resident_ble_initialization_block_43d1a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 19(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3bb8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d1c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d22\n");
    __builtin_unreachable();
}

/* Original0x43D1E..0x43D22. */
REGION void tsl9_resident_ble_initialization_block_43d1e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 15(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x37f8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 19(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xbbb8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D22..0x43D26. */
REGION void tsl9_resident_ble_initialization_block_43d22(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 20(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bd8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d24:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d24\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d2a\n");
    __builtin_unreachable();
}

/* Original0x43D26..0x43D2A. */
REGION void tsl9_resident_ble_initialization_block_43d26(void)
{
    REGS;
    a4 = UINT32_C(0x00000009); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 20(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xabd8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D2A..0x43D2E. */
REGION void tsl9_resident_ble_initialization_block_43d2a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 22(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28f8\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_43d2c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_ble_initialization_edge_43d2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d34\n");
    __builtin_unreachable();
}

/* Original0x43D2E..0x43D34. */
REGION void tsl9_resident_ble_initialization_block_43d2e(void)
{
    REGS;
    a4 = UINT32_C(0x0000003c); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 22(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xabf8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D34..0x43D38. */
REGION void tsl9_resident_ble_initialization_block_43d34(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    PORT(".Lresident_ble_initialization_edge_43d36:\n.option push\n.option rvc\nc.beqz a5,.Lresident_ble_initialization_edge_43d36\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_43d42\n");
    __builtin_unreachable();
}

/* Original0x43D38..0x43D3A. */
REGION void tsl9_resident_ble_initialization_block_43d38(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D3A..0x43D42. */
REGION void tsl9_resident_ble_initialization_block_43d3a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000001a4)) = (uint16_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x43D42..0x43D4E. */
REGION void tsl9_resident_ble_initialization_block_43d42(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000005f5)) = (uint8_t)a4; LIVE;
    PORT(".Lresident_ble_initialization_edge_43d4c:\n.option push\n.option rvc\nc.jal .Lresident_ble_initialization_edge_43d4c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_task_initialize_43b3e\n");
    __builtin_unreachable();
}

/* Original0x43D4E..0x43D50. */
REGION void tsl9_resident_ble_initialization_block_43d4e(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x43D50..0x43D5C. */
REGION void tsl9_resident_ble_initialization_block_43d50(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43D5C..0x43D5E. */
REGION void tsl9_resident_ble_initialization_block_43d5c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x43D5E..0x43D62. */
REGION void tsl9_resident_ble_initialization_block_43d5e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000039C..0x200003AE. */
REGION void tsl9_candidate_memset_2000039c(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_ble_initialization_edge_200003ac:\n.option push\n.option rvc\nc.beqz a0,.Lresident_ble_initialization_edge_200003ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_200003b4\n");
    __builtin_unreachable();
}

/* Original0x200003AE..0x200003B4. */
REGION void tsl9_resident_ble_initialization_block_200003ae(void)
{
    REGS;
    a4 = a0 + a2; LIVE;
    PORT(".Lresident_ble_initialization_edge_200003b2:\n.option push\n.option rvc\nc.bnez a2,.Lresident_ble_initialization_edge_200003b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_ble_initialization_block_200003be\n");
    __builtin_unreachable();
}

/* Original0x200003B4..0x200003BE. */
REGION void tsl9_resident_ble_initialization_block_200003b4(void)
{
    REGS;
    a4 = UINT32_C(0x40024000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000020c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200003BE..0x200003C8. */
REGION void tsl9_resident_ble_initialization_block_200003be(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xffffffff)) = (uint8_t)a1; LIVE;
    PORT(".Lresident_ble_initialization_edge_200003c4:\n.option push\n.option norvc\nbne a0,a4,.Lresident_ble_initialization_edge_200003c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_ble_initialization_block_200003be\n");
    __builtin_unreachable();
}

/* Original0x200003C8..0x200003CA. */
REGION void tsl9_resident_ble_initialization_block_200003c8(void)
{
    REGS;
    PORT(".Lresident_ble_initialization_edge_200003c8:\n.option push\n.option rvc\nc.j .Lresident_ble_initialization_edge_200003c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_ble_initialization_block_200003b4\n");
    __builtin_unreachable();
}
