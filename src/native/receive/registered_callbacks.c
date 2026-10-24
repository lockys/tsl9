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

/* Three complete registered callback functions:3220B/1032i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x11442..0x11452. */
REGION void tsl9_main_services_provider_11442(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11450:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_11450\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1146e\n");
    __builtin_unreachable();
}

/* Original0x11452..0x11458. */
REGION void tsl9_registered_callbacks_block_11452(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11454:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11454\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_11356\n");
    __builtin_unreachable();
}

/* Original0x11458..0x11464. */
REGION void tsl9_registered_callbacks_block_11458(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb77)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x11464..0x1146E. */
REGION void tsl9_registered_callbacks_block_11464(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1146E..0x11474. */
REGION void tsl9_registered_callbacks_block_1146e(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11472:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_11472\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11480\n");
    __builtin_unreachable();
}

/* Original0x11474..0x1147A. */
REGION void tsl9_registered_callbacks_block_11474(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_edge_11476:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11476\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_11356\n");
    __builtin_unreachable();
}

/* Original0x1147A..0x11480. */
REGION void tsl9_registered_callbacks_block_1147a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1147e:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_1147e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11464\n");
    __builtin_unreachable();
}

/* Original0x11480..0x11486. */
REGION void tsl9_registered_callbacks_block_11480(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000010); LIVE;
    PORT(".Lregistered_callbacks_edge_11484:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_11484\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1149a\n");
    __builtin_unreachable();
}

/* Original0x11486..0x11494. */
REGION void tsl9_registered_callbacks_block_11486(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb46); LIVE;
    a1 = UINT32_C(0x00000007); LIVE;
    PORT(".Lregistered_callbacks_edge_11490:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11490\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_13cdc\n");
    __builtin_unreachable();
}

/* Original0x11494..0x1149A. */
REGION void tsl9_registered_callbacks_block_11494(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 16\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11498:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11498\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11464\n");
    __builtin_unreachable();
}

/* Original0x1149A..0x114A0. */
REGION void tsl9_registered_callbacks_block_1149a(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_1149e:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_1149e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_114c4\n");
    __builtin_unreachable();
}

/* Original0x114A0..0x114B0. */
REGION void tsl9_registered_callbacks_block_114a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a1 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffb28); LIVE;
    PORT(".Lregistered_callbacks_edge_114ac:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_114ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_13cdc\n");
    __builtin_unreachable();
}

/* Original0x114B0..0x114BE. */
REGION void tsl9_registered_callbacks_block_114b0(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x114BE..0x114C4. */
REGION void tsl9_registered_callbacks_block_114be(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 8\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_114c2:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_114c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11464\n");
    __builtin_unreachable();
}

/* Original0x114C4..0x114CC. */
REGION void tsl9_registered_callbacks_block_114c4(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000004); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_edge_114ca:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_114ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11464\n");
    __builtin_unreachable();
}

/* Original0x114CC..0x114E2. */
REGION void tsl9_registered_callbacks_block_114cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffafd)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffaff)) = (uint8_t)0; LIVE;
    a0 = a1 ^ UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_114e0:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_114e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11464\n");
    __builtin_unreachable();
}

/* Original0x119C8..0x119EE. */
REGION void tsl9_main_services_provider_119c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    a5 = a1 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s10, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_119ea:\n.option push\n.option norvc\nbgez a5,.Lregistered_callbacks_edge_119ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12292\n");
    __builtin_unreachable();
}

/* Original0x119EE..0x119F6. */
REGION void tsl9_registered_callbacks_block_119ee(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000006c)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x119F6..0x119FC. */
REGION void tsl9_registered_callbacks_block_119f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_119f8:\n.option push\n.option norvc\nbeqz a0,.Lregistered_callbacks_edge_119f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12428\n");
    __builtin_unreachable();
}

/* Original0x119FC..0x11A08. */
REGION void tsl9_registered_callbacks_block_119fc(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x000000b0); LIVE;
    PORT(".Lregistered_callbacks_edge_11a04:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11a04\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1241e\n");
    __builtin_unreachable();
}

/* Original0x11A08..0x11A20. */
REGION void tsl9_registered_callbacks_block_11a08(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x000005e2)); LIVE;
    PORT(".option push\n.option norvc\nauipc s2, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 1496\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11a1c:\n.option push\n.option norvc\nbeq a4,a5,.Lregistered_callbacks_edge_11a1c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1244a\n");
    __builtin_unreachable();
}

/* Original0x11A20..0x11A2C. */
REGION void tsl9_registered_callbacks_block_11a20(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x000005da)); LIVE;
    PORT(".Lregistered_callbacks_edge_11a28:\n.option push\n.option norvc\nbeq a4,a5,.Lregistered_callbacks_edge_11a28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1249c\n");
    __builtin_unreachable();
}

/* Original0x11A2C..0x11A38. */
REGION void tsl9_registered_callbacks_block_11a2c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x000005da)); LIVE;
    PORT(".Lregistered_callbacks_edge_11a34:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11a34\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11A38..0x11A40. */
REGION void tsl9_registered_callbacks_block_11a38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 2\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_11a3c:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11a3c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1244e\n");
    __builtin_unreachable();
}

/* Original0x11A40..0x11A58. */
REGION void tsl9_registered_callbacks_block_11a40(void)
{
    REGS;
    a4 = UINT32_C(0x0000000c); LIVE;
    a4 = a5 * a4; LIVE;
    PORT(".option push\n.option rvc\nli s7, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 129\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nadd s2, s2, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11A58..0x11A6E. */
REGION void tsl9_registered_callbacks_block_11a58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s7\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\naddi s6, s3, 60\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11A6E..0x11A72. */
REGION void tsl9_registered_callbacks_block_11a6e(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11a6e:\n.option push\n.option norvc\nbnez a0,.Lregistered_callbacks_edge_11a6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1238a\n");
    __builtin_unreachable();
}

/* Original0x11A72..0x11A7A. */
REGION void tsl9_registered_callbacks_block_11a72(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s7, s7, 43\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11a76:\n.option push\n.option norvc\nbne s7,s5,.Lregistered_callbacks_edge_11a76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11a58\n");
    __builtin_unreachable();
}

/* Original0x11A7A..0x11A88. */
REGION void tsl9_registered_callbacks_block_11a7a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = a5 + UINT32_C(0x0000055a); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lregistered_callbacks_edge_11a84:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11a84\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11A88..0x11A92. */
REGION void tsl9_registered_callbacks_block_11a88(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 380(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11A92..0x11A96. */
REGION void tsl9_registered_callbacks_block_11a92(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11a92:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11a92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11A96..0x11AA8. */
REGION void tsl9_registered_callbacks_block_11a96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11a9e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5b0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11a9e\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11AA8..0x11AAC. */
REGION void tsl9_registered_callbacks_block_11aa8(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11aa8:\n.option push\n.option norvc\nbnez a0,.Lregistered_callbacks_edge_11aa8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_123c4\n");
    __builtin_unreachable();
}

/* Original0x11AAC..0x11ABE. */
REGION void tsl9_registered_callbacks_block_11aac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000013); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11ab4:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5b8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11ab4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11ABE..0x11AC2. */
REGION void tsl9_registered_callbacks_block_11abe(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11abe:\n.option push\n.option norvc\nbeqz a0,.Lregistered_callbacks_edge_11abe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11bfe\n");
    __builtin_unreachable();
}

/* Original0x11AC2..0x11AC8. */
REGION void tsl9_registered_callbacks_block_11ac2(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lregistered_callbacks_edge_11ac4:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11ac4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11AC8..0x11AD4. */
REGION void tsl9_registered_callbacks_block_11ac8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000fc); LIVE;
    PORT(".Lregistered_callbacks_edge_11ad0:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11ad0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11AD4..0x11AE0. */
REGION void tsl9_registered_callbacks_block_11ad4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000ef); LIVE;
    PORT(".Lregistered_callbacks_edge_11adc:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11adc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11AE0..0x11AEC. */
REGION void tsl9_registered_callbacks_block_11ae0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 2(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000fe); LIVE;
    PORT(".Lregistered_callbacks_edge_11ae8:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11ae8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11AEC..0x11AF8. */
REGION void tsl9_registered_callbacks_block_11aec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000086); LIVE;
    PORT(".Lregistered_callbacks_edge_11af4:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11af4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11AF8..0x11B00. */
REGION void tsl9_registered_callbacks_block_11af8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11afc:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11afc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B00..0x11B0A. */
REGION void tsl9_registered_callbacks_block_11b00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11b06:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11b06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B0A..0x11B14. */
REGION void tsl9_registered_callbacks_block_11b0a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 6(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11b10:\n.option push\n.option norvc\nbne a3,a5,.Lregistered_callbacks_edge_11b10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B14..0x11B3E. */
REGION void tsl9_registered_callbacks_block_11b14(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a2, 8(s3)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 7(s3)\n.option pop\n");
    a4 = a4 + a2; LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 0(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".Lregistered_callbacks_edge_11b3a:\n.option push\n.option norvc\nbeqz a5,.Lregistered_callbacks_edge_11b3a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B3E..0x11B48. */
REGION void tsl9_registered_callbacks_block_11b3e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000495)); LIVE;
    PORT(".Lregistered_callbacks_edge_11b46:\n.option push\n.option rvc\nc.bnez a4,.Lregistered_callbacks_edge_11b46\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11b6e\n");
    __builtin_unreachable();
}

/* Original0x11B48..0x11B6E. */
REGION void tsl9_registered_callbacks_block_11b48(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000048b)) = (uint8_t)a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000047c)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000478)) = (uint16_t)0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000470)) = (uint8_t)0; LIVE;
    PORT(".Lregistered_callbacks_edge_11b6a:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11b6a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_11356\n");
    __builtin_unreachable();
}

