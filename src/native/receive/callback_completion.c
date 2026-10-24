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

/* Five complete callback/input functions:444B/162i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x838E..0x83C6. */
REGION void tsl9_registered_callbacks_provider_838e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -80\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 44(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s5, a5, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s7, 0x20004\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s7, s7, 1016\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s4, 0x10\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 72(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 76(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 68(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 64(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s8, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi s4, s4, -2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s6, s7\n.option pop\n");
    PORT(".option push\n.option norvc\nor s5, s5, a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x83C6..0x83D6. */
REGION void tsl9_callback_completion_block_83c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli s2, s3, 0x2\n.option pop\n");
    PORT(".option push\n.option norvc\nadd a5, s7, s2\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    PORT(".Lcallback_completion_edge_83d2:\n.option push\n.option norvc\nbeq s4,a4,.Lcallback_completion_edge_83d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_8420\n");
    __builtin_unreachable();
}

/* Original0x83D6..0x83E0. */
REGION void tsl9_callback_completion_block_83d6(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcallback_completion_edge_83dc:\n.option push\n.option norvc\nbne a3,a4,.Lcallback_completion_edge_83dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_8420\n");
    __builtin_unreachable();
}

/* Original0x83E0..0x83EA. */
REGION void tsl9_callback_completion_block_83e0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s1, 4(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    PORT(".Lcallback_completion_edge_83e8:\n.option push\n.option rvc\nc.beqz s1,.Lcallback_completion_edge_83e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_8420\n");
    __builtin_unreachable();
}

/* Original0x83EA..0x83F2. */
REGION void tsl9_callback_completion_block_83ea(void)
{
    REGS;
    a4 = UINT32_C(0x0000001e); LIVE;
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    PORT(".Lcallback_completion_edge_83ee:\n.option push\n.option norvc\nbleu s0,a4,.Lcallback_completion_edge_83ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_83f4\n");
    __builtin_unreachable();
}

/* Original0x83F2..0x83F4. */
REGION void tsl9_callback_completion_block_83f2(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    __builtin_unreachable();
}

/* Original0x83F4..0x840C. */
REGION void tsl9_callback_completion_block_83f4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s0, a5, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s5, 0(sp)\n.option pop\n");
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s8\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, sp, 2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x840C..0x841E. */
REGION void tsl9_callback_completion_block_840c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s2, s2, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, s0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, sp\n.option pop\n");
    a1 = UINT32_C(0x000000c0); LIVE;
    PORT(".Lcallback_completion_edge_841c:\n.option push\n.option rvc\nc.jal .Lcallback_completion_edge_841c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_filter_external_8a56\n");
    __builtin_unreachable();
}

/* Original0x841E..0x8420. */
REGION void tsl9_callback_completion_block_841e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8420..0x8424. */
REGION void tsl9_callback_completion_block_8420(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_8420:\n.option push\n.option norvc\nbeqz s3,.Lcallback_completion_edge_8420\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_843c\n");
    __builtin_unreachable();
}

/* Original0x8424..0x843C. */
REGION void tsl9_callback_completion_block_8424(void)
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

/* Original0x843C..0x8440. */
REGION void tsl9_callback_completion_block_843c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    PORT(".Lcallback_completion_edge_843e:\n.option push\n.option rvc\nc.j .Lcallback_completion_edge_843e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_completion_block_83c6\n");
    __builtin_unreachable();
}

/* Original0xA38E..0xA3A0. */
REGION void tsl9_callback_completion_provider_a38e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 357(gp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s0, s0, -1\n.option pop\n");
    PORT(".Lcallback_completion_edge_a39c:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a39c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xA3A0..0xA3AC. */
REGION void tsl9_callback_completion_block_a3a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lcallback_completion_edge_a3a8:\n.option push\n.option norvc\nbltu a5,s0,.Lcallback_completion_edge_a3a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_a3b6\n");
    __builtin_unreachable();
}

/* Original0xA3AC..0xA3B0. */
REGION void tsl9_callback_completion_block_a3ac(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3ac:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a3ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_abf2\n");
    __builtin_unreachable();
}

/* Original0xA3B0..0xA3B2. */
REGION void tsl9_callback_completion_block_a3b0(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3b0:\n.option push\n.option rvc\nc.bnez a0,.Lcallback_completion_edge_a3b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a3c8\n");
    __builtin_unreachable();
}

/* Original0xA3B2..0xA3B6. */
REGION void tsl9_callback_completion_block_a3b2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".Lcallback_completion_edge_a3b4:\n.option push\n.option rvc\nc.j .Lcallback_completion_edge_a3b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_completion_block_a3bc\n");
    __builtin_unreachable();
}

/* Original0xA3B6..0xA3BA. */
REGION void tsl9_callback_completion_block_a3b6(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcallback_completion_edge_a3b8:\n.option push\n.option rvc\nc.bnez s1,.Lcallback_completion_edge_a3b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a3bc\n");
    __builtin_unreachable();
}

/* Original0xA3BA..0xA3BC. */
REGION void tsl9_callback_completion_block_a3ba(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xA3BC..0xA3C8. */
REGION void tsl9_callback_completion_block_a3bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA3C8..0xA3CA. */
REGION void tsl9_callback_completion_block_a3c8(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3c8:\n.option push\n.option rvc\nc.bnez s1,.Lcallback_completion_edge_a3c8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a3b2\n");
    __builtin_unreachable();
}

/* Original0xA3CA..0xA3CC. */
REGION void tsl9_callback_completion_block_a3ca(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3ca:\n.option push\n.option rvc\nc.j .Lcallback_completion_edge_a3ca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_completion_block_a3ba\n");
    __builtin_unreachable();
}

/* Original0xA3CC..0xA3D6. */
REGION void tsl9_record_helpers_provider_a3cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lcallback_completion_edge_a3d2:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a3d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xA3D6..0xA3E0. */
REGION void tsl9_callback_completion_block_a3d6(void)
{
    REGS;
    a5 = UINT32_C(0x00000022); LIVE;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".Lcallback_completion_edge_a3dc:\n.option push\n.option norvc\nbleu a0,a5,.Lcallback_completion_edge_a3dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_a3e8\n");
    __builtin_unreachable();
}

/* Original0xA3E0..0xA3E4. */
REGION void tsl9_callback_completion_block_a3e0(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3e0:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a3e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_completion_provider_10556\n");
    __builtin_unreachable();
}

/* Original0xA3E4..0xA3E8. */
REGION void tsl9_callback_completion_block_a3e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsltiu s0, a0, 61\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA3E8..0xA3EC. */
REGION void tsl9_callback_completion_block_a3e8(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3e8:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a3e8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_abf2\n");
    __builtin_unreachable();
}

/* Original0xA3EC..0xA3EE. */
REGION void tsl9_callback_completion_block_a3ec(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3ec:\n.option push\n.option rvc\nc.bnez a0,.Lcallback_completion_edge_a3ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a40a\n");
    __builtin_unreachable();
}

/* Original0xA3EE..0xA3F0. */
REGION void tsl9_callback_completion_block_a3ee(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3ee:\n.option push\n.option rvc\nc.beqz s0,.Lcallback_completion_edge_a3ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a414\n");
    __builtin_unreachable();
}

/* Original0xA3F0..0xA3FC. */
REGION void tsl9_callback_completion_block_a3f0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffadf)) = (uint8_t)a5; LIVE;
    PORT(".Lcallback_completion_edge_a3fa:\n.option push\n.option rvc\nc.jal .Lcallback_completion_edge_a3fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_completion_provider_a38e\n");
    __builtin_unreachable();
}

