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

/* Five complete helpers plus event body:1938B/645i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x10CE0..0x10CF2. */
REGION void tsl9_central_event_callbacks_entry_10ce0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a6, 16(a0)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x10CF2..0x10CF6. */
REGION void tsl9_central_event_callbacks_block_10cf2(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_10cf2:\n.option push\n.option norvc\nbltu a5,a0,.Lcentral_event_callbacks_edge_10cf2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_10cfa\n");
    __builtin_unreachable();
}

/* Original0x10CF6..0x10CFA. */
REGION void tsl9_central_event_callbacks_block_10cf6(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10CFA..0x10D04. */
REGION void tsl9_central_event_callbacks_block_10cfa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a7, a6, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 0(a7)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_10d02:\n.option push\n.option rvc\nc.beqz a4,.Lcentral_event_callbacks_edge_10d02\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_10cf6\n");
    __builtin_unreachable();
}

/* Original0x10D04..0x10D0C. */
REGION void tsl9_central_event_callbacks_block_10d04(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd t1, a5, a4\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_10d08:\n.option push\n.option norvc\nblt a0,t1,.Lcentral_event_callbacks_edge_10d08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_10cf6\n");
    __builtin_unreachable();
}

/* Original0x10D0C..0x10D14. */
REGION void tsl9_central_event_callbacks_block_10d0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a7, 1(a7)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_10d10:\n.option push\n.option norvc\nbne a7,a1,.Lcentral_event_callbacks_edge_10d10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_10d24\n");
    __builtin_unreachable();
}

/* Original0x10D14..0x10D24. */
REGION void tsl9_central_event_callbacks_block_10d14(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint8_t)a4; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10D24..0x10D2E. */
REGION void tsl9_central_event_callbacks_block_10d24(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lcentral_event_callbacks_edge_10d2c:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_10d2c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_10cf2\n");
    __builtin_unreachable();
}

/* Original0x110F8..0x11120. */
REGION void tsl9_central_event_callbacks_entry_110f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -96\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 88(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 112(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s11, 44(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000088); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11120..0x11124. */
REGION void tsl9_central_event_callbacks_block_11120(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11120:\n.option push\n.option norvc\nbeqz a0,.Lcentral_event_callbacks_edge_11120\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1122a\n");
    __builtin_unreachable();
}

/* Original0x11124..0x11156. */
REGION void tsl9_central_event_callbacks_block_11124(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffeaa); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\naddi s2, gp, 92\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000001)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 76(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000085); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nlui s3, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11156..0x1116E. */
REGION void tsl9_central_event_callbacks_block_11156(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s6, s1, 129\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s11, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nli s7, -128\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, -2\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nli s8, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s9, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nli s5, 12\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1116E..0x11186. */
REGION void tsl9_central_event_callbacks_block_1116e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffe7e); LIVE;
    PORT(".option push\n.option norvc\nsb s7, 3(s11)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 4(s11)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s11, 6\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s10, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11186..0x1118E. */
REGION void tsl9_central_event_callbacks_block_11186(void)
{
    REGS;
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1118a:\n.option push\n.option norvc\nbeq a3,s3,.Lcentral_event_callbacks_edge_1118a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11248\n");
    __builtin_unreachable();
}

/* Original0x1118E..0x111A0. */
REGION void tsl9_central_event_callbacks_block_1118e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a3, 60(s4)\n.option pop\n");
    a1 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option rvc\njalr a3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x111A0..0x111A6. */
REGION void tsl9_central_event_callbacks_block_111a0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_111a4:\n.option push\n.option rvc\nc.beqz a0,.Lcentral_event_callbacks_edge_111a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11248\n");
    __builtin_unreachable();
}

/* Original0x111A6..0x111B8. */
REGION void tsl9_central_event_callbacks_block_111a6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a5, s0, s5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 384(s9)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s10\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x111B8..0x111BA. */
REGION void tsl9_central_event_callbacks_block_111b8(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_111b8:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_111b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_111c4\n");
    __builtin_unreachable();
}

/* Original0x111BA..0x111C4. */
REGION void tsl9_central_event_callbacks_block_111ba(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a5 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s11)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x111C4..0x111D4. */
REGION void tsl9_central_event_callbacks_block_111c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul s0, s0, s5\n.option pop\n");
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nadd s0, s0, s10\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 10(s0)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_111d0:\n.option push\n.option norvc\nbleu a4,a5,.Lcentral_event_callbacks_edge_111d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11202\n");
    __builtin_unreachable();
}