/* Original0x11B6E..0x11B84. */
REGION void tsl9_registered_callbacks_block_11b6e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x000001e0); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000044e)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11B84..0x11B88. */
REGION void tsl9_registered_callbacks_block_11b84(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11b84:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11b84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B88..0x11B90. */
REGION void tsl9_registered_callbacks_block_11b88(void)
{
    REGS;
    a4 = UINT32_C(0x00000020); LIVE;
    PORT(".Lregistered_callbacks_edge_11b8c:\n.option push\n.option norvc\nbeq a5,a4,.Lregistered_callbacks_edge_11b8c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11be8\n");
    __builtin_unreachable();
}

/* Original0x11B90..0x11B98. */
REGION void tsl9_registered_callbacks_block_11b90(void)
{
    REGS;
    a4 = UINT32_C(0x00000021); LIVE;
    PORT(".Lregistered_callbacks_edge_11b94:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11b94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11B98..0x11BA0. */
REGION void tsl9_registered_callbacks_block_11b98(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000163)); LIVE;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_11b9e:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_11b9e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11ba2\n");
    __builtin_unreachable();
}

/* Original0x11BA0..0x11BA2. */
REGION void tsl9_registered_callbacks_block_11ba0(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x11BA2..0x11BAA. */
REGION void tsl9_registered_callbacks_block_11ba2(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lregistered_callbacks_edge_11ba6:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11ba6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x11BAA..0x11BAE. */
REGION void tsl9_registered_callbacks_block_11baa(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11baa:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11baa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11BAE..0x11BB2. */
REGION void tsl9_registered_callbacks_block_11bae(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11bae:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11bae\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_18110\n");
    __builtin_unreachable();
}

/* Original0x11BB2..0x11BB6. */
REGION void tsl9_registered_callbacks_block_11bb2(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11bb2:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11bb2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11BB6..0x11BC0. */
REGION void tsl9_registered_callbacks_block_11bb6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000163)); LIVE;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".Lregistered_callbacks_edge_11bbe:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_11bbe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11bc2\n");
    __builtin_unreachable();
}

/* Original0x11BC0..0x11BC2. */
REGION void tsl9_registered_callbacks_block_11bc0(void)
{
    REGS;
    a0 = UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x11BC2..0x11BCA. */
REGION void tsl9_registered_callbacks_block_11bc2(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lregistered_callbacks_edge_11bc6:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11bc6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x11BCA..0x11BCE. */
REGION void tsl9_registered_callbacks_block_11bca(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11bca:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11bca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11BCE..0x11BD8. */
REGION void tsl9_registered_callbacks_block_11bce(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000163)); LIVE;
    a0 = UINT32_C(0x00000080); LIVE;
    PORT(".Lregistered_callbacks_edge_11bd6:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_11bd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11bdc\n");
    __builtin_unreachable();
}

/* Original0x11BD8..0x11BDC. */
REGION void tsl9_registered_callbacks_block_11bd8(void)
{
    REGS;
    a0 = UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0x11BDC..0x11BE4. */
REGION void tsl9_registered_callbacks_block_11bdc(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lregistered_callbacks_edge_11be0:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11be0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x11BE4..0x11BE8. */
REGION void tsl9_registered_callbacks_block_11be4(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11be4:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11be4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11BE8..0x11BF0. */
REGION void tsl9_registered_callbacks_block_11be8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000163)); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_11bee:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_11bee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11bf2\n");
    __builtin_unreachable();
}

/* Original0x11BF0..0x11BF2. */
REGION void tsl9_registered_callbacks_block_11bf0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x11BF2..0x11BFA. */
REGION void tsl9_registered_callbacks_block_11bf2(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lregistered_callbacks_edge_11bf6:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_11bf6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x11BFA..0x11BFE. */
REGION void tsl9_registered_callbacks_block_11bfa(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11bfa:\n.option push\n.option norvc\njal zero,.Lregistered_callbacks_edge_11bfa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11BFE..0x11C10. */
REGION void tsl9_registered_callbacks_block_11bfe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11c06:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11c06\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11C10..0x11C12. */
REGION void tsl9_registered_callbacks_block_11c10(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11c10:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_11c10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11cc8\n");
    __builtin_unreachable();
}

/* Original0x11C12..0x11C18. */
REGION void tsl9_registered_callbacks_block_11c12(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_11c14:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11c14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C18..0x11C24. */
REGION void tsl9_registered_callbacks_block_11c18(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_11c20:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11c20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C24..0x11C2E. */
REGION void tsl9_registered_callbacks_block_11c24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_11c2a:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11c2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C2E..0x11C3A. */
REGION void tsl9_registered_callbacks_block_11c2e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 2(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".Lregistered_callbacks_edge_11c36:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11c36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C3A..0x11C44. */
REGION void tsl9_registered_callbacks_block_11c3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11c40:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11c40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C44..0x11C56. */
REGION void tsl9_registered_callbacks_block_11c44(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 3(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11C56..0x11C58. */
REGION void tsl9_registered_callbacks_block_11c56(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    __builtin_unreachable();
}

/* Original0x11C58..0x11C5E. */
REGION void tsl9_registered_callbacks_block_11c58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    __builtin_unreachable();
}

/* Original0x11C5E..0x11C64. */
REGION void tsl9_registered_callbacks_block_11c5e(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    PORT(".Lregistered_callbacks_edge_11c60:\n.option push\n.option norvc\nbeqz a5,.Lregistered_callbacks_edge_11c60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11C64..0x11C78. */
REGION void tsl9_registered_callbacks_block_11c64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffa\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000036f)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    a4 = a4 + UINT32_C(0x0000035c); LIVE;
    PORT(".Lregistered_callbacks_edge_11c74:\n.option push\n.option norvc\nbnez a3,.Lregistered_callbacks_edge_11c74\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12186\n");
    __builtin_unreachable();
}

/* Original0x11C78..0x11CB0. */
REGION void tsl9_registered_callbacks_block_11c78(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000359)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000034a)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000346)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000340)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x000001e0); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000322)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11CB0..0x11CC6. */
REGION void tsl9_registered_callbacks_block_11cb0(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000280); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000030c)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11CC6..0x11CC8. */
REGION void tsl9_registered_callbacks_block_11cc6(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11cc6:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11cc6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11CC8..0x11CDA. */
REGION void tsl9_registered_callbacks_block_11cc8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x0000000b); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11cd0:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5d4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11cd0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11CDA..0x11CDC. */
REGION void tsl9_registered_callbacks_block_11cda(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11cda:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_11cda\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11d26\n");
    __builtin_unreachable();
}

/* Original0x11CDC..0x11CE2. */
REGION void tsl9_registered_callbacks_block_11cdc(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_11cde:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11cde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11dce\n");
    __builtin_unreachable();
}

/* Original0x11CE2..0x11CEA. */
REGION void tsl9_registered_callbacks_block_11ce2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11ce6:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11ce6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11CEA..0x11CF2. */
REGION void tsl9_registered_callbacks_block_11cea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11cee:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11cee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11CF2..0x11CFA. */
REGION void tsl9_registered_callbacks_block_11cf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11cf6:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11cf6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11CFA..0x11D02. */
REGION void tsl9_registered_callbacks_block_11cfa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11cfe:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11cfe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D02..0x11D0A. */
REGION void tsl9_registered_callbacks_block_11d02(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11d06:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11d06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D0A..0x11D12. */
REGION void tsl9_registered_callbacks_block_11d0a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 7(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11d0e:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11d0e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D12..0x11D1E. */
REGION void tsl9_registered_callbacks_block_11d12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 2(s3)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 + a4; LIVE;
    __builtin_unreachable();
}

/* Original0x11D1E..0x11D26. */
REGION void tsl9_registered_callbacks_block_11d1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    PORT(".Lregistered_callbacks_edge_11d24:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11d24\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c56\n");
    __builtin_unreachable();
}

/* Original0x11D26..0x11D38. */
REGION void tsl9_registered_callbacks_block_11d26(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11d2e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5e0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11d2e\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11D38..0x11D3A. */
REGION void tsl9_registered_callbacks_block_11d38(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11d38:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_11d38\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11cdc\n");
    __builtin_unreachable();
}

/* Original0x11D3A..0x11D4C. */
REGION void tsl9_registered_callbacks_block_11d3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11d42:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5e8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11d42\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11D4C..0x11D4E. */
REGION void tsl9_registered_callbacks_block_11d4c(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11d4c:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_11d4c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11cdc\n");
    __builtin_unreachable();
}

/* Original0x11D4E..0x11D60. */
REGION void tsl9_registered_callbacks_block_11d4e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    a2 = UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11d56:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5f0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11d56\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11D60..0x11D62. */
REGION void tsl9_registered_callbacks_block_11d60(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11d60:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_11d60\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11cdc\n");
    __builtin_unreachable();
}

/* Original0x11D62..0x11D78. */
REGION void tsl9_registered_callbacks_block_11d62(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s6, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11d6e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a600\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11d6e\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11D78..0x11D7C. */
REGION void tsl9_registered_callbacks_block_11d78(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11d78:\n.option push\n.option norvc\nbeqz a0,.Lregistered_callbacks_edge_11d78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11ee4\n");
    __builtin_unreachable();
}

/* Original0x11D7C..0x11D82. */
REGION void tsl9_registered_callbacks_block_11d7c(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lregistered_callbacks_edge_11d7e:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11d7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11ec0\n");
    __builtin_unreachable();
}

/* Original0x11D82..0x11D8A. */
REGION void tsl9_registered_callbacks_block_11d82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11d86:\n.option push\n.option norvc\nbne a5,s4,.Lregistered_callbacks_edge_11d86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D8A..0x11D92. */
REGION void tsl9_registered_callbacks_block_11d8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11d8e:\n.option push\n.option norvc\nbne a5,s4,.Lregistered_callbacks_edge_11d8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D92..0x11D9C. */
REGION void tsl9_registered_callbacks_block_11d92(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 6(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11d98:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11d98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11D9C..0x11DA8. */
REGION void tsl9_registered_callbacks_block_11d9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a3 = UINT32_C(0x00000070); LIVE;
    PORT(".Lregistered_callbacks_edge_11da4:\n.option push\n.option norvc\nbne a5,a3,.Lregistered_callbacks_edge_11da4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e3e\n");
    __builtin_unreachable();
}

/* Original0x11DA8..0x11DB0. */
REGION void tsl9_registered_callbacks_block_11da8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11dac:\n.option push\n.option norvc\nbne a5,s4,.Lregistered_callbacks_edge_11dac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DB0..0x11DBC. */
REGION void tsl9_registered_callbacks_block_11db0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    a4 = UINT32_C(0x000000f4); LIVE;
    PORT(".Lregistered_callbacks_edge_11db8:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11db8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e78\n");
    __builtin_unreachable();
}

/* Original0x11DBC..0x11DC6. */
REGION void tsl9_registered_callbacks_block_11dbc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 5(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_11dc2:\n.option push\n.option norvc\nbne a3,a4,.Lregistered_callbacks_edge_11dc2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e78\n");
    __builtin_unreachable();
}

/* Original0x11DC6..0x11DCE. */
REGION void tsl9_registered_callbacks_block_11dc6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_11dcc:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11dcc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11d1e\n");
    __builtin_unreachable();
}

/* Original0x11DCE..0x11DD4. */
REGION void tsl9_registered_callbacks_block_11dce(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lregistered_callbacks_edge_11dd0:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11dd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e16\n");
    __builtin_unreachable();
}

/* Original0x11DD4..0x11DDC. */
REGION void tsl9_registered_callbacks_block_11dd4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 0(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11dd8:\n.option push\n.option norvc\nbeqz a3,.Lregistered_callbacks_edge_11dd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DDC..0x11DE4. */
REGION void tsl9_registered_callbacks_block_11ddc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11de0:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11de0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DE4..0x11DEC. */
REGION void tsl9_registered_callbacks_block_11de4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11de8:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11de8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DEC..0x11DF4. */
REGION void tsl9_registered_callbacks_block_11dec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11df0:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11df0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DF4..0x11DFC. */
REGION void tsl9_registered_callbacks_block_11df4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11df8:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11df8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11DFC..0x11E0C. */
REGION void tsl9_registered_callbacks_block_11dfc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + a3; LIVE;
    __builtin_unreachable();
}

/* Original0x11E0C..0x11E12. */
REGION void tsl9_registered_callbacks_block_11e0c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s2)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000018); LIVE;
    __builtin_unreachable();
}

