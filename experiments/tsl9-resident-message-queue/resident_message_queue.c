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

/* Six public-SDK message queue/event bodies:436B/151i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x4319C..0x431A6. */
REGION void tsl9_candidate_message_unlink_4319c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0xfffffff8)); LIVE;
    PORT(".Lresident_message_queue_edge_431a2:\n.option push\n.option norvc\nbne a4,a1,.Lresident_message_queue_edge_431a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_431b4\n");
    __builtin_unreachable();
}

/* Original0x431A6..0x431A8. */
REGION void tsl9_resident_message_queue_block_431a6(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x431A8..0x431B4. */
REGION void tsl9_resident_message_queue_block_431a8(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0xfffffff8)) = (uint32_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffffe)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x431B4..0x431BA. */
REGION void tsl9_resident_message_queue_block_431b4(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0xfffffff8)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_message_queue_edge_431b8:\n.option push\n.option rvc\nc.j .Lresident_message_queue_edge_431b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_queue_block_431a8\n");
    __builtin_unreachable();
}

/* Original0x4354A..0x43566. */
REGION void tsl9_candidate_set_event_4354a(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000019d)); LIVE;
    PORT(".Lresident_message_queue_edge_43562:\n.option push\n.option norvc\nbleu a4,a0,.Lresident_message_queue_edge_43562\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_43582\n");
    __builtin_unreachable();
}

/* Original0x43566..0x43582. */
REGION void tsl9_resident_message_queue_block_43566(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a4 = a0 << UINT32_C(0x00000001); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x000001e4)); LIVE;
    a0 = a0 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211a\n.option pop\n");
    a1 = a1 | a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a1, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa10e\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a3; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43582..0x4358A. */
REGION void tsl9_resident_message_queue_block_43582(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a3; LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4358A..0x435A6. */
REGION void tsl9_candidate_clear_event_4358a(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000019d)); LIVE;
    PORT(".Lresident_message_queue_edge_435a2:\n.option push\n.option norvc\nbleu a4,a0,.Lresident_message_queue_edge_435a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_435c6\n");
    __builtin_unreachable();
}

/* Original0x435A6..0x435C6. */
REGION void tsl9_resident_message_queue_block_435a6(void)
{
    REGS;
    a2 = UINT32_C(0x20003000); LIVE;
    a4 = a0 << UINT32_C(0x00000001); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x000001e4)); LIVE;
    PORT(".option push\n.option norvc\nnot a1, a1\n.option pop\n");
    a0 = a0 + a4; LIVE;
    /* Conditional Xwchc: qk.c.lhu a4, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x211a\n.option pop\n");
    a1 = a1 & a4; LIVE;
    /* Conditional Xwchc: qk.c.sh a1, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa10e\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a3; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x435C6..0x435CE. */
REGION void tsl9_resident_message_queue_block_435c6(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)a3; LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x439A8..0x439D0. */
REGION void tsl9_candidate_stop_task_439a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_message_queue_literal_439c8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_timer_lookup_20000314\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_message_queue_literal_439c8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x439D0..0x439D4. */
REGION void tsl9_resident_message_queue_block_439d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lresident_message_queue_edge_439d2:\n.option push\n.option rvc\nc.beqz a0,.Lresident_message_queue_edge_439d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_439d8\n");
    __builtin_unreachable();
}

/* Original0x439D4..0x439D8. */
REGION void tsl9_resident_message_queue_block_439d4(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x439D8..0x439DE. */
REGION void tsl9_resident_message_queue_block_439d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lresident_message_queue_edge_439dc:\n.option push\n.option rvc\nc.jal .Lresident_message_queue_edge_439dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_clear_event_4358a\n");
    __builtin_unreachable();
}

/* Original0x439DE..0x439EA. */
REGION void tsl9_resident_message_queue_block_439de(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019c)); LIVE;
    PORT(".Lresident_message_queue_edge_439e6:\n.option push\n.option norvc\nbne a5,s2,.Lresident_message_queue_edge_439e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_439f8\n");
    __builtin_unreachable();
}