/* Original0x111D4..0x111FA. */
REGION void tsl9_central_event_callbacks_block_111d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsub a5, s11, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s0)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffb\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xfffffdee)); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 28\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 244(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x111FA..0x11202. */
REGION void tsl9_central_event_callbacks_block_111fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 4(s11)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11202..0x1120A. */
REGION void tsl9_central_event_callbacks_block_11202(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s11, s11, 43\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11206:\n.option push\n.option norvc\nbne s11,s6,.Lcentral_event_callbacks_edge_11206\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1116e\n");
    __builtin_unreachable();
}

/* Original0x1120A..0x11220. */
REGION void tsl9_central_event_callbacks_block_1120a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xfffffdd0)); LIVE;
    a3 = UINT32_C(0x00000088); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s1\n.option pop\n");
    a1 = UINT32_C(0x000000f0); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1121c:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1121c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x11220..0x1122A. */
REGION void tsl9_central_event_callbacks_block_11220(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000068)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1122A..0x11248. */
REGION void tsl9_central_event_callbacks_block_1122a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 92(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 88(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 84(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 80(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s9, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s11, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 96\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11248..0x11250. */
REGION void tsl9_central_event_callbacks_block_11248(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    a5 = a5 + UINT32_C(0x0000000c); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1124c:\n.option push\n.option norvc\nbne s0,s8,.Lcentral_event_callbacks_edge_1124c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11186\n");
    __builtin_unreachable();
}

/* Original0x11250..0x11252. */
REGION void tsl9_central_event_callbacks_block_11250(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11250:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11250\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11202\n");
    __builtin_unreachable();
}

/* Original0x11252..0x11266. */
REGION void tsl9_central_event_callbacks_entry_11252(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 80(a5)\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffd78)); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11266..0x11286. */
REGION void tsl9_central_event_callbacks_entry_11266(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffd6c); LIVE;
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11284:\n.option push\n.option rvc\nc.beqz a0,.Lcentral_event_callbacks_edge_11284\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_112a6\n");
    __builtin_unreachable();
}

/* Original0x11286..0x11292. */
REGION void tsl9_central_event_callbacks_block_11286(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000003c)); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11292..0x11294. */
REGION void tsl9_central_event_callbacks_block_11292(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11292:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_11292\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11314\n");
    __builtin_unreachable();
}

/* Original0x11294..0x112A6. */
REGION void tsl9_central_event_callbacks_block_11294(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x112A6..0x112AA. */
REGION void tsl9_central_event_callbacks_block_112a6(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_112a6:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_112a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_10d9a\n");
    __builtin_unreachable();
}

/* Original0x112AA..0x112B0. */
REGION void tsl9_central_event_callbacks_block_112aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcentral_event_callbacks_edge_112ac:\n.option push\n.option norvc\nbltu a5,a0,.Lcentral_event_callbacks_edge_112ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11294\n");
    __builtin_unreachable();
}

/* Original0x112B0..0x112C8. */
REGION void tsl9_central_event_callbacks_block_112b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlui s2, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -710\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s5, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, s5, -682\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, -2\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x40\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x112C8..0x112D0. */
REGION void tsl9_central_event_callbacks_block_112c8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 2(s0)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_112cc:\n.option push\n.option norvc\nbne a5,s2,.Lcentral_event_callbacks_edge_112cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11302\n");
    __builtin_unreachable();
}

