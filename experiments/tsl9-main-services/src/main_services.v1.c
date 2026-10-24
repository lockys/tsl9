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

/* Five complete original main service functions:974B/328i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9334..0x9342. */
REGION void tsl9_main_runtime_external_9334(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lmain_services_edge_9340:\n.option push\n.option rvc\nc.jal .Lmain_services_edge_9340\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_92ba\n");
    __builtin_unreachable();
}

/* Original0x9342..0x934E. */
REGION void tsl9_main_services_block_9342(void)
{
    REGS;
    a5 = UINT32_C(0x00006000); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffaa5); LIVE;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 12\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x934E..0x9362. */
REGION void tsl9_main_services_block_934e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a4, sp, s1\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".Lmain_services_edge_9360:\n.option push\n.option rvc\nc.jal .Lmain_services_edge_9360\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_services_provider_9290\n");
    __builtin_unreachable();
}

/* Original0x9362..0x9366. */
REGION void tsl9_main_services_block_9362(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".Lmain_services_edge_9364:\n.option push\n.option rvc\nc.jal .Lmain_services_edge_9364\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_services_provider_9290\n");
    __builtin_unreachable();
}

/* Original0x9366..0x936C. */
REGION void tsl9_main_services_block_9366(void)
{
    REGS;
    a1 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lmain_services_edge_936a:\n.option push\n.option rvc\nc.jal .Lmain_services_edge_936a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_services_provider_9290\n");
    __builtin_unreachable();
}

/* Original0x936C..0x9372. */
REGION void tsl9_main_services_block_936c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lmain_services_edge_936e:\n.option push\n.option norvc\nbne s1,s2,.Lmain_services_edge_936e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_services_block_934e\n");
    __builtin_unreachable();
}

