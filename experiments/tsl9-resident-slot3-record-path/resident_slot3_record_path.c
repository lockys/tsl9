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

/* Seven complete conditional SDK slot3/record bodies:1180B/407i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43174..0x43186. */
REGION void tsl9_candidate_external_flash_43174(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000194)); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000018c)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x43186..0x4318A. */
REGION void tsl9_resident_slot3_record_path_block_43186(void)
{
    REGS;
    PORT(".Lresident_slot3_record_path_edge_43186:\n.option push\n.option norvc\nbne a3,a5,.Lresident_slot3_record_path_edge_43186\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_4318c\n");
    __builtin_unreachable();
}

/* Original0x4318A..0x4318C. */
REGION void tsl9_resident_slot3_record_path_block_4318a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4318C..0x43190. */
REGION void tsl9_resident_slot3_record_path_block_4318c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23fa\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_4318e:\n.option push\n.option rvc\nc.bnez a4,.Lresident_slot3_record_path_edge_4318e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_43198\n");
    __builtin_unreachable();
}

/* Original0x43190..0x43196. */
REGION void tsl9_resident_slot3_record_path_block_43190(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23da\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_43192:\n.option push\n.option norvc\nbleu a4,a0,.Lresident_slot3_record_path_edge_43192\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_43198\n");
    __builtin_unreachable();
}