/* Original0x112D0..0x112D6. */
REGION void tsl9_central_event_callbacks_block_112d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 12\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_112d2:\n.option push\n.option norvc\nbne s5,s0,.Lcentral_event_callbacks_edge_112d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_112c8\n");
    __builtin_unreachable();
}

/* Original0x112D6..0x112E4. */
REGION void tsl9_central_event_callbacks_block_112d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 129\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x112E4..0x112F6. */
REGION void tsl9_central_event_callbacks_block_112e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x112F6..0x112F8. */
REGION void tsl9_central_event_callbacks_block_112f6(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_112f6:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_112f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11314\n");
    __builtin_unreachable();
}

/* Original0x112F8..0x11300. */
REGION void tsl9_central_event_callbacks_block_112f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, 43\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_112fc:\n.option push\n.option norvc\nbeq s0,s5,.Lcentral_event_callbacks_edge_112fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11294\n");
    __builtin_unreachable();
}

/* Original0x11300..0x11302. */
REGION void tsl9_central_event_callbacks_block_11300(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11300:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11300\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_112e4\n");
    __builtin_unreachable();
}

/* Original0x11302..0x11310. */
REGION void tsl9_central_event_callbacks_block_11302(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11310..0x11312. */
REGION void tsl9_central_event_callbacks_block_11310(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11310:\n.option push\n.option rvc\nc.beqz a0,.Lcentral_event_callbacks_edge_11310\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_112d0\n");
    __builtin_unreachable();
}

/* Original0x11312..0x11314. */
REGION void tsl9_central_event_callbacks_block_11312(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11312:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11312\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11294\n");
    __builtin_unreachable();
}

/* Original0x11314..0x1133A. */
REGION void tsl9_central_event_callbacks_block_11314(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffccb)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s3, -828(a5)\n.option pop\n");
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffcb3); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1133A..0x11356. */
REGION void tsl9_central_event_callbacks_block_1133a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc98)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11352:\n.option push\n.option norvc\njal zero,.Lcentral_event_callbacks_edge_11352\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_11252\n");
    __builtin_unreachable();
}

/* Original0x114E2..0x114E4. */
REGION void tsl9_central_event_callbacks_entry_114e2(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_114e2:\n.option push\n.option rvc\nc.beqz a0,.Lcentral_event_callbacks_edge_114e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_1152c\n");
    __builtin_unreachable();
}

/* Original0x114E4..0x11510. */
REGION void tsl9_central_event_callbacks_block_114e4(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffaed)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffade)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffad8)) = (uint16_t)a1; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffface)) = (uint8_t)a2; LIVE;
    PORT(".Lcentral_event_callbacks_edge_1150c:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1150c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_11356\n");
    __builtin_unreachable();
}

/* Original0x11510..0x1152A. */
REGION void tsl9_central_event_callbacks_block_11510(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffaae)); LIVE;
    a2 = UINT32_C(0x000001e0); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1152A..0x1152C. */
REGION void tsl9_central_event_callbacks_block_1152a(void)
{
    REGS;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1152C..0x11544. */
REGION void tsl9_central_event_callbacks_block_1152c(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 88(a5)\n.option pop\n");
    a2 = UINT32_C(0x000001e0); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffa8e)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11542:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11542\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_1152a\n");
    __builtin_unreachable();
}

/* Original0x11544..0x1154E. */
REGION void tsl9_central_event_callbacks_entry_11544(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1154a:\n.option push\n.option norvc\nbltu a4,a5,.Lcentral_event_callbacks_edge_1154a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_119c6\n");
    __builtin_unreachable();
}

