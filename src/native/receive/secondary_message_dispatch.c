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

/* Nine complete candidate bodies:2048B/690i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x1264E..0x12658. */
REGION void tsl9_secondary_message_dispatch_entry_1264e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff992)) = (uint8_t)a1; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12656:\n.option push\n.option rvc\nc.beqz a0,.Lsecondary_message_dispatch_edge_12656\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_1265c\n");
    __builtin_unreachable();
}

/* Original0x12658..0x1265C. */
REGION void tsl9_secondary_message_dispatch_block_12658(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_12658:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_12658\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x1265C..0x12660. */
REGION void tsl9_secondary_message_dispatch_block_1265c(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1265c:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_1265c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_11252\n");
    __builtin_unreachable();
}

/* Original0x12660..0x12674. */
REGION void tsl9_secondary_message_dispatch_entry_12660(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, -1672(a5)\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_12670:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_12670\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x12674..0x126A0. */
REGION void tsl9_secondary_message_dispatch_block_12674(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff954); LIVE;
    PORT(".option push\n.option norvc\nsb s0, 1(a5)\n.option pop\n");
    a4 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 88(a4)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000b)) = (uint8_t)0; LIVE;
    a2 = UINT32_C(0x00008000); LIVE;
    a2 = a2 + UINT32_C(0xfffffd00); LIVE;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x126A0..0x126B8. */
REGION void tsl9_secondary_message_dispatch_entry_126a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff93a)) = (uint16_t)a0; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000006); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_126b4:\n.option push\n.option norvc\nbltu a4,a5,.Lsecondary_message_dispatch_edge_126b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_128fc\n");
    __builtin_unreachable();
}

/* Original0x126B8..0x126E8. */
REGION void tsl9_secondary_message_dispatch_block_126b8(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_literal_126b8:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_secondary_message_dispatch_static_data_1a58c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_126b8\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a2 = a2 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nslli s1, a2, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option norvc\naddi s3, a1, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nsrli s1, s1, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x126E8..0x126EC. */
REGION void tsl9_secondary_message_dispatch_block_126e8(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_126e8:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_126e8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x126EC..0x126F6. */
REGION void tsl9_secondary_message_dispatch_block_126ec(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8ea)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x126F6..0x12712. */
REGION void tsl9_secondary_message_dispatch_block_126f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8dc)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1270e:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_1270e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x12712..0x12716. */
REGION void tsl9_secondary_message_dispatch_block_12712(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_12712:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_12712\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x12716..0x1272A. */
REGION void tsl9_secondary_message_dispatch_block_12716(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8c2)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8c2)) = (uint8_t)0; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12726:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_12726\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_11252\n");
    __builtin_unreachable();
}

/* Original0x1272A..0x1273E. */
REGION void tsl9_secondary_message_dispatch_block_1272a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1273a:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_1273a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_central_event_callbacks_entry_110f8\n");
    __builtin_unreachable();
}

/* Original0x1273E..0x12742. */
REGION void tsl9_secondary_message_dispatch_block_1273e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1273e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1273e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x12742..0x12754. */
REGION void tsl9_secondary_message_dispatch_block_12742(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffa\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff896)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12750:\n.option push\n.option norvc\nbne s1,a5,.Lsecondary_message_dispatch_edge_12750\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_128ca\n");
    __builtin_unreachable();
}

