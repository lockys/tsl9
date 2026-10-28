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

/* Four complete conditional SDK capacity/task-state bodies:598B/198i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4DA70..0x4DAD2. */
REGION void tsl9_candidate_external_flash_4da70(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa2)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff9c)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000031c)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa5)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\naddi s3, s3, -93\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nsb zero, -96(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, -95(s1)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xffffff9e)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option norvc\nsw zero, -104(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 0(s3)\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4dace:\n.option push\n.option norvc\njal ra,.Lresident_CCC_capacity_initialization_edge_4dace\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4edd2\n");
    __builtin_unreachable();
}

/* Original0x4DAD2..0x4DAF2. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dad2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000030); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000314)) = (uint8_t)a0; LIVE;
    a0 = UINT32_C(0x20003000); LIVE;
    a0 = a0 + UINT32_C(0x00000320); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_literal_4daea:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4daea\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DAF2..0x4DB08. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4daf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 848(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -96\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, -95\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -104\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4db06:\n.option push\n.option rvc\nc.beqz a0,.Lresident_CCC_capacity_initialization_edge_4db06\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4db3e\n");
    __builtin_unreachable();
}

/* Original0x4DB08..0x4DB18. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db08(void)
{
    REGS;
    a1 = UINT32_C(0x00005000); LIVE;
    a1 = a1 + UINT32_C(0xfffffc04); LIVE;
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_literal_4db10:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4db10\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DB18..0x4DB22. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db18(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000310)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_CCC_capacity_initialization_edge_4db20:\n.option push\n.option rvc\nc.beqz a0,.Lresident_CCC_capacity_initialization_edge_4db20\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4db3e\n");
    __builtin_unreachable();
}

/* Original0x4DB22..0x4DB3E. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db22(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 848(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s4, 848\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x339c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a2, 0(s3)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = a2 << UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa09c\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_literal_4db36:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4db36\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DB3E..0x4DB60. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db3e(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b4)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 0(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x209c\n.option pop\n");
    a1 = UINT32_C(0x00005000); LIVE;
    a1 = a1 + UINT32_C(0xfffffc05); LIVE;
    a0 = a0 + a5; LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa008\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_literal_4db58:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4db58\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DB60..0x4DB66. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db60(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 0(s2)\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4db64:\n.option push\n.option rvc\nc.beqz a0,.Lresident_CCC_capacity_initialization_edge_4db64\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4dbe8\n");
    __builtin_unreachable();
}

/* Original0x4DB66..0x4DB74. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db66(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2010\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = a2 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_literal_4db6c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4db6c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DB74..0x4DB80. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db74(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 0(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2014\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    a4 = a4 + UINT32_C(0x00000009); LIVE;
    a2 = UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x4DB80..0x4DB84. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db80(void)
{
    REGS;
    PORT(".Lresident_CCC_capacity_initialization_edge_4db80:\n.option push\n.option norvc\nbne a3,a5,.Lresident_CCC_capacity_initialization_edge_4db80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4dbdc\n");
    __builtin_unreachable();
}

/* Original0x4DB84..0x4DB88. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db84(void)
{
    REGS;
    PORT(".Lresident_CCC_capacity_initialization_edge_4db84:\n.option push\n.option norvc\njal ra,.Lresident_CCC_capacity_initialization_edge_4db84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4efd8\n");
    __builtin_unreachable();
}

/* Original0x4DB88..0x4DBA0. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4db88(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    a0 = a0 * a5; LIVE;
    a1 = UINT32_C(0x00005000); LIVE;
    a1 = a1 + UINT32_C(0xfffffc06); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_literal_4db98:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4db98\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DBA0..0x4DBAC. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dba0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000318)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4dbaa:\n.option push\n.option rvc\nc.beqz a0,.Lresident_CCC_capacity_initialization_edge_4dbaa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4dbc2\n");
    __builtin_unreachable();
}

/* Original0x4DBAC..0x4DBB0. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dbac(void)
{
    REGS;
    PORT(".Lresident_CCC_capacity_initialization_edge_4dbac:\n.option push\n.option norvc\njal ra,.Lresident_CCC_capacity_initialization_edge_4dbac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4efd8\n");
    __builtin_unreachable();
}

/* Original0x4DBB0..0x4DBC2. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dbb0(void)
{
    REGS;
    a2 = UINT32_C(0x0000000c); LIVE;
    a2 = a0 * a2; LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_literal_4dbba:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4dbba\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4DBC2..0x4DBDC. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dbc2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    a0 = UINT32_C(0x0004e000); LIVE;
    a0 = a0 + UINT32_C(0xfffff916); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4dbd8:\n.option push\n.option norvc\njal zero,.Lresident_CCC_capacity_initialization_edge_4dbd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_4efe2\n");
    __builtin_unreachable();
}

/* Original0x4DBDC..0x4DBE8. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dbdc(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa310\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 + UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_edge_4dbe6:\n.option push\n.option rvc\nc.j .Lresident_CCC_capacity_initialization_edge_4dbe6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_CCC_capacity_initialization_block_4db80\n");
    __builtin_unreachable();
}

/* Original0x4DBE8..0x4DBF2. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4dbe8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 0(s1)\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4dbf0:\n.option push\n.option rvc\nc.j .Lresident_CCC_capacity_initialization_edge_4dbf0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_CCC_capacity_initialization_block_4db84\n");
    __builtin_unreachable();
}

/* Original0x4EDD2..0x4EDF8. */
REGION void tsl9_candidate_external_flash_4edd2(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000201)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    a5 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 940\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb41c\n.option pop\n");
    a5 = a5 + a0; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa41c\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_edge_4edf6:\n.option push\n.option rvc\nc.beqz a5,.Lresident_CCC_capacity_initialization_edge_4edf6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4ee68\n");
    __builtin_unreachable();
}

