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

/* Two complete original main initializers:522B/155i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x12D92..0x12DAE. */
REGION void tsl9_main_provider_12d92(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000180); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000294); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12DAE..0x12DC0. */
REGION void tsl9_main_initializers_block_12dae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    a2 = UINT32_C(0x000000e4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000402); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12DC0..0x12DD0. */
REGION void tsl9_main_initializers_block_12dc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40011\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, -2048\n.option pop\n");
    PORT(".Lmain_initializers_edge_12dcc:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_12dcc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x12DD0..0x12DE2. */
REGION void tsl9_main_initializers_block_12dd0(void)
{
    REGS;
    a1 = UINT32_C(0x00001000); LIVE;
    a2 = UINT32_C(0x00000048); LIVE;
    a1 = a1 + UINT32_C(0xfffff800); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, -2048\n.option pop\n");
    PORT(".Lmain_initializers_edge_12dde:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_12dde\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_gate_entry_9a24\n");
    __builtin_unreachable();
}

/* Original0x12DE2..0x12DEE. */
REGION void tsl9_main_initializers_block_12de2(void)
{
    REGS;
    a2 = UINT32_C(0x00000020); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, sp\n.option pop\n");
    PORT(".Lmain_initializers_edge_12dea:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_12dea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_tagged_external_8520\n");
    __builtin_unreachable();
}

/* Original0x12DEE..0x12E0C. */
REGION void tsl9_main_initializers_block_12dee(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000405); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint16_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x0000006c); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x07271000); LIVE;
    a5 = a5 + UINT32_C(0xfffffe00); LIVE;
    PORT(".Lmain_initializers_edge_12e08:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_12e08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_12e4c\n");
    __builtin_unreachable();
}

/* Original0x12E0C..0x12E18. */
REGION void tsl9_main_initializers_block_12e0c(void)
{
    REGS;
    a5 = UINT32_C(0x08954000); LIVE;
    a5 = a5 + UINT32_C(0x00000400); LIVE;
    PORT(".Lmain_initializers_edge_12e14:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_12e14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_12e50\n");
    __builtin_unreachable();
}

/* Original0x12E18..0x12E24. */
REGION void tsl9_main_initializers_block_12e18(void)
{
    REGS;
    a5 = UINT32_C(0x05b8e000); LIVE;
    a5 = a5 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lmain_initializers_edge_12e20:\n.option push\n.option norvc\nbne a4,a5,.Lmain_initializers_edge_12e20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_12e2a\n");
    __builtin_unreachable();
}

/* Original0x12E24..0x12E26. */
REGION void tsl9_main_initializers_block_12e24(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x12E26..0x12E2A. */
REGION void tsl9_main_initializers_block_12e26(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x12E2A..0x12E38. */
REGION void tsl9_main_initializers_block_12e2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x40006\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, sp\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s0, 1024\n.option pop\n");
    PORT(".Lmain_initializers_edge_12e34:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_12e34\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_18ab0\n");
    __builtin_unreachable();
}

/* Original0x12E38..0x12E4C. */
REGION void tsl9_main_initializers_block_12e38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1044(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsw a5, 1044(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12E4C..0x12E50. */
REGION void tsl9_main_initializers_block_12e4c(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lmain_initializers_edge_12e4e:\n.option push\n.option rvc\nc.j .Lmain_initializers_edge_12e4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_initializers_block_12e26\n");
    __builtin_unreachable();
}

/* Original0x12E50..0x12E54. */
REGION void tsl9_main_initializers_block_12e50(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lmain_initializers_edge_12e52:\n.option push\n.option rvc\nc.j .Lmain_initializers_edge_12e52\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_initializers_block_12e26\n");
    __builtin_unreachable();
}

/* Original0x131C2..0x131E2. */
REGION void tsl9_main_provider_131c2(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x08078000); LIVE;
    a2 = UINT32_C(0x00000070); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffffa00); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x000000c4); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x131E2..0x131F6. */
REGION void tsl9_main_initializers_block_131e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = a4 + UINT32_C(0x000000ba); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff9\n.option pop\n");
    a3 = a3 + UINT32_C(0x000000b6); LIVE;
    a2 = UINT32_C(0x0000005e); LIVE;
    __builtin_unreachable();
}

/* Original0x131F6..0x13204. */
REGION void tsl9_main_initializers_block_131f6(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 + UINT32_C(0xffffffe0); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lmain_initializers_edge_13200:\n.option push\n.option norvc\nbleu a5,a2,.Lmain_initializers_edge_13200\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_132fc\n");
    __builtin_unreachable();
}