/* Original0x11E12..0x11E16. */
REGION void tsl9_registered_callbacks_block_11e12(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    PORT(".Lregistered_callbacks_edge_11e14:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11e14\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c64\n");
    __builtin_unreachable();
}

/* Original0x11E16..0x11E1C. */
REGION void tsl9_registered_callbacks_block_11e16(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_11e18:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11e18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11E1C..0x11E24. */
REGION void tsl9_registered_callbacks_block_11e1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11e20:\n.option push\n.option norvc\nbltu s4,a2,.Lregistered_callbacks_edge_11e20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11E24..0x11E3E. */
REGION void tsl9_registered_callbacks_block_11e24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a4 = a4 + a2; LIVE;
    a5 = a5 + a3; LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_11e3c:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11e3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c56\n");
    __builtin_unreachable();
}

/* Original0x11E3E..0x11E46. */
REGION void tsl9_registered_callbacks_block_11e3e(void)
{
    REGS;
    a3 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lregistered_callbacks_edge_11e42:\n.option push\n.option norvc\nbne a5,a3,.Lregistered_callbacks_edge_11e42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_124be\n");
    __builtin_unreachable();
}

/* Original0x11E46..0x11E50. */
REGION void tsl9_registered_callbacks_block_11e46(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s3)\n.option pop\n");
    a5 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lregistered_callbacks_edge_11e4c:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11e4c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11E50..0x11E5C. */