/* Original0x1154E..0x11570. */
REGION void tsl9_central_event_callbacks_block_1154e(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_literal_1154e:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_central_event_callbacks_static_data_1a548\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcentral_event_callbacks_literal_1154e\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -80\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 56(sp)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11570..0x1157E. */
REGION void tsl9_central_event_callbacks_block_11570(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, a0, 5\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1157a:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1157a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_11266\n");
    __builtin_unreachable();
}

/* Original0x1157E..0x11588. */
REGION void tsl9_central_event_callbacks_block_1157e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa5a)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11586:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_11586\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11628\n");
    __builtin_unreachable();
}

/* Original0x11588..0x11592. */
REGION void tsl9_central_event_callbacks_block_11588(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 3\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1158e:\n.option push\n.option norvc\nbeq a5,s3,.Lcentral_event_callbacks_edge_1158e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11628\n");
    __builtin_unreachable();
}

/* Original0x11592..0x115A0. */
REGION void tsl9_central_event_callbacks_block_11592(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, sp, 7\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    a1 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1159c:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1159c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_10ce0\n");
    __builtin_unreachable();
}

/* Original0x115A0..0x115A2. */
REGION void tsl9_central_event_callbacks_block_115a0(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_115a0:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_115a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11628\n");
    __builtin_unreachable();
}

/* Original0x115A2..0x115AE. */
REGION void tsl9_central_event_callbacks_block_115a2(void)
{
    REGS;
    a2 = UINT32_C(0x00000022); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 12\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_115aa:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_115aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_tagged_external_8520\n");
    __builtin_unreachable();
}

/* Original0x115AE..0x115C0. */
REGION void tsl9_central_event_callbacks_block_115ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 72(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000022); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x115C0..0x115F0. */
REGION void tsl9_central_event_callbacks_block_115c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffa14); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nsb s3, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 11(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 16\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 76(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x115F0..0x115FA. */
REGION void tsl9_central_event_callbacks_block_115f0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".Lcentral_event_callbacks_edge_115f6:\n.option push\n.option norvc\nbleu a4,a5,.Lcentral_event_callbacks_edge_115f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11600\n");
    __builtin_unreachable();
}

/* Original0x115FA..0x11600. */
REGION void tsl9_central_event_callbacks_block_115fa(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x11600..0x11612. */
REGION void tsl9_central_event_callbacks_block_11600(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option norvc\naddi a0, sp, 22\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11612..0x11628. */
REGION void tsl9_central_event_callbacks_block_11612(void)
{
    REGS;
    a3 = UINT32_C(0x00000022); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x000000f0); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0xfffff9be)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11624:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11624\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x11628..0x11634. */
REGION void tsl9_central_event_callbacks_block_11628(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a3, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11630:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11630\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_10ce0\n");
    __builtin_unreachable();
}

/* Original0x11634..0x1163A. */
REGION void tsl9_central_event_callbacks_block_11634(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11636:\n.option push\n.option norvc\nbnez a0,.Lcentral_event_callbacks_edge_11636\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x1163A..0x11644. */
REGION void tsl9_central_event_callbacks_block_1163a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11640:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11640\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x11644..0x11652. */
REGION void tsl9_central_event_callbacks_block_11644(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0x00000043); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1164e:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_1164e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x11652..0x1165E. */
REGION void tsl9_central_event_callbacks_block_11652(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000001)); LIVE;
    a5 = UINT32_C(0x0000004d); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1165a:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_1165a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x1165E..0x1166A. */
REGION void tsl9_central_event_callbacks_block_1165e(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000002)); LIVE;
    a5 = UINT32_C(0x00000054); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11666:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11666\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x1166A..0x11676. */
REGION void tsl9_central_event_callbacks_block_1166a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000034); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11672:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11672\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x11676..0x11682. */
REGION void tsl9_central_event_callbacks_block_11676(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0x00000035); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1167e:\n.option push\n.option norvc\nbeq a5,a4,.Lcentral_event_callbacks_edge_1167e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1168c\n");
    __builtin_unreachable();
}