/* Original0x13204..0x13208. */
REGION void tsl9_main_initializers_block_13204(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_13204:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_13204\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_1316a\n");
    __builtin_unreachable();
}

/* Original0x13208..0x13224. */
REGION void tsl9_main_initializers_block_13208(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = UINT32_C(0x08078000); LIVE;
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = a1 + UINT32_C(0xfffff900); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000027a); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13224..0x13234. */
REGION void tsl9_main_initializers_block_13224(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000036f)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lmain_initializers_edge_13230:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_13230\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_13238\n");
    __builtin_unreachable();
}

/* Original0x13234..0x13238. */
REGION void tsl9_main_initializers_block_13234(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_13234:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_13234\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12e86\n");
    __builtin_unreachable();
}

/* Original0x13238..0x13254. */
REGION void tsl9_main_initializers_block_13238(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = UINT32_C(0x08078000); LIVE;
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = a1 + UINT32_C(0xfffff800); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x000000c2); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13254..0x13264. */
REGION void tsl9_main_initializers_block_13254(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001b7)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lmain_initializers_edge_13260:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_13260\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_13268\n");
    __builtin_unreachable();
}

/* Original0x13264..0x13268. */
REGION void tsl9_main_initializers_block_13264(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_13264:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_13264\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12f18\n");
    __builtin_unreachable();
}

/* Original0x13268..0x13284. */
REGION void tsl9_main_initializers_block_13268(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = UINT32_C(0x08077000); LIVE;
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = a1 + UINT32_C(0x00000700); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000031a); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13284..0x13294. */
REGION void tsl9_main_initializers_block_13284(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000040f)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lmain_initializers_edge_13290:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_13290\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_13298\n");
    __builtin_unreachable();
}

/* Original0x13294..0x13298. */
REGION void tsl9_main_initializers_block_13294(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_13294:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_13294\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12f7a\n");
    __builtin_unreachable();
}

/* Original0x13298..0x132B4. */
REGION void tsl9_main_initializers_block_13298(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = UINT32_C(0x08077000); LIVE;
    a2 = UINT32_C(0x00000100); LIVE;
    a1 = a1 + UINT32_C(0x00000600); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x000003ea); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x132B4..0x132C4. */
REGION void tsl9_main_initializers_block_132b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004df)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lmain_initializers_edge_132c0:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_132c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_132c8\n");
    __builtin_unreachable();
}

/* Original0x132C4..0x132C8. */
REGION void tsl9_main_initializers_block_132c4(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_132c4:\n.option push\n.option norvc\njal ra,.Lmain_initializers_edge_132c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_13084\n");
    __builtin_unreachable();
}

/* Original0x132C8..0x132E4. */
REGION void tsl9_main_initializers_block_132c8(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = UINT32_C(0x08077000); LIVE;
    a2 = UINT32_C(0x00000085); LIVE;
    a1 = a1 + UINT32_C(0x00000500); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff9\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000132); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x132E4..0x132F4. */
REGION void tsl9_main_initializers_block_132e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001ac)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lmain_initializers_edge_132f0:\n.option push\n.option norvc\nbeq a4,a5,.Lmain_initializers_edge_132f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_13304\n");
    __builtin_unreachable();
}

/* Original0x132F4..0x132FC. */
REGION void tsl9_main_initializers_block_132f4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lmain_initializers_edge_132f8:\n.option push\n.option norvc\njal zero,.Lmain_initializers_edge_132f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_13108\n");
    __builtin_unreachable();
}

/* Original0x132FC..0x13302. */
REGION void tsl9_main_initializers_block_132fc(void)
{
    REGS;
    a4 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".Lmain_initializers_edge_132fe:\n.option push\n.option norvc\nbne a3,a4,.Lmain_initializers_edge_132fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_main_initializers_block_131f6\n");
    __builtin_unreachable();
}

/* Original0x13302..0x13304. */
REGION void tsl9_main_initializers_block_13302(void)
{
    REGS;
    PORT(".Lmain_initializers_edge_13302:\n.option push\n.option rvc\nc.j .Lmain_initializers_edge_13302\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_initializers_block_13208\n");
    __builtin_unreachable();
}

/* Original0x13304..0x1330A. */
REGION void tsl9_main_initializers_block_13304(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
