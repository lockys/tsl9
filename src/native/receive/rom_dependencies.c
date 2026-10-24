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

/* Seven complete original dependency functions:422B/153i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x81DE..0x81EE. */
REGION void tsl9_rom_dependency_entry_81de(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9792..0x9798. */
REGION void tsl9_rom_driver_external_9792(void)
{
    REGS;
    a5 = UINT32_C(0x000000fa); LIVE;
    PORT(".Lrom_dependency_edge_9796:\n.option push\n.option rvc\nc.bnez a0,.Lrom_dependency_edge_9796\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_979a\n");
    __builtin_unreachable();
}

/* Original0x9798..0x979A. */
REGION void tsl9_rom_dependency_block_9798(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x979A..0x979E. */
REGION void tsl9_rom_dependency_block_979a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lrom_dependency_edge_979c:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_979c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x9F74..0x9F7A. */
REGION void tsl9_rom_dependency_entry_9f74(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000af)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9FC2..0x9FC8. */
REGION void tsl9_rom_driver_external_9fc2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ac)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA204..0xA20E. */
REGION void tsl9_rom_dependency_entry_a204(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ac)); LIVE;
    PORT(".Lrom_dependency_edge_a20c:\n.option push\n.option rvc\nc.beqz a5,.Lrom_dependency_edge_a20c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a228\n");
    __builtin_unreachable();
}

/* Original0xA20E..0xA212. */
REGION void tsl9_rom_dependency_block_a20e(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a20e:\n.option push\n.option norvc\nbeqz a0,.Lrom_dependency_edge_a20e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA212..0xA216. */
REGION void tsl9_rom_dependency_block_a212(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a212:\n.option push\n.option norvc\njal ra,.Lrom_dependency_edge_a212\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xA216..0xA21A. */
REGION void tsl9_rom_dependency_block_a216(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a216:\n.option push\n.option norvc\nbeqz a0,.Lrom_dependency_edge_a216\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA21A..0xA228. */
REGION void tsl9_rom_dependency_block_a21a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_dependency_edge_a224:\n.option push\n.option norvc\njal zero,.Lrom_dependency_edge_a224\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_d05c\n");
    __builtin_unreachable();
}

/* Original0xA228..0xA22E. */
REGION void tsl9_rom_dependency_block_a228(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b3)); LIVE;
    PORT(".Lrom_dependency_edge_a22c:\n.option push\n.option rvc\nc.beqz a0,.Lrom_dependency_edge_a22c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2a8\n");
    __builtin_unreachable();
}

/* Original0xA22E..0xA230. */
REGION void tsl9_rom_dependency_block_a22e(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a22e:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a22e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA230..0xA246. */
REGION void tsl9_rom_dependency_block_a230(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b3)) = (uint8_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    PORT(".Lrom_dependency_edge_a242:\n.option push\n.option norvc\nbeq a5,a3,.Lrom_dependency_edge_a242\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a286\n");
    __builtin_unreachable();
}

/* Original0xA246..0xA24A. */
REGION void tsl9_rom_dependency_block_a246(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a246:\n.option push\n.option norvc\nbltu a3,a5,.Lrom_dependency_edge_a246\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a294\n");
    __builtin_unreachable();
}

/* Original0xA24A..0xA250. */
REGION void tsl9_rom_dependency_block_a24a(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_dependency_edge_a24c:\n.option push\n.option norvc\nbeq a5,a3,.Lrom_dependency_edge_a24c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a28e\n");
    __builtin_unreachable();
}

/* Original0xA250..0xA254. */
REGION void tsl9_rom_dependency_block_a250(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b4)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xA254..0xA260. */
REGION void tsl9_rom_dependency_block_a254(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000009)); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrom_dependency_edge_a25c:\n.option push\n.option norvc\nbeq a5,a4,.Lrom_dependency_edge_a25c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a26e\n");
    __builtin_unreachable();
}

/* Original0xA260..0xA264. */
REGION void tsl9_rom_dependency_block_a260(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a260:\n.option push\n.option norvc\nbltu a4,a5,.Lrom_dependency_edge_a260\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a298\n");
    __builtin_unreachable();
}

/* Original0xA264..0xA26A. */
REGION void tsl9_rom_dependency_block_a264(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_dependency_edge_a266:\n.option push\n.option norvc\nbeq a5,a4,.Lrom_dependency_edge_a266\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a2be\n");
    __builtin_unreachable();
}