/* Original0x11682..0x1168C. */
REGION void tsl9_central_event_callbacks_block_11682(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffb5); LIVE;
    a5 = a5 & UINT32_C(0x000000f7); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1168a:\n.option push\n.option rvc\nc.bnez a5,.Lcentral_event_callbacks_edge_1168a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x1168C..0x11698. */
REGION void tsl9_central_event_callbacks_block_1168c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000005)); LIVE;
    a4 = UINT32_C(0x00000033); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11694:\n.option push\n.option norvc\nbeq a5,a4,.Lcentral_event_callbacks_edge_11694\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_116a2\n");
    __builtin_unreachable();
}

/* Original0x11698..0x116A2. */
REGION void tsl9_central_event_callbacks_block_11698(void)
{
    REGS;
    a4 = UINT32_C(0x00000030); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1169e:\n.option push\n.option norvc\nbne a5,a4,.Lcentral_event_callbacks_edge_1169e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x116A2..0x116B0. */
REGION void tsl9_central_event_callbacks_block_116a2(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000007)); LIVE;
    a5 = UINT32_C(0x0000002d); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_116ac:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_116ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_1173c\n");
    __builtin_unreachable();
}

/* Original0x116B0..0x116C4. */
REGION void tsl9_central_event_callbacks_block_116b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000016); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff956); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x116C4..0x116C8. */
REGION void tsl9_central_event_callbacks_block_116c4(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_116c4:\n.option push\n.option norvc\nbnez a0,.Lcentral_event_callbacks_edge_116c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11806\n");
    __builtin_unreachable();
}

/* Original0x116C8..0x116DA. */
REGION void tsl9_central_event_callbacks_block_116c8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 76(s2)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff942); LIVE;
    a2 = UINT32_C(0x00000016); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x116DA..0x11702. */
REGION void tsl9_central_event_callbacks_block_116da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 7(s0)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nslli s1, s1, 0x8\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000006)); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nli a6, 9\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli a7, 10\n.option pop\n");
    a0 = UINT32_C(0x0000000c); LIVE;
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x11702..0x11716. */
REGION void tsl9_central_event_callbacks_block_11702(void)
{
    REGS;
    a3 = a4 + a5; LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a3 = a2 + UINT32_C(0xffffffd0); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11712:\n.option push\n.option norvc\nbltu a6,a3,.Lcentral_event_callbacks_edge_11712\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11724\n");
    __builtin_unreachable();
}