/* Original0x12754..0x12762. */
REGION void tsl9_secondary_message_dispatch_block_12754(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s5, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s4, 129\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12762..0x12772. */
REGION void tsl9_secondary_message_dispatch_block_12762(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 64(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s2\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12772..0x12776. */
REGION void tsl9_secondary_message_dispatch_block_12772(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_12772:\n.option push\n.option norvc\nbnez a0,.Lsecondary_message_dispatch_edge_12772\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_128dc\n");
    __builtin_unreachable();
}

/* Original0x12776..0x1277E. */
REGION void tsl9_secondary_message_dispatch_block_12776(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s2, 43\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1277a:\n.option push\n.option norvc\nbne s2,s4,.Lsecondary_message_dispatch_edge_1277a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_12762\n");
    __builtin_unreachable();
}

/* Original0x1277E..0x12782. */
REGION void tsl9_secondary_message_dispatch_block_1277e(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12780:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_12780\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_128e8\n");
    __builtin_unreachable();
}

/* Original0x12782..0x12790. */
REGION void tsl9_secondary_message_dispatch_block_12782(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s3\n.option pop\n");
    a1 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x00000417); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12790..0x127A0. */
REGION void tsl9_secondary_message_dispatch_block_12790(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 112(s1)\n.option pop\n");
    a0 = UINT32_C(0x00000030); LIVE;
    PORT(".option push\n.option norvc\nauipc s2, 0x1fffa\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -1986\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x127A0..0x127AC. */
REGION void tsl9_secondary_message_dispatch_block_127a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffa\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xfffff83c)) = (uint32_t)a0; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_127a8:\n.option push\n.option norvc\nbeqz a0,.Lsecondary_message_dispatch_edge_127a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_128ca\n");
    __builtin_unreachable();
}

/* Original0x127AC..0x127B6. */
REGION void tsl9_secondary_message_dispatch_block_127ac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 72(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000030); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x127B6..0x127D4. */
REGION void tsl9_secondary_message_dispatch_block_127b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 8(s2)\n.option pop\n");
    a5 = UINT32_C(0xfffffffe); LIVE;
    a2 = UINT32_C(0x00000006); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000020)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, s0, 2\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xffffffff)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 76(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x127D4..0x127E4. */
REGION void tsl9_secondary_message_dispatch_block_127d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 8(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 76(s1)\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option norvc\naddi a1, s0, 8\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x127E4..0x127EA. */
REGION void tsl9_secondary_message_dispatch_block_127e4(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_127e6:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_127e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x127EA..0x127EE. */
REGION void tsl9_secondary_message_dispatch_block_127ea(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_127ec:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_127ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_126f6\n");
    __builtin_unreachable();
}

/* Original0x127EE..0x127F2. */
REGION void tsl9_secondary_message_dispatch_block_127ee(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_127ee:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_127ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x127F2..0x12804. */
REGION void tsl9_secondary_message_dispatch_block_127f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007e6)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12800:\n.option push\n.option norvc\nbne s1,a5,.Lsecondary_message_dispatch_edge_12800\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_128ca\n");
    __builtin_unreachable();
}

/* Original0x12804..0x12814. */
REGION void tsl9_secondary_message_dispatch_block_12804(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s2, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 129\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12814..0x12826. */
REGION void tsl9_secondary_message_dispatch_block_12814(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12826..0x12828. */
REGION void tsl9_secondary_message_dispatch_block_12826(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_12826:\n.option push\n.option rvc\nc.beqz a0,.Lsecondary_message_dispatch_edge_12826\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_128c2\n");
    __builtin_unreachable();
}

/* Original0x12828..0x12836. */
REGION void tsl9_secondary_message_dispatch_block_12828(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 360(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, s3\n.option pop\n");
    a1 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x00000417); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12836..0x1284A. */
REGION void tsl9_secondary_message_dispatch_block_12836(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 72(s2)\n.option pop\n");
    a2 = UINT32_C(0x0000002b); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nlui s2, 0x10\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1284A..0x12856. */
REGION void tsl9_secondary_message_dispatch_block_1284a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s1, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 1954\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_12852:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_12852\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_130d6\n");
    __builtin_unreachable();
}

/* Original0x12856..0x12864. */
REGION void tsl9_secondary_message_dispatch_block_12856(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s4, 0x1fff9\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s4, 1978\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s2, s2, -2\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s3, 0x40\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12864..0x1286C. */
REGION void tsl9_secondary_message_dispatch_block_12864(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 2(s1)\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_12868:\n.option push\n.option norvc\nbeq a5,s2,.Lsecondary_message_dispatch_edge_12868\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_12886\n");
    __builtin_unreachable();
}

/* Original0x1286C..0x1287A. */
REGION void tsl9_secondary_message_dispatch_block_1286c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 60(s3)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1287A..0x1287C. */
REGION void tsl9_secondary_message_dispatch_block_1287a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1287a:\n.option push\n.option rvc\nc.beqz a0,.Lsecondary_message_dispatch_edge_1287a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_12886\n");
    __builtin_unreachable();
}

/* Original0x1287C..0x12886. */
REGION void tsl9_secondary_message_dispatch_block_1287c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 380(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12886..0x1288C. */
REGION void tsl9_secondary_message_dispatch_block_12886(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, 12\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_12888:\n.option push\n.option norvc\nbne s4,s1,.Lsecondary_message_dispatch_edge_12888\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_12864\n");
    __builtin_unreachable();
}

/* Original0x1288C..0x12898. */
REGION void tsl9_secondary_message_dispatch_block_1288c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff9\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000754)) = (uint8_t)0; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_12894:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_12894\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10dcc\n");
    __builtin_unreachable();
}

/* Original0x12898..0x1289E. */
REGION void tsl9_secondary_message_dispatch_block_12898(void)
{
    REGS;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1289a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1289a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x1289E..0x128C2. */
REGION void tsl9_secondary_message_dispatch_block_1289e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_128b4:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_960e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_128b4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_128be:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_128be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x128C2..0x128CA. */
REGION void tsl9_secondary_message_dispatch_block_128c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, s1, 43\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_128c6:\n.option push\n.option norvc\nbne s1,s5,.Lsecondary_message_dispatch_edge_128c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_12814\n");
    __builtin_unreachable();
}

/* Original0x128CA..0x128DC. */
REGION void tsl9_secondary_message_dispatch_block_128ca(void)
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

/* Original0x128DC..0x128E0. */
REGION void tsl9_secondary_message_dispatch_block_128dc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_128dc:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_128dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_10d9a\n");
    __builtin_unreachable();
}

/* Original0x128E0..0x128E6. */
REGION void tsl9_secondary_message_dispatch_block_128e0(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_128e2:\n.option push\n.option norvc\nbleu a0,a5,.Lsecondary_message_dispatch_edge_128e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_12782\n");
    __builtin_unreachable();
}

/* Original0x128E6..0x128E8. */
REGION void tsl9_secondary_message_dispatch_block_128e6(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    __builtin_unreachable();
}

/* Original0x128E8..0x128FC. */
REGION void tsl9_secondary_message_dispatch_block_128e8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_128f8:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_128f8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x128FC..0x128FE. */
REGION void tsl9_secondary_message_dispatch_block_128fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1330A..0x13312. */
REGION void tsl9_secondary_message_dispatch_entry_1330a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1330e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1330e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_1316a\n");
    __builtin_unreachable();
}

/* Original0x13312..0x13316. */
REGION void tsl9_secondary_message_dispatch_block_13312(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_13312:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_13312\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12e86\n");
    __builtin_unreachable();
}

/* Original0x13316..0x1331A. */
REGION void tsl9_secondary_message_dispatch_block_13316(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_13316:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_13316\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12f18\n");
    __builtin_unreachable();
}

/* Original0x1331A..0x1331E. */
REGION void tsl9_secondary_message_dispatch_block_1331a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1331a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1331a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12f7a\n");
    __builtin_unreachable();
}

/* Original0x1331E..0x13322. */
REGION void tsl9_secondary_message_dispatch_block_1331e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1331e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1331e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_13084\n");
    __builtin_unreachable();
}

/* Original0x13322..0x13326. */
REGION void tsl9_secondary_message_dispatch_block_13322(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_13322:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_13322\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_13108\n");
    __builtin_unreachable();
}

/* Original0x13326..0x1333C. */
REGION void tsl9_secondary_message_dispatch_block_13326(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 360(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000410); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x13F7E..0x13F88. */
REGION void tsl9_secondary_message_dispatch_entry_13f7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    a1 = UINT32_C(0x000000bd); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13f84:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_13f84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13f66\n");
    __builtin_unreachable();
}

/* Original0x13F88..0x13FA6. */
REGION void tsl9_secondary_message_dispatch_entry_13f88(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x00010000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff9\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffff806)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff8\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 2042\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_13fa2:\n.option push\n.option norvc\nbeq a4,a5,.Lsecondary_message_dispatch_edge_13fa2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_13fc8\n");
    __builtin_unreachable();
}

/* Original0x13FA6..0x13FB0. */
REGION void tsl9_secondary_message_dispatch_block_13fa6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fae:\n.option push\n.option rvc\nc.bnez a5,.Lsecondary_message_dispatch_edge_13fae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_13fc8\n");
    __builtin_unreachable();
}

