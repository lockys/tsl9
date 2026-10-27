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

/* Six complete conditional SDK task/event/message bodies:1378B/479i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43208..0x43224. */
REGION void tsl9_candidate_message_send_43208(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40024\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s2, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".Lresident_task_transition_edge_43222:\n.option push\n.option rvc\nc.bnez a1,.Lresident_task_transition_edge_43222\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_4322c\n");
    __builtin_unreachable();
}

/* Original0x43224..0x43228. */
REGION void tsl9_resident_task_transition_block_43224(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43228..0x4322C. */
REGION void tsl9_resident_task_transition_block_43228(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_task_transition_edge_4322a:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_4322a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_4324e\n");
    __builtin_unreachable();
}

/* Original0x4322C..0x4323C. */
REGION void tsl9_resident_task_transition_block_4322c(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019d)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".Lresident_task_transition_edge_43238:\n.option push\n.option norvc\nbleu a5,s0,.Lresident_task_transition_edge_43238\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_43242\n");
    __builtin_unreachable();
}

/* Original0x4323C..0x43242. */
REGION void tsl9_resident_task_transition_block_4323c(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_transition_edge_4323e:\n.option push\n.option norvc\nbltu a5,s0,.Lresident_task_transition_edge_4323e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_4325a\n");
    __builtin_unreachable();
}

/* Original0x43242..0x43244. */
REGION void tsl9_resident_task_transition_block_43242(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_43242:\n.option push\n.option rvc\nc.jal .Lresident_task_transition_edge_43242\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_message_deallocate_431ba\n");
    __builtin_unreachable();
}

/* Original0x43244..0x4324E. */
REGION void tsl9_resident_task_transition_block_43244(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x4324E..0x4325A. */
REGION void tsl9_resident_task_transition_block_4324e(void)
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

/* Original0x4325A..0x43260. */
REGION void tsl9_resident_task_transition_block_4325a(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0xfffffff8)); LIVE;
    PORT(".Lresident_task_transition_edge_4325e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_transition_edge_4325e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_4326c\n");
    __builtin_unreachable();
}

/* Original0x43260..0x4326C. */
REGION void tsl9_resident_task_transition_block_43260(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0xfffffffe)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_transition_edge_43268:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_transition_edge_43268\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_43278\n");
    __builtin_unreachable();
}

/* Original0x4326C..0x4326E. */
REGION void tsl9_resident_task_transition_block_4326c(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_4326c:\n.option push\n.option rvc\nc.jal .Lresident_task_transition_edge_4326c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_message_deallocate_431ba\n");
    __builtin_unreachable();
}

/* Original0x4326E..0x43278. */
REGION void tsl9_resident_task_transition_block_4326e(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(a5)\n.option pop\n");
    PORT(".Lresident_task_transition_edge_43276:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_43276\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_43228\n");
    __builtin_unreachable();
}

