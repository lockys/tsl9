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

/* Two complete conditional SDK controller queue bodies:284B/101i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x57862..0x57880. */
REGION void tsl9_candidate_controller_pool_57862(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001fb)); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000240)); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000464)); LIVE;
    a4 = a3 + UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_controller_send_queue_edge_5787e:\n.option push\n.option rvc\nc.beqz a2,.Lresident_controller_send_queue_edge_5787e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_send_queue_block_57884\n");
    __builtin_unreachable();
}

/* Original0x57880..0x57884. */
REGION void tsl9_resident_controller_send_queue_block_57880(void)
{
    REGS;
    a4 = a3 << UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x57884..0x5788C. */
REGION void tsl9_resident_controller_send_queue_block_57884(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000004); LIVE;
    a3 = UINT32_C(0x00010000); LIVE;
    a4 = a4 + a5; LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x5788C..0x57890. */
REGION void tsl9_resident_controller_send_queue_block_5788c(void)
{
    REGS;
    PORT(".Lresident_controller_send_queue_edge_5788c:\n.option push\n.option norvc\nbne a4,a5,.Lresident_controller_send_queue_edge_5788c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_send_queue_block_57896\n");
    __builtin_unreachable();
}

/* Original0x57890..0x57892. */
REGION void tsl9_resident_controller_send_queue_block_57890(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x57892..0x57896. */
REGION void tsl9_resident_controller_send_queue_block_57892(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x57896..0x5789C. */
REGION void tsl9_resident_controller_send_queue_block_57896(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27b2\n.option pop\n");
    PORT(".Lresident_controller_send_queue_edge_57898:\n.option push\n.option norvc\nbeq a2,a0,.Lresident_controller_send_queue_edge_57898\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_send_queue_block_57892\n");
    __builtin_unreachable();
}

/* Original0x5789C..0x578A0. */
REGION void tsl9_resident_controller_send_queue_block_5789c(void)
{
    REGS;
    PORT(".Lresident_controller_send_queue_edge_5789c:\n.option push\n.option norvc\nbeq a2,a3,.Lresident_controller_send_queue_edge_5789c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_send_queue_block_57892\n");
    __builtin_unreachable();
}

/* Original0x578A0..0x578A4. */
REGION void tsl9_resident_controller_send_queue_block_578a0(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_controller_send_queue_edge_578a2:\n.option push\n.option rvc\nc.j .Lresident_controller_send_queue_edge_578a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_send_queue_block_5788c\n");
    __builtin_unreachable();
}

/* Original0x6A626..0x6A63E. */
REGION void tsl9_candidate_unprovided_flash_6a626(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".Lresident_controller_send_queue_edge_6a63a:\n.option push\n.option norvc\njal ra,.Lresident_controller_send_queue_edge_6a63a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5784a\n");
    __builtin_unreachable();
}

/* Original0x6A63E..0x6A640. */
REGION void tsl9_resident_controller_send_queue_block_6a63e(void)
{
    REGS;
    PORT(".Lresident_controller_send_queue_edge_6a63e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_controller_send_queue_edge_6a63e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_send_queue_block_6a6fc\n");
    __builtin_unreachable();
}

/* Original0x6A640..0x6A64C. */
REGION void tsl9_resident_controller_send_queue_block_6a640(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0xffffffa8); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a648:\n.option push\n.option norvc\nbnez s4,.Lresident_controller_send_queue_edge_6a648\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_send_queue_block_6a662\n");
    __builtin_unreachable();
}

/* Original0x6A64C..0x6A650. */
REGION void tsl9_resident_controller_send_queue_block_6a64c(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa398\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6A650..0x6A652. */
REGION void tsl9_resident_controller_send_queue_block_6a650(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x6A652..0x6A662. */
REGION void tsl9_resident_controller_send_queue_block_6a652(void)
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

/* Original0x6A662..0x6A66C. */
REGION void tsl9_resident_controller_send_queue_block_6a662(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2394\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lresident_controller_send_queue_edge_6a668:\n.option push\n.option norvc\nbne a3,a4,.Lresident_controller_send_queue_edge_6a668\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_controller_send_queue_block_6a672\n");
    __builtin_unreachable();
}

/* Original0x6A66C..0x6A672. */
REGION void tsl9_resident_controller_send_queue_block_6a66c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nli s3, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6A672..0x6A68C. */
REGION void tsl9_resident_controller_send_queue_block_6a672(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nlw s2, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a0 = UINT32_C(0x00010000); LIVE;
    a0 = a0 + UINT32_C(0xffffff54); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a688:\n.option push\n.option norvc\njal ra,.Lresident_controller_send_queue_edge_6a688\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_controller_pool_57862\n");
    __builtin_unreachable();
}

/* Original0x6A68C..0x6A68E. */
REGION void tsl9_resident_controller_send_queue_block_6a68c(void)
{
    REGS;
    PORT(".Lresident_controller_send_queue_edge_6a68c:\n.option push\n.option rvc\nc.beqz a0,.Lresident_controller_send_queue_edge_6a68c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_send_queue_block_6a6dc\n");
    __builtin_unreachable();
}

/* Original0x6A68E..0x6A698. */
REGION void tsl9_resident_controller_send_queue_block_6a68e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x253c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sh a5, 10(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa53e\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 280(s0)\n.option pop\n");
    PORT(".Lresident_controller_send_queue_edge_6a696:\n.option push\n.option rvc\nc.bnez a5,.Lresident_controller_send_queue_edge_6a696\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_send_queue_block_6a6d4\n");
    __builtin_unreachable();
}

/* Original0x6A698..0x6A69C. */
REGION void tsl9_resident_controller_send_queue_block_6a698(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 280(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6A69C..0x6A6CA. */
REGION void tsl9_resident_controller_send_queue_block_6a69c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 284(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffff81); LIVE;
    PORT(".option push\n.option rvc\naddi s1, s1, -2\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nsh s4, 12(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb51c\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s3, 8(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsll a1, a1, a5\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a6c6:\n.option push\n.option norvc\njal ra,.Lresident_controller_send_queue_edge_6a6c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x6A6CA..0x6A6D4. */
REGION void tsl9_resident_controller_send_queue_block_6a6ca(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    PORT(".Lresident_controller_send_queue_edge_6a6d2:\n.option push\n.option rvc\nc.j .Lresident_controller_send_queue_edge_6a6d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_send_queue_block_6a650\n");
    __builtin_unreachable();
}

/* Original0x6A6D4..0x6A6DC. */
REGION void tsl9_resident_controller_send_queue_block_6a6d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 284(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a6da:\n.option push\n.option rvc\nc.j .Lresident_controller_send_queue_edge_6a6da\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_send_queue_block_6a69c\n");
    __builtin_unreachable();
}

/* Original0x6A6DC..0x6A6E6. */
REGION void tsl9_resident_controller_send_queue_block_6a6dc(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a6e4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_controller_send_queue_edge_6a6e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_controller_send_queue_block_6a6f0\n");
    __builtin_unreachable();
}

/* Original0x6A6E6..0x6A6F0. */
REGION void tsl9_resident_controller_send_queue_block_6a6e6(void)
{
    REGS;
    a1 = UINT32_C(0x00005000); LIVE;
    a1 = a1 + UINT32_C(0x00000555); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6A6F0..0x6A6FC. */
REGION void tsl9_resident_controller_send_queue_block_6a6f0(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a6fa:\n.option push\n.option rvc\nc.j .Lresident_controller_send_queue_edge_6a6fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_send_queue_block_6a652\n");
    __builtin_unreachable();
}

/* Original0x6A6FC..0x6A700. */
REGION void tsl9_resident_controller_send_queue_block_6a6fc(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_controller_send_queue_edge_6a6fe:\n.option push\n.option rvc\nc.j .Lresident_controller_send_queue_edge_6a6fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_controller_send_queue_block_6a652\n");
    __builtin_unreachable();
}