/* Original0x439EA..0x439F8. */
REGION void tsl9_resident_message_queue_block_439ea(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000001dc)); LIVE;
    PORT(".option push\n.option rvc\nor s0, s0, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s0, 476(a5)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x439F8..0x43A04. */
REGION void tsl9_resident_message_queue_block_439f8(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_message_queue_edge_43a02:\n.option push\n.option rvc\nc.bnez s1,.Lresident_message_queue_edge_43a02\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_43a06\n");
    __builtin_unreachable();
}

/* Original0x43A04..0x43A06. */
REGION void tsl9_resident_message_queue_block_43a04(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0x43A06..0x43A14. */
REGION void tsl9_resident_message_queue_block_43a06(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000028C..0x200002B6. */
REGION void tsl9_candidate_message_receive_2000028c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a0 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s0, 408(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x200002B6..0x200002B8. */
REGION void tsl9_resident_message_queue_block_200002b6(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_200002b6:\n.option push\n.option rvc\nc.bnez s0,.Lresident_message_queue_edge_200002b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_200002c8\n");
    __builtin_unreachable();
}

/* Original0x200002B8..0x200002BA. */
REGION void tsl9_resident_message_queue_block_200002b8(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_200002b8:\n.option push\n.option rvc\nc.bnez s1,.Lresident_message_queue_edge_200002b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_200002d2\n");
    __builtin_unreachable();
}

/* Original0x200002BA..0x200002C6. */
REGION void tsl9_resident_message_queue_block_200002ba(void)
{
    REGS;
    a1 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lresident_message_queue_literal_200002be:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_stop_task_439a8\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_message_queue_literal_200002be\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200002C6..0x200002C8. */
REGION void tsl9_resident_message_queue_block_200002c6(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_200002c6:\n.option push\n.option rvc\nc.j .Lresident_message_queue_edge_200002c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_queue_block_200002ee\n");
    __builtin_unreachable();
}

/* Original0x200002C8..0x200002D0. */
REGION void tsl9_resident_message_queue_block_200002c8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, -2(s0)\n.option pop\n");
    PORT(".Lresident_message_queue_edge_200002cc:\n.option push\n.option norvc\nbne a5,s2,.Lresident_message_queue_edge_200002cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_20000306\n");
    __builtin_unreachable();
}

/* Original0x200002D0..0x200002D2. */
REGION void tsl9_resident_message_queue_block_200002d0(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_200002d0:\n.option push\n.option rvc\nc.beqz s1,.Lresident_message_queue_edge_200002d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_20000310\n");
    __builtin_unreachable();
}

/* Original0x200002D2..0x200002E0. */
REGION void tsl9_resident_message_queue_block_200002d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000198); LIVE;
    PORT(".Lresident_message_queue_literal_200002d8:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_unlink_4319c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_message_queue_literal_200002d8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200002E0..0x200002E2. */
REGION void tsl9_resident_message_queue_block_200002e0(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_200002e0:\n.option push\n.option rvc\nc.beqz s0,.Lresident_message_queue_edge_200002e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_200002ba\n");
    __builtin_unreachable();
}

/* Original0x200002E2..0x200002EE. */
REGION void tsl9_resident_message_queue_block_200002e2(void)
{
    REGS;
    a1 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".Lresident_message_queue_literal_200002e6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_set_event_4354a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_message_queue_literal_200002e6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200002EE..0x20000306. */
REGION void tsl9_resident_message_queue_block_200002ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 524(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000306..0x20000308. */
REGION void tsl9_resident_message_queue_block_20000306(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_20000306:\n.option push\n.option rvc\nc.bnez s1,.Lresident_message_queue_edge_20000306\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_2000030a\n");
    __builtin_unreachable();
}

/* Original0x20000308..0x2000030A. */
REGION void tsl9_resident_message_queue_block_20000308(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000030A..0x20000310. */
REGION void tsl9_resident_message_queue_block_2000030a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s0, -8(s0)\n.option pop\n");
    PORT(".Lresident_message_queue_edge_2000030e:\n.option push\n.option rvc\nc.j .Lresident_message_queue_edge_2000030e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_queue_block_200002b6\n");
    __builtin_unreachable();
}

/* Original0x20000310..0x20000314. */
REGION void tsl9_resident_message_queue_block_20000310(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, s0\n.option pop\n");
    PORT(".Lresident_message_queue_edge_20000312:\n.option push\n.option rvc\nc.j .Lresident_message_queue_edge_20000312\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_queue_block_2000030a\n");
    __builtin_unreachable();
}

/* Original0x20000314..0x2000031C. */
REGION void tsl9_candidate_timer_lookup_20000314(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001e8)); LIVE;
    __builtin_unreachable();
}

/* Original0x2000031C..0x2000031E. */
REGION void tsl9_resident_message_queue_block_2000031c(void)
{
    REGS;
    PORT(".Lresident_message_queue_edge_2000031c:\n.option push\n.option rvc\nc.bnez a5,.Lresident_message_queue_edge_2000031c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_message_queue_block_20000322\n");
    __builtin_unreachable();
}

/* Original0x2000031E..0x20000322. */
REGION void tsl9_resident_message_queue_block_2000031e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000322..0x20000328. */
REGION void tsl9_resident_message_queue_block_20000322(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x23ba\n.option pop\n");
    PORT(".Lresident_message_queue_edge_20000324:\n.option push\n.option norvc\nbne a4,a1,.Lresident_message_queue_edge_20000324\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_2000032e\n");
    __builtin_unreachable();
}

/* Original0x20000328..0x2000032E. */
REGION void tsl9_resident_message_queue_block_20000328(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2398\n.option pop\n");
    PORT(".Lresident_message_queue_edge_2000032a:\n.option push\n.option norvc\nbeq a4,a0,.Lresident_message_queue_edge_2000032a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_message_queue_block_2000031e\n");
    __builtin_unreachable();
}

/* Original0x2000032E..0x20000332. */
REGION void tsl9_resident_message_queue_block_2000032e(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_message_queue_edge_20000330:\n.option push\n.option rvc\nc.j .Lresident_message_queue_edge_20000330\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_message_queue_block_2000031c\n");
    __builtin_unreachable();
}