/* Original0x9372..0x937E. */
REGION void tsl9_main_services_block_9372(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12506..0x12528. */
REGION void tsl9_main_runtime_external_12506(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s2, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -1342\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12528..0x1253C. */
REGION void tsl9_main_services_block_12528(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, -1342\n.option pop\n");
    a2 = UINT32_C(0x00000024); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1253C..0x12550. */
REGION void tsl9_main_services_block_1253c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, -2\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s3, 6(s2)\n.option pop\n");
    PORT(".Lmain_services_literal_12546:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_services_provider_119c8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_services_literal_12546\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12550..0x12560. */
REGION void tsl9_main_services_block_12550(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000050); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12560..0x1256A. */
REGION void tsl9_main_services_block_12560(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000006); LIVE;
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1256A..0x12576. */
REGION void tsl9_main_services_block_1256a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x000000a0); LIVE;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12576..0x12582. */
REGION void tsl9_main_services_block_12576(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 340(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000064); LIVE;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12582..0x125A8. */
REGION void tsl9_main_services_block_12582(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000b)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a1 = UINT32_C(0x00000004); LIVE;
    a0 = UINT32_C(0x0000040f); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x125A8..0x125B6. */
REGION void tsl9_main_services_block_125a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000408); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x125B6..0x125C6. */
REGION void tsl9_main_services_block_125b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 9\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000409); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x125C6..0x125D6. */
REGION void tsl9_main_services_block_125c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 10\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x0000040a); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x125D6..0x125E6. */
REGION void tsl9_main_services_block_125d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, sp, 11\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x0000040d); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x125E6..0x12608. */
REGION void tsl9_main_services_block_125e6(void)
{
    REGS;
    a5 = UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 12(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 24(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 196(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s3, 2(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s3, 14(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s3, 26(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12608..0x1261A. */
REGION void tsl9_main_services_block_12608(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 200(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, -1608\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1261A..0x12624. */
REGION void tsl9_main_services_block_1261a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 80(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 0(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12624..0x1262E. */
REGION void tsl9_main_services_block_12624(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1262E..0x1263C. */
REGION void tsl9_main_services_block_1262e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s0)\n.option pop\n");
    PORT(".Lmain_services_literal_12632:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_services_provider_11442\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_services_literal_12632\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1263C..0x1264E. */
REGION void tsl9_main_services_block_1263c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x14C8A..0x14CA6. */
REGION void tsl9_main_provider_14c8a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff8\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -1280\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x0000000a); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x14CA6..0x14CC8. */
REGION void tsl9_main_services_block_14ca6(void)
{
    REGS;
    a5 = UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 2(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 9(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x154A6..0x154BA. */
REGION void tsl9_main_provider_154a6(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000048)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000160); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x154BA..0x154BE. */
REGION void tsl9_main_services_block_154ba(void)
{
    REGS;
    PORT(".Lmain_services_edge_154ba:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_10c1e\n");
    __builtin_unreachable();
}

/* Original0x154BE..0x154C2. */
REGION void tsl9_main_services_block_154be(void)
{
    REGS;
    PORT(".Lmain_services_edge_154be:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_d272\n");
    __builtin_unreachable();
}

/* Original0x154C2..0x154C6. */
REGION void tsl9_main_services_block_154c2(void)
{
    REGS;
    PORT(".Lmain_services_edge_154c2:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_a37c\n");
    __builtin_unreachable();
}

/* Original0x154C6..0x154CA. */
REGION void tsl9_main_services_block_154c6(void)
{
    REGS;
    PORT(".Lmain_services_edge_154c6:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_b0fc\n");
    __builtin_unreachable();
}

/* Original0x154CA..0x154CE. */
REGION void tsl9_main_services_block_154ca(void)
{
    REGS;
    PORT(".Lmain_services_edge_154ca:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_d75a\n");
    __builtin_unreachable();
}

/* Original0x154CE..0x154D2. */
REGION void tsl9_main_services_block_154ce(void)
{
    REGS;
    PORT(".Lmain_services_edge_154ce:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_d196\n");
    __builtin_unreachable();
}

/* Original0x154D2..0x154D6. */
REGION void tsl9_main_services_block_154d2(void)
{
    REGS;
    PORT(".Lmain_services_edge_154d2:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_10158\n");
    __builtin_unreachable();
}

/* Original0x154D6..0x154DA. */
REGION void tsl9_main_services_block_154d6(void)
{
    REGS;
    PORT(".Lmain_services_edge_154d6:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_consumer_entry_c798\n");
    __builtin_unreachable();
}

/* Original0x154DA..0x154DE. */
REGION void tsl9_main_services_block_154da(void)
{
    REGS;
    PORT(".Lmain_services_edge_154da:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_10032\n");
    __builtin_unreachable();
}

/* Original0x154DE..0x154E2. */
REGION void tsl9_main_services_block_154de(void)
{
    REGS;
    PORT(".Lmain_services_edge_154de:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_d4f4\n");
    __builtin_unreachable();
}

/* Original0x154E2..0x154E6. */
REGION void tsl9_main_services_block_154e2(void)
{
    REGS;
    PORT(".Lmain_services_edge_154e2:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_b242\n");
    __builtin_unreachable();
}

/* Original0x154E6..0x154EA. */
REGION void tsl9_main_services_block_154e6(void)
{
    REGS;
    PORT(".Lmain_services_edge_154e6:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_b5e0\n");
    __builtin_unreachable();
}

/* Original0x154EA..0x154EE. */
REGION void tsl9_main_services_block_154ea(void)
{
    REGS;
    PORT(".Lmain_services_edge_154ea:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_e0a4\n");
    __builtin_unreachable();
}

/* Original0x154EE..0x154F2. */
REGION void tsl9_main_services_block_154ee(void)
{
    REGS;
    PORT(".Lmain_services_edge_154ee:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_ceaa\n");
    __builtin_unreachable();
}

/* Original0x154F2..0x154F6. */
REGION void tsl9_main_services_block_154f2(void)
{
    REGS;
    PORT(".Lmain_services_edge_154f2:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_d0ee\n");
    __builtin_unreachable();
}

/* Original0x154F6..0x154FA. */
REGION void tsl9_main_services_block_154f6(void)
{
    REGS;
    PORT(".Lmain_services_edge_154f6:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154f6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_f84a\n");
    __builtin_unreachable();
}

/* Original0x154FA..0x154FE. */
REGION void tsl9_main_services_block_154fa(void)
{
    REGS;
    PORT(".Lmain_services_edge_154fa:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_fb0c\n");
    __builtin_unreachable();
}

/* Original0x154FE..0x15502. */
REGION void tsl9_main_services_block_154fe(void)
{
    REGS;
    PORT(".Lmain_services_edge_154fe:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_154fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_fa50\n");
    __builtin_unreachable();
}

/* Original0x15502..0x15506. */
REGION void tsl9_main_services_block_15502(void)
{
    REGS;
    PORT(".Lmain_services_edge_15502:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_15502\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_ff44\n");
    __builtin_unreachable();
}

/* Original0x15506..0x1550A. */
REGION void tsl9_main_services_block_15506(void)
{
    REGS;
    PORT(".Lmain_services_edge_15506:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_15506\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_b0ba\n");
    __builtin_unreachable();
}

/* Original0x1550A..0x1550E. */
REGION void tsl9_main_services_block_1550a(void)
{
    REGS;
    PORT(".Lmain_services_edge_1550a:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1550a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_aa18\n");
    __builtin_unreachable();
}

/* Original0x1550E..0x15512. */
REGION void tsl9_main_services_block_1550e(void)
{
    REGS;
    PORT(".Lmain_services_edge_1550e:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1550e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_c3be\n");
    __builtin_unreachable();
}

/* Original0x15512..0x15516. */
REGION void tsl9_main_services_block_15512(void)
{
    REGS;
    PORT(".Lmain_services_edge_15512:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_15512\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_c67a\n");
    __builtin_unreachable();
}

/* Original0x15516..0x1551A. */
REGION void tsl9_main_services_block_15516(void)
{
    REGS;
    PORT(".Lmain_services_edge_15516:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_15516\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_d68a\n");
    __builtin_unreachable();
}

/* Original0x1551A..0x1551E. */
REGION void tsl9_main_services_block_1551a(void)
{
    REGS;
    PORT(".Lmain_services_edge_1551a:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1551a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_f0b0\n");
    __builtin_unreachable();
}

/* Original0x1551E..0x15522. */
REGION void tsl9_main_services_block_1551e(void)
{
    REGS;
    PORT(".Lmain_services_edge_1551e:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1551e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_10276\n");
    __builtin_unreachable();
}

/* Original0x15522..0x1552A. */
REGION void tsl9_main_services_block_15522(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lmain_services_edge_15526:\n.option push\n.option norvc\njal zero,.Lmain_services_edge_15526\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_18604\n");
    __builtin_unreachable();
}

/* Original0x17040..0x1705A. */
REGION void tsl9_main_provider_17040(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000168); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1705A..0x1706C. */
REGION void tsl9_main_services_block_1705a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 128(s1)\n.option pop\n");
    PORT(".Lmain_services_literal_1705e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_main_services_provider_16f00\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lmain_services_literal_1705e\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, gp, 363\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1706C..0x17082. */
REGION void tsl9_main_services_block_1706c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40011\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, -1024\n.option pop\n");
    a1 = UINT32_C(0x00000100); LIVE;
    PORT(".Lmain_services_edge_1707e:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1707e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x17082..0x170E8. */
REGION void tsl9_main_services_block_17082(void)
{
    REGS;
    a3 = UINT32_C(0x40001000); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff828)) = (uint16_t)0; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff81c)); LIVE;
    a2 = UINT32_C(0x007a1000); LIVE;
    a2 = a2 + UINT32_C(0x00000200); LIVE;
    a4 = a4 | UINT32_C(0x00000060); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff81c)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff820)); LIVE;
    a1 = UINT32_C(0x00000040); LIVE;
    a0 = UINT32_C(0x40011000); LIVE;
    a4 = a4 | UINT32_C(0x00000100); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff820)) = (uint16_t)a4; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x0000006c); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, -2048\n.option pop\n");
    PORT(".option push\n.option norvc\ndivu a4, a4, a2\n.option pop\n");
    a2 = UINT32_C(0x00000048); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a4 = a4 >> UINT32_C(0x00000010); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff82c)) = (uint16_t)a4; LIVE;
    a4 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff82c)); LIVE;
    a4 = a4 >> UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff83c)) = (uint16_t)a4; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff800)); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffff800)) = (uint16_t)a5; LIVE;
    PORT(".Lmain_services_edge_170e4:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_170e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x170E8..0x170F8. */
REGION void tsl9_main_services_block_170e8(void)
{
    REGS;
    a2 = UINT32_C(0x00000048); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    a0 = UINT32_C(0x40011000); LIVE;
    PORT(".Lmain_services_edge_170f4:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_170f4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x170F8..0x17108. */
REGION void tsl9_main_services_block_170f8(void)
{
    REGS;
    a1 = UINT32_C(0x00000006); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)0; LIVE;
    PORT(".Lmain_services_edge_17104:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17104\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_1904a\n");
    __builtin_unreachable();
}

/* Original0x17108..0x17116. */
REGION void tsl9_main_services_block_17108(void)
{
    REGS;
    a5 = UINT32_C(0x00000040); LIVE;
    a1 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    PORT(".Lmain_services_edge_17112:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17112\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_1904a\n");
    __builtin_unreachable();
}

/* Original0x17116..0x1712E. */
REGION void tsl9_main_services_block_17116(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 12\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x0000000c); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)a5; LIVE;
    PORT(".Lmain_services_edge_1712a:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1712a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_18e1c\n");
    __builtin_unreachable();
}

