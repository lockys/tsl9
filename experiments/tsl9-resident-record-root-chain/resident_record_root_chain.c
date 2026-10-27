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

/* Ten complete conditional SDK root-chain bodies:1700B/572i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x5784A..0x57852. */
REGION void tsl9_candidate_external_flash_5784a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000454)); LIVE;
    __builtin_unreachable();
}

/* Original0x57852..0x57854. */
REGION void tsl9_resident_record_root_chain_block_57852(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57852:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_57852\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57858\n");
    __builtin_unreachable();
}

/* Original0x57854..0x57858. */
REGION void tsl9_resident_record_root_chain_block_57854(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57858..0x5785E. */
REGION void tsl9_resident_record_root_chain_block_57858(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x279a\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_5785a:\n.option push\n.option norvc\nbeq a4,a0,.Lresident_record_root_chain_edge_5785a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_57854\n");
    __builtin_unreachable();
}

/* Original0x5785E..0x57862. */
REGION void tsl9_resident_record_root_chain_block_5785e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_record_root_chain_edge_57860:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57860\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_57852\n");
    __builtin_unreachable();
}

/* Original0x578A4..0x578C0. */
REGION void tsl9_candidate_external_flash_578a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s3, 952\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000ac)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_578be:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_578be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57932\n");
    __builtin_unreachable();
}

/* Original0x578C0..0x578E0. */
REGION void tsl9_resident_record_root_chain_block_578c0(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a4 + UINT32_C(0x000001ec); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 15(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x37fc\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000240)); LIVE;
    PORT(".option push\n.option norvc\naddi s3, s3, 952\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, a4, 492\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, a5, 1\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_578de:\n.option push\n.option rvc\nc.beqz a3,.Lresident_record_root_chain_edge_578de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_578e4\n");
    __builtin_unreachable();
}

/* Original0x578E0..0x578E4. */
REGION void tsl9_resident_record_root_chain_block_578e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli s2, a5, 0x1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x578E4..0x57912. */
REGION void tsl9_resident_record_root_chain_block_578e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu s0, 46(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a0, s2, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s1, s2, 0x4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 33\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai s0, s0, 0x5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x5\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nmul a0, s0, a0\n.option pop\n");
    a1 = UINT32_C(0x00000244); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_literal_5790a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_5790a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57912..0x57914. */
REGION void tsl9_resident_record_root_chain_block_57912(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57912:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_root_chain_edge_57912\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57932\n");
    __builtin_unreachable();
}

/* Original0x57914..0x5792E. */
REGION void tsl9_resident_record_root_chain_block_57914(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 15(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a0, 172(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a4, a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a3, s2, a3\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0xffffff54); LIVE;
    a1 = UINT32_C(0xffffff52); LIVE;
    __builtin_unreachable();
}

/* Original0x5792E..0x57932. */
REGION void tsl9_resident_record_root_chain_block_5792e(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_5792e:\n.option push\n.option norvc\nbltu a5,s2,.Lresident_record_root_chain_edge_5792e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_57942\n");
    __builtin_unreachable();
}

/* Original0x57932..0x57942. */
REGION void tsl9_resident_record_root_chain_block_57932(void)
{
    REGS;
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

/* Original0x57942..0x57946. */
REGION void tsl9_resident_record_root_chain_block_57942(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57942:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_record_root_chain_edge_57942\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_5795a\n");
    __builtin_unreachable();
}

/* Original0x57946..0x5794C. */
REGION void tsl9_resident_record_root_chain_block_57946(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a1, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa52e\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5794C..0x5795A. */
REGION void tsl9_resident_record_root_chain_block_5794c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a0 = a0 + UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_edge_57958:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57958\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_5792e\n");
    __builtin_unreachable();
}

/* Original0x5795A..0x57962. */
REGION void tsl9_resident_record_root_chain_block_5795a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a2, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa532\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    PORT(".Lresident_record_root_chain_edge_57960:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57960\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_5794c\n");
    __builtin_unreachable();
}

/* Original0x57962..0x5797A. */
REGION void tsl9_candidate_external_flash_57962(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x00000263); LIVE;
    a0 = UINT32_C(0x000001e8); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".Lresident_record_root_chain_literal_57972:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_57972\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5797A..0x5798A. */
REGION void tsl9_resident_record_root_chain_block_5797a(void)
{
    REGS;
    a2 = UINT32_C(0x000001e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_record_root_chain_literal_57982:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_57982\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5798A..0x5798E. */
REGION void tsl9_resident_record_root_chain_block_5798a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_record_root_chain_edge_5798c:\n.option push\n.option rvc\nc.beqz s0,.Lresident_record_root_chain_edge_5798c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_579be\n");
    __builtin_unreachable();
}

/* Original0x5798E..0x579A0. */
REGION void tsl9_resident_record_root_chain_block_5798e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 952\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000009c)); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_5799e:\n.option push\n.option rvc\nc.beqz a3,.Lresident_record_root_chain_edge_5799e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_579cc\n");
    __builtin_unreachable();
}