REGION void tsl9_registered_callbacks_block_11e50(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000087); LIVE;
    PORT(".Lregistered_callbacks_edge_11e58:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11e58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11E5C..0x11E66. */
REGION void tsl9_registered_callbacks_block_11e5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_11e62:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11e62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11E66..0x11E78. */
REGION void tsl9_registered_callbacks_block_11e66(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11e76:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11e76\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e0c\n");
    __builtin_unreachable();
}

/* Original0x11E78..0x11E80. */
REGION void tsl9_registered_callbacks_block_11e78(void)
{
    REGS;
    a4 = UINT32_C(0x00000080); LIVE;
    PORT(".Lregistered_callbacks_edge_11e7c:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11e7c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e9c\n");
    __builtin_unreachable();
}

/* Original0x11E80..0x11E8A. */
REGION void tsl9_registered_callbacks_block_11e80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 5(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lregistered_callbacks_edge_11e86:\n.option push\n.option norvc\nbne a3,a4,.Lregistered_callbacks_edge_11e86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e9c\n");
    __builtin_unreachable();
}

/* Original0x11E8A..0x11E9C. */
REGION void tsl9_registered_callbacks_block_11e8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_11e9a:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11e9a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e0c\n");
    __builtin_unreachable();
}

/* Original0x11E9C..0x11EA4. */
REGION void tsl9_registered_callbacks_block_11e9c(void)
{
    REGS;
    a4 = UINT32_C(0x00000070); LIVE;
    PORT(".Lregistered_callbacks_edge_11ea0:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11ea0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11EA4..0x11EAE. */
REGION void tsl9_registered_callbacks_block_11ea4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lregistered_callbacks_edge_11eaa:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11eaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11EAE..0x11EC0. */
REGION void tsl9_registered_callbacks_block_11eae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_11ebe:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11ebe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e0c\n");
    __builtin_unreachable();
}

/* Original0x11EC0..0x11EC6. */
REGION void tsl9_registered_callbacks_block_11ec0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11ec2:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11ec2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11EC6..0x11ECE. */
REGION void tsl9_registered_callbacks_block_11ec6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0x11ECE..0x11ED2. */
REGION void tsl9_registered_callbacks_block_11ece(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11ece:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11ece\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11ED2..0x11EE4. */
REGION void tsl9_registered_callbacks_block_11ed2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000005); LIVE;
    PORT(".Lregistered_callbacks_edge_11ee2:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11ee2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e0c\n");
    __builtin_unreachable();
}

/* Original0x11EE4..0x11EF6. */
REGION void tsl9_registered_callbacks_block_11ee4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11eec:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a608\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11eec\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11EF6..0x11EF8. */
REGION void tsl9_registered_callbacks_block_11ef6(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11ef6:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_11ef6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_11fd8\n");
    __builtin_unreachable();
}

/* Original0x11EF8..0x11EFE. */
REGION void tsl9_registered_callbacks_block_11ef8(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lregistered_callbacks_edge_11efa:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11efa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f92\n");
    __builtin_unreachable();
}

/* Original0x11EFE..0x11F08. */
REGION void tsl9_registered_callbacks_block_11efe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11f04:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11f04\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11F08..0x11F18. */
REGION void tsl9_registered_callbacks_block_11f08(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s3)\n.option pop\n");
    a3 = UINT32_C(0x0000002c); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11f14:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11f14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f50\n");
    __builtin_unreachable();
}

/* Original0x11F18..0x11F1E. */
REGION void tsl9_registered_callbacks_block_11f18(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11f1a:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11f1a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11F1E..0x11F2E. */
REGION void tsl9_registered_callbacks_block_11f1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s3)\n.option pop\n");
    a3 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11f2a:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11f2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f32\n");
    __builtin_unreachable();
}

/* Original0x11F2E..0x11F32. */
REGION void tsl9_registered_callbacks_block_11f2e(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11f2e:\n.option push\n.option norvc\nbeqz a5,.Lregistered_callbacks_edge_11f2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11dc6\n");
    __builtin_unreachable();
}

/* Original0x11F32..0x11F3A. */
REGION void tsl9_registered_callbacks_block_11f32(void)
{
    REGS;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".Lregistered_callbacks_edge_11f36:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11f36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f40\n");
    __builtin_unreachable();
}

/* Original0x11F3A..0x11F40. */
REGION void tsl9_registered_callbacks_block_11f3a(void)
{
    REGS;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11f3c:\n.option push\n.option norvc\nbeq a5,a3,.Lregistered_callbacks_edge_11f3c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e8a\n");
    __builtin_unreachable();
}

/* Original0x11F40..0x11F48. */
REGION void tsl9_registered_callbacks_block_11f40(void)
{
    REGS;
    a3 = UINT32_C(0x000000f4); LIVE;
    PORT(".Lregistered_callbacks_edge_11f44:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11f44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f72\n");
    __builtin_unreachable();
}

/* Original0x11F48..0x11F4E. */
REGION void tsl9_registered_callbacks_block_11f48(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11f4a:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11f4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f72\n");
    __builtin_unreachable();
}

/* Original0x11F4E..0x11F50. */
REGION void tsl9_registered_callbacks_block_11f4e(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11f4e:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11f4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11eae\n");
    __builtin_unreachable();
}

/* Original0x11F50..0x11F58. */
REGION void tsl9_registered_callbacks_block_11f50(void)
{
    REGS;
    a3 = UINT32_C(0x00000090); LIVE;
    PORT(".Lregistered_callbacks_edge_11f54:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11f54\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_124f6\n");
    __builtin_unreachable();
}

/* Original0x11F58..0x11F5E. */
REGION void tsl9_registered_callbacks_block_11f58(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11f5a:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_11f5a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11F5E..0x11F6A. */
REGION void tsl9_registered_callbacks_block_11f5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 3(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000086); LIVE;
    PORT(".Lregistered_callbacks_edge_11f66:\n.option push\n.option norvc\nbne a3,a4,.Lregistered_callbacks_edge_11f66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f72\n");
    __builtin_unreachable();
}

/* Original0x11F6A..0x11F72. */
REGION void tsl9_registered_callbacks_block_11f6a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11f6e:\n.option push\n.option norvc\nbeq a4,a5,.Lregistered_callbacks_edge_11f6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11e66\n");
    __builtin_unreachable();
}

/* Original0x11F72..0x11F7A. */
REGION void tsl9_registered_callbacks_block_11f72(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11f78:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11f78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11ece\n");
    __builtin_unreachable();
}

/* Original0x11F7A..0x11F7E. */
REGION void tsl9_registered_callbacks_block_11f7a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11f7a:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11f7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_124fe\n");
    __builtin_unreachable();
}

/* Original0x11F7E..0x11F8A. */
REGION void tsl9_registered_callbacks_block_11f7e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000086); LIVE;
    PORT(".Lregistered_callbacks_edge_11f86:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_11f86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11F8A..0x11F92. */
REGION void tsl9_registered_callbacks_block_11f8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11f90:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11f90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_124e0\n");
    __builtin_unreachable();
}

/* Original0x11F92..0x11F98. */
REGION void tsl9_registered_callbacks_block_11f92(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11f94:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11f94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11F98..0x11FA0. */
REGION void tsl9_registered_callbacks_block_11f98(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_11f9c:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_11f9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11FA0..0x11FAA. */
REGION void tsl9_registered_callbacks_block_11fa0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_11fa6:\n.option push\n.option norvc\nbltu a3,a5,.Lregistered_callbacks_edge_11fa6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11FAA..0x11FB8. */
REGION void tsl9_registered_callbacks_block_11faa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s3)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a4 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_11fb4:\n.option push\n.option norvc\nbeqz a4,.Lregistered_callbacks_edge_11fb4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11FB8..0x11FBC. */
REGION void tsl9_registered_callbacks_block_11fb8(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11fb8:\n.option push\n.option norvc\nbne a4,a3,.Lregistered_callbacks_edge_11fb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11fc0\n");
    __builtin_unreachable();
}

/* Original0x11FBC..0x11FC0. */
REGION void tsl9_registered_callbacks_block_11fbc(void)
{
    REGS;
    a4 = UINT32_C(0x00000080); LIVE;
    __builtin_unreachable();
}

/* Original0x11FC0..0x11FD8. */
REGION void tsl9_registered_callbacks_block_11fc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s2)\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".Lregistered_callbacks_edge_11fd6:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_11fd6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e12\n");
    __builtin_unreachable();
}