/* Original0x1712E..0x1713C. */
REGION void tsl9_main_services_block_1712e(void)
{
    REGS;
    a5 = UINT32_C(0x00000011); LIVE;
    PORT(".option push\n.option rvc\nsw a5, 16(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".Lmain_services_edge_17138:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17138\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x1713C..0x17146. */
REGION void tsl9_main_services_block_1713c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lmain_services_edge_17142:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17142\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x17146..0x17152. */
REGION void tsl9_main_services_block_17146(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x00000020); LIVE;
    PORT(".Lmain_services_edge_1714e:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1714e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x17152..0x17160. */
REGION void tsl9_main_services_block_17152(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a2 = UINT32_C(0x00000048); LIVE;
    a1 = UINT32_C(0x00000040); LIVE;
    PORT(".Lmain_services_edge_1715c:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_1715c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x17160..0x1716C. */
REGION void tsl9_main_services_block_17160(void)
{
    REGS;
    a2 = UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lmain_services_edge_17168:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17168\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x1716C..0x1719A. */
REGION void tsl9_main_services_block_1716c(void)
{
    REGS;
    a5 = UINT32_C(0x00000104); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000200); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint32_t)0; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000016)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 12\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x40013000); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint16_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint32_t)0; LIVE;
    PORT(".Lmain_services_edge_17196:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_17196\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_196c4\n");
    __builtin_unreachable();
}

/* Original0x1719A..0x171A4. */
REGION void tsl9_main_services_block_1719a(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x40013000); LIVE;
    PORT(".Lmain_services_edge_171a0:\n.option push\n.option norvc\njal ra,.Lmain_services_edge_171a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_1971e\n");
    __builtin_unreachable();
}

/* Original0x171A4..0x171AE. */
REGION void tsl9_main_services_block_171a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 80(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a0, 0(s2)\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x171AE..0x171BA. */
REGION void tsl9_main_services_block_171ae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
