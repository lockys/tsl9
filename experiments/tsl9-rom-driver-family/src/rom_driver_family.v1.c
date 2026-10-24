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

/* Six complete original171BA..173EE functions:564B/208i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x171BA..0x171CC. */
REGION void tsl9_callback_flow_external_171ba(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000060)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x171CC..0x171DE. */
REGION void tsl9_rom_driver_block_171cc(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    a0 = a0 * a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 + UINT32_C(0x00000032); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x171DE..0x171EA. */
REGION void tsl9_rom_driver_entry_171de(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".Lrom_driver_edge_171e6:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_171e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0x171EA..0x171EC. */
REGION void tsl9_rom_driver_block_171ea(void)
{
    REGS;
    PORT(".Lrom_driver_edge_171ea:\n.option push\n.option rvc\nc.beqz a0,.Lrom_driver_edge_171ea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17280\n");
    __builtin_unreachable();
}

/* Original0x171EC..0x171FE. */
REGION void tsl9_rom_driver_block_171ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, gp, 84\n.option pop\n");
    register uintptr_t original_s1 __asm__("s1");
    __asm__ volatile("":"=r"(original_s1)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s1 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x0000000f); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lrom_driver_edge_171fa:\n.option push\n.option norvc\nbeq a5,a4,.Lrom_driver_edge_171fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_1726a\n");
    __builtin_unreachable();
}

/* Original0x171FE..0x1720C. */
REGION void tsl9_rom_driver_block_171fe(void)
{
    REGS;
    register uintptr_t original_s1 __asm__("s1");
    __asm__ volatile("":"=r"(original_s1)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s1 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlbu s0, 3(a5)\n.option pop\n");
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option rvc\nandi s0, s0, 15\n.option pop\n");
    PORT(".Lrom_driver_edge_17208:\n.option push\n.option norvc\nbne s0,a5,.Lrom_driver_edge_17208\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_1720e\n");
    __builtin_unreachable();
}

/* Original0x1720C..0x1720E. */
REGION void tsl9_rom_driver_block_1720c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1720E..0x17216. */
REGION void tsl9_rom_driver_block_1720e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000038)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17216..0x1721C. */
REGION void tsl9_rom_driver_block_17216(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_driver_edge_17218:\n.option push\n.option norvc\nbltu a5,s0,.Lrom_driver_edge_17218\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_1728a\n");
    __builtin_unreachable();
}

/* Original0x1721C..0x17228. */
REGION void tsl9_rom_driver_block_1721c(void)
{
    REGS;
    a5 = UINT32_C(0x000003e9); LIVE;
    PORT(".option push\n.option norvc\nremu a0, a0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nli s0, 2000\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17228..0x17232. */
REGION void tsl9_rom_driver_block_17228(void)
{
    REGS;
    register uintptr_t original_s1 __asm__("s1");
    __asm__ volatile("":"=r"(original_s1)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s1 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_driver_edge_17230:\n.option push\n.option rvc\nc.beqz a5,.Lrom_driver_edge_17230\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17234\n");
    __builtin_unreachable();
}

/* Original0x17232..0x17234. */
REGION void tsl9_rom_driver_block_17232(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s0, s0, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17234..0x17252. */
REGION void tsl9_rom_driver_block_17234(void)
{
    REGS;
    a2 = UINT32_C(0x000003e8); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    register uintptr_t original_s1 __asm__("s1");
    __asm__ volatile("":"=r"(original_s1)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s1 + UINT32_C(0x00000058)); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)); LIVE;
    PORT(".option push\n.option norvc\nmul s0, s0, a2\n.option pop\n");
    a2 = UINT32_C(0x00000271); LIVE;
    PORT(".option push\n.option norvc\ndivu a2, s0, a2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17252..0x1726A. */
REGION void tsl9_rom_driver_block_17252(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)); LIVE;
    a2 = UINT32_C(0x00000050); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1726A..0x1726E. */
REGION void tsl9_rom_driver_block_1726a(void)
{
    REGS;
    PORT(".Lrom_driver_edge_1726a:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_1726a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_abf2\n");
    __builtin_unreachable();
}

/* Original0x1726E..0x17270. */
REGION void tsl9_rom_driver_block_1726e(void)
{
    REGS;
    PORT(".Lrom_driver_edge_1726e:\n.option push\n.option rvc\nc.beqz a0,.Lrom_driver_edge_1726e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_171fe\n");
    __builtin_unreachable();
}

/* Original0x17270..0x1727A. */
REGION void tsl9_rom_driver_block_17270(void)
{
    REGS;
    register uintptr_t original_s1 __asm__("s1");
    __asm__ volatile("":"=r"(original_s1)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s1 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lrom_driver_edge_17278:\n.option push\n.option rvc\nc.beqz a5,.Lrom_driver_edge_17278\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17280\n");
    __builtin_unreachable();
}

/* Original0x1727A..0x1727E. */
REGION void tsl9_rom_driver_block_1727a(void)
{
    REGS;
    PORT(".Lrom_driver_edge_1727a:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_1727a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9fc2\n");
    __builtin_unreachable();
}

/* Original0x1727E..0x17280. */
REGION void tsl9_rom_driver_block_1727e(void)
{
    REGS;
    PORT(".Lrom_driver_edge_1727e:\n.option push\n.option rvc\nc.bnez a0,.Lrom_driver_edge_1727e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_171fe\n");
    __builtin_unreachable();
}

/* Original0x17280..0x1728A. */
REGION void tsl9_rom_driver_block_17280(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1728A..0x17290. */
REGION void tsl9_rom_driver_block_1728a(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrom_driver_edge_1728c:\n.option push\n.option norvc\nbne s0,a5,.Lrom_driver_edge_1728c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_172a0\n");
    __builtin_unreachable();
}

/* Original0x17290..0x172A0. */
REGION void tsl9_rom_driver_block_17290(void)
{
    REGS;
    a5 = UINT32_C(0x000007d1); LIVE;
    PORT(".option push\n.option rvc\nlui s0, 0x1\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a0, a0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -1096\n.option pop\n");
    PORT(".Lrom_driver_edge_1729e:\n.option push\n.option rvc\nc.j,.Lrom_driver_edge_1729e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_driver_block_17228\n");
    __builtin_unreachable();
}

/* Original0x172A0..0x172B6. */
REGION void tsl9_rom_driver_block_172a0(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a2 = a5 + UINT32_C(0x00000388); LIVE;
    PORT(".option push\n.option rvc\naddi s0, s0, -2\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000389); LIVE;
    PORT(".option push\n.option norvc\nmul s0, s0, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a0, a0, a5\n.option pop\n");
    PORT(".Lrom_driver_edge_172b4:\n.option push\n.option rvc\nc.j,.Lrom_driver_edge_172b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_driver_block_17228\n");
    __builtin_unreachable();
}

/* Original0x172B6..0x172C6. */
REGION void tsl9_rom_driver_entry_172b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lrom_driver_edge_172c4:\n.option push\n.option rvc\nc.beqz a5,.Lrom_driver_edge_172c4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_1730e\n");
    __builtin_unreachable();
}

/* Original0x172C6..0x172CA. */
REGION void tsl9_rom_driver_block_172c6(void)
{
    REGS;
    PORT(".Lrom_driver_edge_172c6:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_172c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0x172CA..0x172E2. */
REGION void tsl9_rom_driver_block_172ca(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nlbu s0, 8(a5)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\nandi s0, s0, 15\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lrom_driver_edge_172de:\n.option push\n.option norvc\nbne a5,a4,.Lrom_driver_edge_172de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_172fa\n");
    __builtin_unreachable();
}

/* Original0x172E2..0x172E6. */
REGION void tsl9_rom_driver_block_172e2(void)
{
    REGS;
    PORT(".Lrom_driver_edge_172e2:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_172e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_mode_getter_829e\n");
    __builtin_unreachable();
}

/* Original0x172E6..0x172EC. */
REGION void tsl9_rom_driver_block_172e6(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_driver_edge_172e8:\n.option push\n.option norvc\nbne a0,a5,.Lrom_driver_edge_172e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_172fa\n");
    __builtin_unreachable();
}

/* Original0x172EC..0x172F4. */
REGION void tsl9_rom_driver_block_172ec(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    PORT(".Lrom_driver_edge_172f0:\n.option push\n.option norvc\nbleu s0,a4,.Lrom_driver_edge_172f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_driver_block_172f6\n");
    __builtin_unreachable();
}

/* Original0x172F4..0x172F6. */
REGION void tsl9_rom_driver_block_172f4(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x172F6..0x172FA. */
REGION void tsl9_rom_driver_block_172f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s0, a5, 255\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x172FA..0x17300. */
REGION void tsl9_rom_driver_block_172fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrom_driver_edge_172fc:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_172fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_a2ee\n");
    __builtin_unreachable();
}

/* Original0x17300..0x17304. */
REGION void tsl9_rom_driver_block_17300(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17304..0x1730E. */
REGION void tsl9_rom_driver_block_17304(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1730E..0x17316. */
REGION void tsl9_rom_driver_block_1730e(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrom_driver_edge_17314:\n.option push\n.option rvc\nc.beqz a5,.Lrom_driver_edge_17314\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17304\n");
    __builtin_unreachable();
}

/* Original0x17316..0x1731A. */
REGION void tsl9_rom_driver_block_17316(void)
{
    REGS;
    PORT(".Lrom_driver_edge_17316:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_17316\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0x1731A..0x17320. */
REGION void tsl9_rom_driver_block_1731a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s1, 2\n.option pop\n");
    PORT(".Lrom_driver_edge_1731e:\n.option push\n.option rvc\nc.j,.Lrom_driver_edge_1731e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_driver_block_17304\n");
    __builtin_unreachable();
}

/* Original0x17320..0x17328. */
REGION void tsl9_rom_driver_entry_17320(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrom_driver_edge_17324:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_17324\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0x17328..0x1732A. */
REGION void tsl9_rom_driver_block_17328(void)
{
    REGS;
    PORT(".Lrom_driver_edge_17328:\n.option push\n.option rvc\nc.beqz a0,.Lrom_driver_edge_17328\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_1733e\n");
    __builtin_unreachable();
}

/* Original0x1732A..0x1733E. */
REGION void tsl9_rom_driver_block_1732a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 80(a5)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1733E..0x17344. */
REGION void tsl9_rom_driver_block_1733e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17344..0x17352. */
REGION void tsl9_rom_driver_entry_17344(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lrom_driver_edge_17350:\n.option push\n.option rvc\nc.bnez a0,.Lrom_driver_edge_17350\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17392\n");
    __builtin_unreachable();
}

/* Original0x17352..0x1735A. */
REGION void tsl9_rom_driver_block_17352(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 364(gp)\n.option pop\n");
    PORT(".Lrom_driver_edge_17356:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_17356\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0x1735A..0x1735C. */
REGION void tsl9_rom_driver_block_1735a(void)
{
    REGS;
    PORT(".Lrom_driver_edge_1735a:\n.option push\n.option rvc\nc.beqz s1,.Lrom_driver_edge_1735a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17362\n");
    __builtin_unreachable();
}

/* Original0x1735C..0x17362. */
REGION void tsl9_rom_driver_block_1735c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrom_driver_edge_1735e:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_1735e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0x17362..0x17364. */
REGION void tsl9_rom_driver_block_17362(void)
{
    REGS;
    PORT(".Lrom_driver_edge_17362:\n.option push\n.option rvc\nc.bnez s0,.Lrom_driver_edge_17362\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17398\n");
    __builtin_unreachable();
}

/* Original0x17364..0x17372. */
REGION void tsl9_rom_driver_block_17364(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000005c)); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17372..0x17384. */
REGION void tsl9_rom_driver_block_17372(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrom_driver_literal_17378:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_provider_entry_13d48\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrom_driver_literal_17378\n.option pop\n");
    PORT(".Lrom_driver_edge_17380:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_17380\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x17384..0x17392. */
REGION void tsl9_rom_driver_block_17384(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_driver_edge_1738e:\n.option push\n.option norvc\njal zero,.Lrom_driver_edge_1738e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_1061c\n");
    __builtin_unreachable();
}

/* Original0x17392..0x17396. */
REGION void tsl9_rom_driver_block_17392(void)
{
    REGS;
    PORT(".Lrom_driver_edge_17392:\n.option push\n.option norvc\njal ra,.Lrom_driver_edge_17392\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_status_81aa\n");
    __builtin_unreachable();
}

/* Original0x17396..0x17398. */
REGION void tsl9_rom_driver_block_17396(void)
{
    REGS;
    PORT(".Lrom_driver_edge_17396:\n.option push\n.option rvc\nc.bnez a0,.Lrom_driver_edge_17396\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_17352\n");
    __builtin_unreachable();
}

/* Original0x17398..0x173A2. */
REGION void tsl9_rom_driver_block_17398(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x173A2..0x173B8. */
REGION void tsl9_main_provider_173a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    register uintptr_t original_s0 __asm__("s0");
    __asm__ volatile("":"=r"(original_s0)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s0 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x0000016c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x173B8..0x173C6. */
REGION void tsl9_rom_driver_block_173b8(void)
{
    REGS;
    register uintptr_t original_s0 __asm__("s0");
    __asm__ volatile("":"=r"(original_s0)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_s0 + UINT32_C(0x00000080)); LIVE;
    PORT(".Lrom_driver_literal_173bc:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_rom_driver_entry_172b6\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrom_driver_literal_173bc\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x173C6..0x173D8. */
REGION void tsl9_rom_driver_block_173c6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016d)) = (uint8_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_driver_edge_173d6:\n.option push\n.option rvc\nc.beqz a5,.Lrom_driver_edge_173d6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_driver_block_173e6\n");
    __builtin_unreachable();
}

/* Original0x173D8..0x173E6. */
REGION void tsl9_rom_driver_block_173d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_driver_edge_173e2:\n.option push\n.option norvc\njal zero,.Lrom_driver_edge_173e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0x173E6..0x173EE. */
REGION void tsl9_rom_driver_block_173e6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