/* Original0x11FD8..0x11FEA. */
REGION void tsl9_registered_callbacks_block_11fd8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_11fe0:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a614\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_11fe0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11FEA..0x11FEC. */
REGION void tsl9_registered_callbacks_block_11fea(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_11fea:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_11fea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_120aa\n");
    __builtin_unreachable();
}

/* Original0x11FEC..0x11FF2. */
REGION void tsl9_registered_callbacks_block_11fec(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_11fee:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_11fee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12020\n");
    __builtin_unreachable();
}

/* Original0x11FF2..0x11FFE. */
REGION void tsl9_registered_callbacks_block_11ff2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 0(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000020); LIVE;
    PORT(".Lregistered_callbacks_edge_11ffa:\n.option push\n.option norvc\nbltu a5,a3,.Lregistered_callbacks_edge_11ffa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x11FFE..0x12006. */
REGION void tsl9_registered_callbacks_block_11ffe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12002:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12002\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12006..0x1200E. */
REGION void tsl9_registered_callbacks_block_12006(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1200a:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_1200a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1200E..0x12020. */
REGION void tsl9_registered_callbacks_block_1200e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".Lregistered_callbacks_edge_1201e:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_1201e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c58\n");
    __builtin_unreachable();
}

/* Original0x12020..0x12026. */
REGION void tsl9_registered_callbacks_block_12020(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lregistered_callbacks_edge_12022:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_12022\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12026..0x1202E. */
REGION void tsl9_registered_callbacks_block_12026(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1202a:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_1202a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1202E..0x12046. */
REGION void tsl9_registered_callbacks_block_1202e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s5, gp, 332\n.option pop\n");
    PORT(".option push\n.option rvc\nli s4, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_12036:\n.option push\n.option norvc\nauipc s8,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a638\naddi s8,s8,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_12036\n.option pop\n");
    PORT(".option push\n.option rvc\nli s9, 6\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s10, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nli s7, 4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12046..0x12060. */
REGION void tsl9_registered_callbacks_block_12046(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli a1, s4, 0x1\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + a5; LIVE;
    PORT(".option push\n.option norvc\nmul a1, a1, s9\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s10)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a1, a1, s8\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12060..0x12062. */
REGION void tsl9_registered_callbacks_block_12060(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12060:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_12060\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1209c\n");
    __builtin_unreachable();
}

/* Original0x12062..0x1207A. */
REGION void tsl9_registered_callbacks_block_12062(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a4, s6, s4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    PORT(".Lregistered_callbacks_edge_12076:\n.option push\n.option norvc\nbleu a5,a3,.Lregistered_callbacks_edge_12076\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1207A..0x1209C. */
REGION void tsl9_registered_callbacks_block_1207a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, 128\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s2)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s4\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1209a:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_1209a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c64\n");
    __builtin_unreachable();
}

/* Original0x1209C..0x120A8. */
REGION void tsl9_registered_callbacks_block_1209c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s4, s4, 1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s5, s5, 1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_120a4:\n.option push\n.option norvc\nbne s4,s7,.Lregistered_callbacks_edge_120a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12046\n");
    __builtin_unreachable();
}

/* Original0x120A8..0x120AA. */
REGION void tsl9_registered_callbacks_block_120a8(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_120a8:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_120a8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120AA..0x120BC. */
REGION void tsl9_registered_callbacks_block_120aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_120b2:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a61c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_120b2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x120BC..0x120BE. */
REGION void tsl9_registered_callbacks_block_120bc(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_120bc:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_120bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12114\n");
    __builtin_unreachable();
}

/* Original0x120BE..0x120C4. */
REGION void tsl9_registered_callbacks_block_120be(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lregistered_callbacks_edge_120c0:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_120c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120C4..0x120CC. */
REGION void tsl9_registered_callbacks_block_120c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_120c8:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_120c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120CC..0x120D4. */
REGION void tsl9_registered_callbacks_block_120cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_120d0:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_120d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120D4..0x120DC. */
REGION void tsl9_registered_callbacks_block_120d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_120d8:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_120d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120DC..0x120E4. */
REGION void tsl9_registered_callbacks_block_120dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_120e0:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_120e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x120E4..0x120F0. */
REGION void tsl9_registered_callbacks_block_120e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_120ec:\n.option push\n.option norvc\nbeq a4,a5,.Lregistered_callbacks_edge_120ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_120f6\n");
    __builtin_unreachable();
}

/* Original0x120F0..0x120F6. */
REGION void tsl9_registered_callbacks_block_120f0(void)
{
    REGS;
    a4 = a4 << UINT32_C(0x00000004); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    __builtin_unreachable();
}

/* Original0x120F6..0x12114. */
REGION void tsl9_registered_callbacks_block_120f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s2)\n.option pop\n");
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a3, 0(s3)\n.option pop\n");
    a4 = a4 | a3; LIVE;
    PORT(".Lregistered_callbacks_edge_12112:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12112\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c5e\n");
    __builtin_unreachable();
}

/* Original0x12114..0x12126. */
REGION void tsl9_registered_callbacks_block_12114(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_1211c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a628\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_1211c\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12126..0x12128. */
REGION void tsl9_registered_callbacks_block_12126(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12126:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_12126\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_120be\n");
    __builtin_unreachable();
}

/* Original0x12128..0x1213A. */
REGION void tsl9_registered_callbacks_block_12128(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_12130:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a62c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_12130\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1213A..0x1213E. */
REGION void tsl9_registered_callbacks_block_1213a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_1213a:\n.option push\n.option norvc\nbeqz a0,.Lregistered_callbacks_edge_1213a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1213E..0x12144. */
REGION void tsl9_registered_callbacks_block_1213e(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_12140:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_12140\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12144..0x1214C. */
REGION void tsl9_registered_callbacks_block_12144(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12148:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12148\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1214C..0x12154. */
REGION void tsl9_registered_callbacks_block_1214c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12150:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12150\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12154..0x1215C. */
REGION void tsl9_registered_callbacks_block_12154(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12158:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12158\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1215C..0x12164. */
REGION void tsl9_registered_callbacks_block_1215c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12160:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12160\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12164..0x1216C. */
REGION void tsl9_registered_callbacks_block_12164(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12168:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12168\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1216C..0x12186. */
REGION void tsl9_registered_callbacks_block_1216c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a3, 2(s3)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 0(s3)\n.option pop\n");
    a4 = a4 | a3; LIVE;
    PORT(".Lregistered_callbacks_edge_12184:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12184\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11c56\n");
    __builtin_unreachable();
}

/* Original0x12186..0x1218C. */
REGION void tsl9_registered_callbacks_block_12186(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lregistered_callbacks_edge_12188:\n.option push\n.option norvc\nbne a3,a5,.Lregistered_callbacks_edge_12188\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11cb0\n");
    __builtin_unreachable();
}

/* Original0x1218C..0x12198. */
REGION void tsl9_registered_callbacks_block_1218c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000000a)); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_12194:\n.option push\n.option norvc\nbnez a5,.Lregistered_callbacks_edge_12194\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11cb0\n");
    __builtin_unreachable();
}

/* Original0x12198..0x121A8. */
REGION void tsl9_registered_callbacks_block_12198(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffe36)) = (uint8_t)a5; LIVE;
    PORT(".Lregistered_callbacks_edge_121a4:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_121a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_11356\n");
    __builtin_unreachable();
}

/* Original0x121A8..0x121BA. */
REGION void tsl9_registered_callbacks_block_121a8(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000005c)); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffe18)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x121BA..0x121BC. */
REGION void tsl9_registered_callbacks_block_121ba(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_121ba:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_121ba\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11cb0\n");
    __builtin_unreachable();
}

/* Original0x121BC..0x121C6. */
REGION void tsl9_registered_callbacks_block_121bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a3, 8(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_121c2:\n.option push\n.option norvc\nbne a3,a4,.Lregistered_callbacks_edge_121c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x121C6..0x121D4. */
REGION void tsl9_registered_callbacks_block_121c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 12(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000064); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lregistered_callbacks_edge_121d0:\n.option push\n.option norvc\nbltu a3,a4,.Lregistered_callbacks_edge_121d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x121D4..0x121E2. */
REGION void tsl9_registered_callbacks_block_121d4(void)
{
    REGS;
    a3 = UINT32_C(0x0000000c); LIVE;
    a5 = a5 * a3; LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s2\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a4; LIVE;
    PORT(".Lregistered_callbacks_edge_121e0:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_121e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x121E2..0x12208. */
REGION void tsl9_registered_callbacks_block_121e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffdf2); LIVE;
    PORT(".option push\n.option norvc\nlw a7, 8(a5)\n.option pop\n");
    a2 = UINT32_C(0x0000d000); LIVE;
    a5 = UINT32_C(0x00003000); LIVE;
    a1 = UINT32_C(0x00004000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\naddi t3, a5, -1511\n.option pop\n");
    a0 = a5 + UINT32_C(0xfffffa4d); LIVE;
    PORT(".option push\n.option rvc\nli a6, 9\n.option pop\n");
    a2 = a2 + UINT32_C(0xfffffe82); LIVE;
    a1 = a1 + UINT32_C(0x00000101); LIVE;
    __builtin_unreachable();
}

/* Original0x12208..0x1220C. */
REGION void tsl9_registered_callbacks_block_12208(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12208:\n.option push\n.option norvc\nbleu t1,a3,.Lregistered_callbacks_edge_12208\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12488\n");
    __builtin_unreachable();
}

/* Original0x1220C..0x1222A. */
REGION void tsl9_registered_callbacks_block_1220c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 10(s0)\n.option pop\n");
    a4 = a5 * a3; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 12(s0)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    PORT(".option push\n.option norvc\nlbu t4, 5(a5)\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nor a4, a4, t4\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12226:\n.option push\n.option norvc\nbeq a4,t3,.Lregistered_callbacks_edge_12226\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12262\n");
    __builtin_unreachable();
}

/* Original0x1222A..0x1222E. */
REGION void tsl9_registered_callbacks_block_1222a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_1222a:\n.option push\n.option norvc\nbeq a4,a0,.Lregistered_callbacks_edge_1222a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12236\n");
    __builtin_unreachable();
}

/* Original0x1222E..0x12232. */
REGION void tsl9_registered_callbacks_block_1222e(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_1222e:\n.option push\n.option norvc\nbeq a4,a2,.Lregistered_callbacks_edge_1222e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12236\n");
    __builtin_unreachable();
}

/* Original0x12232..0x12236. */
REGION void tsl9_registered_callbacks_block_12232(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12232:\n.option push\n.option norvc\nbne a4,a1,.Lregistered_callbacks_edge_12232\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x12236..0x12240. */
REGION void tsl9_registered_callbacks_block_12236(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lregistered_callbacks_edge_1223e:\n.option push\n.option rvc\nc.beqz a4,.Lregistered_callbacks_edge_1223e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x12240..0x12244. */
REGION void tsl9_registered_callbacks_block_12240(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12240:\n.option push\n.option norvc\nbeqz a7,.Lregistered_callbacks_edge_12240\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x12244..0x1224C. */
REGION void tsl9_registered_callbacks_block_12244(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 36(a7)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12248:\n.option push\n.option norvc\nbltu a6,a4,.Lregistered_callbacks_edge_12248\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x1224C..0x12262. */
REGION void tsl9_registered_callbacks_block_1224c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option norvc\naddi t4, a4, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nsb t4, 36(a7)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, a7\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000025)) = (uint8_t)a5; LIVE;
    PORT(".Lregistered_callbacks_edge_12260:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12260\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x12262..0x1226A. */
REGION void tsl9_registered_callbacks_block_12262(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_12268:\n.option push\n.option rvc\nc.beqz a4,.Lregistered_callbacks_edge_12268\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x1226A..0x1226E. */
REGION void tsl9_registered_callbacks_block_1226a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_1226a:\n.option push\n.option norvc\nbeqz a7,.Lregistered_callbacks_edge_1226a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_12276\n");
    __builtin_unreachable();
}

/* Original0x1226E..0x12276. */
REGION void tsl9_registered_callbacks_block_1226e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 34(a7)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12276..0x1227E. */
REGION void tsl9_registered_callbacks_block_12276(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lregistered_callbacks_edge_1227c:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_1227c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_12208\n");
    __builtin_unreachable();
}

/* Original0x1227E..0x12288. */
REGION void tsl9_registered_callbacks_block_1227e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 8(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000012); LIVE;
    PORT(".Lregistered_callbacks_edge_12284:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_12284\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12288..0x12290. */
REGION void tsl9_registered_callbacks_block_12288(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1228c:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_1228c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10eb2\n");
    __builtin_unreachable();
}

/* Original0x12290..0x12292. */
REGION void tsl9_registered_callbacks_block_12290(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12290:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12290\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12292..0x12298. */
REGION void tsl9_registered_callbacks_block_12292(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_12296:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_12296\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_122c8\n");
    __builtin_unreachable();
}

/* Original0x12298..0x122AA. */
REGION void tsl9_registered_callbacks_block_12298(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 436(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x122AA..0x122AC. */
REGION void tsl9_registered_callbacks_block_122aa(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_122aa:\n.option push\n.option rvc\nc.beqz a0,.Lregistered_callbacks_edge_122aa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_122be\n");
    __builtin_unreachable();
}

/* Original0x122AC..0x122B8. */
REGION void tsl9_registered_callbacks_block_122ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 88(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x122B8..0x122BE. */
REGION void tsl9_registered_callbacks_block_122b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a5, s1, 2\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_122bc:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_122bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x122BE..0x122C6. */
REGION void tsl9_registered_callbacks_block_122be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 92(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x122C6..0x122C8. */
REGION void tsl9_registered_callbacks_block_122c6(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_122c6:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_122c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_122b8\n");
    __builtin_unreachable();
}

/* Original0x122C8..0x122CE. */
REGION void tsl9_registered_callbacks_block_122c8(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_122cc:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_122cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_122de\n");
    __builtin_unreachable();
}

/* Original0x122CE..0x122D8. */
REGION void tsl9_registered_callbacks_block_122ce(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000019c)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x122D8..0x122DE. */
REGION void tsl9_registered_callbacks_block_122d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a5, s1, 4\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_122dc:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_122dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x122DE..0x122E4. */
REGION void tsl9_registered_callbacks_block_122de(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_122e2:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_122e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12312\n");
    __builtin_unreachable();
}

/* Original0x122E4..0x122EE. */
REGION void tsl9_registered_callbacks_block_122e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffcfd)); LIVE;
    PORT(".Lregistered_callbacks_edge_122ec:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_122ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1230c\n");
    __builtin_unreachable();
}

/* Original0x122EE..0x1230C. */
REGION void tsl9_registered_callbacks_block_122ee(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001bc)); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffa\n.option pop\n");
    a3 = a3 + UINT32_C(0xfffffced); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffa\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xfffffce4)); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1230C..0x12312. */
REGION void tsl9_registered_callbacks_block_1230c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a5, s1, 8\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12310:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12310\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x12312..0x12318. */
REGION void tsl9_registered_callbacks_block_12312(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000010); LIVE;
    PORT(".Lregistered_callbacks_edge_12316:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_12316\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12362\n");
    __builtin_unreachable();
}

/* Original0x12318..0x12326. */
REGION void tsl9_registered_callbacks_block_12318(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000017c)); LIVE;
    a0 = UINT32_C(0x00010000); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12326..0x12332. */
REGION void tsl9_registered_callbacks_block_12326(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffcae); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lregistered_callbacks_edge_12330:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_12330\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_12350\n");
    __builtin_unreachable();
}

/* Original0x12332..0x12336. */
REGION void tsl9_registered_callbacks_block_12332(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12332:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_12332\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x12336..0x1233C. */
REGION void tsl9_registered_callbacks_block_12336(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_12338:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_12338\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x1233C..0x12350. */
REGION void tsl9_registered_callbacks_block_1233c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_literal_12344:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_provider_9508\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_12344\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_1234c:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_1234c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x12350..0x1235C. */
REGION void tsl9_registered_callbacks_block_12350(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc90)) = (uint8_t)0; LIVE;
    PORT(".Lregistered_callbacks_edge_12358:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_12358\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x1235C..0x12362. */
REGION void tsl9_registered_callbacks_block_1235c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a5, s1, 16\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12360:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12360\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x12362..0x1236A. */
REGION void tsl9_registered_callbacks_block_12362(void)
{
    REGS;
    a4 = a1 & UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_edge_12368:\n.option push\n.option rvc\nc.beqz a4,.Lregistered_callbacks_edge_12368\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x1236A..0x12384. */
REGION void tsl9_registered_callbacks_block_1236a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000001b0)); LIVE;
    PORT(".Lregistered_callbacks_literal_12372:\n.option push\n.option norvc\nauipc a2,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a674\naddi a2,a2,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_12372\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_1237a:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a668\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_1237a\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12384..0x1238A. */
REGION void tsl9_registered_callbacks_block_12384(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a5, s1, 1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12388:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12388\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1242c\n");
    __builtin_unreachable();
}

/* Original0x1238A..0x123A8. */
REGION void tsl9_registered_callbacks_block_1238a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a0, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s3, 12(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s4, 10(s0)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lregistered_callbacks_edge_123a4:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_123a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_838e\n");
    __builtin_unreachable();
}

/* Original0x123A8..0x123AA. */
REGION void tsl9_registered_callbacks_block_123a8(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_123a8:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_123a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123AA..0x123C0. */
REGION void tsl9_registered_callbacks_block_123aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s5, s5, s7\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s6)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s5, s5, 9\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".Lregistered_callbacks_literal_123b6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_static_data_1a5a8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lregistered_callbacks_literal_123b6\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x123C0..0x123C4. */
REGION void tsl9_registered_callbacks_block_123c0(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_123c0:\n.option push\n.option norvc\nbeqz a0,.Lregistered_callbacks_edge_123c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11a96\n");
    __builtin_unreachable();
}

/* Original0x123C4..0x123CA. */
REGION void tsl9_registered_callbacks_block_123c4(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lregistered_callbacks_edge_123c6:\n.option push\n.option norvc\nbne s4,a5,.Lregistered_callbacks_edge_123c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123CA..0x123D0. */
REGION void tsl9_registered_callbacks_block_123ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 0(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123ce:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123ce\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123D0..0x123D6. */
REGION void tsl9_registered_callbacks_block_123d0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123d4:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123D6..0x123DC. */
REGION void tsl9_registered_callbacks_block_123d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123da:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123DC..0x123E2. */
REGION void tsl9_registered_callbacks_block_123dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123e0:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123E2..0x123E8. */
REGION void tsl9_registered_callbacks_block_123e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123e6:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123E8..0x123EE. */
REGION void tsl9_registered_callbacks_block_123e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123ec:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123EE..0x123F4. */
REGION void tsl9_registered_callbacks_block_123ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 7(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_123f2:\n.option push\n.option rvc\nc.bnez a5,.Lregistered_callbacks_edge_123f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x123F4..0x123FE. */
REGION void tsl9_registered_callbacks_block_123f4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lregistered_callbacks_edge_123fa:\n.option push\n.option norvc\nbeq a5,a4,.Lregistered_callbacks_edge_123fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11bce\n");
    __builtin_unreachable();
}

/* Original0x123FE..0x12402. */
REGION void tsl9_registered_callbacks_block_123fe(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_123fe:\n.option push\n.option norvc\nbltu a4,a5,.Lregistered_callbacks_edge_123fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11b88\n");
    __builtin_unreachable();
}

/* Original0x12402..0x12406. */
REGION void tsl9_registered_callbacks_block_12402(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12402:\n.option push\n.option norvc\nbeqz a5,.Lregistered_callbacks_edge_12402\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11bae\n");
    __builtin_unreachable();
}

/* Original0x12406..0x1240C. */
REGION void tsl9_registered_callbacks_block_12406(void)
{
    REGS;
    a4 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lregistered_callbacks_edge_12408:\n.option push\n.option norvc\nbeq a5,a4,.Lregistered_callbacks_edge_12408\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11bb6\n");
    __builtin_unreachable();
}

/* Original0x1240C..0x1241E. */
REGION void tsl9_registered_callbacks_block_1240c(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000012c)); LIVE;
    PORT(".option push\n.option norvc\nlbu a1, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 8\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1241E..0x12428. */
REGION void tsl9_registered_callbacks_block_1241e(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000068)); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12428..0x1242C. */
REGION void tsl9_registered_callbacks_block_12428(void)
{
    REGS;
    a5 = UINT32_C(0x00008000); LIVE;
    PORT(".option push\n.option rvc\nxor a5, a5, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1242C..0x1244A. */
REGION void tsl9_registered_callbacks_block_1242c(void)
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
    PORT(".option push\n.option rvc\nlw s9, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s10, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1244A..0x1244E. */
REGION void tsl9_registered_callbacks_block_1244a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1244E..0x12458. */
REGION void tsl9_registered_callbacks_block_1244e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s0)\n.option pop\n");
    a3 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lregistered_callbacks_edge_12454:\n.option push\n.option norvc\nbeq a4,a3,.Lregistered_callbacks_edge_12454\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_121bc\n");
    __builtin_unreachable();
}

/* Original0x12458..0x1245C. */
REGION void tsl9_registered_callbacks_block_12458(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12458:\n.option push\n.option norvc\nbltu a3,a4,.Lregistered_callbacks_edge_12458\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_124a2\n");
    __builtin_unreachable();
}

/* Original0x1245C..0x12462. */
REGION void tsl9_registered_callbacks_block_1245c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_1245e:\n.option push\n.option norvc\nbeq a4,a5,.Lregistered_callbacks_edge_1245e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1227e\n");
    __builtin_unreachable();
}

/* Original0x12462..0x12468. */
REGION void tsl9_registered_callbacks_block_12462(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lregistered_callbacks_edge_12464:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_12464\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12468..0x12480. */
REGION void tsl9_registered_callbacks_block_12468(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00002000); LIVE;
    a2 = a2 + UINT32_C(0xffffff40); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffa\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffb5e)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12480..0x12488. */
REGION void tsl9_registered_callbacks_block_12480(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu t1, 8(s0)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12484:\n.option push\n.option norvc\nbnez t1,.Lregistered_callbacks_edge_12484\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_121e2\n");
    __builtin_unreachable();
}

/* Original0x12488..0x12492. */
REGION void tsl9_registered_callbacks_block_12488(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 1(s0)\n.option pop\n");
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lregistered_callbacks_edge_1248e:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_1248e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x12492..0x1249A. */
REGION void tsl9_registered_callbacks_block_12492(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_12496:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_12496\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10eb2\n");
    __builtin_unreachable();
}

/* Original0x1249A..0x1249C. */
REGION void tsl9_registered_callbacks_block_1249a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_1249a:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_1249a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x1249C..0x124A2. */
REGION void tsl9_registered_callbacks_block_1249c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_124a0:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_124a0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1244e\n");
    __builtin_unreachable();
}

/* Original0x124A2..0x124A8. */
REGION void tsl9_registered_callbacks_block_124a2(void)
{
    REGS;
    a3 = UINT32_C(0x0000001b); LIVE;
    PORT(".Lregistered_callbacks_edge_124a4:\n.option push\n.option norvc\nbeq a4,a3,.Lregistered_callbacks_edge_124a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11a40\n");
    __builtin_unreachable();
}

/* Original0x124A8..0x124AE. */
REGION void tsl9_registered_callbacks_block_124a8(void)
{
    REGS;
    a3 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lregistered_callbacks_edge_124aa:\n.option push\n.option norvc\nbeq a4,a3,.Lregistered_callbacks_edge_124aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11a40\n");
    __builtin_unreachable();
}

/* Original0x124AE..0x124B4. */
REGION void tsl9_registered_callbacks_block_124ae(void)
{
    REGS;
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lregistered_callbacks_edge_124b0:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_124b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124B4..0x124BC. */
REGION void tsl9_registered_callbacks_block_124b4(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s3\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_124b8:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_124b8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10eb2\n");
    __builtin_unreachable();
}

/* Original0x124BC..0x124BE. */
REGION void tsl9_registered_callbacks_block_124bc(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_124bc:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_124bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124BE..0x124C6. */
REGION void tsl9_registered_callbacks_block_124be(void)
{
    REGS;
    a3 = UINT32_C(0x00000032); LIVE;
    PORT(".Lregistered_callbacks_edge_124c2:\n.option push\n.option norvc\nbne a5,a3,.Lregistered_callbacks_edge_124c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124C6..0x124CE. */
REGION void tsl9_registered_callbacks_block_124c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s3)\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_124ca:\n.option push\n.option norvc\nbne a5,a4,.Lregistered_callbacks_edge_124ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124CE..0x124DA. */
REGION void tsl9_registered_callbacks_block_124ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000087); LIVE;
    PORT(".Lregistered_callbacks_edge_124d6:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_124d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124DA..0x124E0. */
REGION void tsl9_registered_callbacks_block_124da(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s3)\n.option pop\n");
    a5 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x124E0..0x124E4. */
REGION void tsl9_registered_callbacks_block_124e0(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_124e0:\n.option push\n.option norvc\nbne a4,a5,.Lregistered_callbacks_edge_124e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x124E4..0x124F6. */
REGION void tsl9_registered_callbacks_block_124e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 1(s2)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a4 = a4 << UINT32_C(0x00000010); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 + UINT32_C(0x00000003); LIVE;
    PORT(".Lregistered_callbacks_edge_124f4:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_124f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_11e0c\n");
    __builtin_unreachable();
}

/* Original0x124F6..0x124FE. */
REGION void tsl9_registered_callbacks_block_124f6(void)
{
    REGS;
    a3 = UINT32_C(0x00000096); LIVE;
    PORT(".Lregistered_callbacks_edge_124fa:\n.option push\n.option norvc\nbeq a4,a3,.Lregistered_callbacks_edge_124fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f7a\n");
    __builtin_unreachable();
}

/* Original0x124FE..0x12504. */
REGION void tsl9_registered_callbacks_block_124fe(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_12500:\n.option push\n.option norvc\nbeq a5,a4,.Lregistered_callbacks_edge_12500\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_11f72\n");
    __builtin_unreachable();
}

/* Original0x12504..0x12506. */
REGION void tsl9_registered_callbacks_block_12504(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_12504:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_12504\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_1240c\n");
    __builtin_unreachable();
}

/* Original0x16F00..0x16F10. */
REGION void tsl9_main_services_provider_16f00(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_16f0e:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_16f0e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16f46\n");
    __builtin_unreachable();
}

/* Original0x16F10..0x16F20. */
REGION void tsl9_registered_callbacks_block_16f10(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000169)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_16f1c:\n.option push\n.option norvc\nbltu a4,a5,.Lregistered_callbacks_edge_16f1c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_16f32\n");
    __builtin_unreachable();
}

/* Original0x16F20..0x16F24. */
REGION void tsl9_registered_callbacks_block_16f20(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000169)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x16F24..0x16F28. */
REGION void tsl9_registered_callbacks_block_16f24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16F28..0x16F32. */
REGION void tsl9_registered_callbacks_block_16f28(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16F32..0x16F3C. */
REGION void tsl9_registered_callbacks_block_16f32(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000169)) = (uint8_t)0; LIVE;
    PORT(".Lregistered_callbacks_edge_16f38:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_16e88\n");
    __builtin_unreachable();
}

/* Original0x16F3C..0x16F3E. */
REGION void tsl9_registered_callbacks_block_16f3c(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f3c:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_16f3c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16f24\n");
    __builtin_unreachable();
}

/* Original0x16F3E..0x16F44. */
REGION void tsl9_registered_callbacks_block_16f3e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_16f40:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f40\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_16dd4\n");
    __builtin_unreachable();
}

/* Original0x16F44..0x16F46. */
REGION void tsl9_registered_callbacks_block_16f44(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f44:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_16f44\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_16f24\n");
    __builtin_unreachable();
}

/* Original0x16F46..0x16F4C. */
REGION void tsl9_registered_callbacks_block_16f46(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000004); LIVE;
    PORT(".Lregistered_callbacks_edge_16f4a:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_16f4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16f7a\n");
    __builtin_unreachable();
}

/* Original0x16F4C..0x16F5C. */
REGION void tsl9_registered_callbacks_block_16f4c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016a)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_16f58:\n.option push\n.option norvc\nbltu a4,a5,.Lregistered_callbacks_edge_16f58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_registered_callbacks_block_16f66\n");
    __builtin_unreachable();
}

/* Original0x16F5C..0x16F60. */
REGION void tsl9_registered_callbacks_block_16f5c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016a)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x16F60..0x16F66. */
REGION void tsl9_registered_callbacks_block_16f60(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 4\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_16f64:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_16f64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_16f28\n");
    __builtin_unreachable();
}

