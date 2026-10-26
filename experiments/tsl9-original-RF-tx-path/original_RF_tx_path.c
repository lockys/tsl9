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

/* Eight complete public-SDK RF TX/API/callback/helper bodies:1778B/620i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x64422..0x64436. */
REGION void tsl9_candidate_TX_basic_callback_64422(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x303c\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64434:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_64434\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64454\n");
    __builtin_unreachable();
}

/* Original0x64436..0x6443A. */
REGION void tsl9_original_RF_tx_path_block_64436(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64436:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64436\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x6443A..0x6444C. */
REGION void tsl9_original_RF_tx_path_block_6443a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 1360(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x6444C..0x64454. */
REGION void tsl9_original_RF_tx_path_block_6444c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64454..0x64460. */
REGION void tsl9_original_RF_tx_path_block_64454(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6445e:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_tx_path_edge_6445e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64474\n");
    __builtin_unreachable();
}

/* Original0x64460..0x64464. */
REGION void tsl9_original_RF_tx_path_block_64460(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64460:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64460\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x64464..0x64474. */
REGION void tsl9_original_RF_tx_path_block_64464(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 1360(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64472:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64472\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_6444c\n");
    __builtin_unreachable();
}

/* Original0x64474..0x6447C. */
REGION void tsl9_original_RF_tx_path_block_64474(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x307c\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64478:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_tx_path_edge_64478\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64486\n");
    __builtin_unreachable();
}

/* Original0x6447C..0x64486. */
REGION void tsl9_original_RF_tx_path_block_6447c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x64486..0x6448E. */
REGION void tsl9_original_RF_tx_path_block_64486(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6448E..0x644AA. */
REGION void tsl9_candidate_TX_callback_6448e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s1, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x233c\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_644a8:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_644a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_645a2\n");
    __builtin_unreachable();
}

/* Original0x644AA..0x644CE. */
REGION void tsl9_original_RF_tx_path_block_644aa(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    PORT(".option push\n.option norvc\naddi s1, s1, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 2(s1)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 1344(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 1344\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_644cc:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_644cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64520\n");
    __builtin_unreachable();
}

/* Original0x644CE..0x644DE. */
REGION void tsl9_original_RF_tx_path_block_644ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a2, 4(s0)\n.option pop\n");
    a3 = a0 & UINT32_C(0x00000030); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    a5 = a2 + UINT32_C(0xfffffc18); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_644da:\n.option push\n.option norvc\nbne a3,a1,.Loriginal_RF_tx_path_edge_644da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_644e2\n");
    __builtin_unreachable();
}

/* Original0x644DE..0x644E2. */
REGION void tsl9_original_RF_tx_path_block_644de(void)
{
    REGS;
    a5 = a2 + UINT32_C(0xfffff830); LIVE;
    __builtin_unreachable();
}

/* Original0x644E2..0x64520. */
REGION void tsl9_original_RF_tx_path_block_644e2(void)
{
    REGS;
    a1 = UINT32_C(0x00010000); LIVE;
    a1 = a1 + UINT32_C(0xfffffa00); LIVE;
    PORT(".option push\n.option norvc\ndivu a3, a5, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nlui a6, 0xfe100\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a6, a6, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a1\n.option pop\n");
    a3 = a3 & UINT32_C(0x0000001f); LIVE;
    a2 = a3 << UINT32_C(0x00000014); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    PORT(".option push\n.option norvc\nand a3, a3, a6\n.option pop\n");
    a3 = a3 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x000000fa); LIVE;
    a2 = UINT32_C(0xfffc0000); LIVE;
    a5 = a5 << UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    a3 = a3 & a2; LIVE;
    a5 = a5 << UINT32_C(0x0000000e); LIVE;
    a5 = a5 >> UINT32_C(0x0000000e); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x64520..0x6452C. */
REGION void tsl9_original_RF_tx_path_block_64520(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a1, 28(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2c4c\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64528:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64528\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x6452C..0x6453C. */
REGION void tsl9_original_RF_tx_path_block_6452c(void)
{
    REGS;
    a0 = UINT32_C(0x00064000); LIVE;
    a0 = a0 + UINT32_C(0x000005dc); LIVE;
    PORT(".Loriginal_RF_tx_path_literal_64534:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_64534\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6453C..0x6456C. */
REGION void tsl9_original_RF_tx_path_block_6453c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1340(s2)\n.option pop\n");
    a5 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0xffffff80); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa0d8\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6456a:\n.option push\n.option rvc\nc.bnez a4,.Loriginal_RF_tx_path_edge_6456a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_6458a\n");
    __builtin_unreachable();
}

/* Original0x6456C..0x64570. */
REGION void tsl9_original_RF_tx_path_block_6456c(void)
{
    REGS;
    a4 = UINT32_C(0x00000196); LIVE;
    __builtin_unreachable();
}

/* Original0x64570..0x6457E. */
REGION void tsl9_original_RF_tx_path_block_64570(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw t1, 16(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x6457E..0x6458A. */
REGION void tsl9_original_RF_tx_path_block_6457e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6458A..0x64596. */
REGION void tsl9_original_RF_tx_path_block_6458a(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a4 = a4 >> UINT32_C(0x0000000c); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64592:\n.option push\n.option norvc\nbne a4,a2,.Loriginal_RF_tx_path_edge_64592\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_6459c\n");
    __builtin_unreachable();
}

/* Original0x64596..0x6459C. */
REGION void tsl9_original_RF_tx_path_block_64596(void)
{
    REGS;
    a4 = UINT32_C(0x0000043e); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6459a:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_6459a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64570\n");
    __builtin_unreachable();
}

/* Original0x6459C..0x645A2. */
REGION void tsl9_original_RF_tx_path_block_6459c(void)
{
    REGS;
    a4 = UINT32_C(0x000001be); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_645a0:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_645a0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64570\n");
    __builtin_unreachable();
}

/* Original0x645A2..0x645AA. */
REGION void tsl9_original_RF_tx_path_block_645a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_645a8:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_tx_path_edge_645a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_645be\n");
    __builtin_unreachable();
}

/* Original0x645AA..0x645AE. */
REGION void tsl9_original_RF_tx_path_block_645aa(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_645aa:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_645aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x645AE..0x645BE. */
REGION void tsl9_original_RF_tx_path_block_645ae(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 1360(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_645bc:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_645bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_6457e\n");
    __builtin_unreachable();
}

/* Original0x645BE..0x645C6. */
REGION void tsl9_original_RF_tx_path_block_645be(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x337c\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_645c2:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_tx_path_edge_645c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_645d0\n");
    __builtin_unreachable();
}

/* Original0x645C6..0x645D0. */
REGION void tsl9_original_RF_tx_path_block_645c6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x645D0..0x645DC. */
REGION void tsl9_original_RF_tx_path_block_645d0(void)
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

/* Original0x645DC..0x645F2. */
REGION void tsl9_candidate_TX_ack_callback_645dc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x333c\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_645f0:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_645f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64672\n");
    __builtin_unreachable();
}

/* Original0x645F2..0x645F6. */
REGION void tsl9_original_RF_tx_path_block_645f2(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_645f2:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_645f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x645F6..0x64610. */
REGION void tsl9_original_RF_tx_path_block_645f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 36(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi a2, sp, 15\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_literal_64608:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_64608\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64610..0x64620. */
REGION void tsl9_original_RF_tx_path_block_64610(void)
{
    REGS;
    a1 = a0 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x18\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_6461e:\n.option push\n.option rvc\nc.bnez a1,.Loriginal_RF_tx_path_edge_6461e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64638\n");
    __builtin_unreachable();
}

/* Original0x64620..0x6462C. */
REGION void tsl9_original_RF_tx_path_block_64620(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 36(s0)\n.option pop\n");
    a3 = UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64628:\n.option push\n.option norvc\nbeq a4,a3,.Loriginal_RF_tx_path_edge_64628\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64638\n");
    __builtin_unreachable();
}

/* Original0x6462C..0x64632. */
REGION void tsl9_original_RF_tx_path_block_6462c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 1(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x309c\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_6462e:\n.option push\n.option norvc\nbeq a5,a3,.Loriginal_RF_tx_path_edge_6462e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64638\n");
    __builtin_unreachable();
}

/* Original0x64632..0x64636. */
REGION void tsl9_original_RF_tx_path_block_64632(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64632:\n.option push\n.option norvc\nbeq a4,a5,.Loriginal_RF_tx_path_edge_64632\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64638\n");
    __builtin_unreachable();
}

/* Original0x64636..0x64638. */
REGION void tsl9_original_RF_tx_path_block_64636(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x64638..0x64644. */
REGION void tsl9_original_RF_tx_path_block_64638(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000540)); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64640:\n.option push\n.option norvc\nbltz a4,.Loriginal_RF_tx_path_edge_64640\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_6464a\n");
    __builtin_unreachable();
}

/* Original0x64644..0x6464A. */
REGION void tsl9_original_RF_tx_path_block_64644(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 36(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbusp a3, 15(sp). */
    PORT(".option push\n.option rvc\n.2byte 0x8794\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 0(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa314\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6464A..0x6465A. */
REGION void tsl9_original_RF_tx_path_block_6464a(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000540); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    PORT(".option push\n.option rvc\nlw a2, 36(s0)\n.option pop\n");
    a1 = a1 & UINT32_C(0x000000ff); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6465A..0x64660. */
REGION void tsl9_original_RF_tx_path_block_6465a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 12(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x24dc\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6465e:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_6465e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64668\n");
    __builtin_unreachable();
}

/* Original0x64660..0x64668. */
REGION void tsl9_original_RF_tx_path_block_64660(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s1). */
    PORT(".option push\n.option rvc\n.2byte 0x2888\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64664:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64664\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x64668..0x64672. */
REGION void tsl9_original_RF_tx_path_block_64668(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64672..0x6467E. */
REGION void tsl9_original_RF_tx_path_block_64672(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6467c:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_tx_path_edge_6467c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64694\n");
    __builtin_unreachable();
}

/* Original0x6467E..0x64682. */
REGION void tsl9_original_RF_tx_path_block_6467e(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_6467e:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_6467e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_6440a\n");
    __builtin_unreachable();
}

/* Original0x64682..0x64692. */
REGION void tsl9_original_RF_tx_path_block_64682(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000550)); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64692..0x64694. */
REGION void tsl9_original_RF_tx_path_block_64692(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64692:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64692\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64668\n");
    __builtin_unreachable();
}

/* Original0x64694..0x6469C. */
REGION void tsl9_original_RF_tx_path_block_64694(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x337c\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64698:\n.option push\n.option norvc\nbne a4,a5,.Loriginal_RF_tx_path_edge_64698\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64668\n");
    __builtin_unreachable();
}

/* Original0x6469C..0x646A8. */
REGION void tsl9_original_RF_tx_path_block_6469c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    PORT(".Loriginal_RF_tx_path_edge_646a6:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_646a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64668\n");
    __builtin_unreachable();
}

/* Original0x64CEC..0x64D14. */
REGION void tsl9_candidate_RF_Tx_64cec(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s2, 1344\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 0(sp)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64d10:\n.option push\n.option norvc\nbeqz a5,.Loriginal_RF_tx_path_edge_64d10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64f00\n");
    __builtin_unreachable();
}

/* Original0x64D14..0x64D2C. */
REGION void tsl9_original_RF_tx_path_block_64d14(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nmv s8, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1300\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64d28:\n.option push\n.option norvc\nbeq a4,a5,.Loriginal_RF_tx_path_edge_64d28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64ebc\n");
    __builtin_unreachable();
}

/* Original0x64D2C..0x64D3C. */
REGION void tsl9_original_RF_tx_path_block_64d2c(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s7, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s9, a3\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64d38:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64d38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_registers_63eda\n");
    __builtin_unreachable();
}

/* Original0x64D3C..0x64D4E. */
REGION void tsl9_original_RF_tx_path_block_64d3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s6, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s10, s2, 1344\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s6, 1376\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64d4c:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_64d4c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64d76\n");
    __builtin_unreachable();
}

/* Original0x64D4E..0x64D50. */
REGION void tsl9_original_RF_tx_path_block_64d4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s4, 15\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64D50..0x64D58. */
REGION void tsl9_original_RF_tx_path_block_64d50(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_literal_64d50:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002d4c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_64d50\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64D58..0x64D5C. */
REGION void tsl9_original_RF_tx_path_block_64d58(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64d58:\n.option push\n.option norvc\nbleu a0,s4,.Loriginal_RF_tx_path_edge_64d58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64d50\n");
    __builtin_unreachable();
}

/* Original0x64D5C..0x64D68. */
REGION void tsl9_original_RF_tx_path_block_64d5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 26(s10)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 + UINT32_C(0xfffffff0); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64d64:\n.option push\n.option norvc\nbltu a5,a0,.Loriginal_RF_tx_path_edge_64d64\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64d50\n");
    __builtin_unreachable();
}

/* Original0x64D68..0x64D76. */
REGION void tsl9_original_RF_tx_path_block_64d68(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000053c)); LIVE;
    a4 = UINT32_C(0x000000a0); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x64D76..0x64D90. */
REGION void tsl9_original_RF_tx_path_block_64d76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1288(s5)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 12(s3)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64d8e:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_tx_path_edge_64d8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64d9c\n");
    __builtin_unreachable();
}

/* Original0x64D90..0x64D9C. */
REGION void tsl9_original_RF_tx_path_block_64d90(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64d98:\n.option push\n.option norvc\nbnez a5,.Loriginal_RF_tx_path_edge_64d98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64ed8\n");
    __builtin_unreachable();
}

/* Original0x64D9C..0x64DA2. */
REGION void tsl9_original_RF_tx_path_block_64d9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1(s10)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x64DA2..0x64DA6. */
REGION void tsl9_original_RF_tx_path_block_64da2(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_64da2:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64da2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_6434a\n");
    __builtin_unreachable();
}

/* Original0x64DA6..0x64E14. */
REGION void tsl9_original_RF_tx_path_block_64da6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s5)\n.option pop\n");
    a2 = UINT32_C(0x00330000); LIVE;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffe7f); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000590)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a4, 1340(s4)\n.option pop\n");
    a3 = UINT32_C(0x0000005a); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000050)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 8(s10)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 12(s10)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a3 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 14(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s7, 1376(s6)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s9, 1(s3)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 14(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 32(s0)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64e10:\n.option push\n.option norvc\nbeqz s8,.Loriginal_RF_tx_path_edge_64e10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64ee0\n");
    __builtin_unreachable();
}

/* Original0x64E14..0x64E28. */
REGION void tsl9_original_RF_tx_path_block_64e14(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s7, 0(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s1, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb104\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s8\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_literal_64e20:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_64e20\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64E28..0x64E44. */
REGION void tsl9_original_RF_tx_path_block_64e28(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 32(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1340(s4)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000070)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 2(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 7(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07c\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 12(s3)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64e42:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_64e42\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64e70\n");
    __builtin_unreachable();
}

/* Original0x64E44..0x64E48. */
REGION void tsl9_original_RF_tx_path_block_64e44(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64e46:\n.option push\n.option rvc\nc.bnez a5,.Loriginal_RF_tx_path_edge_64e46\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64e44\n");
    __builtin_unreachable();
}

/* Original0x64E48..0x64E52. */
REGION void tsl9_original_RF_tx_path_block_64e48(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64E52..0x64E5A. */
REGION void tsl9_original_RF_tx_path_block_64e52(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 8(s3)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64e56:\n.option push\n.option norvc\nbltu a0,a4,.Loriginal_RF_tx_path_edge_64e56\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_64ee8\n");
    __builtin_unreachable();
}

/* Original0x64E5A..0x64E5C. */
REGION void tsl9_original_RF_tx_path_block_64e5a(void)
{
    REGS;
    a0 = a0 - a4; LIVE;
    __builtin_unreachable();
}

/* Original0x64E5C..0x64E70. */
REGION void tsl9_original_RF_tx_path_block_64e5c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 32(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s1, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb384\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sb a0, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb388\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64E70..0x64E7E. */
REGION void tsl9_original_RF_tx_path_block_64e70(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64e7a:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_64e7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63b0e\n");
    __builtin_unreachable();
}

/* Original0x64E7E..0x64E86. */
REGION void tsl9_original_RF_tx_path_block_64e7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64e84:\n.option push\n.option rvc\nc.beqz a5,.Loriginal_RF_tx_path_edge_64e84\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_64ef6\n");
    __builtin_unreachable();
}

/* Original0x64E86..0x64E8E. */
REGION void tsl9_original_RF_tx_path_block_64e86(void)
{
    REGS;
    a0 = UINT32_C(0x00064000); LIVE;
    a0 = a0 + UINT32_C(0x0000048e); LIVE;
    __builtin_unreachable();
}

/* Original0x64E8E..0x64E96. */
REGION void tsl9_original_RF_tx_path_block_64e8e(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_literal_64e8e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_64e8e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64E96..0x64EBC. */
REGION void tsl9_original_RF_tx_path_block_64e96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1288(s5)\n.option pop\n");
    a3 = UINT32_C(0x00800000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffc); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x64EBC..0x64ED8. */
REGION void tsl9_original_RF_tx_path_block_64ebc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64ED8..0x64EE0. */
REGION void tsl9_original_RF_tx_path_block_64ed8(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nlw a0, 4(s10)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64ede:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64ede\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64da2\n");
    __builtin_unreachable();
}

/* Original0x64EE0..0x64EE8. */
REGION void tsl9_original_RF_tx_path_block_64ee0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s7, 0(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_64ee6:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64ee6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64e28\n");
    __builtin_unreachable();
}

/* Original0x64EE8..0x64EF6. */
REGION void tsl9_original_RF_tx_path_block_64ee8(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000238)); LIVE;
    a5 = a5 - a4; LIVE;
    a0 = a0 + a5; LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64ef4:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64ef4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64e5c\n");
    __builtin_unreachable();
}

/* Original0x64EF6..0x64F00. */
REGION void tsl9_original_RF_tx_path_block_64ef6(void)
{
    REGS;
    a0 = UINT32_C(0x00064000); LIVE;
    a0 = a0 + UINT32_C(0x00000422); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64efe:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64efe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64e8e\n");
    __builtin_unreachable();
}

/* Original0x64F00..0x64F04. */
REGION void tsl9_original_RF_tx_path_block_64f00(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_64f02:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_64f02\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_64ebc\n");
    __builtin_unreachable();
}

/* Original0x656C6..0x656F2. */
REGION void tsl9_candidate_RF_Shut_656c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1376\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000e)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 1376\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_656f0:\n.option push\n.option rvc\nc.beqz a0,.Loriginal_RF_tx_path_edge_656f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_656fa\n");
    __builtin_unreachable();
}

/* Original0x656F2..0x656FA. */
REGION void tsl9_original_RF_tx_path_block_656f2(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_literal_656f2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_release_20000110\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loriginal_RF_tx_path_literal_656f2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x656FA..0x6570E. */
REGION void tsl9_original_RF_tx_path_block_656fa(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 9(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3718\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 4(s0)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6570c:\n.option push\n.option rvc\nc.beqz a4,.Loriginal_RF_tx_path_edge_6570c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_6571a\n");
    __builtin_unreachable();
}

/* Original0x6570E..0x65716. */
REGION void tsl9_original_RF_tx_path_block_6570e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2794\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65712:\n.option push\n.option norvc\nbne a3,a4,.Loriginal_RF_tx_path_edge_65712\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_6571a\n");
    __builtin_unreachable();
}

/* Original0x65716..0x6571A. */
REGION void tsl9_original_RF_tx_path_block_65716(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000009)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x6571A..0x65722. */
REGION void tsl9_original_RF_tx_path_block_6571a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000006); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6571e:\n.option push\n.option norvc\nbeq a3,a4,.Loriginal_RF_tx_path_edge_6571e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_6572a\n");
    __builtin_unreachable();
}

/* Original0x65722..0x6572A. */
REGION void tsl9_original_RF_tx_path_block_65722(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65726:\n.option push\n.option norvc\nbne a3,a4,.Loriginal_RF_tx_path_edge_65726\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_65732\n");
    __builtin_unreachable();
}

/* Original0x6572A..0x65732. */
REGION void tsl9_original_RF_tx_path_block_6572a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa798\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb798\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65732..0x65736. */
REGION void tsl9_original_RF_tx_path_block_65732(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_65732:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_65732\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x65736..0x65746. */
REGION void tsl9_original_RF_tx_path_block_65736(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2808\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)0; LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65742:\n.option push\n.option norvc\njal ra,.Loriginal_RF_tx_path_edge_65742\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_stop_task_439a8\n");
    __builtin_unreachable();
}

/* Original0x65746..0x6575A. */
REGION void tsl9_original_RF_tx_path_block_65746(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s1, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65F94..0x65FA8. */
REGION void tsl9_candidate_RF_SetChannel_65f94(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = a5 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 12(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x26d8\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000560); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65fa6:\n.option push\n.option rvc\nc.bnez a4,.Loriginal_RF_tx_path_edge_65fa6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_66054\n");
    __builtin_unreachable();
}

/* Original0x65FA8..0x65FB8. */
REGION void tsl9_original_RF_tx_path_block_65fa8(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 12(a3). */
    PORT(".option push\n.option rvc\n.2byte 0x26d4\n.option pop\n");
    a2 = UINT32_C(0x20003000); LIVE;
    a4 = a2 + UINT32_C(0x00000540); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65fb6:\n.option push\n.option rvc\nc.bnez a3,.Loriginal_RF_tx_path_edge_65fb6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_66046\n");
    __builtin_unreachable();
}

/* Original0x65FB8..0x65FC2. */
REGION void tsl9_original_RF_tx_path_block_65fb8(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000540)); LIVE;
    a3 = a3 & UINT32_C(0x00000040); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65fc0:\n.option push\n.option rvc\nc.beqz a3,.Loriginal_RF_tx_path_edge_65fc0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_66046\n");
    __builtin_unreachable();
}

/* Original0x65FC2..0x65FD0. */
REGION void tsl9_original_RF_tx_path_block_65fc2(void)
{
    REGS;
    a5 = UINT32_C(0x0024b000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint32_t)a0; LIVE;
    a5 = a5 + UINT32_C(0xfffffe9f); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65fcc:\n.option push\n.option norvc\nbltu a5,a0,.Loriginal_RF_tx_path_edge_65fcc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_65fee\n");
    __builtin_unreachable();
}

/* Original0x65FD0..0x65FD4. */
REGION void tsl9_original_RF_tx_path_block_65fd0(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    __builtin_unreachable();
}

/* Original0x65FD4..0x65FE8. */
REGION void tsl9_original_RF_tx_path_block_65fd4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb31c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65fe4:\n.option push\n.option norvc\nbeq a4,a5,.Loriginal_RF_tx_path_edge_65fe4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_65fea\n");
    __builtin_unreachable();
}

/* Original0x65FE8..0x65FEA. */
REGION void tsl9_original_RF_tx_path_block_65fe8(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x65FEA..0x65FEE. */
REGION void tsl9_original_RF_tx_path_block_65fea(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_65fea:\n.option push\n.option norvc\njal zero,.Loriginal_RF_tx_path_edge_65fea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_6434a\n");
    __builtin_unreachable();
}

/* Original0x65FEE..0x65FFA. */
REGION void tsl9_original_RF_tx_path_block_65fee(void)
{
    REGS;
    a5 = UINT32_C(0x00250000); LIVE;
    a3 = a5 + UINT32_C(0x0000048f); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_65ff6:\n.option push\n.option norvc\nbltu a3,a0,.Loriginal_RF_tx_path_edge_65ff6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_66010\n");
    __builtin_unreachable();
}

/* Original0x65FFA..0x66010. */
REGION void tsl9_original_RF_tx_path_block_65ffa(void)
{
    REGS;
    a5 = UINT32_C(0xffdb6000); LIVE;
    a5 = a5 + UINT32_C(0xfffff930); LIVE;
    a5 = a5 + a0; LIVE;
    a3 = UINT32_C(0x000007d0); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6600e:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_6600e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_65fd4\n");
    __builtin_unreachable();
}

/* Original0x66010..0x66018. */
REGION void tsl9_original_RF_tx_path_block_66010(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000490); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_66014:\n.option push\n.option norvc\nbne a0,a5,.Loriginal_RF_tx_path_edge_66014\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_6601e\n");
    __builtin_unreachable();
}

/* Original0x66018..0x6601E. */
REGION void tsl9_original_RF_tx_path_block_66018(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6601c:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_6601c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_65fd4\n");
    __builtin_unreachable();
}

/* Original0x6601E..0x6602A. */
REGION void tsl9_original_RF_tx_path_block_6601e(void)
{
    REGS;
    a5 = UINT32_C(0x0025d000); LIVE;
    a5 = a5 + UINT32_C(0x0000077f); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_66026:\n.option push\n.option norvc\nbltu a5,a0,.Loriginal_RF_tx_path_edge_66026\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_66040\n");
    __builtin_unreachable();
}

/* Original0x6602A..0x66040. */
REGION void tsl9_original_RF_tx_path_block_6602a(void)
{
    REGS;
    a5 = UINT32_C(0xffdb6000); LIVE;
    a5 = a5 + UINT32_C(0xfffff930); LIVE;
    a5 = a5 + a0; LIVE;
    a3 = UINT32_C(0x000007d0); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a3\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_6603e:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_6603e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_65fd4\n");
    __builtin_unreachable();
}

/* Original0x66040..0x66046. */
REGION void tsl9_original_RF_tx_path_block_66040(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_66044:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_66044\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_65fd4\n");
    __builtin_unreachable();
}

/* Original0x66046..0x66054. */
REGION void tsl9_original_RF_tx_path_block_66046(void)
{
    REGS;
    a3 = a0 & UINT32_C(0x000000ff); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb314\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 15(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7f4\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a3\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_66052:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_66052\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_65fea\n");
    __builtin_unreachable();
}

/* Original0x66054..0x66056. */
REGION void tsl9_original_RF_tx_path_block_66054(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002C50..0x20002C76. */
REGION void tsl9_candidate_external_ram_20002c50(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    a2 = a3 + UINT32_C(0x00000540); LIVE;
    a4 = a4 + UINT32_C(0x00000560); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 13(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x375c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 27(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3e2c\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000014)); LIVE;
    a5 = a5 + a1; LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    PORT(".option push\n.option norvc\nsrl a1, a0, a5\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0xb21c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 13(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb75c\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_20002c74:\n.option push\n.option rvc\nc.bnez a1,.Loriginal_RF_tx_path_edge_20002c74\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_20002ca6\n");
    __builtin_unreachable();
}

/* Original0x20002C76..0x20002C84. */
REGION void tsl9_original_RF_tx_path_block_20002c76(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 17(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x3b18\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nli a6, 32\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x20002C84..0x20002C90. */
REGION void tsl9_original_RF_tx_path_block_20002c84(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsrl a1, a0, a4\n.option pop\n");
    a1 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nandi a7, a4, 255\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002c8e:\n.option push\n.option rvc\nc.beqz a1,.Loriginal_RF_tx_path_edge_20002c8e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_original_RF_tx_path_block_20002ca0\n");
    __builtin_unreachable();
}

/* Original0x20002C90..0x20002C94. */
REGION void tsl9_original_RF_tx_path_block_20002c90(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_20002c90:\n.option push\n.option norvc\nbne a5,a3,.Loriginal_RF_tx_path_edge_20002c90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002c9a\n");
    __builtin_unreachable();
}

/* Original0x20002C94..0x20002C9A. */
REGION void tsl9_original_RF_tx_path_block_20002c94(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a7, 1(a2)\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002C9A..0x20002CA0. */
REGION void tsl9_original_RF_tx_path_block_20002c9a(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x20002CA0..0x20002CA6. */
REGION void tsl9_original_RF_tx_path_block_20002ca0(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Loriginal_RF_tx_path_edge_20002ca2:\n.option push\n.option norvc\nbne a4,a6,.Loriginal_RF_tx_path_edge_20002ca2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002c84\n");
    __builtin_unreachable();
}

/* Original0x20002CA6..0x20002CA8. */
REGION void tsl9_original_RF_tx_path_block_20002ca6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002D4C..0x20002D64. */
REGION void tsl9_candidate_external_ram_20002d4c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002D64..0x20002D74. */
REGION void tsl9_original_RF_tx_path_block_20002d64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s1, 1376\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s4, 0\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002d70:\n.option push\n.option norvc\nbeq s0,a0,.Loriginal_RF_tx_path_edge_20002d70\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002dd0\n");
    __builtin_unreachable();
}

/* Original0x20002D74..0x20002D7C. */
REGION void tsl9_original_RF_tx_path_block_20002d74(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, s1, 1376\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002d78:\n.option push\n.option norvc\nbltu a0,s0,.Loriginal_RF_tx_path_edge_20002d78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002de2\n");
    __builtin_unreachable();
}

/* Original0x20002D7C..0x20002D7E. */
REGION void tsl9_original_RF_tx_path_block_20002d7c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsub a0, a0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002D7E..0x20002D98. */
REGION void tsl9_original_RF_tx_path_block_20002d7e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = a4 + UINT32_C(0x00000540); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 26(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2fbc\n.option pop\n");
    PORT(".option push\n.option norvc\nsrli s0, a0, 0x5\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s4, a0, 31\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, a4, 1344\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002d94:\n.option push\n.option norvc\nbltu s0,a5,.Loriginal_RF_tx_path_edge_20002d94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002dca\n");
    __builtin_unreachable();
}

/* Original0x20002D98..0x20002DA0. */
REGION void tsl9_original_RF_tx_path_block_20002d98(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 564\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002DA0..0x20002DA2. */
REGION void tsl9_original_RF_tx_path_block_20002da0(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_20002da0:\n.option push\n.option rvc\nc.jal .Loriginal_RF_tx_path_edge_20002da0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_external_ram_20002c50\n");
    __builtin_unreachable();
}

/* Original0x20002DA2..0x20002DBC. */
REGION void tsl9_original_RF_tx_path_block_20002da2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 26(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a6, 8(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 4(s3)\n.option pop\n");
    a4 = a3 << UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nadd a4, a4, a6\n.option pop\n");
    PORT(".option push\n.option rvc\nsub s0, s0, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a4\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002db8:\n.option push\n.option norvc\nbltu a4,a6,.Loriginal_RF_tx_path_edge_20002db8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002dc0\n");
    __builtin_unreachable();
}

/* Original0x20002DBC..0x20002DC0. */
REGION void tsl9_original_RF_tx_path_block_20002dbc(void)
{
    REGS;
    PORT(".Loriginal_RF_tx_path_edge_20002dbc:\n.option push\n.option norvc\nbltu a4,a1,.Loriginal_RF_tx_path_edge_20002dbc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002dc4\n");
    __builtin_unreachable();
}

/* Original0x20002DC0..0x20002DC4. */
REGION void tsl9_original_RF_tx_path_block_20002dc0(void)
{
    REGS;
    a2 = a4 - a1; LIVE;
    __builtin_unreachable();
}

/* Original0x20002DC4..0x20002DCA. */
REGION void tsl9_original_RF_tx_path_block_20002dc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a2, 8(s1)\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002dc6:\n.option push\n.option norvc\nbleu a3,s0,.Loriginal_RF_tx_path_edge_20002dc6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_original_RF_tx_path_block_20002da0\n");
    __builtin_unreachable();
}

/* Original0x20002DCA..0x20002DD0. */
REGION void tsl9_original_RF_tx_path_block_20002dca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nslli s0, s0, 0x5\n.option pop\n");
    PORT(".option push\n.option norvc\nor s4, s0, s4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002DD0..0x20002DE2. */
REGION void tsl9_original_RF_tx_path_block_20002dd0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20002DE2..0x20002DF2. */
REGION void tsl9_original_RF_tx_path_block_20002de2(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000238)); LIVE;
    PORT(".option push\n.option norvc\nsub s0, a5, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".Loriginal_RF_tx_path_edge_20002df0:\n.option push\n.option rvc\nc.j .Loriginal_RF_tx_path_edge_20002df0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_original_RF_tx_path_block_20002d7e\n");
    __builtin_unreachable();
}
