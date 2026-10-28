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

/* Ten complete conditional control helpers:890B/321i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x5A120..0x5A12A. */
REGION void tsl9_candidate_unprovided_flash_5a120(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a128:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_control_helpers_edge_5a128\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a1d8\n");
    __builtin_unreachable();
}

/* Original0x5A12A..0x5A140. */
REGION void tsl9_resident_transmit_control_helpers_block_5a12a(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000055)) = (uint8_t)a4; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005e)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a1 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000060)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a13c:\n.option push\n.option norvc\nbltu a3,a4,.Lresident_transmit_control_helpers_edge_5a13c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a14a\n");
    __builtin_unreachable();
}

/* Original0x5A140..0x5A14A. */
REGION void tsl9_resident_transmit_control_helpers_block_5a140(void)
{
    REGS;
    a2 = a1 + UINT32_C(0x00000005); LIVE;
    a3 = a3 - a4; LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a146:\n.option push\n.option norvc\nblt a2,a3,.Lresident_transmit_control_helpers_edge_5a146\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a16c\n");
    __builtin_unreachable();
}

/* Original0x5A14A..0x5A15A. */
REGION void tsl9_resident_transmit_control_helpers_block_5a14a(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x0000046c)); LIVE;
    PORT(".option push\n.option rvc\nli a6, 3\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a156:\n.option push\n.option norvc\nbltu a6,a3,.Lresident_transmit_control_helpers_edge_5a156\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a160\n");
    __builtin_unreachable();
}

/* Original0x5A15A..0x5A160. */
REGION void tsl9_resident_transmit_control_helpers_block_5a15a(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    a2 = a3 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x5A160..0x5A16C. */
REGION void tsl9_resident_transmit_control_helpers_block_5a160(void)
{
    REGS;
    a4 = a4 + a1; LIVE;
    a4 = a4 + UINT32_C(0x00000008); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000055)) = (uint8_t)a2; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005e)) = (uint16_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x5A16C..0x5A1BE. */
REGION void tsl9_resident_transmit_control_helpers_block_5a16c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)0; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000055)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000056)); LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000058)); LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005a)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d8\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000056)); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3f0\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa794\n.option pop\n");
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d8\n.option pop\n");
    a4 = a2 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3f8\n.option pop\n");
    a4 = a3 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb798\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005c)); LIVE;
    a1 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a1, 11(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7ac\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000005e)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7b8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a1, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7cc\n.option pop\n");
    a1 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005e)); LIVE;
    a1 = a1 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a1, 13(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7cc\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a1, 58(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d2e\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a1ba:\n.option push\n.option norvc\nbne a1,a2,.Lresident_transmit_control_helpers_edge_5a1ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a1cc\n");
    __builtin_unreachable();
}

/* Original0x5A1BE..0x5A1C4. */
REGION void tsl9_resident_transmit_control_helpers_block_5a1be(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a2, 60(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d52\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_edge_5a1c0:\n.option push\n.option norvc\nbne a2,a3,.Lresident_transmit_control_helpers_edge_5a1c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a1cc\n");
    __builtin_unreachable();
}

/* Original0x5A1C4..0x5A1CC. */
REGION void tsl9_resident_transmit_control_helpers_block_5a1c4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a5, 62(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x3d7e\n.option pop\n");
    a5 = a5 - a4; LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0x5A1CC..0x5A1D8. */
REGION void tsl9_resident_transmit_control_helpers_block_5a1cc(void)
{
    REGS;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000062)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A1D8..0x5A1DC. */
REGION void tsl9_resident_transmit_control_helpers_block_5a1d8(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A568..0x5A588. */
REGION void tsl9_candidate_unprovided_flash_5a568(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = UINT32_C(0x0000001d); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000003bb)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a5 = UINT32_C(0x00000075); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A588..0x5A5AE. */
REGION void tsl9_candidate_unprovided_flash_5a588(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = UINT32_C(0x0000001e); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002f)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    a4 = UINT32_C(0x00008000); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A614..0x5A62A. */
REGION void tsl9_candidate_unprovided_flash_5a614(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a2 = UINT32_C(0x00000004); LIVE;
    a4 = UINT32_C(0x00000023); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb950\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000172)); LIVE;
    a4 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a628:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_control_helpers_edge_5a628\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a65a\n");
    __builtin_unreachable();
}

/* Original0x5A62A..0x5A63E. */
REGION void tsl9_resident_transmit_control_helpers_block_5a62a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000174)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    a3 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a4, a4, a3\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A63E..0x5A65A. */
REGION void tsl9_resident_transmit_control_helpers_block_5a63e(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000143)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d8\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffff85); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A65A..0x5A664. */
REGION void tsl9_resident_transmit_control_helpers_block_5a65a(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000147)); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a660:\n.option push\n.option norvc\nbne a3,a4,.Lresident_transmit_control_helpers_edge_5a660\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a67e\n");
    __builtin_unreachable();
}