/* Original0x43278..0x4328C. */
REGION void tsl9_resident_task_transition_block_43278(void)
{
    REGS;
    a0 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsb s0, -2(a1)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000198); LIVE;
    PORT(".Lresident_task_transition_literal_43284:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_enqueue_2000021c\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_43284\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4328C..0x43292. */
REGION void tsl9_resident_task_transition_block_4328c(void)
{
    REGS;
    a1 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_task_transition_edge_43290:\n.option push\n.option rvc\nc.jal .Lresident_task_transition_edge_43290\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_set_event_4354a\n");
    __builtin_unreachable();
}

/* Original0x43292..0x4329A. */
REGION void tsl9_resident_task_transition_block_43292(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nsw s2, 524(s1)\n.option pop\n");
    PORT(".Lresident_task_transition_edge_43298:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_43298\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_4324e\n");
    __builtin_unreachable();
}

/* Original0x52906..0x5294E. */
REGION void tsl9_candidate_event_build_52906(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -80\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 92(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\nsw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 36\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 72(sp)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nmv s11, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s10, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s9, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s8, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s7, a6\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, a7\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s5, 80(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s4, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 96(sp)\n.option pop\n");
    PORT(".Lresident_task_transition_literal_52946:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_message_allocate_20000236\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_52946\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5294E..0x52950. */
REGION void tsl9_resident_task_transition_block_5294e(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5294e:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_transition_edge_5294e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_529e4\n");
    __builtin_unreachable();
}

/* Original0x52950..0x5297A. */
REGION void tsl9_resident_task_transition_block_52950(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw t1, 12(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a2 = UINT32_C(0x010d4000); LIVE;
    a5 = a0 + UINT32_C(0x00000008); LIVE;
    a2 = a2 + UINT32_C(0xfffffe91); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nsb t1, 8(a0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    /* Conditional Xwchc: qk.c.sb a1, 9(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb50c\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s11\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_task_transition_literal_52972:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_52972\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5297A..0x529A6. */
REGION void tsl9_resident_task_transition_block_5297a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s10, 16(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s9, 17(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s8, 18(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s7, 19(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s6, 20(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s5, 22(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s4, 24(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 25\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_task_transition_literal_5299e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_5299e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x529A6..0x529BA. */
REGION void tsl9_resident_task_transition_block_529a6(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 36\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s1, 31(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xbc64\n.option pop\n");
    PORT(".option push\n.option rvc\nsw a0, 32(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    PORT(".Lresident_task_transition_literal_529b2:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_529b2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x529BA..0x529E4. */
REGION void tsl9_resident_task_transition_block_529ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 28(sp)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003ac)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 80\n.option pop\n");
    PORT(".Lresident_task_transition_edge_529e0:\n.option push\n.option norvc\njal zero,.Lresident_task_transition_edge_529e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_message_send_43208\n");
    __builtin_unreachable();
}

/* Original0x529E4..0x52A02. */
REGION void tsl9_resident_task_transition_block_529e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 80\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EE98..0x5EEB2. */
REGION void tsl9_candidate_transition_parse_5ee98(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    a2 = a0 + UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000078)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".Lresident_task_transition_literal_5eeaa:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_receive_status_2000263a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_5eeaa\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EEB2..0x5EEB6. */
REGION void tsl9_resident_task_transition_block_5eeb2(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5eeb2:\n.option push\n.option norvc\nbnez a0,.Lresident_task_transition_edge_5eeb2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f0ce\n");
    __builtin_unreachable();
}

/* Original0x5EEB6..0x5EED0. */
REGION void tsl9_resident_task_transition_block_5eeb6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a6, 120(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 0(a6)\n.option pop\n");
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 13(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb458\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 1(a6)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5eecc:\n.option push\n.option norvc\nbne a4,a3,.Lresident_task_transition_edge_5eecc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EED0..0x5EEE2. */
REGION void tsl9_resident_task_transition_block_5eed0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 2(a6)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    a3 = a4 >> UINT32_C(0x00000006); LIVE;
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    PORT(".Lresident_task_transition_edge_5eede:\n.option push\n.option norvc\nbleu a5,a4,.Lresident_task_transition_edge_5eede\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EEE2..0x5EEE8. */
REGION void tsl9_resident_task_transition_block_5eee2(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_task_transition_edge_5eee4:\n.option push\n.option norvc\nbnez a3,.Lresident_task_transition_edge_5eee4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EEE8..0x5EF06. */
REGION void tsl9_resident_task_transition_block_5eee8(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a7, a5, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a7, a7, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a7, a7, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a7, 46(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 3(a6)\n.option pop\n");
    a0 = UINT32_C(0x00000011); LIVE;
    a3 = a1 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_transition_edge_5ef02:\n.option push\n.option norvc\nbnez a3,.Lresident_task_transition_edge_5ef02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EF06..0x5EF0E. */
REGION void tsl9_resident_task_transition_block_5ef06(void)
{
    REGS;
    a3 = a1 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_task_transition_edge_5ef0a:\n.option push\n.option norvc\nbnez a3,.Lresident_task_transition_edge_5ef0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f02c\n");
    __builtin_unreachable();
}

/* Original0x5EF0E..0x5EF14. */
REGION void tsl9_resident_task_transition_block_5ef0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a2, a6, 4\n.option pop\n");
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    __builtin_unreachable();
}

/* Original0x5EF14..0x5EF1E. */
REGION void tsl9_resident_task_transition_block_5ef14(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x000000ff); LIVE;
    a4 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Lresident_task_transition_edge_5ef1c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_task_transition_edge_5ef1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5ef50\n");
    __builtin_unreachable();
}

/* Original0x5EF1E..0x5EF2E. */
REGION void tsl9_resident_task_transition_block_5ef1e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3218\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu t3, 41(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nsrli t1, a4, 0x4\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5ef2a:\n.option push\n.option norvc\nbne t3,t1,.Lresident_task_transition_edge_5ef2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EF2E..0x5EF46. */
REGION void tsl9_resident_task_transition_block_5ef2e(void)
{
    REGS;
    a0 = UINT32_C(0x00001000); LIVE;
    a0 = a0 + UINT32_C(0xffffff00); LIVE;
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 & a0; LIVE;
    /* Conditional Xwchc: qk.c.lbu a0, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x2208\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu t1, 42(s0)\n.option pop\n");
    a4 = a4 | a0; LIVE;
    a0 = UINT32_C(0x00000014); LIVE;
    PORT(".Lresident_task_transition_edge_5ef42:\n.option push\n.option norvc\nbne t1,a4,.Lresident_task_transition_edge_5ef42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EF46..0x5EF50. */
REGION void tsl9_resident_task_transition_block_5ef46(void)
{
    REGS;
    a4 = a3 + UINT32_C(0xfffffffe); LIVE;
    a2 = a2 + UINT32_C(0x00000002); LIVE;
    a3 = a4 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x5EF50..0x5EF54. */
REGION void tsl9_resident_task_transition_block_5ef50(void)
{
    REGS;
    a1 = a1 & UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_task_transition_edge_5ef52:\n.option push\n.option rvc\nc.beqz a1,.Lresident_task_transition_edge_5ef52\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5efc0\n");
    __builtin_unreachable();
}

/* Original0x5EF54..0x5EF7C. */
REGION void tsl9_resident_task_transition_block_5ef54(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x2218\n.option pop\n");
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 36(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a1, 2(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x222c\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    a4 = a4 + UINT32_C(0xffffff00); LIVE;
    a1 = a1 << UINT32_C(0x00000008); LIVE;
    a1 = a1 & a4; LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x3218\n.option pop\n");
    a1 = a1 | a4; LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsrai a1, a1, 0x10\n.option pop\n");
    a4 = a1 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sh a4, 38(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xb07a\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5ef7a:\n.option push\n.option rvc\nc.beqz a1,.Lresident_task_transition_edge_5ef7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5efb6\n");
    __builtin_unreachable();
}

/* Original0x5EF7C..0x5EF84. */
REGION void tsl9_resident_task_transition_block_5ef7c(void)
{
    REGS;
    a1 = *(volatile int8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_transition_edge_5ef80:\n.option push\n.option norvc\nbgez a1,.Lresident_task_transition_edge_5ef80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f034\n");
    __builtin_unreachable();
}

/* Original0x5EF84..0x5EF88. */
REGION void tsl9_resident_task_transition_block_5ef84(void)
{
    REGS;
    a1 = UINT32_C(0x0000012c); LIVE;
    __builtin_unreachable();
}

/* Original0x5EF88..0x5EF96. */
REGION void tsl9_resident_task_transition_block_5ef88(void)
{
    REGS;
    a4 = a4 * a1; LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 37(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_transition_edge_5ef92:\n.option push\n.option norvc\nbne a1,a0,.Lresident_task_transition_edge_5ef92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f038\n");
    __builtin_unreachable();
}

/* Original0x5EF96..0x5EF9A. */
REGION void tsl9_resident_task_transition_block_5ef96(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000b); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x5EF9A..0x5EFAE. */
REGION void tsl9_resident_task_transition_block_5ef9a(void)
{
    REGS;
    a5 = a4 - a5; LIVE;
    a1 = a5 + UINT32_C(0xfffffed4); LIVE;
    a0 = UINT32_C(0x00000514); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 40(s0)\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5efaa:\n.option push\n.option norvc\nbleu a1,a0,.Lresident_task_transition_edge_5efaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f060\n");
    __builtin_unreachable();
}

/* Original0x5EFAE..0x5EFB6. */
REGION void tsl9_resident_task_transition_block_5efae(void)
{
    REGS;
    a4 = a4 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 40(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EFB6..0x5EFC0. */
REGION void tsl9_resident_task_transition_block_5efb6(void)
{
    REGS;
    a4 = a3 + UINT32_C(0xfffffffd); LIVE;
    a2 = a2 + UINT32_C(0x00000003); LIVE;
    a3 = a4 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x5EFC0..0x5EFCC. */
REGION void tsl9_resident_task_transition_block_5efc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(a6)\n.option pop\n");
    a0 = UINT32_C(0x00000016); LIVE;
    a4 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lresident_task_transition_edge_5efca:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_transition_edge_5efca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EFCC..0x5EFD2. */
REGION void tsl9_resident_task_transition_block_5efcc(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_task_transition_edge_5efd0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_transition_edge_5efd0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5efe0\n");
    __builtin_unreachable();
}

/* Original0x5EFD2..0x5EFE0. */
REGION void tsl9_resident_task_transition_block_5efd2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a5, 0(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x221c\n.option pop\n");
    a4 = a3 + UINT32_C(0xffffffff); LIVE;
    a3 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 35(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5EFE0..0x5EFE4. */
REGION void tsl9_resident_task_transition_block_5efe0(void)
{
    REGS;
    a0 = UINT32_C(0x00000018); LIVE;
    PORT(".Lresident_task_transition_edge_5efe2:\n.option push\n.option rvc\nc.bnez a3,.Lresident_task_transition_edge_5efe2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5EFE4..0x5F028. */
REGION void tsl9_resident_task_transition_block_5efe4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 46(s0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 120(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 44(s0)\n.option pop\n");
    a5 = a5 - a2; LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lhu a5, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c7e\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a7, 21(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlb a6, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 45(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 85(s0)\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\naddi a2, s0, 86\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5f024:\n.option push\n.option norvc\njal ra,.Lresident_task_transition_edge_5f024\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_event_wrapper_6a79e\n");
    __builtin_unreachable();
}

/* Original0x5F028..0x5F02C. */
REGION void tsl9_resident_task_transition_block_5f028(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_task_transition_edge_5f02a:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f02a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5F02C..0x5F034. */
REGION void tsl9_resident_task_transition_block_5f02c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a2, a6, 5\n.option pop\n");
    a4 = a4 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lresident_task_transition_edge_5f032:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f032\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5ef14\n");
    __builtin_unreachable();
}

/* Original0x5F034..0x5F038. */
REGION void tsl9_resident_task_transition_block_5f034(void)
{
    REGS;
    a1 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lresident_task_transition_edge_5f036:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f036\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5ef88\n");
    __builtin_unreachable();
}

/* Original0x5F038..0x5F03E. */
REGION void tsl9_resident_task_transition_block_5f038(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_task_transition_edge_5f03a:\n.option push\n.option norvc\nbne a1,a0,.Lresident_task_transition_edge_5f03a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f05c\n");
    __builtin_unreachable();
}

/* Original0x5F03E..0x5F04C. */
REGION void tsl9_resident_task_transition_block_5f03e(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x0000051f)); LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_transition_edge_5f04a:\n.option push\n.option rvc\nc.beqz a1,.Lresident_task_transition_edge_5f04a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f054\n");
    __builtin_unreachable();
}

/* Original0x5F04C..0x5F054. */
REGION void tsl9_resident_task_transition_block_5f04c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x000000d7); LIVE;
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_transition_edge_5f052:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f052\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5ef9a\n");
    __builtin_unreachable();
}

/* Original0x5F054..0x5F058. */
REGION void tsl9_resident_task_transition_block_5f054(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000004a); LIVE;
    __builtin_unreachable();
}

/* Original0x5F058..0x5F05C. */
REGION void tsl9_resident_task_transition_block_5f058(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_task_transition_edge_5f05a:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f05a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5ef9a\n");
    __builtin_unreachable();
}

/* Original0x5F05C..0x5F060. */
REGION void tsl9_resident_task_transition_block_5f05c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    PORT(".Lresident_task_transition_edge_5f05e:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f05e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5f058\n");
    __builtin_unreachable();
}

/* Original0x5F060..0x5F070. */
REGION void tsl9_resident_task_transition_block_5f060(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a1, 60(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c4e\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a7, a7, a1\n.option pop\n");
    a1 = UINT32_C(0x20003000); LIVE;
    a1 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x000003f8)); LIVE;
    PORT(".Lresident_task_transition_edge_5f06c:\n.option push\n.option norvc\nble a7,a1,.Lresident_task_transition_edge_5f06c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f084\n");
    __builtin_unreachable();
}

/* Original0x5F070..0x5F07C. */
REGION void tsl9_resident_task_transition_block_5f070(void)
{
    REGS;
    a4 = a4 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 40(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0x5F07C..0x5F084. */
REGION void tsl9_resident_task_transition_block_5f07c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F084..0x5F0CE. */
REGION void tsl9_resident_task_transition_block_5f084(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nsh a7, 60(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a7, 1340(a1)\n.option pop\n");
    a4 = a4 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a0, 12(a7)\n.option pop\n");
    a4 = UINT32_C(0xffffe000); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & a0; LIVE;
    PORT(".option push\n.option norvc\nsw a4, 12(a7)\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000053c)); LIVE;
    a1 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nli a7, -128\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a1; LIVE;
    a1 = UINT32_C(0x20003000); LIVE;
    a1 = a1 + UINT32_C(0x00000514); LIVE;
    a5 = a5 + UINT32_C(0xfffffed5); LIVE;
    PORT(".option push\n.option norvc\nsb a7, 4(a1)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_task_transition_edge_5f0cc:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f0cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5efb6\n");
    __builtin_unreachable();
}

/* Original0x5F0CE..0x5F0D2. */
REGION void tsl9_resident_task_transition_block_5f0ce(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_transition_edge_5f0d0:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f0d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5f07c\n");
    __builtin_unreachable();
}

/* Original0x5F0D2..0x5F10E. */
REGION void tsl9_candidate_external_flash_5f0d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -80\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 1080(a5)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s1, 0xffffe\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s7, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s3, 0x2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s8, s7, 1300\n.option pop\n");
    PORT(".option push\n.option norvc\nli s4, -128\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F10E..0x5F112. */
REGION void tsl9_resident_task_transition_block_5f10e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F112..0x5F116. */
REGION void tsl9_resident_task_transition_block_5f112(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)); LIVE;
    PORT(".Lresident_task_transition_edge_5f114:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_transition_edge_5f114\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f112\n");
    __builtin_unreachable();
}

/* Original0x5F116..0x5F19E. */
REGION void tsl9_resident_task_transition_block_5f116(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nand a4, a3, s1\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 1340(s2)\n.option pop\n");
    a5 = UINT32_C(0x00000592); LIVE;
    a1 = UINT32_C(0x00330000); LIVE;
    PORT(".option push\n.option norvc\nsw s3, 8(a4)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s4, 4(s8)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000064)) = (uint32_t)a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s7)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s8)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffff9f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s8)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1288(s5)\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 & UINT32_C(0xfffffe7f); LIVE;
    a3 = a3 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 1424(s6)\n.option pop\n");
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)); LIVE;
    a2 = a2 | a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000008)) = (uint32_t)a2; LIVE;
    a2 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000050)) = (uint32_t)a2; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x0000002c)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 36(s0)\n.option pop\n");
    a3 = a4 & UINT32_C(0x0000007f); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffff80); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_task_transition_literal_5f196:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_external_ram_20002610\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_task_transition_literal_5f196\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F19E..0x5F1A2. */
REGION void tsl9_resident_task_transition_block_5f19e(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5f19e:\n.option push\n.option norvc\njal ra,.Lresident_task_transition_edge_5f19e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_reset_registers_63e58\n");
    __builtin_unreachable();
}

/* Original0x5F1A2..0x5F1AA. */
REGION void tsl9_resident_task_transition_block_5f1a2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1300(s7)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_task_transition_edge_5f1a8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_task_transition_edge_5f1a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f1b6\n");
    __builtin_unreachable();
}

/* Original0x5F1AA..0x5F1B4. */
REGION void tsl9_resident_task_transition_block_5f1aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1300(s7)\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5f1b0:\n.option push\n.option norvc\njal ra,.Lresident_task_transition_edge_5f1b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_transition_parse_5ee98\n");
    __builtin_unreachable();
}

/* Original0x5F1B4..0x5F1B6. */
REGION void tsl9_resident_task_transition_block_5f1b4(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5f1b4:\n.option push\n.option rvc\nc.beqz a0,.Lresident_task_transition_edge_5f1b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_5f200\n");
    __builtin_unreachable();
}

/* Original0x5F1B6..0x5F1BC. */
REGION void tsl9_resident_task_transition_block_5f1b6(void)
{
    REGS;
    a5 = UINT32_C(0xffffffa0); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa43c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F1BC..0x5F1FE. */
REGION void tsl9_resident_task_transition_block_5f1bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 44(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a7, 21(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0xffffff9f); LIVE;
    a0 = a0 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 40(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlb a6, 35(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 41(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 45(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 85(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    /* Conditional Xwchc: qk.c.lhu a2, 62(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x3c72\n.option pop\n");
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option norvc\naddi a2, s0, 86\n.option pop\n");
    PORT(".Lresident_task_transition_edge_5f1fa:\n.option push\n.option norvc\njal ra,.Lresident_task_transition_edge_5f1fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_event_wrapper_6a79e\n");
    __builtin_unreachable();
}

/* Original0x5F1FE..0x5F200. */
REGION void tsl9_resident_task_transition_block_5f1fe(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5f1fe:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f1fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5f210\n");
    __builtin_unreachable();
}

/* Original0x5F200..0x5F210. */
REGION void tsl9_resident_task_transition_block_5f200(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 40(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000020); LIVE;
    a5 = a5 & UINT32_C(0x00000060); LIVE;
    PORT(".Lresident_task_transition_edge_5f20c:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_task_transition_edge_5f20c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f228\n");
    __builtin_unreachable();
}

/* Original0x5F210..0x5F228. */
REGION void tsl9_resident_task_transition_block_5f210(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 80\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5F228..0x5F232. */
REGION void tsl9_resident_task_transition_block_5f228(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 10(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2438\n.option pop\n");
    a5 = UINT32_C(0x000000a5); LIVE;
    PORT(".Lresident_task_transition_edge_5f22e:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_task_transition_edge_5f22e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_transition_block_5f10e\n");
    __builtin_unreachable();
}

/* Original0x5F232..0x5F234. */
REGION void tsl9_resident_task_transition_block_5f232(void)
{
    REGS;
    PORT(".Lresident_task_transition_edge_5f232:\n.option push\n.option rvc\nc.j .Lresident_task_transition_edge_5f232\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_transition_block_5f1bc\n");
    __builtin_unreachable();
}

/* Original0x6A79E..0x6A7BC. */
REGION void tsl9_candidate_event_wrapper_6a79e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu t1, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu t3, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu t4, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a7, a7, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a6, a6, 255\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t4, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t3, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw t1, 0(sp)\n.option pop\n");
    PORT(".Lresident_task_transition_edge_6a7b8:\n.option push\n.option norvc\njal zero,.Lresident_task_transition_edge_6a7b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_event_build_52906\n");
    __builtin_unreachable();
}

/* Original0x2000021C..0x20000224. */
REGION void tsl9_candidate_message_enqueue_2000021c(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0xfffffff8)) = (uint32_t)0; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lresident_task_transition_edge_20000222:\n.option push\n.option rvc\nc.bnez a5,.Lresident_task_transition_edge_20000222\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_2000022a\n");
    __builtin_unreachable();
}

/* Original0x20000224..0x20000228. */
REGION void tsl9_resident_task_transition_block_20000224(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000228..0x2000022A. */
REGION void tsl9_resident_task_transition_block_20000228(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000022A..0x20000230. */
REGION void tsl9_resident_task_transition_block_2000022a(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffff8)); LIVE;
    PORT(".Lresident_task_transition_edge_2000022e:\n.option push\n.option rvc\nc.bnez a4,.Lresident_task_transition_edge_2000022e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_task_transition_block_20000228\n");
    __builtin_unreachable();
}

/* Original0x20000230..0x20000236. */
REGION void tsl9_resident_task_transition_block_20000230(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffff8)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