/* Original0xA26A..0xA26E. */
REGION void tsl9_rom_dependency_block_a26a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xA26E..0xA274. */
REGION void tsl9_rom_dependency_block_a26e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b4)); LIVE;
    PORT(".Lrom_dependency_edge_a272:\n.option push\n.option rvc\nc.bnez a4,.Lrom_dependency_edge_a272\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2d2\n");
    __builtin_unreachable();
}

/* Original0xA274..0xA27A. */
REGION void tsl9_rom_dependency_block_a274(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ae)); LIVE;
    PORT(".Lrom_dependency_edge_a278:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a278\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA27A..0xA282. */
REGION void tsl9_rom_dependency_block_a27a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrom_dependency_edge_a280:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a280\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2ca\n");
    __builtin_unreachable();
}

/* Original0xA282..0xA286. */
REGION void tsl9_rom_dependency_block_a282(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_dependency_edge_a284:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a284\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a2ca\n");
    __builtin_unreachable();
}

/* Original0xA286..0xA28E. */
REGION void tsl9_rom_dependency_block_a286(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b4)); LIVE;
    PORT(".option push\n.option norvc\nseqz a5, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA28E..0xA294. */
REGION void tsl9_rom_dependency_block_a28e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b4)) = (uint8_t)a5; LIVE;
    PORT(".Lrom_dependency_edge_a292:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a292\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a254\n");
    __builtin_unreachable();
}

/* Original0xA294..0xA298. */
REGION void tsl9_rom_dependency_block_a294(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrom_dependency_edge_a296:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a296\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a28e\n");
    __builtin_unreachable();
}

/* Original0xA298..0xA2A0. */
REGION void tsl9_rom_dependency_block_a298(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000038)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA2A0..0xA2A8. */
REGION void tsl9_rom_dependency_block_a2a0(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)) = (uint8_t)a0; LIVE;
    PORT(".Lrom_dependency_edge_a2a6:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a2a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a26e\n");
    __builtin_unreachable();
}

/* Original0xA2A8..0xA2AA. */
REGION void tsl9_rom_dependency_block_a2a8(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a2a8:\n.option push\n.option rvc\nc.beqz a5,.Lrom_dependency_edge_a2a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA2AA..0xA2B6. */
REGION void tsl9_rom_dependency_block_a2aa(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b3)) = (uint8_t)a5; LIVE;
    PORT(".Lrom_dependency_edge_a2b4:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a2b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2e4\n");
    __builtin_unreachable();
}

/* Original0xA2B6..0xA2BE. */
REGION void tsl9_rom_dependency_block_a2b6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)); LIVE;
    PORT(".option push\n.option norvc\nseqz a5, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA2BE..0xA2C4. */
REGION void tsl9_rom_dependency_block_a2be(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)) = (uint8_t)a5; LIVE;
    PORT(".Lrom_dependency_edge_a2c2:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a2c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a26e\n");
    __builtin_unreachable();
}

/* Original0xA2C4..0xA2C8. */
REGION void tsl9_rom_dependency_block_a2c4(void)
{
    REGS;
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lrom_dependency_edge_a2c6:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a2c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2ca\n");
    __builtin_unreachable();
}

/* Original0xA2C8..0xA2CA. */
REGION void tsl9_rom_dependency_block_a2c8(void)
{
    REGS;
    a0 = UINT32_C(0x0000000c); LIVE;
    __builtin_unreachable();
}

/* Original0xA2CA..0xA2D2. */
REGION void tsl9_rom_dependency_block_a2ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_dependency_edge_a2ce:\n.option push\n.option norvc\njal zero,.Lrom_dependency_edge_a2ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_b6ea\n");
    __builtin_unreachable();
}

/* Original0xA2D2..0xA2DC. */
REGION void tsl9_rom_dependency_block_a2d2(void)
{
    REGS;
    a3 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b2)); LIVE;
    PORT(".Lrom_dependency_edge_a2d8:\n.option push\n.option norvc\nbeq a4,a3,.Lrom_dependency_edge_a2d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a2c4\n");
    __builtin_unreachable();
}

/* Original0xA2DC..0xA2E0. */
REGION void tsl9_rom_dependency_block_a2dc(void)
{
    REGS;
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lrom_dependency_edge_a2de:\n.option push\n.option rvc\nc.bnez a5,.Lrom_dependency_edge_a2de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a2ca\n");
    __builtin_unreachable();
}