/* Original0x13FB0..0x13FBA. */
REGION void tsl9_secondary_message_dispatch_block_13fb0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fb8:\n.option push\n.option rvc\nc.beqz a5,.Lsecondary_message_dispatch_edge_13fb8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_13fc8\n");
    __builtin_unreachable();
}

/* Original0x13FBA..0x13FC8. */
REGION void tsl9_secondary_message_dispatch_block_13fba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a0, 2(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x000000af); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fc4:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_13fc4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13f66\n");
    __builtin_unreachable();
}

/* Original0x13FC8..0x13FD4. */
REGION void tsl9_secondary_message_dispatch_block_13fc8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 6(s0)\n.option pop\n");
    a5 = UINT32_C(0x00010000); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fd0:\n.option push\n.option norvc\nbeq a5,a4,.Lsecondary_message_dispatch_edge_13fd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_13ff6\n");
    __builtin_unreachable();
}

/* Original0x13FD4..0x13FDE. */
REGION void tsl9_secondary_message_dispatch_block_13fd4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fdc:\n.option push\n.option rvc\nc.bnez a5,.Lsecondary_message_dispatch_edge_13fdc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_13ff6\n");
    __builtin_unreachable();
}

/* Original0x13FDE..0x13FE8. */
REGION void tsl9_secondary_message_dispatch_block_13fde(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13fe6:\n.option push\n.option rvc\nc.beqz a5,.Lsecondary_message_dispatch_edge_13fe6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_secondary_message_dispatch_block_13ff6\n");
    __builtin_unreachable();
}

/* Original0x13FE8..0x13FF6. */
REGION void tsl9_secondary_message_dispatch_block_13fe8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a0, 6(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x000000af); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_13ff2:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_13ff2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13f66\n");
    __builtin_unreachable();
}

/* Original0x13FF6..0x1400C. */
REGION void tsl9_secondary_message_dispatch_block_13ff6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_13ffe:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_provider_9508\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_13ffe\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_14008:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_14008\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_94ee\n");
    __builtin_unreachable();
}

/* Original0x1400C..0x1401C. */
REGION void tsl9_secondary_message_dispatch_entry_1400c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_14018:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_14018\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_secondary_message_dispatch_entry_1330a\n");
    __builtin_unreachable();
}

/* Original0x1401C..0x14030. */
REGION void tsl9_secondary_message_dispatch_block_1401c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_14024:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_8e18\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_14024\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1402c:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1402c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x14030..0x14044. */
REGION void tsl9_secondary_message_dispatch_block_14030(void)
{
    REGS;
    a2 = UINT32_C(0x000000c8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_14038:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_99e8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_14038\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_14040:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_14040\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x14044..0x14056. */
REGION void tsl9_secondary_message_dispatch_block_14044(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_14052:\n.option push\n.option norvc\njal zero,.Lsecondary_message_dispatch_edge_14052\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13f66\n");
    __builtin_unreachable();
}

/* Original0x15584..0x1559C. */
REGION void tsl9_secondary_message_dispatch_entry_15584(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000167)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000167)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_15598:\n.option push\n.option norvc\nbltu a4,a5,.Lsecondary_message_dispatch_edge_15598\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_155ca\n");
    __builtin_unreachable();
}

/* Original0x1559C..0x155AE. */
REGION void tsl9_secondary_message_dispatch_block_1559c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000019); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_155a2:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_secondary_message_dispatch_entry_15584\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_155a2\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_155aa:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_155aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x155AE..0x155BE. */
REGION void tsl9_secondary_message_dispatch_block_155ae(void)
{
    REGS;
    a2 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lsecondary_message_dispatch_literal_155b0:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_secondary_message_dispatch_static_data_19dd4\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsecondary_message_dispatch_literal_155b0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_155ba:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_155ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_19bf0\n");
    __builtin_unreachable();
}

/* Original0x155BE..0x155C4. */
REGION void tsl9_secondary_message_dispatch_block_155be(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_155c0:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_155c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0x155C4..0x155CA. */
REGION void tsl9_secondary_message_dispatch_block_155c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x155CA..0x155D0. */
REGION void tsl9_secondary_message_dispatch_block_155ca(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000167)) = (uint8_t)0; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_155ce:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_155ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_155ae\n");
    __builtin_unreachable();
}

/* Original0x163AC..0x163BC. */
REGION void tsl9_secondary_message_dispatch_entry_163ac(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163b8:\n.option push\n.option norvc\nbnez a5,.Lsecondary_message_dispatch_edge_163b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_167a4\n");
    __builtin_unreachable();
}

/* Original0x163BC..0x163CC. */
REGION void tsl9_secondary_message_dispatch_block_163bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000024); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_163c8:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_163c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16756\n");
    __builtin_unreachable();
}

/* Original0x163CC..0x163D0. */
REGION void tsl9_secondary_message_dispatch_block_163cc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_163cc:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_163cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_164f4\n");
    __builtin_unreachable();
}

/* Original0x163D0..0x163D6. */
REGION void tsl9_secondary_message_dispatch_block_163d0(void)
{
    REGS;
    a5 = UINT32_C(0x00000011); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163d2:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_163d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166d8\n");
    __builtin_unreachable();
}

/* Original0x163D6..0x163DA. */
REGION void tsl9_secondary_message_dispatch_block_163d6(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_163d6:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_163d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16466\n");
    __builtin_unreachable();
}

/* Original0x163DA..0x163E0. */
REGION void tsl9_secondary_message_dispatch_block_163da(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163dc:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_163dc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16698\n");
    __builtin_unreachable();
}

/* Original0x163E0..0x163E4. */
REGION void tsl9_secondary_message_dispatch_block_163e0(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_163e0:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_163e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16424\n");
    __builtin_unreachable();
}

/* Original0x163E4..0x163EA. */
REGION void tsl9_secondary_message_dispatch_block_163e4(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163e6:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_163e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16680\n");
    __builtin_unreachable();
}

/* Original0x163EA..0x163EE. */
REGION void tsl9_secondary_message_dispatch_block_163ea(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_163ea:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_163ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16404\n");
    __builtin_unreachable();
}

/* Original0x163EE..0x163F6. */
REGION void tsl9_secondary_message_dispatch_block_163ee(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163f2:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_163f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_163fe\n");
    __builtin_unreachable();
}