/* Original0x579A0..0x579A4. */
REGION void tsl9_resident_record_root_chain_block_579a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x579A4..0x579AA. */
REGION void tsl9_resident_record_root_chain_block_579a4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 8(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2712\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_579a6:\n.option push\n.option norvc\nbeq a2,a5,.Lresident_record_root_chain_edge_579a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_57a08\n");
    __builtin_unreachable();
}

/* Original0x579AA..0x579AE. */
REGION void tsl9_resident_record_root_chain_block_579aa(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_record_root_chain_edge_579ac:\n.option push\n.option rvc\nc.bnez a4,.Lresident_record_root_chain_edge_579ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_579a4\n");
    __builtin_unreachable();
}

/* Original0x579AE..0x579B2. */
REGION void tsl9_resident_record_root_chain_block_579ae(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41e\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_579b0:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_579b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_579f2\n");
    __builtin_unreachable();
}

/* Original0x579B2..0x579BC. */
REGION void tsl9_resident_record_root_chain_block_579b2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_literal_579b4:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_579b4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x579BC..0x579BE. */
REGION void tsl9_resident_record_root_chain_block_579bc(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x579BE..0x579C8. */
REGION void tsl9_resident_record_root_chain_block_579be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x579C8..0x579CC. */
REGION void tsl9_resident_record_root_chain_block_579c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a3\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_579ca:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_579ca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_579a4\n");
    __builtin_unreachable();
}

/* Original0x579CC..0x579E0. */
REGION void tsl9_resident_record_root_chain_block_579cc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41e\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s0, 156(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s0, 160(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 180(s1)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_579dc:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_579dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_578a4\n");
    __builtin_unreachable();
}

/* Original0x579E0..0x579F2. */
REGION void tsl9_resident_record_root_chain_block_579e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s1)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 10(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 14(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_579f0:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_579f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_579bc\n");
    __builtin_unreachable();
}

/* Original0x579F2..0x57A08. */
REGION void tsl9_resident_record_root_chain_block_579f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 0(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 180(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s0, 160(s1)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 180(s1)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57a06:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57a06\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_579e0\n");
    __builtin_unreachable();
}

/* Original0x57A08..0x57A1A. */
REGION void tsl9_resident_record_root_chain_block_57a08(void)
{
    REGS;
    a4 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a4 << UINT32_C(0x00000010); LIVE;
    a2 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_edge_57a16:\n.option push\n.option norvc\nbgez a2,.Lresident_record_root_chain_edge_57a16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_579c8\n");
    __builtin_unreachable();
}

/* Original0x57A1A..0x57A1E. */
REGION void tsl9_resident_record_root_chain_block_57a1a(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_record_root_chain_edge_57a1c:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57a1c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_579ae\n");
    __builtin_unreachable();
}

/* Original0x57A1E..0x57A36. */
REGION void tsl9_candidate_external_flash_57a1e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x000003b8); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000000ac)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, a5, 952\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57a34:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_root_chain_edge_57a34\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57a3e\n");
    __builtin_unreachable();
}

