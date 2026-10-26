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

/* One complete public-SDK timer-list service:288B/103i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x200004FA..0x2000051A. */
REGION void tsl9_candidate_external_ram_200004fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s0, 488(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000518:\n.option push\n.option rvc\nc.beqz s0,.Lresident_timer_service_edge_20000518\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_service_block_200005c4\n");
    __builtin_unreachable();
}

/* Original0x2000051A..0x2000053C. */
REGION void tsl9_resident_timer_service_block_2000051a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s4, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option rvc\nli s7, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s5, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x1c9c\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, 492\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 412\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, 564\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000053C..0x20000540. */
REGION void tsl9_resident_timer_service_block_2000053c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x203e\n.option pop\n");
    PORT(".Lresident_timer_service_edge_2000053e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_timer_service_edge_2000053e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_service_block_2000055c\n");
    __builtin_unreachable();
}

/* Original0x20000540..0x20000546. */
REGION void tsl9_resident_timer_service_block_20000540(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 12(s0)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000542:\n.option push\n.option norvc\nbnez s7,.Lresident_timer_service_edge_20000542\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_20000556\n");
    __builtin_unreachable();
}

/* Original0x20000546..0x2000054A. */
REGION void tsl9_resident_timer_service_block_20000546(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 488(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000054A..0x20000552. */
REGION void tsl9_resident_timer_service_block_2000054a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw s8, 12(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000550:\n.option push\n.option rvc\nc.jal .Lresident_timer_service_edge_20000550\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_candidate_heap_release_20000110\n");
    __builtin_unreachable();
}

/* Original0x20000552..0x20000556. */
REGION void tsl9_resident_timer_service_block_20000552(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, s8\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000554:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_20000554\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_200005ae\n");
    __builtin_unreachable();
}

/* Original0x20000556..0x2000055C. */
REGION void tsl9_resident_timer_service_block_20000556(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a5, 12(s7)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_2000055a:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_2000055a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_2000054a\n");
    __builtin_unreachable();
}

/* Original0x2000055C..0x20000562. */
REGION void tsl9_resident_timer_service_block_2000055c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 480(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000562..0x2000056C. */
REGION void tsl9_resident_timer_service_block_20000562(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    a4 = a0 - a5; LIVE;
    PORT(".Lresident_timer_service_edge_20000568:\n.option push\n.option norvc\nbleu a5,a0,.Lresident_timer_service_edge_20000568\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_20000574\n");
    __builtin_unreachable();
}

/* Original0x2000056C..0x20000574. */
REGION void tsl9_resident_timer_service_block_2000056c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 4(s3)\n.option pop\n");
    a4 = a4 - a5; LIVE;
    a4 = a4 + a0; LIVE;
    __builtin_unreachable();
}

/* Original0x20000574..0x2000057C. */
REGION void tsl9_resident_timer_service_block_20000574(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, s6, 895\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000578:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_timer_service_edge_20000578\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_200005ec\n");
    __builtin_unreachable();
}

/* Original0x2000057C..0x2000058C. */
REGION void tsl9_resident_timer_service_block_2000057c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw zero, 16(s2)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x202e\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a0, 0(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2008\n.option pop\n");
    PORT(".Lresident_timer_service_literal_20000584:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_set_event_4354a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_timer_service_literal_20000584\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x2000058C..0x20000592. */
REGION void tsl9_resident_timer_service_block_2000058c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a4, 12(s0)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_20000590:\n.option push\n.option rvc\nc.beqz a5,.Lresident_timer_service_edge_20000590\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_service_block_200005dc\n");
    __builtin_unreachable();
}

/* Original0x20000592..0x200005A0. */
REGION void tsl9_resident_timer_service_block_20000592(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a1, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a2, 4(s3)\n.option pop\n");
    a5 = a5 + a1; LIVE;
    PORT(".option push\n.option rvc\nmv a3, a5\n.option pop\n");
    PORT(".Lresident_timer_service_edge_2000059c:\n.option push\n.option norvc\nbltu a5,a1,.Lresident_timer_service_edge_2000059c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_200005a4\n");
    __builtin_unreachable();
}

/* Original0x200005A0..0x200005A4. */
REGION void tsl9_resident_timer_service_block_200005a0(void)
{
    REGS;
    PORT(".Lresident_timer_service_edge_200005a0:\n.option push\n.option norvc\nbltu a5,a2,.Lresident_timer_service_edge_200005a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_200005a8\n");
    __builtin_unreachable();
}

/* Original0x200005A4..0x200005A8. */
REGION void tsl9_resident_timer_service_block_200005a4(void)
{
    REGS;
    a3 = a5 - a2; LIVE;
    __builtin_unreachable();
}

/* Original0x200005A8..0x200005AE. */
REGION void tsl9_resident_timer_service_block_200005a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw a3, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s7, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200005AE..0x200005B0. */
REGION void tsl9_resident_timer_service_block_200005ae(void)
{
    REGS;
    PORT(".Lresident_timer_service_edge_200005ae:\n.option push\n.option rvc\nc.bnez s0,.Lresident_timer_service_edge_200005ae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_service_block_2000053c\n");
    __builtin_unreachable();
}

/* Original0x200005B0..0x200005C0. */
REGION void tsl9_resident_timer_service_block_200005b0(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x0000019c); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_timer_service_edge_200005bc:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_timer_service_edge_200005bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_20000614\n");
    __builtin_unreachable();
}

/* Original0x200005C0..0x200005C4. */
REGION void tsl9_resident_timer_service_block_200005c0(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x200005C4..0x200005DC. */
REGION void tsl9_resident_timer_service_block_200005c4(void)
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
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x200005DC..0x200005E0. */
REGION void tsl9_resident_timer_service_block_200005dc(void)
{
    REGS;
    PORT(".Lresident_timer_service_edge_200005dc:\n.option push\n.option norvc\nbnez s7,.Lresident_timer_service_edge_200005dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_200005e6\n");
    __builtin_unreachable();
}

/* Original0x200005E0..0x200005E6. */
REGION void tsl9_resident_timer_service_block_200005e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a4, 488(s1)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_200005e4:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_200005e4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_2000054a\n");
    __builtin_unreachable();
}

/* Original0x200005E6..0x200005EC. */
REGION void tsl9_resident_timer_service_block_200005e6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a4, 12(s7)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_200005ea:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_200005ea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_2000054a\n");
    __builtin_unreachable();
}

/* Original0x200005EC..0x200005F2. */
REGION void tsl9_resident_timer_service_block_200005ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 40(s4)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_200005f0:\n.option push\n.option rvc\nc.beqz a4,.Lresident_timer_service_edge_200005f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_timer_service_block_20000606\n");
    __builtin_unreachable();
}

