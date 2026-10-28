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

/* Three complete conditional callback/counter bodies:258B/86i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x55C32..0x55C34. */
REGION void tsl9_candidate_controller_callback_55c32(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_55c32:\n.option push\n.option rvc\nc.beqz a0,.Lresident_controller_callback_targets_edge_55c32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_callback_targets_block_55c46\n");
    __builtin_unreachable();
}

/* Original0x55C34..0x55C46. */
REGION void tsl9_resident_controller_callback_targets_block_55c34(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000026)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x55C46..0x55C48. */
REGION void tsl9_resident_controller_callback_targets_block_55c46(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x561B8..0x561D2. */
REGION void tsl9_candidate_unprovided_flash_561b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 952\n.option pop\n");
    PORT(".Lresident_controller_callback_targets_edge_561ce:\n.option push\n.option norvc\njal ra,.Lresident_controller_callback_targets_edge_561ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_43e6a\n");
    __builtin_unreachable();
}

/* Original0x561D2..0x561E0. */
REGION void tsl9_resident_controller_callback_targets_block_561d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 180(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a0, 86(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_controller_callback_targets_edge_561dc:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_controller_callback_targets_edge_561dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_callback_targets_block_56236\n");
    __builtin_unreachable();
}

/* Original0x561E0..0x5620C. */
REGION void tsl9_resident_controller_callback_targets_block_561e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a0, 486(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 482(s0)\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x000f4000); LIVE;
    a5 = a5 + a0; LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000023c)); LIVE;
    a5 = a5 + UINT32_C(0x00000271); LIVE;
    a2 = a2 + UINT32_C(0x00000240); LIVE;
    PORT(".option push\n.option norvc\nmulhsu a1, a5, a0\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 * a5; LIVE;
    PORT(".Lresident_controller_callback_targets_edge_56208:\n.option push\n.option norvc\njal ra,.Lresident_controller_callback_targets_edge_56208\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x5620C..0x56232. */
REGION void tsl9_resident_controller_callback_targets_block_5620c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 64(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a4, 94(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a1, 88(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a7, 156(s1)\n.option pop\n");
    a4 = a4 - a5; LIVE;
    a4 = a4 * a1; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 144(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\naddi t1, a1, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nli t3, 40\n.option pop\n");
    a4 = a4 + a5; LIVE;
    __builtin_unreachable();
}

/* Original0x56232..0x56236. */
REGION void tsl9_resident_controller_callback_targets_block_56232(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_56232:\n.option push\n.option norvc\nbltu a2,t1,.Lresident_controller_callback_targets_edge_56232\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_callback_targets_block_56240\n");
    __builtin_unreachable();
}

/* Original0x56236..0x56240. */
REGION void tsl9_resident_controller_callback_targets_block_56236(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56240..0x5624A. */
REGION void tsl9_resident_controller_callback_targets_block_56240(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a6, a2, t3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a7\n.option pop\n");
    a3 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nadd a6, a6, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5624A..0x5624C. */
REGION void tsl9_resident_controller_callback_targets_block_5624a(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_5624a:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_callback_targets_edge_5624a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_callback_targets_block_56252\n");
    __builtin_unreachable();
}

/* Original0x5624C..0x56252. */
REGION void tsl9_resident_controller_callback_targets_block_5624c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh a2, 86(s0)\n.option pop\n");
    PORT(".Lresident_controller_callback_targets_edge_56250:\n.option push\n.option rvc\nc.j .Lresident_controller_callback_targets_edge_56250\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_callback_targets_block_56236\n");
    __builtin_unreachable();
}

/* Original0x56252..0x56256. */
REGION void tsl9_resident_controller_callback_targets_block_56252(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_56252:\n.option push\n.option norvc\nbne s0,a5,.Lresident_controller_callback_targets_edge_56252\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_callback_targets_block_5625a\n");
    __builtin_unreachable();
}

/* Original0x56256..0x5625A. */
REGION void tsl9_resident_controller_callback_targets_block_56256(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    PORT(".Lresident_controller_callback_targets_edge_56258:\n.option push\n.option rvc\nc.beqz a5,.Lresident_controller_callback_targets_edge_56258\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_callback_targets_block_5624c\n");
    __builtin_unreachable();
}

/* Original0x5625A..0x56262. */
REGION void tsl9_resident_controller_callback_targets_block_5625a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw t4, 140(a5)\n.option pop\n");
    PORT(".Lresident_controller_callback_targets_edge_5625e:\n.option push\n.option norvc\nbne t4,a1,.Lresident_controller_callback_targets_edge_5625e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_callback_targets_block_5626e\n");
    __builtin_unreachable();
}

/* Original0x56262..0x5626E. */
REGION void tsl9_resident_controller_callback_targets_block_56262(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000090)); LIVE;
    PORT(".option push\n.option norvc\nsub a3, a6, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a3, a3, a1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5626E..0x56272. */
REGION void tsl9_resident_controller_callback_targets_block_5626e(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_5626e:\n.option push\n.option norvc\nbltu a3,a0,.Lresident_controller_callback_targets_edge_5626e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_callback_targets_block_56276\n");
    __builtin_unreachable();
}

/* Original0x56272..0x56276. */
REGION void tsl9_resident_controller_callback_targets_block_56272(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_controller_callback_targets_edge_56274:\n.option push\n.option rvc\nc.j .Lresident_controller_callback_targets_edge_56274\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_callback_targets_block_5624a\n");
    __builtin_unreachable();
}

/* Original0x56276..0x5627A. */
REGION void tsl9_resident_controller_callback_targets_block_56276(void)
{
    REGS;
    a2 = a2 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_controller_callback_targets_edge_56278:\n.option push\n.option rvc\nc.j .Lresident_controller_callback_targets_edge_56278\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_callback_targets_block_56232\n");
    __builtin_unreachable();
}

/* Original0x56CB2..0x56CB4. */
REGION void tsl9_candidate_controller_callback_56cb2(void)
{
    REGS;
    PORT(".Lresident_controller_callback_targets_edge_56cb2:\n.option push\n.option rvc\nc.beqz a0,.Lresident_controller_callback_targets_edge_56cb2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_callback_targets_block_56cda\n");
    __builtin_unreachable();
}

/* Original0x56CB4..0x56CC4. */
REGION void tsl9_resident_controller_callback_targets_block_56cb4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x00000022); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_controller_callback_targets_edge_56cc0:\n.option push\n.option norvc\njal ra,.Lresident_controller_callback_targets_edge_56cc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x56CC4..0x56CDA. */
REGION void tsl9_resident_controller_callback_targets_block_56cc4(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 16(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 39(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56CDA..0x56CDC. */
REGION void tsl9_resident_controller_callback_targets_block_56cda(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