/* Original0x11716..0x11724. */
REGION void tsl9_central_event_callbacks_block_11716(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a1, a1, a7\n.option pop\n");
    a1 = a1 + UINT32_C(0xffffffd0); LIVE;
    a1 = a1 + a2; LIVE;
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x11724..0x1172A. */
REGION void tsl9_central_event_callbacks_block_11724(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11726:\n.option push\n.option norvc\nbne a5,a0,.Lcentral_event_callbacks_edge_11726\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11702\n");
    __builtin_unreachable();
}

/* Original0x1172A..0x11736. */
REGION void tsl9_central_event_callbacks_block_1172a(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    a2 = a2 + UINT32_C(0xffffffad); LIVE;
    a2 = (uint32_t)(a2 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x11736..0x1173C. */
REGION void tsl9_central_event_callbacks_block_11736(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11738:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11738\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_114e2\n");
    __builtin_unreachable();
}

/* Original0x1173C..0x1174A. */
REGION void tsl9_central_event_callbacks_block_1173c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a3, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11746:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11746\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_10ce0\n");
    __builtin_unreachable();
}

/* Original0x1174A..0x1174C. */
REGION void tsl9_central_event_callbacks_block_1174a(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_1174a:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_1174a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x1174C..0x11756. */
REGION void tsl9_central_event_callbacks_block_1174c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11752:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11752\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11756..0x11764. */
REGION void tsl9_central_event_callbacks_block_11756(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a4 = UINT32_C(0x00000054); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11760:\n.option push\n.option norvc\nbne a3,a4,.Lcentral_event_callbacks_edge_11760\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11764..0x11770. */
REGION void tsl9_central_event_callbacks_block_11764(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    a4 = UINT32_C(0x00000045); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1176c:\n.option push\n.option norvc\nbne a3,a4,.Lcentral_event_callbacks_edge_1176c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11770..0x1177C. */
REGION void tsl9_central_event_callbacks_block_11770(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0x000000bf); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11778:\n.option push\n.option norvc\nbne a3,a4,.Lcentral_event_callbacks_edge_11778\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x1177C..0x11788. */
REGION void tsl9_central_event_callbacks_block_1177c(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a5 = UINT32_C(0x000000aa); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11784:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11784\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11788..0x1178C. */
REGION void tsl9_central_event_callbacks_block_11788(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11788:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11788\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0x1178C..0x117A0. */
REGION void tsl9_central_event_callbacks_block_1178c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000150); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x0000015d); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    a5 = a0 - a5; LIVE;
    PORT(".Lcentral_event_callbacks_edge_1179c:\n.option push\n.option norvc\nbleu a5,a4,.Lcentral_event_callbacks_edge_1179c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117e8\n");
    __builtin_unreachable();
}

/* Original0x117A0..0x117B6. */
REGION void tsl9_central_event_callbacks_block_117a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s3)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a2 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff87c); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x117B6..0x117B8. */
REGION void tsl9_central_event_callbacks_block_117b6(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_117b6:\n.option push\n.option rvc\nc.bnez a0,.Lcentral_event_callbacks_edge_117b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_117e8\n");
    __builtin_unreachable();
}

/* Original0x117B8..0x117CA. */
REGION void tsl9_central_event_callbacks_block_117b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 76(s3)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a2 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff868); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x117CA..0x117E8. */
REGION void tsl9_central_event_callbacks_block_117ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 7(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nslli s1, s1, 0x8\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nadd s1, s1, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x117E8..0x117F6. */
REGION void tsl9_central_event_callbacks_block_117e8(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nsw s2, 336(gp)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_117f2:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_117f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_114e2\n");
    __builtin_unreachable();
}

/* Original0x117F6..0x11806. */
REGION void tsl9_central_event_callbacks_block_117f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 80\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11806..0x1180C. */
REGION void tsl9_central_event_callbacks_block_11806(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1180a:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_1180a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11736\n");
    __builtin_unreachable();
}

/* Original0x1180C..0x11818. */
REGION void tsl9_central_event_callbacks_block_1180c(void)
{
    REGS;
    a1 = a0 + UINT32_C(0x00000005); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11814:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11814\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_11266\n");
    __builtin_unreachable();
}

/* Original0x11818..0x1181A. */
REGION void tsl9_central_event_callbacks_block_11818(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11818:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11818\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x1181A..0x11824. */
REGION void tsl9_central_event_callbacks_block_1181a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007c7)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11822:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_11822\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_1188e\n");
    __builtin_unreachable();
}

/* Original0x11824..0x11836. */
REGION void tsl9_central_event_callbacks_block_11824(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 80(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000007a8)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11836..0x1184A. */
REGION void tsl9_central_event_callbacks_block_11836(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 88(s0)\n.option pop\n");
    a2 = UINT32_C(0x00001000); LIVE;
    a2 = a2 + UINT32_C(0xfffffc80); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000794)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1184A..0x1184C. */
REGION void tsl9_central_event_callbacks_block_1184a(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_1184a:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_1184a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x1184C..0x11860. */
REGION void tsl9_central_event_callbacks_block_1184c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 92(s3)\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000077e)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11860..0x11870. */
REGION void tsl9_central_event_callbacks_block_11860(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1904\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s4, s1\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1186e:\n.option push\n.option rvc\nc.bnez a5,.Lcentral_event_callbacks_edge_1186e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11924\n");
    __builtin_unreachable();
}

/* Original0x11870..0x11874. */
REGION void tsl9_central_event_callbacks_block_11870(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11870:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11870\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_10d9a\n");
    __builtin_unreachable();
}

/* Original0x11874..0x11880. */
REGION void tsl9_central_event_callbacks_block_11874(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nlhu a0, 10(s0)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_1187c:\n.option push\n.option norvc\nbleu s1,a5,.Lcentral_event_callbacks_edge_1187c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_11894\n");
    __builtin_unreachable();
}

/* Original0x11880..0x11886. */
REGION void tsl9_central_event_callbacks_block_11880(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 380(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11886..0x1188E. */
REGION void tsl9_central_event_callbacks_block_11886(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000075a)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x1188E..0x11892. */
REGION void tsl9_central_event_callbacks_block_1188e(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_1188e:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1188e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x11892..0x11894. */
REGION void tsl9_central_event_callbacks_block_11892(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11892:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11892\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11894..0x118BC. */
REGION void tsl9_central_event_callbacks_block_11894(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a5, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s2, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 1874\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 4\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a4, s2, a5\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000002)) = (uint16_t)a0; LIVE;
    a0 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 76(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x118BC..0x118C2. */
REGION void tsl9_central_event_callbacks_block_118bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 8(s4)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_118c0:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_118c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_118ca\n");
    __builtin_unreachable();
}

/* Original0x118C2..0x118CA. */
REGION void tsl9_central_event_callbacks_block_118c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 10(s0)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint16_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x118CA..0x118CE. */
REGION void tsl9_central_event_callbacks_block_118ca(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_118ca:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_118ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_110f8\n");
    __builtin_unreachable();
}

/* Original0x118CE..0x118D4. */
REGION void tsl9_central_event_callbacks_block_118ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 8(s4)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_118d2:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_118d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_1190e\n");
    __builtin_unreachable();
}

/* Original0x118D4..0x118EC. */
REGION void tsl9_central_event_callbacks_block_118d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 88(s0)\n.option pop\n");
    a2 = UINT32_C(0x00002000); LIVE;
    a2 = a2 + UINT32_C(0xffffff40); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000006f2)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x118EC..0x1190C. */
REGION void tsl9_central_event_callbacks_block_118ec(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 232(s0)\n.option pop\n");
    a2 = UINT32_C(0x00010000); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffa\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x000006dc)); LIVE;
    a2 = a2 + UINT32_C(0xffffffff); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nadd s1, s1, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1190C..0x1190E. */
REGION void tsl9_central_event_callbacks_block_1190c(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_1190c:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_1190c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11886\n");
    __builtin_unreachable();
}

/* Original0x1190E..0x11922. */
REGION void tsl9_central_event_callbacks_block_1190e(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a5, s1, a5\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s2\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000a)) = (uint8_t)0; LIVE;
    PORT(".Lcentral_event_callbacks_edge_1191e:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1191e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10eb2\n");
    __builtin_unreachable();
}