/* Original0x200005F2..0x200005F6. */
REGION void tsl9_resident_timer_service_block_200005f2(void)
{
    REGS;
    PORT(".Lresident_timer_service_edge_200005f2:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_timer_service_edge_200005f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_2000060c\n");
    __builtin_unreachable();
}

/* Original0x200005F6..0x20000602. */
REGION void tsl9_resident_timer_service_block_200005f6(void)
{
    REGS;
    a0 = a5 - a0; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 16(s2)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_200005fe:\n.option push\n.option norvc\nbleu a5,a0,.Lresident_timer_service_edge_200005fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_timer_service_block_20000606\n");
    __builtin_unreachable();
}

/* Original0x20000602..0x20000606. */
REGION void tsl9_resident_timer_service_block_20000602(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 16(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x20000606..0x2000060C. */
REGION void tsl9_resident_timer_service_block_20000606(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s7, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 12(s0)\n.option pop\n");
    PORT(".Lresident_timer_service_edge_2000060a:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_2000060a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_200005ae\n");
    __builtin_unreachable();
}

/* Original0x2000060C..0x20000614. */
REGION void tsl9_resident_timer_service_block_2000060c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 4(s3)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".Lresident_timer_service_edge_20000612:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_20000612\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_200005f6\n");
    __builtin_unreachable();
}

/* Original0x20000614..0x2000061A. */
REGION void tsl9_resident_timer_service_block_20000614(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    PORT(".Lresident_timer_service_edge_20000618:\n.option push\n.option rvc\nc.j .Lresident_timer_service_edge_20000618\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_timer_service_block_200005c4\n");
    __builtin_unreachable();
}