/* Original0x4EDF8..0x4EE10. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4edf8(void)
{
    REGS;
    a0 = UINT32_C(0x0000003c); LIVE;
    a0 = a5 * a0; LIVE;
    a1 = UINT32_C(0x00009000); LIVE;
    a1 = a1 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_literal_4ee08:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4ee08\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EE10..0x4EE28. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee10(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a2, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2410\n.option pop\n");
    a5 = UINT32_C(0x0000003c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = a2 * a5; LIVE;
    PORT(".option push\n.option norvc\nsw a0, 852(s1)\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_literal_4ee20:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4ee20\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EE28..0x4EE34. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee28(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 852(s1)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2414\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a2 = UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x4EE34..0x4EE38. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee34(void)
{
    REGS;
    PORT(".Lresident_CCC_capacity_initialization_edge_4ee34:\n.option push\n.option norvc\nblt a4,a3,.Lresident_CCC_capacity_initialization_edge_4ee34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4ee56\n");
    __builtin_unreachable();
}

/* Original0x4EE38..0x4EE56. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a0 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x00000030); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0x00000358); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lresident_CCC_capacity_initialization_literal_4ee4e:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_CCC_capacity_initialization_literal_4ee4e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EE56..0x4EE68. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee56(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sh a2, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa392\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002a)) = (uint32_t)0; LIVE;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0x0000003c); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_edge_4ee66:\n.option push\n.option rvc\nc.j .Lresident_CCC_capacity_initialization_edge_4ee66\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_CCC_capacity_initialization_block_4ee34\n");
    __builtin_unreachable();
}

/* Original0x4EE68..0x4EE72. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4ee68(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EFD8..0x4EFE2. */
REGION void tsl9_candidate_external_flash_4efd8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003b4)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4EFE2..0x4EFF2. */
REGION void tsl9_candidate_external_flash_4efe2(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = a4 + UINT32_C(0x00000358); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    a4 = a4 + UINT32_C(0x00000358); LIVE;
    a2 = UINT32_C(0x0000000c); LIVE;
    __builtin_unreachable();
}

/* Original0x4EFF2..0x4EFF6. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4eff2(void)
{
    REGS;
    a1 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_edge_4eff4:\n.option push\n.option rvc\nc.bnez a1,.Lresident_CCC_capacity_initialization_edge_4eff4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4f000\n");
    __builtin_unreachable();
}

/* Original0x4EFF6..0x4F000. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4eff6(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4F000..0x4F008. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4f000(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a3 = a3 + UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_CCC_capacity_initialization_edge_4f004:\n.option push\n.option norvc\nbne a5,a2,.Lresident_CCC_capacity_initialization_edge_4f004\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_CCC_capacity_initialization_block_4eff2\n");
    __builtin_unreachable();
}

/* Original0x4F008..0x4F00C. */
REGION void tsl9_resident_CCC_capacity_initialization_block_4f008(void)
{
    REGS;
    a0 = UINT32_C(0x00000013); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