/* Original0xA3FC..0xA3FE. */
REGION void tsl9_callback_completion_block_a3fc(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a3fc:\n.option push\n.option rvc\nc.beqz a0,.Lcallback_completion_edge_a3fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_callback_completion_block_a46e\n");
    __builtin_unreachable();
}

/* Original0xA3FE..0xA40A. */
REGION void tsl9_callback_completion_block_a3fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcallback_completion_edge_a406:\n.option push\n.option norvc\njal zero,.Lcallback_completion_edge_a406\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0xA40A..0xA40E. */
REGION void tsl9_callback_completion_block_a40a(void)
{
    REGS;
    PORT(".Lcallback_completion_edge_a40a:\n.option push\n.option norvc\njal ra,.Lcallback_completion_edge_a40a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_completion_provider_ab5e\n");
    __builtin_unreachable();
}

/* Original0xA40E..0xA414. */
REGION void tsl9_callback_completion_block_a40e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lcallback_completion_edge_a410:\n.option push\n.option norvc\nbeq a0,a5,.Lcallback_completion_edge_a410\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_a3ee\n");
    __builtin_unreachable();
}

/* Original0xA414..0xA430. */
REGION void tsl9_callback_completion_block_a414(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffabe)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffab0)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lcallback_completion_edge_a42c:\n.option push\n.option norvc\nbleu a5,a4,.Lcallback_completion_edge_a42c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_completion_block_a454\n");
    __builtin_unreachable();
}

/* Original0xA430..0xA454. */
REGION void tsl9_callback_completion_block_a430(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffaa2)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa93)) = (uint8_t)a5; LIVE;
    PORT(".Lcallback_completion_literal_a446:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_completion_literal_a446\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcallback_completion_edge_a450:\n.option push\n.option norvc\njal zero,.Lcallback_completion_edge_a450\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA454..0xA46E. */
REGION void tsl9_callback_completion_block_a454(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000003e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lcallback_completion_literal_a460:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lcallback_completion_literal_a460\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lcallback_completion_edge_a46a:\n.option push\n.option norvc\njal zero,.Lcallback_completion_edge_a46a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA46E..0xA476. */
REGION void tsl9_callback_completion_block_a46e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAB5E..0xAB68. */
REGION void tsl9_callback_completion_provider_ab5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000038b)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10556..0x1056E. */
REGION void tsl9_callback_completion_provider_10556(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000140); LIVE;
    a5 = *(volatile int16_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a5, 0x1f\n.option pop\n");
    a5 = a5 ^ a0; LIVE;
    a0 = a5 - a0; LIVE;
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