/* Original0x16F66..0x16F70. */
REGION void tsl9_registered_callbacks_block_16f66(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016a)) = (uint8_t)0; LIVE;
    PORT(".Lregistered_callbacks_edge_16f6c:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f6c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_16e88\n");
    __builtin_unreachable();
}

/* Original0x16F70..0x16F72. */
REGION void tsl9_registered_callbacks_block_16f70(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f70:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_16f70\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16f60\n");
    __builtin_unreachable();
}

/* Original0x16F72..0x16F78. */
REGION void tsl9_registered_callbacks_block_16f72(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_16f74:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_16dd4\n");
    __builtin_unreachable();
}

/* Original0x16F78..0x16F7A. */
REGION void tsl9_registered_callbacks_block_16f78(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f78:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_16f78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_16f60\n");
    __builtin_unreachable();
}

/* Original0x16F7A..0x16F84. */
REGION void tsl9_registered_callbacks_block_16f7a(void)
{
    REGS;
    a5 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_edge_16f82:\n.option push\n.option rvc\nc.beqz a5,.Lregistered_callbacks_edge_16f82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16f28\n");
    __builtin_unreachable();
}

/* Original0x16F84..0x16F8A. */
REGION void tsl9_registered_callbacks_block_16f84(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lregistered_callbacks_edge_16f86:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_16e88\n");
    __builtin_unreachable();
}