/* Original0x57A36..0x57A3E. */
REGION void tsl9_resident_record_root_chain_block_57a36(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_literal_57a36:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_57a36\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A3E..0x57A4A. */
REGION void tsl9_resident_record_root_chain_block_57a3e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 172(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A4A..0x57A64. */
REGION void tsl9_candidate_external_flash_57a4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 952\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000009c)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a5, a3\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 952\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A64..0x57A66. */
REGION void tsl9_resident_record_root_chain_block_57a64(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57a64:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_root_chain_edge_57a64\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57ab6\n");
    __builtin_unreachable();
}

/* Original0x57A66..0x57A6C. */
REGION void tsl9_resident_record_root_chain_block_57a66(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2792\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57a68:\n.option push\n.option norvc\nbne a2,a0,.Lresident_record_root_chain_edge_57a68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_57abe\n");
    __builtin_unreachable();
}

/* Original0x57A6C..0x57A6E. */
REGION void tsl9_resident_record_root_chain_block_57a6c(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57a6c:\n.option push\n.option rvc\nc.bnez a4,.Lresident_record_root_chain_edge_57a6c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57a9c\n");
    __builtin_unreachable();
}

/* Original0x57A6E..0x57A74. */
REGION void tsl9_resident_record_root_chain_block_57a6e(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsw a4, 156(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A74..0x57A7E. */
REGION void tsl9_resident_record_root_chain_block_57a74(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lresident_record_root_chain_literal_57a76:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_57a76\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A7E..0x57A8C. */
REGION void tsl9_resident_record_root_chain_block_57a7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nlhu a5, 180(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57a8a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_57a8a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57ab0\n");
    __builtin_unreachable();
}

/* Original0x57A8C..0x57A90. */
REGION void tsl9_resident_record_root_chain_block_57a8c(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57a8c:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_57a8c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57a1e\n");
    __builtin_unreachable();
}

/* Original0x57A90..0x57A94. */
REGION void tsl9_resident_record_root_chain_block_57a90(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 156(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A94..0x57A9C. */
REGION void tsl9_resident_record_root_chain_block_57a94(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57A9C..0x57AA4. */
REGION void tsl9_resident_record_root_chain_block_57a9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 160(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57aa0:\n.option push\n.option norvc\nbne a3,a5,.Lresident_record_root_chain_edge_57aa0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_57aaa\n");
    __builtin_unreachable();
}

/* Original0x57AA4..0x57AAA. */
REGION void tsl9_resident_record_root_chain_block_57aa4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a4, 160(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57aa8:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57aa8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_57a74\n");
    __builtin_unreachable();
}

/* Original0x57AAA..0x57AB0. */
REGION void tsl9_resident_record_root_chain_block_57aaa(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_record_root_chain_edge_57aae:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57aae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_57a74\n");
    __builtin_unreachable();
}

/* Original0x57AB0..0x57AB6. */
REGION void tsl9_resident_record_root_chain_block_57ab0(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 180(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57AB6..0x57ABC. */
REGION void tsl9_resident_record_root_chain_block_57ab6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 180(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_57aba:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_57aba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_57a94\n");
    __builtin_unreachable();
}

/* Original0x57ABC..0x57ABE. */
REGION void tsl9_resident_record_root_chain_block_57abc(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_57abc:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57abc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_57a8c\n");
    __builtin_unreachable();
}

/* Original0x57ABE..0x57AC4. */
REGION void tsl9_resident_record_root_chain_block_57abe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_record_root_chain_edge_57ac2:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_57ac2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_57a64\n");
    __builtin_unreachable();
}

/* Original0x58462..0x5847C. */
REGION void tsl9_candidate_external_flash_58462(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 412\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3028\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_58478:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_58478\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x5847C..0x58486. */
REGION void tsl9_resident_record_root_chain_block_5847c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3028\n.option pop\n");
    a1 = UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_record_root_chain_edge_58482:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_58482\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x58486..0x58498. */
REGION void tsl9_resident_record_root_chain_block_58486(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 4(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 6(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58498..0x584A8. */
REGION void tsl9_candidate_external_flash_58498(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_584a4:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_584a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_59e64\n");
    __builtin_unreachable();
}

/* Original0x584A8..0x584AC. */
REGION void tsl9_resident_record_root_chain_block_584a8(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_584a8:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_584a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5784a\n");
    __builtin_unreachable();
}

/* Original0x584AC..0x584B0. */
REGION void tsl9_resident_record_root_chain_block_584ac(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_584ac:\n.option push\n.option norvc\nbeqz a0,.Lresident_record_root_chain_edge_584ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_585ae\n");
    __builtin_unreachable();
}

/* Original0x584B0..0x5852C. */
REGION void tsl9_resident_record_root_chain_block_584b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 96(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 148(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nli a6, 0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000088)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw a4, 88(s1)\n.option pop\n");
    a1 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000098)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw a4, 92(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    a1 = a1 + UINT32_C(0x000004be); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000009c)) = (uint32_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 21(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3bd8\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000138); LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffeff)) = (uint8_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 23(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3bf8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 22(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bf4\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 952\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xffffff00)) = (uint16_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 25(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3f98\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 24(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2f94\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xffffff02)) = (uint16_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 27(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3fb8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 26(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2fb4\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xffffff04)) = (uint16_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 28(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2fd8\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 29(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3fdc\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xffffff06)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a6, 4(a0)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffefd)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_record_root_chain_literal_58524:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_58524\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5852C..0x58536. */
REGION void tsl9_resident_record_root_chain_block_5852c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 6(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x20f8\n.option pop\n");
    a5 = UINT32_C(0x000000b6); LIVE;
    PORT(".Lresident_record_root_chain_edge_58532:\n.option push\n.option norvc\nbne a4,a5,.Lresident_record_root_chain_edge_58532\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_58556\n");
    __builtin_unreachable();
}

/* Original0x58536..0x58546. */
REGION void tsl9_resident_record_root_chain_block_58536(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 320(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 60(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_record_root_chain_edge_58542:\n.option push\n.option norvc\nbne a5,a4,.Lresident_record_root_chain_edge_58542\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_585be\n");
    __builtin_unreachable();
}

/* Original0x58546..0x58556. */
REGION void tsl9_resident_record_root_chain_block_58546(void)
{
    REGS;
    a5 = UINT32_C(0x00000202); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 326(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 328(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_58554:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_58554\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_58578\n");
    __builtin_unreachable();
}

/* Original0x58556..0x58562. */
REGION void tsl9_resident_record_root_chain_block_58556(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 216(s2)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_record_root_chain_edge_5855e:\n.option push\n.option norvc\nbgez a4,.Lresident_record_root_chain_edge_5855e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_58578\n");
    __builtin_unreachable();
}

/* Original0x58562..0x58578. */
REGION void tsl9_resident_record_root_chain_block_58562(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 148(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 152(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x239c\n.option pop\n");
    a5 = a5 & a4; LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 320(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x58578..0x5857E. */
REGION void tsl9_resident_record_root_chain_block_58578(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_5857a:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_5857a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_59d3e\n");
    __builtin_unreachable();
}

/* Original0x5857E..0x5858C. */
REGION void tsl9_resident_record_root_chain_block_5857e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 224(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x0000000a); LIVE;
    a5 = a5 & UINT32_C(0x00000200); LIVE;
    PORT(".Lresident_record_root_chain_edge_5858a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_record_root_chain_edge_5858a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_5858e\n");
    __builtin_unreachable();
}

/* Original0x5858C..0x5858E. */
REGION void tsl9_resident_record_root_chain_block_5858c(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x5858E..0x58596. */
REGION void tsl9_resident_record_root_chain_block_5858e(void)
{
    REGS;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_record_root_chain_edge_58592:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_58592\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x58596..0x585A2. */
REGION void tsl9_resident_record_root_chain_block_58596(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 216(s2)\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000011); LIVE;
    PORT(".Lresident_record_root_chain_edge_5859e:\n.option push\n.option norvc\nbgez a4,.Lresident_record_root_chain_edge_5859e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_585ae\n");
    __builtin_unreachable();
}

/* Original0x585A2..0x585AE. */
REGION void tsl9_resident_record_root_chain_block_585a2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_record_root_chain_edge_585aa:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_585aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x585AE..0x585BE. */
REGION void tsl9_resident_record_root_chain_block_585ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_585ba:\n.option push\n.option norvc\njal zero,.Lresident_record_root_chain_edge_585ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_58462\n");
    __builtin_unreachable();
}

/* Original0x585BE..0x585C8. */
REGION void tsl9_resident_record_root_chain_block_585be(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 326(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 327(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_585c6:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_585c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_58578\n");
    __builtin_unreachable();
}

/* Original0x59D3E..0x59D98. */
REGION void tsl9_candidate_external_flash_59d3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s1, 952\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 564\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a4, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d3a\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002f)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlhu a5, 8(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nli s4, 800\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a4 = a4 * a5; LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a4, a4, s4\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000008c)) = (uint32_t)a4; LIVE;
    a0 = UINT32_C(0x0000012c); LIVE;
    a0 = a5 * a0; LIVE;
    PORT(".Lresident_record_root_chain_edge_59d94:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59d94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x59D98..0x59DA2. */
REGION void tsl9_resident_record_root_chain_block_59d98(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a0, 132(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59d9e:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59d9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_56326\n");
    __builtin_unreachable();
}

/* Original0x59DA2..0x59DCE. */
REGION void tsl9_resident_record_root_chain_block_59da2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 8(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 58(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c3e\n.option pop\n");
    a3 = UINT32_C(0x000004e2); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 * a4; LIVE;
    PORT(".option push\n.option norvc\nremu a5, a5, s4\n.option pop\n");
    a5 = a5 * a3; LIVE;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 32(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb01e\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 132(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 130(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59dca:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59dca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55d3c\n");
    __builtin_unreachable();
}

/* Original0x59DCE..0x59DD4. */
REGION void tsl9_resident_record_root_chain_block_59dce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59dd0:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59dd0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5605c\n");
    __builtin_unreachable();
}

/* Original0x59DD4..0x59DE4. */
REGION void tsl9_resident_record_root_chain_block_59dd4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c6e\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    a1 = a1 + UINT32_C(0xfffffffe); LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_edge_59de0:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59de0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_55d00\n");
    __builtin_unreachable();
}

/* Original0x59DE4..0x59DEA. */
REGION void tsl9_resident_record_root_chain_block_59de4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59de6:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59de6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57b28\n");
    __builtin_unreachable();
}

/* Original0x59DEA..0x59E00. */
REGION void tsl9_resident_record_root_chain_block_59dea(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 309(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004e4)); LIVE;
    PORT(".option push\n.option norvc\nsw s0, 168(s3)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_record_root_chain_edge_59dfe:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_root_chain_edge_59dfe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59e22\n");
    __builtin_unreachable();
}

/* Original0x59E00..0x59E0E. */
REGION void tsl9_resident_record_root_chain_block_59e00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 492\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 52(s2)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59e0c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_root_chain_edge_59e0c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59e22\n");
    __builtin_unreachable();
}

/* Original0x59E0E..0x59E16. */
REGION void tsl9_resident_record_root_chain_block_59e0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a1, 152(s0)\n.option pop\n");
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59E16..0x59E22. */
REGION void tsl9_resident_record_root_chain_block_59e16(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 52(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 156(s0)\n.option pop\n");
    a0 = UINT32_C(0x0000000e); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59E22..0x59E3E. */
REGION void tsl9_resident_record_root_chain_block_59e22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 14(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 16(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59e3a:\n.option push\n.option norvc\njal zero,.Lresident_record_root_chain_edge_59e3a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_56716\n");
    __builtin_unreachable();
}

/* Original0x59E64..0x59E74. */
REGION void tsl9_candidate_external_flash_59e64(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59e70:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59e70\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57962\n");
    __builtin_unreachable();
}

/* Original0x59E74..0x59E78. */
REGION void tsl9_resident_record_root_chain_block_59e74(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59e76:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_root_chain_edge_59e76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59ee0\n");
    __builtin_unreachable();
}

/* Original0x59E78..0x59E7C. */
REGION void tsl9_resident_record_root_chain_block_59e78(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_59e78:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59e78\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5784a\n");
    __builtin_unreachable();
}

/* Original0x59E7C..0x59E82. */
REGION void tsl9_resident_record_root_chain_block_59e7c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59e7e:\n.option push\n.option norvc\nbeqz a0,.Lresident_record_root_chain_edge_59e7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_5a000\n");
    __builtin_unreachable();
}

/* Original0x59E82..0x59EAE. */
REGION void tsl9_resident_record_root_chain_block_59e82(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa53e\n.option pop\n");
    a5 = UINT32_C(0xffffffb0); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa57c\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s2, 492\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 16(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2b9e\n.option pop\n");
    a4 = UINT32_C(0x00000104); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s2, 492\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_edge_59eaa:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_record_root_chain_edge_59eaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_59eb2\n");
    __builtin_unreachable();
}

/* Original0x59EAE..0x59EB2. */
REGION void tsl9_resident_record_root_chain_block_59eae(void)
{
    REGS;
    a0 = UINT32_C(0x00000104); LIVE;
    __builtin_unreachable();
}

/* Original0x59EB2..0x59EC0. */
REGION void tsl9_resident_record_root_chain_block_59eb2(void)
{
    REGS;
    a4 = a0 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_record_root_chain_edge_59ebc:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_record_root_chain_edge_59ebc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_59ec4\n");
    __builtin_unreachable();
}

/* Original0x59EC0..0x59EC4. */
REGION void tsl9_resident_record_root_chain_block_59ec0(void)
{
    REGS;
    a0 = UINT32_C(0x00000040); LIVE;
    __builtin_unreachable();
}

/* Original0x59EC4..0x59ED4. */
REGION void tsl9_resident_record_root_chain_block_59ec4(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x0000024d); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_record_root_chain_literal_59ecc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_59ecc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59ED4..0x59EDA. */
REGION void tsl9_resident_record_root_chain_block_59ed4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 272(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59ed8:\n.option push\n.option rvc\nc.bnez a0,.Lresident_record_root_chain_edge_59ed8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59ef0\n");
    __builtin_unreachable();
}

/* Original0x59EDA..0x59EE0. */
REGION void tsl9_resident_record_root_chain_block_59eda(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59edc:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59edc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_57a4a\n");
    __builtin_unreachable();
}

/* Original0x59EE0..0x59EF0. */
REGION void tsl9_resident_record_root_chain_block_59ee0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59EF0..0x59F1C. */
REGION void tsl9_resident_record_root_chain_block_59ef0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000538)); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s1, 952\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000000dc)); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 276(s0)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000000d8)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3318\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a3, 252(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 248(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59f1a:\n.option push\n.option rvc\nc.bnez a4,.Lresident_record_root_chain_edge_59f1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59f24\n");
    __builtin_unreachable();
}

/* Original0x59F1C..0x59F24. */
REGION void tsl9_resident_record_root_chain_block_59f1c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffff3f); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 248(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59F24..0x59F6A. */
REGION void tsl9_resident_record_root_chain_block_59f24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 252(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 248(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh zero, 326(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a5, 268(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a5, 58(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x3cbe\n.option pop\n");
    PORT(".option push\n.option norvc\nsw a4, 264(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 46(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 324(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 74(s1)\n.option pop\n");
    a4 = a4 | UINT32_C(0xffffffc1); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 46(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 361(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 208(s1)\n.option pop\n");
    a3 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsw a3, 164(s0)\n.option pop\n");
    a3 = a4 << UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_record_root_chain_edge_59f66:\n.option push\n.option norvc\nbgez a3,.Lresident_record_root_chain_edge_59f66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_record_root_chain_block_59f72\n");
    __builtin_unreachable();
}

/* Original0x59F6A..0x59F72. */
REGION void tsl9_resident_record_root_chain_block_59f6a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000050); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59F72..0x59F78. */
REGION void tsl9_resident_record_root_chain_block_59f72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 82(s1)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59f76:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_root_chain_edge_59f76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59f86\n");
    __builtin_unreachable();
}

/* Original0x59F78..0x59F86. */
REGION void tsl9_resident_record_root_chain_block_59f78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 164(s0)\n.option pop\n");
    a4 = UINT32_C(0x00400000); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsw a5, 164(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59F86..0x59FA2. */
REGION void tsl9_resident_record_root_chain_block_59f86(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 64(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07e\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    a5 = UINT32_C(0x00001000); LIVE;
    a5 = a5 + UINT32_C(0xfffffbb8); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 74(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59f9e:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59f9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_560aa\n");
    __builtin_unreachable();
}

/* Original0x59FA2..0x59FAE. */
REGION void tsl9_resident_record_root_chain_block_59fa2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 20(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 322(s0)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59faa:\n.option push\n.option norvc\njal ra,.Lresident_record_root_chain_edge_59faa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_63966\n");
    __builtin_unreachable();
}

/* Original0x59FAE..0x59FF4. */
REGION void tsl9_resident_record_root_chain_block_59fae(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 391(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000028); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 389(s0)\n.option pop\n");
    a5 = UINT32_C(0x000006f0); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 376(s0)\n.option pop\n");
    a5 = UINT32_C(0x0000007f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 378(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffd000); LIVE;
    a5 = a5 + UINT32_C(0xfffffeba); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 380(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 252(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 323(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 384(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 385(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 386(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 387(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_record_root_chain_edge_59ff2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_record_root_chain_edge_59ff2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_59ffa\n");
    __builtin_unreachable();
}

/* Original0x59FF4..0x59FFA. */
REGION void tsl9_resident_record_root_chain_block_59ff4(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 398(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x59FFA..0x5A000. */
REGION void tsl9_resident_record_root_chain_block_59ffa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh zero, 8(s1)\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_59ffe:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_59ffe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_59ee0\n");
    __builtin_unreachable();
}

/* Original0x5A000..0x5A004. */
REGION void tsl9_resident_record_root_chain_block_5a000(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_5a002:\n.option push\n.option rvc\nc.j .Lresident_record_root_chain_edge_5a002\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_record_root_chain_block_59ee0\n");
    __builtin_unreachable();
}

/* Original0x5E3A8..0x5E3D2. */
REGION void tsl9_candidate_external_flash_5e3a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40024\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option norvc\nlw s1, 524(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_record_root_chain_literal_5e3ca:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_record_root_chain_literal_5e3ca\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5E3D2..0x5E3D4. */
REGION void tsl9_resident_record_root_chain_block_5e3d2(void)
{
    REGS;
    PORT(".Lresident_record_root_chain_edge_5e3d2:\n.option push\n.option rvc\nc.beqz a0,.Lresident_record_root_chain_edge_5e3d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_record_root_chain_block_5e3fc\n");
    __builtin_unreachable();
}

/* Original0x5E3D4..0x5E3FC. */
REGION void tsl9_resident_record_root_chain_block_5e3d4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nsh s2, 2(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a1, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa10c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb110\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s1, 524(s0)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019f)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lresident_record_root_chain_edge_5e3f8:\n.option push\n.option norvc\njal zero,.Lresident_record_root_chain_edge_5e3f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x5E3FC..0x5E40E. */
REGION void tsl9_resident_record_root_chain_block_5e3fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s1, 524(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