/* Original0x5A664..0x5A66E. */
REGION void tsl9_resident_transmit_control_helpers_block_5a664(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000051f)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a66c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_control_helpers_edge_5a66c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a674\n");
    __builtin_unreachable();
}

/* Original0x5A66E..0x5A670. */
REGION void tsl9_resident_transmit_control_helpers_block_5a66e(void)
{
    REGS;
    a4 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x5A670..0x5A674. */
REGION void tsl9_resident_transmit_control_helpers_block_5a670(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_edge_5a672:\n.option push\n.option rvc\nc.j .Lresident_transmit_control_helpers_edge_5a672\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_control_helpers_block_5a676\n");
    __builtin_unreachable();
}

/* Original0x5A674..0x5A676. */
REGION void tsl9_resident_transmit_control_helpers_block_5a674(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a2, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A676..0x5A67E. */
REGION void tsl9_resident_transmit_control_helpers_block_5a676(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000017f)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d8\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_edge_5a67c:\n.option push\n.option rvc\nc.j .Lresident_transmit_control_helpers_edge_5a67c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_control_helpers_block_5a63e\n");
    __builtin_unreachable();
}

/* Original0x5A67E..0x5A686. */
REGION void tsl9_resident_transmit_control_helpers_block_5a67e(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a4, a4, a3\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_edge_5a684:\n.option push\n.option rvc\nc.j .Lresident_transmit_control_helpers_edge_5a684\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_control_helpers_block_5a670\n");
    __builtin_unreachable();
}

/* Original0x5A686..0x5A6A4. */
REGION void tsl9_candidate_unprovided_flash_5a686(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = UINT32_C(0x00000024); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)) = (uint8_t)0; LIVE;
    a4 = *(volatile int8_t *)(uintptr_t)(a0 + UINT32_C(0x00000143)); LIVE;
    a3 = *(volatile int8_t *)(uintptr_t)(a0 + UINT32_C(0x00000179)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a6a0:\n.option push\n.option norvc\nbne a3,a4,.Lresident_transmit_control_helpers_edge_5a6a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a6a8\n");
    __builtin_unreachable();
}

