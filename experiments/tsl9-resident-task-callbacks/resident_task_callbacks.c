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

/* Two public-SDK registered task callbacks:260B/104i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x432A4..0x432A6. */
REGION void tsl9_candidate_registered_callback_432a4(void)
{
    REGS;
    PORT(".Lresident_task_callbacks_edge_432a4:\n.option push\n.option rvc\nc.beqz a1,.Lresident_task_callbacks_edge_432a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_43322\n");
    __builtin_unreachable();
}

/* Original0x432A6..0x432B6. */
REGION void tsl9_resident_task_callbacks_block_432a6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    a4 = UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x432B6..0x432BE. */
REGION void tsl9_resident_task_callbacks_block_432b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsra a5, a1, s0\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_callbacks_edge_432bc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_callbacks_edge_432bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_43318\n");
    __builtin_unreachable();
}

/* Original0x432BE..0x432E4. */
REGION void tsl9_resident_task_callbacks_block_432be(void)
{
    REGS;
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    a4 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    a0 = a0 * a4; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s2, 556(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsll s1, s1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 0(s2)\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_432e2:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_callbacks_edge_432e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_432ee\n");
    __builtin_unreachable();
}

/* Original0x432E4..0x432EC. */
REGION void tsl9_resident_task_callbacks_block_432e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 4(s2)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x432EC..0x432EE. */
REGION void tsl9_resident_task_callbacks_block_432ec(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __builtin_unreachable();
}

/* Original0x432EE..0x432FE. */
REGION void tsl9_resident_task_callbacks_block_432ee(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul s0, s0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 556(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_432fc:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_callbacks_edge_432fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_43306\n");
    __builtin_unreachable();
}

/* Original0x432FE..0x43306. */
REGION void tsl9_resident_task_callbacks_block_432fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 4(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43306..0x43318. */
REGION void tsl9_resident_task_callbacks_block_43306(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nxor a1, a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43318..0x4331E. */
REGION void tsl9_resident_task_callbacks_block_43318(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_4331a:\n.option push\n.option norvc\nbne s0,a4,.Lresident_task_callbacks_edge_4331a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_callbacks_block_432b6\n");
    __builtin_unreachable();
}

/* Original0x4331E..0x43322. */
REGION void tsl9_resident_task_callbacks_block_4331e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_43320:\n.option push\n.option rvc\nc.j .Lresident_task_callbacks_edge_43320\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_callbacks_block_43306\n");
    __builtin_unreachable();
}

/* Original0x43322..0x43326. */
REGION void tsl9_resident_task_callbacks_block_43322(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43326..0x4333C. */
REGION void tsl9_candidate_registered_callback_43326(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a4 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_43338:\n.option push\n.option norvc\nbgez a4,.Lresident_task_callbacks_edge_43338\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_callbacks_block_4335a\n");
    __builtin_unreachable();
}

/* Original0x4333C..0x43344. */
REGION void tsl9_resident_task_callbacks_block_4333c(void)
{
    REGS;
    PORT(".Lresident_task_callbacks_literal_4333c:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_receive_2000028c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_callbacks_literal_4333c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43344..0x43346. */
REGION void tsl9_resident_task_callbacks_block_43344(void)
{
    REGS;
    PORT(".Lresident_task_callbacks_edge_43344:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_callbacks_edge_43344\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_43348\n");
    __builtin_unreachable();
}

/* Original0x43346..0x43348. */
REGION void tsl9_resident_task_callbacks_block_43346(void)
{
    REGS;
    PORT(".Lresident_task_callbacks_edge_43346:\n.option push\n.option rvc\nc.jal .Lresident_task_callbacks_edge_43346\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_message_deallocate_431ba\n");
    __builtin_unreachable();
}

/* Original0x43348..0x4334C. */
REGION void tsl9_resident_task_callbacks_block_43348(void)
{
    REGS;
    a5 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nxor s0, s0, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4334C..0x4335A. */
REGION void tsl9_resident_task_callbacks_block_4334c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4335A..0x4335C. */
REGION void tsl9_resident_task_callbacks_block_4335a(void)
{
    REGS;
    PORT(".Lresident_task_callbacks_edge_4335a:\n.option push\n.option rvc\nc.beqz a1,.Lresident_task_callbacks_edge_4335a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_4334c\n");
    __builtin_unreachable();
}

/* Original0x4335C..0x43362. */
REGION void tsl9_resident_task_callbacks_block_4335c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x43362..0x4336A. */
REGION void tsl9_resident_task_callbacks_block_43362(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsra a3, s0, a4\n.option pop\n");
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_callbacks_edge_43368:\n.option push\n.option rvc\nc.beqz a3,.Lresident_task_callbacks_edge_43368\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_callbacks_block_4339e\n");
    __builtin_unreachable();
}

/* Original0x4336A..0x43392. */
REGION void tsl9_resident_task_callbacks_block_4336a(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    a5 = a5 + a4; LIVE;
    a3 = UINT32_C(0x0000000c); LIVE;
    a5 = a5 * a3; LIVE;
    a3 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s2, 556(a3)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsll s1, s1, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s2, s2, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 4(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43392..0x4339A. */
REGION void tsl9_resident_task_callbacks_block_43392(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 4(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4339A..0x4339E. */
REGION void tsl9_resident_task_callbacks_block_4339a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nxor s0, s0, s1\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_4339c:\n.option push\n.option rvc\nc.j .Lresident_task_callbacks_edge_4339c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_callbacks_block_4334c\n");
    __builtin_unreachable();
}

/* Original0x4339E..0x433A4. */
REGION void tsl9_resident_task_callbacks_block_4339e(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_callbacks_edge_433a0:\n.option push\n.option norvc\nbne a4,a2,.Lresident_task_callbacks_edge_433a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_callbacks_block_43362\n");
    __builtin_unreachable();
}

/* Original0x433A4..0x433A8. */
REGION void tsl9_resident_task_callbacks_block_433a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lresident_task_callbacks_edge_433a6:\n.option push\n.option rvc\nc.j .Lresident_task_callbacks_edge_433a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_callbacks_block_4339a\n");
    __builtin_unreachable();
}
