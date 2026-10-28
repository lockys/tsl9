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

/* Twelve complete conditional state helpers:682B/257i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x5A1DC..0x5A1E6. */
REGION void tsl9_candidate_unprovided_flash_5a1dc(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb958\n.option pop\n");
    PORT(".Lresident_transmit_state_helpers_edge_5a1e4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a1e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a202\n");
    __builtin_unreachable();
}

/* Original0x5A1E6..0x5A202. */
REGION void tsl9_resident_transmit_state_helpers_block_5a1e6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000054)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x0000001c); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A202..0x5A206. */
REGION void tsl9_resident_transmit_state_helpers_block_5a202(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A222..0x5A22C. */
REGION void tsl9_candidate_unprovided_flash_5a222(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a22a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a22a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a23a\n");
    __builtin_unreachable();
}

/* Original0x5A22C..0x5A23A. */
REGION void tsl9_resident_transmit_state_helpers_block_5a22c(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = UINT32_C(0x0000002d); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A23A..0x5A23E. */
REGION void tsl9_resident_transmit_state_helpers_block_5a23a(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A23E..0x5A248. */
REGION void tsl9_candidate_unprovided_flash_5a23e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a246:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a246\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a25a\n");
    __builtin_unreachable();
}

/* Original0x5A248..0x5A25A. */
REGION void tsl9_resident_transmit_state_helpers_block_5a248(void)
{
    REGS;
    a4 = UINT32_C(0x00000007); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002d)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A25A..0x5A25E. */
REGION void tsl9_resident_transmit_state_helpers_block_5a25a(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A25E..0x5A268. */
REGION void tsl9_candidate_unprovided_flash_5a25e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a266:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a266\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a282\n");
    __builtin_unreachable();
}

/* Original0x5A268..0x5A282. */
REGION void tsl9_resident_transmit_state_helpers_block_5a268(void)
{
    REGS;
    a4 = UINT32_C(0x0000000a); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000035); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A282..0x5A286. */
REGION void tsl9_resident_transmit_state_helpers_block_5a282(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A286..0x5A290. */
REGION void tsl9_candidate_unprovided_flash_5a286(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a28e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a28e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a29e\n");
    __builtin_unreachable();
}

/* Original0x5A290..0x5A29E. */
REGION void tsl9_resident_transmit_state_helpers_block_5a290(void)
{
    REGS;
    a4 = UINT32_C(0x0000000b); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = UINT32_C(0x00000037); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A29E..0x5A2A2. */
REGION void tsl9_resident_transmit_state_helpers_block_5a29e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A2A2..0x5A2D6. */
REGION void tsl9_candidate_unprovided_flash_5a2a2(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = UINT32_C(0x0000000c); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa33c\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    /* Conditional Xwchc: qk.c.lhu a3, 20(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bd6\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb334\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 22(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bf4\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa354\n.option pop\n");
    /* Conditional Xwchc: qk.c.lhu a3, 22(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2bf6\n.option pop\n");
    a3 = a3 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 5(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb354\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 24(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x2f94\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a3, 6(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa374\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 25(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x3f9c\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 7(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb37c\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002e)); LIVE;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a2d4:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_state_helpers_edge_5a2d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a2ec\n");
    __builtin_unreachable();
}

/* Original0x5A2D6..0x5A2DC. */
REGION void tsl9_resident_transmit_state_helpers_block_5a2d6(void)
{
    REGS;
    a5 = UINT32_C(0x0000003a); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A2DC..0x5A2EC. */
REGION void tsl9_resident_transmit_state_helpers_block_5a2dc(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002e)); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002e)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A2EC..0x5A2F0. */
REGION void tsl9_resident_transmit_state_helpers_block_5a2ec(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a2ee:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a2ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a2dc\n");
    __builtin_unreachable();
}

/* Original0x5A2F0..0x5A306. */
REGION void tsl9_resident_transmit_state_helpers_block_5a2f0(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002e)) = (uint8_t)0; LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x000000a0)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a304:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a304\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a2dc\n");
    __builtin_unreachable();
}

/* Original0x5A306..0x5A310. */
REGION void tsl9_candidate_unprovided_flash_5a306(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a30e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a30e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a322\n");
    __builtin_unreachable();
}

/* Original0x5A310..0x5A322. */
REGION void tsl9_resident_transmit_state_helpers_block_5a310(void)
{
    REGS;
    a4 = UINT32_C(0x0000000d); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A322..0x5A326. */
REGION void tsl9_resident_transmit_state_helpers_block_5a322(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A326..0x5A330. */
REGION void tsl9_candidate_unprovided_flash_5a326(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a32e:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a32e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a344\n");
    __builtin_unreachable();
}

/* Original0x5A330..0x5A344. */
REGION void tsl9_resident_transmit_state_helpers_block_5a330(void)
{
    REGS;
    a4 = UINT32_C(0x00000011); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002c)); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 3(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb3b8\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002b)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 4(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3d8\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A344..0x5A348. */
REGION void tsl9_resident_transmit_state_helpers_block_5a344(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A348..0x5A352. */
REGION void tsl9_candidate_unprovided_flash_5a348(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a350:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a350\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a36c\n");
    __builtin_unreachable();
}

/* Original0x5A352..0x5A36C. */
REGION void tsl9_resident_transmit_state_helpers_block_5a352(void)
{
    REGS;
    a4 = UINT32_C(0x00000012); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a5 = UINT32_C(0x0000004a); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A36C..0x5A370. */
REGION void tsl9_resident_transmit_state_helpers_block_5a36c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A370..0x5A37A. */
REGION void tsl9_candidate_unprovided_flash_5a370(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a378:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a378\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a382\n");
    __builtin_unreachable();
}

/* Original0x5A37A..0x5A382. */
REGION void tsl9_resident_transmit_state_helpers_block_5a37a(void)
{
    REGS;
    a4 = UINT32_C(0x00000013); LIVE;
    /* Conditional Xwchc: qk.c.sb a4, 2(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa3b8\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A382..0x5A386. */
REGION void tsl9_resident_transmit_state_helpers_block_5a382(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A386..0x5A3A6. */
REGION void tsl9_candidate_unprovided_flash_5a386(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = UINT32_C(0x00000016); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa33c\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000144)); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb334\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000145)); LIVE;
    a3 = a3 & UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa35c\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a3a4:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_state_helpers_edge_5a3a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a3ee\n");
    __builtin_unreachable();
}

/* Original0x5A3A6..0x5A3B0. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3a6(void)
{
    REGS;
    a3 = UINT32_C(0x0000034f); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a3ac:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_transmit_state_helpers_edge_5a3ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_state_helpers_block_5a3c6\n");
    __builtin_unreachable();
}

/* Original0x5A3B0..0x5A3BA. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3b0(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xfffffe88); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000148)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a3b8:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_state_helpers_edge_5a3b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a3ea\n");
    __builtin_unreachable();
}

/* Original0x5A3BA..0x5A3BC. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A3BC..0x5A3C2. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3bc(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A3C2..0x5A3C6. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3c2(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x5A3C6..0x5A3CE. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3c6(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e4)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a3ca:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_transmit_state_helpers_edge_5a3ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_state_helpers_block_5a3d0\n");
    __builtin_unreachable();
}

/* Original0x5A3CE..0x5A3D0. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3ce(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A3D0..0x5A3EA. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3d0(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004e)) = (uint8_t)a4; LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000055); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A3EA..0x5A3EE. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x3\n.option pop\n");
    PORT(".Lresident_transmit_state_helpers_edge_5a3ec:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a3ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a3bc\n");
    __builtin_unreachable();
}

/* Original0x5A3EE..0x5A3F2. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3ee(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a3f0:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a3f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a3fe\n");
    __builtin_unreachable();
}

/* Original0x5A3F2..0x5A3F8. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3f2(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xffffffb0); LIVE;
    a4 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x5A3F8..0x5A3FE. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    PORT(".Lresident_transmit_state_helpers_edge_5a3fc:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a3fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a3c2\n");
    __builtin_unreachable();
}

/* Original0x5A3FE..0x5A406. */
REGION void tsl9_resident_transmit_state_helpers_block_5a3fe(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xffffffbc); LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a404:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a404\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a3f8\n");
    __builtin_unreachable();
}

/* Original0x5A48E..0x5A4C6. */
REGION void tsl9_candidate_unprovided_flash_5a48e(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 21(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb95c\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000040)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000110)); LIVE;
    a3 = UINT32_C(0x00000018); LIVE;
    a5 = a5 + UINT32_C(0x00000008); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000014c)) = (uint16_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa334\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000014a)); LIVE;
    /* Conditional Xwchc: qk.c.sb a3, 3(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb334\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000014b)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000005)) = (uint8_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000006)) = (uint8_t)0; LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 4(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa350\n.option pop\n");
    a1 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000148)); LIVE;
    a2 = UINT32_C(0xffff0000); LIVE;
    a2 = a2 & a1; LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a4c4:\n.option push\n.option rvc\nc.beqz a2,.Lresident_transmit_state_helpers_edge_5a4c4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a4cc\n");
    __builtin_unreachable();
}

/* Original0x5A4C6..0x5A4CC. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4c6(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a5, 5(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb35c\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 6(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xa37c\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A4CC..0x5A4D6. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4cc(void)
{
    REGS;
    a5 = a3 & UINT32_C(0x00000004); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e6)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a4d4:\n.option push\n.option rvc\nc.beqz a5,.Lresident_transmit_state_helpers_edge_5a4d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a512\n");
    __builtin_unreachable();
}

/* Original0x5A4D6..0x5A4E0. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4d6(void)
{
    REGS;
    a3 = UINT32_C(0x0000034f); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a4dc:\n.option push\n.option norvc\nbleu a4,a3,.Lresident_transmit_state_helpers_edge_5a4dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_state_helpers_block_5a4f6\n");
    __builtin_unreachable();
}

/* Original0x5A4E0..0x5A4EA. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4e0(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xfffffe88); LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000148)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a4e8:\n.option push\n.option rvc\nc.beqz a4,.Lresident_transmit_state_helpers_edge_5a4e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a50e\n");
    __builtin_unreachable();
}

/* Original0x5A4EA..0x5A4EC. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A4EC..0x5A4F2. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4ec(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffd5); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A4F2..0x5A4F6. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4f2(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x5A4F6..0x5A4FE. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4f6(void)
{
    REGS;
    a4 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x000001e4)); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a4fa:\n.option push\n.option norvc\nbleu a4,a5,.Lresident_transmit_state_helpers_edge_5a4fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_transmit_state_helpers_block_5a500\n");
    __builtin_unreachable();
}

/* Original0x5A4FE..0x5A500. */
REGION void tsl9_resident_transmit_state_helpers_block_5a4fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a4, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A500..0x5A50E. */
REGION void tsl9_resident_transmit_state_helpers_block_5a500(void)
{
    REGS;
    a5 = UINT32_C(0x00000059); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000004e)) = (uint8_t)a4; LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 16(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa91c\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x5A50E..0x5A512. */
REGION void tsl9_resident_transmit_state_helpers_block_5a50e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x3\n.option pop\n");
    PORT(".Lresident_transmit_state_helpers_edge_5a510:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a510\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a4ec\n");
    __builtin_unreachable();
}

/* Original0x5A512..0x5A516. */
REGION void tsl9_resident_transmit_state_helpers_block_5a512(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a514:\n.option push\n.option rvc\nc.beqz a3,.Lresident_transmit_state_helpers_edge_5a514\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_transmit_state_helpers_block_5a522\n");
    __builtin_unreachable();
}

/* Original0x5A516..0x5A51C. */
REGION void tsl9_resident_transmit_state_helpers_block_5a516(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xffffffb0); LIVE;
    a4 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x5A51C..0x5A522. */
REGION void tsl9_resident_transmit_state_helpers_block_5a51c(void)
{
    REGS;
    PORT(".option push\n.option norvc\ndiv a5, a5, a4\n.option pop\n");
    PORT(".Lresident_transmit_state_helpers_edge_5a520:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a520\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a4f2\n");
    __builtin_unreachable();
}

/* Original0x5A522..0x5A52A. */
REGION void tsl9_resident_transmit_state_helpers_block_5a522(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xffffffbc); LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_transmit_state_helpers_edge_5a528:\n.option push\n.option rvc\nc.j .Lresident_transmit_state_helpers_edge_5a528\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_transmit_state_helpers_block_5a51c\n");
    __builtin_unreachable();
}