/* Original0x16F8A..0x16F8C. */
REGION void tsl9_registered_callbacks_block_16f8a(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f8a:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_16f8a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16fa4\n");
    __builtin_unreachable();
}

/* Original0x16F8C..0x16F92. */
REGION void tsl9_registered_callbacks_block_16f8c(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lregistered_callbacks_edge_16f8e:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f8e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_16e88\n");
    __builtin_unreachable();
}

/* Original0x16F92..0x16F94. */
REGION void tsl9_registered_callbacks_block_16f92(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f92:\n.option push\n.option rvc\nc.bnez a0,.Lregistered_callbacks_edge_16f92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_registered_callbacks_block_16fa4\n");
    __builtin_unreachable();
}

/* Original0x16F94..0x16F98. */
REGION void tsl9_registered_callbacks_block_16f94(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16f94:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_9af0\n");
    __builtin_unreachable();
}

/* Original0x16F98..0x16F9E. */
REGION void tsl9_registered_callbacks_block_16f98(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lregistered_callbacks_edge_16f9a:\n.option push\n.option norvc\njal ra,.Lregistered_callbacks_edge_16f9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_12b24\n");
    __builtin_unreachable();
}

/* Original0x16F9E..0x16FA4. */
REGION void tsl9_registered_callbacks_block_16f9e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori a0, s0, 1\n.option pop\n");
    PORT(".Lregistered_callbacks_edge_16fa2:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_16fa2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_16f28\n");
    __builtin_unreachable();
}

/* Original0x16FA4..0x16FB4. */
REGION void tsl9_registered_callbacks_block_16fa4(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00000030); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16FB4..0x16FB6. */
REGION void tsl9_registered_callbacks_block_16fb4(void)
{
    REGS;
    PORT(".Lregistered_callbacks_edge_16fb4:\n.option push\n.option rvc\nc.j .Lregistered_callbacks_edge_16fb4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_registered_callbacks_block_16f9e\n");
    __builtin_unreachable();
}
