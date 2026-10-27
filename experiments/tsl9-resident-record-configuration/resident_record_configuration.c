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

/* Three complete conditional SDK configuration-chain bodies:1028B/355i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x581CE..0x581E8. */
REGION void tsl9_candidate_external_flash_581ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000039)); LIVE;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_581e4:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_581e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_583ec\n");
    __builtin_unreachable();
}

/* Original0x581E8..0x581FA. */
REGION void tsl9_resident_record_configuration_block_581e8(void)
{
    REGS;
    a5 = UINT32_C(0xffffffb5); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17c\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000003c)); LIVE;
    a1 = UINT32_C(0x00000022); LIVE;
    PORT(".Lresident_record_configuration_edge_581f6:\n.option push\n.option norvc\njal ra,.Lresident_record_configuration_edge_581f6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x581FA..0x58204. */
REGION void tsl9_resident_record_configuration_block_581fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s2, 60(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_configuration_edge_58200:\n.option push\n.option norvc\nbleu s2,a5,.Lresident_record_configuration_edge_58200\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58206\n");
    __builtin_unreachable();
}

/* Original0x58204..0x58206. */
REGION void tsl9_resident_record_configuration_block_58204(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58206..0x5820A. */
REGION void tsl9_resident_record_configuration_block_58206(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s2, s2, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5820A..0x5822A. */
REGION void tsl9_resident_record_configuration_block_5820a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s0, 148(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000022); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa49c\n.option pop\n");
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa01c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20f8\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    a5 = UINT32_C(0x000000b4); LIVE;
    PORT(".option push\n.option norvc\naddi s3, s3, 952\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58226:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_58226\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5823c\n");
    __builtin_unreachable();
}

/* Original0x5822A..0x58236. */
REGION void tsl9_resident_record_configuration_block_5822a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 216(s3)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_record_configuration_edge_58232:\n.option push\n.option norvc\nbgez a4,.Lresident_record_configuration_edge_58232\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5823c\n");
    __builtin_unreachable();
}

/* Original0x58236..0x5823C. */
REGION void tsl9_resident_record_configuration_block_58236(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa01c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5823C..0x58250. */
REGION void tsl9_resident_record_configuration_block_5823c(void)
{
    REGS;
    a5 = UINT32_C(0x00000022); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 1(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 100(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\naddi s4, s1, 102\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5824c:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_5824c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58262\n");
    __builtin_unreachable();
}

/* Original0x58250..0x58262. */
REGION void tsl9_resident_record_configuration_block_58250(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a1, 132(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    a1 = a1 + UINT32_C(0x0000000c); LIVE;
    PORT(".Lresident_record_configuration_literal_5825a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_5825a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58262..0x5826A. */
REGION void tsl9_resident_record_configuration_block_58262(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 101(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_configuration_edge_58268:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_configuration_edge_58268\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58274\n");
    __builtin_unreachable();
}

/* Original0x5826A..0x58274. */
REGION void tsl9_resident_record_configuration_block_5826a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 100(s1)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_configuration_edge_58270:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_58270\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5827c\n");
    __builtin_unreachable();
}

/* Original0x58274..0x5827C. */
REGION void tsl9_resident_record_configuration_block_58274(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201c\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa01c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5827C..0x5828C. */
REGION void tsl9_resident_record_configuration_block_5827c(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 2\n.option pop\n");
    PORT(".Lresident_record_configuration_literal_58284:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_58284\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5828C..0x58292. */
REGION void tsl9_resident_record_configuration_block_5828c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 117(s1)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58290:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_58290\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_5829a\n");
    __builtin_unreachable();
}

/* Original0x58292..0x5829A. */
REGION void tsl9_resident_record_configuration_block_58292(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x201c\n.option pop\n");
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa01c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5829A..0x582AC. */
REGION void tsl9_resident_record_configuration_block_5829a(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s1, 118\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 8\n.option pop\n");
    PORT(".Lresident_record_configuration_literal_582a4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_582a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x582AC..0x582D8. */
REGION void tsl9_resident_record_configuration_block_582ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 88(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 89(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 15(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb47c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 90(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 91(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 17(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 92(s1)\n.option pop\n");
    a4 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 18(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa83c\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 20(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa85c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 19(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb838\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_configuration_edge_582d4:\n.option push\n.option norvc\nbne s2,a5,.Lresident_record_configuration_edge_582d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_582da\n");
    __builtin_unreachable();
}

/* Original0x582D8..0x582DA. */
REGION void tsl9_resident_record_configuration_block_582d8(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x582DA..0x58312. */
REGION void tsl9_resident_record_configuration_block_582da(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 21(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb85c\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a5, s2, 0x1\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    PORT(".option push\n.option norvc\nlw a1, 148(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 24(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac18\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 25(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc18\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 26(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2fb8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac38\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 26(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2fba\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 27(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc38\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 32(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339e\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac58\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 29(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc5c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 180(s3)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5830e:\n.option push\n.option norvc\nbeqz a5,.Lresident_record_configuration_edge_5830e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58446\n");
    __builtin_unreachable();
}

/* Original0x58312..0x58350. */
REGION void tsl9_resident_record_configuration_block_58312(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 78(s1)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000234); LIVE;
    PORT(".option push\n.option norvc\nlhu t4, 8(a5)\n.option pop\n");
    a3 = UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nlhu a4, 42(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, t4, 400\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a2, a2, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a3, 96(s1)\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000022); LIVE;
    PORT(".option push\n.option norvc\nlw t0, 156(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t5, 4(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x1\n.option pop\n");
    a4 = a4 + UINT32_C(0x0000000b); LIVE;
    PORT(".option push\n.option rvc\nli t2, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nli s2, 800\n.option pop\n");
    PORT(".option push\n.option rvc\nli t6, 5\n.option pop\n");
    a2 = a2 + a3; LIVE;
    __builtin_unreachable();
}

/* Original0x58350..0x58354. */
REGION void tsl9_resident_record_configuration_block_58350(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, t0\n.option pop\n");
    PORT(".option push\n.option rvc\nli t1, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58354..0x5835A. */
REGION void tsl9_resident_record_configuration_block_58354(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 78(s1)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58358:\n.option push\n.option rvc\nc.bnez a0,.Lresident_record_configuration_edge_58358\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58400\n");
    __builtin_unreachable();
}

/* Original0x5835A..0x5835E. */
REGION void tsl9_resident_record_configuration_block_5835a(void)
{
    REGS;
    PORT(".Lresident_record_configuration_edge_5835a:\n.option push\n.option norvc\nbltu a4,t1,.Lresident_record_configuration_edge_5835a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5836c\n");
    __builtin_unreachable();
}

/* Original0x5835E..0x5836C. */
REGION void tsl9_resident_record_configuration_block_5835e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 78(s1)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58368:\n.option push\n.option norvc\nbleu a5,t6,.Lresident_record_configuration_edge_58368\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58350\n");
    __builtin_unreachable();
}

/* Original0x5836C..0x583EC. */
REGION void tsl9_resident_record_configuration_block_5836c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 78(s1)\n.option pop\n");
    a3 = UINT32_C(0x82000000); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 22(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa87c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 78(s1)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 23(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb87c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 262(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 30(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xac7c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 263(s3)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc7c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 264(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 32(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 265(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 33(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 266(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 34(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000023)); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000023)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000200)); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a4 = a5 << UINT32_C(0x00000019); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & a3; LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x583EC..0x583FC. */
REGION void tsl9_resident_record_configuration_block_583ec(void)
{
    REGS;
    a5 = UINT32_C(0xffffffb4); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa17c\n.option pop\n");
    a1 = UINT32_C(0x00000022); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_record_configuration_edge_583f8:\n.option push\n.option norvc\njal ra,.Lresident_record_configuration_edge_583f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x583FC..0x58400. */
REGION void tsl9_resident_record_configuration_block_583fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_583fe:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_583fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_5820a\n");
    __builtin_unreachable();
}

/* Original0x58400..0x5841E. */
REGION void tsl9_resident_record_configuration_block_58400(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a3, a5, t4\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t3, 144(a0)\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000190); LIVE;
    PORT(".option push\n.option norvc\ndivu a3, a3, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a7, a3, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nsltu a3, a7, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a6, a7\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5841a:\n.option push\n.option norvc\nbne t2,a3,.Lresident_record_configuration_edge_5841a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58422\n");
    __builtin_unreachable();
}

/* Original0x5841E..0x58422. */
REGION void tsl9_resident_record_configuration_block_5841e(void)
{
    REGS;
    PORT(".Lresident_record_configuration_edge_5841e:\n.option push\n.option norvc\nbltu a7,t5,.Lresident_record_configuration_edge_5841e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58426\n");
    __builtin_unreachable();
}

/* Original0x58422..0x58426. */
REGION void tsl9_resident_record_configuration_block_58422(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a6, a7, t5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58426..0x5842E. */
REGION void tsl9_resident_record_configuration_block_58426(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a3, a6, t3\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5842a:\n.option push\n.option norvc\nbltu t3,a6,.Lresident_record_configuration_edge_5842a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5843c\n");
    __builtin_unreachable();
}

/* Original0x5842E..0x58436. */
REGION void tsl9_resident_record_configuration_block_5842e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a3, t3, a6\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58432:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_record_configuration_edge_58432\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5843c\n");
    __builtin_unreachable();
}

/* Original0x58436..0x5843C. */
REGION void tsl9_resident_record_configuration_block_58436(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 78(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5843C..0x58440. */
REGION void tsl9_resident_record_configuration_block_5843c(void)
{
    REGS;
    PORT(".Lresident_record_configuration_edge_5843c:\n.option push\n.option norvc\nbleu t1,a3,.Lresident_record_configuration_edge_5843c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58442\n");
    __builtin_unreachable();
}

/* Original0x58440..0x58442. */
REGION void tsl9_resident_record_configuration_block_58440(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv t1, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58442..0x58446. */
REGION void tsl9_resident_record_configuration_block_58442(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_record_configuration_edge_58444:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_58444\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58354\n");
    __builtin_unreachable();
}

/* Original0x58446..0x5845A. */
REGION void tsl9_resident_record_configuration_block_58446(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 25(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x3d9c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 24(a1). */
    PORT(".option push\n.option rvc\n.2byte 0x2d98\n.option pop\n");
    a3 = UINT32_C(0x00000006); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a5 = a5 >> UINT32_C(0x00000003); LIVE;
    a5 = a5 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58456:\n.option push\n.option norvc\nbleu a5,a3,.Lresident_record_configuration_edge_58456\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_5845c\n");
    __builtin_unreachable();
}

/* Original0x5845A..0x5845C. */
REGION void tsl9_resident_record_configuration_block_5845a(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0x5845C..0x58462. */
REGION void tsl9_resident_record_configuration_block_5845c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a4, 78(s1)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58460:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_58460\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_5836c\n");
    __builtin_unreachable();
}

/* Original0x58744..0x58750. */
REGION void tsl9_candidate_external_flash_58744(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5874c:\n.option push\n.option norvc\njal ra,.Lresident_record_configuration_edge_5874c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_581ce\n");
    __builtin_unreachable();
}

/* Original0x58750..0x5877E. */
REGION void tsl9_resident_record_configuration_block_58750(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw a4, 148(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a3 = UINT32_C(0x00800000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000070)) = (uint32_t)a4; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_record_configuration_literal_58776:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_58776\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5877E..0x58788. */
REGION void tsl9_resident_record_configuration_block_5877e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58788..0x587A6. */
REGION void tsl9_candidate_external_flash_58788(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000098)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".Lresident_record_configuration_literal_5879e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_5879e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x587A6..0x587AA. */
REGION void tsl9_resident_record_configuration_block_587a6(void)
{
    REGS;
    PORT(".Lresident_record_configuration_edge_587a6:\n.option push\n.option norvc\nbnez a0,.Lresident_record_configuration_edge_587a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_588a0\n");
    __builtin_unreachable();
}

/* Original0x587AA..0x587BE. */
REGION void tsl9_resident_record_configuration_block_587aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s1, 152(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3098\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa438\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_587ba:\n.option push\n.option norvc\nbne a5,a3,.Lresident_record_configuration_edge_587ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_588a4\n");
    __builtin_unreachable();
}

/* Original0x587BE..0x587CC. */
REGION void tsl9_resident_record_configuration_block_587be(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20bc\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a2, 61(s0)\n.option pop\n");
    a3 = a5 >> UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_record_configuration_edge_587c8:\n.option push\n.option norvc\nbne a2,a3,.Lresident_record_configuration_edge_587c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_588a8\n");
    __builtin_unreachable();
}

/* Original0x587CC..0x587D8. */
REGION void tsl9_resident_record_configuration_block_587cc(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s1, 4\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_587d4:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_record_configuration_edge_587d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_588ac\n");
    __builtin_unreachable();
}

/* Original0x587D8..0x587E2. */
REGION void tsl9_resident_record_configuration_block_587d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_record_configuration_edge_587e0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_587e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58806\n");
    __builtin_unreachable();
}

/* Original0x587E2..0x58802. */
REGION void tsl9_resident_record_configuration_block_587e2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 116(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 117(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 118\n.option pop\n");
    PORT(".Lresident_record_configuration_literal_587fa:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_587fa\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58802..0x58806. */
REGION void tsl9_resident_record_configuration_block_58802(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s1, 10\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58806..0x58810. */
REGION void tsl9_resident_record_configuration_block_58806(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 124(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_configuration_edge_5880e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_5880e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58834\n");
    __builtin_unreachable();
}

/* Original0x58810..0x58834. */
REGION void tsl9_resident_record_configuration_block_58810(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 124(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 152(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 126\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, 6\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 125(s0)\n.option pop\n");
    PORT(".Lresident_record_configuration_literal_5882c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_configuration_literal_5882c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58834..0x5883A. */
REGION void tsl9_resident_record_configuration_block_58834(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 3(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x30bc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_record_configuration_edge_58838:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_58838\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58848\n");
    __builtin_unreachable();
}

/* Original0x5883A..0x58848. */
REGION void tsl9_resident_record_configuration_block_5883a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 63(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_record_configuration_edge_58844:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_58844\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_588b0\n");
    __builtin_unreachable();
}

/* Original0x58848..0x5884E. */
REGION void tsl9_resident_record_configuration_block_58848(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5884a:\n.option push\n.option norvc\njal ra,.Lresident_record_configuration_edge_5884a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_585c8\n");
    __builtin_unreachable();
}

/* Original0x5884E..0x58858. */
REGION void tsl9_resident_record_configuration_block_5884e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nli s1, 127\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58854:\n.option push\n.option norvc\nbne a0,a5,.Lresident_record_configuration_edge_58854\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}

/* Original0x58858..0x5885E. */
REGION void tsl9_resident_record_configuration_block_58858(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 62(s0)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5885c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_5885c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58876\n");
    __builtin_unreachable();
}

/* Original0x5885E..0x58868. */
REGION void tsl9_resident_record_configuration_block_5885e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 62(s0)\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_58864:\n.option push\n.option norvc\njal ra,.Lresident_record_configuration_edge_58864\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x58868..0x58876. */
REGION void tsl9_resident_record_configuration_block_58868(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58876..0x58880. */
REGION void tsl9_resident_record_configuration_block_58876(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 60(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_configuration_edge_5887c:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_configuration_edge_5887c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_configuration_block_58890\n");
    __builtin_unreachable();
}

/* Original0x58880..0x5888A. */
REGION void tsl9_resident_record_configuration_block_58880(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000051f)); LIVE;
    PORT(".Lresident_record_configuration_edge_58888:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_configuration_edge_58888\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_configuration_block_58890\n");
    __builtin_unreachable();
}

/* Original0x5888A..0x58890. */
REGION void tsl9_resident_record_configuration_block_5888a(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 60(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58890..0x588A0. */
REGION void tsl9_resident_record_configuration_block_58890(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_5889c:\n.option push\n.option norvc\njal zero,.Lresident_record_configuration_edge_5889c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58744\n");
    __builtin_unreachable();
}

/* Original0x588A0..0x588A4. */
REGION void tsl9_resident_record_configuration_block_588a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_588a2:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_588a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}

/* Original0x588A4..0x588A8. */
REGION void tsl9_resident_record_configuration_block_588a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 7\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_588a6:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_588a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}

/* Original0x588A8..0x588AC. */
REGION void tsl9_resident_record_configuration_block_588a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 5\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_588aa:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_588aa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}

/* Original0x588AC..0x588B0. */
REGION void tsl9_resident_record_configuration_block_588ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 3\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_588ae:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_588ae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}

/* Original0x588B0..0x588B4. */
REGION void tsl9_resident_record_configuration_block_588b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 20\n.option pop\n");
    PORT(".Lresident_record_configuration_edge_588b2:\n.option push\n.option rvc\nc.j .Lresident_record_configuration_edge_588b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_configuration_block_58868\n");
    __builtin_unreachable();
}