/* Original0x43196..0x43198. */
REGION void tsl9_resident_slot3_record_path_block_43196(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43198..0x4319C. */
REGION void tsl9_resident_slot3_record_path_block_43198(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_slot3_record_path_edge_4319a:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_4319a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_43186\n");
    __builtin_unreachable();
}

/* Original0x43932..0x43956. */
REGION void tsl9_candidate_external_flash_43932(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a2\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_43954:\n.option push\n.option rvc\nc.jal .Lresident_slot3_record_path_edge_43954\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x43956..0x43962. */
REGION void tsl9_resident_slot3_record_path_block_43956(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    PORT(".Lresident_slot3_record_path_literal_4395a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_timer_lookup_20000314\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot3_record_path_literal_4395a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43962..0x43966. */
REGION void tsl9_resident_slot3_record_path_block_43962(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_43964:\n.option push\n.option rvc\nc.beqz a0,.Lresident_slot3_record_path_edge_43964\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_4398c\n");
    __builtin_unreachable();
}

/* Original0x43966..0x4398A. */
REGION void tsl9_resident_slot3_record_path_block_43966(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000023c)); LIVE;
    a2 = UINT32_C(0x00000640); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmul a5, a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhu a1, a1, s1\n.option pop\n");
    a0 = a5 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a0, a5\n.option pop\n");
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_slot3_record_path_edge_43986:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_43986\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x4398A..0x4398C. */
REGION void tsl9_resident_slot3_record_path_block_4398a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4398C..0x439A8. */
REGION void tsl9_resident_slot3_record_path_block_4398c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nseqz a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E76C..0x5E78E. */
REGION void tsl9_candidate_external_flash_5e76c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s2, 952\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 128(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 77(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s2, 952\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e78c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e78c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e7d8\n");
    __builtin_unreachable();
}

/* Original0x5E78E..0x5E794. */
REGION void tsl9_resident_slot3_record_path_block_5e78e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203c\n.option pop\n");
    a0 = UINT32_C(0x00000012); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e792:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e792\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e7cc\n");
    __builtin_unreachable();
}

/* Original0x5E794..0x5E79E. */
REGION void tsl9_resident_slot3_record_path_block_5e794(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x000004a6); LIVE;
    __builtin_unreachable();
}

/* Original0x5E79E..0x5E7AA. */
REGION void tsl9_resident_slot3_record_path_block_5e79e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s1, 78\n.option pop\n");
    PORT(".Lresident_slot3_record_path_literal_5e7a2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot3_record_path_literal_5e7a2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E7AA..0x5E7BA. */
REGION void tsl9_resident_slot3_record_path_block_5e7aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 11(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb4bc\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 17(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb89c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 19(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb8bc\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 18(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28bc\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa498\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e7b8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e7b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e84a\n");
    __builtin_unreachable();
}

/* Original0x5E7BA..0x5E7BE. */
REGION void tsl9_resident_slot3_record_path_block_5e7ba(void)
{
    REGS;
    PORT(".Lresident_slot3_record_path_edge_5e7ba:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e7ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_heap_free_sum_430e0\n");
    __builtin_unreachable();
}

/* Original0x5E7BE..0x5E7C2. */
REGION void tsl9_resident_slot3_record_path_block_5e7be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 88(s0)\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e7c0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e7c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e7e8\n");
    __builtin_unreachable();
}

/* Original0x5E7C2..0x5E7CA. */
REGION void tsl9_resident_slot3_record_path_block_5e7c2(void)
{
    REGS;
    a5 = UINT32_C(0x00000400); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e7c6:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_slot3_record_path_edge_5e7c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e7e4\n");
    __builtin_unreachable();
}

/* Original0x5E7CA..0x5E7CC. */
REGION void tsl9_resident_slot3_record_path_block_5e7ca(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    __builtin_unreachable();
}

/* Original0x5E7CC..0x5E7D8. */
REGION void tsl9_resident_slot3_record_path_block_5e7cc(void)
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

/* Original0x5E7D8..0x5E7E4. */
REGION void tsl9_resident_slot3_record_path_block_5e7d8(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x000004a0); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e7e2:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e7e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e79e\n");
    __builtin_unreachable();
}

/* Original0x5E7E4..0x5E7E8. */
REGION void tsl9_resident_slot3_record_path_block_5e7e4(void)
{
    REGS;
    a0 = a0 + UINT32_C(0xfffffc00); LIVE;
    __builtin_unreachable();
}

/* Original0x5E7E8..0x5E7EE. */
REGION void tsl9_resident_slot3_record_path_block_5e7e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 180(s0)\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e7ec:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e7ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e804\n");
    __builtin_unreachable();
}

/* Original0x5E7EE..0x5E802. */
REGION void tsl9_resident_slot3_record_path_block_5e7ee(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x000001ec); LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 16(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2b1e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 15(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3778\n.option pop\n");
    a5 = a5 * a4; LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e7fe:\n.option push\n.option norvc\nbleu a0,a5,.Lresident_slot3_record_path_edge_5e7fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e7ca\n");
    __builtin_unreachable();
}

/* Original0x5E802..0x5E804. */
REGION void tsl9_resident_slot3_record_path_block_5e802(void)
{
    REGS;
    a0 = a0 - a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5E804..0x5E80E. */
REGION void tsl9_resident_slot3_record_path_block_5e804(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\ndivu s0, a0, a5\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e80a:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e80a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43174\n");
    __builtin_unreachable();
}

/* Original0x5E80E..0x5E814. */
REGION void tsl9_resident_slot3_record_path_block_5e80e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e810:\n.option push\n.option norvc\nbleu s0,a0,.Lresident_slot3_record_path_edge_5e810\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e816\n");
    __builtin_unreachable();
}

/* Original0x5E814..0x5E816. */
REGION void tsl9_resident_slot3_record_path_block_5e814(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E816..0x5E822. */
REGION void tsl9_resident_slot3_record_path_block_5e816(void)
{
    REGS;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 66(s1)\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e820:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_5e820\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e7ca\n");
    __builtin_unreachable();
}

/* Original0x5E822..0x5E836. */
REGION void tsl9_resident_slot3_record_path_block_5e822(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    a0 = a5 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x0000024e); LIVE;
    PORT(".Lresident_slot3_record_path_literal_5e82e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot3_record_path_literal_5e82e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E836..0x5E844. */
REGION void tsl9_resident_slot3_record_path_block_5e836(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a2, 66(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a0, 68(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a4, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a6, a2, -1\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x5E844..0x5E848. */
REGION void tsl9_resident_slot3_record_path_block_5e844(void)
{
    REGS;
    PORT(".Lresident_slot3_record_path_edge_5e844:\n.option push\n.option norvc\nblt a5,a2,.Lresident_slot3_record_path_edge_5e844\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e896\n");
    __builtin_unreachable();
}

/* Original0x5E848..0x5E84A. */
REGION void tsl9_resident_slot3_record_path_block_5e848(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a0, 72(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E84A..0x5E862. */
REGION void tsl9_resident_slot3_record_path_block_5e84a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 32(s1)\n.option pop\n");
    a3 = a5 + UINT32_C(0x0000019c); LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 3(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x32a8\n.option pop\n");
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\naddi s0, a5, 412\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e85e:\n.option push\n.option norvc\nbne a4,a3,.Lresident_slot3_record_path_edge_5e85e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e8ae\n");
    __builtin_unreachable();
}

/* Original0x5E862..0x5E868. */
REGION void tsl9_resident_slot3_record_path_block_5e862(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 22(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28f2\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 50(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x38be\n.option pop\n");
    a2 = a2 + a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5E868..0x5E86E. */
REGION void tsl9_resident_slot3_record_path_block_5e868(void)
{
    REGS;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e86a:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e86a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43932\n");
    __builtin_unreachable();
}

/* Original0x5E86E..0x5E876. */
REGION void tsl9_resident_slot3_record_path_block_5e86e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3028\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e872:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e872\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x5E876..0x5E87A. */
REGION void tsl9_resident_slot3_record_path_block_5e876(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 56(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3c92\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e878:\n.option push\n.option rvc\nc.beqz a2,.Lresident_slot3_record_path_edge_5e878\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e88e\n");
    __builtin_unreachable();
}

/* Original0x5E87A..0x5E88E. */
REGION void tsl9_resident_slot3_record_path_block_5e87a(void)
{
    REGS;
    a0 = UINT32_C(0x00061000); LIVE;
    PORT(".option push\n.option norvc\naddi a3, s1, 49\n.option pop\n");
    a2 = a2 << UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff838); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e88a:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e88a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43874\n");
    __builtin_unreachable();
}

/* Original0x5E88E..0x5E896. */
REGION void tsl9_resident_slot3_record_path_block_5e88e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 952(s2)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e894:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e894\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e7cc\n");
    __builtin_unreachable();
}

/* Original0x5E896..0x5E89A. */
REGION void tsl9_resident_slot3_record_path_block_5e896(void)
{
    REGS;
    PORT(".Lresident_slot3_record_path_edge_5e896:\n.option push\n.option norvc\nble a6,a5,.Lresident_slot3_record_path_edge_5e896\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e8a8\n");
    __builtin_unreachable();
}

/* Original0x5E89A..0x5E8A0. */
REGION void tsl9_resident_slot3_record_path_block_5e89a(void)
{
    REGS;
    a3 = a4 + UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E8A0..0x5E8A8. */
REGION void tsl9_resident_slot3_record_path_block_5e8a0(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a1; LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e8a6:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e8a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e844\n");
    __builtin_unreachable();
}

/* Original0x5E8A8..0x5E8AE. */
REGION void tsl9_resident_slot3_record_path_block_5e8a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e8ac:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e8ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e8a0\n");
    __builtin_unreachable();
}

/* Original0x5E8AE..0x5E8B4. */
REGION void tsl9_resident_slot3_record_path_block_5e8ae(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e8b0:\n.option push\n.option norvc\nbne a4,a5,.Lresident_slot3_record_path_edge_5e8b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5e8b8\n");
    __builtin_unreachable();
}

/* Original0x5E8B4..0x5E8B8. */
REGION void tsl9_resident_slot3_record_path_block_5e8b4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 50(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x38b2\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e8b6:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e8b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e868\n");
    __builtin_unreachable();
}

/* Original0x5E8B8..0x5E8BC. */
REGION void tsl9_resident_slot3_record_path_block_5e8b8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 22(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28f2\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e8ba:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_5e8ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_5e868\n");
    __builtin_unreachable();
}

/* Original0x5E8BC..0x5E8D2. */
REGION void tsl9_candidate_external_flash_5e8bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x0000026e); LIVE;
    a0 = UINT32_C(0x000000e8); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_slot3_record_path_literal_5e8ca:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot3_record_path_literal_5e8ca\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E8D2..0x5E8D6. */
REGION void tsl9_resident_slot3_record_path_block_5e8d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5e8d4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_slot3_record_path_edge_5e8d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e946\n");
    __builtin_unreachable();
}

/* Original0x5E8D6..0x5E8E4. */
REGION void tsl9_resident_slot3_record_path_block_5e8d6(void)
{
    REGS;
    a2 = UINT32_C(0x000000e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_slot3_record_path_literal_5e8dc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_slot3_record_path_literal_5e8dc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E8E4..0x5E938. */
REGION void tsl9_resident_slot3_record_path_block_5e8e4(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsw s0, 1080(a5)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsb zero, 10(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 8(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    PORT(".option push\n.option rvc\nsw a4, 116(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a5, 120(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffff); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 48(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb81e\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 125(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 129(s0)\n.option pop\n");
    a5 = UINT32_C(0x0005e000); LIVE;
    a5 = a5 + UINT32_C(0x0000076c); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 104(s0)\n.option pop\n");
    a5 = UINT32_C(0x00060000); LIVE;
    a5 = a5 + UINT32_C(0x000004a6); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 108(s0)\n.option pop\n");
    a5 = UINT32_C(0x00060000); LIVE;
    a5 = a5 + UINT32_C(0x00000350); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 112(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000240)); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e936:\n.option push\n.option rvc\nc.bnez a5,.Lresident_slot3_record_path_edge_5e936\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_5e946\n");
    __builtin_unreachable();
}

/* Original0x5E938..0x5E946. */
REGION void tsl9_resident_slot3_record_path_block_5e938(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004f8)); LIVE;
    a1 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_slot3_record_path_edge_5e942:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5e942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43b28\n");
    __builtin_unreachable();
}

/* Original0x5E946..0x5E950. */
REGION void tsl9_resident_slot3_record_path_block_5e946(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ECA2..0x5ECB0. */
REGION void tsl9_candidate_external_flash_5eca2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5ecac:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5ecac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x5ECB0..0x5ECC8. */
REGION void tsl9_resident_slot3_record_path_block_5ecb0(void)
{
    REGS;
    a5 = UINT32_C(0xffffffa0); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa4bc\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019f)); LIVE;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5ecc4:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5ecc4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x5ECC8..0x5ECE4. */
REGION void tsl9_resident_slot3_record_path_block_5ecc8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a3, 22(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x28f6\n.option pop\n");
    a4 = UINT32_C(0x00000640); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 952(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\ndiv a4, a4, a3\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 952(s0)\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_5ece0:\n.option push\n.option norvc\nblt a5,a4,.Lresident_slot3_record_path_edge_5ece0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_5ecec\n");
    __builtin_unreachable();
}

/* Original0x5ECE4..0x5ECE8. */
REGION void tsl9_resident_slot3_record_path_block_5ece4(void)
{
    REGS;
    PORT(".Lresident_slot3_record_path_edge_5ece4:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_5ece4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43edc\n");
    __builtin_unreachable();
}

/* Original0x5ECE8..0x5ECEC. */
REGION void tsl9_resident_slot3_record_path_block_5ece8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 952(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5ECEC..0x5ECF6. */
REGION void tsl9_resident_slot3_record_path_block_5ecec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60350..0x6036A. */
REGION void tsl9_candidate_external_flash_60350(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1080(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 33(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_slot3_record_path_edge_60366:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_slot3_record_path_edge_60366\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60424\n");
    __builtin_unreachable();
}

/* Original0x6036A..0x6037E. */
REGION void tsl9_resident_slot3_record_path_block_6036a(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a4 = a3 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3378\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a0 = a3 + UINT32_C(0x00000514); LIVE;
    PORT(".Lresident_slot3_record_path_edge_6037a:\n.option push\n.option norvc\nbne a2,a4,.Lresident_slot3_record_path_edge_6037a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60424\n");
    __builtin_unreachable();
}

/* Original0x6037E..0x60386. */
REGION void tsl9_resident_slot3_record_path_block_6037e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a2, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3410\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_60382:\n.option push\n.option norvc\nbne a5,s1,.Lresident_slot3_record_path_edge_60382\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_6042e\n");
    __builtin_unreachable();
}

/* Original0x60386..0x6038E. */
REGION void tsl9_resident_slot3_record_path_block_60386(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lresident_slot3_record_path_edge_6038a:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_slot3_record_path_edge_6038a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60498\n");
    __builtin_unreachable();
}

/* Original0x6038E..0x6039A. */
REGION void tsl9_resident_slot3_record_path_block_6038e(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    a1 = UINT32_C(0x00000026); LIVE;
    PORT(".Lresident_slot3_record_path_edge_60396:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_slot3_record_path_edge_60396\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_6039e\n");
    __builtin_unreachable();
}

/* Original0x6039A..0x6039E. */
REGION void tsl9_resident_slot3_record_path_block_6039a(void)
{
    REGS;
    a1 = UINT32_C(0x00000027); LIVE;
    __builtin_unreachable();
}

/* Original0x6039E..0x6041E. */
REGION void tsl9_resident_slot3_record_path_block_6039e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    /* Conditional Xwchc: qk.c.sb a1, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb40c\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlui a6, 0xffce0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a6, a6, -1\n.option pop\n");
    a2 = a2 & UINT32_C(0xfffffe7f); LIVE;
    a2 = a2 | UINT32_C(0x00000080); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nand a2, a2, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    a2 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x0000053c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000050)) = (uint32_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000514)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000001)) = (uint8_t)0; LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = UINT32_C(0x00330000); LIVE;
    a3 = a3 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 & UINT32_C(0xfffffe7f); LIVE;
    a3 = a3 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a3 = a3 | a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000050)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a3 = a3 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a3; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffff80); LIVE;
    a4 = a4 | a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x6041E..0x60424. */
REGION void tsl9_resident_slot3_record_path_block_6041e(void)
{
    REGS;
    a5 = UINT32_C(0xffffffa1); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x60424..0x6042E. */
REGION void tsl9_resident_slot3_record_path_block_60424(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6042E..0x60436. */
REGION void tsl9_resident_slot3_record_path_block_6042e(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lresident_slot3_record_path_edge_60432:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_slot3_record_path_edge_60432\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_6046a\n");
    __builtin_unreachable();
}

/* Original0x60436..0x60442. */
REGION void tsl9_resident_slot3_record_path_block_60436(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    a4 = UINT32_C(0x00000026); LIVE;
    PORT(".Lresident_slot3_record_path_edge_6043e:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_slot3_record_path_edge_6043e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60446\n");
    __builtin_unreachable();
}

/* Original0x60442..0x60446. */
REGION void tsl9_resident_slot3_record_path_block_60442(void)
{
    REGS;
    a4 = UINT32_C(0x00000027); LIVE;
    __builtin_unreachable();
}

/* Original0x60446..0x6046A. */
REGION void tsl9_resident_slot3_record_path_block_60446(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb418\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_slot3_record_path_edge_60468:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_60468\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_6041e\n");
    __builtin_unreachable();
}

/* Original0x6046A..0x60472. */
REGION void tsl9_resident_slot3_record_path_block_6046a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 32(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_slot3_record_path_edge_60470:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_60470\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_60498\n");
    __builtin_unreachable();
}

/* Original0x60472..0x60482. */
REGION void tsl9_resident_slot3_record_path_block_60472(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    /* Conditional Xwchc: qk.c.lhu a2, 54(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3872\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019f)); LIVE;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_slot3_record_path_edge_6047e:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_6047e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43932\n");
    __builtin_unreachable();
}

/* Original0x60482..0x60498. */
REGION void tsl9_resident_slot3_record_path_block_60482(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    PORT(".option push\n.option norvc\nsb s1, 33(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_60494:\n.option push\n.option norvc\njal zero,.Lresident_slot3_record_path_edge_60494\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6020a\n");
    __builtin_unreachable();
}

/* Original0x60498..0x604A6. */
REGION void tsl9_resident_slot3_record_path_block_60498(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_604a2:\n.option push\n.option norvc\njal zero,.Lresident_slot3_record_path_edge_604a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5eca2\n");
    __builtin_unreachable();
}

/* Original0x604A6..0x604B4. */
REGION void tsl9_candidate_external_flash_604a6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a8)); LIVE;
    PORT(".Lresident_slot3_record_path_edge_604b2:\n.option push\n.option rvc\nc.bnez a4,.Lresident_slot3_record_path_edge_604b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_60514\n");
    __builtin_unreachable();
}

/* Original0x604B4..0x604C4. */
REGION void tsl9_resident_slot3_record_path_block_604b4(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a3, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3374\n.option pop\n");
    a2 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_slot3_record_path_edge_604c0:\n.option push\n.option norvc\nbeq a2,a3,.Lresident_slot3_record_path_edge_604c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60514\n");
    __builtin_unreachable();
}

/* Original0x604C4..0x604CC. */
REGION void tsl9_resident_slot3_record_path_block_604c4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3378\n.option pop\n");
    a3 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lresident_slot3_record_path_edge_604c8:\n.option push\n.option norvc\nbeq a3,a4,.Lresident_slot3_record_path_edge_604c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_slot3_record_path_block_60514\n");
    __builtin_unreachable();
}

/* Original0x604CC..0x604E8. */
REGION void tsl9_resident_slot3_record_path_block_604cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 128(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 32(s0)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000019f)); LIVE;
    a4 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_slot3_record_path_edge_604e6:\n.option push\n.option rvc\nc.beqz a4,.Lresident_slot3_record_path_edge_604e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_604f2\n");
    __builtin_unreachable();
}

/* Original0x604E8..0x604F2. */
REGION void tsl9_resident_slot3_record_path_block_604e8(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 33(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a2, 26(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c32\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_604f0:\n.option push\n.option rvc\nc.j .Lresident_slot3_record_path_edge_604f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_slot3_record_path_block_604fe\n");
    __builtin_unreachable();
}

/* Original0x604F2..0x604F6. */
REGION void tsl9_resident_slot3_record_path_block_604f2(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_slot3_record_path_edge_604f4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_slot3_record_path_edge_604f4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_slot3_record_path_block_604e8\n");
    __builtin_unreachable();
}

/* Original0x604F6..0x604FE. */
REGION void tsl9_resident_slot3_record_path_block_604f6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 54(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3872\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 33(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x604FE..0x60504. */
REGION void tsl9_resident_slot3_record_path_block_604fe(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_slot3_record_path_edge_60500:\n.option push\n.option norvc\njal ra,.Lresident_slot3_record_path_edge_60500\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43932\n");
    __builtin_unreachable();
}

/* Original0x60504..0x60514. */
REGION void tsl9_resident_slot3_record_path_block_60504(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_slot3_record_path_edge_60510:\n.option push\n.option norvc\njal zero,.Lresident_slot3_record_path_edge_60510\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6020a\n");
    __builtin_unreachable();
}

/* Original0x60514..0x60516. */
REGION void tsl9_resident_slot3_record_path_block_60514(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