/* Original0x163F6..0x163FC. */
REGION void tsl9_secondary_message_dispatch_block_163f6(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_163f8:\n.option push\n.option norvc\nbleu a2,a5,.Lsecondary_message_dispatch_edge_163f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_163fe\n");
    __builtin_unreachable();
}

/* Original0x163FC..0x163FE. */
REGION void tsl9_secondary_message_dispatch_block_163fc(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    __builtin_unreachable();
}

/* Original0x163FE..0x16402. */
REGION void tsl9_secondary_message_dispatch_block_163fe(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_163fe:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_163fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0x16402..0x16404. */
REGION void tsl9_secondary_message_dispatch_block_16402(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16402:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16402\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16404..0x1640A. */
REGION void tsl9_secondary_message_dispatch_block_16404(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16406:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16406\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1668c\n");
    __builtin_unreachable();
}

/* Original0x1640A..0x1640E. */
REGION void tsl9_secondary_message_dispatch_block_1640a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1640a:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_1640a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16684\n");
    __builtin_unreachable();
}

/* Original0x1640E..0x16414. */
REGION void tsl9_secondary_message_dispatch_block_1640e(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16410:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16410\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16690\n");
    __builtin_unreachable();
}

/* Original0x16414..0x1641C. */
REGION void tsl9_secondary_message_dispatch_block_16414(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16418:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16418\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16692\n");
    __builtin_unreachable();
}

/* Original0x1641C..0x16424. */
REGION void tsl9_secondary_message_dispatch_block_1641c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16424..0x1642A. */
REGION void tsl9_secondary_message_dispatch_block_16424(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16426:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16426\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166aa\n");
    __builtin_unreachable();
}

/* Original0x1642A..0x1642E. */
REGION void tsl9_secondary_message_dispatch_block_1642a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1642a:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_1642a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1644a\n");
    __builtin_unreachable();
}

/* Original0x1642E..0x16434. */
REGION void tsl9_secondary_message_dispatch_block_1642e(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16430:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16430\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166a4\n");
    __builtin_unreachable();
}

/* Original0x16434..0x16438. */
REGION void tsl9_secondary_message_dispatch_block_16434(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16434:\n.option push\n.option norvc\nbleu a2,a5,.Lsecondary_message_dispatch_edge_16434\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1669e\n");
    __builtin_unreachable();
}

/* Original0x16438..0x1643C. */
REGION void tsl9_secondary_message_dispatch_block_16438(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16438:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16438\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7ec\n");
    __builtin_unreachable();
}

/* Original0x1643C..0x16448. */
REGION void tsl9_secondary_message_dispatch_block_1643c(void)
{
    REGS;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16444:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16444\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7dc\n");
    __builtin_unreachable();
}