/* Original0xA2E0..0xA2E4. */
REGION void tsl9_rom_dependency_block_a2e0(void)
{
    REGS;
    a0 = UINT32_C(0x00000009); LIVE;
    PORT(".Lrom_dependency_edge_a2e2:\n.option push\n.option rvc\nc.j .Lrom_dependency_edge_a2e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_block_a2ca\n");
    __builtin_unreachable();
}

/* Original0xA2E4..0xA2EA. */
REGION void tsl9_rom_dependency_block_a2e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA2EE..0xA2FC. */
REGION void tsl9_rom_driver_external_a2ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrom_dependency_edge_a2f8:\n.option push\n.option norvc\njal ra,.Lrom_dependency_edge_a2f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_mode_getter_829e\n");
    __builtin_unreachable();
}

/* Original0xA2FC..0xA302. */
REGION void tsl9_rom_dependency_block_a2fc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrom_dependency_edge_a2fe:\n.option push\n.option norvc\nbne a0,a5,.Lrom_dependency_edge_a2fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a364\n");
    __builtin_unreachable();
}

/* Original0xA302..0xA306. */
REGION void tsl9_rom_dependency_block_a302(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a302:\n.option push\n.option norvc\njal ra,.Lrom_dependency_edge_a302\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_entry_81de\n");
    __builtin_unreachable();
}

/* Original0xA306..0xA30E. */
REGION void tsl9_rom_dependency_block_a306(void)
{
    REGS;
    a5 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lrom_dependency_edge_a30c:\n.option push\n.option rvc\nc.beqz a5,.Lrom_dependency_edge_a30c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a312\n");
    __builtin_unreachable();
}

/* Original0xA30E..0xA312. */
REGION void tsl9_rom_dependency_block_a30e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrom_dependency_edge_a310:\n.option push\n.option rvc\nc.jal .Lrom_dependency_edge_a310\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_entry_a204\n");
    __builtin_unreachable();
}

/* Original0xA312..0xA316. */
REGION void tsl9_rom_dependency_block_a312(void)
{
    REGS;
    PORT(".option push\n.option rvc\nandi s1, s1, 2\n.option pop\n");
    PORT(".Lrom_dependency_edge_a314:\n.option push\n.option rvc\nc.beqz s1,.Lrom_dependency_edge_a314\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a372\n");
    __builtin_unreachable();
}

/* Original0xA316..0xA31C. */
REGION void tsl9_rom_dependency_block_a316(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrom_dependency_edge_a318:\n.option push\n.option norvc\njal ra,.Lrom_dependency_edge_a318\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_dispatch_external_821e\n");
    __builtin_unreachable();
}

/* Original0xA31C..0xA31E. */
REGION void tsl9_rom_dependency_block_a31c(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a31c:\n.option push\n.option rvc\nc.beqz a0,.Lrom_dependency_edge_a31c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a372\n");
    __builtin_unreachable();
}

/* Original0xA31E..0xA320. */
REGION void tsl9_rom_dependency_block_a31e(void)
{
    REGS;
    PORT(".Lrom_dependency_edge_a31e:\n.option push\n.option rvc\nc.beqz s0,.Lrom_dependency_edge_a31e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_rom_dependency_block_a372\n");
    __builtin_unreachable();
}

/* Original0xA320..0xA332. */
REGION void tsl9_rom_dependency_block_a320(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x0000000f); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lrom_dependency_edge_a32e:\n.option push\n.option norvc\nbeq a5,a4,.Lrom_dependency_edge_a32e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_rom_dependency_block_a372\n");
    __builtin_unreachable();
}

/* Original0xA332..0xA364. */
REGION void tsl9_rom_dependency_block_a332(void)
{
    REGS;
    a2 = UINT32_C(0x000003e8); LIVE;
    PORT(".option push\n.option norvc\nmul a2, s0, a2\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b0)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b0)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000af)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrom_dependency_literal_a356:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_rom_dependency_entry_9f74\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrom_dependency_literal_a356\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_dependency_edge_a360:\n.option push\n.option norvc\njal zero,.Lrom_dependency_edge_a360\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA364..0xA372. */
REGION void tsl9_rom_dependency_block_a364(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrom_dependency_edge_a36e:\n.option push\n.option norvc\njal zero,.Lrom_dependency_edge_a36e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_10816\n");
    __builtin_unreachable();
}

/* Original0xA372..0xA37C. */
REGION void tsl9_rom_dependency_block_a372(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xABF2..0xABFC. */
REGION void tsl9_rom_driver_external_abf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000002ee)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