/* Original0x11922..0x11924. */
REGION void tsl9_central_event_callbacks_block_11922(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11922:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11922\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11886\n");
    __builtin_unreachable();
}

/* Original0x11924..0x11928. */
REGION void tsl9_central_event_callbacks_block_11924(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s1)\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11926:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_11926\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_11886\n");
    __builtin_unreachable();
}

/* Original0x11928..0x1192C. */
REGION void tsl9_central_event_callbacks_block_11928(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11928:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11928\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x1192C..0x11932. */
REGION void tsl9_central_event_callbacks_block_1192c(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1192e:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_1192e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x11932..0x11946. */
REGION void tsl9_central_event_callbacks_block_11932(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcentral_event_callbacks_literal_1193a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_provider_9508\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcentral_event_callbacks_literal_1193a\n.option pop\n");
    PORT(".Lcentral_event_callbacks_edge_11942:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_11942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x11946..0x11948. */
REGION void tsl9_central_event_callbacks_block_11946(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_11946:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_11946\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_11886\n");
    __builtin_unreachable();
}

/* Original0x11948..0x11960. */
REGION void tsl9_central_event_callbacks_block_11948(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x000006a2)); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000698); LIVE;
    PORT(".Lcentral_event_callbacks_edge_1195c:\n.option push\n.option norvc\nbeq a4,a5,.Lcentral_event_callbacks_edge_1195c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_119b8\n");
    __builtin_unreachable();
}

/* Original0x11960..0x1196C. */
REGION void tsl9_central_event_callbacks_block_11960(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000069a)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11968:\n.option push\n.option norvc\nbeq a4,a5,.Lcentral_event_callbacks_edge_11968\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_119bc\n");
    __builtin_unreachable();
}