/* Original0x16448..0x1644A. */
REGION void tsl9_secondary_message_dispatch_block_16448(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16448:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16448\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x1644A..0x16450. */
REGION void tsl9_secondary_message_dispatch_block_1644a(void)
{
    REGS;
    a5 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1644c:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1644c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166c2\n");
    __builtin_unreachable();
}

/* Original0x16450..0x16454. */
REGION void tsl9_secondary_message_dispatch_block_16450(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16450:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_16450\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166b8\n");
    __builtin_unreachable();
}

/* Original0x16454..0x1645A. */
REGION void tsl9_secondary_message_dispatch_block_16454(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16456:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16456\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166ce\n");
    __builtin_unreachable();
}

/* Original0x1645A..0x16460. */
REGION void tsl9_secondary_message_dispatch_block_1645a(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1645c:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_1645c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16460..0x16464. */
REGION void tsl9_secondary_message_dispatch_block_16460(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16460:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16460\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_18110\n");
    __builtin_unreachable();
}

/* Original0x16464..0x16466. */
REGION void tsl9_secondary_message_dispatch_block_16464(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16464:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16464\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16466..0x1646C. */
REGION void tsl9_secondary_message_dispatch_block_16466(void)
{
    REGS;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16468:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16468\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1670a\n");
    __builtin_unreachable();
}

/* Original0x1646C..0x16470. */
REGION void tsl9_secondary_message_dispatch_block_1646c(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1646c:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_1646c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_164a8\n");
    __builtin_unreachable();
}

/* Original0x16470..0x16476. */
REGION void tsl9_secondary_message_dispatch_block_16470(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16472:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16472\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166f2\n");
    __builtin_unreachable();
}

/* Original0x16476..0x1647A. */
REGION void tsl9_secondary_message_dispatch_block_16476(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16476:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_16476\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1648a\n");
    __builtin_unreachable();
}

/* Original0x1647A..0x16480. */
REGION void tsl9_secondary_message_dispatch_block_1647a(void)
{
    REGS;
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1647c:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1647c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166e6\n");
    __builtin_unreachable();
}

/* Original0x16480..0x16484. */
REGION void tsl9_secondary_message_dispatch_block_16480(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16480:\n.option push\n.option norvc\nbleu a2,a5,.Lsecondary_message_dispatch_edge_16480\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166de\n");
    __builtin_unreachable();
}

/* Original0x16484..0x1648A. */
REGION void tsl9_secondary_message_dispatch_block_16484(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16488:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16488\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166e2\n");
    __builtin_unreachable();
}

/* Original0x1648A..0x16490. */
REGION void tsl9_secondary_message_dispatch_block_1648a(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1648c:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1648c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16702\n");
    __builtin_unreachable();
}

/* Original0x16490..0x16494. */
REGION void tsl9_secondary_message_dispatch_block_16490(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16490:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_16490\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_166fa\n");
    __builtin_unreachable();
}

/* Original0x16494..0x1649A. */
REGION void tsl9_secondary_message_dispatch_block_16494(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16496:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16496\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16706\n");
    __builtin_unreachable();
}

/* Original0x1649A..0x164A2. */
REGION void tsl9_secondary_message_dispatch_block_1649a(void)
{
    REGS;
    a5 = UINT32_C(0x00000019); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1649e:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_1649e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x164A2..0x164A6. */
REGION void tsl9_secondary_message_dispatch_block_164a2(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164a2:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_164a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b594\n");
    __builtin_unreachable();
}

/* Original0x164A6..0x164A8. */
REGION void tsl9_secondary_message_dispatch_block_164a6(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164a6:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_164a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x164A8..0x164AE. */
REGION void tsl9_secondary_message_dispatch_block_164a8(void)
{
    REGS;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164aa:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16736\n");
    __builtin_unreachable();
}

/* Original0x164AE..0x164B2. */
REGION void tsl9_secondary_message_dispatch_block_164ae(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164ae:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_164ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_164d2\n");
    __builtin_unreachable();
}

/* Original0x164B2..0x164B8. */
REGION void tsl9_secondary_message_dispatch_block_164b2(void)
{
    REGS;
    a5 = UINT32_C(0x0000001c); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164b4:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1671e\n");
    __builtin_unreachable();
}

/* Original0x164B8..0x164BC. */
REGION void tsl9_secondary_message_dispatch_block_164b8(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164b8:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_164b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16714\n");
    __builtin_unreachable();
}

/* Original0x164BC..0x164C2. */
REGION void tsl9_secondary_message_dispatch_block_164bc(void)
{
    REGS;
    a5 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164be:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1672a\n");
    __builtin_unreachable();
}

/* Original0x164C2..0x164C8. */
REGION void tsl9_secondary_message_dispatch_block_164c2(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164c4:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_164c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x164C8..0x164CC. */
REGION void tsl9_secondary_message_dispatch_block_164c8(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x164CC..0x164D0. */
REGION void tsl9_secondary_message_dispatch_block_164cc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164cc:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_164cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0x164D0..0x164D2. */
REGION void tsl9_secondary_message_dispatch_block_164d0(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164d0:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_164d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x164D2..0x164DA. */
REGION void tsl9_secondary_message_dispatch_block_164d2(void)
{
    REGS;
    a5 = UINT32_C(0x00000021); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164d6:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16746\n");
    __builtin_unreachable();
}

/* Original0x164DA..0x164DE. */
REGION void tsl9_secondary_message_dispatch_block_164da(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164da:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_164da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1673c\n");
    __builtin_unreachable();
}

/* Original0x164DE..0x164E6. */
REGION void tsl9_secondary_message_dispatch_block_164de(void)
{
    REGS;
    a5 = UINT32_C(0x00000022); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164e2:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1674c\n");
    __builtin_unreachable();
}

/* Original0x164E6..0x164EE. */
REGION void tsl9_secondary_message_dispatch_block_164e6(void)
{
    REGS;
    a5 = UINT32_C(0x00000023); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164ea:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_164ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x164EE..0x164F4. */
REGION void tsl9_secondary_message_dispatch_block_164ee(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164f2:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_164f2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16750\n");
    __builtin_unreachable();
}

/* Original0x164F4..0x164FC. */
REGION void tsl9_secondary_message_dispatch_block_164f4(void)
{
    REGS;
    a5 = UINT32_C(0x00000036); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_164f8:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_164f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x164FC..0x16500. */
REGION void tsl9_secondary_message_dispatch_block_164fc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_164fc:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_164fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165b6\n");
    __builtin_unreachable();
}

/* Original0x16500..0x16508. */
REGION void tsl9_secondary_message_dispatch_block_16500(void)
{
    REGS;
    a5 = UINT32_C(0x0000002d); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16504:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16504\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16788\n");
    __builtin_unreachable();
}

/* Original0x16508..0x1650C. */
REGION void tsl9_secondary_message_dispatch_block_16508(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16508:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_16508\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1654e\n");
    __builtin_unreachable();
}

/* Original0x1650C..0x16514. */
REGION void tsl9_secondary_message_dispatch_block_1650c(void)
{
    REGS;
    a5 = UINT32_C(0x00000028); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16510:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16510\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16770\n");
    __builtin_unreachable();
}

/* Original0x16514..0x16518. */
REGION void tsl9_secondary_message_dispatch_block_16514(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16514:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_16514\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1652a\n");
    __builtin_unreachable();
}

/* Original0x16518..0x16520. */
REGION void tsl9_secondary_message_dispatch_block_16518(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1651c:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1651c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16766\n");
    __builtin_unreachable();
}

/* Original0x16520..0x16524. */
REGION void tsl9_secondary_message_dispatch_block_16520(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16520:\n.option push\n.option norvc\nbleu a2,a5,.Lsecondary_message_dispatch_edge_16520\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16760\n");
    __builtin_unreachable();
}

/* Original0x16524..0x1652A. */
REGION void tsl9_secondary_message_dispatch_block_16524(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16528:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16528\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1676a\n");
    __builtin_unreachable();
}

/* Original0x1652A..0x16532. */
REGION void tsl9_secondary_message_dispatch_block_1652a(void)
{
    REGS;
    a5 = UINT32_C(0x0000002a); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1652e:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1652e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1677c\n");
    __builtin_unreachable();
}

/* Original0x16532..0x16536. */
REGION void tsl9_secondary_message_dispatch_block_16532(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16532:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_16532\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16778\n");
    __builtin_unreachable();
}

/* Original0x16536..0x1653E. */
REGION void tsl9_secondary_message_dispatch_block_16536(void)
{
    REGS;
    a5 = UINT32_C(0x0000002b); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1653a:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1653a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16784\n");
    __builtin_unreachable();
}

/* Original0x1653E..0x16548. */
REGION void tsl9_secondary_message_dispatch_block_1653e(void)
{
    REGS;
    a5 = UINT32_C(0x0000002c); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16544:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_16544\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16548..0x1654C. */
REGION void tsl9_secondary_message_dispatch_block_16548(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16548:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16548\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f97c\n");
    __builtin_unreachable();
}

/* Original0x1654C..0x1654E. */
REGION void tsl9_secondary_message_dispatch_block_1654c(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1654c:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1654c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x1654E..0x16556. */
REGION void tsl9_secondary_message_dispatch_block_1654e(void)
{
    REGS;
    a5 = UINT32_C(0x00000031); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16552:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16552\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16794\n");
    __builtin_unreachable();
}

/* Original0x16556..0x1655A. */
REGION void tsl9_secondary_message_dispatch_block_16556(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16556:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_16556\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16570\n");
    __builtin_unreachable();
}

/* Original0x1655A..0x16562. */
REGION void tsl9_secondary_message_dispatch_block_1655a(void)
{
    REGS;
    a5 = UINT32_C(0x0000002f); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1655e:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1655e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1678c\n");
    __builtin_unreachable();
}

/* Original0x16562..0x16568. */
REGION void tsl9_secondary_message_dispatch_block_16562(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16564:\n.option push\n.option norvc\nbleu a2,a5,.Lsecondary_message_dispatch_edge_16564\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1678e\n");
    __builtin_unreachable();
}

/* Original0x16568..0x1656A. */
REGION void tsl9_secondary_message_dispatch_block_16568(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1656A..0x1656E. */
REGION void tsl9_secondary_message_dispatch_block_1656a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1656a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1656a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b176\n");
    __builtin_unreachable();
}

/* Original0x1656E..0x16570. */
REGION void tsl9_secondary_message_dispatch_block_1656e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1656e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1656e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16570..0x16578. */
REGION void tsl9_secondary_message_dispatch_block_16570(void)
{
    REGS;
    a5 = UINT32_C(0x00000033); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16574:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16574\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16798\n");
    __builtin_unreachable();
}

/* Original0x16578..0x1657E. */
REGION void tsl9_secondary_message_dispatch_block_16578(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1657a:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_1657a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1679a\n");
    __builtin_unreachable();
}

/* Original0x1657E..0x16586. */
REGION void tsl9_secondary_message_dispatch_block_1657e(void)
{
    REGS;
    a5 = UINT32_C(0x00000034); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16582:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16582\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x16586..0x1658A. */
REGION void tsl9_secondary_message_dispatch_block_16586(void)
{
    REGS;
    a5 = UINT32_C(0x00000035); LIVE;
    __builtin_unreachable();
}

/* Original0x1658A..0x1658E. */
REGION void tsl9_secondary_message_dispatch_block_1658a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1658a:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_1658a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x1658E..0x165A4. */
REGION void tsl9_secondary_message_dispatch_block_1658e(void)
{
    REGS;
    a2 = a2 + UINT32_C(0xffffffcb); LIVE;
    PORT(".option push\n.option rvc\nsrai a2, a2, 0x1\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = a2 & UINT32_C(0x000000ff); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint8_t)a5; LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165a0:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_165a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_profiles_provider_184aa\n");
    __builtin_unreachable();
}

/* Original0x165A4..0x165B4. */
REGION void tsl9_secondary_message_dispatch_block_165a4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001d)) = (uint8_t)a0; LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 28\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_165b0:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_165b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x165B4..0x165B6. */
REGION void tsl9_secondary_message_dispatch_block_165b4(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_165b4:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_165b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x165B6..0x165BE. */
REGION void tsl9_secondary_message_dispatch_block_165b6(void)
{
    REGS;
    a5 = UINT32_C(0x0000003f); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165ba:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_165ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x165BE..0x165C2. */
REGION void tsl9_secondary_message_dispatch_block_165be(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_165be:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_165be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_16606\n");
    __builtin_unreachable();
}

/* Original0x165C2..0x165CA. */
REGION void tsl9_secondary_message_dispatch_block_165c2(void)
{
    REGS;
    a5 = UINT32_C(0x0000003a); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165c6:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_165c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x165CA..0x165CE. */
REGION void tsl9_secondary_message_dispatch_block_165ca(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_165ca:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_165ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165e8\n");
    __builtin_unreachable();
}

/* Original0x165CE..0x165D6. */
REGION void tsl9_secondary_message_dispatch_block_165ce(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165d2:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_165d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x165D6..0x165E6. */
REGION void tsl9_secondary_message_dispatch_block_165d6(void)
{
    REGS;
    a2 = a2 + UINT32_C(0xffffffcc); LIVE;
    PORT(".option push\n.option norvc\nsrai a0, a2, 0x1\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165e2:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_165e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18232\n");
    __builtin_unreachable();
}

/* Original0x165E6..0x165E8. */
REGION void tsl9_secondary_message_dispatch_block_165e6(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_165e6:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_165e6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x165E8..0x165F0. */
REGION void tsl9_secondary_message_dispatch_block_165e8(void)
{
    REGS;
    a5 = UINT32_C(0x0000003c); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165ec:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_165ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x165F0..0x165F4. */
REGION void tsl9_secondary_message_dispatch_block_165f0(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_165f0:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_165f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x165F4..0x165FC. */
REGION void tsl9_secondary_message_dispatch_block_165f4(void)
{
    REGS;
    a5 = UINT32_C(0x0000003d); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_165f8:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_165f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x165FC..0x16604. */
REGION void tsl9_secondary_message_dispatch_block_165fc(void)
{
    REGS;
    a5 = UINT32_C(0x0000003e); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16600:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16600\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x16604..0x16606. */
REGION void tsl9_secondary_message_dispatch_block_16604(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16604:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16604\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16606..0x1660E. */
REGION void tsl9_secondary_message_dispatch_block_16606(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1660a:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1660a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x1660E..0x16612. */
REGION void tsl9_secondary_message_dispatch_block_1660e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1660e:\n.option push\n.option norvc\nbltu a5,a2,.Lsecondary_message_dispatch_edge_1660e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1662c\n");
    __builtin_unreachable();
}

/* Original0x16612..0x1661A. */
REGION void tsl9_secondary_message_dispatch_block_16612(void)
{
    REGS;
    a5 = UINT32_C(0x00000041); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16616:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16616\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x1661A..0x1661E. */
REGION void tsl9_secondary_message_dispatch_block_1661a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1661a:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_1661a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x1661E..0x16626. */
REGION void tsl9_secondary_message_dispatch_block_1661e(void)
{
    REGS;
    a5 = UINT32_C(0x00000042); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16622:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16622\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x16626..0x1662C. */
REGION void tsl9_secondary_message_dispatch_block_16626(void)
{
    REGS;
    a5 = UINT32_C(0x00000043); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1662a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1662a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1658a\n");
    __builtin_unreachable();
}

/* Original0x1662C..0x16634. */
REGION void tsl9_secondary_message_dispatch_block_1662c(void)
{
    REGS;
    a5 = UINT32_C(0x00000046); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16630:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_16630\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_165d6\n");
    __builtin_unreachable();
}

/* Original0x16634..0x16638. */
REGION void tsl9_secondary_message_dispatch_block_16634(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16634:\n.option push\n.option norvc\nbltu a2,a5,.Lsecondary_message_dispatch_edge_16634\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x16638..0x16640. */
REGION void tsl9_secondary_message_dispatch_block_16638(void)
{
    REGS;
    a5 = UINT32_C(0x00000047); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1663c:\n.option push\n.option norvc\nbeq a2,a5,.Lsecondary_message_dispatch_edge_1663c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1658e\n");
    __builtin_unreachable();
}

/* Original0x16640..0x16648. */
REGION void tsl9_secondary_message_dispatch_block_16640(void)
{
    REGS;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16644:\n.option push\n.option norvc\nbne a2,a5,.Lsecondary_message_dispatch_edge_16644\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16648..0x1664C. */
REGION void tsl9_secondary_message_dispatch_block_16648(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16648:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16648\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_mode_getter_829e\n");
    __builtin_unreachable();
}

/* Original0x1664C..0x16652. */
REGION void tsl9_secondary_message_dispatch_block_1664c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1664e:\n.option push\n.option norvc\nbne a0,a5,.Lsecondary_message_dispatch_edge_1664e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_167a0\n");
    __builtin_unreachable();
}

/* Original0x16652..0x16656. */
REGION void tsl9_secondary_message_dispatch_block_16652(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16652:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16652\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x16656..0x1665C. */
REGION void tsl9_secondary_message_dispatch_block_16656(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16658:\n.option push\n.option norvc\nbeq a0,a5,.Lsecondary_message_dispatch_edge_16658\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_167a0\n");
    __builtin_unreachable();
}

/* Original0x1665C..0x16660. */
REGION void tsl9_secondary_message_dispatch_block_1665c(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1665c:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1665c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x16660..0x16666. */
REGION void tsl9_secondary_message_dispatch_block_16660(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16662:\n.option push\n.option norvc\nbeq a0,a5,.Lsecondary_message_dispatch_edge_16662\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_167a0\n");
    __builtin_unreachable();
}

/* Original0x16666..0x1666A. */
REGION void tsl9_secondary_message_dispatch_block_16666(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16666:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16666\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x1666A..0x16670. */
REGION void tsl9_secondary_message_dispatch_block_1666a(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1666c:\n.option push\n.option norvc\nbeq a0,a5,.Lsecondary_message_dispatch_edge_1666c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_secondary_message_dispatch_block_167a0\n");
    __builtin_unreachable();
}

/* Original0x16670..0x16676. */
REGION void tsl9_secondary_message_dispatch_block_16670(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16672:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16672\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_secondary_message_dispatch_entry_15584\n");
    __builtin_unreachable();
}

/* Original0x16676..0x16678. */
REGION void tsl9_secondary_message_dispatch_block_16676(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x16678..0x1667E. */
REGION void tsl9_secondary_message_dispatch_block_16678(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lsecondary_message_dispatch_edge_1667a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1667a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_secondary_message_dispatch_entry_13f7e\n");
    __builtin_unreachable();
}

/* Original0x1667E..0x16680. */
REGION void tsl9_secondary_message_dispatch_block_1667e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1667e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1667e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16680..0x16684. */
REGION void tsl9_secondary_message_dispatch_block_16680(void)
{
    REGS;
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16682:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16682\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_163fe\n");
    __builtin_unreachable();
}

/* Original0x16684..0x16686. */
REGION void tsl9_secondary_message_dispatch_block_16684(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x16686..0x1668A. */
REGION void tsl9_secondary_message_dispatch_block_16686(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16686:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16686\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0x1668A..0x1668C. */
REGION void tsl9_secondary_message_dispatch_block_1668a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1668a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1668a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x1668C..0x16690. */
REGION void tsl9_secondary_message_dispatch_block_1668c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1668e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1668e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16686\n");
    __builtin_unreachable();
}

/* Original0x16690..0x16692. */
REGION void tsl9_secondary_message_dispatch_block_16690(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x16692..0x16696. */
REGION void tsl9_secondary_message_dispatch_block_16692(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16692:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16692\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d3c6\n");
    __builtin_unreachable();
}

/* Original0x16696..0x16698. */
REGION void tsl9_secondary_message_dispatch_block_16696(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16696:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16696\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16698..0x1669C. */
REGION void tsl9_secondary_message_dispatch_block_16698(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16698:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16698\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_deec\n");
    __builtin_unreachable();
}

/* Original0x1669C..0x1669E. */
REGION void tsl9_secondary_message_dispatch_block_1669c(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1669c:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1669c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x1669E..0x166A2. */
REGION void tsl9_secondary_message_dispatch_block_1669e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1669e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1669e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_e042\n");
    __builtin_unreachable();
}

/* Original0x166A2..0x166A4. */
REGION void tsl9_secondary_message_dispatch_block_166a2(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166a2:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x166A4..0x166A8. */
REGION void tsl9_secondary_message_dispatch_block_166a4(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166a4:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_166a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_e048\n");
    __builtin_unreachable();
}

/* Original0x166A8..0x166AA. */
REGION void tsl9_secondary_message_dispatch_block_166a8(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166a8:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166a8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x166AA..0x166B2. */
REGION void tsl9_secondary_message_dispatch_block_166aa(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x166B2..0x166B6. */
REGION void tsl9_secondary_message_dispatch_block_166b2(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166b2:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_166b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x166B6..0x166B8. */
REGION void tsl9_secondary_message_dispatch_block_166b6(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166b6:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x166B8..0x166C2. */
REGION void tsl9_secondary_message_dispatch_block_166b8(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_166c0:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x166C2..0x166CE. */
REGION void tsl9_secondary_message_dispatch_block_166c2(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_166cc:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x166CE..0x166D8. */
REGION void tsl9_secondary_message_dispatch_block_166ce(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_166d6:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x166D8..0x166DC. */
REGION void tsl9_secondary_message_dispatch_block_166d8(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166d8:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_166d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_f666\n");
    __builtin_unreachable();
}

/* Original0x166DC..0x166DE. */
REGION void tsl9_secondary_message_dispatch_block_166dc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166dc:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x166DE..0x166E2. */
REGION void tsl9_secondary_message_dispatch_block_166de(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x166E2..0x166E6. */
REGION void tsl9_secondary_message_dispatch_block_166e2(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_166e4:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166e4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166ec\n");
    __builtin_unreachable();
}

/* Original0x166E6..0x166EC. */
REGION void tsl9_secondary_message_dispatch_block_166e6(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x166EC..0x166F0. */
REGION void tsl9_secondary_message_dispatch_block_166ec(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166ec:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_166ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x166F0..0x166F2. */
REGION void tsl9_secondary_message_dispatch_block_166f0(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166f0:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x166F2..0x166FA. */
REGION void tsl9_secondary_message_dispatch_block_166f2(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_166f8:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_166f8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166ec\n");
    __builtin_unreachable();
}

/* Original0x166FA..0x166FC. */
REGION void tsl9_secondary_message_dispatch_block_166fa(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x166FC..0x16700. */
REGION void tsl9_secondary_message_dispatch_block_166fc(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_166fc:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_166fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f818\n");
    __builtin_unreachable();
}

/* Original0x16700..0x16702. */
REGION void tsl9_secondary_message_dispatch_block_16700(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16700:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16700\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16702..0x16706. */
REGION void tsl9_secondary_message_dispatch_block_16702(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16704:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16704\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166fc\n");
    __builtin_unreachable();
}

/* Original0x16706..0x1670A. */
REGION void tsl9_secondary_message_dispatch_block_16706(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16708:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16708\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_164a2\n");
    __builtin_unreachable();
}

/* Original0x1670A..0x16714. */
REGION void tsl9_secondary_message_dispatch_block_1670a(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16712:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16712\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x16714..0x1671E. */
REGION void tsl9_secondary_message_dispatch_block_16714(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1671c:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1671c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x1671E..0x1672A. */
REGION void tsl9_secondary_message_dispatch_block_1671e(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000080); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16728:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16728\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x1672A..0x16736. */
REGION void tsl9_secondary_message_dispatch_block_1672a(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16734:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16734\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_166b2\n");
    __builtin_unreachable();
}

/* Original0x16736..0x1673C. */
REGION void tsl9_secondary_message_dispatch_block_16736(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1673a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1673a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_164cc\n");
    __builtin_unreachable();
}

/* Original0x1673C..0x16740. */
REGION void tsl9_secondary_message_dispatch_block_1673c(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x16740..0x16744. */
REGION void tsl9_secondary_message_dispatch_block_16740(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16740:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16740\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ec\n");
    __builtin_unreachable();
}

/* Original0x16744..0x16746. */
REGION void tsl9_secondary_message_dispatch_block_16744(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16744:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16744\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16746..0x1674C. */
REGION void tsl9_secondary_message_dispatch_block_16746(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1674a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1674a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16740\n");
    __builtin_unreachable();
}

/* Original0x1674C..0x16750. */
REGION void tsl9_secondary_message_dispatch_block_1674c(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x16750..0x16754. */
REGION void tsl9_secondary_message_dispatch_block_16750(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16750:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16750\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0x16754..0x16756. */
REGION void tsl9_secondary_message_dispatch_block_16754(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16754:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16754\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16756..0x1675A. */
REGION void tsl9_secondary_message_dispatch_block_16756(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1675A..0x1675E. */
REGION void tsl9_secondary_message_dispatch_block_1675a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1675a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1675a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f71e\n");
    __builtin_unreachable();
}

/* Original0x1675E..0x16760. */
REGION void tsl9_secondary_message_dispatch_block_1675e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1675e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1675e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16760..0x16766. */
REGION void tsl9_secondary_message_dispatch_block_16760(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16764:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16764\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1675a\n");
    __builtin_unreachable();
}

/* Original0x16766..0x1676A. */
REGION void tsl9_secondary_message_dispatch_block_16766(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1676A..0x1676E. */
REGION void tsl9_secondary_message_dispatch_block_1676a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1676a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1676a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0x1676E..0x16770. */
REGION void tsl9_secondary_message_dispatch_block_1676e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1676e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1676e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16770..0x16772. */
REGION void tsl9_secondary_message_dispatch_block_16770(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x16772..0x16776. */
REGION void tsl9_secondary_message_dispatch_block_16772(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16772:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_16772\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0x16776..0x16778. */
REGION void tsl9_secondary_message_dispatch_block_16776(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16776:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16776\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16778..0x1677C. */
REGION void tsl9_secondary_message_dispatch_block_16778(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1677a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1677a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16772\n");
    __builtin_unreachable();
}

/* Original0x1677C..0x1677E. */
REGION void tsl9_secondary_message_dispatch_block_1677c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1677E..0x16782. */
REGION void tsl9_secondary_message_dispatch_block_1677e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1677e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1677e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0x16782..0x16784. */
REGION void tsl9_secondary_message_dispatch_block_16782(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16782:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16782\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16784..0x16788. */
REGION void tsl9_secondary_message_dispatch_block_16784(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16786:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16786\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1677e\n");
    __builtin_unreachable();
}

/* Original0x16788..0x1678C. */
REGION void tsl9_secondary_message_dispatch_block_16788(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_1678a:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1678a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16548\n");
    __builtin_unreachable();
}

/* Original0x1678C..0x1678E. */
REGION void tsl9_secondary_message_dispatch_block_1678c(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1678E..0x16792. */
REGION void tsl9_secondary_message_dispatch_block_1678e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1678e:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1678e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fa24\n");
    __builtin_unreachable();
}

/* Original0x16792..0x16794. */
REGION void tsl9_secondary_message_dispatch_block_16792(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_16792:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16792\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x16794..0x16798. */
REGION void tsl9_secondary_message_dispatch_block_16794(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_16796:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_16796\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1656a\n");
    __builtin_unreachable();
}

/* Original0x16798..0x1679A. */
REGION void tsl9_secondary_message_dispatch_block_16798(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1679A..0x1679E. */
REGION void tsl9_secondary_message_dispatch_block_1679a(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1679a:\n.option push\n.option norvc\njal ra,.Lsecondary_message_dispatch_edge_1679a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fa30\n");
    __builtin_unreachable();
}

/* Original0x1679E..0x167A0. */
REGION void tsl9_secondary_message_dispatch_block_1679e(void)
{
    REGS;
    PORT(".Lsecondary_message_dispatch_edge_1679e:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_1679e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_1641c\n");
    __builtin_unreachable();
}

/* Original0x167A0..0x167A4. */
REGION void tsl9_secondary_message_dispatch_block_167a0(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsecondary_message_dispatch_edge_167a2:\n.option push\n.option rvc\nc.j .Lsecondary_message_dispatch_edge_167a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_secondary_message_dispatch_block_16678\n");
    __builtin_unreachable();
}

/* Original0x167A4..0x167A6. */
REGION void tsl9_secondary_message_dispatch_block_167a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