/* Original0x5A6A4..0x5A6A8. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6a4(void)
{
    REGS;
    a3 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A6A8..0x5A6B0. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6a8(void)
{
    REGS;
    a3 = *(volatile int8_t *)(uintptr_t)(a0 + UINT32_C(0x00000178)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a6ac:\n.option push\n.option norvc\nbne a3,a4,.Lresident_transmit_control_helpers_edge_5a6ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_control_helpers_block_5a6b8\n");
    __builtin_unreachable();
}

/* Original0x5A6B0..0x5A6B8. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6b0(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a3, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33b4\n.option pop\n");
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A6B8..0x5A6CE. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6b8(void)
{
    REGS;
    a3 = *(volatile int8_t *)(uintptr_t)(a0 + UINT32_C(0x00000177)); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d4\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000176)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d8\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a2, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3f0\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000172)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a6cc:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_control_helpers_edge_5a6cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a6dc\n");
    __builtin_unreachable();
}

/* Original0x5A6CE..0x5A6D0. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6ce(void)
{
    REGS;
    PORT(".Lresident_transmit_control_helpers_edge_5a6ce:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_control_helpers_edge_5a6ce\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a6dc\n");
    __builtin_unreachable();
}

/* Original0x5A6D0..0x5A6DC. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6d0(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    a4 = UINT32_C(0x00010000); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x5A6DC..0x5A6E0. */
REGION void tsl9_resident_transmit_control_helpers_block_5a6dc(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A6E0..0x5A70C. */
REGION void tsl9_candidate_unprovided_flash_5a6e0(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = UINT32_C(0x00000028); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000040a)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a4 = UINT32_C(0x0000000a); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d8\n.option pop\n");
    a4 = UINT32_C(0x00000032); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d8\n.option pop\n");
    a5 = UINT32_C(0xffffff95); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A70C..0x5A71E. */
REGION void tsl9_candidate_unprovided_flash_5a70c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s1, 272(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_edge_5a71c:\n.option push\n.option rvc\nc.beqz s1,.Lresident_transmit_control_helpers_edge_5a71c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a764\n");
    __builtin_unreachable();
}

/* Original0x5A71E..0x5A746. */
REGION void tsl9_resident_transmit_control_helpers_block_5a71e(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000060)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = a0 + UINT32_C(0x00000128); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x0000000a); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000012e)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 2(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa0bc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 3\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_transmit_control_helpers_literal_5a73e:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_control_helpers_literal_5a73e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A746..0x5A75A. */
REGION void tsl9_resident_transmit_control_helpers_block_5a746(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 302(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 8(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xa49c\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a5, 302(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 9(s1). */
    PORT(".option push\n.option rvc\n.2byte 0xb49c\n.option pop\n");
    a5 = UINT32_C(0x00000015); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A75A..0x5A764. */
REGION void tsl9_resident_transmit_control_helpers_block_5a75a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A764..0x5A768. */
REGION void tsl9_resident_transmit_control_helpers_block_5a764(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a766:\n.option push\n.option rvc\nc.j .Lresident_transmit_control_helpers_edge_5a766\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_control_helpers_block_5a75a\n");
    __builtin_unreachable();
}

/* Original0x5A7BA..0x5A7C4. */
REGION void tsl9_candidate_unprovided_flash_5a7ba(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a7c2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_control_helpers_edge_5a7c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a800\n");
    __builtin_unreachable();
}

/* Original0x5A7C4..0x5A7E4. */
REGION void tsl9_resident_transmit_control_helpers_block_5a7c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 248\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_transmit_control_helpers_literal_5a7dc:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_control_helpers_literal_5a7dc\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A7E4..0x5A800. */
REGION void tsl9_resident_transmit_control_helpers_block_5a7e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000030); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A800..0x5A804. */
REGION void tsl9_resident_transmit_control_helpers_block_5a800(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A804..0x5A80A. */
REGION void tsl9_candidate_unprovided_flash_5a804(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a808:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_control_helpers_edge_5a808\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a84a\n");
    __builtin_unreachable();
}

/* Original0x5A80A..0x5A82C. */
REGION void tsl9_resident_transmit_control_helpers_block_5a80a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000009); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb958\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 248\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_transmit_control_helpers_literal_5a824:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_control_helpers_literal_5a824\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A82C..0x5A84A. */
REGION void tsl9_resident_transmit_control_helpers_block_5a82c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 160(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 43(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 160(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A84A..0x5A84E. */
REGION void tsl9_resident_transmit_control_helpers_block_5a84a(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A898..0x5A8A2. */
REGION void tsl9_candidate_unprovided_flash_5a898(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_control_helpers_edge_5a8a0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_control_helpers_edge_5a8a0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_control_helpers_block_5a924\n");
    __builtin_unreachable();
}

/* Original0x5A8A2..0x5A908. */
REGION void tsl9_resident_transmit_control_helpers_block_5a8a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x0000000f); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000074)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = a0 + UINT32_C(0x00000068); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000075)); LIVE;
    a2 = UINT32_C(0x0000000c); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 5(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3d8\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000076)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 6(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3f8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000005a)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3f8\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000005a)); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 8(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa798\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000005c)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 9(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb798\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000005d)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 10(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7b8\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000064)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 11(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000066)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa7d8\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000066)); LIVE;
    a0 = a5 + UINT32_C(0x0000000e); LIVE;
    a4 = a4 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 13(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb7d8\n.option pop\n");
    PORT(".Lresident_transmit_control_helpers_literal_5a900:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_transmit_control_helpers_literal_5a900\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A908..0x5A924. */
REGION void tsl9_resident_transmit_control_helpers_block_5a908(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 42(s0)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 42(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000040); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa81c\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A924..0x5A928. */
REGION void tsl9_resident_transmit_control_helpers_block_5a924(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