/* Original0x1196C..0x11978. */
REGION void tsl9_central_event_callbacks_block_1196c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000069a)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_11974:\n.option push\n.option norvc\nbne a4,a5,.Lcentral_event_callbacks_edge_11974\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_central_event_callbacks_block_117f6\n");
    __builtin_unreachable();
}

/* Original0x11978..0x1197A. */
REGION void tsl9_central_event_callbacks_block_11978(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x1197A..0x119A0. */
REGION void tsl9_central_event_callbacks_block_1197a(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    a5 = a5 * a4; LIVE;
    a4 = UINT32_C(0xfffe0000); LIVE;
    a4 = a4 + UINT32_C(0x00000080); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a3 = a0 + a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000000a)) = (uint8_t)0; LIVE;
    a4 = UINT32_C(0x00040000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000048)); LIVE;
    a5 = a5 + UINT32_C(0x00000004); LIVE;
    a0 = a0 + a5; LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x119A0..0x119AC. */
REGION void tsl9_central_event_callbacks_block_119a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000634); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lcentral_event_callbacks_edge_119aa:\n.option push\n.option rvc\nc.beqz a5,.Lcentral_event_callbacks_edge_119aa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_central_event_callbacks_block_119c0\n");
    __builtin_unreachable();
}

/* Original0x119AC..0x119B0. */
REGION void tsl9_central_event_callbacks_block_119ac(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_119ac:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_119ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x119B0..0x119B6. */
REGION void tsl9_central_event_callbacks_block_119b0(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcentral_event_callbacks_edge_119b2:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_119b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x119B6..0x119B8. */
REGION void tsl9_central_event_callbacks_block_119b6(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_119b6:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_119b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_1188e\n");
    __builtin_unreachable();
}

/* Original0x119B8..0x119BC. */
REGION void tsl9_central_event_callbacks_block_119b8(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcentral_event_callbacks_edge_119ba:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_119ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_1197a\n");
    __builtin_unreachable();
}

/* Original0x119BC..0x119C0. */
REGION void tsl9_central_event_callbacks_block_119bc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lcentral_event_callbacks_edge_119be:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_119be\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_1197a\n");
    __builtin_unreachable();
}

/* Original0x119C0..0x119C4. */
REGION void tsl9_central_event_callbacks_block_119c0(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_119c0:\n.option push\n.option norvc\njal ra,.Lcentral_event_callbacks_edge_119c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_110f8\n");
    __builtin_unreachable();
}

/* Original0x119C4..0x119C6. */
REGION void tsl9_central_event_callbacks_block_119c4(void)
{
    REGS;
    PORT(".Lcentral_event_callbacks_edge_119c4:\n.option push\n.option rvc\nc.j .Lcentral_event_callbacks_edge_119c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_central_event_callbacks_block_1188e\n");
    __builtin_unreachable();
}

/* Original0x119C6..0x119C8. */
REGION void tsl9_central_event_callbacks_block_119c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
